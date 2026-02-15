# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1 --temp 1.0  --model  /AI/models/Step-3.5-Flash-MXFP4_MOE-00001-of-00007.gguf

import pygame
import random
import sys
import math
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 12

# Colors - Modern gradient palette
BACKGROUND = (10, 15, 25)
GRID_COLOR = (25, 35, 50)
GRID_HIGHLIGHT = (35, 50, 70)

# Snake colors with gradient
SNAKE_HEAD_COLOR = (0, 230, 150)
SNAKE_BODY_START = (0, 200, 100)
SNAKE_BODY_END = (0, 150, 50)
SNAKE_EYE_COLOR = (255, 255, 255)
SNAKE_PUPIL_COLOR = (0, 0, 0)

# Food colors
FOOD_COLOR = (255, 80, 80)
FOOD_GLOW = (255, 150, 150, 100)

# UI Colors
TEXT_COLOR = (220, 240, 255)
SCORE_BG = (20, 30, 45, 200)
GAME_OVER_BG = (10, 20, 35, 230)
BUTTON_COLOR = (0, 180, 120)
BUTTON_HOVER = (0, 220, 150)


class Particle:
    """Particle effect for when food is eaten"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.color = (
            random.randint(200, 255),
            random.randint(50, 150),
            random.randint(50, 100)
        )
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 40))
            color_with_alpha = (*self.color, alpha)
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), color_with_alpha)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = False
        self.eye_offset = 0

        # Initialize positions for starting snake
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0] - i, self.positions[0][1]))

    def get_head_position(self):
        return self.positions[0]

    def turn(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = head_x + dx
        new_y = head_y + dy

        # Check wall collision
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return False

        # Check self collision (excluding tail if moving)
        if (new_x, new_y) in self.positions[1:]:
            return False

        self.positions.insert(0, (new_x, new_y))

        if not self.grow_pending:
            self.positions.pop()
        else:
            self.grow_pending = False
            self.length += 1

        # Animate eyes
        self.eye_offset = (self.eye_offset + 1) % 20
        return True

    def grow(self):
        self.grow_pending = True

    def draw(self, surface):
        for i, (x, y) in enumerate(self.positions):
            # Calculate color based on position in snake
            ratio = i / max(1, len(self.positions) - 1)
            color = [
                SNAKE_BODY_START[j] + (SNAKE_BODY_END[j] - SNAKE_BODY_START[j]) * ratio
                for j in range(3)
            ]

            # Draw snake segment with rounded effect
            rect = pygame.Rect(
                x * GRID_SIZE + 2,
                y * GRID_SIZE + 2,
                GRID_SIZE - 4,
                GRID_SIZE - 4
            )
            pygame.draw.rect(surface, color, rect, border_radius=8)

            # Add highlight to segments
            highlight_rect = pygame.Rect(
                x * GRID_SIZE + 4,
                y * GRID_SIZE + 4,
                GRID_SIZE - 12,
                GRID_SIZE - 12
            )
            pygame.draw.rect(surface, (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40)),
                             highlight_rect, border_radius=4)

            # Draw eyes on head
            if i == 0:
                self.draw_eyes(surface, x, y)

    def draw_eyes(self, surface, x, y):
        # Calculate eye positions based on direction
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # Eye offset animation
        offset = math.sin(self.eye_offset * 0.5) * 1.5

        if self.direction == (1, 0):  # Right
            left_eye = (center_x + 4, center_y - 3 + offset)
            right_eye = (center_x + 4, center_y + 3 + offset)
        elif self.direction == (-1, 0):  # Left
            left_eye = (center_x - 4, center_y - 3 + offset)
            right_eye = (center_x - 4, center_y + 3 + offset)
        elif self.direction == (0, 1):  # Down
            left_eye = (center_x - 3 + offset, center_y + 4)
            right_eye = (center_x + 3 + offset, center_y + 4)
        else:  # Up
            left_eye = (center_x - 3 + offset, center_y - 4)
            right_eye = (center_x + 3 + offset, center_y - 4)

        # Draw eyes
        pygame.draw.circle(surface, SNAKE_EYE_COLOR, left_eye, 3)
        pygame.draw.circle(surface, SNAKE_EYE_COLOR, right_eye, 3)
        pygame.draw.circle(surface, SNAKE_PUPIL_COLOR, left_eye, 1)
        pygame.draw.circle(surface, SNAKE_PUPIL_COLOR, right_eye, 1)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.glow_phase = 0
        self.randomize_position()

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
        self.glow_phase = 0

    def draw(self, surface):
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # Pulsing glow effect
        glow_radius = GRID_SIZE // 2 + 2 + math.sin(self.glow_phase) * 2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, FOOD_GLOW, (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))

        # Draw food with 3D effect
        pygame.draw.circle(surface, FOOD_COLOR, (center_x, center_y), GRID_SIZE // 2 - 2)

        # Highlight
        pygame.draw.circle(surface, (255, 150, 150),
                           (center_x - 2, center_y - 2), GRID_SIZE // 4)

        self.glow_phase += 0.1


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)

        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.particles = []
        self.game_over = False
        self.game_started = False

        # Ensure food doesn't spawn on snake initially
        while self.food.position in self.snake.positions:
            self.food.randomize_position()

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            for y in range(0, HEIGHT, GRID_SIZE):
                # Create subtle grid pattern
                color = GRID_HIGHLIGHT if (x // GRID_SIZE + y // GRID_SIZE) % 2 == 0 else GRID_COLOR
                rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect, 1)

    def draw_score(self):
        # Score background with transparency
        score_bg = pygame.Surface((200, 50), pygame.SRCALPHA)
        score_bg.fill(SCORE_BG)
        self.screen.blit(score_bg, (10, 10))

        score_text = self.font_medium.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 15))

        length_text = self.font_small.render(f"Length: {self.snake.length}", True, TEXT_COLOR)
        self.screen.blit(length_text, (20, 45))

    def draw_start_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("SNAKE GAME", True, (0, 230, 150))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))

        subtitle = self.font_medium.render("Enhanced Edition", True, (100, 200, 255))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 3 + 60))

        # Draw animated snake preview
        preview_x = WIDTH // 2
        preview_y = HEIGHT // 2
        for i in range(5):
            color_ratio = i / 4
            color = [
                SNAKE_BODY_START[j] + (SNAKE_BODY_END[j] - SNAKE_BODY_START[j]) * color_ratio
                for j in range(3)
            ]
            rect = pygame.Rect(
                preview_x - 60 + i * 25,
                preview_y,
                20,
                20
            )
            pygame.draw.rect(self.screen, color, rect, border_radius=8)

        # Draw food
        pygame.draw.circle(self.screen, FOOD_COLOR, (preview_x + 70, preview_y + 10), 10)

        start_text = self.font_medium.render("Press SPACE to Start", True, BUTTON_COLOR)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 80))

        controls = [
            "CONTROLS:",
            "Arrow Keys - Move Snake",
            "SPACE - Pause/Start",
            "R - Restart (during game)",
            "ESC - Quit"
        ]

        for i, line in enumerate(controls):
            control_text = self.font_small.render(line, True, TEXT_COLOR)
            self.screen.blit(control_text, (WIDTH // 2 - control_text.get_width() // 2, HEIGHT // 2 + 150 + i * 30))

    def draw_game_over(self):
        # Game over overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))

        score_text = self.font_medium.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

        length_text = self.font_medium.render(f"Snake Length: {self.snake.length}", True, TEXT_COLOR)
        self.screen.blit(length_text, (WIDTH // 2 - length_text.get_width() // 2, HEIGHT // 2 + 50))

        # Draw restart button
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3, border_radius=10)

        restart_text = self.font_medium.render("PLAY AGAIN", True, (255, 255, 255))
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 135))

        quit_text = self.font_small.render("Press ESC to Quit", True, TEXT_COLOR)
        self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 200))

    def handle_collisions(self):
        # Check food collision
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.score += 10

            # Create particle effect
            for _ in range(15):
                self.particles.append(Particle(
                    self.food.position[0] * GRID_SIZE + GRID_SIZE // 2,
                    self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                ))

            self.food.randomize_position()

            # Ensure food doesn't spawn on snake
            while self.food.position in self.snake.positions:
                self.food.randomize_position()

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.restart_game()

                    elif self.game_started:
                        if event.key == pygame.K_SPACE:
                            self.game_started = False
                        elif event.key == pygame.K_r:
                            self.restart_game()

                        # Direction controls
                        elif event.key == pygame.K_UP:
                            self.snake.turn((0, -1))
                        elif event.key == pygame.K_DOWN:
                            self.snake.turn((0, 1))
                        elif event.key == pygame.K_LEFT:
                            self.snake.turn((-1, 0))
                        elif event.key == pygame.K_RIGHT:
                            self.snake.turn((1, 0))

                    else:  # Start screen
                        if event.key == pygame.K_SPACE:
                            self.game_started = True

                if self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)
                    if button_rect.collidepoint(mouse_pos):
                        self.restart_game()

            # Clear screen with background color
            self.screen.fill(BACKGROUND)

            # Draw grid
            self.draw_grid()

            if not self.game_started:
                self.draw_start_screen()
            else:
                # Move snake
                if not self.snake.move():
                    self.game_over = True

                self.handle_collisions()
                self.update_particles()

                # Draw game elements
                self.food.draw(self.screen)
                self.snake.draw(self.screen)

                # Draw particles
                for particle in self.particles:
                    particle.draw(self.screen)

                self.draw_score()

                if self.game_over:
                    self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

    def restart_game(self):
        self.snake.reset()
        self.food.randomize_position()
        self.score = 0
        self.particles = []
        self.game_over = False
        self.game_started = True

        # Ensure food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()


if __name__ == "__main__":
    game = Game()
    game.run()
