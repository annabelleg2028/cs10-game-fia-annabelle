"""CS10 Arcade starter game.

One student on each team owns edits to this file.
Other students build features in game-yourname.py files and share them for integration.
"""

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade Team Game"

SPRITE_SCALING_PLAYER = 0.1
MOVEMENT_SPEED = 5
AUTO_MOVE_SPEED = 2  # Speed for automatic upward movement


class GameView(arcade.View):
    """Minimal view students can extend."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

        self.player_sprite = None
        self.player_list = None

        # Track which keys are pressed
        self.left_pressed = False
        self.right_pressed = False

        # Camera/scroll position
        self.camera_y = 0

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

        # Set up the player sprite
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite(
            "/Users/annabellegrant/cs10-game-fia-annabelle/player2.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

    def on_draw(self) -> None:
        self.clear()

        # Set up the camera so it follows the player
        arcade.set_viewport(0, SCREEN_WIDTH, int(self.camera_y), int(self.camera_y) + SCREEN_HEIGHT)

        # Draw the player sprite
        self.player_list.draw()

        arcade.draw_text(
            "CS10 Arcade Starter",
            SCREEN_WIDTH / 2,
            int(self.camera_y) + SCREEN_HEIGHT / 2 + 24,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )
        arcade.draw_text(
            "Edit game.py (owner) or your game-yourname.py file",
            SCREEN_WIDTH / 2,
            int(self.camera_y) + SCREEN_HEIGHT / 2 - 20,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )

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
        # Always move up slowly
        self.player_sprite.center_y += AUTO_MOVE_SPEED

        # Move left/right with arrow keys
        if self.left_pressed:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Keep camera centered on player
        self.camera_y = self.player_sprite.center_y - SCREEN_HEIGHT / 2


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
