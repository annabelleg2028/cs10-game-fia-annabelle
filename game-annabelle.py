import arcade
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Perfect Grid Edition"

SPRITE_SCALING_PLAYER = 0.08
MOVEMENT_SPEED = 9
SCROLL_SPEED = 7

# Define 5 distinct horizontal lanes
LANES = [150, 275, 400, 525, 650]
# Define vertical row spacing (200px ensures no large empty patches)
ROW_SPACING = 200

class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()

        self.player_sprite = None
        self.left_pressed = False
        self.right_pressed = False

        self.health = 5
        self.score = 0
        self.is_game_over = False

        self.messages = []
        self.last_hit_time = 0

        # Track which lane is used in the most recent row to prevent "walls"
        self.last_hazard_lane = -1

    def on_show_view(self) -> None:
        self.setup()

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("player2.png", scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        for i in range(2):
            bg = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            bg.center_x = SCREEN_WIDTH / 2
            bg.center_y = (i * SCREEN_HEIGHT) + (SCREEN_HEIGHT / 2)
            self.background_list.append(bg)

        # Initial wave setup: 5 rows of action
        for i in range(5):
            y_pos = SCREEN_HEIGHT + (i * ROW_SPACING)
            self.spawn_row(y_pos)

    def spawn_row(self, y_pos):
        """Spawns one hazard and one token in guaranteed different lanes."""
        # 1. Pick a lane for the hazard (don't pick the same lane as the previous row)
        possible_hazard_lanes = [l for l in LANES if l != self.last_hazard_lane]
        h_lane = random.choice(possible_hazard_lanes)
        self.last_hazard_lane = h_lane

        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
        hazard.center_x = h_lane
        hazard.center_y = y_pos
        hazard.is_stationary = random.random() < 0.90 # 90% Stationary
        hazard.change_x = random.choice([-3, 3]) if not hazard.is_stationary else 0
        self.hazard_list.append(hazard)

        # 2. Pick a lane for the token (Must NOT be the hazard lane or adjacent)
        # This ensures they never overlap or even touch diagonally
        possible_token_lanes = [l for l in LANES if abs(l - h_lane) > 150]

        if possible_token_lanes:
            t_lane = random.choice(possible_token_lanes)
            token = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
            token.center_x = t_lane
            token.center_y = y_pos + (ROW_SPACING / 2) # Staggered vertically
            token.value = random.choice([1, 5, 10, -5])
            self.token_list.append(token)

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.0, "color": color, "size": 28})

    def on_draw(self) -> None:
        self.clear()
        self.background_list.draw()
        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Score: {self.score}", SCREEN_WIDTH - 180, SCREEN_HEIGHT - 50, arcade.color.WHITE, 24, bold=True)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(50 + (i * 45), SCREEN_HEIGHT - 45, 15, color)

        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], msg["size"], bold=True, anchor_x="center")

        if self.is_game_over:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 180))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 50, anchor_x="center")

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.LEFT: self.left_pressed = True
        elif key == arcade.key.RIGHT: self.right_pressed = True

    def on_key_release(self, key, modifiers) -> None:
        if key == arcade.key.LEFT: self.left_pressed = False
        elif key == arcade.key.RIGHT: self.right_pressed = False

    def on_update(self, delta_time: float) -> None:
        if self.is_game_over: return

        # Message logic
        for msg in self.messages:
            msg["y"] += 2
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

        # Player movement
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Background scroll
        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2: bg.center_y += SCREEN_HEIGHT * 2

        # Update hazards
        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED
            if not hazard.is_stationary:
                hazard.center_x += hazard.change_x
                if hazard.left < 50 or hazard.right > SCREEN_WIDTH - 50:
                    hazard.change_x *= -1

            if hazard.top < 0:
                hazard.remove_from_sprite_lists()
                # When one hazard leaves, spawn a new row at the very top
                self.spawn_row(SCREEN_HEIGHT + ROW_SPACING)

        # Update tokens
        for token in self.token_list:
            token.center_y -= SCROLL_SPEED
            if token.top < 0:
                token.remove_from_sprite_lists()

        # Collision logic
        current_time = time.time()
        invincible = (current_time - self.last_hit_time) < 1.5
        self.player_sprite.alpha = 150 if invincible else 255

        if not invincible and arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list):
            self.health -= 1
            self.add_message("-1 HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)
            self.last_hit_time = current_time
            if self.health <= 0: self.is_game_over = True

        hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for token in hits:
            self.score += token.value
            color = arcade.color.GOLD if token.value > 0 else arcade.color.ORANGE_RED
            txt = f"+{token.value}" if token.value > 0 else f"{token.value}"
            self.add_message(txt, token.center_x, token.center_y, color)
            token.remove_from_sprite_lists()

def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
