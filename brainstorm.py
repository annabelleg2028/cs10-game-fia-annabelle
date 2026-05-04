"""CS10 Arcade starter game.

One student on each team owns edits to this file.
Other students build features in game-yourname.py files and share them for integration.
"""

import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade Team Game"

SPRITE_SCALING_PLAYER = 0.1
MOVEMENT_SPEED = 5
AUTO_MOVE_SPEED = 2
OBSTACLE_WIDTH = 100
OBSTACLE_HEIGHT = 30


class Obstacle(arcade.Sprite):
    """An obstacle that moves down the screen."""

    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT


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
        self.game_over = False
        self.score = 0

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

        self.player_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(
            "/Users/annabellegrant/cs10-game-fia-annabelle/player2.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

        self.game_over = False
        self.score = 0

    def on_draw(self) -> None:
        self.clear()

        # Draw scrolling background lines
        for i in range(-1, 3):
            y = (i * 100) - (self.scroll_y % 100)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.WHITE, 2)

        # Draw obstacles
        for obstacle in self.obstacle_list:
            arcade.draw_rectangle_filled(
                obstacle.center_x,
                obstacle.center_y,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT,
                arcade.color.RED
            )

        self.player_list.draw()

        # Draw score
        arcade.draw_text(
            f"Score: {self.score}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            14,
        )

        if self.game_over:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK)
            arcade.draw_text(
                "GAME OVER!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 50,
                arcade.color.RED,
                40,
                anchor_x="center",
            )
            arcade.draw_text(
                f"Final Score: {self.score}",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
            )
            arcade.draw_text(
                "Press R to restart",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )

    def on_key_press(self, key, modifiers) -> None:
        """Handle key presses."""
        if self.game_over and key == arcade.key.R:
            self.on_show_view()
            return

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
        if self.game_over:
            return

        # Always move forward (scroll background)
        self.scroll_y += AUTO_MOVE_SPEED
        self.obstacle_spawn_y += AUTO_MOVE_SPEED
        self.score += 1

        # Spawn new obstacles
        if self.obstacle_spawn_y > 100:
            x = random.randrange(50, SCREEN_WIDTH - 50)
            obstacle = Obstacle(x, SCREEN_HEIGHT + 50)
            self.obstacle_list.append(obstacle)
            self.obstacle_spawn_y = 0

        # Move obstacles down
        for obstacle in self.obstacle_list:
            obstacle.center_y -= AUTO_MOVE_SPEED

 """CS10 Arcade starter game.

One student on each team owns edits to this file.
Other students build features in game-yourname.py files and share them for integration.
"""

import arcade
import random

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
        self.game_over = False
        self.score = 0

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

        self.player_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(
            "/Users/annabellegrant/cs10-game-fia-annabelle/player2.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

        self.game_over = False
        self.score = 0
        self.scroll_y = 0
        self.obstacle_spawn_y = 0

    def on_draw(self) -> None:
        self.clear()

        # Draw scrolling background lines
        for i in range(-1, 3):
            y = (i * 100) - (self.scroll_y % 100)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.WHITE, 2)

        # Draw obstacles as red rectangles
        for obstacle in self.obstacle_list:
            arcade.draw_rectangle_filled(
                obstacle["x"],
                obstacle["y"],
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT,
                arcade.color.RED
            )

        self.player_list.draw()

        # Draw score
        arcade.draw_text(
            f"Score: {self.score}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            14,
        )

        if self.game_over:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK)
            arcade.draw_text(
                "GAME OVER!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 50,
                arcade.color.RED,
                40,
                anchor_x="center",
            )
            arcade.draw_text(
                f"Final Score: {self.score}",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
            )
            arcade.draw_text(
                "Press R to restart",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )

    def on_key_press(self, key, modifiers) -> None:
        """Handle key presses."""
        if self.game_over and key == arcade.key.R:
            self.on_show_view()
            return

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
        if self.game_over:
            return

        # Always move forward (scroll background)
        self.scroll_y += AUTO_MOVE_SPEED
        self.obstacle_spawn_y += AUTO_MOVE_SPEED
        self.score += 1

        # Spawn new obstacles
        if self.obstacle_spawn_y > 100:
            x = random.randrange(50, SCREEN_WIDTH - 50)
            self.obstacle_list.append({"x": x, "y": SCREEN_HEIGHT + 50})
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
        if self.player_sprite.center_x < 0:
            self.player_sprite.center_x = 0
        if self.player_sprite.center_x > SCREEN_WIDTH:
            self.player_sprite.center_x = SCREEN_WIDTH

        # Check for collisions with obstacles
        player_rect = arcade.Rect(
            self.player_sprite.center_x - self.player_sprite.width/2,
            self.player_sprite.center_y - self.player_sprite.height/2,
            self.player_sprite.width,
            self.player_sprite.height
        )

        for obstacle in self.obstacle_list:
            obstacle_rect = arcade.Rect(
                obstacle["x"] - OBSTACLE_WIDTH/2,
                obstacle["y"] - OBSTACLE_HEIGHT/2,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            )

            if player_rect.collides_with_rect(obstacle_rect):
                self.game_over = True


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
