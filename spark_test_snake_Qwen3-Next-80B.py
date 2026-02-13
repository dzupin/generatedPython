# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

# functional  context 256K perfect summary  partial censor Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf    (https://huggingface.co/unsloth/Qwen3-Next-80B-A3B-Instruct-GGUF)  (text only)
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf


import pygame
import random
import time

# Initialize pygame
pygame.init()

# Colors (modern, pleasing palette)
BACKGROUND_COLOR = (15, 20, 35)  # Deep navy blue
SNAKE_COLOR = (70, 200, 150)  # Soft neon green
FOOD_COLOR = (255, 100, 100)  # Soft pink
TEXT_COLOR = (220, 220, 255)  # Light white-blue
BORDER_COLOR = (40, 60, 100)  # Darker border
GRID_COLOR = (30, 40, 70)  # Subtle grid

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Beautiful Snake Game")
clock = pygame.time.Clock()

# Font settings
font_large = pygame.font.SysFont('Arial', 48, bold=True)
font_medium = pygame.font.SysFont('Arial', 32)
font_small = pygame.font.SysFont('Arial', 24)


def draw_gradient_background():
    """Draw a vertical gradient background"""
    for y in range(WINDOW_HEIGHT):
        # Gradient from dark blue to slightly lighter blue
        intensity = int(15 + (y / WINDOW_HEIGHT) * 30)
        color = (intensity, intensity + 5, intensity + 20)
        pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))


def draw_grid():
    """Draw subtle grid lines"""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)


def draw_snake(snake_body):
    """Draw the snake with a gradient effect and rounded corners"""
    for i, segment in enumerate(snake_body):
        # Head gets a different color
        if i == 0:
            color = (100, 220, 180)  # Brighter head
        else:
            # Gradient effect along the snake body
            alpha = 1.0 - (i / len(snake_body)) * 0.5
            r = int(SNAKE_COLOR[0] * alpha)
            g = int(SNAKE_COLOR[1] * alpha)
            b = int(SNAKE_COLOR[2] * alpha)
            color = (r, g, b)

        # Draw rounded rectangle for each segment
        rect = pygame.Rect(
            segment[0] * GRID_SIZE + 2,
            segment[1] * GRID_SIZE + 2,
            GRID_SIZE - 4,
            GRID_SIZE - 4
        )
        pygame.draw.rect(screen, color, rect, border_radius=8)

        # Add subtle eye effect to the head
        if i == 0:
            # Position eyes based on direction
            eye_size = 3
            # Left eye
            pygame.draw.circle(screen, (10, 10, 10),
                               (segment[0] * GRID_SIZE + 7, segment[1] * GRID_SIZE + 7), eye_size)
            # Right eye
            pygame.draw.circle(screen, (10, 10, 10),
                               (segment[0] * GRID_SIZE + 13, segment[1] * GRID_SIZE + 7), eye_size)


def draw_food(food_position):
    """Draw an appealing food item with a glow effect"""
    # Draw glow effect
    for i in range(3):
        alpha = 0.3 - (i * 0.1)
        size = GRID_SIZE + i * 4
        glow_rect = pygame.Rect(
            food_position[0] * GRID_SIZE + (GRID_SIZE - size) // 2,
            food_position[1] * GRID_SIZE + (GRID_SIZE - size) // 2,
            size, size
        )
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface,
                           (FOOD_COLOR[0], FOOD_COLOR[1], FOOD_COLOR[2], int(255 * alpha)),
                           (size // 2, size // 2), size // 2)
        screen.blit(glow_surface, glow_rect.topleft)

    # Draw the food
    pygame.draw.circle(screen, FOOD_COLOR,
                       (food_position[0] * GRID_SIZE + GRID_SIZE // 2,
                        food_position[1] * GRID_SIZE + GRID_SIZE // 2),
                       GRID_SIZE // 2 - 2)

    # Add a highlight
    pygame.draw.circle(screen, (255, 200, 200),
                       (food_position[0] * GRID_SIZE + GRID_SIZE // 3,
                        food_position[1] * GRID_SIZE + GRID_SIZE // 3),
                       3)


def show_score(score):
    """Display the current score"""
    score_text = font_medium.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))


def show_game_over(score):
    """Display game over screen with animated effect"""
    # Dark overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Game Over text
    game_over_text = font_large.render("Game Over", True, (255, 80, 80))
    text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
    screen.blit(game_over_text, text_rect)

    # Score text
    score_text = font_medium.render(f"Final Score: {score}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(score_text, score_rect)

    # Restart instruction
    restart_text = font_small.render("Press SPACE to Restart or ESC to Quit", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
    screen.blit(restart_text, restart_rect)

    # Add some floating particles
    for _ in range(15):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(2, 5)
        color = (random.randint(200, 255), random.randint(100, 150), random.randint(100, 150))
        pygame.draw.circle(screen, color, (x, y), size)


def game_loop():
    """Main game loop"""
    # Initial snake position
    snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (1, 0)  # Start moving right
    snake_length = 1

    # Initial food position
    food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    # Game state
    game_over = False
    paused = False
    score = 0

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_direction != (0, 1):
                    snake_direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake_direction != (0, -1):
                    snake_direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake_direction != (1, 0):
                    snake_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                    snake_direction = (1, 0)
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_SPACE and game_over:
                    # Restart game
                    snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                    snake_direction = (1, 0)
                    snake_length = 1
                    food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                    game_over = False
                    paused = False
                    score = 0
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        if game_over:
            screen.fill(BACKGROUND_COLOR)
            draw_gradient_background()
            draw_grid()
            show_score(score)
            show_game_over(score)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if paused:
            screen.fill(BACKGROUND_COLOR)
            draw_gradient_background()
            draw_grid()
            draw_snake(snake_body)
            draw_food(food_position)
            show_score(score)

            # Pause overlay
            pause_text = font_large.render("PAUSED", True, TEXT_COLOR)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_text, text_rect)

            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Move snake
        head_x, head_y = snake_body[0]
        dx, dy = snake_direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Check for self-collision
        if new_head in snake_body:
            game_over = True
            continue

        # Add new head
        snake_body.insert(0, new_head)

        # Check if food eaten
        if new_head == food_position:
            snake_length += 1
            score += 10

            # Generate new food (avoiding snake body)
            while True:
                food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                if food_position not in snake_body:
                    break
        else:
            # Remove tail if no food eaten
            if len(snake_body) > snake_length:
                snake_body.pop()

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        draw_gradient_background()
        draw_grid()
        draw_snake(snake_body)
        draw_food(food_position)
        show_score(score)

        pygame.display.flip()
        clock.tick(FPS)


# Start the game
if __name__ == "__main__":
    game_loop()
