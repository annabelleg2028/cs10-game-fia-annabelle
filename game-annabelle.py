import math
import random
import time

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Grey Whale Migration"

GRID_COLUMNS = 8
SCROLL_SPEED = 5.0
MOVEMENT_SPEED = 8
PATROL_SPEED = 2

SPRITE_SCALING_PLAYER = 0.08
PLAYER_START_Y = 120

HEALTH_MAX = 5
DISTANCE_TO_ALASKA = 6000
DISTANCE_PER_LEVEL = 600
TOTAL_LEVELS = 10

LANE_WIDTH = SCREEN_WIDTH / GRID_COLUMNS
ROW_HEIGHT = 80


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


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


def draw_fish(center_x, center_y, scale=1.0, color=(245, 210, 85, 255)):
    body_w = 34 * scale
    body_h = 18 * scale
    tail_w = 12 * scale
    tail_h = 14 * scale
    eye_offset_x = 8 * scale
    eye_offset_y = 3 * scale

    arcade.draw_ellipse_filled(center_x, center_y, body_w, body_h, color)
    arcade.draw_triangle_filled(
        center_x - body_w * 0.5,
        center_y,
        center_x - body_w * 0.5 - tail_w,
        center_y + tail_h * 0.55,
        center_x - body_w * 0.5 - tail_w,
        center_y - tail_h * 0.55,
        color,
    )
    arcade.draw_circle_filled(center_x + eye_offset_x, center_y + eye_offset_y, 1.8 * scale, arcade.color.WHITE)
    arcade.draw_circle_filled(center_x + eye_offset_x, center_y + eye_offset_y, 0.8 * scale, arcade.color.BLACK)
    arcade.draw_line(
        center_x - 4 * scale,
        center_y,
        center_x + 4 * scale,
        center_y - 1 * scale,
        arcade.color.WHITE,
        max(1, int(scale)),
    )


def draw_trash(center_x, center_y, scale=1.0):
    size = 24 * scale
    arcade.draw_lbwh_rectangle_filled(center_x - size / 2, center_y - size / 2, size, size, (145, 145, 150, 255))
    arcade.draw_line(center_x - size * 0.35, center_y - size * 0.25, center_x + size * 0.35, center_y + size * 0.3, arcade.color.DARK_GRAY, 2)
    arcade.draw_line(center_x - size * 0.25, center_y + size * 0.3, center_x + size * 0.3, center_y - size * 0.25, arcade.color.DARK_GRAY, 2)


