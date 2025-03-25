import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)
BACKGROUND = (20, 20, 20)
PANEL_COLOR = (40, 40, 40)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Initialize game variables
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = (1, 0)
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
score = 0
game_over = False

# Game statistics
start_time = time.time()
game_duration = 0
max_snake_length = 1
food_eaten = 0
moves_made = 0
avg_speed = 0

# Initialize fonts
font = pygame.font.SysFont('Arial', 25)
stats_font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 30, bold=True)


def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))


def draw_snake():
    # Draw snake head
    head = snake[0]
    head_rect = pygame.Rect(head[0] * GRID_SIZE, head[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, GREEN, head_rect)

    # Draw snake eyes
    eye_radius = GRID_SIZE // 8
    eye_offset = GRID_SIZE // 4

    # Left eye
    left_eye_pos = (head[0] * GRID_SIZE + eye_offset, head[1] * GRID_SIZE + eye_offset)
    pygame.draw.circle(screen, BLACK, left_eye_pos, eye_radius)

    # Right eye
    right_eye_pos = (head[0] * GRID_SIZE + GRID_SIZE - eye_offset, head[1] * GRID_SIZE + eye_offset)
    pygame.draw.circle(screen, BLACK, right_eye_pos, eye_radius)

    # Draw snake body with gradient color
    for i, segment in enumerate(snake[1:], 1):
        # Create a gradient from green to dark green
        color_factor = 1 - (i / len(snake))
        segment_color = (
            int(GREEN[0] * color_factor + DARK_GREEN[0] * (1 - color_factor)),
            int(GREEN[1] * color_factor + DARK_GREEN[1] * (1 - color_factor)),
            int(GREEN[2] * color_factor + DARK_GREEN[2] * (1 - color_factor))
        )

        segment_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, segment_color, segment_rect)

        # Add a small inner rectangle for texture
        inner_margin = GRID_SIZE // 5
        inner_rect = pygame.Rect(
            segment[0] * GRID_SIZE + inner_margin,
            segment[1] * GRID_SIZE + inner_margin,
            GRID_SIZE - 2 * inner_margin,
            GRID_SIZE - 2 * inner_margin
        )
        pygame.draw.rect(screen, (
            min(segment_color[0] + 30, 255),
            min(segment_color[1] + 30, 255),
            min(segment_color[2] + 30, 255)
        ), inner_rect)


def draw_food():
    food_rect = pygame.Rect(food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, RED, food_rect)

    # Add a shiny effect
    shine_radius = GRID_SIZE // 4
    shine_pos = (food[0] * GRID_SIZE + shine_radius, food[1] * GRID_SIZE + shine_radius)
    pygame.draw.circle(screen, WHITE, shine_pos, shine_radius // 2)


def draw_score():
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display time
    current_time = time.time() - start_time if not game_over else game_duration
    minutes = int(current_time // 60)
    seconds = int(current_time % 60)
    time_text = font.render(f'Time: {minutes:02d}:{seconds:02d}', True, WHITE)
    screen.blit(time_text, (WIDTH - time_text.get_width() - 10, 10))


def draw_game_over():
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

    # Create a panel for statistics
    panel_width, panel_height = 400, 350
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2

    # Draw panel background
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

    # Game over title
    title_text = title_font.render('GAME OVER', True, RED)
    title_rect = title_text.get_rect(center=(WIDTH // 2, panel_y + 30))
    screen.blit(title_text, title_rect)

    # Statistics
    stats = [
        f"Score: {score}",
        f"Time Played: {int(game_duration // 60):02d}:{int(game_duration % 60):02d}",
        f"Snake Length: {len(snake)}",
        f"Food Eaten: {food_eaten}",
        f"Moves Made: {moves_made}",
        f"Avg. Speed: {avg_speed:.2f} moves/sec",
        f"Max Possible Score: {GRID_WIDTH * GRID_HEIGHT - 1}"
    ]

    # Display statistics
    for i, stat in enumerate(stats):
        stat_text = stats_font.render(stat, True, WHITE)
        screen.blit(stat_text, (panel_x + 30, panel_y + 70 + i * 30))

    # Restart instruction
    restart_text = font.render('Press R to Restart', True, GREEN)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, panel_y + panel_height - 30))
    screen.blit(restart_text, restart_rect)


def update_game():
    global snake, food, score, game_over, snake_direction, food_eaten, moves_made, max_snake_length, game_duration, avg_speed

    # Get user input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and snake_direction != (0, 1):
        snake_direction = (0, -1)
    elif keys[pygame.K_DOWN] and snake_direction != (0, -1):
        snake_direction = (0, 1)
    elif keys[pygame.K_LEFT] and snake_direction != (1, 0):
        snake_direction = (-1, 0)
    elif keys[pygame.K_RIGHT] and snake_direction != (-1, 0):
        snake_direction = (1, 0)

    # Move the snake
    head_x, head_y = snake[0]
    new_head = (head_x + snake_direction[0], head_y + snake_direction[1])
    moves_made += 1

    # Check for collisions with walls
    if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
        game_over = True
        game_duration = time.time() - start_time
        avg_speed = moves_made / game_duration if game_duration > 0 else 0
        return

    # Check for collisions with self
    if new_head in snake[1:]:
        game_over = True
        game_duration = time.time() - start_time
        avg_speed = moves_made / game_duration if game_duration > 0 else 0
        return

    # Add new head
    snake.insert(0, new_head)

    # Update max snake length
    max_snake_length = max(max_snake_length, len(snake))

    # Check if snake ate food
    if new_head == food:
        # Generate new food
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in snake:
                break
        score += 1
        food_eaten += 1
    else:
        # Remove tail if no food was eaten
        snake.pop()


def reset_game():
    global snake, snake_direction, food, score, game_over, start_time, game_duration
    global max_snake_length, food_eaten, moves_made, avg_speed

    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (1, 0)
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    score = 0
    game_over = False

    # Reset statistics
    start_time = time.time()
    game_duration = 0
    max_snake_length = 1
    food_eaten = 0
    moves_made = 0
    avg_speed = 0


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    # Fill the screen
    screen.fill(BACKGROUND)

    # Draw grid
    draw_grid()

    if not game_over:
        # Update game state
        update_game()

    # Draw game elements
    draw_snake()
    draw_food()
    draw_score()

    if game_over:
        draw_game_over()

    # Update display
    pygame.display.flip()
    clock.tick(FPS)
