import arcade
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Vertical Runner"

# Set player size here
SPRITE_SCALING_PLAYER = 0.5
MOVEMENT_SPEED = 7
SCROLL_SPEED = 4

class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()

        self.player_sprite = None
        self.left_pressed = False
        self.right_pressed = False

        self.health = 5
        self.is_game_over = False

    def on_show_view(self) -> None:
        self.setup()

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()

        # 1. Setup Player (Fixed low on screen)
        # Using your local image file
        self.player_sprite = arcade.Sprite(
            "player2.png",
            scale=SPRITE_SCALING_PLAYER
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = 120
        self.player_list.append(self.player_sprite)

        # 2. Setup Background (Two sprites stacking vertically to loop)
        for i in range(2):
            bg = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            bg.center_x = SCREEN_WIDTH / 2
            bg.center_y = (i * SCREEN_HEIGHT) + (SCREEN_HEIGHT / 2)
            self.background_list.append(bg)

        # 3. Create initial spread out obstacles
        for i in range(6):
            self.create_hazard(start_y=SCREEN_HEIGHT + (i * 200))

    def create_hazard(self, start_y=None):
        # Using a built-in bomb; feel free to change to your own image path
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)

        hazard.center_x = random.randint(50, SCREEN_WIDTH - 50)
        hazard.center_y = start_y if start_y is not None else SCREEN_HEIGHT + 100

        # Logic for types: Stationary vs Moving
        hazard.is_stationary = random.choice([True, False])
        hazard.change_x = random.choice([-3, 3]) if not hazard.is_stationary else 0

        self.hazard_list.append(hazard)

    def on_draw(self) -> None:
        self.clear()

        self.background_list.draw()
        self.hazard_list.draw()
        self.player_list.draw()

        # Draw Health (5 Hearts)
        for i in range(5):
            # Hearts are Red if you have health, Gray if lost
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_heart(50 + (i * 40), SCREEN_HEIGHT - 40, 30, color)

        if self.is_game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                             arcade.color.WHITE, 50, anchor_x="center")

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.LEFT: self.left_pressed = True
        elif key == arcade.key.RIGHT: self.right_pressed = True

    def on_key_release(self, key, modifiers) -> None:
        if key == arcade.key.LEFT: self.left_pressed = False
        elif key == arcade.key.RIGHT: self.right_pressed = False

    def on_update(self, delta_time: float) -> None:
        if self.is_game_over:
            return

        # Player move Left/Right only
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Scroll Background DOWN (to make player look like they are moving UP)
        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2:
                bg.center_y += SCREEN_HEIGHT * 2

        # Handle Hazards (They move down with the world)
        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED

            # If moving type, bounce left/right
            if not hazard.is_stationary:
                hazard.center_x += hazard.change_x
                if hazard.left < 0 or hazard.right > SCREEN_WIDTH:
                    hazard.change_x *= -1

            # Reset to top if it leaves the bottom
            if hazard.top < 0:
                hazard.center_y = SCREEN_HEIGHT + random.randint(100, 300)
                hazard.center_x = random.randint(50, SCREEN_WIDTH - 50)

        # Check for hits
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list)
        for hit in hit_list:
            self.health -= 1
            hit.remove_from_sprite_lists()
            self.create_hazard() # Spawn a replacement

            if self.health <= 0:
                self.is_game_over = True

def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
