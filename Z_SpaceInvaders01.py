# Import necessary libraries
import pygame
import random
import math
import sys # To exit cleanly
from os import path # For potential asset loading

# PROMPT for Gemini 2.5 Pro Experimental 03-25 :  Write Space Invaders game in python using pygame library. Make it visually appealing


# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLAYER_COLOR = GREEN
INVADER_COLORS = [(200, 200, 200), (150, 150, 250), (250, 150, 150)] # Different rows
BULLET_COLOR = YELLOW
BARRIER_COLOR = GREEN

# Player properties
PLAYER_SPEED = 5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 20
PLAYER_LIVES = 3
PLAYER_GUN_COOLDOWN = 400 # milliseconds
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 50

# Bullet properties
BULLET_SPEED = 7
BULLET_WIDTH = 4
BULLET_HEIGHT = 10

# Invader properties
INVADER_WIDTH = 30
INVADER_HEIGHT = 20
INVADER_ROWS = 5
INVADER_COLS = 11
INVADER_H_SPACE = 15 # Horizontal space between invaders
INVADER_V_SPACE = 10 # Vertical space between invaders
INVADER_START_X = 50
INVADER_START_Y = 50
INVADER_INITIAL_MOVE_SPEED = 1 # Initial pixels per move
INVADER_INITIAL_MOVE_INTERVAL = 1000 # milliseconds between moves (decreases)
INVADER_DROP_AMOUNT = 10 # Pixels invaders drop when hitting edge
INVADER_SHOOT_COOLDOWN_MIN = 1000 # Min ms between any invader shot
INVADER_SHOOT_COOLDOWN_MAX = 5000 # Max ms
INVADER_SPEEDUP_FACTOR = 0.95 # Multiplier for move interval when one dies
INVADER_POINTS = {0: 30, 1: 20, 2: 20, 3: 10, 4: 10} # Points per row (top=0)

# Barrier properties
BARRIER_COUNT = 4
BARRIER_PART_SIZE = 8 # Size of one block in the barrier
BARRIER_Y_POS = SCREEN_HEIGHT - 120
BARRIER_HITS_TO_DESTROY = 4

# --- Asset loading (Placeholders - replace with actual loading) ---
# asset_dir = path.join(path.dirname(__file__), 'assets') # Assumes 'assets' folder
# try:
#     player_img = pygame.image.load(path.join(asset_dir, 'player.png')).convert_alpha()
#     invader_imgs = [
#         pygame.image.load(path.join(asset_dir, 'invader1a.png')).convert_alpha(),
#         pygame.image.load(path.join(asset_dir, 'invader1b.png')).convert_alpha(),
#         # ... load other invader types and animation frames
#     ]
#     bullet_img = pygame.image.load(path.join(asset_dir, 'bullet.png')).convert_alpha()
#     # Load sounds
#     shoot_sound = pygame.mixer.Sound(path.join(asset_dir, 'shoot.wav'))
#     invader_killed_sound = pygame.mixer.Sound(path.join(asset_dir, 'invaderkilled.wav'))
#     player_death_sound = pygame.mixer.Sound(path.join(asset_dir, 'explosion.wav'))
# except pygame.error as e:
#     print(f"Warning: Could not load assets. Using drawing. Error: {e}")
player_img = None
invader_imgs_data = {} # Store generated surfaces if no assets
bullet_img = None
shoot_sound = None
invader_killed_sound = None
player_death_sound = None
# --- Helper Functions ---

