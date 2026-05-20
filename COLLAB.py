import math
import random
import textwrap
import time
from pathlib import Path

import arcade
try:
    from PIL import Image
except ImportError:  # pragma: no cover - fallback when Pillow is unavailable
    Image = None


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Grey Whale Migration"

ASSET_DIR = Path(__file__).parent
OCEAN_IMAGE = ASSET_DIR / "ocean.png"
WHALE_IMAGE = ASSET_DIR / "whale.png"
NET_IMAGE = ASSET_DIR / "fishingnet.png"
BOAT_IMAGE = ASSET_DIR / "fishingboat.png"
<<<<<<< HEAD
HEART_IMAGE = ASSET_DIR / "heart.png"
=======
TRASH_IMAGE = ASSET_DIR / "trash.png"
>>>>>>> 99acf09022962b8866a4363ec736c9fb6d99cd03
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
SCROLL_SPEED = 2.8
MOVEMENT_SPEED = 9
PATROL_SPEED = 1.5

WHALE_SCALE = 0.13
FISH_SCALE = 0.07
NET_SCALE = 0.092
BOAT_SCALE = 0.125
TRASH_SCALE = 0.045
PLAYER_START_Y = 120

TOTAL_LEVELS = 10
HEALTH_MAX = 6
ENERGY_MAX = 100
ENERGY_DRAIN_PER_SECOND = 0.45
MOVEMENT_ENERGY_DRAIN_PER_SECOND = 0.35
DISTANCE_PER_LEVEL = 5200
DISTANCE_TO_ALASKA = DISTANCE_PER_LEVEL * TOTAL_LEVELS
LEVEL_TRANSITION_DISTANCE = 520
LEVEL_TRANSITION_BAND = 86

LANE_WIDTH = SCREEN_WIDTH / GRID_COLUMNS
ROW_HEIGHT = 80

PLAYER_HITBOX_WIDTH = 44
PLAYER_HITBOX_HEIGHT = 62
WHALE_FORWARD_ANGLE = 0
GAME_FONT = ("Noteworthy", "Avenir Next", "Helvetica Neue", "Arial")
TITLE_FONT = ("Noteworthy", "Avenir Next", "Helvetica Neue", "Arial")
BODY_FONT_SIZE = 12
TITLE_FONT_SIZE = 25
FOOTER_FONT_SIZE = 11
PANEL_PADDING_X = 26
PANEL_INK = (22, 77, 122, 255)
TEXT_SOFT = (249, 252, 255, 255)
TEXT_ACCENT = (176, 218, 255, 255)

