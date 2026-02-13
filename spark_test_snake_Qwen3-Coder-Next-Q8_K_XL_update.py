# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 0-shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# 0-shot
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Qwen3-Coder-Next-UD-Q8_K_XL-00001-of-00003.gguf

import pygame
import time
import random
import os

# Initialize pygame
pygame.init()

# --- Configuration & Visuals ---
WIDTH = 600
HEIGHT = 600
BLOCK_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake: Addictive Edition")
clock = pygame.time.Clock()

# --- Visual Settings ---
# Colors
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
GREEN_MAIN = (0, 255, 128)
GREEN_DARK = (0, 200, 100)
RED_MAIN = (255, 50, 50)
YELLOW = (255, 255, 0)

# Load High Score
high_score = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0


# --- Classes for Addictive Elements ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = 1.0  # Opacity/Life
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= self.decay
        self.size *= 0.95

    def draw(self, surface):
        if self.life > 0:
            alpha_val = int(255 * self.life)
            # Create a temporary surface for transparency
            temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.color, alpha_val), (self.size, self.size), self.size)
            surface.blit(temp_surf, (self.x - self.size, self.y - self.size))


class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0
        self.dy = -1  # Floats up

    def update(self):
        self.y += self.dy
        self.life -= 0.02

    def draw(self, surface):
        if self.life > 0:
            font = pygame.font.SysFont('Arial', 20, bold=True)
            text_surface = font.render(self.text, True, (*self.color, int(255 * self.life)))
            surface.blit(text_surface, (self.x, self.y))


# --- Helper Functions ---

def draw_grid():
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, (30, 30, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, (30, 30, 50), (0, y), (WIDTH, y))


def draw_snake(snake_list):
    for index, block in enumerate(snake_list):
        x, y = block
        color = GREEN_MAIN if index == 0 else GREEN_DARK

        # Glow effect
        glow_rect = pygame.Rect(x - 3, y - 3, BLOCK_SIZE + 6, BLOCK_SIZE + 6)
        pygame.draw.rect(screen, (0, 255, 0, 60), glow_rect)

        # Main block
        pygame.draw.rect(screen, color, [x, y, BLOCK_SIZE, BLOCK_SIZE])

        # Eyes
        if index == 0:
            eye_size = 3
            pygame.draw.circle(screen, BLACK, (x + 5, y + 5), eye_size)
            pygame.draw.circle(screen, BLACK, (x + 15, y + 5), eye_size)


def draw_food(food_x, food_y, hue_shift):
    # Dynamic color for food based on background hue
    r = int(255 * abs(pygame.math.Vector2(1, 0).rotate(hue_shift).x))
    g = int(255 * abs(pygame.math.Vector2(1, 0).rotate(hue_shift + 120).x))
    b = 200

    center_x = food_x + BLOCK_SIZE // 2
    center_y = food_y + BLOCK_SIZE // 2

    # Outer Glow
    for i in range(1, 5):
        alpha = 255 - (i * 50)
        pygame.draw.circle(screen, (r, g, b, alpha), (center_x, center_y), (BLOCK_SIZE // 2) + i, 2)

    # Core
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), BLOCK_SIZE // 3)


def show_message(msg, color, y_offset=0, font=pygame.font.SysFont('Arial', 50, bold=True)):
    text_surface = font.render(msg, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + y_offset))
    screen.blit(text_surface, text_rect)


def show_score(score, high_score):
    score_font = pygame.font.SysFont('Arial', 25, bold=True)
    score_text = score_font.render(f"Score: {score}  |  Best: {high_score}", True, WHITE)
    screen.blit(score_text, (10, 10))


# --- Main Game Logic ---

def gameLoop():
    global high_score

    game_over = False
    game_close = False
    hue_shift = 0  # For background color cycling

    # Snake Init
    x1 = WIDTH / 2
    y1 = HEIGHT / 2
    x1_change = 0
    y1_change = 0
    snake_List = []
    Length_of_snake = 1
    speed = 15

    # Food Init
    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    # Effects Lists
    particles = []
    floating_texts = []
    shake_time = 0

    while not game_over:

        # --- Game Over Screen ---
        while game_close:
            # Save High Score
            if Length_of_snake - 1 > high_score:
                high_score = Length_of_snake - 1
                with open("highscore.txt", "w") as f:
                    f.write(str(high_score))

            screen.fill(BLACK)
            show_message("GAME OVER", RED_MAIN, -60)
            show_message(f"Score: {Length_of_snake - 1}", WHITE, -10)
            show_message("Press C-Play Again or Q-Quit", WHITE, 40, pygame.font.SysFont('Arial', 20))

            # Draw particles even in Game Over
            for p in particles:
                p.update()
                p.draw(screen)
            particles = [p for p in particles if p.life > 0]

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # --- Main Loop ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change, y1_change = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change, y1_change = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    x1_change, y1_change = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    x1_change, y1_change = 0, BLOCK_SIZE

        # Logic
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
            shake_time = 10  # Trigger shake on death

        x1 += x1_change
        y1 += y1_change

        # Background Cycle
        hue_shift += 0.5

        # Draw Background (Dynamic Color)
        base_color = (10 + hue_shift % 20, 10, 20 + (hue_shift % 30))
        screen.fill(base_color)
        draw_grid()

        # Draw Food
        draw_food(food_x, food_y, hue_shift)

        # Snake Movement
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Self Collision
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True
                shake_time = 15

        draw_snake(snake_List)
        show_score(Length_of_snake - 1, high_score)

        # Food Consumption
        if x1 == food_x and y1 == food_y:
            # Logic
            food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            Length_of_snake += 1
            speed = min(25, 15 + (Length_of_snake // 5))  # Cap speed at 25

            # Effects
            for _ in range(15):  # Create explosion
                particles.append(Particle(food_x + BLOCK_SIZE // 2, food_y + BLOCK_SIZE // 2, RED_MAIN))
            floating_texts.append(FloatingText(food_x, food_y, "+1", YELLOW))
            shake_time = 5

        # Update & Draw Particles
        for p in particles:
            p.update()
            p.draw(screen)
        particles = [p for p in particles if p.life > 0]

        # Update & Draw Floating Text
        for ft in floating_texts:
            ft.update()
            ft.draw(screen)
        floating_texts = [ft for ft in floating_texts if ft.life > 0]

        # Screen Shake Logic
        if shake_time > 0:
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            screen.blit(screen, (dx, dy))  # Shift the whole frame
            shake_time -= 1

        pygame.display.update()
        clock.tick(speed)

    pygame.quit()
    quit()


gameLoop()
