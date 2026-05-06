import arcade
import random
import time
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Maximum Buffer Runner"

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

        # Initial Spawning: Fewer objects, massive vertical gaps
        for i in range(4):
            self.create_hazard(start_y=SCREEN_HEIGHT + (i * 400))
            if i % 2 == 0:
                self.create_token(start_y=SCREEN_HEIGHT + (i * 400) + 200)

    def get_safe_position(self, start_y):
        """Finds a spot at least 350 pixels away from any other object."""
        max_attempts = 100 # Checking extra hard
        for _ in range(max_attempts):
            # Keep items away from the extreme edges for better visibility
            x = random.randint(150, SCREEN_WIDTH - 150)
            y = start_y if start_y is not None else SCREEN_HEIGHT + 300

            too_close = False

            # Distance check against all current hazards
            for sprite in self.hazard_list:
                dist = math.sqrt((x - sprite.center_x)**2 + (y - sprite.center_y)**2)
                if dist < 350: # The new massive buffer
                    too_close = True
                    break

            if not too_close:
                # Distance check against all current tokens
                for sprite in self.token_list:
                    dist = math.sqrt((x - sprite.center_x)**2 + (y - sprite.center_y)**2)
                    if dist < 350:
                        too_close = True
                        break

            if not too_close:
                return x, y

        # If no spot found, push it very far up to wait for space
        return random.randint(150, SCREEN_WIDTH - 150), (start_y + 400 if start_y else SCREEN_HEIGHT + 600)

    def create_hazard(self, start_y=None):
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
        hazard.center_x, hazard.center_y = self.get_safe_position(start_y)

        # 90% Stationary - makes the game feel very structured
        hazard.is_stationary = random.random() < 0.90
        hazard.change_x = random.choice([-4, 4]) if not hazard.is_stationary else 0
        self.hazard_list.append(hazard)

    def create_token(self, start_y=None):
        token = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
        token.center_x, token.center_y = self.get_safe_position(start_y)
        token.value = random.choice([1, 1, 5, 5, 10, -5])
        self.token_list.append(token)

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.2, "color": color, "size": 32})

    def on_draw(self) -> None:
        self.clear()
        self.background_list.draw()
        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Score: {self.score}", SCREEN_WIDTH - 180, SCREEN_HEIGHT - 50, arcade.