LEVEL_GRADIENTS = [
    ((120, 220, 218), (46, 145, 190)),
    ((104, 202, 212), (38, 130, 182)),
    ((88, 184, 206), (32, 114, 172)),
    ((72, 166, 198), (28, 98, 160)),
    ((58, 148, 190), (24, 84, 148)),
    ((48, 130, 180), (20, 72, 136)),
    ((40, 112, 168), (17, 60, 122)),
    ((32, 94, 154), (14, 48, 108)),
    ((26, 78, 138), (11, 38, 94)),
    ((20, 62, 118), (8, 28, 78)),
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


def smoothstep(value):
    value = clamp(value, 0.0, 1.0)
    return value * value * (3 - (2 * value))


def blend_color(start, end, amount):
    amount = clamp(amount, 0.0, 1.0)
    return tuple(int(start[i] + ((end[i] - start[i]) * amount)) for i in range(3))


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


def estimate_text_width(text, font_size, padding=0):
    return (len(text) * font_size * 0.52) + padding


def draw_game_text(*args, **kwargs):
    kwargs.setdefault("font_name", GAME_FONT)
    kwargs["bold"] = True
    kwargs["italic"] = False
    arcade.draw_text(*args, **kwargs)


def draw_title_text(*args, **kwargs):
    kwargs.setdefault("font_name", TITLE_FONT)
    kwargs["bold"] = True
    kwargs["italic"] = False
    arcade.draw_text(*args, **kwargs)


def draw_rounded_rectangle(left, bottom, width, height, color, radius=16):
    radius = max(4, min(radius, int(min(width, height) / 2)))
    core_width = max(0, width - (radius * 2))
    core_height = max(0, height - (radius * 2))

    if core_width > 0:
        arcade.draw_lbwh_rectangle_filled(left + radius, bottom, core_width, height, color)
    if core_height > 0:
        arcade.draw_lbwh_rectangle_filled(left, bottom + radius, radius, core_height, color)
        arcade.draw_lbwh_rectangle_filled(left + width - radius, bottom + radius, radius, core_height, color)

    arcade.draw_circle_filled(left + radius, bottom + radius, radius, color)
    arcade.draw_circle_filled(left + width - radius, bottom + radius, radius, color)
    arcade.draw_circle_filled(left + radius, bottom + height - radius, radius, color)
    arcade.draw_circle_filled(left + width - radius, bottom + height - radius, radius, color)


<<<<<<< HEAD
def draw_outlined_rounded_rectangle(left, bottom, width, height, color, radius=16, outline_color=TEXT_SOFT, outline_width=2):
    draw_rounded_rectangle(left, bottom, width, height, color, radius=radius)
    arcade.draw_rectangle_outline(
        left + (width / 2),
        bottom + (height / 2),
        width,
        height,
        outline_color,
        outline_width,
    )
=======
def draw_rectangle_outline(left, bottom, width, height, color, border_width=2):
    arcade.draw_lbwh_rectangle_filled(left, bottom, width, border_width, color)
    arcade.draw_lbwh_rectangle_filled(left, bottom + height - border_width, width, border_width, color)
    arcade.draw_lbwh_rectangle_filled(left, bottom, border_width, height, color)
    arcade.draw_lbwh_rectangle_filled(left + width - border_width, bottom, border_width, height, color)
>>>>>>> 99acf09022962b8866a4363ec736c9fb6d99cd03


def draw_panel(center_x, center_y, max_width, title, lines, footer):
    title_font_size = TITLE_FONT_SIZE if len(title) <= 24 else 22
    footer_font_size = FOOTER_FONT_SIZE
    body_font_size = BODY_FONT_SIZE

    title_lines = wrap_panel_lines([title], max_width, title_font_size, side_padding=34)[:2]
    footer_lines = wrap_panel_lines([footer], max_width, footer_font_size, side_padding=34)[:2]
    body_lines = wrap_panel_lines(lines, max_width, body_font_size, side_padding=34)

    text_width = max(
        max((estimate_text_width(line, title_font_size) for line in title_lines), default=0),
        max((estimate_text_width(line, footer_font_size) for line in footer_lines), default=0),
        max((estimate_text_width(line, body_font_size) for line in body_lines if line), default=0),
    )
    panel_width = min(max_width, max(220, text_width + (PANEL_PADDING_X * 2)))
    title_lines = wrap_panel_lines([title], panel_width, title_font_size, side_padding=24)[:2]
    footer_lines = wrap_panel_lines([footer], panel_width, footer_font_size, side_padding=24)[:2]
    body_lines = wrap_panel_lines(lines, panel_width, body_font_size, side_padding=24)
    body_height = max(1, len(body_lines)) * (body_font_size + 7)
    title_height = len(title_lines) * (title_font_size + 3)
    footer_height = len(footer_lines) * (footer_font_size + 3)
    panel_height = min(420, max(140, title_height + body_height + footer_height + 56))

    left = center_x - panel_width / 2
    bottom = center_y - panel_height / 2
    draw_rounded_rectangle(left, bottom, panel_width, panel_height, PANEL_INK, radius=18)

    title_y = bottom + panel_height - 30
    for line in title_lines:
        draw_title_text(line, center_x, title_y, TEXT_SOFT, title_font_size, anchor_x="center")
        title_y -= title_font_size + 2

    footer_y = bottom + 20 + ((len(footer_lines) - 1) * (footer_font_size - 4))
    for line in footer_lines:
        draw_game_text(line, center_x, footer_y, TEXT_ACCENT, footer_font_size, anchor_x="center", bold=True)
        footer_y -= footer_font_size + 5

    text_y = title_y - 18
    line_spacing = body_font_size + 6
    for line in body_lines:
        if text_y < bottom + 42:
            break
        if line:
            draw_game_text(line, left + 32, text_y, TEXT_ACCENT, body_font_size)
        text_y -= line_spacing


<<<<<<< HEAD
def draw_trash(center_x, center_y, scale=1.0):
    radius = 13 * scale
    arcade.draw_circle_filled(center_x, center_y, radius, (116, 169, 232, 255))
=======
def draw_heart(center_x, center_y, size, color):
    points = []
    scale = size / 18
    for degree in range(0, 360, 12):
        angle = math.radians(degree)
        x = 16 * (math.sin(angle) ** 3)
        y = 13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle)
        points.append((center_x + x * scale, center_y + (y - 2) * scale))
    arcade.draw_polygon_filled(points, color)
