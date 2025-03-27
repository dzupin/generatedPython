import pygame
import random
import math
import sys
import os # Needed for path joining and checking existence



# PROMPT for Gemini 2.5 Pro Experimental 03-25 : can you generate image assets used in this game for me?



# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Asset Directory
ASSET_DIR = "assets"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TRANSPARENT = (0, 0, 0, 0) # For asset generation

# Game Element Colors & Properties (Used in both game and asset generation)
PLAYER_COLOR = GREEN
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 20
PLAYER_SPEED = 5
PLAYER_LIVES = 3
PLAYER_GUN_COOLDOWN = 400 # milliseconds
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 50

BULLET_COLOR = YELLOW
BULLET_WIDTH = 4
BULLET_HEIGHT = 10
BULLET_SPEED = 7

INVADER_WIDTH = 30
INVADER_HEIGHT = 20
INVADER_COLORS = [
    (200, 200, 200), # Row 0/3/4 type
    (150, 150, 250), # Row 1/2 type
    (250, 150, 150), # Row 2 type (ensure this matches row index if needed)
]
INVADER_ROWS = 5
INVADER_COLS = 11
INVADER_H_SPACE = 15
INVADER_V_SPACE = 10
INVADER_START_X = 50 # Adjusted later based on grid width
INVADER_START_Y = 50
INVADER_INITIAL_MOVE_SPEED = 1
INVADER_INITIAL_MOVE_INTERVAL = 1000
INVADER_DROP_AMOUNT = 10
INVADER_SHOOT_COOLDOWN_MIN = 1000
INVADER_SHOOT_COOLDOWN_MAX = 5000
INVADER_SPEEDUP_FACTOR = 0.95
INVADER_POINTS = {0: 30, 1: 20, 2: 20, 3: 10, 4: 10}

BARRIER_COLOR = GREEN
BARRIER_COUNT = 4
BARRIER_PART_SIZE = 8
BARRIER_Y_POS = SCREEN_HEIGHT - 120
BARRIER_HITS_TO_DESTROY = 4

# List of required asset filenames
REQUIRED_ASSETS = [
    "player.png",
    "bullet.png"
]
# Add invader assets dynamically based on INVADER_COLORS
for i in range(len(INVADER_COLORS)):
    REQUIRED_ASSETS.append(f"invader_row{i}_a.png")
    REQUIRED_ASSETS.append(f"invader_row{i}_b.png")

# --- Asset Generation Functions ---

