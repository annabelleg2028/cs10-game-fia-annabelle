import math
import random
import time
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

OCEAN_IMAGE_WIDTH = 1023
OCEAN_IMAGE_HEIGHT = 1537
OCEAN_TILE_WIDTH = SCREEN_WIDTH
OCEAN_TILE_HEIGHT = OCEAN_TILE_WIDTH * (OCEAN_IMAGE_HEIGHT / OCEAN_IMAGE_WIDTH)

GRID_COLUMNS = 8
SCROLL_SPEED = 5.0
MOVEMENT_SPEED = 8
PATROL_SPEED = 2

WHALE_SCALE = 0.13
FISH_SCALE = 0.07
PLAYER_START_Y = 120

HEALTH_MAX = 5
DISTANCE_TO_ALASKA = 6000
DISTANCE_PER_LEVEL = 600
TOTAL_LEVELS = 10

LANE_WIDTH = SCREEN_WIDTH / GRID_COLUMNS
ROW_HEIGHT = 80

PLAYER_HITBOX_WIDTH = 44
PLAYER_HITBOX_HEIGHT = 62


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def rectangles_overlap(a_center_x, a_center_y, a_width, a_height, b_center_x, b_center_y, b_width, b_height):
    return (
        abs(a_center_x - b_center_x) * 2 < (a_width + b_width)
        and abs(a_center_y - b_center_y) * 2 < (a_height + b_height)
    )


