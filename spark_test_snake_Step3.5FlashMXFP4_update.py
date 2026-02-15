# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1 --temp 1.0  --model  /AI/models/Step-3.5-Flash-MXFP4_MOE-00001-of-00007.gguf

import pygame
import random
import sys
import math
from pygame import gfxdraw
import json
import os
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
BASE_FPS = 12
MAX_FPS = 20

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
GOLDEN_FOOD_COLOR = (255, 215, 0)
GOLDEN_FOOD_GLOW = (255, 255, 100, 150)
SLOW_FOOD_COLOR = (100, 200, 255)
SLOW_FOOD_GLOW = (150, 220, 255, 150)

# UI Colors
TEXT_COLOR = (220, 240, 255)
SCORE_BG = (20, 30, 45, 200)
GAME_OVER_BG = (10, 20, 35, 230)
BUTTON_COLOR = (0, 180, 120)
BUTTON_HOVER = (0, 220, 150)
COMBO_COLOR = (255, 215, 0)
HIGH_SCORE_COLOR = (255, 100, 100)


class Particle:
    """Enhanced particle effect with multiple types"""

    def __init__(self, x, y, particle_type="normal"):
        self.x = x
        self.y = y
        self.type = particle_type
        self.size = random.uniform(2, 5)
        self.speed_x = random.uniform(-4, 4)
        self.speed_y = random.uniform(-4, 4)
        self.life = random.randint(20, 40)

        if particle_type == "golden":
            self.color = (255, random.randint(200, 255), random.randint(0, 100))
        elif particle_type == "slow":
            self.color = (random.randint(100, 200), random.randint(150, 255), 255)
        else:
            self.color = (
                random.randint(200, 255),
                random.randint(50, 150),
                random.randint(50, 100)
            )

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        self.speed_x *= 0.98  # Air resistance
        self.speed_y *= 0.98

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 40))
            color_with_alpha = (*self.color, alpha)
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), color_with_alpha)
            # Add glow for golden particles
            if self.type == "golden":
                glow_alpha = int(100 * (self.life / 40))
                glow_color = (255, 255, 200, glow_alpha)
                gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size * 1.5), glow_color)