def save_surface(surface, filename):
    """Saves a Pygame surface to a file in the asset directory."""
    if not os.path.exists(ASSET_DIR):
        try:
            os.makedirs(ASSET_DIR)
            print(f"Created asset directory: {ASSET_DIR}")
        except OSError as e:
            print(f"Error creating directory {ASSET_DIR}: {e}")
            return # Cannot save if directory creation failed
    filepath = os.path.join(ASSET_DIR, filename)
    try:
        pygame.image.save(surface, filepath)
        # print(f"Successfully generated: {filepath}") # Keep it less verbose maybe
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def create_player_asset():
    """Creates the player ship asset."""
    surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    # Simple cannon shape
    pygame.draw.rect(surface, PLAYER_COLOR, (0, PLAYER_HEIGHT - 8, PLAYER_WIDTH, 8))
    pygame.draw.rect(surface, PLAYER_COLOR, (PLAYER_WIDTH // 2 - 8, PLAYER_HEIGHT - 14, 16, 6))
    pygame.draw.rect(surface, PLAYER_COLOR, (PLAYER_WIDTH // 2 - 3, 0, 6, PLAYER_HEIGHT - 10))
    pygame.draw.rect(surface, WHITE, (PLAYER_WIDTH // 2 - 1, 2, 2, 4)) # Detail
    save_surface(surface, "player.png")

def create_bullet_asset():
    """Creates the bullet asset."""
    surface = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    pygame.draw.rect(surface, BULLET_COLOR, (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
    save_surface(surface, "bullet.png")

def create_invader_asset(row_type, frame):
    """Creates an invader asset."""
    surface = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    color = INVADER_COLORS[row_type % len(INVADER_COLORS)]
    pixel_size = 2
    mid_x = INVADER_WIDTH // (2*pixel_size)
    mid_y = INVADER_HEIGHT // (2*pixel_size)

    def draw_pixel(x, y, c=color):
        px = (mid_x + x) * pixel_size
        py = (mid_y + y - 3) * pixel_size # Adjust vertical offset
        pygame.draw.rect(surface, c, (px, py, pixel_size, pixel_size))

    # Simplified Invader Designs (Adjust as desired)
    if row_type == 0: # Top
        for dx in [-1, 0, 1]: draw_pixel(dx, 0)
        for dx in [-2, -1, 0, 1, 2]: draw_pixel(dx, 1)
        for dx in [-3, -2, -1, 0, 1, 2, 3]: draw_pixel(dx, 2)
        for dx in [-3, -1, 0, 1, 3]: draw_pixel(dx, 3)
        for dx in [-3, -2, 0, 2, 3]: draw_pixel(dx, 4)
        if frame == 'a':
            for dx in [-2, 2]: draw_pixel(dx, 5) # Semicolon removed, statement moved below
            for dx in [-1, 1]: draw_pixel(dx, 6)
        else:
            for dx in [-1, 1]: draw_pixel(dx, 5) # Semicolon removed, statement moved below
            for dx in [-2, 2]: draw_pixel(dx, 6)
    elif row_type == 1: # Middle
        for dx in [-2, -1, 0, 1, 2]: draw_pixel(dx, 1)
        for dx in [-3, -2, -1, 0, 1, 2, 3]: draw_pixel(dx, 2)
        for dx in [-4,-3, -1, 0, 1, 3, 4]: draw_pixel(dx, 3)
        for dx in [-4,-3, -2, -1, 0, 1, 2, 3, 4]: draw_pixel(dx, 4)
        if frame == 'a':
            for dx in [-4, 4]: draw_pixel(dx, 2) # Semicolon removed, statement moved below
            for dx in [-3, 3]: draw_pixel(dx, 5)
            for dx in [-2, -1, 1, 2]: draw_pixel(dx, 5)
        else:
            for dx in [-4, 4]: draw_pixel(dx, 5) # Semicolon removed, statement moved below
            for dx in [-3, 3]: draw_pixel(dx, 4)
            # These were likely intended to be separate calls anyway
            draw_pixel(-1, 5)
            draw_pixel(1, 5)
    elif row_type == 2: # Bottom
        for dx in [-2,-1, 0, 1, 2]: draw_pixel(dx, 0)
        for dx in [-3,-2, -1, 0, 1, 2, 3]: draw_pixel(dx, 1)
        for dx in [-4,-3,-2,-1, 0, 1, 2, 3, 4]: draw_pixel(dx, 2)
        for dx in [-4, -2,-1, 0, 1, 2, 4]: draw_pixel(dx, 3)
        for dx in [-3,-2, 2, 3]: draw_pixel(dx, 4)
        if frame == 'a':
            for dx in [-3, -1, 1, 3]: draw_pixel(dx, 5) # Semicolon removed, statement moved below
            for dx in [-2, 2]: draw_pixel(dx, 6)
        else:
            for dx in [-2, -1, 1, 2]: draw_pixel(dx, 5) # Semicolon removed, statement moved below
            for dx in [-3, 3]: draw_pixel(dx, 6)

    filename = f"invader_row{row_type}_{frame}.png"
    save_surface(surface, filename)

def check_and_generate_assets():
    """Checks if required assets exist, generates them if missing."""
    print("Checking for assets...")
    needs_generation = False
    if not os.path.exists(ASSET_DIR):
        print(f"Asset directory '{ASSET_DIR}' not found.")
        needs_generation = True
    else:
        for filename in REQUIRED_ASSETS:
            filepath = os.path.join(ASSET_DIR, filename)
            if not os.path.exists(filepath):
                print(f"Missing asset: {filename}")
                needs_generation = True
                break # No need to check further

    if needs_generation:
        print("Generating required assets...")
        pygame_initialized_for_generation = False
        try:
            # Temporarily initialize Pygame just for drawing assets
            pygame.init()
            pygame_initialized_for_generation = True
            print(" -> Generating player...")
            create_player_asset()
            print(" -> Generating bullet...")
            create_bullet_asset()
            print(" -> Generating invaders...")
            for i in range(len(INVADER_COLORS)):
                create_invader_asset(i, 'a')
                create_invader_asset(i, 'b')
            print("Asset generation complete.")
        except Exception as e:
            print(f"An error occurred during asset generation: {e}")
            # Decide if you want to proceed with fallback graphics or exit
            # For simplicity, we'll let the loading process handle fallbacks later
        finally:
            # Ensure Pygame is quit if it was initialized for generation
            if pygame_initialized_for_generation:
                pygame.quit()
                print("Temporary Pygame instance for generation quit.")
    else:
        print("All required assets found.")

# --- Global Asset Variables (will be loaded after check/generation) ---
player_img = None
bullet_img = None
invader_images_loaded = {} # Pre-load invader images here
shoot_sound = None
invader_killed_sound = None
player_death_sound = None
use_assets = False # Flag set True if loading succeeds

# --- Asset Loading Function ---
def load_game_assets():
    global player_img, bullet_img, invader_images_loaded, use_assets
    global shoot_sound, invader_killed_sound, player_death_sound
    print("Loading game assets...")
    try:
        # Load images (assuming they exist after the check/generation)
        player_img = pygame.image.load(os.path.join(ASSET_DIR, 'player.png')).convert_alpha()
        bullet_img = pygame.image.load(os.path.join(ASSET_DIR, 'bullet.png')).convert_alpha()

        invader_images_loaded = {}
        for i in range(len(INVADER_COLORS)):
             img_key = f'row{i}'
             img_a = pygame.image.load(os.path.join(ASSET_DIR, f'invader_row{i}_a.png')).convert_alpha()
             img_b = pygame.image.load(os.path.join(ASSET_DIR, f'invader_row{i}_b.png')).convert_alpha()
             # Scale them if needed (optional, but good practice if source differs)
             img_a_scaled = pygame.transform.scale(img_a, (INVADER_WIDTH, INVADER_HEIGHT))
             img_b_scaled = pygame.transform.scale(img_b, (INVADER_WIDTH, INVADER_HEIGHT))
             invader_images_loaded[img_key] = [img_a_scaled, img_b_scaled]

        # Load sounds (optional, place dummy files if you want to test without real sounds)
        # Sound loading might fail if files are missing, even if directory exists
        try:
            shoot_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, 'shoot.wav'))
            invader_killed_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, 'invaderkilled.wav'))
            player_death_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, 'explosion.wav'))
            print("Sounds loaded.")
        except pygame.error as e:
            print(f"Warning: Could not load sounds. {e}")
            # Set sounds to None so the game doesn't crash trying to play them
            shoot_sound = None
            invader_killed_sound = None
            player_death_sound = None

        use_assets = True # Mark assets as successfully loaded
        print("Image assets loaded successfully.")

    except pygame.error as e:
        print(f"Error loading image assets: {e}. Game will use fallback drawings.")
        use_assets = False
        # Reset image vars to ensure fallback is used
        player_img = None
        bullet_img = None
        invader_images_loaded = {}
    except Exception as e:
         print(f"An unexpected error occurred during asset loading: {e}")
         use_assets = False
         player_img = None
         bullet_img = None
         invader_images_loaded = {}


# --- Fallback Cache (if asset loading fails) ---
invader_fallback_cache = {}

# --- Helper Functions ---
def draw_text(surface, text, size, x, y, color=WHITE, font_name=None):
    """Draws text on the screen."""
    if font_name is None:
        font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_lives(surface, x, y, lives, img=None):
    """Draws player lives icons."""
    img_width = PLAYER_WIDTH // 1.5
    img_height = PLAYER_HEIGHT // 1.5
    for i in range(lives - 1):
        pos_x = x + (img_width + 5) * i
        if use_assets and img: # Use scaled image if assets loaded
             try: # Protect against img being None unexpectedly
                 img_scaled = pygame.transform.scale(img, (int(img_width), int(img_height)))
                 img_rect = img_scaled.get_rect()
                 img_rect.left = pos_x
                 img_rect.bottom = y
                 surface.blit(img_scaled, img_rect)
             except:
                  # Draw fallback rect if scaling/blitting fails
                 rect = pygame.Rect(pos_x, y - img_height, img_width, img_height)
                 pygame.draw.rect(surface, PLAYER_COLOR, rect)
        else: # Draw fallback rectangle if no assets
             rect = pygame.Rect(pos_x, y - img_height, img_width, img_height)
             pygame.draw.rect(surface, PLAYER_COLOR, rect)


# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image_orig = None # Store original for scaling lives icon
        if use_assets and player_img:
            self.image_orig = player_img
            self.image = self.image_orig.copy()
        else:
            # Fallback drawing
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(PLAYER_COLOR)
            pygame.draw.rect(self.image, WHITE, (PLAYER_WIDTH // 2 - 2, 0, 4, 5)) # Nozzle detail
            self.image_orig = self.image # Use drawing for lives icon

        self.rect = self.image.get_rect()
        self.rect.centerx = PLAYER_START_X
        self.rect.bottom = PLAYER_START_Y
        self.speed_x = 0
        self.lives = PLAYER_LIVES
        self.last_shot_time = pygame.time.get_ticks()
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.hide_duration = 1000 # ms

    def update(self):
        now = pygame.time.get_ticks()
        if self.hidden and now - self.hide_timer > self.hide_duration:
            self.hidden = False
            self.rect.centerx = PLAYER_START_X
            self.rect.bottom = PLAYER_START_Y

        if self.hidden:
             return

        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speed_x = -PLAYER_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speed_x = PLAYER_SPEED
        if keystate[pygame.K_SPACE]:
            self.shoot()

        self.rect.x += self.speed_x
        self.rect.clamp_ip(self.game.screen.get_rect()) # Keep player on screen

    def shoot(self):
        now = pygame.time.get_ticks()
        if not self.hidden and now - self.last_shot_time > PLAYER_GUN_COOLDOWN:
            self.last_shot_time = now
            bullet = Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED)
            self.game.all_sprites.add(bullet)
            self.game.player_bullets.add(bullet)
            if shoot_sound:
                 shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (-500, -500) # Move way off screen
        self.lives -= 1
        if player_death_sound:
            player_death_sound.play()

    def draw(self, surface):
         if not self.hidden:
             surface.blit(self.image, self.rect)

class Invader(pygame.sprite.Sprite):
    def __init__(self, x, y, row, col, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.row = row
        self.col = col
        self.points = INVADER_POINTS.get(row, 10)

        self.image_type = row % len(INVADER_COLORS) # Map row to image type index
        self.anim_frame = 0
        self.images = []

        if use_assets:
            img_key = f'row{self.image_type}'
            if img_key in invader_images_loaded:
                 self.images = invader_images_loaded[img_key]
            else:
                 print(f"Warning: Missing loaded images for {img_key}, using fallback.")
                 self.images = self._get_fallback_images()
        else:
             self.images = self._get_fallback_images()

        # Final check in case something went wrong
        if not self.images:
             print(f"CRITICAL: No images for Invader row {row}. Creating emergency fallback.")
             img = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT))
             img.fill(RED)
             self.images = [img, img]

        self.image = self.images[self.anim_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def _get_fallback_images(self):
        """Gets or creates simple drawing surfaces if images aren't loaded."""
        global invader_fallback_cache
        key = (self.image_type, INVADER_WIDTH, INVADER_HEIGHT)
        if key not in invader_fallback_cache:
             images = []
             color = INVADER_COLORS[self.image_type]
             # Simple block shape - Frame A
             img_a = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT), pygame.SRCALPHA)
             img_a.fill(color)
             pygame.draw.rect(img_a, WHITE, (5, INVADER_HEIGHT-5, 4, 4))
             pygame.draw.rect(img_a, WHITE, (INVADER_WIDTH-9, INVADER_HEIGHT-5, 4, 4))
             # Frame B
             img_b = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT), pygame.SRCALPHA)
             img_b.fill(color)
             pygame.draw.rect(img_b, BLACK, (0, INVADER_HEIGHT-5, 4, 4))
             pygame.draw.rect(img_b, BLACK, (INVADER_WIDTH-4, INVADER_HEIGHT-5, 4, 4))

             images.append(img_a)
             images.append(img_b)
             invader_fallback_cache[key] = images
        return invader_fallback_cache[key]

    def update(self):
        # Animation is toggled by the Game class
        pass

    def toggle_animation(self):
         self.anim_frame = 1 - self.anim_frame
         # Handle potential errors if images list is somehow wrong
         try:
            self.image = self.images[self.anim_frame]
            # Center preservation might be needed if frames have different transparent padding
            # old_center = self.rect.center
            # self.rect = self.image.get_rect(center=old_center)
         except IndexError:
              print(f"Error toggling animation for invader (row {self.row}, col {self.col}). Frame: {self.anim_frame}, Images: {len(self.images)}")
              # Use frame 0 as a safe default if index is out of bounds
              if self.images:
                   self.image = self.images[0]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y):
        pygame.sprite.Sprite.__init__(self)
        if use_assets and bullet_img:
             self.image = bullet_img
        else:
            self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
            self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        if speed_y < 0: self.rect.bottom = y # Player bullet
        else: self.rect.top = y # Invader bullet
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class BarrierPart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.size = BARRIER_PART_SIZE
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BARRIER_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = BARRIER_HITS_TO_DESTROY

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            # Degrade visually (simple darken)
            try:
                current_color = self.image.get_at((0,0))
                fade = 60 # Increase fade for more noticeable steps
                new_r = max(0, current_color[0] - fade)
                new_g = max(0, current_color[1] - fade)
                new_b = max(0, current_color[2] - fade)
                self.image.fill((new_r, new_g, new_b))
            except Exception as e:
                print(f"Error getting/setting barrier color: {e}") # Handle potential errors


