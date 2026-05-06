import arcade
import random
import time

# --- GRID SETTINGS ---
GRID_COLUMNS = 6
SCROLL_SPEED = 9
MOVEMENT_SPEED = 12
PATROL_SPEED = 5         # Speed of horizontal moving bombs
# -----------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CS10 Arcade: Patrol Hazards"
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
        """Spawns static hazards, patrol hazards, or coins."""
        all_cols = list(range(GRID_COLUMNS))

        # 1. Check for Patrol Row (25% chance)
        if random.random() < 0.25:
            # Patrol rows are exclusive - one moving bomb, nothing else.
            h_col = random.choice(all_cols)
            hazard = self.create_hazard(h_col)
            # Give it horizontal velocity
            hazard.change_x = PATROL_SPEED if random.random() > 0.5 else -PATROL_SPEED
            # We treat the whole row as "blocked" for diagonal logic next time
            self.prev_hazard_cols = [c for c in all_cols]

        else:
            # 2. Standard Static Row Logic
            occupied_cols = []
            banned_cols = set()
            for pc in self.prev_hazard_cols:
                banned_cols.update([pc, pc - 1, pc + 1])

            safe_choices = [c for c in all_cols if c not in banned_cols]
            if not safe_choices:
                safe_choices = [c for c in all_cols if c not in self.prev_hazard_cols]

            h1_col = random.choice(safe_choices)
            occupied_cols.append(h1_col)
            self.create_hazard(h1_col)

            # Potential second hazard (3-cell gap rule)
            potential_h2_cols = [c for c in safe_choices if abs(c - h1_col) >= 4]
            if potential_h2_cols and random.random() < 0.3:
                h2_col = random.choice(potential_h2_cols)
                occupied_cols.append(h2_col)
                self.create_hazard(h2_col)

            self.prev_hazard_cols = occupied_cols

            # Spawn Coin
            remaining_cols = [c for c in all_cols if c not in occupied_cols]
            if remaining_cols and random.random() < 0.5:
                self.create_coin(random.choice(remaining_cols))

        self.next_spawn_y += self.row_height

    def create_hazard(self, col):
        hazard = arcade.Sprite(":resources:images/tiles/bomb.png", 0.45)
        hazard.center_x = (col * self.col_width) + (self.col_width / 2)
        hazard.center_y = self.next_spawn_y + (self.row_height / 2)
        hazard.change_x = 0 # Default is static
        self.hazard_list.append(hazard)
        return hazard

    def create_coin(self, col):
        token = arcade.Sprite(":resources:images/items/coinGold.png", 0.35)
        token.center_x = (col * self.col_width) + (self.col_width / 2)
        token.center_y = self.next_spawn_y + (self.row_height / 2)
        token.value = 5
        self.token_list.append(token)

    def on_draw(self):
        self.clear()
        self.background_list.draw()

        # Grid visual guide
        for i in range(GRID_COLUMNS + 1):
            arcade.draw_line(i * self.col_width, 0, i * self.col_width, SCREEN_HEIGHT, arcade.color.DARK_GRAY, 1)

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

        # Player Movement
        if self.left_pressed and self.player_sprite.left > 0:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed and self.player_sprite.right < SCREEN_WIDTH:
            self.player_sprite.center_x += MOVEMENT_SPEED

        # Scrolling items and Horizontal bouncing
        for hazard in self.hazard_list:
            hazard.center_y -= SCROLL_SPEED
            hazard.center_x += hazard.change_x

            # Bounce logic
            if hazard.left < 0 or hazard.right > SCREEN_WIDTH:
                hazard.change_x *= -1

        for token in self.token_list:
            token.center_y -= SCROLL_SPEED

        # Refill/Clean
        while self.next_spawn_y < SCREEN_HEIGHT + self.row_height:
            self.spawn_row()

        for item_list in [self.hazard_list, self.token_list]:
            for item in item_list:
                if item.top < -50: item.remove_from_sprite_lists()

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