class FloatingText:
    """Floating score/combo text effect"""

    def __init__(self, x, y, text, color, size=24):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.life = 60
        self.velocity = -1.5

    def update(self):
        self.y += self.velocity
        self.life -= 1

    def draw(self, surface, font):
        if self.life > 0:
            alpha = int(255 * (self.life / 60))
            text_surface = font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            surface.blit(text_surface, (self.x, self.y))


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
        self.trail = []  # For tail trail effect
        self.max_trail_length = 5

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

        # Add to trail
        if len(self.positions) > 1:
            self.trail.append(self.positions[-1])
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)

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
        # Draw trail first (behind snake)
        for i, (x, y) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            trail_color = (*SNAKE_BODY_START, alpha)
            rect = pygame.Rect(
                x * GRID_SIZE + 2,
                y * GRID_SIZE + 2,
                GRID_SIZE - 4,
                GRID_SIZE - 4
            )
            s = pygame.Surface((GRID_SIZE - 4, GRID_SIZE - 4), pygame.SRCALPHA)
            pygame.draw.rect(s, trail_color, s.get_rect(), border_radius=8)
            surface.blit(s, (rect.x, rect.y))

        # Draw snake body
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
            pygame.draw.rect(surface,
                             (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40)),
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
        self.type = "normal"  # normal, golden, slow
        self.randomize_position()

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
        self.glow_phase = 0
        # Randomly decide food type (10% golden, 15% slow, 75% normal)
        rand = random.random()
        if rand < 0.10:
            self.type = "golden"
        elif rand < 0.25:
            self.type = "slow"
        else:
            self.type = "normal"

    def get_points(self):
        if self.type == "golden":
            return 50
        elif self.type == "slow":
            return 5
        return 10

    def get_color(self):
        if self.type == "golden":
            return GOLDEN_FOOD_COLOR, GOLDEN_FOOD_GLOW
        elif self.type == "slow":
            return SLOW_FOOD_COLOR, SLOW_FOOD_GLOW
        return FOOD_COLOR, FOOD_GLOW

    def draw(self, surface):
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        color, glow_color = self.get_color()

        # Pulsing glow effect
        glow_radius = GRID_SIZE // 2 + 2 + math.sin(self.glow_phase) * 2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))

        # Draw food with 3D effect
        pygame.draw.circle(surface, color, (center_x, center_y), GRID_SIZE // 2 - 2)

        # Highlight
        highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        pygame.draw.circle(surface, highlight_color,
                           (center_x - 2, center_y - 2), GRID_SIZE // 4)

        # Special effects for different food types
        if self.type == "golden":
            # Draw sparkles
            for i in range(4):
                angle = self.glow_phase + i * math.pi / 2
                sparkle_x = center_x + math.cos(angle) * 8
                sparkle_y = center_y + math.sin(angle) * 8
                pygame.draw.circle(surface, (255, 255, 200), (int(sparkle_x), int(sparkle_y)), 2)
        elif self.type == "slow":
            # Draw slow motion circles
            for i in range(3):
                radius = 4 + i * 3
                alpha = 100 - i * 30
                slow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(slow_surface, (*SLOW_FOOD_COLOR, alpha), (radius, radius), radius, 1)
                surface.blit(slow_surface, (center_x - radius, center_y - radius))

        self.glow_phase += 0.1


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_tiny = pygame.font.SysFont('Arial', 18)

        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.particles = []
        self.floating_texts = []
        self.game_over = False
        self.game_started = False
        self.paused = False
        self.combo = 0
        self.last_food_time = 0
        self.fps = BASE_FPS
        self.slow_motion_timer = 0
        self.high_score = self.load_high_score()
        self.session_start_time = datetime.now()
        self.total_foods_eaten = 0
        self.max_length = 3
        self.achievements = {
            "first_food": False,
            "combo_5": False,
            "combo_10": False,
            "length_10": False,
            "length_20": False,
            "score_100": False,
            "score_500": False
        }

        # Ensure food doesn't spawn on snake initially
        while self.food.position in self.snake.positions:
            self.food.randomize_position()

    def load_high_score(self):
        try:
            with open("snake_highscore.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except:
            return 0

    def save_high_score(self):
        try:
            with open("snake_highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass

    def check_achievements(self):
        if not self.achievements["first_food"] and self.total_foods_eaten >= 1:
            self.achievements["first_food"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "FIRST FOOD!", (255, 255, 0), 36)

        if not self.achievements["combo_5"] and self.combo >= 5:
            self.achievements["combo_5"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "COMBO x5!", COMBO_COLOR, 36)

        if not self.achievements["combo_10"] and self.combo >= 10:
            self.achievements["combo_10"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "COMBO x10!", (255, 100, 255), 36)

        if not self.achievements["length_10"] and self.snake.length >= 10:
            self.achievements["length_10"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "LENGTH 10!", (100, 255, 255), 36)

        if not self.achievements["length_20"] and self.snake.length >= 20:
            self.achievements["length_20"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "LENGTH 20!", (255, 150, 150), 36)

        if not self.achievements["score_100"] and self.score >= 100:
            self.achievements["score_100"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "100 POINTS!", (255, 215, 0), 36)

        if not self.achievements["score_500"] and self.score >= 500:
            self.achievements["score_500"] = True
            self.add_floating_text(WIDTH // 2, HEIGHT // 2, "500 POINTS!", (255, 50, 50), 36)

    def add_floating_text(self, x, y, text, color, size=24):
        self.floating_texts.append(FloatingText(x, y, text, color, size))

    def add_particles(self, x, y, count=15, particle_type="normal"):
        for _ in range(count):
            self.particles.append(Particle(x, y, particle_type))

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            for y in range(0, HEIGHT, GRID_SIZE):
                # Create subtle grid pattern with slight animation
                wave = math.sin(pygame.time.get_ticks() * 0.001 + x / 50 + y / 50) * 5
                color_val = 30 + int(wave)
                color = (color_val, color_val + 10, color_val + 20)
                rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect, 1)

    def draw_score(self):
        # Score background with transparency
        score_bg = pygame.Surface((250, 100), pygame.SRCALPHA)
        score_bg.fill(SCORE_BG)
        self.screen.blit(score_bg, (10, 10))

        # Main score
        score_text = self.font_medium.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 15))

        # Length
        length_text = self.font_small.render(f"Length: {self.snake.length}", True, TEXT_COLOR)
        self.screen.blit(length_text, (20, 45))

        # Combo
        if self.combo > 1:
            combo_text = self.font_small.render(f"Combo x{self.combo}", True, COMBO_COLOR)
            self.screen.blit(combo_text, (20, 70))

        # FPS indicator (speed)
        fps_text = self.font_tiny.render(f"Speed: {self.fps}", True, (150, 200, 255))
        self.screen.blit(fps_text, (180, 15))

        # Food type indicator
        if self.food.type == "golden":
            food_type_text = self.font_tiny.render("GOLDEN FOOD!", True, (255, 215, 0))
            self.screen.blit(food_type_text, (180, 35))
        elif self.food.type == "slow":
            food_type_text = self.font_tiny.render("SLOW MOTION", True, SLOW_FOOD_COLOR)
            self.screen.blit(food_type_text, (180, 35))

    def draw_start_screen(self):
        # Semi-transparent overlay with pulse effect
        pulse = math.sin(pygame.time.get_ticks() * 0.002) * 20
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 180 + int(pulse)))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("SNAKE GAME", True, (0, 230, 150))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        subtitle = self.font_medium.render("Enhanced Edition", True, (100, 200, 255))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 4 + 60))

        # Draw animated snake preview with movement
        preview_x = WIDTH // 2
        preview_y = HEIGHT // 4 + 90
        time_offset = pygame.time.get_ticks() * 0.003

        for i in range(7):
            x_offset = math.sin(time_offset + i * 0.5) * 10
            color_ratio = i / 6
            color = [
                SNAKE_BODY_START[j] + (SNAKE_BODY_END[j] - SNAKE_BODY_START[j]) * color_ratio
                for j in range(3)
            ]
            rect = pygame.Rect(
                preview_x - 80 + i * 25 + x_offset,
                preview_y,
                20,
                20
            )
            pygame.draw.rect(self.screen, color, rect, border_radius=8)

            # Draw eyes on head
            if i == 0:
                eye_offset = math.sin(time_offset * 2) * 2
                pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                   (preview_x - 80 + 4 + x_offset, preview_y + 6 + eye_offset), 3)
                pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                   (preview_x - 80 + 4 + x_offset, preview_y + 14 + eye_offset), 3)
                pygame.draw.circle(self.screen, SNAKE_PUPIL_COLOR,
                                   (preview_x - 80 + 4 + x_offset, preview_y + 6 + eye_offset), 1)
                pygame.draw.circle(self.screen, SNAKE_PUPIL_COLOR,
                                   (preview_x - 80 + 4 + x_offset, preview_y + 14 + eye_offset), 1)

        # Draw food with animation
        food_pulse = math.sin(pygame.time.get_ticks() * 0.005) * 3
        pygame.draw.circle(self.screen, FOOD_COLOR,
                           (preview_x + 70, preview_y + 10 + food_pulse), 10 + food_pulse / 2)

        start_text = self.font_medium.render("Press SPACE to Start", True, BUTTON_COLOR)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 4 + 150))

        # High score
        high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, HIGH_SCORE_COLOR)
        self.screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 4 + 190))

        # Controls - moved up and made more compact
        controls = [
            "CONTROLS:",
            "Arrow Keys - Move Snake",
            "SPACE - Pause/Resume",
            "R - Restart",
            "ESC - Quit",
            "",
            "FEATURES:",
            "• Golden Food: 50 pts (10% chance)",
            "• Slow Food: 5 pts, slows game (15% chance)",
            "• Combo System: Eat quickly for multipliers!",
            "• Achievements: Unlock milestones",
            "• Progressive difficulty: Speed increases with score"
        ]

        # Start controls at a position that ensures all content fits
        controls_y = HEIGHT // 4 + 220
        max_line_width = 0

        # First calculate the maximum line width to center all text
        for line in controls:
            control_text = self.font_tiny.render(line, True, TEXT_COLOR)
            max_line_width = max(max_line_width, control_text.get_width())

        # Draw controls with consistent centering
        for i, line in enumerate(controls):
            control_text = self.font_tiny.render(line, True, TEXT_COLOR)
            x_pos = WIDTH // 2 - max_line_width // 2
            y_pos = controls_y + i * 22

            # Ensure text doesn't go below the screen
            if y_pos + 22 > HEIGHT - 10:
                break

            self.screen.blit(control_text, (x_pos, y_pos))

    def draw_game_over(self):
        # Game over overlay with shake effect
        shake_x = random.randint(-2, 2) if self.game_over else 0
        shake_y = random.randint(-2, 2) if self.game_over else 0

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG)
        self.screen.blit(overlay, (shake_x, shake_y))

        game_over_text = self.font_large.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(game_over_text,
                         (WIDTH // 2 - game_over_text.get_width() // 2 + shake_x, HEIGHT // 4 + shake_y))

        score_text = self.font_medium.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2 + shake_x, HEIGHT // 3 + shake_y))

        length_text = self.font_medium.render(f"Snake Length: {self.snake.length}", True, TEXT_COLOR)
        self.screen.blit(length_text, (WIDTH // 2 - length_text.get_width() // 2 + shake_x, HEIGHT // 3 + 40 + shake_y))

        # High score
        high_score_color = HIGH_SCORE_COLOR if self.score >= self.high_score else TEXT_COLOR
        high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, high_score_color)
        self.screen.blit(high_score_text,
                         (WIDTH // 2 - high_score_text.get_width() // 2 + shake_x, HEIGHT // 3 + 80 + shake_y))

        # Check and update high score
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            new_record_text = self.font_medium.render("NEW HIGH SCORE!", True, (255, 215, 0))
            self.screen.blit(new_record_text,
                             (WIDTH // 2 - new_record_text.get_width() // 2 + shake_x, HEIGHT // 3 + 120 + shake_y))

        # Stats - moved closer to the top
        stats_y = HEIGHT // 3 + 160
        stats = [
            f"Total Foods Eaten: {self.total_foods_eaten}",
            f"Max Combo: {max(self.combo, 1)}",
            f"Session Time: {int((datetime.now() - self.session_start_time).total_seconds())}s"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.font_small.render(stat, True, (150, 200, 255))
            self.screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2 + shake_x, stats_y + i * 25))

        # Draw restart button - positioned after all stats
        button_y = stats_y + len(stats) * 25 + 30
        button_rect = pygame.Rect(WIDTH // 2 - 100, button_y, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3, border_radius=10)

        restart_text = self.font_medium.render("PLAY AGAIN", True, (255, 255, 255))
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, button_y + 15))

        quit_text = self.font_small.render("Press ESC to Quit", True, TEXT_COLOR)
        self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, button_y + 70))


    def handle_collisions(self):
        current_time = pygame.time.get_ticks()

        # Check food collision
        if self.snake.get_head_position() == self.food.position:
            points = self.food.get_points()

            # Apply combo multiplier
            if current_time - self.last_food_time < 2000:  # Within 2 seconds
                self.combo += 1
                combo_multiplier = min(self.combo, 5)  # Cap at 5x
                points *= combo_multiplier
            else:
                self.combo = 1

            self.score += points
            self.total_foods_eaten += 1

            # Create particle effect based on food type
            particle_count = 20 if self.food.type == "golden" else 15
            particle_type = self.food.type if self.food.type in ["golden", "slow"] else "normal"
            self.add_particles(
                self.food.position[0] * GRID_SIZE + GRID_SIZE // 2,
                self.food.position[1] * GRID_SIZE + GRID_SIZE // 2,
                particle_count,
                particle_type
            )

            # Add floating score text
            self.add_floating_text(
                self.food.position[0] * GRID_SIZE + GRID_SIZE // 2,
                self.food.position[1] * GRID_SIZE,
                f"+{points}",
                COMBO_COLOR if self.combo > 1 else TEXT_COLOR,
                20
            )

            # Special effects for golden food
            if self.food.type == "golden":
                self.add_floating_text(WIDTH // 2, HEIGHT // 2, "GOLDEN FOOD x5!", (255, 215, 0), 30)

            self.snake.grow()
            self.last_food_time = current_time

            # Update max length
            if self.snake.length > self.max_length:
                self.max_length = self.snake.length

            # Check achievements
            self.check_achievements()

            # Speed up game based on score (progressive difficulty)
            self.fps = min(MAX_FPS, BASE_FPS + (self.score // 100))

            # Slow motion effect for slow food
            if self.food.type == "slow":
                self.slow_motion_timer = 60  # 1 second at 60 FPS equivalent

            self.food.randomize_position()

            # Ensure food doesn't spawn on snake
            while self.food.position in self.snake.positions:
                self.food.randomize_position()

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def update_floating_texts(self):
        for ft in self.floating_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.floating_texts.remove(ft)

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
                            self.paused = not self.paused
                        elif event.key == pygame.K_r:
                            self.restart_game()
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

                # Handle mouse clicks on the game over screen
                if self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Recalculate button rect position (same as in draw_game_over)
                    button_y = HEIGHT // 3 + 160 + len([
                        f"Total Foods Eaten: {self.total_foods_eaten}",
                        f"Max Combo: {max(self.combo, 1)}",
                        f"Session Time: {int((datetime.now() - self.session_start_time).total_seconds())}s"
                    ]) * 25 + 30
                    button_rect = pygame.Rect(WIDTH // 2 - 100, button_y, 200, 50)
                    if button_rect.collidepoint(mouse_pos):
                        self.restart_game()

            # Clear screen with background color
            self.screen.fill(BACKGROUND)

            # Draw grid
            self.draw_grid()

            if not self.game_started:
                self.draw_start_screen()
            else:
                if not self.paused and not self.game_over:
                    # Move snake (with slow motion effect)
                    if self.slow_motion_timer > 0:
                        # Only move snake every 3 frames during slow motion
                        if pygame.time.get_ticks() % 3 == 0:
                            if not self.snake.move():
                                self.game_over = True
                        self.slow_motion_timer -= 1
                    else:
                        if not self.snake.move():
                            self.game_over = True

                    self.handle_collisions()

                # Always update particles and floating texts (even when paused)
                self.update_particles()
                self.update_floating_texts()

                # Draw game elements
                self.food.draw(self.screen)
                self.snake.draw(self.screen)

                # Draw particles
                for particle in self.particles:
                    particle.draw(self.screen)

                # Draw floating texts
                for ft in self.floating_texts:
                    ft.draw(self.screen, self.font_small)

                self.draw_score()

                if self.game_over:
                    self.draw_game_over()
                elif self.paused:
                    # Pause overlay
                    pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pause_overlay.fill((0, 0, 0, 150))
                    self.screen.blit(pause_overlay, (0, 0))
                    pause_text = self.font_large.render("PAUSED", True, (255, 255, 255))
                    self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
                    resume_text = self.font_medium.render("Press SPACE to resume", True, TEXT_COLOR)
                    self.screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))

            pygame.display.flip()
            # Adjust FPS based on slow motion
            current_fps = self.fps // 2 if self.slow_motion_timer > 0 else self.fps
            self.clock.tick(current_fps)

    def restart_game(self):
        self.snake.reset()
        self.food.randomize_position()
        self.score = 0
        self.particles = []
        self.floating_texts = []
        self.game_over = False
        self.game_started = True
        self.paused = False
        self.combo = 0
        self.last_food_time = 0
        self.fps = BASE_FPS
        self.slow_motion_timer = 0
        self.total_foods_eaten = 0
        self.max_length = 3
        self.session_start_time = datetime.now()
        self.achievements = {
            "first_food": False,
            "combo_5": False,
            "combo_10": False,
            "length_10": False,
            "length_20": False,
            "score_100": False,
            "score_500": False
        }

        # Ensure food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()


if __name__ == "__main__":
    game = Game()
    game.run()

