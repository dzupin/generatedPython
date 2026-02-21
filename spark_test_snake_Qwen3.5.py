# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 0-shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-397B-A17B-UD-TQ1_0.gguf  --mmproj /AI/models/Qwen3.5-397B-A17B-mmproj-BF16.gguf

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (10, 10, 15)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
DARK_GREEN = (0, 200, 80)
RED = (255, 100, 100)
GOLD = (255, 215, 0)
GRAY = (40, 40, 50)
LIGHT_GRAY = (80, 80, 90)

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('🐍 Snake Game')
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)


def draw_gradient_background():
    """Draw a gradient background"""
    for y in range(WINDOW_HEIGHT):
        gradient = max(10, 30 - y * 0.05)
        color = (gradient, gradient, gradient + 10)
        pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))


def draw_grid():
    """Draw subtle grid lines"""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)


def draw_snake(snake):
    """Draw the snake with gradient effect"""
    for i, segment in enumerate(snake):
        x = segment[0] * GRID_SIZE
        y = segment[1] * GRID_SIZE

        # Head is brighter, tail is darker
        if i == 0:
            color = GREEN
            # Draw eyes
            eye_offset = GRID_SIZE // 4
            pygame.draw.circle(screen, BLACK, (x + eye_offset, y + eye_offset), 4)
            pygame.draw.circle(screen, BLACK, (x + GRID_SIZE - eye_offset, y + eye_offset), 4)
        else:
            # Gradient from green to dark green
            gradient_factor = i / len(snake)
            r = int(0 + gradient_factor * 50)
            g = int(255 - gradient_factor * 100)
            b = int(100 - gradient_factor * 50)
            color = (r, g, b)

        # Draw rounded rectangle segment
        rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(screen, color, rect, border_radius=5)

        # Highlight border
        pygame.draw.rect(screen, DARK_GREEN, rect, 2, border_radius=5)


def draw_food(position):
    """Draw the food with glow effect"""
    x = position[0] * GRID_SIZE
    y = position[1] * GRID_SIZE

    # Main food circle
    pygame.draw.circle(screen, RED, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), GRID_SIZE // 2 - 2)

    # Glow effect
    for i in range(3, 0, -1):
        pygame.draw.circle(screen, (255, 150, 150), (x + GRID_SIZE // 2, y + GRID_SIZE // 2),
                           GRID_SIZE // 2 - 2 + i, 1)


def draw_score(score):
    """Draw the score display"""
    score_text = font_medium.render(f"Score: {score}", True, GOLD)
    screen.blit(score_text, (20, 20))


def draw_game_over(score, high_score):
    """Draw game over screen"""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    game_over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 200))

    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 280))

    high_score_text = font_medium.render(f"High Score: {high_score}", True, GOLD)
    screen.blit(high_score_text, (WINDOW_WIDTH // 2 - high_score_text.get_width() // 2, 340))

    restart_text = font_small.render("Press SPACE to Restart or ESC to Quit", True, LIGHT_GRAY)
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 420))


def draw_start_screen():
    """Draw start screen"""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title_text = font_large.render("SNAKE", True, GREEN)
    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 150))

    instruction_text = font_medium.render("Press SPACE to Start", True, WHITE)
    screen.blit(instruction_text, (WINDOW_WIDTH // 2 - instruction_text.get_width() // 2, 250))

    controls_text = font_small.render("Use Arrow Keys to Move", True, LIGHT_GRAY)
    screen.blit(controls_text, (WINDOW_WIDTH // 2 - controls_text.get_width() // 2, 320))


def get_random_position(snake):
    """Get a random position for food that doesn't overlap with snake"""
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in snake:
            return (x, y)


def main():
    # Game variables
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = (1, 0)  # Moving right
    next_direction = (1, 0)
    food = get_random_position(snake)
    score = 0
    high_score = 0
    game_speed = 8
    game_state = "START"  # START, PLAYING, GAME_OVER

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == "START":
                    if event.key == pygame.K_SPACE:
                        game_state = "PLAYING"

                elif game_state == "PLAYING":
                    # Prevent 180-degree turns
                    if event.key == pygame.K_UP and direction[1] != 1:
                        next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction[1] != -1:
                        next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction[0] != 1:
                        next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction[0] != -1:
                        next_direction = (1, 0)

                elif game_state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        # Reset game
                        snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                        direction = (1, 0)
                        next_direction = (1, 0)
                        food = get_random_position(snake)
                        score = 0
                        game_speed = 8
                        game_state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        # Drawing
        draw_gradient_background()
        draw_grid()

        if game_state == "START":
            draw_start_screen()

        elif game_state == "PLAYING":
            # Update direction
            direction = next_direction

            # Move snake
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            # Check collisions
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                    new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                    new_head in snake):
                game_state = "GAME_OVER"
                high_score = max(score, high_score)
            else:
                snake.insert(0, new_head)

                # Check if food eaten
                if new_head == food:
                    score += 10
                    food = get_random_position(snake)
                    # Increase speed slightly
                    if game_speed < 15:
                        game_speed += 0.5
                else:
                    snake.pop()

            # Draw game elements
            draw_snake(snake)
            draw_food(food)
            draw_score(score)

        elif game_state == "GAME_OVER":
            draw_snake(snake)
            draw_food(food)
            draw_score(score)
            draw_game_over(score, high_score)

        pygame.display.flip()
        clock.tick(game_speed)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
