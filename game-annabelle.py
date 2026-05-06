import arcade
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Infinite Runner"

SPRITE_SCALING_PLAYER = 0.1
SPRITE_SCALING_HAZARD = 0.5
MOVEMENT_SPEED = 5
WORLD_SPEED = 4

class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        # Initialize lists here so they aren't 'None' if on_draw runs early
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()

        self.player_sprite = None
        self.left_pressed = False
        self.right_pressed = False

        self.health = 5
        self.is_game_over = False

    def on_show_view(self) -> None:
        """This runs once when the view is shown."""
        self.setup()

    def setup(self):
        """Set up the game variables."""
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()

        # 1. Setup Player (Fixed Y position)
        # Using a built-in Arcade resource so the path works for everyone
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 150
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # 2. Setup Background (Two identical sprites to loop)
        for i in range(2):
            bg = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_PASTEL_BLUE)
            bg.center_x = (i * SCREEN_WIDTH) + (SCREEN_WIDTH / 2)
            bg.center_y = SCREEN_HEIGHT / 2
            self.background_list.append(bg)

        # 3. Create initial obstacles
        for i in range(3):
            self.create_hazard()

    def create_hazard(self):
        # Using built-in bomb resource
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.4)
        hazard.center_x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 400)
        hazard.center_y = random.randint(50, 250)

        # Randomly decide if it moves up/down or stays still
        hazard.is_stationary = random.choice([True, False])
        hazard.change_y = 3 if not hazard.is_stationary else 0

        self.hazard_list.append(hazard)

    def on_draw(self) -> None:
        self.clear() # Clears screen to background color

        # Draw everything
        self.background_list.draw()
        self.hazard_list.draw()
        self.player_list.draw()

        # Draw 5 Hearts (Red if you have health, Gray if lost)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(50 + (i * 40), SCREEN_HEIGHT - 40, 15, color)

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

        # Player horizontal movement
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Scroll Background to the left
        for bg in self.background_list:
            bg.center_x -= WORLD_SPEED
            # If the background piece goes off screen, reset it to the right side
            if bg.center_x <= -SCREEN_WIDTH / 2:
                bg.center_x += SCREEN_WIDTH * 2

        # Handle Hazards
        for hazard in self.hazard_list:
            hazard.center_x -= WORLD_SPEED

            # If it's a moving type, bob it up and down
            if not hazard.is_stationary:
                hazard.center_y += hazard.change_y
                if hazard.center_y > 400 or hazard.center_y < 50:
                    hazard.change_y *= -1

            # Reset hazard to right side if it leaves the screen
            if hazard.right < 0:
                hazard.center_x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
                hazard.center_y = random.randint(50, 400)

        # Check for hits
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list)
        for hit in hit_list:
            self.health -= 1
            hit.remove_from_sprite_lists() # Delete the one we hit
            self.create_hazard() # Add a new one back into the loop

            if self.health <= 0:
                self.is_game_over = True

def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
