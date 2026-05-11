import math
import random
import textwrap
import time
from pathlib import Path

import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Grey Whale Migration"

ASSET_DIR = Path(__file__).parent
OCEAN_IMAGE = ASSET_DIR / "ocean.png"
WHALE_IMAGE = ASSET_DIR / "whale.png"
HEART_IMAGE = ASSET_DIR / "heart.png"
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
SCROLL_SPEED = 3.4
MOVEMENT_SPEED = 8
PATROL_SPEED = 2

WHALE_SCALE = 0.13
FISH_SCALE = 0.07
PLAYER_START_Y = 120

TOTAL_LEVELS = 14
HEALTH_MAX = 5
DISTANCE_PER_LEVEL = 3800
DISTANCE_TO_ALASKA = DISTANCE_PER_LEVEL * TOTAL_LEVELS

LANE_WIDTH = SCREEN_WIDTH / GRID_COLUMNS
ROW_HEIGHT = 80

PLAYER_HITBOX_WIDTH = 44
PLAYER_HITBOX_HEIGHT = 62
WHALE_FORWARD_ANGLE = 0
GAME_FONT = ("Italianno", "Italiana", "Georgia", "Times New Roman", "Arial")

LEVEL_GRADIENTS = [
    ((42, 140, 170), (16, 74, 130)),
    ((62, 175, 140), (24, 98, 122)),
    ((58, 110, 200), (24, 60, 150)),
    ((125, 150, 210), (52, 78, 160)),
    ((70, 175, 190), (20, 102, 145)),
    ((145, 172, 125), (55, 118, 118)),
    ((92, 150, 215), (30, 82, 178)),
    ((135, 132, 205), (58, 68, 155)),
    ((82, 175, 150), (26, 110, 128)),
    ((155, 165, 190), (62, 86, 145)),
    ((105, 188, 170), (36, 128, 140)),
    ((90, 142, 218), (30, 82, 188)),
    ((150, 155, 215), (62, 80, 178)),
    ((165, 200, 210), (65, 132, 185)),
]

LESSONS = {
    "fish": {
        "title": "Fish",
        "body": "Fish give the whale energy for the long migration. In the real ocean, grey whales feed on tiny animals and need healthy feeding grounds near Alaska.",
    },
    "net": {
        "title": "Fishing Net",
        "body": "Lost or active fishing gear can trap whales as they migrate. Entanglement can make it hard to swim, feed, or surface for air.",
    },
    "boat": {
        "title": "Shipping Boat",
        "body": "Grey whales travel through busy coastal waters. Large ships can injure whales, especially when migration routes cross shipping lanes.",
    },
    "trash": {
        "title": "Ocean Trash",
        "body": "Plastic and other trash can be swallowed or can injure marine animals. Keeping waste out of rivers and beaches helps protect the migration route.",
    },
    "food_trash": {
        "title": "Hidden Trash",
        "body": "Not everything floating in the ocean is food. Trash can look like prey, but eating it can hurt whales and the food web they depend on.",
    },
}

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


def wrap_panel_lines(lines, panel_width, font_size, side_padding=68):
    characters_per_line = max(12, int((panel_width - side_padding) / (font_size * 0.58)))
    wrapped = []
    for paragraph in lines:
        wrapped.extend(textwrap.wrap(paragraph, width=characters_per_line, break_long_words=True))
        wrapped.append("")
    if wrapped:
        wrapped.pop()
    return wrapped


def draw_game_text(*args, **kwargs):
    kwargs.setdefault("font_name", GAME_FONT)
    arcade.draw_text(*args, **kwargs)


