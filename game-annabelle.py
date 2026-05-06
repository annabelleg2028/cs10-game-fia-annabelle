import arcade
import random
import time

# --- COMPACT GRID SETTINGS ---
GRID_COLUMNS = 6         # More columns = smaller square cells
SCROLL_SPEED = 9
MOVEMENT_SPEED = 12
# -----------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Compact Grid"
SPRITE_SCALING_PLAYER = 0.07 # Slightly smaller player for smaller cells

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

        # Grid Math
        self.col_width = SCREEN_WIDTH / GRID_COLUMNS
        self.row_height = self.col_width
        self.next_spawn_y = 0
        self.last_hazard_col = -1

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

        # Fill screen rows
        while self.next_spawn_y < SCREEN_HEIGHT + self.row_height:
            self.spawn_row()

    def spawn_row(self):
        """Spawns 1 mandatory hazard and a potential coin in smaller cells."""
        available_cols = list(range(GRID_COLUMNS))

        # Hazard: 1 per row
        h_choices = [c for c in available_cols if c != self.last_hazard_col]
        h_col = random.choice(h_choices)
        self.last_hazard_col = h_col
        available_cols.remove(h_col)

        # Scaled sprites slightly for smaller grid cells
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.45)
        hazard.center_x = (h_col * self.col_width) + (self.col_width / 2)
        hazard.center_y = self.next_spawn_y + (self.row_height / 2)
        self.hazard_list.append(hazard)

        # Coin: 50% chance
        if random.random() < 0.5:
            t_col = random.choice(available_cols)
            token = arcade.Sprite(":resources:images/items/coinGold.png", 0.35)
            token.center_x = (t_col * self.col_width) + (self.col_width / 2)
            token.center_y = self.next_spawn_y + (self.row_height / 2)
            token.value = 5
            self.token_list.append(token)

        self.next_spawn_y += self.row_height

    def draw_grid_lines(self):
        for i in range(GRID_COLUMNS + 1):
            x = i * self.col_width
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_GRAY, 1)

        line_y = self.next_spawn_y % self.row_height
        while line_y < SCREEN_HEIGHT:
            arcade.draw_line(0, line_y, SCREEN_WIDTH, line_y, arcade.color.DARK_GRAY, 1)
            line_y += self.row_height

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.draw_grid_lines()

        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

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

        self.next_spawn_y -= SCROLL_SPEED

        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        for bg in self.background_list:
            bg.center_y -= SCROLL_SPEED
            if bg.center_y <= -SCREEN_HEIGHT / 2: bg.center_y += SCREEN_HEIGHT * 2

        for item_list in [self.hazard_list, self.token_list]:
            for item in item_list:
                item.center_y -= SCROLL_SPEED

        while self.next_spawn_y < SCREEN_HEIGHT + self.row_height:
            self.spawn_row()

        for item_list in [self.hazard_list, self.token_list]:
            for item in item_list:
                if item.top < -50: item.remove_from_sprite_lists()

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

        for msg in self.messages:
            msg["y"] += 2
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

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
