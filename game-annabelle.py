import arcade
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Speed & Surprise"

SPRITE_SCALING_PLAYER = 0.08
MOVEMENT_SPEED = 9
SCROLL_SPEED = 7 # Faster world speed

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

        # System for pop-up messages
        self.messages = []
        self.last_hit_time = 0 # To prevent losing all hearts instantly

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
            self.create_hazard(start_y=SCREEN_HEIGHT + (i * 180))

        for i in range(3):
            self.create_token(start_y=SCREEN_HEIGHT + (i * 350))

    def create_hazard(self, start_y=None):
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
        hazard.center_x = random.randint(100, SCREEN_WIDTH - 100)
        hazard.center_y = start_y if start_y is not None else SCREEN_HEIGHT + random.randint(100, 200)
        hazard.is_stationary = random.random() < 0.75
        hazard.change_x = random.choice([-4, 4]) if not hazard.is_stationary else 0
        self.hazard_list.append(hazard)

    def create_token(self, start_y=None):
        token = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
        token.center_x = random.randint(50, SCREEN_WIDTH - 50)
        token.center_y = start_y if start_y is not None else SCREEN_HEIGHT + random.randint(100, 300)
        token.value = random.choice([1, 1, 5, 5, 10, -5])
        self.token_list.append(token)

    def add_message(self, text, x, y, color):
        # Stores message content, position, and a "life" timer
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.0, "color": color})

    def on_draw(self) -> None:
        self.clear()

        self.background_list.draw()
        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        # UI: Score & Health
        arcade.draw_text(f"Score: {self.score}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 45, arcade.color.WHITE, 20, bold=True)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(50 + (i * 40), SCREEN_HEIGHT - 40, 15, color)

        # Draw pop-up notifications
        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 18, bold=True, anchor_x="center")

        if self.is_game_over:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0,0,0,180))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 50, anchor_x="center")

    def on_update(self, delta_time: float) -> None:
        if self.is_game_over:
            return

        # Update Messages (make them float up and fade)
        for msg in self.messages:
            msg["y"] += 2
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

        # Player Movement
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Scroll background, hazards, and tokens
        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2: bg.center_y += SCREEN_HEIGHT * 2

        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED
            if not hazard.is_stationary:
                hazard.center_x += hazard.change_x
                if hazard.left < 0 or hazard.right > SCREEN_WIDTH: hazard.change_x *= -1
            if hazard.top < 0:
                hazard.center_y = SCREEN_HEIGHT +
