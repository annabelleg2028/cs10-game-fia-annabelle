import arcade
import random
import time

# --- EDITABLE SETTINGS ---
GRID_COLUMNS = 6
SCROLL_SPEED = 7
MOVEMENT_SPEED = 10
# -------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Absolute Grid Alignment"
SPRITE_SCALING_PLAYER = 0.08

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        self.left_pressed = False
        self.right_pressed = False

        self.health = 5
        self.score = 0
        self.is_game_over = False
        self.last_hit_time = 0
        self.messages = []

        # Calculate grid math
        self.col_width = SCREEN_WIDTH / GRID_COLUMNS
        self.row_height = self.col_width # Ensures square cells
        self.grid_scroll_offset = 0
        self.last_col = -1

        # Track the "top" row to keep spawns perfectly sequential
        self.next_spawn_y = SCREEN_HEIGHT

    def setup(self):
        self.player_sprite = arcade.Sprite("player2.png", scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        for i in range(2):
            bg = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            bg.center_x = SCREEN_WIDTH / 2
            bg.center_y = (i * SCREEN_HEIGHT) + (SCREEN_HEIGHT / 2)
            self.background_list.append(bg)

        # Fill the initial screen with sequential rows
        for _ in range(int(SCREEN_HEIGHT / self.row_height) + 5):
            self.spawn_in_next_row()

    def spawn_in_next_row(self):
        """Spawns exactly one item in the center of the next available grid row."""
        # Pick column
        valid_cols = [c for c in range(GRID_COLUMNS) if c != self.last_col]
        chosen_col = random.choice(valid_cols)
        self.last_col = chosen_col

        # CALCULATE PERFECT CENTER
        # X: (Column index * width) + half-width
        # Y: (Current top tracking Y) + half-height
        center_x = (chosen_col * self.col_width) + (self.col_width / 2)
        center_y = self.next_spawn_y + (self.row_height / 2)

        if random.random() < 0.7:
            item = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
            self.hazard_list.append(item)
        else:
            item = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
            item.value = 5
            self.token_list.append(item)

        item.center_x = center_x
        item.center_y = center_y

        # Move the spawn pointer up for the next row
        self.next_spawn_y += self.row_height

    def draw_grid_lines(self):
        """Draws visual grid for verification."""
        # Vertical Lines
        for i in range(GRID_COLUMNS + 1):
            x = i * self.col_width
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_GRAY, 1)

        # Horizontal Lines (Locked to the scrolling items)
        offset = self.grid_scroll_offset % self.row_height
        for i in range(int(SCREEN_HEIGHT / self.row_height) + 2):
            y = offset + (i * self.row_height)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.DARK_GRAY, 1)

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.draw_grid_lines()

        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        # UI Overlay
        arcade.draw_text(f"Score: {self.score}", 20, 20, arcade.color.WHITE, 20, bold=True)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(SCREEN_WIDTH - 220 + (i * 45), 35, 15, color)

        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 24, bold=True, anchor_x="center")

        if self.is_game_over:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 180))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 50, anchor_x="center")

    def on_update(self, delta_time):
        if self.is_game_over: return

        # Sync visual grid and spawn pointer with scroll
        self.grid_scroll_offset -= SCROLL_SPEED
        self.next_spawn_y -= SCROLL_SPEED

        # Smooth Player Controls
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Message Animations
        for msg in self.messages:
            msg["y"] += 2
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

        # Scrolling logic
        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2: bg.center_y += SCREEN_HEIGHT * 2

        # Item Recycling
        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED
            if hazard.top < 0:
                hazard.remove_from_sprite_lists()
                self.spawn_in_next_row()

        for token in self.token_list:
            token.center_y -= SCROLL_SPEED
            if token.top < 0:
                token.remove_from_sprite_lists()
                self.spawn_in_next_row()

        # Collisions
        curr_time = time.time()
        invincible = (curr_time - self.last_hit_time) < 1.2
        self.player_sprite.alpha = 160 if invincible else 255

        if not invincible:
            if arcade.check_for_collision_with_list(self.player_sprite, self.hazard_list):
                self.health -= 1
                self.last_hit_time = curr_time
                self.add_message("-1 HEART", self.player_sprite.center_x, self.player_sprite.top + 20, arcade.color.RED)
                if self.health <= 0: self.is_game_over = True

        hits = arcade.check_for_collision_with_list(self.player_sprite, self.token_list)
        for coin in hits:
            self.score += coin.value
            self.add_message(f"+{coin.value}", coin.center_x, coin.center_y, arcade.color.GOLD)
            coin.remove_from_sprite_lists()
            self.spawn_in_next_row()

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.0, "color": color})

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT: self.left_pressed = True
        elif key == arcade.key.RIGHT: self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT: self.left_pressed = False
        elif key == arcade.key.RIGHT: self.right_pressed = False

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    view.setup()
    arcade.run()

if __name__ == "__main__":
    main()
