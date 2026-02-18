# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

# functional  context 256K perfect summary  partial censor Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf    (https://huggingface.co/unsloth/Qwen3-Next-80B-A3B-Instruct-GGUF)  (text only)
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf

import pygame
import random
import math

# --- Initialization ---
pygame.init()
pygame.font.init()
pygame.display.set_caption("Neon Snake")

# Screen Dimensions
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors (Neon Palette)
BACKGROUND_COLOR = (20, 20, 40)  # Deep dark blue/purple
SNAKE_COLOR = (0, 255, 128)  # Neon Green
SNAKE_HEAD_COLOR = (0, 200, 100)
FOOD_COLOR = (255, 50, 100)  # Neon Pink
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (15, 15, 30)
GAME_OVER_COLOR = (50, 20, 20)  # Dark Red tint for Game Over screen

# Game Settings
TILE_SIZE = 25
TILE_COUNT = WIDTH // TILE_SIZE
GAME_SPEED = 10


class Particle:
    """Creates an explosion effect when food is eaten"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.speed_x = random.uniform(-4, 4)
        self.speed_y = random.uniform(-4, 4)
        self.life = 1.0  # Opacity/Life (1.0 to 0.0)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 0.03
        self.size = max(0, self.size - 0.15)

    def draw(self, surface):
        alpha = int(255 * self.life)
        if alpha > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        # Start in the middle
        self.x = (WIDTH // 2 // TILE_SIZE) * TILE_SIZE
        self.y = (HEIGHT // 2 // TILE_SIZE) * TILE_SIZE
        self.dx = TILE_SIZE
        self.dy = 0
        self.body = []
        self.length = 3
        self.score = 0
        self.dead = False

        # Initialize body segments
        for i in range(self.length):
            self.body.append((self.x - i * TILE_SIZE, self.y))

    def update(self):
        if self.dead:
            return

        # Move Head
        self.x += self.dx
        self.y += self.dy

        # Wall Collision (Hard walls)
        if self.x < 0 or self.x >= WIDTH or self.y < 0 or self.y >= HEIGHT:
            self.dead = True

        # Self Collision (Check head against body, excluding the head itself which is at index 0)
        for segment in self.body[1:]:
            if self.x == segment[0] and self.y == segment[1]:
                self.dead = True

        # Add new head
        self.body.insert(0, (self.x, self.y))

        # Remove tail if not growing
        if len(self.body) > self.length:
            self.body.pop()

    def grow(self):
        self.length += 1
        self.score += 10

    def draw(self, surface):
        # Draw Body
        for i, (bx, by) in enumerate(self.body):
            # Determine Color
            if i == 0:
                color = SNAKE_HEAD_COLOR  # Bright Head
                glow_intensity = 60
            else:
                # Gradient color for tail (Green to Darker Green)
                multiplier = 1 - (i / (len(self.body) + 5))
                color = (0, int(200 * multiplier), int(128 * multiplier))
                glow_intensity = 20

            # Draw Glow behind body segments
            if i % 2 == 0:  # Optimization: only draw glow on even segments
                glow_surf = pygame.Surface((TILE_SIZE + 10, TILE_SIZE + 10), pygame.SRCALPHA)
                alpha_val = int(glow_intensity * (1 - i / len(self.body)))
                pygame.draw.circle(glow_surf, (*color, alpha_val),
                                   (TILE_SIZE // 2 + 5, TILE_SIZE // 2 + 5), TILE_SIZE // 2 + 5)
                surface.blit(glow_surf, (bx - 5, by - 5), special_flags=pygame.BLEND_ADD)

            # Draw Rect
            rect = pygame.Rect(bx + 1, by + 1, TILE_SIZE - 2, TILE_SIZE - 2)
            # Add border for segment definition
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, (20, 20, 40), rect, width=1, border_radius=6)

            # Draw Eyes on Head
            if i == 0:
                eye_color = (20, 20, 20)
                eye_size = 4

                # Offset logic based on direction
                offset_x = TILE_SIZE // 3
                offset_y = TILE_SIZE // 3

                # Left Eye
                ex1, ey1 = bx + offset_x, by + offset_y
                if self.dx > 0:
                    ex1 += 5
                elif self.dx < 0:
                    ex1 -= 5
                elif self.dy > 0:
                    ey1 += 5
                elif self.dy < 0:
                    ey1 -= 5
                pygame.draw.circle(surface, eye_color, (ex1, ey1), eye_size)

                # Right Eye
                ex2, ey2 = bx + offset_x, by + offset_y
                if self.dx > 0:
                    ey2 += 5
                elif self.dx < 0:
                    ey2 -= 5
                elif self.dy > 0:
                    ex2 += 5
                elif self.dx < 0:
                    ex2 -= 5
                pygame.draw.circle(surface, eye_color, (ex2, ey2), eye_size)


class Food:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.pulse = 0

    def place(self, snake_body):
        valid_position = False
        while not valid_position:
            self.x = random.randint(0, TILE_COUNT - 1) * TILE_SIZE
            self.y = random.randint(0, TILE_COUNT - 1) * TILE_SIZE
            if (self.x, self.y) not in snake_body:
                valid_position = True

    def draw(self, surface):
        # Pulsing effect
        self.pulse += 0.15
        radius = (TILE_SIZE // 2) - 3
        pulse_offset = math.sin(self.pulse) * 3

        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2

        # Draw Glow
        glow_radius = radius + 8 + pulse_offset
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*FOOD_COLOR, 60), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius), special_flags=pygame.BLEND_ADD)

        # Draw Food Circle
        pygame.draw.circle(surface, FOOD_COLOR, (center_x, center_y), radius)

        # Inner highlight
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 2, center_y - 2), radius // 3)


def draw_background(surface):
    surface.fill(BACKGROUND_COLOR)

    # Draw Grid
    for x in range(0, WIDTH, TILE_SIZE):
        pygame.draw.line(surface, (25, 25, 45), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, (25, 25, 45), (0, y), (WIDTH, y))


def draw_text(surface, text, size, x, y, color=TEXT_COLOR, center=True, bold=False, font_name="Arial"):
    font = pygame.font.SysFont(font_name, size, bold=bold)
    render = font.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    surface.blit(render, rect)


def draw_button(surface, text, x, y, width, height, active, action=None):
    color = (80, 80, 120) if not active else (100, 100, 160)
    border_color = SNAKE_COLOR if active else (50, 50, 80)

    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=10)
    pygame.draw.rect(surface, border_color, (x, y, width, height), width=3, border_radius=10)

    draw_text(surface, text, 24, x + width // 2, y + height // 2, center=True)


def main():
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food()
    particles = []
    food.place(snake.body)

    # Game States
    state = "MENU"  # MENU, PLAYING, PAUSED, GAMEOVER
    frame_count = 0

    while True:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Common Controls across most states
            if event.type == pygame.KEYDOWN:
                if state == "PLAYING":
                    # Prevent reversing directly
                    if event.key == pygame.K_UP and snake.dy == 0:
                        snake.dx, snake.dy = 0, -TILE_SIZE
                    elif event.key == pygame.K_DOWN and snake.dy == 0:
                        snake.dx, snake.dy = 0, TILE_SIZE
                    elif event.key == pygame.K_LEFT and snake.dx == 0:
                        snake.dx, snake.dy = -TILE_SIZE, 0
                    elif event.key == pygame.K_RIGHT and snake.dx == 0:
                        snake.dx, snake.dy = TILE_SIZE, 0
                    elif event.key == pygame.K_SPACE:
                        state = "PAUSED"

                elif state == "PAUSED":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        state = "PLAYING"

                elif state == "GAMEOVER":
                    # Any key restarts the game
                    state = "MENU"

                elif state == "MENU":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        state = "PLAYING"
                        snake.reset()
                        particles = []
                        food.place(snake.body)

            # Mouse Click Support
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "PLAYING":
                    state = "PAUSED"
                elif state == "PAUSED":
                    state = "PLAYING"
                elif state == "GAMEOVER":
                    state = "MENU"

        # --- Game Logic Update ---
        if state == "PLAYING":
            frame_count += 1
            # Control game speed
            if frame_count % GAME_SPEED == 0:
                snake.update()

                # Check Food Collision
                if snake.x == food.x and snake.y == food.y:
                    snake.grow()
                    food.place(snake.body)
                    # Create particles
                    for _ in range(12):
                        particles.append(Particle(food.x + TILE_SIZE // 2, food.y + TILE_SIZE // 2, FOOD_COLOR))

                # Update Particles
                particles = [p for p in particles if p.life > 0]
                for p in particles:
                    p.update()

            # Check for Death Condition (Self or Wall)
            if snake.dead:
                # Create a death explosion
                for _ in range(20):
                    particles.append(Particle(snake.x + TILE_SIZE // 2, snake.y + TILE_SIZE // 2, (255, 80, 80)))
                state = "GAMEOVER"

        # --- Drawing ---
        draw_background(WIN)

        if state == "MENU":
            # Draw Decorative Elements
            draw_text(WIN, "NEON SNAKE", 60, WIDTH // 2, HEIGHT // 3, SNAKE_COLOR, bold=True)
            draw_text(WIN, "Press Space or Click to Start", 24, WIDTH // 2, HEIGHT // 2 + 20, TEXT_COLOR)

            # Draw a sample snake in the menu
            sample_y = HEIGHT - 100
            for i in range(5):
                size = 20 - i * 2
                color_val = 200 - i * 40
                pygame.draw.circle(WIN, (0, color_val, 100), (150 + i * 40, sample_y), size)
                pygame.draw.circle(WIN, (0, color_val, 100), (WIDTH - 150 - i * 40, sample_y), size)

        elif state == "PLAYING" or state == "PAUSED":

            # Draw Food
            food.draw(WIN)

            # Draw Snake
            snake.draw(WIN)

            # Draw Particles
            for p in particles:
                p.draw(WIN)

            # Draw HUD
            draw_text(WIN, f"SCORE: {snake.score}", 24, WIDTH - 90, 30, TEXT_COLOR, center=False)

            if state == "PAUSED":
                # Dim background slightly
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BACKGROUND_COLOR)
                WIN.blit(overlay, (0, 0))

                draw_text(WIN, "PAUSED", 60, WIDTH // 2, HEIGHT // 2, (255, 200, 50), bold=True)

        elif state == "GAMEOVER":
            # Draw semi-transparent Game Over overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(GAME_OVER_COLOR)
            WIN.blit(overlay, (0, 0))

            draw_text(WIN, "GAME OVER", 70, WIDTH // 2, HEIGHT // 3, (255, 80, 80), bold=True)
            draw_text(WIN, f"Final Score: {snake.score}", 35, WIDTH // 2, HEIGHT // 2, TEXT_COLOR)

            # Draw a pulsing "Press Key" indicator
            pulse = int(math.sin(pygame.time.get_ticks() / 200) * 20)
            draw_text(WIN, "Press Any Key to Restart", 20, WIDTH // 2, HEIGHT // 2 + 80, (200, 200, 200))

            # Draw a "Death Mark" at the head location
            pygame.draw.line(WIN, (255, 0, 0),
                             (snake.x - 10, snake.y - 10), (snake.x + 10, snake.y + 10), 4)
            pygame.draw.line(WIN, (255, 0, 0),
                             (snake.x + 10, snake.y - 10), (snake.x - 10, snake.y + 10), 4)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
