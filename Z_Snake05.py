import pygame
import random
import sys

# PROMPT for Gemini 2.5 Pro Experimental 03-25 : Write Snake game in python using pygame library. Make it visually appealing

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # Size of each snake segment and grid square
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Ensure screen dimensions are multiples of GRID_SIZE for perfect fit
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

# Colors (RGB)
BACKGROUND_COLOR = (30, 30, 40)     # Dark Slate Blue/Gray
SNAKE_HEAD_COLOR = (0, 200, 0)    # Bright Green
SNAKE_BODY_COLOR_1 = (0, 150, 0)   # Darker Green
SNAKE_BODY_COLOR_2 = (0, 170, 50)   # Slightly Lighter Dark Green
FOOD_COLOR = (255, 50, 50)       # Bright Red
SCORE_COLOR = (230, 230, 230)   # Light Gray/Off-white
GAMEOVER_COLOR = (255, 0, 0)     # Red for game over text
BORDER_COLOR = (60, 60, 70)      # Border for segments (optional, subtle)

SNAKE_SPEED = 10 # Controls game speed (frames per second)

# --- Screen Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Visually Appealing Snake Game")
clock = pygame.time.Clock()

# --- Fonts ---
try:
    # Try using a nicer built-in font if available
    score_font = pygame.font.SysFont("bahnschrift", 35)
    game_over_font_big = pygame.font.SysFont("consolas", 75)
    game_over_font_small = pygame.font.SysFont("consolas", 30)
except pygame.error:
    # Fallback to default font
    print("Warning: Using default font. Consider installing 'bahnschrift' or 'consolas'.")
    score_font = pygame.font.SysFont(None, 50)
    game_over_font_big = pygame.font.SysFont(None, 100)
    game_over_font_small = pygame.font.SysFont(None, 40)


# --- Helper Functions ---

def draw_segment(surface, color, position, border_radius=4):
    """Draws a single rounded segment."""
    rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    # Optional: Add a subtle border for definition
    # pygame.draw.rect(surface, BORDER_COLOR, rect, width=1, border_radius=border_radius)

def draw_snake(surface, snake_list):
    """Draws the entire snake with alternating body colors and a distinct head."""
    # Draw head
    if snake_list:
        draw_segment(surface, SNAKE_HEAD_COLOR, snake_list[-1], border_radius=6) # Slightly more rounded head

    # Draw body segments
    for i, segment in enumerate(snake_list[:-1]):
        color = SNAKE_BODY_COLOR_1 if i % 2 == 0 else SNAKE_BODY_COLOR_2
        draw_segment(surface, color, segment, border_radius=3)

def draw_food(surface, position):
    """Draws the food."""
    draw_segment(surface, FOOD_COLOR, position, border_radius=8) # Make food quite round

def place_food(snake_list):
    """Places food randomly on the grid, avoiding the snake."""
    while True:
        x = random.randrange(0, GRID_WIDTH) * GRID_SIZE
        y = random.randrange(0, GRID_HEIGHT) * GRID_SIZE
        food_pos = [x, y]
        # Ensure food doesn't spawn on the snake
        if food_pos not in snake_list:
            return food_pos

def display_score(surface, score):
    """Displays the current score."""
    score_text = f"Score: {score}"
    value = score_font.render(score_text, True, SCORE_COLOR)
    surface.blit(value, [10, 10]) # Position at top-left

def message(surface, msg, color, font, y_offset=0):
    """Displays a centered message."""
    mesg = font.render(msg, True, color)
    text_rect = mesg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_offset))
    surface.blit(mesg, text_rect)

# --- Game Loop ---
def game_loop():
    game_over = False
    game_close = False # Flag to indicate if the game over screen should be shown

    # Initial snake state
    lead_x = SCREEN_WIDTH / 2
    lead_y = SCREEN_HEIGHT / 2
    lead_x_change = 0
    lead_y_change = 0
    snake_list = [[lead_x, lead_y]]
    snake_length = 1

    # Initial food position
    food_pos = place_food(snake_list)

    score = 0

    # --- Main Game Cycle ---
    while not game_over:

        # --- Game Over Screen Loop ---
        while game_close:
            screen.fill(BACKGROUND_COLOR)
            message(screen, "Game Over!", GAMEOVER_COLOR, game_over_font_big, y_offset=-50)
            message(screen, f"Final Score: {score}", SCORE_COLOR, score_font, y_offset=20)
            message(screen, "C-Play Again / Q-Quit", SCORE_COLOR, game_over_font_small, y_offset=80)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False # Exit inner loop
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False # Exit inner loop
                    if event.key == pygame.K_c:
                        game_loop() # Restart the game by calling the loop again

        # --- Event Handling (Active Game) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Prevent reversing direction immediately
                if event.key == pygame.K_LEFT and lead_x_change == 0:
                    lead_x_change = -GRID_SIZE
                    lead_y_change = 0
                elif event.key == pygame.K_RIGHT and lead_x_change == 0:
                    lead_x_change = GRID_SIZE
                    lead_y_change = 0
                elif event.key == pygame.K_UP and lead_y_change == 0:
                    lead_y_change = -GRID_SIZE
                    lead_x_change = 0
                elif event.key == pygame.K_DOWN and lead_y_change == 0:
                    lead_y_change = GRID_SIZE
                    lead_x_change = 0
                elif event.key == pygame.K_q: # Allow quitting during game
                     game_over = True

        # --- Game Logic ---

        # Boundary collision check
        if lead_x >= SCREEN_WIDTH or lead_x < 0 or lead_y >= SCREEN_HEIGHT or lead_y < 0:
            game_close = True # Trigger game over screen

        # Update snake position
        lead_x += lead_x_change
        lead_y += lead_y_change

        # Create new head
        snake_head = [lead_x, lead_y]

        # Self-collision check (only if snake is long enough to collide)
        if snake_length > 1 and snake_head in snake_list[:-1]:
             game_close = True # Trigger game over screen

        # Add new head if game not over yet
        if not game_close:
            snake_list.append(snake_head)

            # Maintain snake length (remove tail)
            if len(snake_list) > snake_length:
                del snake_list[0]

            # Food collision check
            if lead_x == food_pos[0] and lead_y == food_pos[1]:
                food_pos = place_food(snake_list)
                snake_length += 1
                score += 1
                # Optional: Increase speed slightly on eating?
                # global SNAKE_SPEED
                # SNAKE_SPEED += 0.1

        # --- Drawing ---
        if not game_close: # Only draw the game elements if not in game_over state
            screen.fill(BACKGROUND_COLOR)
            draw_food(screen, food_pos)
            draw_snake(screen, snake_list)
            display_score(screen, score)

        # Update the display
        pygame.display.update()

        # --- Frame Rate Control ---
        clock.tick(SNAKE_SPEED)

    # --- Cleanup ---
    pygame.quit()
    sys.exit() # Ensures the script exits cleanly

# --- Start the Game ---
if __name__ == "__main__":
    game_loop()