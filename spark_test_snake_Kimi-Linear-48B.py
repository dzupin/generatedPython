import math

import pygame
import sys
import random

# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 1048576 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Kimi-Linear-48B-A3B-Instruct.Q8_0.gguf

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game dimensions
CELL_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (220, 20, 60)
BLUE = (65, 105, 225)
GRAY = (50, 50, 50)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT // 2
        self.dx = 0
        self.dy = 0
        self.body = [(self.x, self.y)]
        self.grow = 1

    def move(self):
        if self.dx == 0 and self.dy == 0:
            return

        new_x = self.x + self.dx
        new_y = self.y + self.dy

        # Check wall collision
        if (new_x < 0 or new_x >= GRID_WIDTH or
                new_y < 0 or new_y >= GRID_HEIGHT):
            self.reset()
            return

        # Check self collision
        if (new_x, new_y) in self.body:
            self.reset()
            return

        self.x = new_x
        self.y = new_y
        self.body.append((self.x, self.y))

        # Remove tail if not growing
        if self.grow == 0:
            self.body.pop(0)
        else:
            self.grow = 0


class Food:
    def __init__(self):
        self.randomize()

    def randomize(self):
        self.x = random.randint(0, GRID_WIDTH - 1)
        self.y = random.randint(0, GRID_HEIGHT - 1)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Snake Game")

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.reset()

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False

        # Special effects
        self.particles = []
        self.fruit_bounce = 0

    def run(self):
        clock = pygame.time.Clock()

        while True:
            self.handle_events()

            if not self.game_over and not self.paused:
                self.update()

            self.draw()
            clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                elif (not self.game_over and not self.paused):
                    if event.key == pygame.K_UP and self.snake.dy != 1:
                        self.snake.dx = 0
                        self.snake.dy = -1
                    elif event.key == pygame.K_DOWN and self.snake.dy != -1:
                        self.snake.dx = 0
                        self.snake.dy = 1
                    elif event.key == pygame.K_LEFT and self.snake.dx != 1:
                        self.snake.dx = -1
                        self.snake.dy = 0
                    elif event.key == pygame.K_RIGHT and self.snake.dx != -1:
                        self.snake.dx = 1
                        self.snake.dy = 0

            # Optional: Reset direction if no key is pressed
            elif event.type == pygame.KEYUP:
                # You can choose to stop the snake when a key is released
                # Or just keep going until collision. Here's how to stop it:
                if (event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
                    self.snake.dx = 0
                    self.snake.dy = 0

            # Game over restart
            if (event.type == pygame.KEYDOWN and
                    self.game_over and event.key == pygame.K_RETURN):
                self.reset()

    def update(self):
        self.snake.move()

        # Check food collision
        if (self.snake.x, self.snake.y) == (self.food.x, self.food.y):
            self.score += 10
            self.food.randomize()
            self.snake.grow = 1

            # Create particle effect
            for _ in range(5):
                angle = random.uniform(0, 2 * 3.14159)
                speed = random.uniform(2, 6)
                self.particles.append({
                    'x': self.food.x,
                    'y': self.food.y,
                    'dx': math.cos(angle) * speed,
                    'dy': math.sin(angle) * speed,
                    'life': 30
                })

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color = (
                min(255, GRAY[0] + (y // 4) * 10),
                min(255, GRAY[1] + (y // 4) * 10),
                min(255, GRAY[2] + (y // 4) * 10)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        if self.game_over or self.paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            text1 = self.font_large.render("GAME OVER" if self.game_over else "PAUSED",
                                           True, WHITE)
            text2 = self.font_medium.render("Press ENTER to restart" if self.game_over
                                            else "Press SPACE to continue",
                                            True, WHITE)

            rect1 = text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

            self.screen.blit(text1, rect1)
            self.screen.blit(text2, rect2)
        else:
            # Draw snake with gradient colors
            for i, (x, y) in enumerate(self.snake.body):
                hue = int((i * 10) % 360)
                color = pygame.Color(0)
                color.hsla = (hue, 70, 50 + min(i // 5, 30), 1)

                # Draw snake segments
                rect = pygame.Rect(x * CELL_SIZE + 2,
                                   y * CELL_SIZE + 2,
                                   CELL_SIZE - 4,
                                   CELL_SIZE - 4)

                # Create gradient effect for head
                if i == len(self.snake.body) - 1:
                    radius = min(CELL_SIZE // 2, 10)
                    pygame.draw.circle(self.screen, color,
                                       (x * CELL_SIZE + CELL_SIZE // 2,
                                        y * CELL_SIZE + CELL_SIZE // 2),
                                       radius)
                else:
                    pygame.draw.rect(self.screen, color, rect)

            # Draw food with pulsing effect
            center_x = self.food.x * CELL_SIZE + CELL_SIZE // 2
            center_y = self.food.y * CELL_SIZE + CELL_SIZE // 2

            if self.fruit_bounce > 0:
                radius = min(CELL_SIZE // 2, 10) + int(math.sin(self.fruit_bounce) * 3)
                color = RED
            else:
                radius = min(CELL_SIZE // 2, 10)
                color = RED

            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

            # Draw food highlight
            if self.fruit_bounce < 20:
                inner_radius = max(5, radius - 8)
                pygame.draw.circle(self.screen, WHITE,
                                   (center_x, center_y), inner_radius, 2)

            self.fruit_bounce += 0.3

        # Draw UI
        ui_color = BLACK if not self.paused else GRAY

        score_text = self.font_small.render(f"Score: {self.score}", True, ui_color)
        high_score_text = self.font_small.render(f"High Score: {max(self.high_score, self.score)}",
                                                 True, ui_color)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))

        # Draw pause indicator
        if self.paused:
            pause_text = self.font_small.render("PAUSED", True, ui_color)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