def draw_net(center_x, center_y, scale=1.0):
    width = 58 * scale
    height = 22 * scale
    arcade.draw_lbwh_rectangle_filled(center_x - width / 2, center_y - height / 2, width, height, (82, 148, 158, 190))
    for i in range(4):
        x = center_x - width / 2 + (i + 1) * width / 5
        arcade.draw_line(x, center_y - height / 2, x, center_y + height / 2, (230, 245, 245, 120), 1)
    for i in range(2):
        y = center_y - height / 2 + (i + 1) * height / 3
        arcade.draw_line(center_x - width / 2, y, center_x + width / 2, y, (230, 245, 245, 120), 1)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        self.player_sprite = None

        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

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

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("player2.png", scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        for i in range(2):
            bg = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            bg.center_x = SCREEN_WIDTH / 2
            bg.center_y = (i * SCREEN_HEIGHT) + (SCREEN_HEIGHT / 2)
            self.background_list.append(bg)

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

        while self.next_spawn_y < SCREEN_HEIGHT + ROW_HEIGHT:
            self.spawn_row()

    def spawn_hazard(self, col):
        hazard_kind_roll = random.random()
        if hazard_kind_roll < 0.55:
            hazard = arcade.SpriteSolidColor(34, 34, (145, 145, 150, 255))
            hazard.kind = "trash"
        else:
            hazard = arcade.SpriteSolidColor(60, 24, (84, 150, 160, 225))
            hazard.kind = "net"
        hazard.alpha = 0
        hazard.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        hazard.center_y = self.next_spawn_y + (ROW_HEIGHT / 2)
        hazard.change_x = 0
        self.hazard_list.append(hazard)
        return hazard

    def spawn_token(self, col, is_school=False):
        token = arcade.SpriteSolidColor(44 if not is_school else 50, 22 if not is_school else 24, arcade.color.GOLD)
        token.alpha = 0
        token.center_x = (col * LANE_WIDTH) + (LANE_WIDTH / 2)
        token.center_y = self.next_spawn_y + (ROW_HEIGHT / 2)
        token.value = 5 if not is_school else 10
        token.kind = "fish"
        self.token_list.append(token)
        return token

    def spawn_row(self):
        all_cols = list(range(GRID_COLUMNS))
        occupied_cols = []
        distance_ratio = clamp(self.distance_traveled / DISTANCE_TO_ALASKA, 0.0, 1.0)

        if self.rows_since_last_patrol >= 0 and random.random() < (0.24 + distance_ratio * 0.18):
            h_col = random.choice(all_cols)
            hazard = self.spawn_hazard(h_col)
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

            for _ in range(hazard_total):
                h_col = random.choice(safe_choices)
                occupied_cols.append(h_col)
                self.spawn_hazard(h_col)

            self.prev_hazard_cols = occupied_cols

            remaining_cols = [c for c in all_cols if c not in occupied_cols]
            fish_chance = clamp(0.48 - distance_ratio * 0.18 + (0.18 if self.health <= 2 else 0.0), 0.18, 0.72)
            if remaining_cols and random.random() < fish_chance:
                token_col = random.choice(remaining_cols)
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
                        self.spawn_token(token_lane, is_school=True)

        self.next_spawn_y += self.row_height

    @property
    def row_height(self):
        return SCREEN_WIDTH / GRID_COLUMNS

    def draw_grid_lines(self):
        for i in range(GRID_COLUMNS + 1):
            x = i * LANE_WIDTH
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_GRAY, 2)

        line_y = self.next_spawn_y % self.row_height
        while line_y < SCREEN_HEIGHT:
            arcade.draw_line(0, line_y, SCREEN_WIDTH, line_y, arcade.color.DARK_GRAY, 2)
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
        arcade.draw_circle_filled(scale_x, marker_y, 7, arcade.color.GOLD)

    def draw_hud_hearts(self):
        arcade.draw_text("Health", 18, 42, arcade.color.WHITE, 12)
        for i in range(HEALTH_MAX):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            draw_heart(70 + (i * 30), 48, 12, color)

    def draw_ui(self):
        arcade.draw_text(f"Score: {self.score}", 20, 20, arcade.color.WHITE, 18, bold=True)
        arcade.draw_text(f"Level: {min(TOTAL_LEVELS, int(self.distance_traveled // DISTANCE_PER_LEVEL) + 1)}", 20, SCREEN_HEIGHT - 30, arcade.color.WHITE, 14, bold=True)
        arcade.draw_text(f"Distance: {int(self.distance_traveled)} / {DISTANCE_TO_ALASKA}", 20, SCREEN_HEIGHT - 52, arcade.color.WHITE, 13)
        self.draw_hud_hearts()
        self.draw_distance_scale()

        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 18, bold=True, anchor_x="center")

    def draw_hazard(self, hazard):
        if hazard.kind == "trash":
            draw_trash(hazard.center_x, hazard.center_y, 1.0)
        else:
            draw_net(hazard.center_x, hazard.center_y, 1.0)

    def draw_token(self, token):
        draw_fish(token.center_x, token.center_y, 1.0, arcade.color.GOLD)

    def resolve_collisions(self):
        curr_time = time.time()
        invincible = (curr_time - self.last_hit_time) < 1.0
        self.player_sprite.alpha = 160 if invincible else 255

        if not invincible:
            if arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list):
                self.health -= 1
                self.last_hit_time = curr_time
                self.add_message("-1 HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)

        hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for fish in hits:
            self.score += fish.value
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
        self.background_list.draw()
        self.draw_grid_lines()

        for hazard in self.hazard_list:
            self.draw_hazard(hazard)
        for token in self.token_list:
            self.draw_token(token)

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

        if self.left_pressed:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += MOVEMENT_SPEED

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
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.R and (self.is_game_over or self.won):
            self.setup()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    view.setup()
    arcade.run()


if __name__ == "__main__":
    main()
