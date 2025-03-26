import pygame
import sys
import random
import time

# PROMPT Gemini_2.5:  write snake game in python using pygame library. Make the game visually appealing

# --- Constants ---
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Directions (using tuples for easier vector addition)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)       # Background
GREEN = (57, 255, 20)        # Snake body
DARK_GREEN = (0, 100, 0)      # Snake head (slightly darker)
RED = (255, 69, 0)           # Food (Tomato Red)
GOLD = (255, 215, 0)         # Score text
GRAY = (128, 128, 128)       # Game over text

# Game speed
INITIAL_SPEED = 10
SPEED_INCREMENT = 0.5 # How much speed increases per food eaten

# --- Game Setup ---
def setup_game():
    """Initializes or resets the game state."""
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2),  # Start in the middle
             (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
             (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
    direction = RIGHT
    change_to = direction
    food_pos = place_food(snake)
    score = 0
    speed = INITIAL_SPEED
    game_over = False
    return snake, direction, change_to, food_pos, score, speed, game_over

def place_food(snake):
    """Places food randomly on the grid, avoiding the snake."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos

# --- Drawing Functions ---
def draw_grid(surface):
    """Optional: Draw subtle grid lines for better orientation."""
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)

def draw_snake(surface, snake):
    """Draws the snake with rounded segments and a distinct head."""
    # Head
    head_rect = pygame.Rect(snake[0][0] * GRID_SIZE, snake[0][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, DARK_GREEN, head_rect, border_radius=5)
    # Body
    for segment in snake[1:]:
        seg_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, GREEN, seg_rect, border_radius=8) # More rounded body

def draw_food(surface, pos):
    """Draws the food as a rounded square."""
    food_rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, RED, food_rect, border_radius=5)

def show_score(surface, score, font):
    """Displays the current score."""
    score_text = font.render(f"Score: {score}", True, GOLD)
    score_rect = score_text.get_rect(topleft=(10, 10))
    surface.blit(score_text, score_rect)

def game_over_screen(surface, score, font_large, font_small):
    """Displays the game over message and instructions."""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Per-pixel alpha
    overlay.fill((0, 0, 0, 180)) # Black with ~70% opacity
    surface.blit(overlay, (0, 0))

    # Game Over Text
    game_over_text = font_large.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    surface.blit(game_over_text, game_over_rect)

    # Final Score
    final_score_text = font_small.render(f"Final Score: {score}", True, GOLD)
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
    surface.blit(final_score_text, final_score_rect)

    # Instructions
    instructions_text = font_small.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)
    instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    surface.blit(instructions_text, instructions_rect)

# --- Main Game Function ---
def main():
    pygame.init()

    # Screen and Clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Visually Appealing Snake")
    clock = pygame.time.Clock()

    # Fonts
    try:
        # Try using a common nice font, fallback to default if not found
        score_font = pygame.font.SysFont('consolas', 24)
        game_over_font_large = pygame.font.SysFont('impact', 60)
        game_over_font_small = pygame.font.SysFont('consolas', 30)
    except:
        print("Warning: Preferred fonts not found. Using default Pygame font.")
        score_font = pygame.font.Font(None, 30) # Default font
        game_over_font_large = pygame.font.Font(None, 75)
        game_over_font_small = pygame.font.Font(None, 40)


    # Initialize game state
    snake, direction, change_to, food_pos, score, speed, game_over = setup_game()

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over: # Only handle movement input if game is active
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and direction != DOWN:
                        change_to = UP
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and direction != UP:
                        change_to = DOWN
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and direction != RIGHT:
                        change_to = LEFT
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and direction != LEFT:
                        change_to = RIGHT
                else: # Handle restart/quit input on game over screen
                     if event.key == pygame.K_r:
                         # Reset game
                         snake, direction, change_to, food_pos, score, speed, game_over = setup_game()
                     elif event.key == pygame.K_q:
                         running = False

        if not game_over:
            # --- Game Logic ---
            # Validate direction change (prevent 180 degree turns)
            if change_to == UP and direction != DOWN: direction = UP
            if change_to == DOWN and direction != UP: direction = DOWN
            if change_to == LEFT and direction != RIGHT: direction = LEFT
            if change_to == RIGHT and direction != LEFT: direction = RIGHT

            # Move snake
            head_x, head_y = snake[0]
            new_head = ((head_x + direction[0]) % GRID_WIDTH, (head_y + direction[1]) % GRID_HEIGHT) # Wrap around screen edges

            # --- Collision Detection ---
            # Wall collision (handled by modulo/wrap-around now)
            # Self collision
            if new_head in snake:
                game_over = True
                # Small delay before showing game over screen for effect
                # pygame.time.wait(500) # Optional: pause slightly

            if not game_over:
                # Add new head
                snake.insert(0, new_head)

                # Check for food collision
                if new_head == food_pos:
                    score += 1
                    speed += SPEED_INCREMENT # Increase speed
                    food_pos = place_food(snake) # Place new food
                    # Don't pop the tail, snake grows
                else:
                    snake.pop() # Remove tail segment

        # --- Drawing ---
        screen.fill(DARK_GRAY)
        # draw_grid(screen) # Optional: uncomment to see grid lines
        draw_snake(screen, snake)
        draw_food(screen, food_pos)
        show_score(screen, score, score_font)

        if game_over:
            game_over_screen(screen, score, game_over_font_large, game_over_font_small)

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Rate Control ---
        clock.tick(speed) # Control game speed

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()