import arcade
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Balanced Runner"

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

        for i in range(6):
            self.create_hazard(start_y=SCREEN_HEIGHT + (i * 250))
            if i % 2 == 0:
                self.create_token(start_y=SCREEN_HEIGHT + (i * 250) + 125)

    def get_safe_position(self, start_y):
        """Finds a position that doesn't overlap with existing sprites."""
        max_attempts = 10
        for _ in range(max_attempts):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = start_y if start_y is not None else SCREEN_HEIGHT + 200

            too_close = False

            # Check hazards
            for sprite in self.hazard_list:
                if arcade.get_distance(x, y, sprite.center_x, sprite.center_y) < 150:
                    too_close = True
                    break

            # Check tokens (only if not already too close to a hazard)
            if not too_close:
                for sprite in self.token_list:
                    if arcade.get_distance(x, y, sprite.center_x, sprite.center_y) < 150:
                        too_close = True
                        break

            if not too_close:
                return x, y

        return random.randint(100, SCREEN_WIDTH - 100), start_y

    def create_hazard(self, start_y=None):
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
        hazard.center_x, hazard.center_y = self.get_safe_position(start_y)

        hazard.is_stationary = random.random() < 0.80
        hazard.change_x = random.choice([-4, 4]) if not hazard.is_stationary else 0

        if not hazard.is_stationary:
            hazard.center_x = random.randint(200, SCREEN_WIDTH - 200)

        self.hazard_list.append(hazard)

    def create_token(self, start_y=None):
        token = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
        token.center_x, token.center_y = self.get_safe_position(start_y)
        token.value = random.choice([1, 1, 5, 5, 10, -5])
        self.token_list.append(token)

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.2, "color": color, "size": 28})

    def on_draw(self) -> None:
        self.clear()
        self.background_list.draw()
        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        # UI
        arcade.draw_text(f"Score: {self.score}", SCREEN_WIDTH - 170, SCREEN_HEIGHT - 45, arcade.color.WHITE, 24, bold=True)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(50 + (i * 40), SCREEN_HEIGHT - 40, 15, color)

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
                hazard.center_x, hazard.center_y = self.get_safe_position(SCREEN_HEIGHT + 200)

        for token in self.token_list:
            token.center_y -= SCROLL_SPEED
            if token.top < 0:
                token.center_x, token.center_y = self.get_safe_position(SCREEN_HEIGHT + 400)

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

            token.center_x, token.center_y = self.get_safe_position(SCREEN_HEIGHT + random.randint(300, 600))
            token.value = random.choice([1, 1, 5, 5, 10, -5])

def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
