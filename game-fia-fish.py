import math
import random
from pathlib import Path

import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fia's Fish Swim"

ASSET_DIR = Path(__file__).parent
OCEAN_IMAGE = ASSET_DIR / "ocean.png"
FISH_IMAGE = ASSET_DIR / "fish1.png"

FISH_SCALE = 0.16
FISH_SPEED = 6
BUBBLE_COUNT = 8
GAME_SECONDS = 45


class FishSwimGame(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.ocean = arcade.load_texture(OCEAN_IMAGE)
        self.fish = arcade.load_texture(FISH_IMAGE)
        self.fish_width = self.fish.width * FISH_SCALE
        self.fish_height = self.fish.height * FISH_SCALE
        self.fish_x = SCREEN_WIDTH / 2
        self.fish_y = SCREEN_HEIGHT / 2
        self.fish_angle = 0
        self.target_x = self.fish_x
        self.target_y = self.fish_y
        self.score = 0
        self.time_left = GAME_SECONDS
        self.game_over = False
        self.bubbles = []
        self.reset_game()

    def reset_game(self) -> None:
        self.fish_x = SCREEN_WIDTH / 2
        self.fish_y = SCREEN_HEIGHT / 2
        self.fish_angle = 0
        self.target_x = self.fish_x
        self.target_y = self.fish_y
        self.score = 0
        self.time_left = GAME_SECONDS
        self.game_over = False
        self.bubbles = [self.make_bubble() for _ in range(BUBBLE_COUNT)]

    def make_bubble(self) -> dict:
        radius = random.randint(12, 26)
        return {
            "x": random.randint(radius, SCREEN_WIDTH - radius),
            "y": random.randint(radius, SCREEN_HEIGHT - radius),
            "radius": radius,
            "speed": random.uniform(15, 45),
        }

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_texture_rect(
            self.ocean,
            arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        for bubble in self.bubbles:
            arcade.draw_circle_filled(
                bubble["x"],
                bubble["y"],
                bubble["radius"],
                (170, 230, 255, 130),
            )
            arcade.draw_circle_outline(
                bubble["x"],
                bubble["y"],
                bubble["radius"],
                arcade.color.WHITE,
                2,
            )

        arcade.draw_texture_rect(
            self.fish,
            arcade.LBWH(
                self.fish_x - self.fish_width / 2,
                self.fish_y - self.fish_height / 2,
                self.fish_width,
                self.fish_height,
            ),
            angle=self.fish_angle,
        )
        self.draw_scoreboard()

        if self.game_over:
            arcade.draw_lbwh_rectangle_filled(
                SCREEN_WIDTH / 2 - 215,
                SCREEN_HEIGHT / 2 - 75,
                430,
                150,
                (0, 45, 85, 210),
            )
            arcade.draw_text(
                "Time's up!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 32,
                arcade.color.WHITE,
                32,
                anchor_x="center",
            )
            arcade.draw_text(
                f"Final score: {self.score}",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 8,
                arcade.color.AQUA,
                20,
                anchor_x="center",
            )
            arcade.draw_text(
                "Press SPACE to swim again",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 45,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )

    def draw_scoreboard(self) -> None:
        arcade.draw_lbwh_rectangle_filled(
            10,
            SCREEN_HEIGHT - 55,
            205,
            46,
            (0, 45, 85, 180),
        )
        arcade.draw_text(
            f"Score: {self.score}",
            24,
            SCREEN_HEIGHT - 42,
            arcade.color.WHITE,
            18,
        )
        arcade.draw_text(
            f"Time: {math.ceil(self.time_left)}",
            135,
            SCREEN_HEIGHT - 42,
            arcade.color.WHITE,
            18,
        )

    def on_update(self, delta_time: float) -> None:
        if self.game_over:
            return

        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True
            return

        self.move_fish()
        self.move_bubbles(delta_time)
        self.check_bubble_catches()

    def move_fish(self) -> None:
        dx = self.target_x - self.fish_x
        dy = self.target_y - self.fish_y
        distance = math.hypot(dx, dy)

        if distance > 1:
            self.fish_x += dx / distance * min(FISH_SPEED, distance)
            self.fish_y += dy / distance * min(FISH_SPEED, distance)
            self.fish_angle = math.degrees(math.atan2(dy, dx))

    def move_bubbles(self, delta_time: float) -> None:
        for bubble in self.bubbles:
            bubble["y"] += bubble["speed"] * delta_time
            if bubble["y"] - bubble["radius"] > SCREEN_HEIGHT:
                new_bubble = self.make_bubble()
                bubble.update(new_bubble)
                bubble["y"] = -bubble["radius"]

    def check_bubble_catches(self) -> None:
        fish_radius = max(self.fish_width, self.fish_height) / 3

        for bubble in self.bubbles:
            dx = bubble["x"] - self.fish_x
            dy = bubble["y"] - self.fish_y
            if math.hypot(dx, dy) < fish_radius + bubble["radius"]:
                self.score += 1
                bubble.update(self.make_bubble())

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.target_x = x
        self.target_y = y

    def on_mouse_drag(
        self,
        x: int,
        y: int,
        dx: int,
        dy: int,
        buttons: int,
        modifiers: int,
    ) -> None:
        self.target_x = x
        self.target_y = y

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.SPACE and self.game_over:
            self.reset_game()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(FishSwimGame())
    arcade.run()


if __name__ == "__main__":
    main()
