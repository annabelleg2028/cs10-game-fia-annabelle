import arcade
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Infinite Runner"

SPRITE_SCALING_PLAYER = 0.1
SPRITE_SCALING_HAZARD = 0.05
MOVEMENT_SPEED = 5
WORLD_SPEED = 3 # This is how fast the background/obstacles move toward the player

class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

        self.player_sprite = None
        self.player_list = None
        self.background_list = None
        self.hazard_list = None

        self.left_pressed = False
        self.right_pressed = False

        self.health = 5
        self.is_game_over = False

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()

        # 1. Setup Player (Fixed Y position)
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/robot/robot_idle.png", # Using resource for portability
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 4
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # 2. Setup Scrolling Background (Two sprites to loop)
        for i in range(2):
            # Replace with your background image path
            bg = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_PASTEL_BLUE)
            bg.center_x = i * SCREEN_WIDTH + (SCREEN_WIDTH / 2)
            bg.center_y = SCREEN_HEIGHT / 2
            self.background_list.append(bg)

        # 3. Add initial hazards
        self.create_hazard(stationary=True)
        self.create_hazard(stationary=False)

    def create_hazard(self, stationary=True):
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", SPRITE_SCALING_HAZARD)
        hazard.center_x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 1.5)
        hazard.center_y = random.randint(50, 200)

        # Custom property to tell them apart
        hazard.is_stationary = stationary
        if not stationary:
            hazard.change_y = 2 # Moving up and down

        self.hazard_list.append(hazard)

    def on_draw(self) -> None:
        self.clear()

        self.background_list.draw()
        self.hazard_list.draw()
        self.player_list.draw()

        # Draw Health Hearts
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_heart(50 + (i * 40), SCREEN_HEIGHT - 40, 30, color)

        if self.is_game_over:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 150))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 50, anchor_x="center")

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.LEFT: self.left_pressed = True
        elif key == arcade.key.RIGHT: self.right_pressed = True

    def on_key_release(self, key, modifiers) -> None:
        if key == arcade.key.LEFT: self.left_pressed = False
        elif key == arcade.key.RIGHT: self.right_pressed = False

    def on_update(self, delta_time: float) -> None:
        if self.is_game_over:
            return

        # Move Player Left/Right within bounds
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Scroll Background
        for bg in self.background_list:
            bg.center_x -= WORLD_SPEED
            if bg.center_x <= -SCREEN_WIDTH / 2:
                bg.center_x += SCREEN_WIDTH * 2

        # Handle Hazards
        for hazard in self.hazard_list:
            hazard.center_x -= WORLD_SPEED # Everything moves left

            if not hazard.is_stationary:
                hazard.center_y += hazard.change_y
                if hazard.center_y > 250 or hazard.center_y < 50:
                    hazard.change_y *= -1

            # Reset hazard to right side if it goes off screen
            if hazard.right < 0:
                hazard.center_x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 200)
                hazard.center_y = random.randint(50, 250)

        # Collision Detection
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list)
        for hit in hit_list:
            self.health -= 1
            hit.remove_from_sprite_lists() # Remove obstacle so it doesn't hit twice
            self.create_hazard(stationary=random.choice([True, False])) # Spawn a new one

            if self.health <= 0:
                self.is_game_over = True

def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
