import arcade
import random
import time

# --- GRID CONFIGURATION ---
# Edit these to change the feel of the game immediately
GRID_COLUMNS = 5      # How many lanes (Horizontal)
GRID_ROW_HEIGHT = 160 # How tall each cell is (Vertical)
# --------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Grid Debugger"
SCROLL_SPEED = 7
SPRITE_SCALING_PLAYER = 0.08
MOVEMENT_SPEED = 10

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()
        self.token_list = arcade.SpriteList()

        self.player_sprite = None
        self.health = 5
        self.score = 0
        self.is_game_over = False
        self.last_hit_time = 0
        self.messages = []

        # Grid state
        self.column_width = SCREEN_WIDTH / GRID_COLUMNS
        self.current_grid_y = 0 # Tracks the scrolling "floor" of the grid
        self.last_occupied_column = -1

    def setup(self):
        self.player_sprite = arcade.Sprite("player2.png", scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # Fill the screen with items initially
        # We spawn one item per row height
        for i in range(6):
            y_pos = SCREEN_HEIGHT + (i * GRID_ROW_HEIGHT)
            self.spawn_in_grid(y_pos)

    def spawn_in_grid(self, y_start):
        """Spawns exactly one thing in the middle of a grid cell."""
        # 1. Pick a random column, but not the same as the last one
        cols = list(range(GRID_COLUMNS))
        if self.last_occupied_column in cols:
            cols.remove(self.last_occupied_column)

        chosen_col = random.choice(cols)
        self.last_occupied_column = chosen_col

        # 2. Calculate the exact center of that grid square
        center_x = (chosen_col * self.column_width) + (self.column_width / 2)
        center_y = y_start + (GRID_ROW_HEIGHT / 2)

        # 3. Decide: Hazard or Token? (70% Hazard for challenge)
        if random.random() < 0.7:
            item = arcade.Sprite(":resources:images/tiles/bomb.png", 0.5)
            item.center_x = center_x
            item.center_y = center_y
            self.hazard_list.append(item)
        else:
            item = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
            item.center_x = center_x
            item.center_y = center_y
            item.value = 5
            self.token_list.append(item)

    def draw_grid_lines(self):
        """Draws the helper lines so you can see the squares."""
        # Vertical Lines (Columns)
        for i in range(GRID_COLUMNS + 1):
            x = i * self.column_width
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_GRAY, 1)

        # Horizontal Lines (Rows)
        # We use a modulo trick to make the lines scroll with the game
        start_y = self.current_grid_y % GRID_ROW_HEIGHT
        for i in range(int(SCREEN_HEIGHT / GRID_ROW_HEIGHT) + 2):
            y = start_y + (i * GRID_ROW_HEIGHT)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.DARK_GRAY, 1)

    def on_draw(self):
        self.clear()

        # Draw the grid first (background)
        self.draw_grid_lines()

        self.hazard_list.draw()
        self.token_list.draw()
        self.player_list.draw()

        # UI
        arcade.draw_text(f"Score: {self.score}", 20, 20, arcade.color.WHITE, 18)
        for i in range(5):
            color = arcade.color.RED if i < self.health else arcade.color.GRAY
            arcade.draw_circle_filled(SCREEN_WIDTH - 200 + (i * 40), 30, 12, color)

        for msg in self.messages:
            arcade.draw_text(msg["text"], msg["x"], msg["y"], msg["color"], 20, bold=True, anchor_x="center")

        if self.is_game_over:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 150))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 50, anchor_x="center")

    def on_update(self, delta_time):
        if self.is_game_over: return

        # Update grid scroll tracker
        self.current_grid_y -= SCROLL_SPEED

        # Move messages
        for msg in self.messages:
            msg["y"] += 2
            msg["timer"] -= delta_time
        self.messages = [m for m in self.messages if m["timer"] > 0]

        # Player Movement
        # (Standard left/right logic omitted for brevity, add your key listeners here)

        # Scrolling items
        for item in self.hazard_list:
            item.center_y -= SCROLL_SPEED
            if item.top < 0:
                item.remove_from_sprite_lists()
                self.spawn_in_grid(SCREEN_HEIGHT)

        for item in self.token_list:
            item.center_y -= SCROLL_SPEED
            if item.top < 0:
                item.remove_from_sprite_lists()
                self.spawn_in_grid(SCREEN_HEIGHT)

        # Collision logic...
        # (Standard collision code here)

    def add_message(self, text, x, y, color):
        self.messages.append({"text": text, "x": x, "y": y, "timer": 1.0, "color": color})

# --- BOILERPLATE TO RUN ---
def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    view.setup()
    arcade.run()

if __name__ == "__main__":
    main()
