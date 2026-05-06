import arcade
import random
import time
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Ultra Spaced Runner"

SPRITE_SCALING_PLAYER = 0.08
MOVEMENT_SPEED = 9
SCROLL_SPEED = 7

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

        # Build initial waves - Spacing them even further vertically (300 pixels)
        for i in range(5):
            self.create_hazard(start_y=SCREEN_HEIGHT + (i * 300))
            if i % 2 == 0:
                self.create_token(start_y=SCREEN_HEIGHT + (i * 300) + 150)

    def get_safe_position(self, start_y):
        """Finds a spot at least 250 pixels away from any other object."""
        max_attempts = 50 # Try very hard to find a clear spot
        for _ in range(max_attempts):
            x = random.randint(150, SCREEN_WIDTH - 150)
            y = start_y if start_y is not None else SCREEN_HEIGHT + 200

            too_close = False

            # Check hazards distance
            for sprite in self.hazard_list:
                dist = math.sqrt((x - sprite.center_x)**2 + (y - sprite.center_y)**2)
                if dist < 250: # Increased buffer
                    too_close = True
                    break

            if not too_close:
                # Check tokens distance
                for sprite in self.token_list:
                    dist = math.sqrt((x - sprite.center_x)**2 + (y - sprite.center_y)**2)
                    if dist < 250:
                        too_close = True
                        break

            if not too_close:
                return x, y

        # If after 50 tries it can't find a spot, move it further up to wait for room
        return random.randint(150, SCREEN_WIDTH - 150), (start_y + 100 if start_y else SCREEN_HEIGHT + 300)

    def create_hazard(self, start_y=None):
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
        hazard.center_x, hazard.center_y = self.get_safe_position(start_y)

        # 85% Stationary to make lanes predictable
        hazard.is_stationary = random.random() < 0.85
        hazard.change_x = random.choice([-4, 4]) if not hazard.is_stationary else 0

        self.hazard_list.append(hazard)

    def create_token(self, start_y=None):
        token = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
        token.center_x, token.center_y = self.get_safe_position(start_y)
        token.value = random.choice([1, 1, 5, 5, 10, -5])
        self.token_list.append(token)

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.2, "color": color, "size": 30})

    def on_draw(self) -> None:
        self.clear()
        self.background_list.draw()
        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        # UI: Score and Health
        arcade.draw_text(f"Score: {self.score}", SCREEN_WIDTH - 180, SCREEN_HEIGHT - 50, arcade.color.WHITE, 26, bold=True)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(60 + (i * 45), SCREEN_HEIGHT - 45, 18, color)

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

        for msg in self.messages:
            msg["y"] += 2
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2: bg.center_y += SCREEN_HEIGHT * 2

        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED
            if not hazard.is_stationary:
                hazard.center_x += hazard.change_x
                if hazard.left < 0 or hazard.right > SCREEN_WIDTH: hazard.change_x *= -1

            if hazard.top < 0:
                # Recalculate safe position at the top
                hazard.center_x, hazard.center_y = self.get_safe_position(SCREEN_HEIGHT + 200)

        for token in self.token_list:
            token.center_y -= SCROLL_SPEED
            if token.top < 0:
                token.center_x, token.center_y = self.get_safe_position(SCREEN_HEIGHT + 300)

        # Hit detection with 1.5s invincibility
        current_time = time.time()
        invincible = (current_time - self.last_hit_time) < 1.5
        self.player_sprite.alpha = 130 if invincible else 255

        if not invincible and arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list):
            self.health -= 1
            self.add_message("-1 HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)
            self.last_hit_time = current_time
            if self.health <= 0: self.is_game_over = True

        # Token collection
        hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for token in hits:
            self.score += token.value
            color = arcade.color.GOLD if token.value > 0 else arcade.color.ORANGE_RED
            txt = f"+{token.value}" if token.value > 0 else f"{token.value}"
            self.add_message(txt, token.center_x, token.center_y, color)

            # Reposition the token safely far away
            token.center_x, token.center_y = self.get_safe_position(SCREEN_HEIGHT + random.randint(400, 800))
            token.value = random.choice([1, 1, 5, 5, 10, -5])

def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