def draw_panel(center_x, center_y, width, height, title, lines, footer):
    left = center_x - width / 2
    bottom = center_y - height / 2
    arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, (5, 28, 45, 232))
    arcade.draw_lbwh_rectangle_outline(left, bottom, width, height, (170, 230, 240, 255), 2)

    title_font_size = 28 if len(title) <= 24 else 24
    title_lines = wrap_panel_lines([title], width, title_font_size, side_padding=86)[:2]
    title_y = bottom + height - 38
    for line in title_lines:
        draw_game_text(line, center_x, title_y, arcade.color.WHITE, title_font_size, anchor_x="center", bold=True)
        title_y -= title_font_size + 5

    footer_font_size = 15
    footer_lines = wrap_panel_lines([footer], width, footer_font_size, side_padding=86)
    while len(footer_lines) > 2 and footer_font_size > 11:
        footer_font_size -= 1
        footer_lines = wrap_panel_lines([footer], width, footer_font_size, side_padding=86)
    footer_lines = footer_lines[:2]
    footer_y = bottom + 34 + ((len(footer_lines) - 1) * (footer_font_size - 5))
    for line in footer_lines:
        draw_game_text(line, center_x, footer_y, arcade.color.GOLD, footer_font_size, anchor_x="center", bold=True)
        footer_y -= footer_font_size + 5

    text_y = min(title_y - 20, bottom + height - 92)
    footer_top = bottom + 68
    body_font_size = 15
    line_spacing = 22
    body_lines = wrap_panel_lines(lines, width, body_font_size, side_padding=76)
    available_lines = max(1, int((text_y - footer_top) // line_spacing) + 1)
    while len(body_lines) > available_lines and body_font_size > 10:
        body_font_size -= 1
        line_spacing = body_font_size + 6
        body_lines = wrap_panel_lines(lines, width, body_font_size, side_padding=76)
        available_lines = max(1, int((text_y - footer_top) // line_spacing) + 1)

    for line in body_lines:
        if text_y < footer_top:
            break
        if line:
            draw_game_text(line, left + 34, text_y, (225, 245, 245, 255), body_font_size)
        text_y -= line_spacing


def draw_heart(center_x, center_y, size, color):
    points = []
    scale = size / 18
    for degree in range(0, 360, 12):
        angle = math.radians(degree)
        x = 16 * (math.sin(angle) ** 3)
        y = 13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle)
        points.append((center_x + x * scale, center_y + (y - 2) * scale))
    arcade.draw_polygon_filled(points, color)
    arcade.draw_polygon_outline(points, (255, 235, 235, 180), max(1, int(size * 0.08)))


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
        self.heart_texture = arcade.load_texture(HEART_IMAGE)
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
        self.game_state = "intro"
        self.current_lesson = None
        self.lesson_return_state = "playing"
        self.seen_lessons = set()
        self.last_level = 1
        self.level_banner_timer = 0.0
        self.level_banner_text = ""

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
        self.player_sprite.angle = WHALE_FORWARD_ANGLE
        self.player_list.append(self.player_sprite)

        self.left_pressed = False
        self.right_pressed = False
        self.health = HEALTH_MAX
        self.score = 0
        self.is_game_over = False
        self.won = False
        self.last_hit_time = 0
        self.messages = []
        self.game_state = "intro"
        self.current_lesson = None
        self.lesson_return_state = "playing"
        self.seen_lessons = set()
        self.last_level = 1
        self.level_banner_timer = 0.0
        self.level_banner_text = ""
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

    @property
    def current_level(self):
        return min(TOTAL_LEVELS, int(self.distance_traveled // DISTANCE_PER_LEVEL) + 1)

    @property
    def level_ratio(self):
        return (self.current_level - 1) / (TOTAL_LEVELS - 1)

    def choose_hazard_kind(self):
        if self.current_level == 1:
            return "trash" if random.random() < 0.50 else "net"
        if self.current_level == 2:
            return "trash" if random.random() < 0.42 else "net"

        roll = random.random()
        if roll < 0.42:
            return "net"
        if roll < 0.74:
            return "trash"
        return "boat"

    def start_migration(self):
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()
        self.health = HEALTH_MAX
        self.score = 0
        self.is_game_over = False
        self.won = False
        self.messages = []
        self.current_lesson = None
        self.distance_traveled = 0.0
        self.next_spawn_y = 0.0
        self.prev_hazard_cols = []
        self.rows_since_last_patrol = 0
        self.background_offset = 0.0
        self.last_level = 1
        self.level_banner_timer = 0.0
        self.level_banner_text = ""
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_sprite.angle = WHALE_FORWARD_ANGLE

        while self.next_spawn_y < SCREEN_HEIGHT + ROW_HEIGHT:
            self.spawn_row()

        self.game_state = "playing"

    def spawn_hazard(self, col, hazard_kind=None):
        if hazard_kind == "boat":
            hazard = arcade.SpriteSolidColor(82, 28, (70, 78, 88, 255))
            hazard.kind = "boat"
            hazard.damage = 2
        elif hazard_kind == "trash":
            hazard = arcade.SpriteSolidColor(34, 34, (170, 125, 70, 255))
            hazard.kind = "trash"
            hazard.damage = 1
        elif hazard_kind == "net":
            hazard = arcade.SpriteSolidColor(76, 26, (190, 210, 220, 210))
            hazard.kind = "net"
            hazard.damage = 1
        else:
            return self.spawn_hazard(col, self.choose_hazard_kind())

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
        hidden_trash_chance = clamp(0.15 + (self.level_ratio * 0.30), 0.15, 0.45)
        token.value = random.choice([-10, -5]) if random.random() < hidden_trash_chance else random.choice([5, 10, 15, 20])
        token.kind = "fish"
        token.is_trash = token.value < 0
        self.token_list.append(token)
        return token

    def spawn_row(self):
        all_cols = list(range(GRID_COLUMNS))
        occupied_cols = []
        distance_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        difficulty = self.level_ratio

        can_spawn_boats = self.current_level >= 3
        if can_spawn_boats and self.rows_since_last_patrol >= 0 and random.random() < (0.12 + difficulty * 0.38):
            h_col = random.choice(all_cols)
            occupied_cols.append(h_col)
            hazard = self.spawn_hazard(h_col, "boat")
            patrol_speed = PATROL_SPEED + difficulty * 2.2
            hazard.change_x = patrol_speed if random.random() > 0.5 else -patrol_speed
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
            if self.current_level >= 3 and random.random() < (0.28 + difficulty * 0.42):
                hazard_total += 1
            if self.current_level >= 5 and random.random() < (0.18 + difficulty * 0.38):
                hazard_total += 1
            if self.current_level >= 9 and random.random() < (0.12 + difficulty * 0.34):
                hazard_total += 1
            if self.current_level >= 12 and random.random() < (0.10 + difficulty * 0.24):
                hazard_total += 1

            for _ in range(min(hazard_total, len(safe_choices))):
                h_col = random.choice(safe_choices)
                occupied_cols.append(h_col)
                safe_choices.remove(h_col)
                self.spawn_hazard(h_col)

            self.prev_hazard_cols = occupied_cols

            remaining_cols = [c for c in all_cols if c not in occupied_cols]
            fish_chance = clamp(0.56 - difficulty * 0.34 + (0.16 if self.health <= 2 else 0.0), 0.14, 0.72)
            if self.current_level >= 2 and remaining_cols and random.random() < fish_chance:
                token_col = random.choice(remaining_cols)
                occupied_cols.append(token_col)
                remaining_cols.remove(token_col)
                self.spawn_token(token_col)

            school_chance = clamp(0.32 - difficulty * 0.18, 0.10, 0.32)
            if self.current_level >= 2 and remaining_cols and random.random() < school_chance and distance_ratio > 0.15:
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

        level_index = self.current_level - 1
        local_progress = (self.distance_traveled % DISTANCE_PER_LEVEL) / DISTANCE_PER_LEVEL
        top_start, bottom_start = LEVEL_GRADIENTS[level_index]
        top_end, bottom_end = LEVEL_GRADIENTS[min(level_index + 1, TOTAL_LEVELS - 1)]
        top_color = tuple(
            int(top_start[i] + ((top_end[i] - top_start[i]) * local_progress))
            for i in range(3)
        )
        bottom_color = tuple(
            int(bottom_start[i] + ((bottom_end[i] - bottom_start[i]) * local_progress))
            for i in range(3)
        )
        bands = 24
        band_height = SCREEN_HEIGHT / bands
        for band in range(bands):
            ratio = band / max(1, bands - 1)
            red = int(bottom_color[0] + ((top_color[0] - bottom_color[0]) * ratio))
            green = int(bottom_color[1] + ((top_color[1] - bottom_color[1]) * ratio))
            blue = int(bottom_color[2] + ((top_color[2] - bottom_color[2]) * ratio))
            arcade.draw_lbwh_rectangle_filled(
                0,
                band * band_height,
                SCREEN_WIDTH,
                band_height + 1,
                (red, green, blue, 118),
            )

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
        panel_left = SCREEN_WIDTH - 156
        panel_bottom = 92
        panel_width = 132
        panel_height = 410
        arcade.draw_lbwh_rectangle_filled(panel_left, panel_bottom, panel_width, panel_height, (0, 35, 55, 150))
        arcade.draw_text("Migration", panel_left + panel_width / 2, panel_bottom + panel_height - 28, arcade.color.WHITE, 13, anchor_x="center", bold=True)

        route = [
            (panel_left + 82, panel_bottom + 54),
            (panel_left + 58, panel_bottom + 130),
            (panel_left + 70, panel_bottom + 205),
            (panel_left + 48, panel_bottom + 285),
            (panel_left + 76, panel_bottom + 356),
        ]
        for start, end in zip(route, route[1:]):
            arcade.draw_line(start[0], start[1], end[0], end[1], (200, 235, 230, 255), 4)

        labels = [
            ("Baja", route[0]),
            ("CA", route[1]),
            ("OR/WA", route[2]),
            ("B.C.", route[3]),
            ("Alaska", route[4]),
        ]
        for label, (x, y) in labels:
            arcade.draw_circle_filled(x, y, 5, arcade.color.WHITE)
            arcade.draw_text(label, panel_left + 8, y - 7, (220, 245, 245, 255), 10)

        progress = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        segment_progress = progress * (len(route) - 1)
        segment_index = min(len(route) - 2, int(segment_progress))
        local_progress = segment_progress - segment_index
        start = route[segment_index]
        end = route[segment_index + 1]
        marker_x = start[0] + ((end[0] - start[0]) * local_progress)
        marker_y = start[1] + ((end[1] - start[1]) * local_progress)
        arcade.draw_circle_filled(marker_x, marker_y, 8, (120, 220, 160, 255))
        arcade.draw_circle_outline(marker_x, marker_y, 10, arcade.color.WHITE, 2)
        arcade.draw_text(f"{int(progress * 100)}%", panel_left + panel_width / 2, panel_bottom + 14, arcade.color.GOLD, 12, anchor_x="center", bold=True)

    def draw_hud_hearts(self):
        panel_left = SCREEN_WIDTH - 360
        heart_gap = 28
        hearts_width = (HEALTH_MAX - 1) * heart_gap
        start_x = panel_left + 230 - (hearts_width / 2)
        arcade.draw_text("Health", start_x - 14, SCREEN_HEIGHT - 31, arcade.color.WHITE, 12, anchor_x="right")
        for i in range(HEALTH_MAX):
            color = arcade.color.RED if i < self.health else (110, 30, 30, 255)
            draw_heart(start_x + (i * heart_gap), SCREEN_HEIGHT - 25, 12, color)

    def draw_ui(self):
        level = min(TOTAL_LEVELS, int(self.distance_traveled // DISTANCE_PER_LEVEL) + 1)
        arcade.draw_lbwh_rectangle_filled(12, 540, 330, 48, (0, 40, 70, 170))
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH - 360, 540, 336, 48, (0, 40, 70, 170))
        arcade.draw_text(f"Level: {level}/{TOTAL_LEVELS}", 24, 556, arcade.color.WHITE, 16, bold=True)
        arcade.draw_text(
            f"Distance: {int(self.distance_traveled)} / {DISTANCE_TO_ALASKA} mi",
            145,
            556,
            arcade.color.WHITE,
            13,
        )
        arcade.draw_text(f"Points: {self.score}", SCREEN_WIDTH - 348, 556, arcade.color.WHITE, 16, bold=True)
        self.draw_hud_hearts()
        self.draw_distance_scale()

        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 18, bold=True, anchor_x="center")

        if self.level_banner_timer > 0:
            alpha = int(218 * clamp(self.level_banner_timer / 2.4, 0.0, 1.0))
            arcade.draw_lbwh_rectangle_filled(190, 254, 420, 92, (0, 35, 55, alpha))
            arcade.draw_lbwh_rectangle_outline(190, 254, 420, 92, (170, 230, 240, min(255, alpha + 30)), 2)
            banner_font_size = 24 if len(self.level_banner_text) <= 28 else 19
            banner_lines = wrap_panel_lines([self.level_banner_text], 420, banner_font_size, side_padding=56)[:2]
            banner_y = 308 + ((len(banner_lines) - 1) * 12)
            for line in banner_lines:
                arcade.draw_text(
                    line,
                    SCREEN_WIDTH / 2,
                    banner_y,
                    arcade.color.WHITE,
                    banner_font_size,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                )
                banner_y -= banner_font_size + 5

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

    def start_lesson(self, lesson_key, return_state="playing"):
        if lesson_key in self.seen_lessons:
            return False
        self.seen_lessons.add(lesson_key)
        self.current_lesson = LESSONS[lesson_key]
        self.lesson_return_state = return_state
        self.game_state = "lesson"
        self.left_pressed = False
        self.right_pressed = False
        return True

    def draw_intro(self):
        lines = [
            "You are a grey whale migrating north from the warm Baja California breeding lagoons toward cold feeding waters near Alaska.",
            "Your objective is to reach Alaska. Level 1 has trash and fishing nets, Level 2 adds fish that may hide trash, and Level 3 adds shipping boats.",
            "The first time you bump into each kind of object, the game pauses to teach you what it means. Hazard lessons are free: you learn without losing a heart.",
            "Move with A/D or the arrow keys. Eat fish for hidden points and follow the coastal route on the right.",
        ]
        draw_panel(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 640, 430, "Grey Whale Migration", lines, "Press SPACE to start")

    def draw_lesson(self):
        if not self.current_lesson:
            return
        title = self.current_lesson["title"]
        draw_panel(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            590,
            310,
            title,
            [self.current_lesson["body"]],
            "Press SPACE to continue",
        )

    def draw_end_explanation(self):
        if self.won:
            title = "You Made It To Alaska"
            lines = [
                "Success! Grey whales make one of the longest migrations of any mammal, traveling between breeding lagoons in Mexico and feeding grounds near Alaska.",
                "People can help by using less single-use plastic, picking up beach and river trash, choosing sustainable seafood, and supporting whale-safe shipping speeds.",
                "Reporting entangled or injured marine mammals to local rescue groups also helps experts respond safely.",
            ]
        else:
            title = "Migration Stopped"
            lines = [
                "During migration, whales face many human-made threats. Pollution, fishing gear, and ships can turn a long natural journey into a dangerous one.",
                "People can help by keeping trash out of waterways, recycling fishing line, supporting cleaner harbors, and giving whales space from boats.",
            ]
        draw_panel(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 650, 405, title, lines, "Press R to restart")

    def resolve_collisions(self):
        curr_time = time.time()
        invincible = (curr_time - self.last_hit_time) < 1.0
        self.player_sprite.alpha = 160 if invincible else 255

        if not invincible:
            hits = [hazard for hazard in self.hazard_list if self.touches_visible_hazard(hazard)]
            if hits:
                lesson_key = hits[0].kind
                if lesson_key not in self.seen_lessons:
                    hits[0].remove_from_sprite_lists()
                    self.last_hit_time = curr_time
                    if self.start_lesson(lesson_key):
                        return

                damage = max(hit.damage for hit in hits)
                self.health -= damage
                self.last_hit_time = curr_time
                self.add_message(f"-{damage} HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)
                self.start_lesson(lesson_key)
                if self.game_state == "lesson":
                    return

        hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for fish in hits:
            lesson_key = "food_trash" if fish.is_trash else "fish"
            if fish.value < 0 and lesson_key not in self.seen_lessons:
                fish.remove_from_sprite_lists()
                if self.start_lesson(lesson_key):
                    return

            self.score += fish.value
            if fish.value > 0:
                self.health = min(HEALTH_MAX, self.health + 1)
                self.distance_traveled = min(DISTANCE_TO_ALASKA, self.distance_traveled + 10)
                self.add_message(f"+{fish.value}", fish.center_x, fish.center_y, arcade.color.GOLD)
            else:
                self.add_message(str(fish.value), fish.center_x, fish.center_y, arcade.color.RED)
                self.start_lesson(lesson_key)
            fish.remove_from_sprite_lists()
            if fish.value > 0:
                self.start_lesson(lesson_key)
            if self.game_state == "lesson":
                return

    def update_messages(self, delta_time):
        for msg in self.messages:
            msg["y"] += 1.5
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]
        if self.level_banner_timer > 0:
            self.level_banner_timer = max(0.0, self.level_banner_timer - delta_time)

    def update_level_banner(self):
        if self.current_level > self.last_level:
            self.last_level = self.current_level
            if self.current_level == 2:
                self.level_banner_text = "Level 2: Fish enter the route"
            elif self.current_level == 3:
                self.level_banner_text = "Level 3: Shipping boats enter the route"
            else:
                self.level_banner_text = f"Level {self.current_level}"
            self.level_banner_timer = 2.4

    def on_draw(self):
        self.clear()
        self.draw_ocean_background()
        self.draw_grid_lines()

        for hazard in self.hazard_list:
            self.draw_hazard(hazard)
        self.token_list.draw()
        self.player_list.draw()
        self.draw_ui()

        if self.game_state == "intro":
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 175))
            self.draw_intro()
        elif self.game_state == "lesson":
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 175))
            self.draw_lesson()
        elif self.is_game_over or self.won:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))
            self.draw_end_explanation()

    def on_update(self, delta_time):
        if self.game_state != "playing" or self.is_game_over or self.won:
            self.update_messages(delta_time)
            return

        difficulty = self.level_ratio
        wave = 1.0 + (0.25 * math.sin(self.distance_traveled / 350.0))
        current_scroll = clamp(SCROLL_SPEED + ((difficulty ** 1.35) * 4.8) + (wave * 0.35), 3.2, 8.8)

        self.distance_traveled += current_scroll
        self.next_spawn_y -= current_scroll
        self.background_offset = (self.background_offset - current_scroll * 0.65) % OCEAN_TILE_HEIGHT

        if self.left_pressed:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += MOVEMENT_SPEED
        self.player_sprite.angle = WHALE_FORWARD_ANGLE

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
        self.update_level_banner()

        if self.health <= 0:
            self.is_game_over = True
        if self.distance_traveled >= DISTANCE_TO_ALASKA:
            self.won = True

        self.update_messages(delta_time)

    def update_player_controls(self):
        if self.left_pressed:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += MOVEMENT_SPEED
        self.player_sprite.angle = WHALE_FORWARD_ANGLE

        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        if self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.right = SCREEN_WIDTH
        self.player_sprite.center_y = PLAYER_START_Y

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.0, "color": color})

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.SPACE, arcade.key.ENTER):
            if self.game_state == "intro":
                self.start_migration()
            elif self.game_state == "lesson":
                self.current_lesson = None
                self.last_hit_time = time.time()
                self.game_state = "playing"
        elif self.game_state != "playing":
            return
        elif key in (arcade.key.LEFT, arcade.key.A):
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