def draw_text(surface, text, size, x, y, color=WHITE, font_name=None):
    """Draws text on the screen."""
    if font_name is None:
        font_name = pygame.font.match_font('arial') # Or use 'pressstart2p' if installed
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_lives(surface, x, y, lives, img=None):
    """Draws player lives icons."""
    for i in range(lives - 1): # Draw icons for remaining lives (excluding current one)
        if img:
             img_rect = img.get_rect()
             img_scaled = pygame.transform.scale(img, (PLAYER_WIDTH // 1.5, PLAYER_HEIGHT // 1.5))
             img_rect = img_scaled.get_rect()
             img_rect.left = x + 40 * i
             img_rect.bottom = y
             surface.blit(img_scaled, img_rect)
        else:
             # Draw simple rectangle if no image
             rect = pygame.Rect(x + 30 * i, y - PLAYER_HEIGHT // 1.5, PLAYER_WIDTH // 1.5, PLAYER_HEIGHT // 1.5)
             pygame.draw.rect(surface, PLAYER_COLOR, rect)


# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image_orig = None
        if player_img:
            self.image_orig = player_img
            self.image = self.image_orig.copy()
        else:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(PLAYER_COLOR)
            # Add a little detail
            pygame.draw.rect(self.image, WHITE, (PLAYER_WIDTH // 2 - 2, 0, 4, 5))

        self.rect = self.image.get_rect()
        self.rect.centerx = PLAYER_START_X
        self.rect.bottom = PLAYER_START_Y
        self.speed_x = 0
        self.lives = PLAYER_LIVES
        self.last_shot_time = pygame.time.get_ticks()
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
         # Unhide if necessary
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = PLAYER_START_X
            self.rect.bottom = PLAYER_START_Y

        if self.hidden:
             return # Don't process input/movement if hidden

        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speed_x = -PLAYER_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speed_x = PLAYER_SPEED
        if keystate[pygame.K_SPACE]:
            self.shoot()

        self.rect.x += self.speed_x

        # Keep player on screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if not self.hidden and now - self.last_shot_time > PLAYER_GUN_COOLDOWN:
            self.last_shot_time = now
            bullet = Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED) # Negative speed = up
            self.game.all_sprites.add(bullet)
            self.game.player_bullets.add(bullet)
            if shoot_sound:
                 shoot_sound.play()

    def hide(self):
        """Temporarily hide the player after being hit."""
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (-200, -200) # Move off-screen
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
        self.points = INVADER_POINTS.get(row, 10) # Get points based on row

        # --- Image Handling ---
        self.image_type = row % len(INVADER_COLORS) # Cycle through colors/types if needed
        self.anim_frame = 0
        self.images = []

        # Attempt to load images or create fallback drawings
        # This part needs specific asset names if using real images
        if player_img: # Using player_img load success as a proxy for all assets
             # Example: Assuming names like 'invader_row0_a.png', 'invader_row0_b.png' etc.
             try:
                 img_a = pygame.image.load(path.join(asset_dir, f'invader_row{self.image_type}_a.png')).convert_alpha()
                 img_b = pygame.image.load(path.join(asset_dir, f'invader_row{self.image_type}_b.png')).convert_alpha()
                 img_a_scaled = pygame.transform.scale(img_a, (INVADER_WIDTH, INVADER_HEIGHT))
                 img_b_scaled = pygame.transform.scale(img_b, (INVADER_WIDTH, INVADER_HEIGHT))
                 self.images.append(img_a_scaled)
                 self.images.append(img_b_scaled)
             except:
                 # Fallback if specific invader images fail
                 self.images = self._create_fallback_images()
        else:
             self.images = self._create_fallback_images()

        self.image = self.images[self.anim_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # --- End Image Handling ---


    def _create_fallback_images(self):
        """Creates simple drawing surfaces if images aren't loaded."""
        key = (self.image_type, INVADER_WIDTH, INVADER_HEIGHT)
        if key not in invader_imgs_data:
             images = []
             color = INVADER_COLORS[self.image_type]
             # Simple block shape
             img_a = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT), pygame.SRCALPHA)
             img_a.fill(color)
             pygame.draw.rect(img_a, WHITE, (5, INVADER_HEIGHT-5, 4, 4)) # Little detail 1
             pygame.draw.rect(img_a, WHITE, (INVADER_WIDTH-9, INVADER_HEIGHT-5, 4, 4)) # Little detail 2

             # Slightly different shape for animation
             img_b = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT), pygame.SRCALPHA)
             img_b.fill(color)
             pygame.draw.rect(img_b, BLACK, (0, INVADER_HEIGHT-5, 4, 4))
             pygame.draw.rect(img_b, BLACK, (INVADER_WIDTH-4, INVADER_HEIGHT-5, 4, 4))

             images.append(img_a)
             images.append(img_b)
             invader_imgs_data[key] = images # Cache generated images
        return invader_imgs_data[key]


    def update(self):
        # Animation is toggled by the Game class during movement
        pass

    def toggle_animation(self):
         self.anim_frame = 1 - self.anim_frame # Toggle between 0 and 1
         self.image = self.images[self.anim_frame]
         # Need to preserve center after changing image if sizes differ slightly
         # old_center = self.rect.center
         # self.rect = self.image.get_rect()
         # self.rect.center = old_center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y):
        pygame.sprite.Sprite.__init__(self)
        if bullet_img:
             self.image = bullet_img
        else:
            self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
            self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y # Start slightly above player or below invader
        if speed_y < 0: # Player bullet starts above player
             self.rect.bottom = y
        else: # Invader bullet starts below invader
             self.rect.top = y
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y
        # Kill if it moves off the screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class BarrierPart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.size = BARRIER_PART_SIZE
        # Start with a full block image
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BARRIER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = BARRIER_HITS_TO_DESTROY

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            # Visually degrade the barrier part (e.g., darken color, could use multiple images)
            # Simple darkening:
            current_color = self.image.get_at((0,0))
            fade = 50
            new_color = (max(0, current_color[0]-fade), max(0, current_color[1]-fade), max(0, current_color[2]-fade))
            self.image.fill(new_color)


# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # For sound
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "START" # START, PLAYING, GAME_OVER, NEXT_WAVE
        self.score = 0
        self.level = 1
        self.font_name = pygame.font.match_font('arial') # Or find a pixel font

        # Invader movement control
        self.invader_direction = 1 # 1 = right, -1 = left
        self.invader_move_timer = pygame.time.get_ticks()
        self.invader_current_move_interval = INVADER_INITIAL_MOVE_INTERVAL
        self.invaders_need_to_drop = False

        # Invader shooting control
        self.invader_shoot_timer = pygame.time.get_ticks()
        self.invader_current_shoot_cooldown = random.randint(INVADER_SHOOT_COOLDOWN_MIN, INVADER_SHOOT_COOLDOWN_MAX)

        # For managing which invaders can shoot
        self.bottom_invaders = {} # key: col, value: invader sprite


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
                # Track the bottom-most invader in each column
                if col not in self.bottom_invaders or invader.rect.bottom > self.bottom_invaders[col].rect.bottom:
                    self.bottom_invaders[col] = invader

    def update_bottom_invaders(self, killed_invader=None):
         """ Recalculate bottom invaders, potentially optimized if killed_invader is known """
         if killed_invader:
              col = killed_invader.col
              # If the killed one was the bottom one in its column, find the next highest
              if col in self.bottom_invaders and self.bottom_invaders[col] == killed_invader:
                   self.bottom_invaders.pop(col) # Remove it first
                   highest_in_col = None
                   for invader in self.invaders:
                        if invader.col == col:
                             if highest_in_col is None or invader.rect.bottom > highest_in_col.rect.bottom:
                                  highest_in_col = invader
                   if highest_in_col:
                        self.bottom_invaders[col] = highest_in_col
         else: # Full recalculation if no specific one killed (e.g., new wave)
              self.bottom_invaders.clear()
              for invader in self.invaders:
                   col = invader.col
                   if col not in self.bottom_invaders or invader.rect.bottom > self.bottom_invaders[col].rect.bottom:
                       self.bottom_invaders[col] = invader


    def create_barriers(self):
        barrier_width_parts = 7 # How many blocks wide
        barrier_height_parts = 5 # How many blocks tall
        total_barrier_span = BARRIER_COUNT * barrier_width_parts * BARRIER_PART_SIZE
        space_between_barriers = (SCREEN_WIDTH - total_barrier_span - 100) // (BARRIER_COUNT - 1 if BARRIER_COUNT > 1 else 1)
        start_x = 50

        barrier_shape = [ # Simple blocky U-shape (1=part, 0=empty)
            "1111111",
            "1111111",
            "1100011",
            "1000001",
            "1000001"
        ]

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

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.invaders = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.invader_bullets = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()

        # Create player
        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Create invaders and barriers
        self.create_invader_grid()
        self.create_barriers()

        self.run() # Start the main game loop for this new game


    def next_level(self):
        self.level += 1
        self.state = "PLAYING" # Or maybe a brief "NEXT_WAVE" state display
        self.invader_current_move_interval *= 0.9 # Make next wave faster
        self.invader_direction = 1
        self.invaders_need_to_drop = False

        # Clear bullets
        for bullet in self.player_bullets: bullet.kill()
        for bullet in self.invader_bullets: bullet.kill()
        # Barriers might persist or regenerate - let's keep them damaged
        # self.barriers.empty() # Uncomment to regenerate barriers fully
        # self.create_barriers() # Uncomment to regenerate barriers fully

        # Respawn player if needed? (Usually not between levels)
        self.player.rect.centerx = PLAYER_START_X
        self.player.rect.bottom = PLAYER_START_Y

        # Create new invaders
        self.create_invader_grid()

        # Short delay maybe?
        pygame.time.wait(1000)


    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
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

            if self.invaders_need_to_drop:
                move_x = 0
                move_y = INVADER_DROP_AMOUNT
                self.invader_direction *= -1 # Change direction after dropping
                self.invaders_need_to_drop = False # Reset drop flag

            hit_edge = False
            lowest_invader_pos = 0
            for invader in self.invaders:
                invader.rect.x += move_x
                invader.rect.y += move_y
                invader.toggle_animation() # Animate on each move step

                # Check if any invader hits the side AFTER moving (if not dropping)
                if move_y == 0:
                     if (invader.rect.right > SCREEN_WIDTH - 10 and self.invader_direction == 1) or \
                        (invader.rect.left < 10 and self.invader_direction == -1):
                          hit_edge = True

                # Track the lowest position
                if invader.rect.bottom > lowest_invader_pos:
                    lowest_invader_pos = invader.rect.bottom

            if hit_edge:
                 self.invaders_need_to_drop = True # Signal drop on next move cycle

            # Check if invaders reached player level (Game Over condition)
            if lowest_invader_pos >= self.player.rect.top - 10:
                 self.state = "GAME_OVER"
                 self.playing = False


    def invader_maybe_shoot(self):
         now = pygame.time.get_ticks()
         if now - self.invader_shoot_timer > self.invader_current_shoot_cooldown:
              self.invader_shoot_timer = now
              self.invader_current_shoot_cooldown = random.randint(INVADER_SHOOT_COOLDOWN_MIN, INVADER_SHOOT_COOLDOWN_MAX)

              # Pick a random column that still has invaders
              eligible_shooters = list(self.bottom_invaders.values())
              if eligible_shooters:
                   shooter = random.choice(eligible_shooters)
                   bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, BULLET_SPEED) # Positive speed = down
                   self.all_sprites.add(bullet)
                   self.invader_bullets.add(bullet)
                   # Play invader shoot sound if available


    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        self.move_invaders()
        self.invader_maybe_shoot()

        # --- Collision Detection ---

        # Player bullets hitting invaders
        hits = pygame.sprite.groupcollide(self.invaders, self.player_bullets, True, True)
        for invader_hit in hits: # The keys are the invaders hit
            self.score += invader_hit.points
            if invader_killed_sound:
                 invader_killed_sound.play()
            # Speed up remaining invaders
            self.invader_current_move_interval *= INVADER_SPEEDUP_FACTOR
            # Update who is at the bottom for shooting
            self.update_bottom_invaders(killed_invader=invader_hit)
            # Add explosion effect maybe?

        # Invader bullets hitting player
        hits = pygame.sprite.spritecollide(self.player, self.invader_bullets, True, pygame.sprite.collide_mask) # Use mask if images have transparency
        if hits and not self.player.hidden:
            self.player.hide()
            if self.player.lives <= 0:
                self.state = "GAME_OVER"
                self.playing = False # Stop this game instance loop

        # Bullets (either type) hitting barriers
        pygame.sprite.groupcollide(self.player_bullets, self.barriers, True, False, pygame.sprite.collide_mask)
        barrier_hits = pygame.sprite.groupcollide(self.invader_bullets, self.barriers, True, False, pygame.sprite.collide_mask)
        for bullet, parts_hit in barrier_hits.items():
             for part in parts_hit:
                 part.hit() # Damage the barrier part


        # Invaders hitting barriers (optional - usually they just pass over)
        # barrier_invader_hits = pygame.sprite.groupcollide(self.barriers, self.invaders, True, False)
        # for barrier_part in barrier_invader_hits:
             # Instantly destroy barrier part if invader touches it
        #     barrier_part.kill()

        # Check if all invaders are destroyed
        if not self.invaders:
             # self.playing = False # Stop current loop
             # self.state = "NEXT_WAVE" # Go to next level logic
             self.next_level()


    def events(self):
        # Game Loop - Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
                pygame.quit()
                sys.exit()

            # Handle input based on state
            if self.state == "START":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.new_game()
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            elif self.state == "PLAYING":
                 if event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_ESCAPE: # Optional Pause/Quit
                         self.playing = False # Exit current game
                         self.state = "START" # Go back to menu
            elif self.state == "GAME_OVER":
                 if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = "START" # Go back to menu before starting new game
                    if event.key == pygame.K_ESCAPE:
                         self.running = False


    def draw(self):
        # Game Loop - Draw
        self.screen.fill(BLACK) # Background

        if self.state == "START":
            self.show_start_screen()
        elif self.state == "PLAYING" or self.state == "NEXT_WAVE": # Draw game elements for playing or transitioning
            # Draw all sprites (use Player's custom draw)
            for sprite in self.all_sprites:
                 if isinstance(sprite, Player):
                      sprite.draw(self.screen)
                 else:
                      self.screen.blit(sprite.image, sprite.rect)

            # Draw Score and Level
            draw_text(self.screen, f"Score: {self.score}", 18, SCREEN_WIDTH / 2, 10)
            draw_text(self.screen, f"Level: {self.level}", 18, SCREEN_WIDTH - 60, 10)
            # Draw Lives
            draw_lives(self.screen, 10, SCREEN_HEIGHT - 10, self.player.lives, self.player.image_orig if player_img else None)

            if self.state == "NEXT_WAVE": # Optional message between waves
                 draw_text(self.screen, f"LEVEL {self.level}", 48, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)


        elif self.state == "GAME_OVER":
            self.show_game_over_screen()

        pygame.display.flip() # Update the screen


    def show_start_screen(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, "SPACE INVADERS", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, "Arrows or A/D to move, Space to shoot", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "Press ENTER to begin", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)

    def show_game_over_screen(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, f"Final Score: {self.score}", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "Press ENTER for Menu", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        draw_text(self.screen, "Press ESCAPE to Quit", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 40)


# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    while game.running:
        if game.state == "START":
             game.show_start_screen()
             pygame.display.flip()
             game.events() # Process events to start/quit
        elif game.state == "GAME_OVER":
             game.show_game_over_screen()
             pygame.display.flip()
             game.events() # Process events to restart/quit
        # Note: The PLAYING state is handled within game.new_game() -> game.run()

    pygame.quit()