# --- Game Class ---
class Game:
    def __init__(self):
        # Pygame is initialized in main execution block BEFORE Game() is created
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "START"
        self.score = 0
        self.level = 1
        self.font_name = pygame.font.match_font('arial')

        # Game state variables reset in new_game()
        self.player = None
        self.all_sprites = pygame.sprite.Group()
        self.invaders = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.invader_bullets = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.bottom_invaders = {}

        self.invader_direction = 1
        self.invader_move_timer = 0
        self.invader_current_move_interval = INVADER_INITIAL_MOVE_INTERVAL
        self.invaders_need_to_drop = False
        self.invader_shoot_timer = 0
        self.invader_current_shoot_cooldown = random.randint(INVADER_SHOOT_COOLDOWN_MIN, INVADER_SHOOT_COOLDOWN_MAX)

    def create_invader_grid(self):
        self.bottom_invaders.clear()
        total_grid_width = (INVADER_COLS * INVADER_WIDTH) + ((INVADER_COLS - 1) * INVADER_H_SPACE)
        start_offset_x = (SCREEN_WIDTH - total_grid_width) // 2

        for row in range(INVADER_ROWS):
            for col in range(INVADER_COLS):
                x = start_offset_x + col * (INVADER_WIDTH + INVADER_H_SPACE)
                y = INVADER_START_Y + row * (INVADER_HEIGHT + INVADER_V_SPACE)
                invader = Invader(x, y, row, col, self)
                self.all_sprites.add(invader)
                self.invaders.add(invader)
                # Track bottom invader in each column
                if col not in self.bottom_invaders or invader.rect.bottom > self.bottom_invaders[col].rect.bottom:
                    self.bottom_invaders[col] = invader

    def update_bottom_invaders(self, killed_invader=None):
        if killed_invader:
            col = killed_invader.col
            if col in self.bottom_invaders and self.bottom_invaders[col] == killed_invader:
                self.bottom_invaders.pop(col) # Remove killed one
                highest_in_col = None
                for invader in self.invaders: # Find the next one down in that column
                    if invader.col == col:
                        if highest_in_col is None or invader.rect.bottom > highest_in_col.rect.bottom:
                            highest_in_col = invader
                if highest_in_col:
                    self.bottom_invaders[col] = highest_in_col
        # No need for full recalc unless wave changes typically

    def create_barriers(self):
        barrier_width_parts = 7
        barrier_height_parts = 5
        # Calculate spacing more dynamically
        total_barrier_block_width = BARRIER_COUNT * barrier_width_parts * BARRIER_PART_SIZE
        available_space = SCREEN_WIDTH - 100 # Margins
        if BARRIER_COUNT > 1:
            space_between_barriers = (available_space - total_barrier_block_width) // (BARRIER_COUNT - 1)
        else:
            space_between_barriers = 0 # Or center it if only one
        start_x = 50

        barrier_shape = ["1111111","1111111","1100011","1000001","1000001"]

        for i in range(BARRIER_COUNT):
            barrier_base_x = start_x + i * (barrier_width_parts * BARRIER_PART_SIZE + space_between_barriers)
            for row_idx, row_str in enumerate(barrier_shape):
                 for col_idx, char in enumerate(row_str):
                     if char == '1':
                        part_x = barrier_base_x + col_idx * BARRIER_PART_SIZE
                        part_y = BARRIER_Y_POS + row_idx * BARRIER_PART_SIZE
                        part = BarrierPart(part_x, part_y)
                        self.all_sprites.add(part)
                        self.barriers.add(part)

    def new_game(self):
        self.score = 0
        self.level = 1
        self.state = "PLAYING"
        self.invader_current_move_interval = INVADER_INITIAL_MOVE_INTERVAL
        self.invader_direction = 1
        self.invaders_need_to_drop = False

        # Clear groups before adding new sprites
        self.all_sprites.empty()
        self.invaders.empty()
        self.player_bullets.empty()
        self.invader_bullets.empty()
        self.barriers.empty()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.create_invader_grid()
        self.create_barriers()

        # Reset timers
        self.invader_move_timer = pygame.time.get_ticks()
        self.invader_shoot_timer = pygame.time.get_ticks()
        self.invader_current_shoot_cooldown = random.randint(INVADER_SHOOT_COOLDOWN_MIN, INVADER_SHOOT_COOLDOWN_MAX)

        # Start the game loop specific to this play session
        self.run()

    def next_level(self):
        print(f"Starting Level {self.level + 1}")
        self.level += 1
        self.state = "PLAYING"
        self.invader_current_move_interval = max(100, self.invader_current_move_interval * 0.9) # Speed up, with minimum
        self.invader_direction = 1
        self.invaders_need_to_drop = False

        # Clear remaining bullets and invaders
        self.invaders.empty() # Kill existing invaders first
        self.player_bullets.empty()
        self.invader_bullets.empty()

        # Remove dead sprites from all_sprites group (important!)
        self.all_sprites.remove(*self.invaders)
        self.all_sprites.remove(*self.player_bullets)
        self.all_sprites.remove(*self.invader_bullets)


        # Keep damaged barriers
        # Keep player (reset position maybe)
        self.player.rect.centerx = PLAYER_START_X
        self.player.rect.bottom = PLAYER_START_Y
        self.player.hidden = False # Ensure player is visible

        # Create new grid
        self.create_invader_grid()

        # Reset timers
        self.invader_move_timer = pygame.time.get_ticks()
        self.invader_shoot_timer = pygame.time.get_ticks()
        self.invader_current_shoot_cooldown = random.randint(INVADER_SHOOT_COOLDOWN_MIN, INVADER_SHOOT_COOLDOWN_MAX)

        # Short pause/message display?
        self.screen.fill(BLACK)
        draw_text(self.screen, f"LEVEL {self.level}", 48, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
        pygame.display.flip()
        pygame.time.wait(1500)


    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds (optional)
            self.events()
            if self.state == "PLAYING":
                self.update()
            self.draw()

    def move_invaders(self):
        now = pygame.time.get_ticks()
        if now - self.invader_move_timer > self.invader_current_move_interval:
            self.invader_move_timer = now
            move_x = INVADER_INITIAL_MOVE_SPEED * self.invader_direction
            move_y = 0
            lowest_invader_pos = 0
            hit_edge = False

            if self.invaders_need_to_drop:
                move_x = 0
                move_y = INVADER_DROP_AMOUNT
                self.invader_direction *= -1
                self.invaders_need_to_drop = False # Reset flag *after* using it

            # Update positions and check edges in one loop
            for invader in self.invaders:
                invader.rect.x += move_x
                invader.rect.y += move_y
                invader.toggle_animation()

                # Check screen boundary collision only if not dropping
                if move_y == 0:
                     if (invader.rect.right > SCREEN_WIDTH - 10 and self.invader_direction == 1) or \
                        (invader.rect.left < 10 and self.invader_direction == -1):
                          hit_edge = True

                if invader.rect.bottom > lowest_invader_pos:
                    lowest_invader_pos = invader.rect.bottom

            # If an edge was hit during horizontal movement, schedule a drop for the *next* move cycle
            if hit_edge:
                 self.invaders_need_to_drop = True

            # Game Over check: Invaders reached barrier level or player level
            if lowest_invader_pos >= BARRIER_Y_POS - INVADER_HEIGHT // 2: # Reached top of barriers
                 print("Game Over: Invaders reached barriers.")
                 self.state = "GAME_OVER"
                 self.playing = False


    def invader_maybe_shoot(self):
         now = pygame.time.get_ticks()
         if now - self.invader_shoot_timer > self.invader_current_shoot_cooldown:
              self.invader_shoot_timer = now
              self.invader_current_shoot_cooldown = random.randint(INVADER_SHOOT_COOLDOWN_MIN, INVADER_SHOOT_COOLDOWN_MAX)

              eligible_shooters = list(self.bottom_invaders.values())
              if eligible_shooters:
                   shooter = random.choice(eligible_shooters)
                   bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, BULLET_SPEED)
                   self.all_sprites.add(bullet)
                   self.invader_bullets.add(bullet)
                   # Play invader shoot sound here if loaded

    def update(self):
        self.all_sprites.update()
        self.move_invaders()
        self.invader_maybe_shoot()

        # Collisions
        hits = pygame.sprite.groupcollide(self.invaders, self.player_bullets, True, True)
        for invader_hit in hits:
            self.score += invader_hit.points
            if invader_killed_sound: invader_killed_sound.play()
            self.invader_current_move_interval = max(50, self.invader_current_move_interval * INVADER_SPEEDUP_FACTOR) # Speed up, min interval 50ms
            self.update_bottom_invaders(killed_invader=invader_hit)
            # Explosion effect?

        if not self.player.hidden:
            hits = pygame.sprite.spritecollide(self.player, self.invader_bullets, True, pygame.sprite.collide_rect_ratio(0.8)) # Rect collision often fine
            if hits:
                self.player.hide()
                if self.player.lives <= 0:
                    print("Game Over: Player out of lives.")
                    self.state = "GAME_OVER"
                    self.playing = False # Stop inner loop

        # Bullets hitting barriers (both types)
        barrier_player_bullet_hits = pygame.sprite.groupcollide(self.barriers, self.player_bullets, False, True)
        for part, bullets in barrier_player_bullet_hits.items():
             part.hit()

        barrier_invader_bullet_hits = pygame.sprite.groupcollide(self.barriers, self.invader_bullets, False, True)
        for part, bullets in barrier_invader_bullet_hits.items():
             part.hit()

        # Invaders reaching barriers (destroy barrier part instantly)
        invader_barrier_hits = pygame.sprite.groupcollide(self.barriers, self.invaders, True, False) # Kill barrier part
        # No action needed for invader, they just pass through

        # Check for level clear
        if not self.invaders:
             # Stop current gameplay loop to transition
             self.playing = False
             # Set state for next level (will be handled in main loop)
             self.state = "NEXT_WAVE"


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False # Stop outer loop too
            # Handle input based on state (only relevant if not in self.run())
            # Input during PLAYING is handled by player.update()
            if self.state != "PLAYING":
                 if event.type == pygame.KEYDOWN:
                    if self.state == "START":
                        if event.key == pygame.K_RETURN:
                             # new_game() will be called in the main loop based on state change
                             self.state = "NEW_GAME_REQUEST" # Signal to main loop
                        if event.key == pygame.K_ESCAPE:
                             self.running = False
                    elif self.state == "GAME_OVER":
                        if event.key == pygame.K_RETURN:
                             self.state = "START" # Go back to menu
                        if event.key == pygame.K_ESCAPE:
                             self.running = False


    def draw(self):
        self.screen.fill(BLACK)
        # Draw elements based on state
        if self.state == "START":
            self.show_start_screen()
        elif self.state == "PLAYING":
            # Draw all sprites (player uses its own draw method)
            for sprite in self.all_sprites:
                if isinstance(sprite, Player):
                    sprite.draw(self.screen)
                else:
                    self.screen.blit(sprite.image, sprite.rect)
            # UI
            draw_text(self.screen, f"Score: {self.score}", 18, SCREEN_WIDTH / 2, 10)
            draw_text(self.screen, f"Level: {self.level}", 18, SCREEN_WIDTH - 50, 10)
            draw_lives(self.screen, 10, SCREEN_HEIGHT - 5, self.player.lives, self.player.image_orig) # Pass original potentially loaded image
        elif self.state == "GAME_OVER":
             # Optionally draw final game state behind text
             # for sprite in self.all_sprites: self.screen.blit(sprite.image, sprite.rect)
            self.show_game_over_screen()
        # Draw other states if needed (e.g., PAUSED)

        pygame.display.flip()


    def show_start_screen(self):
        # self.screen.fill(BLACK) # Already filled in draw()
        draw_text(self.screen, "SPACE INVADERS", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, "Arrows or A/D to move, Space to shoot", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "Press ENTER to begin", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)

    def show_game_over_screen(self):
        # self.screen.fill(BLACK) # Already filled in draw()
        draw_text(self.screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, f"Final Score: {self.score}", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "Press ENTER for Menu", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        draw_text(self.screen, "Press ESCAPE to Quit", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 40)

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Check for assets and generate if missing
    check_and_generate_assets()

    # 2. Initialize Pygame for the main game
    print("Initializing Pygame for game...")
    pygame.init()
    pygame.mixer.init() # Initialize mixer for sounds

    # 3. Load assets (after checking/generating)
    load_game_assets()

    # 4. Create Game instance
    game = Game()

    # 5. Main Loop (handles state transitions)
    while game.running:
        if game.state == "START":
            game.events() # Handle ENTER to start or ESC to quit
            game.draw() # Show start screen
        elif game.state == "NEW_GAME_REQUEST":
             print("Starting New Game...")
             game.new_game() # This enters the inner 'run' loop
             # After new_game().run() finishes (player lost or beat level),
             # control returns here. The state will be GAME_OVER or NEXT_WAVE.
        elif game.state == "NEXT_WAVE":
             game.next_level() # Sets up next level
             game.run() # Enters the inner 'run' loop again for the new level
        elif game.state == "GAME_OVER":
            game.events() # Handle ENTER for menu or ESC to quit
            game.draw() # Show game over screen
        else:
            # Fallback for unexpected states
            print(f"Unhandled game state: {game.state}")
            game.running = False

        # Small delay to prevent hogging CPU in menu states
        # game.clock.tick(15) # Only needed if not calling clock.tick inside run()

    # 6. Quit Pygame
    print("Exiting Game.")
    pygame.quit()
    sys.exit()