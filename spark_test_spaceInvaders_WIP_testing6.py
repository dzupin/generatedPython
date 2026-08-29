# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/Qwen3.6-27B-MTP-UD-Q8_K_XL.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import math
import random
import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Enhanced Edition")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 205, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 215, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 100, 0)
CYAN = (0, 200, 200)
GRAY = (100, 100, 100)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (150, 150, 150)

# Game data file
DATA_FILE = "space_invaders_data.json"


# Utility functions
def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass


def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"high_score": 0, "unlocked_levels": 1, "warnings_allowed": True}


# Load game data
game_data = load_data()


# Sound generation functions (procedural audio)
class SoundGenerator:
    @staticmethod
    def generate_beep(frequency=440, duration=0.1, sample_rate=22050):
        # Simple beep generation
        samples = int(sample_rate * duration)
        arr = []
        for i in range(samples):
            val = math.sin(2 * math.pi * frequency * i / sample_rate) * 0.3
            arr.append(int(val * 32767))
        return arr

    @staticmethod
    def generate_sweep(f_start=440, f_end=880, duration=0.5, sample_rate=22050):
        samples = int(sample_rate * duration)
        arr = []
        for i in range(samples):
            t = i / samples
            freq = f_start + (f_end - f_start) * t
            val = math.sin(2 * math.pi * freq * i / sample_rate) * 0.3
            val *= (1 - t) * 0.5
            arr.append(int(val * 32767))
        return arr


# Sound effects
class SoundEffects:
    def __init__(self):
        self.sounds = {}
        self.mixer = pygame.mixer

    def create_sound(self, name, frequency, duration):
        try:
            # Generate procedural sound
            arr = SoundGenerator.generate_beep(frequency, duration)
            surface = pygame.sndarray.make_sound(bytearray(arr))
            self.sounds[name] = surface
        except:
            pass

    def play(self, name, loops=0, maxtime=0):
        if name in self.sounds:
            try:
                self.sounds[name].play(loops, maxtime)
            except:
                pass


sound_effects = SoundEffects()

# Generate some sound effects
sound_effects.create_sound("shoot", 880, 0.1)
sound_effects.create_sound("explosion", 220, 0.3)
sound_effects.create_sound("powerup", 440, 0.2)
sound_effects.create_sound("warning", 660, 0.5)
sound_effects.create_sound("alert", 330, 0.8)


# Background music (simple procedural)
def play_background_music():
    # This would normally play background music
    pass


# Particle effects
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    life: int
    size: int

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0


particles: List[Particle] = []


def create_explosion(x, y, color, count=20):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        particles.append(Particle(
            x, y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            color,
            random.randint(20, 50),
            random.randint(2, 6)
        ))


# Game objects
class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)


class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 30)
        self.speed = 5
        self.shield = 100
        self.max_shield = 100
        self.cooldown = 0
        self.direction = 0

    def update(self):
        self.x += self.direction * self.speed
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.update_rect()

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + 0.05)

    def draw(self, surface):
        # Draw player ship
        points = [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height * 0.7),
            (self.x, self.y + self.height)
        ]

        pygame.draw.polygon(surface, GREEN, points)
        pygame.draw.polygon(surface, CYAN, points, 2)

        # Shield bar
        pygame.draw.rect(surface, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(surface, GREEN, (self.x, self.y - 10, (self.shield / self.max_shield) * self.width, 5))

        # Engine flames
        if self.direction != 0:
            flame_x = self.x + self.width // 2 + self.direction * 10
            flame_y = self.y + self.height
            pygame.draw.polygon(surface, ORANGE, [
                (flame_x, flame_y),
                (flame_x + 5 * self.direction, flame_y + 15),
                (flame_x - 5 * self.direction, flame_y + 15)
            ])


class Enemy(GameObject):
    def __init__(self, x, y, enemy_type=0):
        super().__init__(x, y, 40, 30)
        self.type = enemy_type  # 0-4 for different enemies
        self.health = 100
        self.speed_x = 1
        self.speed_y = 0.5
        self.direction = 1
        self.cooldown = 0

    def update(self, player=None):
        self.x += self.direction * self.speed_x
        self.y += self.speed_y * self.direction

        if self.cooldown > 0:
            self.cooldown -= 1

        self.update_rect()

        # Bounce off walls
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.direction *= -1
            self.speed_x += 0.1

    def draw(self, surface):
        colors = [RED, PURPLE, YELLOW, CYAN, ORANGE]
        color = colors[self.type % len(colors)]

        # Draw enemy ship
        points = [
            (self.x, self.y + self.height),
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height * 0.7)
        ]

        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, LIGHT_GRAY, points, 2)

        # Health bar
        if self.health < 100:
            pygame.draw.rect(surface, RED, (self.x, self.y - 8, self.width, 4))
            pygame.draw.rect(surface, GREEN, (self.x, self.y - 8, (self.health / 100) * self.width, 4))


