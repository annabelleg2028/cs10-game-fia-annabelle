"""CS10 Arcade starter game.

One student on each team owns edits to this file.
Other students build features in game-yourname.py files and share them for integration.
"""

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade Team Game"

SPRITE_SCALING_PLAYER = 0.1


class GameView(arcade.View):
    """Minimal view students can extend."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

        self.player_sprite = None
        self.player_list = None

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

        # Set up the player sprite
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite(
            "player2.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

    def on_draw(self) -> None:
        self.clear()

        # Draw the player sprite
        self.player_list.draw()

        arcade.draw_text(
            "CS10 Arcade Starter",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 24,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )
        arcade.draw_text(
            "Edit game.py (owner) or your game-yourname.py file",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 20,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