def circle_rectangle_overlap(circle_x, circle_y, radius, rect_x, rect_y, rect_width, rect_height):
    closest_x = clamp(circle_x, rect_x - rect_width / 2, rect_x + rect_width / 2)
    closest_y = clamp(circle_y, rect_y - rect_height / 2, rect_y + rect_height / 2)
    return (circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2 <= radius ** 2


def draw_heart(center_x, center_y, size, color):
    r = size * 0.45
    arcade.draw_circle_filled(center_x - r * 0.65, center_y + r * 0.2, r, color)
    arcade.draw_circle_filled(center_x + r * 0.65, center_y + r * 0.2, r, color)
    arcade.draw_triangle_filled(
        center_x - r * 1.15,
        center_y + r * 0.15,
        center_x + r * 1.15,
        center_y + r * 0.15,
        center_x,
        center_y - r * 1.45,
        color,
    )


def draw_trash(center_x, center_y, scale=1.0):
    radius = 13 * scale
    arcade.draw_circle_filled(center_x, center_y, radius, (170, 125, 70, 255))
    arcade.draw_circle_outline(center_x, center_y, radius + 2, arcade.color.BLACK, 2)
    arcade.draw_line(
        center_x - radius * 0.5,
        center_y - radius * 0.3,
        center_x + radius * 0.45,
        center_y + radius * 0.35,
        (80, 65, 50, 255),
        2,
    )


def draw_net(center_x, center_y, scale=1.0):
    width = 72 * scale
    height = 24 * scale
    arcade.draw_lbwh_rectangle_filled(
        center_x - width / 2,
        center_y - height / 2,
        width,
        height,
        (190, 210, 220, 210),
    )
    for i in range(4):
        x = center_x - width / 2 + (i + 1) * width / 5
        arcade.draw_line(x, center_y - height / 2, x, center_y + height / 2, (30, 80, 95, 130), 1)
    for i in range(2):
        y = center_y - height / 2 + (i + 1) * height / 3
        arcade.draw_line(center_x - width / 2, y, center_x + width / 2, y, (30, 80, 95, 130), 1)


def draw_boat(center_x, center_y, scale=1.0):
    width = 82 * scale
    height = 28 * scale
    arcade.draw_lbwh_rectangle_filled(
        center_x - width / 2,
        center_y - height / 2,
        width,
        height,
        (70, 78, 88, 255),
    )
    arcade.draw_lbwh_rectangle_filled(
        center_x - width * 0.28,
        center_y + height * 0.15,
        width * 0.22,
        height * 0.35,
        (120, 90, 55, 255),
    )


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        self.ocean = arcade.load_texture(OCEAN_IMAGE)
        self.whale_texture = arcade.load_texture(WHALE_IMAGE)
        self.fish_textures = [arcade.load_texture(path) for path in FISH_IMAGES]
        self.player_sprite = None

        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()

        self.left_pressed = False
        self.right_pressed = False

        self.health = HEALTH_MAX
        self.score = 0
        self.is_game_over = False
        self.won = False
        self.last_hit_time = 0
        self.messages = []

        self.distance_traveled = 0.0
        self.next_spawn_y = 0.0
        self.prev_hazard_cols = []
        self.rows_since_last_patrol = 0
        self.background_offset = 0.0

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(WHALE_IMAGE, scale=WHALE_SCALE)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_sprite.angle = 90
        self.player_list.append(self.player_sprite)

        self.left_pressed = False
        self.right_pressed = False
        self.health = HEALTH_MAX
        self.score = 0
        self.is_game_over = False
        self.won = False
        self.last_hit_time = 0
        self.messages = []
        self.distance_traveled = 0.0
        self.next_spawn_y = 0.0
        self.prev_hazard_cols = []
        self.rows_since_last_patrol = 0
        self.background_offset = 0.0

        while self.next_spawn_y < SCREEN_HEIGHT + ROW_HEIGHT:
            self.spawn_row()

    @property
    def row_height(self):
        return ROW_HEIGHT

    def spawn_hazard(self, col, hazard_kind=None):
        hazard_kind_roll = random.random()
        if hazard_kind == "boat":
            hazard = arcade.SpriteSolidColor(82, 28, (70, 78, 88, 255))
            hazard.kind = "boat"
            hazard.damage = 2
        elif hazard_kind_roll < 0.55:
            hazard = arcade.SpriteSolidColor(34, 34, (170, 125, 70, 255))
            hazard.kind = "trash"
            hazard.damage = 1
        else:
            hazard = arcade.SpriteSolidColor(76, 26, (190, 210, 220, 210))
            hazard.kind = "net"
            hazard.damage = 1

        hazard.alpha = 0
        hazard.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        hazard.center_y = self.next_spawn_y + (ROW_HEIGHT / 2)
        hazard.change_x = 0
        self.hazard_list.append(hazard)
        return hazard

    def spawn_token(self, col, is_school=False):
        texture_path = random.choice(FISH_IMAGES)
        token = arcade.Sprite(texture_path, scale=FISH_SCALE * (1.15 if is_school else 1.0))
        token.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        token.center_y = self.next_spawn_y + (ROW_HEIGHT / 2)
        token.value = 10 if is_school else 5
        token.kind = "fish"
        self.token_list.append(token)
        return token

    def spawn_row(self):
        all_cols = list(range(GRID_COLUMNS))
        occupied_cols = []
        distance_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)

        if self.rows_since_last_patrol >= 0 and random.random() < (0.24 + distance_ratio * 0.18):
            h_col = random.choice(all_cols)
            occupied_cols.append(h_col)
            hazard = self.spawn_hazard(h_col, "boat")
            hazard.change_x = PATROL_SPEED if random.random() > 0.5 else -PATROL_SPEED
            self.prev_hazard_cols = [h_col]
            self.rows_since_last_patrol = 0
        else:
            self.rows_since_last_patrol += 1
            banned_cols = set()
            for pc in self.prev_hazard_cols:
                banned_cols.update([pc, pc - 1, pc + 1])

            safe_choices = [c for c in all_cols if c not in banned_cols]
            if not safe_choices:
                safe_choices = [c for c in all_cols if c not in self.prev_hazard_cols]
            if not safe_choices:
                safe_choices = all_cols

            hazard_total = 1
            if distance_ratio > 0.35 and random.random() < 0.6:
                hazard_total += 1
            if distance_ratio > 0.70 and random.random() < 0.4:
                hazard_total += 1

            for _ in range(min(hazard_total, len(safe_choices))):
                h_col = random.choice(safe_choices)
                occupied_cols.append(h_col)
                safe_choices.remove(h_col)
                self.spawn_hazard(h_col)

            self.prev_hazard_cols = occupied_cols

            remaining_cols = [c for c in all_cols if c not in occupied_cols]
            fish_chance = clamp(0.48 - distance_ratio * 0.18 + (0.18 if self.health <= 2 else 0.0), 0.18, 0.72)
            if remaining_cols and random.random() < fish_chance:
                token_col = random.choice(remaining_cols)
                occupied_cols.append(token_col)
                remaining_cols.remove(token_col)
                self.spawn_token(token_col)

            if remaining_cols and random.random() < 0.32 and distance_ratio > 0.15:
                lane = random.choice(remaining_cols)
                neighbor_lanes = [lane]
                if lane > 0:
                    neighbor_lanes.append(lane - 1)
                if lane < GRID_COLUMNS - 1:
                    neighbor_lanes.append(lane + 1)
                for token_lane in neighbor_lanes[:2]:
                    if token_lane in remaining_cols:
                        occupied_cols.append(token_lane)
                        remaining_cols.remove(token_lane)
                        self.spawn_token(token_lane, is_school=True)

        self.next_spawn_y += self.row_height

    def draw_ocean_background(self):
        y = self.background_offset - OCEAN_TILE_HEIGHT
        while y < SCREEN_HEIGHT:
            arcade.draw_texture_rect(
                self.ocean,
                arcade.LBWH(0, y, OCEAN_TILE_WIDTH, OCEAN_TILE_HEIGHT),
            )
            y += OCEAN_TILE_HEIGHT

        progress = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        red = int(90 - 45 * progress)
        green = int(120 + 65 * progress)
        blue = int(150 + 55 * progress)
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (red, green, blue, 35))

    def draw_grid_lines(self):
        line_color = (210, 245, 250, 50)
        for i in range(GRID_COLUMNS + 1):
            x = i * LANE_WIDTH
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, line_color, 2)

        line_y = self.next_spawn_y % self.row_height
        while line_y < SCREEN_HEIGHT:
            arcade.draw_line(0, line_y, SCREEN_WIDTH, line_y, line_color, 2)
            line_y += self.row_height

    def draw_distance_scale(self):
        scale_x = SCREEN_WIDTH - 34
        bottom = 125
        top = 520
        arcade.draw_line(scale_x, bottom, scale_x, top, arcade.color.WHITE, 2)
        arcade.draw_text("Distance", scale_x - 8, top + 10, arcade.color.WHITE, 11, anchor_x="right")
        arcade.draw_text("0", scale_x - 22, bottom - 8, arcade.color.WHITE, 10, anchor_x="right")
        arcade.draw_text("Alaska", scale_x - 22, top - 8, arcade.color.WHITE, 10, anchor_x="right")

        for mark in range(1000, DISTANCE_TO_ALASKA + 1, 1000):
            ratio = mark / DISTANCE_TO_ALASKA
            y = bottom + ((top - bottom) * ratio)
            arcade.draw_line(scale_x - 8, y, scale_x + 8, y, arcade.color.WHITE, 2)
            arcade.draw_text(f"{mark // 1000}k", scale_x - 24, y - 6, arcade.color.LIGHT_GRAY, 10, anchor_x="right")

        marker_y = bottom + ((top - bottom) * clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0))
        arcade.draw_circle_filled(scale_x, marker_y, 7, (120, 220, 160, 255))

    def draw_hud_hearts(self):
        arcade.draw_text("Health", 18, 42, arcade.color.WHITE, 12)
        for i in range(HEALTH_MAX):
            color = arcade.color.RED if i < self.health else (110, 30, 30, 255)
            draw_heart(70 + (i * 30), 48, 12, color)

    def draw_ui(self):
        level = min(TOTAL_LEVELS, int(self.distance_traveled // DISTANCE_PER_LEVEL) + 1)
        arcade.draw_lbwh_rectangle_filled(12, 540, 330, 48, (0, 40, 70, 170))
        arcade.draw_text(f"Score: {self.score}", 24, 556, arcade.color.WHITE, 16, bold=True)
        arcade.draw_text(f"Level: {level}/{TOTAL_LEVELS}", 145, 556, arcade.color.WHITE, 16, bold=True)
        arcade.draw_text(
            f"{int(clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0) * 100)}% to Alaska",
            250,
            556,
            arcade.color.WHITE,
            13,
        )
        self.draw_hud_hearts()
        self.draw_distance_scale()

        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 18, bold=True, anchor_x="center")

    def draw_hazard(self, hazard):
        if hazard.kind == "trash":
            draw_trash(hazard.center_x, hazard.center_y, 1.0)
        elif hazard.kind == "boat":
            draw_boat(hazard.center_x, hazard.center_y, 1.0)
        else:
            draw_net(hazard.center_x, hazard.center_y, 1.0)

    def touches_visible_hazard(self, hazard):
        player_x = self.player_sprite.center_x
        player_y = self.player_sprite.center_y

        if hazard.kind == "trash":
            return circle_rectangle_overlap(
                hazard.center_x,
                hazard.center_y,
                15,
                player_x,
                player_y,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )

        if hazard.kind == "boat":
            return rectangles_overlap(
                player_x,
                player_y,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
                hazard.center_x,
                hazard.center_y + 4,
                82,
                38,
            )

        return rectangles_overlap(
            player_x,
            player_y,
            PLAYER_HITBOX_WIDTH,
            PLAYER_HITBOX_HEIGHT,
            hazard.center_x,
            hazard.center_y,
            72,
            24,
        )

    def resolve_collisions(self):
        curr_time = time.time()
        invincible = (curr_time - self.last_hit_time) < 1.0
        self.player_sprite.alpha = 160 if invincible else 255

        if not invincible:
            hits = [hazard for hazard in self.hazard_list if self.touches_visible_hazard(hazard)]
            if hits:
                damage = max(hit.damage for hit in hits)
                self.health -= damage
                self.last_hit_time = curr_time
                self.add_message(f"-{damage} HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)

        hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for fish in hits:
            self.score += fish.value
            self.health = min(HEALTH_MAX, self.health + 1)
            self.distance_traveled = min(DISTANCE_TO_ALASKA, self.distance_traveled + 10)
            self.add_message("+FISH", fish.center_x, fish.center_y, arcade.color.GOLD)
            fish.remove_from_sprite_lists()

    def update_messages(self, delta_time):
        for msg in self.messages:
            msg["y"] += 1.5
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

    def on_draw(self):
        self.clear()
        self.draw_ocean_background()
        self.draw_grid_lines()

        for hazard in self.hazard_list:
            self.draw_hazard(hazard)
        self.token_list.draw()
        self.player_list.draw()
        self.draw_ui()

        if self.is_game_over or self.won:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 180))
            title = "YOU MADE IT TO ALASKA" if self.won else "GAME OVER"
            arcade.draw_text(title, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10, arcade.color.WHITE, 44, anchor_x="center", bold=True)
            arcade.draw_text("Press R to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 35, arcade.color.LIGHT_GRAY, 18, anchor_x="center")

    def on_update(self, delta_time):
        if self.is_game_over or self.won:
            self.update_messages(delta_time)
            return

        distance_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        wave = 1.0 + (0.25 * math.sin(self.distance_traveled / 350.0))
        current_scroll = clamp(SCROLL_SPEED + (distance_ratio * 2.8) + wave, 4.0, 9.5)

        self.distance_traveled += current_scroll
        self.next_spawn_y -= current_scroll
        self.background_offset = (self.background_offset - current_scroll * 0.65) % OCEAN_TILE_HEIGHT

        if self.left_pressed:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += MOVEMENT_SPEED
        self.player_sprite.angle = 90

        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        if self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.right = SCREEN_WIDTH
        self.player_sprite.center_y = PLAYER_START_Y

        for hazard in self.hazard_list:
            hazard.center_y -= current_scroll
            hazard.center_x += hazard.change_x
            if hazard.left < 0 or hazard.right > SCREEN_WIDTH:
                hazard.change_x *= -1

        for token in self.token_list:
            token.center_y -= current_scroll

        while self.next_spawn_y < SCREEN_HEIGHT + self.row_height:
            self.spawn_row()

        for item_list in [self.hazard_list, self.token_list]:
            for item in item_list:
                if item.top < -60:
                    item.remove_from_sprite_lists()

        self.resolve_collisions()

        if self.health <= 0:
            self.is_game_over = True
        if self.distance_traveled >= DISTANCE_TO_ALASKA:
            self.won = True

        self.update_messages(delta_time)

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.0, "color": color})

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key == arcade.key.R and (self.is_game_over or self.won):
            self.setup()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    view.setup()
    arcade.run()


if __name__ == "__main__":
    main()
