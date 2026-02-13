# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Devstral-Small-2-24B-Instruct-2512-Q8_0.gguf  --mmproj /AI/models/Devstral-Small-2-24B-Instruct-2512-mmproj-BF16.gguf

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
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
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 100, 0)
BACKGROUND = (50, 50, 50)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0
        self.color = GREEN
        self.head_color = YELLOW
        self.speed = FPS

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        if new_head in self.positions[1:]:
            return False  # Game over

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

        return True  # Game continues

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0

    def render(self, surface):
        for i, p in enumerate(self.positions):
            # Draw head differently
            if i == 0:
                rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, self.head_color, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)  # Border
            else:
                # Gradient effect for body
                color_intensity = 150 + (i * 5) % 100
                body_color = (0, color_intensity, 0)
                rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, body_color, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)  # Border

class Food:
    def __init__(self):
        self.types = ["regular", "special", "power"]  # Define types first
        self.current_type = "regular"
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        self.current_type = random.choice(self.types)

        # Special food appears less frequently
        if self.current_type == "special":
            if random.random() > 0.3:  # 70% chance to change back to regular
                self.current_type = "regular"
        elif self.current_type == "power":
            if random.random() > 0.5:  # 50% chance to change back to regular
                self.current_type = "regular"

    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))

        if self.current_type == "regular":
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.circle(surface, WHITE, (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                               self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)
        elif self.current_type == "special":
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, PURPLE, rect, 3)  # Border
            pygame.draw.circle(surface, YELLOW, (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                               self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 4)
        elif self.current_type == "power":
            pygame.draw.rect(surface, ORANGE, rect)
            pygame.draw.rect(surface, RED, rect, 2)  # Border
            pygame.draw.rect(surface, WHITE, (self.position[0] * GRID_SIZE + 5, self.position[1] * GRID_SIZE + 5,
                                            GRID_SIZE - 10, GRID_SIZE - 10))

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)

def show_game_over(surface, score):
    font = pygame.font.SysFont('arial', 50)
    text = font.render(f"Game Over! Score: {score}", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))

    font_small = pygame.font.SysFont('arial', 30)
    restart_text = font_small.render("Press R to restart or Q to quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))

    surface.blit(text, text_rect)
    surface.blit(restart_text, restart_rect)

def show_score(surface, score):
    font = pygame.font.SysFont('arial', 20)
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 10))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake.reset()
                        food.randomize_position()
                        game_over = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT

        if not game_over:
            # Update game state
            if not snake.update():
                game_over = True

            # Check if snake eats food
            if snake.get_head_position() == food.position:
                # Different effects for different food types
                if food.current_type == "regular":
                    snake.length += 1
                    snake.score += 10
                elif food.current_type == "special":
                    snake.length += 2
                    snake.score += 30
                elif food.current_type == "power":
                    snake.speed = min(snake.speed + 2, 20)  # Increase speed
                    snake.score += 20

                food.randomize_position()
                # Make sure food doesn't spawn on snake
                while food.position in snake.positions:
                    food.randomize_position()

        # Drawing
        screen.fill(BACKGROUND)
        draw_grid(screen)

        snake.render(screen)
        food.render(screen)
        show_score(screen, snake.score)

        if game_over:
            show_game_over(screen, snake.score)

        pygame.display.update()
        clock.tick(snake.speed)

if __name__ == "__main__":
    main()
