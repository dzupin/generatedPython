# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 1-shot  (missed self.screen used screen instead)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is noticeable to end user and therefore more addictive to play.
# 1-shot game repored single errot and single fix included several other corrections
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-35B-A3B-UD-Q8_K_XL.gguf  --mmproj /AI/models/Qwen3.5-35B-A3B_mmproj-BF16.gguf


import pygame
import random
import os
import math
import time

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 25)
DARK_BG = (20, 20, 35)
GREEN = (76, 201, 157)
DARK_GREEN = (46, 151, 107)
RED = (255, 87, 87)
YELLOW = (255, 215, 0)
CYAN = (0, 255, 255)
PURPLE = (186, 85, 211)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
LIGHT_GRAY = (180, 180, 185)
GRAY = (100, 100, 105)

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 25
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS_BASE = 10


# Particle System
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.alpha = 255
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity[0] *= 0.95
        self.velocity[1] *= 0.95
        self.alpha -= 8
        self.size = max(0, self.size - 0.2)

    def is_alive(self):
        return self.alpha > 0 and self.size > 0

    def draw(self, screen):
        if self.is_alive():
            alpha_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.color, int(self.alpha)),
                               (int(self.size), int(self.size)), int(self.size))
            screen.blit(alpha_surface, (self.x - self.size, self.y - self.size))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # FIXED: Window title without emojis
        pygame.display.set_caption("NEON SNAKE - ULTIMATE")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)

        # Initialize high_score FIRST before calling load_high_score()
        self.high_score = 0
        self.load_high_score()

        # Game state
        self.snake = []
        self.food = None
        self.special_food = None
        self.particles = []
        self.score = 0
        self.level = 1
        self.combo = 0
        self.streak = 0
        self.last_eat_time = 0
        self.game_over = False
        self.paused = False
        self.show_achievement = False
        self.achievement_timer = 0
        self.achievement_name = "Achievement"

        # Achievements - FIXED: Replaced emojis with text
        self.achievements = {
            'first_100': {'name': 'Rookie', 'points': 100, 'unlocked': False, 'icon': '[BRONZE]'},
            'first_500': {'name': 'Pro', 'points': 500, 'unlocked': False, 'icon': '[SILVER]'},
            'first_1000': {'name': 'Master', 'points': 1000, 'unlocked': False, 'icon': '[GOLD]'},
            'combo_10': {'name': 'Combo King', 'points': 10, 'unlocked': False, 'icon': '[COMBO]'},
            'level_5': {'name': 'Speedster', 'points': 5, 'unlocked': False, 'icon': '[SPEED]'},
        }

        self.combo_count = 0
        self.combo_max = 0
        self.special_food_timer = 0
        self.special_food_active = False

        self.direction = (1, 0)

    def load_high_score(self):
        try:
            if os.path.exists("snake_high_score.txt"):
                with open("snake_high_score.txt", "r") as f:
                    self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        try:
            with open("snake_high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.score = 0
        self.level = 1
        self.combo = 0
        self.streak = 0
        self.combo_count = 0
        self.combo_max = 0
        self.special_food_active = False
        self.special_food_timer = 0
        self.particles = []
        self.game_over = False
        self.paused = False
        self.show_achievement = False
        self.achievement_timer = 0
        self.food = self.spawn_food()
        self.special_food = None
        self.direction = (1, 0)
        self.spawn_special_food()

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def spawn_special_food(self):
        if not self.special_food_active:
            self.special_food_timer = random.randint(10, 30)
            self.special_food_active = True
            self.special_food = self.spawn_food()

    def get_base_speed(self):
        base = FPS_BASE
        bonus = self.level * 1.5
        return min(base + bonus, 30)

    def get_combo_bonus(self):
        if self.combo >= 10:
            return 2.0
        elif self.combo >= 5:
            return 1.5
        return 1.0

    def update(self):
        if self.game_over or self.paused:
            return

        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()

        # Decrease special food timer
        if self.special_food_active:
            self.special_food_timer -= 1
            if self.special_food_timer <= 0:
                self.special_food = None
                self.special_food_active = False

        # Move snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Check collision with walls
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over = True
            self.save_high_score()
            return

        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            self.save_high_score()
            return

        # Check food collision
        ate_food = False
        if new_head == self.food:
            self.snake.insert(0, new_head)
            ate_food = True
            self.handle_food_eaten(True)
            self.food = self.spawn_food()
        elif self.special_food_active and new_head == self.special_food:
            self.snake.insert(0, new_head)
            ate_food = True
            self.handle_food_eaten(True, special=True)
            self.special_food = None
            self.special_food_active = False
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

        if not ate_food:
            # Check streak for combo reset
            current_time = time.time()
            if current_time - self.last_eat_time > 5:
                self.combo_count = 0
                if self.combo_count > self.combo_max:
                    self.combo_max = self.combo_count
            self.last_eat_time = current_time

        # Check achievements
        self.check_achievements()

    def handle_food_eaten(self, food_eaten, special=False):
        base_points = 10 if not special else 25
        combo_bonus = self.get_combo_bonus()
        streak_bonus = self.streak * 2

        if not special:
            self.combo_count += 1
            self.combo = self.combo_count

        points = int(base_points * combo_bonus + streak_bonus)
        self.score += points
        self.streak += 1

        # Create particles
        fx, fy = self.food[0] * GRID_SIZE + GRID_SIZE // 2, self.food[1] * GRID_SIZE + GRID_SIZE // 2
        for _ in range(15):
            self.particles.append(Particle(fx, fy, (RED, GREEN, YELLOW)[random.randint(0, 2)]))

        # Level up every 100 points
        new_level = 1 + (self.score // 100)
        if new_level > self.level:
            self.level = new_level
            self.show_achievement = True
            self.achievement_timer = 120

    def check_achievements(self):
        for key, achievement in self.achievements.items():
            if not achievement['unlocked'] and self.score >= achievement['points']:
                achievement['unlocked'] = True
                self.show_achievement = True
                self.achievement_timer = 180
                self.achievement_name = achievement['name']

    def draw(self):
        # Draw background with gradient
        self.screen.fill(DARK_BG)

        # Draw grid
        self.draw_grid()

        # Draw particles
        for p in self.particles:
            p.draw(self.screen)

        # Draw special food if active
        if self.special_food_active and self.special_food:
            self.draw_special_food()

        # Draw food
        self.draw_food()

        # Draw snake
        self.draw_snake()

        # Draw UI
        self.draw_ui()

        # Draw achievement
        if self.show_achievement and self.achievement_timer > 0:
            self.draw_achievement()

        # Draw pause
        if self.paused:
            self.draw_pause()

        # Draw game over
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (30, 30, 50), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (30, 30, 50), (0, y), (WINDOW_WIDTH, y))

    def draw_food(self):
        x, y = self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE
        center_x, center_y = x + GRID_SIZE // 2, y + GRID_SIZE // 2

        # Glow effect
        glow_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*RED, 80), (GRID_SIZE, GRID_SIZE), GRID_SIZE // 2)
        self.screen.blit(glow_surface, (x - GRID_SIZE, y - GRID_SIZE))

        # Main food
        pygame.draw.circle(self.screen, RED, (center_x, center_y), GRID_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, YELLOW, (center_x - 3, center_y - 3), 4)

    def draw_special_food(self):
        x, y = self.special_food[0] * GRID_SIZE, self.special_food[1] * GRID_SIZE
        center_x, center_y = x + GRID_SIZE // 2, y + GRID_SIZE // 2

        # Pulsing effect
        pulse = math.sin(time.time() * 5) * 5 + 10

        # Glow effect
        glow_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*GOLD, 120), (GRID_SIZE, GRID_SIZE), int(pulse))
        self.screen.blit(glow_surface, (x - GRID_SIZE, y - GRID_SIZE))

        # Star shape
        points = []
        for i in range(5):
            angle = i * 72 * math.pi / 180 - 90
            outer_x = center_x + int(12 * math.cos(angle))
            outer_y = center_y + int(12 * math.sin(angle))
            points.append((outer_x, outer_y))
            angle += 36 * math.pi / 180
            inner_x = center_x + int(6 * math.cos(angle))
            inner_y = center_y + int(6 * math.sin(angle))
            points.append((inner_x, inner_y))

        pygame.draw.polygon(self.screen, GOLD, points)
        pygame.draw.polygon(self.screen, WHITE, points, 2)

    def draw_snake(self):
        for i, segment in enumerate(self.snake):
            x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE

            # Gradient color based on position
            if i == 0:
                color = GREEN
                glow = 80
            else:
                color = DARK_GREEN
                glow = 50

            # Glow effect
            glow_surface = pygame.Surface((GRID_SIZE + 4, GRID_SIZE + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color, glow), (0, 0, GRID_SIZE + 4, GRID_SIZE + 4), border_radius=4)
            self.screen.blit(glow_surface, (x - 2, y - 2))

            # Main segment
            pygame.draw.rect(self.screen, color, (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2), border_radius=4)

            # Highlight
            if i == 0:
                pygame.draw.rect(self.screen, WHITE, (x + 4, y + 4, 8, 8), border_radius=2)

    def draw_ui(self):
        # Score
        text = self.font_medium.render(f"Score: {self.score}", True, GREEN)
        self.screen.blit(text, (15, 15))

        # High Score
        text = self.font_small.render(f"High Score: {self.high_score}", True, LIGHT_GRAY)
        self.screen.blit(text, (15, 45))

        # Level
        level_text = self.font_medium.render(f"Level: {self.level}", True, CYAN)
        self.screen.blit(level_text, (WINDOW_WIDTH - 150, 15))

        # Combo indicator
        if self.combo_count > 1:
            combo_text = self.font_small.render(f"Combo: {self.combo_count}x", True, ORANGE)
            self.screen.blit(combo_text, (WINDOW_WIDTH - 150, 50))

        # Streak
        if self.streak > 0:
            streak_text = self.font_tiny.render(f"Streak: {self.streak}", True, YELLOW)
            self.screen.blit(streak_text, (WINDOW_WIDTH - 150, 75))

        # Achievements list
        unlocked_count = sum(1 for a in self.achievements.values() if a['unlocked'])
        achievement_text = self.font_tiny.render(f"Achievements: {unlocked_count}/{len(self.achievements)}", True,
                                                 PURPLE)
        self.screen.blit(achievement_text, (15, WINDOW_HEIGHT - 25))

    def draw_achievement(self):
        alpha = min(255, self.achievement_timer * 2)
        overlay = pygame.Surface((WINDOW_WIDTH, 100), pygame.SRCALPHA)
        overlay.fill((*PURPLE, alpha))
        self.screen.blit(overlay, (0, 100))

        achievement = self.achievements.get('level_5', {'name': 'Achievement', 'icon': '[TROPHY]'})
        # FIXED: Replaced emoji with text
        text = self.font_medium.render(f"{achievement.get('icon', '[TROPHY]')} {achievement['name']} UNLOCKED!", True,
                                       WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(text, text_rect)

        self.achievement_timer -= 1
        if self.achievement_timer <= 0:
            self.show_achievement = False

    def draw_pause(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        text = self.font_medium.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        text = self.font_small.render("Press P to Resume", True, LIGHT_GRAY)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(text, text_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(text, text_rect)

        text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(text, text_rect)

        if self.score >= self.high_score:
            # FIXED: Replaced emoji with text
            text = self.font_small.render("[NEW HIGH SCORE!]", True, GOLD)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(text, text_rect)

        text = self.font_small.render("Press SPACE to Restart", True, LIGHT_GRAY)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.reset_game()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif not self.paused:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        if self.direction != (0, 1):
                            self.direction = (0, -1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.direction != (0, -1):
                            self.direction = (0, 1)
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.direction != (1, 0):
                            self.direction = (-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.direction != (-1, 0):
                            self.direction = (1, 0)
        return True

    def run(self):
        self.reset_game()
        self.direction = (1, 0)
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.get_base_speed())
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