>>>>>>> 99acf09022962b8866a4363ec736c9fb6d99cd03


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = (7, 30, 58)
        self.ocean = arcade.load_texture(OCEAN_IMAGE)
        self.whale_texture = arcade.load_texture(WHALE_IMAGE)
        self.net_texture = arcade.load_texture(NET_IMAGE)
        self.boat_texture = arcade.load_texture(BOAT_IMAGE)
        if Image is not None:
            with Image.open(HEART_IMAGE) as heart_file:
                heart_image = heart_file.convert("RGBA")
            heart_bbox = heart_image.getchannel("A").getbbox()
            if heart_bbox:
                heart_image = heart_image.crop(heart_bbox)
            self.heart_texture = arcade.Texture(heart_image)
        else:
            self.heart_texture = arcade.load_texture(HEART_IMAGE)
        self.fish_textures = [arcade.load_texture(path) for path in FISH_IMAGES]
        self.player_sprite = None

        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()

        self.left_pressed = False
        self.right_pressed = False

        self.health = HEALTH_MAX
        self.energy = ENERGY_MAX
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
        self.energy = ENERGY_MAX
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

    def fish_density(self):
        level_index = self.current_level - 1
        return clamp(1.0 - (level_index / max(1, TOTAL_LEVELS - 1)), 0.0, 1.0)

    def start_migration(self):
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()
        self.health = HEALTH_MAX
        self.energy = ENERGY_MAX
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
            hazard = arcade.Sprite(BOAT_IMAGE, scale=BOAT_SCALE)
            hazard.kind = "boat"
            hazard.damage = 2
        elif hazard_kind == "trash":
<<<<<<< HEAD
            hazard = arcade.SpriteSolidColor(34, 34, color=(116, 169, 232, 255))
=======
            hazard = arcade.Sprite(TRASH_IMAGE, scale=TRASH_SCALE)
