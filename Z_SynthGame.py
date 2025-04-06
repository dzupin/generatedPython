import pygame
import random
import math

# PROMPT for Gemini 2.5Pro Preview 03-25:  write a retro synthwave style game in python using pygame library.

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors (Synthwave Palette) ---
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (20, 5, 40) # Dark purple/blue
NEON_PINK = (255, 0, 255)
NEON_CYAN = (0, 255, 255)
NEON_YELLOW = (255, 255, 0)
GRID_COLOR = (80, 0, 120) # Dimmer purple for grid
SUN_YELLOW = (255, 220, 0)
SUN_ORANGE = (255, 100, 0)
WHITE = (255, 255, 255)

# --- Game Settings ---
PLAYER_SPEED = 7
INITIAL_OBSTACLE_SPEED = 4
OBSTACLE_SPEED_INCREASE = 0.005 # How much speed increases per frame
OBSTACLE_SPAWN_RATE = 40 # Lower number means more frequent spawns
MAX_OBSTACLE_SPEED = 12

# --- Initialization ---
pygame.init()
# Optional: Initialize mixer for sound later
# pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Synthwave Runner")
clock = pygame.time.Clock()
try:
    font = pygame.font.Font(None, 36) # Default font
    title_font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 24)
except pygame.error:
    print("Warning: Default font not found. Using system font.")
    font = pygame.font.SysFont(None, 36) # Fallback system font
    title_font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 24)

# --- Game Objects ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Simple triangle shape
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA) # Use SRCALPHA for transparency
        pygame.draw.polygon(self.image, NEON_CYAN, [(0, 40), (20, 0), (40, 40)])
        # Outline
        pygame.draw.polygon(self.image, WHITE, [(0, 40), (20, 0), (40, 40)], 2)
        # self.image.set_colorkey(BLACK) # Not needed with SRCALPHA
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x = PLAYER_SPEED

        self.rect.x += self.speed_x

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        width = random.randint(30, 60)
        height = 20
        self.image = pygame.Surface((width, height))
        self.image.fill(NEON_PINK)
        # Add a simple white highlight/edge
        pygame.draw.line(self.image, WHITE, (0,0), (width, 0), 2)

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -50) # Start off screen top
        self.speed_y = speed

    def update(self):
        self.rect.y += self.speed_y
        # Remove obstacle if it goes off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove sprite from all groups

# --- Drawing Functions ---

def draw_background(surface, grid_offset):
    surface.fill(BACKGROUND_COLOR)

    # --- Horizon ---
    horizon_y = SCREEN_HEIGHT // 2 + 50
    pygame.draw.line(surface, NEON_PINK, (0, horizon_y), (SCREEN_WIDTH, horizon_y), 3)

    # --- Sun ---
    sun_radius = 60
    sun_center = (SCREEN_WIDTH // 2, horizon_y)
    pygame.draw.circle(surface, SUN_ORANGE, sun_center, sun_radius)
    pygame.draw.circle(surface, SUN_YELLOW, sun_center, sun_radius - 15)

    # --- Perspective Grid ---
    num_horizontal_lines = 10
    num_vertical_lines = 15
    vanishing_point = (SCREEN_WIDTH // 2, horizon_y)

    # Horizontal lines (move downwards)
    for i in range(num_horizontal_lines):
        # Calculate y position based on perspective and offset
        # Closer lines move faster
        line_progress = (i + (grid_offset % (SCREEN_HEIGHT / num_horizontal_lines)) / (SCREEN_HEIGHT / num_horizontal_lines)) / num_horizontal_lines
        y = horizon_y + int((SCREEN_HEIGHT - horizon_y) * (line_progress ** 1.5)) # Exponential spacing

        if y < SCREEN_HEIGHT:
            pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)

    # Vertical lines
    for i in range(num_vertical_lines + 1):
        # Calculate x position at the bottom of the screen
        x_bottom = (SCREEN_WIDTH / num_vertical_lines) * i

        # Calculate perspective shift - more extreme towards edges
        center_offset = x_bottom - SCREEN_WIDTH / 2
        perspective_factor = abs(center_offset) / (SCREEN_WIDTH / 2)
        x_horizon = vanishing_point[0] + center_offset * (0.1 + perspective_factor * 0.2) # Adjust multiplier for effect

        pygame.draw.line(surface, GRID_COLOR, (x_bottom, SCREEN_HEIGHT), (x_horizon, horizon_y), 1)


def draw_text(surface, text, size, x, y, color=WHITE):
    if size == "large":
        font_to_use = title_font
    elif size == "small":
        font_to_use = small_font
    else:
        font_to_use = font
    text_surface = font_to_use.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# --- Game States ---
def show_start_screen():
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "Retro Synth Runner", "large", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, NEON_CYAN)
    draw_text(screen, "Use Arrow Keys or A/D to Move", "medium", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
    draw_text(screen, "Press any key to start", "medium", SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, NEON_YELLOW)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                waiting = False

def show_game_over_screen(score):
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "GAME OVER", "large", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, NEON_PINK)
    draw_text(screen, f"Final Score: {score}", "medium", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
    draw_text(screen, "Press R to Restart or Q to Quit", "medium", SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, NEON_YELLOW)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_r:
                    waiting = False

# --- Game Loop ---
game_over = True
running = True
score = 0
obstacle_speed = INITIAL_OBSTACLE_SPEED
obstacle_timer = 0
grid_scroll_speed = 3
grid_y_offset = 0

while running:
    # Handle Start/Game Over screens
    if game_over:
        if score == 0: # Only show start screen initially
             show_start_screen()
        else:
             show_game_over_screen(score)

        # Reset game variables after screen display
        game_over = False
        all_sprites = pygame.sprite.Group()
        obstacles = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        score = 0
        obstacle_speed = INITIAL_OBSTACLE_SPEED
        obstacle_timer = 0
        grid_y_offset = 0


    # --- Process Input (Events) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Optional: Handle keydown for single actions if needed
        # if event.type == pygame.KEYDOWN:
        #    pass

    # --- Update ---
    all_sprites.update()

    # Spawn obstacles
    obstacle_timer += 1
    if obstacle_timer >= OBSTACLE_SPAWN_RATE:
        obstacle_timer = 0
        if len(obstacles) < 15: # Limit number of obstacles on screen
            new_obstacle = Obstacle(obstacle_speed)
            all_sprites.add(new_obstacle)
            obstacles.add(new_obstacle)

    # Increase difficulty (speed)
    if obstacle_speed < MAX_OBSTACLE_SPEED:
        obstacle_speed += OBSTACLE_SPEED_INCREASE
        # Update existing obstacles slightly (optional, can make it harder)
        # for obs in obstacles:
        #     obs.speed_y = obstacle_speed

    # Collision Detection
    hits = pygame.sprite.spritecollide(player, obstacles, False) # False: don't kill obstacles on hit
    if hits:
        game_over = True
        # Optional: Add explosion effect or sound here

    # Update score
    score += 1

    # Update grid scroll offset
    grid_y_offset += grid_scroll_speed
    # No need to reset offset here, the drawing function handles modulo


    # --- Draw / Render ---
    # Draw background elements
    draw_background(screen, grid_y_offset)

    # Draw sprites
    all_sprites.draw(screen)

    # Draw score
    draw_text(screen, f"Score: {score}", "medium", SCREEN_WIDTH - 100, 20, NEON_YELLOW)

    # --- Double Buffering ---
    pygame.display.flip() # Update the full screen

    # --- Control Framerate ---
    clock.tick(FPS)


pygame.quit()