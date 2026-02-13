# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# 1 Shot ( accidentally removed the Direction enum definition. )
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1  --model  /AI/models/stepfun-ai_Step-3.5-Flash-IQ4_XS-00001-of-00003.gguf

import pygame
import random
import math
from enum import Enum
import json
import os
from datetime import datetime

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
GRID_COLOR = (20, 30, 40, 30)
SNAKE_HEAD_COLOR = (0, 255, 150)
SNAKE_BODY_COLOR = (0, 200, 100)
FOOD_COLOR = (255, 50, 100)
SPECIAL_FOOD_COLOR = (255, 215, 0)  # Gold
TEXT_COLOR = (220, 220, 255)
UI_BG = (20, 25, 40, 200)
DANGER_ZONE_COLOR = (255, 50, 50, 30)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class FoodType(Enum):
    NORMAL = 1
    SPECIAL = 2
    SPEED_BOOST = 3
    SCORE_MULTIPLIER = 4


class Particle:
    def __init__(self, x, y, color, size=None, speed=None, angle=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = size if size else random.uniform(2, 5)
        self.speed = speed if speed else random.uniform(0.5, 2.0)
        self.angle = angle if angle else random.uniform(0, 2 * math.pi)
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
        self.grow_pending = 2
        self.particles = []
        self.speed_boost_timer = 0
        self.score_multiplier_timer = 0
        self.shield_timer = 0
        self.combo_count = 0
        self.last_food_time = 0

    def get_head_position(self):
        return self.positions[0]

    def turn(self, direction):
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

        # Check for collision with self (unless shielded)
        if new_position in self.positions[1:] and self.shield_timer <= 0:
            return False

        self.positions.insert(0, new_position)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

        # Update timers
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
        if self.score_multiplier_timer > 0:
            self.score_multiplier_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1

        return True

    def grow(self, food_type=FoodType.NORMAL):
        self.grow_pending += 1
        self.length += 1

        # Calculate score with multipliers
        base_score = 10
        if food_type == FoodType.SPECIAL:
            base_score = 50
        elif food_type == FoodType.SPEED_BOOST:
            base_score = 15
        elif food_type == FoodType.SCORE_MULTIPLIER:
            base_score = 20

        multiplier = 1
        if self.score_multiplier_timer > 0:
            multiplier = 2

        self.score += base_score * multiplier

        # Combo system: eat within 2 seconds for bonus
        current_time = pygame.time.get_ticks()
        if current_time - self.last_food_time < 2000:
            self.combo_count += 1
            combo_bonus = 5 * self.combo_count
            self.score += combo_bonus
        else:
            self.combo_count = 0

        self.last_food_time = current_time

        # Create particles based on food type
        particle_count = 15
        particle_color = FOOD_COLOR

        if food_type == FoodType.SPECIAL:
            particle_count = 30
            particle_color = SPECIAL_FOOD_COLOR
        elif food_type == FoodType.SPEED_BOOST:
            particle_count = 20
            particle_color = (100, 200, 255)
        elif food_type == FoodType.SCORE_MULTIPLIER:
            particle_count = 25
            particle_color = (255, 100, 255)

        for _ in range(particle_count):
            self.particles.append(
                Particle(
                    self.positions[0][0] * GRID_SIZE + GRID_SIZE // 2,
                    self.positions[0][1] * GRID_SIZE + GRID_SIZE // 2,
                    particle_color
                )
            )

    def update_particles(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        # Draw particles first
        for particle in self.particles:
            particle.draw(surface)

        # Draw snake with effects
        for i, (x, y) in enumerate(self.positions):
            rect = pygame.Rect(
                x * GRID_SIZE + 1,
                y * GRID_SIZE + 1,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )

            # Determine color based on position and effects
            if i == 0:  # Head
                if self.shield_timer > 0:
                    color = (100, 200, 255)  # Blue when shielded
                else:
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
                # Gradient effect
                factor = max(0.3, 1.0 - (i / len(self.positions) * 0.7))
                color = (
                    int(SNAKE_BODY_COLOR[0] * factor),
                    int(SNAKE_BODY_COLOR[1] * factor),
                    int(SNAKE_BODY_COLOR[2] * factor)
                )

            # Draw segment
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

            # Draw shield effect
            if i == 0 and self.shield_timer > 0:
                shield_rect = pygame.Rect(
                    x * GRID_SIZE - 2,
                    y * GRID_SIZE - 2,
                    GRID_SIZE + 4,
                    GRID_SIZE + 4
                )
                pygame.draw.rect(surface, (100, 200, 255, 100), shield_rect, 3, border_radius=6)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = FoodType.NORMAL
        self.spawn_time = 0
        self.lifetime = 8000  # Special food disappears after 8 seconds
        self.pulse = 0
        self.pulse_dir = 1
        self.randomize_position()

    def randomize_position(self, food_type=FoodType.NORMAL):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
        self.type = food_type
        self.spawn_time = pygame.time.get_ticks()
        self.pulse = 0

    def update(self):
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1

        # Check if special food should disappear
        if self.type != FoodType.NORMAL:
            current_time = pygame.time.get_ticks()
            if current_time - self.spawn_time > self.lifetime:
                return False  # Food should be removed
        return True

    def get_color(self):
        if self.type == FoodType.SPECIAL:
            return SPECIAL_FOOD_COLOR
        elif self.type == FoodType.SPEED_BOOST:
            return (100, 200, 255)
        elif self.type == FoodType.SCORE_MULTIPLIER:
            return (255, 100, 255)
        return FOOD_COLOR

    def draw(self, surface):
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # Pulsing effect
        base_size = GRID_SIZE // 2 - 2
        size = base_size + self.pulse * 2

        # Draw glow based on food type
        color = self.get_color()
        glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)

        # Different glow patterns for different food types
        if self.type == FoodType.SPECIAL:
            # Star-shaped glow for special food
            for i in range(5):
                angle = (pygame.time.get_ticks() / 500 + i * 72) * math.pi / 180
                glow_x = size * 2 + math.cos(angle) * size * 1.5
                glow_y = size * 2 + math.sin(angle) * size * 1.5
                pygame.draw.circle(
                    glow_surface,
                    (*color, 80),
                    (glow_x, glow_y),
                    size * 0.8
                )
        else:
            # Circular glow for other foods
            for i in range(3):
                alpha = 50 - i * 15
                glow_size = size + i * 2
                pygame.draw.circle(
                    glow_surface,
                    (*color, alpha),
                    (size * 2, size * 2),
                    glow_size
                )

        surface.blit(glow_surface, (center_x - size * 2, center_y - size * 2))

        # Draw food
        pygame.draw.circle(surface, color, (center_x, center_y), size)

        # Add special effects
        if self.type == FoodType.SPECIAL:
            # Draw star pattern
            points = []
            for i in range(5):
                angle = (i * 72 + 90) * math.pi / 180
                radius = size if i % 2 == 0 else size * 0.5
                px = center_x + math.cos(angle) * radius
                py = center_y + math.sin(angle) * radius
                points.append((px, py))
            pygame.draw.polygon(surface, (255, 255, 200), points)
        elif self.type == FoodType.SPEED_BOOST:
            # Draw lightning bolt
            bolt_points = [
                (center_x - size // 2, center_y - size),
                (center_x + size // 4, center_y - size // 2),
                (center_x - size // 4, center_y - size // 2),
                (center_x + size // 2, center_y + size),
                (center_x - size // 4, center_y + size // 2),
                (center_x + size // 4, center_y + size // 2),
            ]
            pygame.draw.polygon(surface, (200, 255, 255), bolt_points)
        elif self.type == FoodType.SCORE_MULTIPLIER:
            # Draw X pattern
            pygame.draw.line(surface, (255, 200, 255),
                             (center_x - size // 2, center_y - size // 2),
                             (center_x + size // 2, center_y + size // 2), 3)
            pygame.draw.line(surface, (255, 200, 255),
                             (center_x + size // 2, center_y - size // 2),
                             (center_x - size // 2, center_y + size // 2), 3)

        # Draw timer for special foods
        if self.type != FoodType.NORMAL:
            current_time = pygame.time.get_ticks()
            time_left = max(0, self.lifetime - (current_time - self.spawn_time))
            timer_ratio = time_left / self.lifetime

            # Draw timer bar above food
            bar_width = GRID_SIZE
            bar_height = 3
            bar_x = x * GRID_SIZE + (GRID_SIZE - bar_width) // 2
            bar_y = y * GRID_SIZE - 8

            # Background
            pygame.draw.rect(surface, (100, 100, 100, 100),
                             (bar_x, bar_y, bar_width, bar_height))
            # Fill
            fill_color = color if timer_ratio > 0.3 else (255, 50, 50)
            pygame.draw.rect(surface, fill_color,
                             (bar_x, bar_y, int(bar_width * timer_ratio), bar_height))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Snake Deluxe")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_tiny = pygame.font.SysFont('Arial', 18)
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.paused = False
        self.base_speed = 8
        self.current_speed = self.base_speed
        self.last_move_time = 0
        self.grid_surface = self.create_grid_surface()
        self.special_food_timer = 0
        self.danger_zones = []
        self.achievements = self.load_achievements()
        self.show_achievement = None
        self.achievement_timer = 0

        # Ensure food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()

    def load_achievements(self):
        try:
            with open('snake_achievements.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "first_blood": {"name": "First Blood", "desc": "Score 50 points", "unlocked": False},
                "combo_master": {"name": "Combo Master", "desc": "Get 5x combo", "unlocked": False},
                "special_eater": {"name": "Special Eater", "desc": "Eat 3 special foods", "unlocked": False},
                "speed_demon": {"name": "Speed Demon", "desc": "Reach speed 15", "unlocked": False},
                "long_snake": {"name": "Long Snake", "desc": "Reach length 20", "unlocked": False}
            }

    def save_achievements(self):
        with open('snake_achievements.json', 'w') as f:
            json.dump(self.achievements, f)

    def check_achievements(self):
        newly_unlocked = []

        if self.snake.score >= 50 and not self.achievements["first_blood"]["unlocked"]:
            self.achievements["first_blood"]["unlocked"] = True
            newly_unlocked.append("first_blood")

        if self.snake.combo_count >= 5 and not self.achievements["combo_master"]["unlocked"]:
            self.achievements["combo_master"]["unlocked"] = True
            newly_unlocked.append("combo_master")

        if self.special_food_timer >= 3 and not self.achievements["special_eater"]["unlocked"]:
            self.achievements["special_eater"]["unlocked"] = True
            newly_unlocked.append("special_eater")

        if self.current_speed >= 15 and not self.achievements["speed_demon"]["unlocked"]:
            self.achievements["speed_demon"]["unlocked"] = True
            newly_unlocked.append("speed_demon")

        if self.snake.length >= 20 and not self.achievements["long_snake"]["unlocked"]:
            self.achievements["long_snake"]["unlocked"] = True
            newly_unlocked.append("long_snake")

        if newly_unlocked:
            self.show_achievement = newly_unlocked[0]
            self.achievement_timer = 180  # 3 seconds at 60 FPS
            self.save_achievements()

    def create_grid_surface(self):
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)
        return surface

    def spawn_special_food(self):
        # Determine special food type based on game state
        food_types = [FoodType.SPECIAL, FoodType.SPEED_BOOST, FoodType.SCORE_MULTIPLIER]
        weights = [0.5, 0.25, 0.25]  # Special food most common

        # Adjust probabilities based on snake length
        if self.snake.length < 5:
            weights = [0.7, 0.2, 0.1]
        elif self.snake.length > 15:
            weights = [0.3, 0.4, 0.3]

        food_type = random.choices(food_types, weights=weights)[0]
        self.food.randomize_position(food_type)
        self.special_food_timer += 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_u:
                        # Debug: spawn special food
                        self.spawn_special_food()
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
        self.paused = False
        self.current_speed = self.base_speed
        self.special_food_timer = 0
        self.danger_zones = []

        while self.food.position in self.snake.positions:
            self.food.randomize_position()

    def update(self, current_time):
        if self.game_over or self.paused:
            return

        # Move snake at controlled speed
        move_delay = 1000 / self.current_speed

        if current_time - self.last_move_time > move_delay:
            if not self.snake.move():
                self.game_over = True
                self.check_achievements()
                return

            self.last_move_time = current_time

            # Check if snake ate food
            if self.snake.get_head_position() == self.food.position:
                food_type = self.food.type
                self.snake.grow(food_type)

                # Apply food effects
                if food_type == FoodType.SPEED_BOOST:
                    self.snake.speed_boost_timer = 300  # 5 seconds at 60 FPS
                elif food_type == FoodType.SCORE_MULTIPLIER:
                    self.snake.score_multiplier_timer = 600  # 10 seconds
                elif food_type == FoodType.SPECIAL:
                    self.special_food_timer += 1
                    # Special food gives temporary shield
                    self.snake.shield_timer = 180  # 3 seconds

                # Spawn new food
                if food_type != FoodType.NORMAL:
                    # 30% chance to spawn another special food
                    if random.random() < 0.3:
                        self.spawn_special_food()
                    else:
                        self.food.randomize_position()
                else:
                    # Every 5 normal foods, spawn special food
                    if self.snake.score % 50 == 0 and self.snake.score > 0:
                        self.spawn_special_food()
                    else:
                        self.food.randomize_position()

                # Ensure food doesn't spawn on snake
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()

                # Increase speed based on length (soft cap at 15)
                self.current_speed = min(15, self.base_speed + (self.snake.length // 5))

                # Add danger zones for long snakes
                if self.snake.length > 10 and random.random() < 0.1:
                    self.add_danger_zone()

        # Update food
        if not self.food.update():
            self.food.randomize_position()

        # Update snake effects
        self.snake.update_particles()

        # Update danger zones
        self.danger_zones = [z for z in self.danger_zones if z[2] > 0]
        for i in range(len(self.danger_zones)):
            self.danger_zones[i] = (self.danger_zones[i][0], self.danger_zones[i][1], self.danger_zones[i][2] - 1)

    def add_danger_zone(self):
        """Add a temporary danger zone that damages snake if entered"""
        x = random.randint(0, GRID_WIDTH - 3)
        y = random.randint(0, GRID_HEIGHT - 3)
        self.danger_zones.append((x, y, 300))  # 5 seconds at 60 FPS

    def draw_danger_zones(self, surface):
        for x, y, timer in self.danger_zones:
            alpha = int(100 * (timer / 300))
            if alpha > 0:
                s = pygame.Surface((GRID_SIZE * 3, GRID_SIZE * 3), pygame.SRCALPHA)
                pygame.draw.rect(s, (*DANGER_ZONE_COLOR[:3], alpha),
                                 (0, 0, GRID_SIZE * 3, GRID_SIZE * 3), 2)
                surface.blit(s, (x * GRID_SIZE, y * GRID_SIZE))

    def draw_ui(self):
        # Score display
        score_text = self.font_medium.render(f"Score: {self.snake.score}", True, TEXT_COLOR)
        length_text = self.font_small.render(f"Length: {self.snake.length}", True, TEXT_COLOR)
        speed_text = self.font_small.render(f"Speed: {self.current_speed:.1f}", True, TEXT_COLOR)

        # Combo display
        combo_color = (255, 215, 0) if self.snake.combo_count > 0 else TEXT_COLOR
        combo_text = self.font_small.render(f"Combo: x{self.snake.combo_count}", True, combo_color)

        # Active effects
        effects = []
        if self.snake.speed_boost_timer > 0:
            effects.append(f"SPEED BOOST: {self.snake.speed_boost_timer // 60 + 1}s")
        if self.snake.score_multiplier_timer > 0:
            effects.append(f"2X SCORE: {self.snake.score_multiplier_timer // 60 + 1}s")
        if self.snake.shield_timer > 0:
            effects.append(f"SHIELD: {self.snake.shield_timer // 60 + 1}s")

        effects_text = self.font_small.render(" | ".join(effects), True, (100, 200, 255))

        # Draw all UI elements
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(length_text, (20, 60))
        self.screen.blit(speed_text, (20, 100))
        self.screen.blit(combo_text, (20, 140))

        if effects:
            self.screen.blit(effects_text, (WIDTH // 2 - effects_text.get_width() // 2, 20))

        # Draw special food counter
        if self.special_food_timer > 0:
            special_text = self.font_small.render(f"Special Foods: {self.special_food_timer}", True, SPECIAL_FOOD_COLOR)
            self.screen.blit(special_text, (WIDTH - special_text.get_width() - 20, 60))

        # Achievement notification
        if self.show_achievement:
            ach = self.achievements[self.show_achievement]
            ach_text = self.font_medium.render(f"Achievement Unlocked: {ach['name']}", True, (255, 215, 0))
            desc_text = self.font_small.render(ach['desc'], True, TEXT_COLOR)

            # Draw background
            bg_rect = pygame.Rect(
                WIDTH // 2 - ach_text.get_width() // 2 - 20,
                HEIGHT - 120,
                ach_text.get_width() + 40,
                80
            )
            pygame.draw.rect(self.screen, (0, 0, 0, 200), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, 3, border_radius=10)

            self.screen.blit(ach_text, (WIDTH // 2 - ach_text.get_width() // 2, HEIGHT - 110))
            self.screen.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, HEIGHT - 70))

            self.achievement_timer -= 1
            if self.achievement_timer <= 0:
                self.show_achievement = None

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, (255, 100, 100))
            score_text = self.font_medium.render(f"Final Score: {self.snake.score}", True, TEXT_COLOR)
            length_text = self.font_small.render(f"Final Length: {self.snake.length}", True, TEXT_COLOR)
            restart_text = self.font_small.render("Press R to Restart | ESC to Quit", True, (200, 255, 200))

            self.screen.blit(game_over_text,
                             (WIDTH // 2 - game_over_text.get_width() // 2,
                              HEIGHT // 2 - 80))
            self.screen.blit(score_text,
                             (WIDTH // 2 - score_text.get_width() // 2,
                              HEIGHT // 2 - 10))
            self.screen.blit(length_text,
                             (WIDTH // 2 - length_text.get_width() // 2,
                              HEIGHT // 2 + 30))
            self.screen.blit(restart_text,
                             (WIDTH // 2 - restart_text.get_width() // 2,
                              HEIGHT // 2 + 90))

        # Pause screen
        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            pause_text = self.font_large.render("PAUSED", True, (255, 255, 255))
            continue_text = self.font_small.render("Press P to continue", True, (200, 200, 255))

            self.screen.blit(pause_text,
                             (WIDTH // 2 - pause_text.get_width() // 2,
                              HEIGHT // 2 - 50))
            self.screen.blit(continue_text,
                             (WIDTH // 2 - continue_text.get_width() // 2,
                              HEIGHT // 2 + 20))

        # Controls hint
        if not self.game_over and not self.paused and self.snake.score == 0:
            controls = [
                "CONTROLS:",
                "Arrow Keys or WASD to move",
                "P to Pause",
                "ESC to Quit"
            ]
            for i, line in enumerate(controls):
                text = self.font_tiny.render(line, True, (180, 200, 255))
                self.screen.blit(text, (WIDTH - text.get_width() - 20, 20 + i * 25))

    def draw(self):
        # Clear screen with background color
        self.screen.fill(BACKGROUND)

        # Draw grid
        self.screen.blit(self.grid_surface, (0, 0))

        # Draw danger zones
        self.draw_danger_zones(self.screen)

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
