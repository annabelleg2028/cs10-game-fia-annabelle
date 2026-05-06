import arcade
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Feedback Edition"

SPRITE_SCALING_PLAYER = 0.08
MOVEMENT_SPEED = 10
SCROLL_SPEED = 7

LANES = [150, 275, 400, 525, 650]
ROW_SPACING = 140

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
        self.last_hit_time = 0

        # New: List to hold floating text notifications
        self.messages = []

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

        for i in range(8):
            self.spawn_wave(SCREEN_HEIGHT + (i * ROW_SPACING))

    def spawn_wave(self, y_pos):
        # Hazard placement
        bomb_idx = random.randint(0, len(LANES) - 1)
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
        hazard.center_x = LANES[bomb_idx]
        hazard.center_y = y_pos
        self.hazard_list.append(hazard)

        # Token placement (at least 2 lanes away)
        allowed_indices = [i for i in range(len(LANES)) if abs(i - bomb_idx) >= 2]
        if not allowed_indices: allowed_indices = [i for i in range(len(LANES)) if i != bomb_idx]

        token = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
        token.center_x = LANES[random.choice(allowed_indices)]
        token.center_y = y_pos + random.randint(-20, 20) # Slight vertical variety
        token.value = random.choice([1, 5, 10])
        self.token_list.append(token)

    def add_message(self, text, x, y, color):
        """Creates a floating notification."""
        self.messages.append({
            "text": text,
            "x": x,
            "y": y,
            "timer": 1.0, # How long it stays visible
            "color": color
        })

    def on_draw(self) -> None:
        self.clear()
        self.background_list.draw()
        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        # UI
        arcade.draw_text(f"Score: {self.score}", 20, 20, arcade.color.WHITE, 20, bold=True)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(SCREEN_WIDTH - 220 + (i * 45), 35, 15, color)

        # Draw floating notifications
        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 24, bold=True, anchor_x="center")

        if self.is_game_over:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 180))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 50, anchor_x="center")

    def on_update(self, delta_time: float) -> None:
        if self.is_game_over: return

        # Update floating messages
        for msg in self.messages:
            msg["y"] += 2  # Move up
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0] # Remove old ones

        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2: bg.center_y += SCREEN_HEIGHT * 2

        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED
            if hazard.top < 0:
                hazard.remove_from_sprite_lists()
                self.spawn_wave(SCREEN_HEIGHT + ROW_SPACING)

        for token in self.token_list:
            token.center_y -= SCROLL_SPEED
            if token.top < 0:
                token.remove_from_sprite_lists()

        # Hits and Feedback
        current_time = time.time()
        invincible = (current_time - self.last_hit_time) < 1.2
        self.player_sprite.alpha = 160 if invincible else 255

        if not invincible:
            hit_hazard = arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list)
            if hit_hazard:
                self.health -= 1
                self.last_hit_time = current_time
                self.add_message("-1 HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)
                if self.health <= 0: self.is_game_over = True

        coin_hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for coin in coin_hits:
            self.score += coin.value
            self.add_message(f"+{coin.value}", coin.center_x, coin.center_y, arcade.color.GOLD)
            coin.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT: self.left_pressed = True
        elif key == arcade.key.RIGHT: self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT: self.left_pressed = False
        elif key == arcade.key.RIGHT: self.right_pressed = False

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(GameView())
    arcade.run()

if __name__ == "__main__":
    main()
