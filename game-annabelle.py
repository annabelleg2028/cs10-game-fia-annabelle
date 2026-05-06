import arcade
import random
import time

# --- GRID SETTINGS ---
GRID_COLUMNS = 6
SCROLL_SPEED = 9
MOVEMENT_SPEED = 12
PATROL_SPEED = 5
# -----------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Crash-Proof Patrols"
SPRITE_SCALING_PLAYER = 0.07

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

        # Track previous hazard columns to prevent diagonal touching
        self.prev_hazard_cols = []

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

        while self.next_spawn_y < SCREEN_HEIGHT + self.row_height:
            self.spawn_row()

    def spawn_row(self):
        """Spawns hazards with safety checks to prevent IndexError."""
        all_cols = list(range(GRID_COLUMNS))
        occupied_cols = []

        # 1. 25% chance for a Patrol Row (Exclusive)
        if random.random() < 0.25:
            h_col = random.choice(all_cols)
            hazard = self.create_hazard(h_col)
            hazard.change_x = PATROL_SPEED if random.random() > 0.5 else -PATROL_SPEED
            # If a row is moving, we ban the center lane of the next row to be safe
            self.prev_hazard_cols = [h_col]

        else:
            # 2. Static Row Logic with Crash Protection
            banned_cols = set()
            for pc in self.prev_hazard_cols:
                banned_cols.update([pc, pc - 1, pc + 1])

            # Filter choices based on diagonal/vertical rules
            safe_choices = [c for c in all_cols if c not in banned_cols]

            # --- CRASH PROTECTION ---
            # If no "safe" spots exist, fall back to any column except exactly where the last one was
            if not safe_choices:
                safe_choices = [c for c in all_cols if c not in self.prev_hazard_cols]
            # If STILL no choices (impossible in 6 cols, but good for safety), just use everything
            if not safe_choices:
                safe_choices = all_cols

            # Pick first hazard
            h1_col = random.choice(safe_choices)
            occupied_cols.append(h1_col)
            self.create_hazard(h1_col)

            # Potential second hazard (3-cell gap rule + diagonal rule)
            # We check if there's a column that is 4 indexes away AND is in safe_choices
            potential_h2_cols = [c for c in safe_choices if abs(c - h1_col) >= 4]

            if potential_h2_cols and random.random() < 0.3:
                h2_col = random.choice(potential_h2_cols)
                occupied_cols.append(h2_col)
                self.create_hazard(h2_col)

            self.prev_hazard_cols = occupied_cols

            #
