# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Qwen3-Coder-Next-UD-Q8_K_XL-00001-of-00003.gguf

import pygame
import time
import random

# Initialize pygame
pygame.init()

# --- Configuration & Visuals ---
# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN_MAIN = (0, 255, 128)  # Neon Green
GREEN_DARK = (0, 200, 100)
RED_MAIN = (255, 50, 50)  # Neon Red
BLUE_BG = (20, 20, 40)  # Dark Blue/Gray background
GRID_LINE = (30, 30, 60)

# Screen dimensions
WIDTH = 600
HEIGHT = 600
BLOCK_SIZE = 20  # Size of one grid square

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont('Arial', 40, bold=True)
font_small = pygame.font.SysFont('Arial', 20)


def draw_grid():
    """Draws a subtle background grid"""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_LINE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_LINE, (0, y), (WIDTH, y))


def draw_snake(snake_list):
    """Draws the snake with a glow effect"""
    for index, block in enumerate(snake_list):
        x, y = block
        # Head is brighter, body gets slightly darker
        color = GREEN_MAIN if index == 0 else GREEN_DARK

        # Create the glow effect using an outer shadow
        glow_rect = pygame.Rect(x - 2, y - 2, BLOCK_SIZE + 4, BLOCK_SIZE + 4)
        pygame.draw.rect(screen, (0, 255, 0, 50), glow_rect)  # Simple transparency hack

        # Draw the main block
        pygame.draw.rect(screen, color, [x, y, BLOCK_SIZE, BLOCK_SIZE])

        # Draw eyes on the head
        if index == 0:
            eye_size = 4
            # Simple logic to place eyes based on direction isn't needed for simple aesthetics
            # We will just place them in the center for a cute look
            pygame.draw.circle(screen, BLACK, (x + 5, y + 5), eye_size)
            pygame.draw.circle(screen, BLACK, (x + 15, y + 5), eye_size)


def draw_food(food_x, food_y):
    """Draws the food as a glowing circle"""
    # Pulsing effect calculation (optional visual flair)
    pulse = abs(pygame.time.get_ticks() % 500 - 250) / 250  # goes from 0 to 1 and back

    radius = BLOCK_SIZE // 2 - 2
    center_x = food_x + BLOCK_SIZE // 2
    center_y = food_y + BLOCK_SIZE // 2

    # Draw outer glow
    glow_color = (255, 100, 100)
    for i in range(1, 4):
        alpha = 255 - (i * 60)
        if alpha < 0: alpha = 0
        pygame.draw.circle(screen, glow_color, (center_x, center_y), radius + i, 1)

    # Draw main food
    pygame.draw.circle(screen, RED_MAIN, (center_x, center_y), radius)


def show_message(msg, color, y_offset=0, font=font_large):
    """Renders text to the center of the screen"""
    text_surface = font.render(msg, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + y_offset))
    screen.blit(text_surface, text_rect)


def show_score(score):
    """Displays current score in top left"""
    score_surface = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surface, (10, 10))


# --- Main Game Loop ---
def gameLoop():
    game_over = False
    game_close = False

    # Initial Snake Position
    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1
    speed = 15

    # Initial Food Position
    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    while not game_over:

        # Game Over Screen
        while game_close:
            screen.fill(BLACK)
            show_message("GAME OVER", RED_MAIN, -50)
            show_message(f"Final Score: {Length_of_snake - 1}", WHITE, 0)
            show_message("Press C-Play Again or Q-Quit", BLUE_BG, 60, font_small)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # Main Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        # Boundary Collision Check
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change

        # Draw Background
        screen.fill(BLACK)
        draw_grid()

        # Draw Food
        draw_food(food_x, food_y)

        # Snake Logic
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)

        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Self Collision Check
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        draw_snake(snake_List)
        show_score(Length_of_snake - 1)

        # Food Consumption Logic
        if x1 == food_x and y1 == food_y:
            food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            Length_of_snake += 1

            # Increase speed slightly every 5 points
            if Length_of_snake % 5 == 0:
                speed += 1

        pygame.display.update()
        clock.tick(speed)

    pygame.quit()
    quit()


# Start the game
gameLoop()
