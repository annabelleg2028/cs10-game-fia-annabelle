"""Grey whale migration serious game MVP."""

import random
from typing import Optional

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Grey Whale Migration"

LANES = 8
LANE_WIDTH = SCREEN_WIDTH / LANES
ROW_HEIGHT = 80

SPRITE_SCALING_PLAYER = 0.08
PLAYER_SPEED = 6
BASE_SCROLL_SPEED = 2.5

HEALTH_MAX = 5
HEAT_MAX = 100.0
TOTAL_LEVELS = 10
DISTANCE_PER_LEVEL = 900
DISTANCE_TO_ALASKA = TOTAL_LEVELS * DISTANCE_PER_LEVEL

WARM_COLOR = (255, 214, 120, 255)
COOL_COLOR = (90, 180, 135, 255)
DEEP_WATER = (10, 65, 90, 255)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def lerp(start: float, end: float, amount: float) -> float:
    return start + ((end - start) * amount)


def lerp_color(start, end, amount: float):
    amount = clamp(amount, 0.0, 1.0)
    return tuple(int(lerp(start[i], end[i], amount)) for i in range(4))


class GameView(arcade.View):
    def __init__(self, window: Optional[arcade.Window] = None) -> None:
        super().__init__(window=window)
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

        self.player_sprite = None
        self.player_list = arcade.SpriteList()
        self.trash_list = arcade.SpriteList()
        self.net_list = arcade.SpriteList()
        self.boat_list = arcade.SpriteList()
        self.fish_list = arcade.SpriteList()
        self.mystery_list = arcade.SpriteList()

        self.left_pressed = False
        self.right_pressed = False

        self.distance_traveled = 0.0
        self.spawn_cursor = 0.0
        self.level = 1
        self.health = HEALTH_MAX
        self.score = 0
        self.heat = 18.0
        self.game_over = False
        self.won = False
        self.messages = []

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def setup(self) -> None:
        self.player_list = arcade.SpriteList()
        self.trash_list = arcade.SpriteList()
        self.net_list = arcade.SpriteList()
        self.boat_list = arcade.SpriteList()
        self.fish_list = arcade.SpriteList()
        self.mystery_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("player2.png", scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 4
        self.player_list.append(self.player_sprite)

        self.left_pressed = False
        self.right_pressed = False

        self.distance_traveled = 0.0
        self.spawn_cursor = 0.0
        self.level = 1
        self.health = HEALTH_MAX
        self.score = 0
        self.heat = 18.0
        self.game_over = False
        self.won = False
        self.messages = []

        while self.spawn_cursor < SCREEN_HEIGHT + ROW_HEIGHT:
            self.spawn_row()

    def make_item(self, width: int, height: int, color, col: int, row_y: float):
        item = arcade.SpriteSolidColor(width, height, color)
        item.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        item.center_y = row_y
        return item

    def pick_lane(self, occupied: set[int], buffer: int = 1):
        choices = [
            lane
            for lane in range(LANES)
            if all(abs(lane - taken) > buffer for taken in occupied)
        ]
        if not choices:
            choices = [lane for lane in range(LANES) if lane not in occupied]
        if not choices:
            choices = list(range(LANES))
        return random.choice(choices)

    def spawn_trash(self, lane: int, row_y: float) -> None:
        sprite = self.make_item(36, 36, (116, 169, 232, 255), lane, row_y)
        sprite.damage = 1
        sprite.kind = "trash"
        self.trash_list.append(sprite)

    def spawn_net(self, lane: int, row_y: float) -> None:
        sprite = self.make_item(64, 26, (80, 145, 160, 210), lane, row_y)
        sprite.damage = 1
        sprite.kind = "net"
        self.net_list.append(sprite)

    def spawn_boat(self, lane: int, row_y: float) -> None:
        sprite = self.make_item(92, 34, (124, 84, 48, 255), lane, row_y)
        sprite.damage = 2
        sprite.kind = "boat"
        self.boat_list.append(sprite)

    def spawn_fish(self, lane: int, row_y: float) -> None:
        sprite = self.make_item(44, 20, (245, 215, 85, 255), lane, row_y)
        sprite.heal = 1
        sprite.points = 10
        sprite.kind = "fish"
        self.fish_list.append(sprite)

    def spawn_mystery(self, lane: int, row_y: float) -> None:
        sprite = self.make_item(48, 48, (150, 95, 185, 255), lane, row_y)
        sprite.kind = "mystery"
        self.mystery_list.append(sprite)

    def spawn_row(self) -> None:
        row_y = self.spawn_cursor + (ROW_HEIGHT / 2)
        occupied: set[int] = set()

        level_ratio = (self.level - 1) / (TOTAL_LEVELS - 1)
        heat_ratio = clamp(self.heat / HEAT_MAX, 0.0, 1.0)

        hazard_total = 1
        if self.level >= 4 and random.random() < 0.70:
            hazard_total += 1
        if self.level >= 7 and random.random() < 0.55:
            hazard_total += 1

        for _ in range(hazard_total):
            lane = self.pick_lane(occupied)
            occupied.add(lane)
            roll = random.random()
            if roll < 0.35:
                self.spawn_boat(lane, row_y)
            elif roll < 0.70:
                self.spawn_net(lane, row_y)
            else:
                self.spawn_trash(lane, row_y)

        fish_chance = clamp(0.46 - (heat_ratio * 0.30) + (level_ratio * 0.08), 0.12, 0.60)
        if random.random() < fish_chance:
            lane = self.pick_lane(occupied)
            occupied.add(lane)
            self.spawn_fish(lane, row_y)

        mystery_chance = 0.12 + (0.04 if self.level >= 5 else 0.0)
        if random.random() < mystery_chance:
            lane = self.pick_lane(occupied)
            occupied.add(lane)
            self.spawn_mystery(lane, row_y)

        self.spawn_cursor += ROW_HEIGHT

    def draw_background(self) -> None:
        progress_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        band_count = 6
        band_height = SCREEN_HEIGHT / band_count

        for band in range(band_count):
            band_ratio = band / max(1, band_count - 1)
            warm_to_cool = clamp((progress_ratio * 0.85) + (band_ratio * 0.15), 0.0, 1.0)
            top_color = lerp_color(WARM_COLOR, COOL_COLOR, warm_to_cool)
            bottom_color = lerp_color(DEEP_WATER, COOL_COLOR, band_ratio * 0.5 + progress_ratio * 0.25)
            color = lerp_color(top_color, bottom_color, 0.35)
            arcade.draw_lbwh_rectangle_filled(
                0,
                band * band_height,
                SCREEN_WIDTH,
                band_height + 1,
                color,
            )

        for wave in range(8):
            y = 30 + (wave * 70) + int((self.distance_traveled * 0.35) % 40)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, (255, 255, 255, 18), 1)

    def draw_mysteries(self) -> None:
        for mystery in self.mystery_list:
            arcade.draw_text(
                "?",
                mystery.center_x,
                mystery.center_y - 16,
                arcade.color.WHITE,
                26,
                bold=True,
                anchor_x="center",
            )

    def draw_trash(self) -> None:
        for trash in self.trash_list:
            arcade.draw_circle_filled(trash.center_x, trash.center_y, trash.width / 2, (116, 169, 232, 255))

    def draw_ui(self) -> None:
        arcade.draw_text(
            f"Level {self.level}/{TOTAL_LEVELS}",
            18,
            SCREEN_HEIGHT - 28,
            arcade.color.WHITE,
            14,
            bold=True,
        )
        arcade.draw_text(
            f"Score: {self.score}",
            18,
            SCREEN_HEIGHT - 48,
            arcade.color.WHITE,
            14,
        )
        arcade.draw_text(
            f"Distance: {int(self.distance_traveled)} / {DISTANCE_TO_ALASKA}",
            18,
            SCREEN_HEIGHT - 68,
            arcade.color.WHITE,
            14,
        )

        arcade.draw_text(
            "Health",
            18,
            42,
            arcade.color.WHITE,
            12,
        )
        for index in range(HEALTH_MAX):
            color = arcade.color.RED if index < self.health else arcade.color.DARK_GRAY
            arcade.draw_circle_filled(72 + (index * 30), 48, 10, color)

        heat_x = SCREEN_WIDTH - 240
        heat_y = 24
        heat_width = 210
        heat_ratio = clamp(self.heat / HEAT_MAX, 0.0, 1.0)
        arcade.draw_text("Heat", heat_x, heat_y + 20, arcade.color.WHITE, 12)
        arcade.draw_lbwh_rectangle_filled(heat_x, heat_y, heat_width, 14, (50, 50, 60, 220))
        arcade.draw_lbwh_rectangle_filled(
            heat_x,
            heat_y,
            heat_width * heat_ratio,
            14,
            lerp_color((100, 210, 120, 255), (240, 80, 65, 255), heat_ratio),
        )

        progress_x = SCREEN_WIDTH - 240
        progress_y = 56
        progress_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        arcade.draw_text("To Alaska", progress_x, progress_y + 20, arcade.color.WHITE, 12)
        arcade.draw_lbwh_rectangle_filled(progress_x, progress_y, 210, 14, (50, 50, 60, 220))
        arcade.draw_lbwh_rectangle_filled(
            progress_x,
            progress_y,
            210 * progress_ratio,
            14,
            lerp_color((255, 210, 90, 255), (105, 200, 140, 255), progress_ratio),
        )

        arcade.draw_text(
            "Arrow keys steer. R restarts after a win or loss.",
            SCREEN_WIDTH / 2,
            14,
            arcade.color.WHITE,
            11,
            anchor_x="center",
        )

        for message in self.messages:
            arcade.draw_text(
                message["text"],
                message["x"],
                message["y"],
                message["color"],
                18,
                bold=True,
                anchor_x="center",
            )

    def apply_collision_result(self, sprite, health_delta: int = 0, score_delta: int = 0, heat_delta: float = 0.0, text: str = "", color=arcade.color.WHITE) -> None:
        if health_delta:
            self.health = int(clamp(self.health + health_delta, 0, HEALTH_MAX))
        if score_delta:
            self.score += score_delta
        if heat_delta:
            self.heat = clamp(self.heat + heat_delta, 0.0, HEAT_MAX)
        if text:
            self.messages.append(
                {
                    "text": text,
                    "x": sprite.center_x,
                    "y": sprite.center_y,
                    "timer": 1.0,
                    "color": color,
                }
            )
        sprite.remove_from_sprite_lists()

    def resolve_collisions(self) -> None:
        for sprite in arcade.check_for_collision_with_list(self.player_sprite, self.fish_list):
            self.apply_collision_result(
                sprite,
                health_delta=sprite.heal,
                score_delta=sprite.points,
                heat_delta=-8.0,
                text="+FISH POD",
                color=arcade.color.GOLD,
            )

        for sprite in arcade.check_for_collision_with_list(self.player_sprite, self.mystery_list):
            if random.random() < 0.55:
                self.apply_collision_result(
                    sprite,
                    health_delta=2,
                    score_delta=15,
                    heat_delta=-10.0,
                    text="+2 HEARTS",
                    color=arcade.color.LIGHT_GREEN,
                )
            else:
                self.apply_collision_result(
                    sprite,
                    health_delta=-2,
                    score_delta=0,
                    heat_delta=2.0,
                    text="FISHERMAN!",
                    color=arcade.color.RED,
                )

        for sprite in arcade.check_for_collision_with_list(self.player_sprite, self.trash_list):
            self.apply_collision_result(
                sprite,
                health_delta=-1,
                heat_delta=1.0,
                text="-TRASH",
                color=arcade.color.LIGHT_GRAY,
            )

        for sprite in arcade.check_for_collision_with_list(self.player_sprite, self.net_list):
            self.apply_collision_result(
                sprite,
                health_delta=-1,
                heat_delta=1.0,
                text="-NET",
                color=arcade.color.AQUA,
            )

        for sprite in arcade.check_for_collision_with_list(self.player_sprite, self.boat_list):
            self.apply_collision_result(
                sprite,
                health_delta=-2,
                heat_delta=2.0,
                text="-BOAT",
                color=arcade.color.ORANGE_RED,
            )

    def update_messages(self, delta_time: float) -> None:
        for message in self.messages:
            message["y"] += 1.4
            message["timer"] -= delta_time
        self.messages = [message for message in self.messages if message["timer"] > 0]

    def update_player(self) -> None:
        if self.left_pressed:
            self.player_sprite.center_x -= PLAYER_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += PLAYER_SPEED

        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        if self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.right = SCREEN_WIDTH

        self.player_sprite.center_y = SCREEN_HEIGHT / 4

    def update_world(self, delta_time: float) -> None:
        frame_scale = delta_time * 60.0
        current_speed = BASE_SCROLL_SPEED + ((self.level - 1) * 0.35) + (self.heat * 0.015)
        travel = current_speed * frame_scale

        self.distance_traveled += travel
        self.spawn_cursor -= travel
        self.heat = clamp(self.heat + ((0.018 + (self.level * 0.004)) * frame_scale), 0.0, HEAT_MAX)

        for sprite_list in [self.trash_list, self.net_list, self.boat_list, self.fish_list, self.mystery_list]:
            for sprite in sprite_list:
                sprite.center_y -= travel
                if sprite.top < -60:
                    sprite.remove_from_sprite_lists()

        while self.spawn_cursor < SCREEN_HEIGHT + ROW_HEIGHT:
            self.spawn_row()

    def update_level_state(self) -> None:
        self.level = min(TOTAL_LEVELS, int(self.distance_traveled // DISTANCE_PER_LEVEL) + 1)

        if self.distance_traveled >= DISTANCE_TO_ALASKA:
            self.won = True

        if self.health <= 0 or self.heat >= HEAT_MAX:
            self.game_over = True

    def on_draw(self) -> None:
        self.clear()
        self.draw_background()
        self.draw_trash()
        self.net_list.draw()
        self.boat_list.draw()
        self.fish_list.draw()
        self.mystery_list.draw()
        self.draw_mysteries()
        self.player_list.draw()
        self.draw_ui()

        if self.game_over or self.won:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 170))
            title = "YOU MADE IT TO ALASKA" if self.won else "THE MIGRATION ENDED"
            subtitle = "Press R to swim again"
            arcade.draw_text(
                title,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 20,
                arcade.color.WHITE,
                32,
                bold=True,
                anchor_x="center",
            )
            arcade.draw_text(
                subtitle,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 25,
                arcade.color.LIGHT_GRAY,
                18,
                anchor_x="center",
            )

    def on_update(self, delta_time: float) -> None:
        if self.game_over or self.won:
            self.update_messages(delta_time)
            return

        self.update_level_state()
        self.update_world(delta_time)
        self.update_player()
        self.resolve_collisions()
        self.update_level_state()
        self.update_messages(delta_time)

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.R and (self.game_over or self.won):
            self.setup()

    def on_key_release(self, key, modifiers) -> None:
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView(window)
    window.show_view(view)
    view.setup()
    arcade.run()


if __name__ == "__main__":
    main()