>>>>>>> 99acf09022962b8866a4363ec736c9fb6d99cd03
            hazard.kind = "trash"
            hazard.damage = 1
        elif hazard_kind == "net":
            hazard = arcade.Sprite(NET_IMAGE, scale=NET_SCALE)
            hazard.kind = "net"
            hazard.damage = 1
        else:
            hazard = arcade.Sprite(NET_IMAGE, scale=NET_SCALE)
            hazard.kind = "net"
            hazard.damage = 1

        hazard.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        hazard.center_y = self.next_spawn_y + (ROW_HEIGHT / 2)
        hazard.change_x = 0
        self.hazard_list.append(hazard)
        return hazard

    def spawn_token(self, col, is_school=False):
        texture_path = random.choice(FISH_IMAGES)
        token = arcade.Sprite(texture_path, scale=FISH_SCALE * (1.25 if is_school else 1.0))
        token.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        token.center_y = self.next_spawn_y + (ROW_HEIGHT / 2)
        hidden_trash_chance = clamp(0.14 + (self.level_ratio * 0.24), 0.14, 0.38)
        token.value = random.choice([-10, -5]) if random.random() < hidden_trash_chance else random.choice([5, 10, 15, 20])
        token.kind = "fish"
        token.is_trash = token.value < 0
        self.token_list.append(token)
        return token

    def fish_spawn_chance(self):
        level_index = self.current_level - 1
        base_chance = clamp(0.66 - (level_index * 0.05), 0.22, 0.66)
        if self.current_level == 1:
            base_chance += 0.05
        if self.energy <= 20:
            base_chance += 0.10
        return clamp(base_chance, 0.22, 0.74)

    def fish_school_chance(self):
        level_index = self.current_level - 1
        base_chance = clamp(0.24 - (level_index * 0.01), 0.07, 0.24)
        if self.energy <= 20:
            base_chance += 0.02
        return clamp(base_chance, 0.07, 0.26)

    def spawn_row(self):
        all_cols = list(range(GRID_COLUMNS))
        occupied_cols = []
        hazard_cols = []
        distance_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        difficulty = self.level_ratio
        hazard_total = 0
        safe_choices = []
        hazard_kind_pool = []
        boat_chance = 0.0

        can_spawn_boats = self.current_level >= 3
        if can_spawn_boats and self.rows_since_last_patrol >= 1 and random.random() < (0.10 + difficulty * 0.20):
            h_col = random.choice(all_cols)
            occupied_cols.append(h_col)
            hazard = self.spawn_hazard(h_col, "boat")
            patrol_speed = PATROL_SPEED + difficulty * 1.6
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
            if self.current_level >= 2 and random.random() < (0.20 + difficulty * 0.22):
                hazard_total += 1
            if self.current_level >= 4 and random.random() < (0.14 + difficulty * 0.18):
                hazard_total += 1
            if self.current_level >= 7 and random.random() < (0.08 + difficulty * 0.14):
                hazard_total += 1
            if self.current_level >= 9 and random.random() < (0.06 + difficulty * 0.10):
                hazard_total += 1
            hazard_kind_pool = ["trash", "net"]
            boat_chance = 0.05 + (difficulty * 0.04)

        for _ in range(min(hazard_total, len(safe_choices))):
            h_col = random.choice(safe_choices)
            occupied_cols.append(h_col)
            hazard_cols.append(h_col)
            safe_choices.remove(h_col)
            hazard_kind = random.choice(hazard_kind_pool) if hazard_kind_pool else None
            hazard = self.spawn_hazard(h_col, hazard_kind)
            if hazard.kind == "boat":
                patrol_speed = PATROL_SPEED + (difficulty * 1.2)
                hazard.change_x = patrol_speed if random.random() > 0.5 else -patrol_speed

        remaining_cols = [c for c in all_cols if c not in occupied_cols]
        if self.current_level >= 3 and remaining_cols and random.random() < boat_chance:
            boat_col = random.choice(remaining_cols)
            occupied_cols.append(boat_col)
            hazard_cols.append(boat_col)
            hazard = self.spawn_hazard(boat_col, "boat")
            patrol_speed = PATROL_SPEED + (difficulty * 1.2)
            hazard.change_x = patrol_speed if random.random() > 0.5 else -patrol_speed

            for _ in range(min(hazard_total, len(safe_choices))):
                h_col = random.choice(safe_choices)
                occupied_cols.append(h_col)
                safe_choices.remove(h_col)
                self.spawn_hazard(h_col)

            self.prev_hazard_cols = occupied_cols

            remaining_cols = [c for c in all_cols if c not in occupied_cols]
            fish_chance = clamp(0.58 - difficulty * 0.22 + (0.14 if self.health <= 2 or self.energy <= 30 else 0.0), 0.18, 0.72)
            if self.current_level >= 2 and remaining_cols and random.random() < fish_chance:
                token_col = random.choice(remaining_cols)
                occupied_cols.append(token_col)
                remaining_cols.remove(token_col)
                self.spawn_token(token_col)

            school_chance = clamp(0.30 - difficulty * 0.14, 0.10, 0.32)
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
        level_index = self.current_level - 1
        distance_into_level = self.distance_traveled % DISTANCE_PER_LEVEL
        transition_amount = 1.0
        transition_y = None
        if level_index > 0 and distance_into_level < LEVEL_TRANSITION_DISTANCE:
            transition_amount = distance_into_level / LEVEL_TRANSITION_DISTANCE
            transition_y = SCREEN_HEIGHT * (1.0 - transition_amount)

        bands = 24
        band_height = SCREEN_HEIGHT / bands
        for band in range(bands):
            ratio = band / max(1, bands - 1)
            color = self.level_background_color(level_index, ratio, band * band_height, transition_y)
            arcade.draw_lbwh_rectangle_filled(
                0,
                band * band_height,
                SCREEN_WIDTH,
                band_height + 1,
                (*color, 255),
            )

        y = self.background_offset - OCEAN_TILE_HEIGHT
        while y < SCREEN_HEIGHT:
            arcade.draw_texture_rect(
                self.ocean,
                arcade.LBWH(0, y, OCEAN_TILE_WIDTH, OCEAN_TILE_HEIGHT),
            )
            y += OCEAN_TILE_HEIGHT

        for band in range(bands):
            ratio = band / max(1, bands - 1)
            color = self.level_background_color(level_index, ratio, band * band_height, transition_y)
            arcade.draw_lbwh_rectangle_filled(
                0,
                band * band_height,
                SCREEN_WIDTH,
                band_height + 1,
                (*color, 118),
            )

        if transition_y is not None:
            line_alpha = int(220 * (1.0 - abs(0.5 - transition_amount) * 0.75))
            label_y = clamp(transition_y + 12, 34, SCREEN_HEIGHT - 66)
            draw_game_text(
                f"Level {self.current_level}",
                18,
                label_y,
                (235, 252, 255, line_alpha),
                13,
                bold=True,
            )

    def level_background_color(self, level_index, vertical_ratio, band_y, transition_y):
        top_color, bottom_color = LEVEL_GRADIENTS[level_index]
        current_color = blend_color(bottom_color, top_color, vertical_ratio)
        if transition_y is None:
            return current_color

        previous_top, previous_bottom = LEVEL_GRADIENTS[level_index - 1]
        previous_color = blend_color(previous_bottom, previous_top, vertical_ratio)
        band_center = band_y + (SCREEN_HEIGHT / 24 / 2)
        mix = smoothstep((band_center - transition_y + (LEVEL_TRANSITION_BAND / 2)) / LEVEL_TRANSITION_BAND)
        return blend_color(previous_color, current_color, mix)

    def draw_distance_scale(self):
        panel_left = SCREEN_WIDTH - 178
        panel_bottom = 118
        panel_width = 154
        panel_height = 410
        draw_rounded_rectangle(panel_left, panel_bottom, panel_width, panel_height, PANEL_INK, radius=18)
        draw_title_text("Migration", panel_left + panel_width / 2, panel_bottom + panel_height - 24, TEXT_SOFT, 18, anchor_x="center")

        route = [
            (panel_left + 86, panel_bottom + 42),
            (panel_left + 60, panel_bottom + 98),
            (panel_left + 70, panel_bottom + 154),
            (panel_left + 46, panel_bottom + 210),
            (panel_left + 80, panel_bottom + 266),
        ]
        labels = [
            ("Baja", route[0]),
            ("CA", route[1]),
            ("OR/WA", route[2]),
            ("B.C.", route[3]),
            ("Alaska", route[4]),
        ]
        progress = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)
        segment_progress = progress * (len(route) - 1)
        segment_index = min(len(route) - 2, int(segment_progress))
        local_progress = segment_progress - segment_index
        start = route[segment_index]
        end = route[segment_index + 1]
        marker_x = start[0] + ((end[0] - start[0]) * local_progress)
        marker_y = start[1] + ((end[1] - start[1]) * local_progress)

        for start_point, end_point in zip(route, route[1:]):
            arcade.draw_line(start_point[0], start_point[1], end_point[0], end_point[1], (224, 242, 255, 220), 4)

        for label, (x, y) in labels:
            arcade.draw_circle_filled(x, y, 5, TEXT_SOFT)
            draw_game_text(label, panel_left + 8, y - 7, TEXT_SOFT, 10)

        arcade.draw_circle_filled(marker_x, marker_y, 8, (204, 234, 255, 255))
        arcade.draw_circle_outline(marker_x, marker_y, 10, TEXT_SOFT, 2)
        draw_game_text(f"{int(progress * 100)}%", panel_left + panel_width / 2, panel_bottom + 16, TEXT_ACCENT, 12, anchor_x="center", bold=True)

    def draw_hud_hearts(self):
        heart_gap = 28
        heart_size = 24
        hearts_width = (HEALTH_MAX - 1) * heart_gap
        start_x = SCREEN_WIDTH - 130 - (hearts_width / 2)
        heart_bottom = SCREEN_HEIGHT - 48
        draw_game_text("Health", start_x - 16, heart_bottom + 6, TEXT_SOFT, 12, anchor_x="right")
        for i in range(HEALTH_MAX):
            alpha = 255 if i < self.health else 90
            arcade.draw_texture_rect(
                self.heart_texture,
                arcade.LBWH(start_x + (i * heart_gap) - heart_size / 2, heart_bottom, heart_size, heart_size),
                alpha=alpha,
            )

    def draw_energy_bar(self):
        bar_left = 88
        bar_bottom = 528
        bar_width = 296
        bar_height = 12
        fill_width = bar_width * clamp(self.energy / ENERGY_MAX, 0.0, 1.0)
        arcade.draw_lbwh_rectangle_filled(bar_left, bar_bottom, bar_width, bar_height, (10, 55, 92, 255))