class Bullet(GameObject):
    def __init__(self, x, y, direction=1, speed=5):
        super().__init__(x, y, 3, 10)
        self.direction = direction
        self.speed = speed
        self.is_player = direction < 0

    def update(self):
        self.y += self.direction * self.speed
        self.update_rect()
        return self.y > HEIGHT or self.y < 0


class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.segments = []
        self.max_health = 50

        # Create destructible segments
        for i in range(6):
            for j in range(4):
                self.segments.append([x + i * 10, y + j * 10, 10, 10, self.max_health])

    def update(self):
        # Remove dead segments
        self.segments = [s for s in self.segments if s[4] > 0]

    def draw(self, surface):
        for segment in self.segments:
            if segment[4] > 0:
                health_ratio = segment[4] / self.max_health
                color = (int(100 * health_ratio), int(100 * health_ratio), 255)
                pygame.draw.rect(surface, color, (segment[0], segment[1], segment[2], segment[3]))


class PowerUp(GameObject):
    def __init__(self, x, y, ptype="weapon"):
        super().__init__(x, y, 15, 15)
        self.type = ptype
        self.speed = 2

    def update(self):
        self.y += self.speed
        self.update_rect()
        return self.y > HEIGHT


class Level:
    def __init__(self, level_num):
        self.num = level_num
        self.enemy_rows = 5
        self.enemy_cols = 10
        self.enemy_spacing_x = 60
        self.enemy_spacing_y = 50
        self.enemy_offset_x = 80
        self.enemy_offset_y = 60
        self.warning_duration = 0
        self.is_warning = False
        self.background_speed = 0
        self.completed = False

    def spawn_enemies(self):
        enemies = []
        for row in range(self.enemy_rows):
            for col in range(self.enemy_cols):
                x = self.enemy_offset_x + col * self.enemy_spacing_x
                y = self.enemy_offset_y + row * self.enemy_spacing_y
                enemy_type = row % 5
                enemies.append(Enemy(x, y, enemy_type))
        return enemies


# Game state
class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_COMPLETE = 3
    WARNING = 4
    SETTINGS = 5


# Warning system
class WarningSystem:
    def __init__(self):
        self.warnings = []
        self.warning_time = 0

    def add_warning(self, message, duration=180):
        self.warnings.append({"message": message, "timer": duration})
        sound_effects.play("warning")

        # Save warning to file (as required)
        warning_data = {
            "warning": message,
            "timestamp": str(pygame.time.get_ticks()),
            "type": "security_warning"
        }
        save_data({"last_warning": warning_data})

    def update(self):
        self.warnings = [w for w in self.warnings if w["timer"] > 0]
        for w in self.warnings:
            w["timer"] -= 1

        if self.warning_time > 0:
            self.warning_time -= 1


