import math
import random
from pathlib import Path

import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Grey Whale Migration"

ASSET_DIR = Path(__file__).parent
OCEAN_IMAGE = ASSET_DIR / "ocean.png"
WHALE_IMAGE = ASSET_DIR / "whale.png"
FISH_IMAGES = [
    ASSET_DIR / "fish1.png",
    ASSET_DIR / "fish2.png",
    ASSET_DIR / "fish3.png",
    ASSET_DIR / "fish4.png",
]

WHALE_SCALE = 0.13
FISH_SCALE = 0.08
ITEM_COUNT = 10
GAME_DISTANCE = 2200

HEALTH_MAX = 5
BASE_SCROLL_SPEED = 65


class WhaleMigrationGame(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.ocean = arcade.load_texture(OCEAN_IMAGE)
        self.whale = arcade.load_texture(WHALE_IMAGE)
        self.fish_textures = [arcade.load_texture(path) for path in FISH_IMAGES]
        self.reset_game()

    def reset_game(self) -> None:
        self.whale_x = SCREEN_WIDTH / 2
        self.whale_y = 120
        self.whale_angle = 0
        self.health = HEALTH_MAX
        self.score = 0
        self.distance = 0
        self.level = 1
        self.game_over = False
        self.win = False
        self.spawn_timer = 0
        self.background_offset = 0
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        self.obstacles = []
        self.collectibles = []
        self.mysteries = []

        for _ in range(ITEM_COUNT):
            self.obstacles.append(self.make_obstacle(random.choice(["trash", "boat", "net"])))
            self.collectibles.append(self.make_collectible())
        for _ in range(3):
            self.mysteries.append(self.make_mystery())

    def make_collectible(self) -> dict:
        texture = random.choice(self.fish_textures)
        scale = FISH_SCALE * random.uniform(0.9, 1.2)
        width = texture.width * scale
        height = texture.height * scale
        return {
            "type": "fish",
            "texture": texture,
            "scale": scale,
            "x": random.randint(60, SCREEN_WIDTH - 60),
            "y": random.randint(SCREEN_HEIGHT + 30, SCREEN_HEIGHT + 700),
            "width": width,
            "height": height,
            "speed": random.uniform(45, 95),
            "points": random.choice([1, 1, 2]),
        }

    def make_mystery(self) -> dict:
        good = random.choice([True, True, False])
        texture = random.choice(self.fish_textures if good else self.fish_textures[:2])
        scale = FISH_SCALE * (1.0 if good else 0.9)
        width = texture.width * scale
        height = texture.height * scale
        return {
            "type": "mystery",
            "texture": texture,
            "scale": scale,
            "x": random.randint(80, SCREEN_WIDTH - 80),
            "y": random.randint(SCREEN_HEIGHT + 200, SCREEN_HEIGHT + 1000),
            "width": width,
            "height": height,
            "speed": random.uniform(70, 120),
            "good": good,
        }

    def make_obstacle(self, obstacle_type: str) -> dict:
        x = random.randint(40, SCREEN_WIDTH - 40)
        y = random.randint(SCREEN_HEIGHT + 60, SCREEN_HEIGHT + 900)
        level_boost = max(0, self.level - 1)

        if obstacle_type == "trash":
            return {
                "type": "trash",
                "x": x,
                "y": y,
                "radius": random.randint(12, 20),
                "speed": random.uniform(85, 135) + level_boost * 6,
                "damage": 1,
                "color": (116, 169, 232, 255),
            }
        if obstacle_type == "boat":
            width = random.randint(60, 110)
            height = random.randint(24, 34)
            return {
                "type": "boat",
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "speed": random.uniform(110, 165) + level_boost * 8,
                "damage": 2,
                "color": (70, 78, 88, 255),
            }

        width = random.randint(80, 150)
        height = random.randint(18, 26)
        return {
            "type": "net",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "speed": random.uniform(95, 145) + level_boost * 7,
            "damage": 1,
            "color": (190, 210, 220, 210),
        }

    def on_draw(self) -> None:
        self.clear()

        arcade.draw_texture_rect(
            self.ocean,
            arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        self.draw_water_tint()
        self.draw_background_current()
        self.draw_collectibles()
        self.draw_mysteries()
        self.draw_obstacles()
        self.draw_whale()
        self.draw_ui()

        if self.game_over or self.win:
            self.draw_end_panel()

    def draw_water_tint(self) -> None:
        progress = min(1.0, self.distance / GAME_DISTANCE)
        red = int(90 - 45 * progress)
        green = int(120 + 65 * progress)
        blue = int(150 + 55 * progress)
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (red, green, blue, 30),
        )

    def draw_background_current(self) -> None:
        bands = 7
        band_height = SCREEN_HEIGHT / bands
        progress = min(1.0, self.distance / GAME_DISTANCE)
        for i in range(bands):
            alpha = 16 if i % 2 == 0 else 8
            shift = int(20 * progress)
            arcade.draw_lbwh_rectangle_filled(
                0,
                i * band_height,
                SCREEN_WIDTH,
                band_height,
                (50 + shift, 120 + shift, 160 + shift, alpha),
            )

    def draw_whale(self) -> None:
        whale_width = self.whale.width * WHALE_SCALE
        whale_height = self.whale.height * WHALE_SCALE
        arcade.draw_texture_rect(
            self.whale,
            arcade.LBWH(
                self.whale_x - whale_width / 2,
                self.whale_y - whale_height / 2,
                whale_width,
                whale_height,
            ),
            angle=self.whale_angle,
        )

    def draw_collectibles(self) -> None:
        for item in self.collectibles:
            arcade.draw_texture_rect(
                item["texture"],
                arcade.LBWH(
                    item["x"] - item["width"] / 2,
                    item["y"] - item["height"] / 2,
                    item["width"],
                    item["height"],
                ),
                angle=0,
            )

    def draw_mysteries(self) -> None:
        for item in self.mysteries:
            arcade.draw_texture_rect(
                item["texture"],
                arcade.LBWH(
                    item["x"] - item["width"] / 2,
                    item["y"] - item["height"] / 2,
                    item["width"],
                    item["height"],
                ),
                angle=0,
            )
            arcade.draw_text(
                "?",
                item["x"],
                item["y"] - 10,
                arcade.color.WHITE,
                18,
                anchor_x="center",
            )

    def draw_obstacles(self) -> None:
        for obstacle in self.obstacles:
            if obstacle["type"] == "trash":
                arcade.draw_circle_filled(
                    obstacle["x"],
                    obstacle["y"],
                    obstacle["radius"],
                    obstacle["color"],
                )
                arcade.draw_circle_outline(
                    obstacle["x"],
                    obstacle["y"],
                    obstacle["radius"] + 2,
                    arcade.color.BLACK,
                    2,
                )
            else:
                arcade.draw_lbwh_rectangle_filled(
                    obstacle["x"] - obstacle["width"] / 2,
                    obstacle["y"] - obstacle["height"] / 2,
                    obstacle["width"],
                    obstacle["height"],
                    obstacle["color"],
                )
                if obstacle["type"] == "boat":
                    arcade.draw_lbwh_rectangle_filled(
                        obstacle["x"] - obstacle["width"] * 0.28,
                        obstacle["y"] + obstacle["height"] * 0.15,
                        obstacle["width"] * 0.22,
                        obstacle["height"] * 0.35,
                        (120, 90, 55, 255),
                    )

    def draw_ui(self) -> None:
        arcade.draw_lbwh_rectangle_filled(12, 540, 320, 48, (0, 40, 70, 170))
        arcade.draw_text(
            f"Health: {self.health}/{HEALTH_MAX}",
            24,
            556,
            arcade.color.WHITE,
            16,
        )
        arcade.draw_text(
            f"Score: {self.score}",
            148,
            556,
            arcade.color.WHITE,
            16,
        )
        arcade.draw_text(
            f"Level: {self.level}/10",
            250,
            556,
            arcade.color.WHITE,
            16,
        )

        for i in range(HEALTH_MAX):
            color = arcade.color.RED if i < self.health else (110, 30, 30, 255)
            arcade.draw_circle_filled(25 + i * 22, 520, 8, color)

        progress = min(1.0, self.distance / GAME_DISTANCE)
        arcade.draw_lbwh_rectangle_filled(12, 14, 290, 18, (0, 40, 70, 160))
        arcade.draw_lbwh_rectangle_filled(12, 14, 290 * progress, 18, (120, 220, 160, 220))
        arcade.draw_text(
            "Northbound migration",
            14,
            36,
            arcade.color.WHITE,
            12,
        )
        arcade.draw_text(f"{int(progress * 100)}% to Alaska", 306, 12, arcade.color.WHITE, 12)

    def draw_end_panel(self) -> None:
        arcade.draw_lbwh_rectangle_filled(
            150,
            170,
            500,
            260,
            (0, 40, 70, 220),
        )
        title = "You reached Alaska!" if self.win else "The whale could not continue"
        subtitle = "Press SPACE to swim again"
        detail = (
            "You balanced food, danger, and travel north."
            if self.win
            else "Try avoiding boats and nets while gathering fish."
        )
        arcade.draw_text(title, SCREEN_WIDTH / 2, 360, arcade.color.WHITE, 30, anchor_x="center")
        arcade.draw_text(
            f"Final score: {self.score}",
            SCREEN_WIDTH / 2,
            315,
            arcade.color.AQUA,
            22,
            anchor_x="center",
        )
        arcade.draw_text(
            detail,
            SCREEN_WIDTH / 2,
            275,
            arcade.color.WHITE,
            16,
            anchor_x="center",
        )
        arcade.draw_text(
            subtitle,
            SCREEN_WIDTH / 2,
            230,
            arcade.color.WHITE,
            16,
            anchor_x="center",
        )

    def on_update(self, delta_time: float) -> None:
        if self.game_over or self.win:
            return

        self.spawn_timer += delta_time
        self.background_offset = (self.background_offset + delta_time * 25) % SCREEN_HEIGHT
        self.distance += BASE_SCROLL_SPEED * delta_time
        self.level = min(10, 1 + int(self.distance / 220))

        self.move_whale()
        self.update_obstacles(delta_time)
        self.update_collectibles(delta_time)
        self.update_mysteries(delta_time)
        self.check_collisions()
        self.replenish_spawns()

        if self.health <= 0:
            self.game_over = True
        elif self.distance >= GAME_DISTANCE:
            self.win = True

    def move_whale(self) -> None:
        move_speed = 4.6 + self.level * 0.08
        dx = 0
        dy = 0

        if self.move_left:
            dx -= move_speed
        if self.move_right:
            dx += move_speed
        if self.move_down:
            dy -= move_speed
        if self.move_up:
            dy += move_speed

        if dx or dy:
            if dx and dy:
                dx *= 0.7071
                dy *= 0.7071
            self.whale_x += dx
            self.whale_y += dy
            if dx or dy:
                self.whale_angle = math.degrees(math.atan2(dy, dx))

        whale_width = self.whale.width * WHALE_SCALE
        whale_height = self.whale.height * WHALE_SCALE
        self.whale_x = max(whale_width / 2, min(SCREEN_WIDTH - whale_width / 2, self.whale_x))
        self.whale_y = max(whale_height / 2, min(SCREEN_HEIGHT - whale_height / 2, self.whale_y))

    def update_obstacles(self, delta_time: float) -> None:
        speed_scale = 1.0 + (self.level - 1) * 0.08
        for obstacle in self.obstacles:
            obstacle["y"] -= obstacle["speed"] * speed_scale * delta_time
            if obstacle["y"] < -80:
                replacement = self.make_obstacle(random.choice(["trash", "boat", "net"]))
                obstacle.update(replacement)
                obstacle["y"] = SCREEN_HEIGHT + random.randint(60, 500)

    def update_collectibles(self, delta_time: float) -> None:
        speed_scale = 1.0 + (self.level - 1) * 0.04
        for item in self.collectibles:
            item["y"] -= item["speed"] * speed_scale * delta_time
            if item["y"] < -120:
                replacement = self.make_collectible()
                item.update(replacement)
                item["y"] = SCREEN_HEIGHT + random.randint(180, 700)

    def update_mysteries(self, delta_time: float) -> None:
        speed_scale = 1.0 + (self.level - 1) * 0.05
        for item in self.mysteries:
            item["y"] -= item["speed"] * speed_scale * delta_time
            if item["y"] < -120:
                replacement = self.make_mystery()
                item.update(replacement)
                item["y"] = SCREEN_HEIGHT + random.randint(250, 1000)

    def replenish_spawns(self) -> None:
        if self.spawn_timer >= max(0.35, 1.2 - self.level * 0.08):
            self.spawn_timer = 0
            if len(self.obstacles) < ITEM_COUNT + self.level:
                self.obstacles.append(self.make_obstacle(random.choice(["trash", "boat", "net"])))
            if len(self.collectibles) < ITEM_COUNT + 2:
                self.collectibles.append(self.make_collectible())
            if len(self.mysteries) < 3 + self.level // 4:
                self.mysteries.append(self.make_mystery())

    def check_collisions(self) -> None:
        whale_width = self.whale.width * WHALE_SCALE
        whale_height = self.whale.height * WHALE_SCALE
        whale_radius = max(whale_width, whale_height) * 0.35

        for obstacle in self.obstacles:
            if self.circle_hit(obstacle["x"], obstacle["y"], self.obstacle_radius(obstacle), whale_radius):
                self.health -= obstacle["damage"]
                obstacle["y"] = SCREEN_HEIGHT + random.randint(100, 400)
                obstacle["x"] = random.randint(40, SCREEN_WIDTH - 40)

        for item in self.collectibles:
            if self.circle_hit(item["x"], item["y"], max(item["width"], item["height"]) * 0.35, whale_radius):
                self.score += item["points"]
                self.health = min(HEALTH_MAX, self.health + 1)
                replacement = self.make_collectible()
                item.update(replacement)
                item["y"] = SCREEN_HEIGHT + random.randint(180, 700)

        for item in self.mysteries:
            if self.circle_hit(item["x"], item["y"], max(item["width"], item["height"]) * 0.35, whale_radius):
                if item["good"]:
                    self.score += 2
                    self.health = min(HEALTH_MAX, self.health + 1)
                else:
                    self.health -= 2
                replacement = self.make_mystery()
                item.update(replacement)
                item["y"] = SCREEN_HEIGHT + random.randint(250, 1000)

    def circle_hit(self, x1: float, y1: float, radius1: float, radius2: float) -> bool:
        dx = x1 - self.whale_x
        dy = y1 - self.whale_y
        return math.hypot(dx, dy) < radius1 + radius2

    def obstacle_radius(self, obstacle: dict) -> float:
        if obstacle["type"] == "trash":
            return obstacle["radius"]
        return max(obstacle["width"], obstacle["height"]) * 0.35

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol in (arcade.key.UP, arcade.key.W):
            self.move_up = True
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.move_down = True
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            self.move_left = True
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.move_right = True
        if symbol == arcade.key.SPACE and (self.game_over or self.win):
            self.reset_game()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol in (arcade.key.UP, arcade.key.W):
            self.move_up = False
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.move_down = False
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            self.move_left = False
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.move_right = False


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(WhaleMigrationGame())
    arcade.run()


if __name__ == "__main__":
    main()
