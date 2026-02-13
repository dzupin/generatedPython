import pygame
import sys
import random

# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1  --model  /AI/models/stepfun-ai_Step-3.5-Flash-IQ4_XS-00001-of-00003.gguf

import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 60

# Colors
BACKGROUND = (10, 10, 20)
GRID_COLOR = (20, 30, 40, 30)  # RGBA with alpha
SNAKE_HEAD_COLOR = (0, 255, 150)
SNAKE_BODY_COLOR = (0, 200, 100)
FOOD_COLOR = (255, 50, 100)
TEXT_COLOR = (220, 220, 255)
UI_BG = (20, 25, 40, 200)


# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = random.randint(20, 40)
        self.max_life = self.life

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.size = max(0.5, self.size * 0.95)

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

    def is_alive(self):
        return self.life > 0


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.grow_pending = 2  # Start with length 3
        self.particles = []

    def get_head_position(self):
        return self.positions[0]

    def turn(self, direction):
        # Prevent turning 180 degrees
        if (direction == Direction.UP and self.direction != Direction.DOWN) or \
                (direction == Direction.DOWN and self.direction != Direction.UP) or \
                (direction == Direction.LEFT and self.direction != Direction.RIGHT) or \
                (direction == Direction.RIGHT and self.direction != Direction.LEFT):
            self.next_direction = direction

    def move(self):
        self.direction = self.next_direction
        head = self.get_head_position()
        x, y = self.direction.value
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)

        # Check for collision with self
        if new_position in self.positions[1:]:
            return False  # Game over

        self.positions.insert(0, new_position)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

        return True  # Continue playing

    def grow(self):
        self.grow_pending += 1
        self.score += 10
        self.length += 1

        # Add particles at food position
        for _ in range(15):
            self.particles.append(
                Particle(
                    self.positions[0][0] * GRID_SIZE + GRID_SIZE // 2,
                    self.positions[0][1] * GRID_SIZE + GRID_SIZE // 2,
                    FOOD_COLOR
                )
            )

    def update_particles(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        # Draw particles first (behind snake)
        for particle in self.particles:
            particle.draw(surface)

        # Draw snake with gradient effect
        for i, (x, y) in enumerate(self.positions):
            rect = pygame.Rect(
                x * GRID_SIZE + 1,
                y * GRID_SIZE + 1,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )

            # Gradient from head to tail
            if i == 0:  # Head
                color = SNAKE_HEAD_COLOR
                # Draw eyes
                eye_size = GRID_SIZE // 6
                if self.direction == Direction.RIGHT:
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + GRID_SIZE - eye_size * 2,
                                        y * GRID_SIZE + eye_size * 3), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + GRID_SIZE - eye_size * 2,
                                        y * GRID_SIZE + GRID_SIZE - eye_size * 3), eye_size)
                elif self.direction == Direction.LEFT:
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + eye_size * 2,
                                        y * GRID_SIZE + eye_size * 3), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + eye_size * 2,
                                        y * GRID_SIZE + GRID_SIZE - eye_size * 3), eye_size)
                elif self.direction == Direction.UP:
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + eye_size * 3,
                                        y * GRID_SIZE + eye_size * 2), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + GRID_SIZE - eye_size * 3,
                                        y * GRID_SIZE + eye_size * 2), eye_size)
                else:  # DOWN
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + eye_size * 3,
                                        y * GRID_SIZE + GRID_SIZE - eye_size * 2), eye_size)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (x * GRID_SIZE + GRID_SIZE - eye_size * 3,
                                        y * GRID_SIZE + GRID_SIZE - eye_size * 2), eye_size)
            else:  # Body
                # Gradient effect based on position in body
                factor = max(0.3, 1.0 - (i / len(self.positions) * 0.7))
                color = (
                    int(SNAKE_BODY_COLOR[0] * factor),
                    int(SNAKE_BODY_COLOR[1] * factor),
                    int(SNAKE_BODY_COLOR[2] * factor)
                )

            # Draw rounded rectangle for snake segment
            pygame.draw.rect(surface, color, rect, border_radius=4)

            # Add highlight to head
            if i == 0:
                highlight = pygame.Rect(
                    x * GRID_SIZE + 3,
                    y * GRID_SIZE + 3,
                    GRID_SIZE - 6,
                    GRID_SIZE // 3
                )
                pygame.draw.rect(surface, (150, 255, 200), highlight, border_radius=2)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        self.pulse = 0
        self.pulse_dir = 1

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )

    def update(self):
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1

    def draw(self, surface):
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # Pulsing effect
        base_size = GRID_SIZE // 2 - 2
        size = base_size + self.pulse * 2

        # Draw glow
        glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        for i in range(3):
            alpha = 50 - i * 15
            glow_size = size + i * 2
            pygame.draw.circle(
                glow_surface,
                (*FOOD_COLOR, alpha),
                (size * 2, size * 2),
                glow_size
            )
        surface.blit(glow_surface, (center_x - size * 2, center_y - size * 2))

        # Draw food with gradient
        pygame.draw.circle(surface, FOOD_COLOR, (center_x, center_y), size)
        highlight = pygame.Rect(
            center_x - size // 2,
            center_y - size // 2,
            size,
            size // 2
        )
        pygame.draw.ellipse(surface, (255, 150, 180), highlight)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Snake")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.game_speed = 8  # Moves per second
        self.last_move_time = 0
        self.grid_surface = self.create_grid_surface()

        # Ensure food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()

    def create_grid_surface(self):
        """Create a surface with grid lines"""
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)
        return surface

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_UP:
                        self.snake.turn(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.turn(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.turn(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.turn(Direction.RIGHT)
                    elif event.key == pygame.K_w:
                        self.snake.turn(Direction.UP)
                    elif event.key == pygame.K_s:
                        self.snake.turn(Direction.DOWN)
                    elif event.key == pygame.K_a:
                        self.snake.turn(Direction.LEFT)
                    elif event.key == pygame.K_d:
                        self.snake.turn(Direction.RIGHT)

        return True

    def reset_game(self):
        self.snake.reset()
        self.food.randomize_position()
        self.game_over = False
        self.game_speed = 8

        # Ensure food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()

    def update(self, current_time):
        if self.game_over:
            return

        # Move snake at controlled speed
        if current_time - self.last_move_time > 1000 / self.game_speed:
            if not self.snake.move():
                self.game_over = True
                return

            self.last_move_time = current_time

            # Check if snake ate food
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow()
                self.food.randomize_position()
                self.game_speed = min(15, 8 + self.snake.score // 50)  # Gradually increase speed

                # Ensure food doesn't spawn on snake
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()

        # Update particles and food animation
        self.snake.update_particles()
        self.food.update()

    def draw_ui(self):
        """Draw UI elements like score and game over screen"""
        # Score display
        score_text = self.font_medium.render(f"Score: {self.snake.score}", True, TEXT_COLOR)
        length_text = self.font_small.render(f"Length: {self.snake.length}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(length_text, (20, 60))

        # Game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Game over text
            game_over_text = self.font_large.render("GAME OVER", True, (255, 100, 100))
            score_text = self.font_medium.render(f"Final Score: {self.snake.score}", True, TEXT_COLOR)
            restart_text = self.font_small.render("Press R to Restart", True, (200, 255, 200))

            self.screen.blit(game_over_text,
                             (WIDTH // 2 - game_over_text.get_width() // 2,
                              HEIGHT // 2 - 60))
            self.screen.blit(score_text,
                             (WIDTH // 2 - score_text.get_width() // 2,
                              HEIGHT // 2 + 10))
            self.screen.blit(restart_text,
                             (WIDTH // 2 - restart_text.get_width() // 2,
                              HEIGHT // 2 + 70))

        # Controls hint
        if not self.game_over and self.snake.score == 0:
            controls = [
                "CONTROLS:",
                "Arrow Keys or WASD to move",
                "R to restart (when game over)"
            ]
            for i, line in enumerate(controls):
                text = self.font_small.render(line, True, (180, 200, 255))
                self.screen.blit(text, (WIDTH - text.get_width() - 20, 20 + i * 30))

    def draw(self):
        # Clear screen with background color
        self.screen.fill(BACKGROUND)

        # Draw grid
        self.screen.blit(self.grid_surface, (0, 0))

        # Draw game elements
        self.food.draw(self.screen)
        self.snake.draw(self.screen)

        # Draw UI
        self.draw_ui()

        # Update display
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()

            running = self.handle_events()
            self.update(current_time)
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