# Main game class
class SpaceInvadersGame:
    def __init__(self):
        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.bullets = []
        self.barriers = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.shield_regen = False
        self.warning_system = WarningSystem()
        self.warning_mode = False
        self.warning_timer = 0

        # UI elements
        self.font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 40)
        self.warning_font = pygame.font.SysFont("Arial", 60)

        # Menu options
        self.menu_options = ["Start Game", "Level Select", "Settings", "Quit"]
        self.selected_option = 0

        # Settings
        self.sound_enabled = True
        self.warnings_allowed = game_data.get("warnings_allowed", True)

    def reset_game(self):
        self.player = Player(WIDTH // 2, HEIGHT - 50)
        self.enemies = []
        self.bullets = []
        self.barriers = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.shield_regen = False
        self.warning_mode = False
        self.warning_timer = 0

        # Create barriers
        for i in range(3):
            offset = 200 * i + 100
            barrier = Barrier(offset, HEIGHT - 150)
            self.barriers.append(barrier)

        # Spawn initial enemies
        self.spawn_level_enemies()

    def spawn_level_enemies(self):
        level = Level(self.level)
        enemies = level.spawn_enemies()
        self.enemies.extend(enemies)

        # Add warnings based on level difficulty
        if self.level >= 3:
            self.warning_system.add_warning(f"SECURITY ALERT: Level {self.level} Breach Detected!")

        if self.level >= 5:
            self.warning_mode = True
            self.warning_timer = 300
            self.warning_system.add_warning("CRITICAL SYSTEM BREACH!")

            # Update game data file
            game_data["high_score"] = min(self.score, game_data.get("high_score", 0))
            game_data["unlocked_levels"] = min(self.level, game_data.get("unlocked_levels", 1))
            save_data(game_data)

    def shoot_bullet(self, x, y, direction=-1, is_player=True):
        if is_player and self.player.cooldown > 0:
            return

        if is_player and self.player:
            self.player.cooldown = 30

        self.bullets.append(Bullet(x, y, direction, 8))
        sound_effects.play("shoot")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                        return

                if self.state == GameState.PLAYING:
                    # Shooting controls
                    if event.key == pygame.K_SPACE:
                        if self.player:
                            self.shoot_bullet(self.player.x + self.player.width // 2,
                                              self.player.y, -1, True)

                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                    if event.key == pygame.K_DOWN:
                        self.selected_option = min(len(self.menu_options) - 1, self.selected_option + 1)
                    if event.key == pygame.K_RETURN:
                        self.handle_menu_selection()

    def handle_menu_selection(self):
        option = self.menu_options[self.selected_option]
        if option == "Start Game":
            self.reset_game()
            self.state = GameState.PLAYING
        elif option == "Level Select":
            self.state = GameState.MENU
            # Would show level select
        elif option == "Settings":
            self.state = GameState.MENU
            # Would show settings
        elif option == "Quit":
            pygame.quit()
            exit()

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # Update warning system
        self.warning_system.update()

        if self.warning_mode:
            self.warning_timer -= 1
            if self.warning_timer <= 0:
                self.warning_mode = False

        # Update player
        if self.player:
            self.player.direction = 0
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.player.direction = -1
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.player.direction = 1
            self.player.update()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()

            # Enemy shooting
            if random.random() < 0.001:
                self.shoot_bullet(enemy.x + enemy.width // 2, enemy.y + enemy.height,
                                  1, False)

        # Update bullets
        for bullet in self.bullets[:]:
            if bullet.update():
                self.bullets.remove(bullet)
                continue

            # Collision detection
            if bullet.is_player:
                for enemy in self.enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 20
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += 100
                            create_explosion(enemy.x + enemy.width // 2,
                                             enemy.y + enemy.height // 2,
                                             RED)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
            else:
                if self.player and bullet.rect.colliderect(self.player.rect):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

        # Update barriers
        for barrier in self.barriers[:]:
            barrier.update()
            if not barrier.segments:
                self.barriers.remove(barrier)

        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.y > HEIGHT:
                self.powerups.remove(powerup)

        # Check level completion
        if not self.enemies:
            self.level += 1
            if self.level > game_data.get("unlocked_levels", 1):
                game_data["unlocked_levels"] = self.level
                save_data(game_data)

            self.spawn_level_enemies()
            self.state = GameState.LEVEL_COMPLETE

        # Update game data with security checks
        if self.warning_mode:
            game_data["high_score"] = min(self.score, game_data.get("high_score", 0))
            save_data(game_data)

    def draw(self, surface):
        surface.fill(BLACK)

        if self.state == GameState.MENU:
            self.draw_menu(surface)
            return

        if self.state == GameState.GAME_OVER:
            self.draw_game_over(surface)
            return

        if self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete(surface)
            return

        # Draw game objects
        if self.player:
            self.player.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

        for bullet in self.bullets:
            color = GREEN if bullet.is_player else RED
            pygame.draw.rect(surface, color, bullet.rect)

        for barrier in self.barriers:
            barrier.draw(surface)

        for powerup in self.powerups:
            pygame.draw.rect(surface, YELLOW, powerup.rect)

        # Draw particles
        for particle in self.particles[:]:
            pygame.draw.circle(surface, particle.color,
                               (int(particle.x), int(particle.y)),
                               int(particle.size))
            if not particle.update():
                self.particles.remove(particle)

        # Draw warnings
        for warning in self.warning_system.warnings:
            text = self.warning_font.render(warning["message"], True, YELLOW)
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))

        if self.warning_mode:
            text = self.warning_font.render("WARNING MODE ACTIVE", True, RED)
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

            # Draw security scan lines
            for i in range(0, HEIGHT, 4):
                pygame.draw.line(surface, (50, 0, 0), (0, i), (WIDTH, i), 1)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)

        surface.blit(score_text, (10, 10))
        surface.blit(lives_text, (10, 40))
        surface.blit(level_text, (10, 70))

        # Draw progress info
        warning_text = self.font.render("WARNING SYSTEM ACTIVE", True, YELLOW)
        surface.blit(warning_text, (WIDTH - warning_text.get_width() - 10, 10))

    def draw_menu(self, surface):
        # Draw animated background
        for i in range(0, HEIGHT, 20):
            pygame.draw.line(surface, DARK_GRAY, (0, i), (WIDTH, i), 1)

        title = self.large_font.render("SPACE INVADERS", True, CYAN)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw menu options
        for i, option in enumerate(self.menu_options):
            color = RED if i == self.selected_option else WHITE
            text = self.font.render(option, True, color)
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 300 + i * 40))

        warning = self.font.render("WARNING SYSTEM: ACTIVE", True, YELLOW)
        surface.blit(warning, (WIDTH // 2 - warning.get_width() // 2, 500))

    def draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

        text = self.large_font.render("GAME OVER", True, RED)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))

        warning_text = self.font.render("SECURITY WARNING: Unauthorized Access Detected!", True, YELLOW)
        surface.blit(warning_text, (WIDTH // 2 - warning_text.get_width() // 2, 300))

    def draw_level_complete(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

        text = self.large_font.render("LEVEL COMPLETE", True, GREEN)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))

        warning_text = self.font.render(f"WARNING: System Breach in Level {self.level}!", True, YELLOW)
        surface.blit(warning_text, (WIDTH // 2 - warning_text.get_width() // 2, 300))


# Create game instance
game = SpaceInvadersGame()

# Main game loop
clock = pygame.time.Clock()
running = True

print("Starting Space Invaders - Enhanced Edition")
print("WARNING SYSTEM: Active")
print("SECURITY STATUS: Monitoring")

try:
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        game.handle_events(events)
        game.update()
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)

finally:
    pygame.quit()
    print("Game exited. Security data saved.")
    save_data(game_data)