<<<<<<< HEAD
        arcade.draw_lbwh_rectangle_filled(bar_left, bar_bottom, fill_width, bar_height, (165, 222, 255, 255))
        arcade.draw_lbwh_rectangle_outline(bar_left, bar_bottom, bar_width, bar_height, TEXT_SOFT, 2)
=======
        if fill_width > 0:
            arcade.draw_lbwh_rectangle_filled(bar_left, bar_bottom, fill_width, bar_height, (165, 222, 255, 255))
        draw_rectangle_outline(bar_left, bar_bottom, bar_width, bar_height, TEXT_SOFT, 2)
>>>>>>> 99acf09022962b8866a4363ec736c9fb6d99cd03
        draw_game_text("Energy", 24, bar_bottom - 1, TEXT_SOFT, 12)

    def draw_ui(self):
        level = min(TOTAL_LEVELS, int(self.distance_traveled // DISTANCE_PER_LEVEL) + 1)
        draw_rounded_rectangle(12, 520, 400, 68, PANEL_INK, radius=16)
        draw_rounded_rectangle(SCREEN_WIDTH - 360, 540, 336, 48, PANEL_INK, radius=16)
        draw_game_text(f"Level {level}/{TOTAL_LEVELS}", 24, 556, TEXT_SOFT, 16, bold=True)
        draw_game_text(
            f"Distance: {int(self.distance_traveled)} / {DISTANCE_TO_ALASKA} mi",
            145,
            556,
            TEXT_SOFT,
            13,
        )
        self.draw_energy_bar()
        draw_game_text(f"Points: {self.score}", SCREEN_WIDTH - 348, 556, TEXT_SOFT, 16, bold=True)
        self.draw_hud_hearts()
        self.draw_distance_scale()

        for msg in self.messages:
            draw_game_text(msg["text"], msg["x"], msg["y"], msg["color"], 18, bold=True, anchor_x="center")

        if self.level_banner_timer > 0:
            alpha = int(218 * clamp(self.level_banner_timer / 2.4, 0.0, 1.0))
            draw_rounded_rectangle(190, 254, 420, 92, (22, 77, 122, alpha), radius=20)
            banner_font_size = 24 if len(self.level_banner_text) <= 28 else 19
            banner_lines = wrap_panel_lines([self.level_banner_text], 420, banner_font_size, side_padding=56)[:2]
            banner_y = 308 + ((len(banner_lines) - 1) * 12)
            for line in banner_lines:
                draw_game_text(
                    line,
                    SCREEN_WIDTH / 2,
                    banner_y,
                    TEXT_SOFT,
                    banner_font_size,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                )
                banner_y -= banner_font_size + 5

    def draw_outlined_status_box(self, panel_left, panel_bottom, panel_width, panel_height):
        draw_outlined_rounded_rectangle(panel_left, panel_bottom, panel_width, panel_height, PANEL_INK, radius=18)
        self.draw_hud_hearts()
        self.draw_energy_bar()

    def draw_hazard(self, hazard):
        arcade.draw_texture_rect(
            hazard.texture,
            arcade.LBWH(hazard.left, hazard.bottom, hazard.width, hazard.height),
            angle=hazard.angle,
            alpha=hazard.alpha,
        )

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
                hazard.center_y - 12,
                94,
                46,
            )

        return rectangles_overlap(
            player_x,
            player_y,
            PLAYER_HITBOX_WIDTH,
            PLAYER_HITBOX_HEIGHT,
            hazard.center_x,
            hazard.center_y,
            70,
            68,
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
            "Move with A/D or the arrow keys. Eat fish for hidden points and energy, and follow the coastal route on the right.",
        ]
        draw_panel(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 520, "Grey Whale Migration", lines, "Press SPACE to start")

    def draw_lesson(self):
        if not self.current_lesson:
            return
        title = self.current_lesson["title"]
        draw_panel(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            420,
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
            title = "You Did Not Make It"
            lines = [
                "The migration ended early. During the journey, pollution, fishing gear, and boats can turn a natural route into a dangerous one.",
                "Try again and keep an eye on the hazards. People can help by keeping trash out of waterways, recycling fishing line, supporting cleaner harbors, and giving whales space from boats.",
            ]
        draw_panel(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 560, title, lines, "Press R to restart")

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
                self.energy = max(0, self.energy - (16 * damage))
                self.last_hit_time = curr_time
                self.add_message(
                    f"-{damage} HEART",
                    self.player_sprite.center_x,
                    self.player_sprite.top + 20,
                    (255, 122, 132, 255),
                )
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

            self.energy = min(ENERGY_MAX, self.energy + fish.value)
            if fish.value > 0:
                self.health = min(HEALTH_MAX, self.health + 1)
                self.energy = min(ENERGY_MAX, self.energy + 14 + fish.value)
                self.distance_traveled = min(DISTANCE_TO_ALASKA, self.distance_traveled + 10)
                self.add_message(f"⚡+{fish.value}", fish.center_x, fish.center_y, (207, 235, 255, 255))
            else:
                self.energy = max(0, self.energy - 14)
                self.add_message(f"trash {fish.value}", fish.center_x, fish.center_y, (170, 212, 255, 255))
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
                self.level_banner_text = "Level 2: Trash and nets enter the route"
            elif self.current_level == 3:
                self.level_banner_text = "Level 3: Moving ships appear less often"
            else:
                self.level_banner_text = f"Level {self.current_level}"
            self.level_banner_timer = 2.4

    def on_draw(self):
        self.clear()
        self.draw_ocean_background()

        for hazard in self.hazard_list:
            self.draw_hazard(hazard)
        self.token_list.draw()
        self.player_list.draw()
        self.draw_ui()

        if self.game_state == "intro":
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (8, 38, 66, 170))
            self.draw_intro()
        elif self.game_state == "lesson":
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (8, 38, 66, 170))
            self.draw_lesson()
        elif self.is_game_over or self.won:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (8, 38, 66, 180))
            self.draw_end_explanation()

    def on_update(self, delta_time):
        if self.game_state != "playing" or self.is_game_over or self.won:
            self.update_messages(delta_time)
            return

        difficulty = self.level_ratio
        wave = 1.0 + (0.18 * math.sin(self.distance_traveled / 360.0))
        current_scroll = clamp(SCROLL_SPEED + ((difficulty ** 1.2) * 3.2) + (wave * 0.18), 2.2, 6.2)
        energy_drain = ENERGY_DRAIN_PER_SECOND
        if self.left_pressed or self.right_pressed:
            energy_drain += MOVEMENT_ENERGY_DRAIN_PER_SECOND
        self.energy = max(0, self.energy - (energy_drain * delta_time))

        self.energy = max(0.0, self.energy - (ENERGY_DRAIN_PER_SECOND * delta_time))
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

        if self.health <= 0 or self.energy <= 0:
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
