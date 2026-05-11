"""CS10 Arcade starter game.

One student on each team owns edits to this file.
Other students build features in game-yourname.py files and share them for integration.
"""

import arcade
import random
import traceback

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade Team Game"

SPRITE_SCALING_PLAYER = 0.1
MOVEMENT_SPEED = 5
AUTO_MOVE_SPEED = 2
OBSTACLE_WIDTH = 100
OBSTACLE_HEIGHT = 30


class GameView(arcade.View):
    """Minimal view students can extend."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

        self.player_sprite = None
        self.player_list = None
        self.obstacle_list = None

        self.left_pressed = False
        self.right_pressed = False

        self.scroll_y = 0
        self.obstacle_spawn_y = 0
        self.score = 0

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

        self.player_list = arcade.SpriteList()
        self.obstacle_list = []

        self.player_sprite = arcade.Sprite(
            "player2.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

        self.score = 0
        self.scroll_y = 0
        self.obstacle_spawn_y = 0

    def on_draw(self) -> None:
        try:
            self.clear()

            # Draw scrolling background lines
            for i in range(-1, 3):
                y = (i * 100) - (self.scroll_y % 100)
                arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.WHITE, 2)

            # Draw obstacles as red rectangles
            for obstacle in self.obstacle_list:
                arcade.draw_lbwh_rectangle_filled(
                    obstacle["x"] - (OBSTACLE_WIDTH / 2),
                    obstacle["y"] - (OBSTACLE_HEIGHT / 2),
                    OBSTACLE_WIDTH,
                    OBSTACLE_HEIGHT,
                    arcade.color.RED
                )

            # Draw the player sprite
            self.player_list.draw()

            # Draw score
            arcade.draw_text(
                f"Score: {self.score}",
                10,
                SCREEN_HEIGHT - 30,
                arcade.color.WHITE,
                14,
            )
        except Exception as e:
            print(f"Error in on_draw: {e}")
            traceback.print_exc()

    def on_key_press(self, key, modifiers) -> None:
        """Handle key presses."""
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers) -> None:
        """Handle key releases."""
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time: float) -> None:
        """Update game logic."""
        try:
            # Always move forward (scroll background)
            self.scroll_y += AUTO_MOVE_SPEED
            self.obstacle_spawn_y += AUTO_MOVE_SPEED
            self.score += 1

            # Spawn new obstacles
            if self.obstacle_spawn_y > 100:
                x = random.randrange(100, SCREEN_WIDTH - 100)
                self.obstacle_list.append({"x": x, "y": SCREEN_HEIGHT - 50})
                self.obstacle_spawn_y = 0

            # Move obstacles down
            for obstacle in self.obstacle_list:
                obstacle["y"] -= AUTO_MOVE_SPEED

            # Remove obstacles that are off screen
            self.obstacle_list = [obs for obs in self.obstacle_list if obs["y"] > -50]

            # Move left/right with arrow keys
            if self.left_pressed:
                self.player_sprite.center_x -= MOVEMENT_SPEED
            if self.right_pressed:
                self.player_sprite.center_x += MOVEMENT_SPEED

            # Keep player in bounds
            if self.player_sprite.left < 0:
                self.player_sprite.left = 0
            if self.player_sprite.right > SCREEN_WIDTH:
                self.player_sprite.right = SCREEN_WIDTH

            # Keep player Y centered on screen
            self.player_sprite.center_y = SCREEN_HEIGHT / 2
        except Exception as e:
            print(f"Error in on_update: {e}")
            traceback.print_exc()


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
