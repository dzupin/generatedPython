import pygame
import sys
import random

# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.


# --- Configuration & Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30  # Size of the snake segments
FPS = 15  # Game speed (higher is faster)

# --- Colors (R, G, B) ---
COLOR_BG = (20, 20, 20)  # Dark Grey Background
COLOR_GRID = (35, 35, 35)  # Faint Grid Lines
COLOR_SNAKE_HEAD = (0, 255, 127)  # Neon Green (Head)
COLOR_SNAKE_BODY = (0, 200, 100)  # Darker Green (Body)
COLOR_FOOD = (255, 105, 80)  # Hot Pink/Red (Food)
COLOR_TEXT = (240, 240, 240)  # Off-White Text

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Pygame")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)
big_font = pygame.font.SysFont("arial", 40, bold=True)


def draw_grid():
    """Draws vertical and horizontal lines to create a grid effect."""
    # Draw vertical lines
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    # Draw horizontal lines
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))


def draw_text(surface, font_obj, text, color, x, y, centered=False):
    """Helper to render text easily."""
    text_surface = font_obj.render(text, True, color)
    rect = text_surface.get_rect()
    if centered:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_surface, rect)


def main():
    # Game State Variables
    snake = [[5, 5], [4, 5], [3, 5]]  # List of [x, y] coordinates
    score = 0
    snake_dir = (1, 0)  # Current direction (x_change, y_change)
    game_over = False

    # Generate random food position
    # Ensure food aligns with the grid
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE
    food_pos = [random.randint(0, cols - 1), random.randint(0, rows - 1)]

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        main()  # Restart game by calling main recursively (simple reset)
                    elif event.key == pygame.K_q:
                        running = False
                else:
                    # Prevent reversing direction immediately (can't go down if going up)
                    if event.key == pygame.K_LEFT and snake_dir != (1, 0):
                        snake_dir = (-1, 0)
                    elif event.key == pygame.K_RIGHT and snake_dir != (-1, 0):
                        snake_dir = (1, 0)
                    elif event.key == pygame.K_UP and snake_dir != (0, 1):
                        snake_dir = (0, -1)
                    elif event.key == pygame.K_DOWN and snake_dir != (0, -1):
                        snake_dir = (0, 1)

        # 2. Game Logic (only if game is not over)
        if not game_over:
            # Calculate new head position
            head_x, head_y = snake[0]
            dx, dy = snake_dir
            new_head = [head_x + dx, head_y + dy]

            # Check Wall Collisions
            if (new_head[0] < 0 or new_head[0] >= cols or
                    new_head[1] < 0 or new_head[1] >= rows):
                game_over = True

            # Check Self Collision
            if new_head in snake:
                game_over = True

            # Move Snake
            snake.insert(0, new_head)  # Add new head

            # Check Food Collision
            if new_head == food_pos:
                score += 1
                # Spawn new food (ensure it doesn't spawn on snake)
                while True:
                    food_pos = [random.randint(0, cols - 1), random.randint(0, rows - 1)]
                    if food_pos not in snake:
                        break
            else:
                # If we didn't eat food, remove the tail to maintain size
                snake.pop()

        # 3. Drawing
        screen.fill(COLOR_BG)
        draw_grid()

        # Draw Food (Draw as a circle for visual variety)
        fx, fy = food_pos
        pygame.draw.circle(screen, COLOR_FOOD,
                           (fx * BLOCK_SIZE + BLOCK_SIZE // 2, fy * BLOCK_SIZE + BLOCK_SIZE // 2),
                           BLOCK_SIZE // 2 - 2)  # -2 for padding

        # Draw Snake
        for i, block in enumerate(snake):
            x, y = block
            # Determine color: Head is different color than body
            block_color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY

            # Draw rectangle for snake body
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, block_color, rect)

            # Optional: Add a small black outline to separate blocks visually
            pygame.draw.rect(screen, COLOR_BG, rect, 1)

        # Draw Score (Top Left)
        draw_text(screen, font, f"Score: {score}", COLOR_TEXT, 10, 10)

        # Draw Game Over Screen
        if game_over:
            # Darken background
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(overlay, (0, 0))

            draw_text(screen, big_font, "GAME OVER", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                      centered=True)
            draw_text(screen, font, f"Final Score: {score}", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                      centered=True)
            draw_text(screen, font, "Press 'R' to Restart", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
                      centered=True)

        # Update Display
        pygame.display.flip()

        # Control Speed
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
