# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1 --temp 1.0  --model  /AI/models/Step-3.5-Flash-MXFP4_MOE-00001-of-00007.gguf

# to fix 8 follow up errors original reasoning model is unusably slow and unreliable therefore for fixes I used:
#             /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Devstral-Small-2-24B-Instruct-2512-Q8_0.gguf  --mmproj /AI/models/Devstral-Small-2-24B-Instruct-2512-mmproj-BF16.gguf

from math import cos, sin, radians
import pygame
import random
import sys
import json
import os
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Deluxe")
clock = pygame.time.Clock()

# Load fonts
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 36, bold=True)
font_large = pygame.font.SysFont('Arial', 72, bold=True)
font_score = pygame.font.SysFont('Courier New', 28, bold=True)

# High score file
HIGH_SCORE_FILE = "space_invaders_highscores.json"


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.life = random.randint(20, 40)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, -1)
        self.gravity = 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, self.color,
                             (int(self.x), int(self.y), int(self.size), int(self.size)))

    def is_alive(self):
        return self.life > 0


class PowerUp:
    TYPES = {
        'rapid': {'color': CYAN, 'symbol': '⚡', 'duration': 10000, 'name': 'Rapid Fire'},
        'multishot': {'color': ORANGE, 'symbol': '✦', 'duration': 15000, 'name': 'Triple Shot'},
        'shield': {'color': BLUE, 'symbol': '🛡', 'duration': 8000, 'name': 'Shield'},
        'speed': {'color': GREEN, 'symbol': '⚡', 'duration': 12000, 'name': 'Speed Boost'},
        'magnet': {'color': PINK, 'symbol': '🧲', 'duration': 10000, 'name': 'Score Magnet'},
        'bomb': {'color': YELLOW, 'symbol': '💣', 'duration': 1, 'name': 'Screen Clear'}
    }

    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.speed = 2
        self.width = 30
        self.height = 30
        self.angle = 0
        self.data = self.TYPES[power_type]

    def update(self):
        self.y += self.speed
        self.angle = (self.angle + 5) % 360

    def draw(self, surface):
        # Draw spinning power-up
        points = []
        for i in range(3):
            angle_rad = radians(self.angle + i * 120)  # Changed from pygame.math.radians
            px = self.x + 15 + 10 * cos(angle_rad)  # Changed from pygame.math.cos
            py = self.y + 15 + 10 * sin(angle_rad)  # Changed from pygame.math.sin
            points.append((px, py))

        pygame.draw.polygon(surface, self.data['color'], points)
        pygame.draw.polygon(surface, WHITE, points, 2)

        # Draw symbol
        symbol_text = font_small.render(self.data['symbol'], True, WHITE)
        surface.blit(symbol_text, (self.x + 8, self.y + 5))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.base_speed = 5
        self.speed = self.base_speed
        self.color = GREEN
        self.lives = 3
        self.score = 0
        self.shoot_cooldown = 0
        self.base_shoot_delay = 250
        self.shoot_delay = self.base_shoot_delay
        self.powerups = {
            'rapid': {'active': False, 'timer': 0},
            'multishot': {'active': False, 'timer': 0},
            'shield': {'active': False, 'timer': 0},
            'speed': {'active': False, 'timer': 0},
            'magnet': {'active': False, 'timer': 0}
        }
        self.shield_active = False
        self.shield_timer = 0
        self.magnet_active = False
        self.magnet_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.last_kill_time = 0

    def draw(self, surface):
        # Draw shield if active
        if self.shield_active:
            shield_alpha = min(200, 100 + int(50 * (self.shield_timer / 8000)))
            shield_surface = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surface, (0, 150, 255, shield_alpha),
                                (0, 0, self.width + 30, self.height + 30), 4)
            surface.blit(shield_surface, (self.x - 15, self.y - 15))

        # Draw player ship
        points = [
            (self.x + self.width // 2, self.y),  # Top
            (self.x, self.y + self.height),  # Bottom left
            (self.x + self.width, self.y + self.height)  # Bottom right
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (200, 255, 200), points, 2)

        # Draw cockpit
        pygame.draw.rect(surface, BLUE,
                         (self.x + self.width // 2 - 5, self.y + 10, 10, 10))

        # Draw engine glow
        if random.random() > 0.7:
            pygame.draw.polygon(surface, (255, 150, 0), [
                (self.x + 10, self.y + self.height),
                (self.x + 20, self.y + self.height + 5),
                (self.x + 30, self.y + self.height)
            ])

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(self.x, WIDTH - self.width))

    def shoot(self):
        current_delay = self.shoot_delay
        if self.powerups['rapid']['active']:
            current_delay = max(50, self.base_shoot_delay * 0.3)

        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = current_delay
            bullets = []

            if self.powerups['multishot']['active']:
                # Triple shot
                for i in range(-1, 2):
                    bullets.append(Bullet(self.x + self.width // 2 + i * 12, self.y, -10, YELLOW))
            else:
                bullets.append(Bullet(self.x + self.width // 2, self.y, -10, YELLOW))

            return bullets
        return []

    def update(self, current_time):
        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= clock.get_time()

        # Update powerup timers
        for powerup in self.powerups.values():
            if powerup['active']:
                powerup['timer'] -= clock.get_time()
                if powerup['timer'] <= 0:
                    powerup['active'] = False

        # Update shield
        if self.shield_active:
            self.shield_timer -= clock.get_time()
            if self.shield_timer <= 0:
                self.shield_active = False

        # Update magnet
        if self.magnet_active:
            self.magnet_timer -= clock.get_time()
            if self.magnet_timer <= 0:
                self.magnet_active = False

        # Update combo
        if current_time - self.last_kill_time > 2000:  # 2 second window for combos
            self.combo = 0

        # Update speed based on powerup
        if self.powerups['speed']['active']:
            self.speed = self.base_speed * 1.8
        else:
            self.speed = self.base_speed

    def activate_powerup(self, power_type):
        if power_type == 'shield':
            self.shield_active = True
            self.shield_timer = PowerUp.TYPES['shield']['duration']
        elif power_type == 'magnet':
            self.magnet_active = True
            self.magnet_timer = PowerUp.TYPES['magnet']['duration']
        elif power_type == 'bomb':  # Special handling for bomb
            # Bomb is handled elsewhere, so we just need to make sure it's not in powerups dict
            pass
        else:  # For other powerups (rapid, multishot, speed)
            self.powerups[power_type]['active'] = True
            self.powerups[power_type]['timer'] = PowerUp.TYPES[power_type]['duration']

    def take_damage(self):
        if self.shield_active:
            self.shield_active = False
            return False
        self.lives -= 1
        return True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_magnet_rect(self):
        if self.magnet_active:
            return pygame.Rect(self.x - 100, self.y - 100,
                               self.width + 200, self.height + 200)
        return None


class Alien:
    def __init__(self, x, y, alien_type=0, wave=1):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.type = alien_type
        self.wave = wave
        self.base_speed = 2
        self.speed = self.base_speed * (1 + wave * 0.1)
        self.direction = 1
        self.move_down = False
        self.shoot_timer = 0
        self.shoot_delay = random.randint(2000, 5000)
        self.health = 1
        self.color = [PURPLE, RED, BLUE, ORANGE][alien_type % 4]
        self.score_value = [10, 20, 30, 50][alien_type % 4]
        self.last_move_time = 0
        self.move_delay = 500

    def draw(self, surface):
        # Draw different alien types
        if self.type == 0:
            # Crab-like alien
            points = [
                (self.x + 10, self.y + 5),
                (self.x + 30, self.y + 5),
                (self.x + 5, self.y + 15),
                (self.x + 35, self.y + 15),
                (self.x + 10, self.y + 25),
                (self.x + 30, self.y + 25)
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, (255, 200, 200), points, 2)
            # Eyes
            pygame.draw.circle(surface, WHITE, (self.x + 15, self.y + 15), 4)
            pygame.draw.circle(surface, WHITE, (self.x + 25, self.y + 15), 4)
            pygame.draw.circle(surface, BLACK, (self.x + 15, self.y + 15), 2)
            pygame.draw.circle(surface, BLACK, (self.x + 25, self.y + 15), 2)

        elif self.type == 1:
            # Squid-like alien
            pygame.draw.ellipse(surface, self.color,
                                (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(surface, (255, 200, 200),
                                (self.x, self.y, self.width, self.height), 2)
            # Eyes
            pygame.draw.circle(surface, WHITE, (self.x + 10, self.y + 15), 3)
            pygame.draw.circle(surface, WHITE, (self.x + 30, self.y + 15), 3)
            pygame.draw.circle(surface, BLACK, (self.x + 10, self.y + 15), 1)
            pygame.draw.circle(surface, BLACK, (self.x + 30, self.y + 15), 1)

        elif self.type == 2:
            # Classic UFO shape
            pygame.draw.ellipse(surface, self.color,
                                (self.x + 5, self.y, self.width - 10, self.height // 2))
            pygame.draw.rect(surface, self.color,
                             (self.x, self.y + self.height // 2, self.width, self.height // 2))
            pygame.draw.ellipse(surface, self.color,
                                (self.x + 10, self.y - 5, 20, 15))
            pygame.draw.ellipse(surface, (255, 200, 200),
                                (self.x + 5, self.y, self.width - 10, self.height // 2), 2)
            # Eyes
            pygame.draw.circle(surface, WHITE, (self.x + 15, self.y + 15), 3)
            pygame.draw.circle(surface, WHITE, (self.x + 25, self.y + 15), 3)

        else:  # type 3 - Boss alien
            # Draw larger, menacing alien
            pygame.draw.ellipse(surface, self.color,
                                (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(surface, (255, 200, 0),
                                (self.x, self.y, self.width, self.height), 3)
            # Crown/spikes
            for i in range(5):
                angle = i * 72
                spike_x = self.x + self.width // 2 + 8 * cos(radians(angle))  # Changed from pygame.math
                spike_y = self.y + 5 + 8 * sin(radians(angle))  # Changed from pygame.math
                pygame.draw.line(surface, YELLOW,
                                 (self.x + self.width // 2, self.y),
                                 (spike_x, spike_y), 3)
            # Eyes
            pygame.draw.circle(surface, RED, (self.x + 12, self.y + 15), 5)
            pygame.draw.circle(surface, RED, (self.x + 28, self.y + 15), 5)
            pygame.draw.circle(surface, YELLOW, (self.x + 12, self.y + 15), 2)
            pygame.draw.circle(surface, YELLOW, (self.x + 28, self.y + 15), 2)

    def move(self, aliens, current_time):
        if current_time - self.last_move_time < self.move_delay:
            return False

        self.last_move_time = current_time

        # Check if any alien needs to move down
        move_down = False
        for alien in aliens:
            if (alien.x <= 10 and alien.direction == -1) or \
                    (alien.x >= WIDTH - alien.width - 10 and alien.direction == 1):
                move_down = True
                break

        if move_down:
            self.y += 15
            self.direction *= -1
        else:
            self.x += self.speed * self.direction

        return move_down

    def can_shoot(self, current_time):
        if current_time - self.shoot_timer > self.shoot_delay:
            self.shoot_timer = current_time
            return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Bullet:
    def __init__(self, x, y, speed, color, is_alien=False):
        self.x = x
        self.y = y
        self.width = 4 if not is_alien else 6
        self.height = 12 if not is_alien else 8
        self.speed = speed
        self.color = color
        self.is_alien = is_alien

    def draw(self, surface):
        if self.is_alien:
            # Alien bullet with trail
            for i in range(3):
                trail_alpha = 150 - i * 50
                trail_color = (*self.color, trail_alpha) if len(self.color) == 3 else self.color
                pygame.draw.rect(surface, trail_color,
                                 (self.x - self.width // 2, self.y + i * 3,
                                  self.width, self.height - i * 3))
        else:
            # Player bullet with glow
            pygame.draw.rect(surface, self.color,
                             (self.x - self.width // 2, self.y, self.width, self.height))
            pygame.draw.rect(surface, WHITE,
                             (self.x - self.width // 2, self.y, self.width, self.height // 3))

    def move(self):
        self.y += self.speed

    def is_off_screen(self):
        return self.y < -20 or self.y > HEIGHT + 20

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2)
        self.brightness = random.randint(150, 255)
        self.twinkle_speed = random.uniform(0.05, 0.2)
        self.twinkle_offset = random.uniform(0, 6.28)

    def update(self, current_time):
        twinkle = (sin(current_time * self.twinkle_speed + self.twinkle_offset) + 1) / 2
        self.current_brightness = int(self.brightness * twinkle)

    def draw(self, surface):
        color = (self.current_brightness, self.current_brightness, self.current_brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Game:
    def __init__(self):
        self.player = Player()
        self.aliens = []
        self.player_bullets = []
        self.alien_bullets = []
        self.particles = []
        self.powerups = []
        self.stars = [Star() for _ in range(100)]
        self.alien_move_timer = 0
        self.alien_move_delay = 500
        self.alien_shoot_timer = 0
        self.alien_shoot_delay = 2000
        self.wave = 1
        self.aliens_per_row = 8
        self.aliens_per_col = 3
        self.game_state = "menu"  # "menu", "playing", "paused", "game_over", "win"
        self.screen_shake = 0
        self.last_score = 0
        self.high_scores = self.load_high_scores()
        self.current_score_multiplier = 1
        self.multiplier_timer = 0
        self.create_wave()
        self.menu_selection = 0
        self.menu_options = ["Start Game", "How to Play", "High Scores", "Quit"]
        self.game_start_time = 0
        self.total_play_time = 0

    def load_high_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"scores": []}
        return {"scores": []}

    def save_high_score(self, score, wave):
        if score > 0:
            self.high_scores["scores"].append({
                "score": score,
                "wave": wave,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "play_time": self.total_play_time
            })
            self.high_scores["scores"].sort(key=lambda x: x["score"], reverse=True)
            self.high_scores["scores"] = self.high_scores["scores"][:10]  # Keep top 10

            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f, indent=2)

    def create_wave(self):
        self.aliens = []
        rows = min(3 + self.wave // 2, 6)
        cols = min(8 + self.wave // 3, 12)

        start_x = 80
        start_y = 50

        for row in range(rows):
            for col in range(cols):
                alien_type = (row + self.wave) % 4
                x = start_x + col * 50
                y = start_y + row * 45
                self.aliens.append(Alien(x, y, alien_type, self.wave))

        # Adjust alien speed based on wave
        for alien in self.aliens:
            alien.speed = alien.base_speed * (1 + self.wave * 0.15)
            alien.move_delay = max(100, 500 - (self.wave * 40))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:  # Start Game
                            self.game_state = "playing"
                            self.game_start_time = pygame.time.get_ticks()
                        elif self.menu_selection == 1:  # How to Play
                            self.game_state = "help"
                        elif self.menu_selection == 2:  # High Scores
                            self.game_state = "high_scores"
                        elif self.menu_selection == 3:  # Quit
                            pygame.quit()
                            sys.exit()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elif self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        bullets = self.player.shoot()
                        if bullets:
                            self.player_bullets.extend(bullets)
                    elif event.key == pygame.K_p:
                        self.game_state = "paused"
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"

                elif self.game_state == "paused":
                    if event.key == pygame.K_p:
                        self.game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"

                elif self.game_state in ["game_over", "win", "help", "high_scores"]:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"

                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.__init__()  # Reset game

    def update(self):
        current_time = pygame.time.get_ticks()

        # Update stars
        for star in self.stars:
            star.update(current_time)

        if self.game_state != "playing":
            return

        # Update total play time
        self.total_play_time = (current_time - self.game_start_time) // 1000

        # Update player
        self.player.update(current_time)

        # Handle player movement (continuous)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1)

        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.player_bullets.remove(bullet)
                continue

            # Check collision with aliens
            bullet_rect = bullet.get_rect()
            for alien in self.aliens[:]:
                if bullet_rect.colliderect(alien.get_rect()):
                    alien.health -= 1
                    if alien.health <= 0:
                        # Create explosion particles
                        for _ in range(15):
                            self.particles.append(Particle(
                                alien.x + alien.width // 2,
                                alien.y + alien.height // 2,
                                alien.color
                            ))

                        # Update score with multiplier
                        base_score = alien.score_value
                        if self.player.combo > 1:
                            base_score *= self.player.combo
                        self.player.score += base_score * self.current_score_multiplier

                        # Update combo
                        self.player.combo += 1
                        self.player.last_kill_time = current_time
                        self.multiplier_timer = current_time

                        # Chance to spawn power-up (increases with combo)
                        powerup_chance = 0.15 + min(0.1, self.player.combo * 0.02)
                        if random.random() < powerup_chance:
                            power_type = random.choice(list(PowerUp.TYPES.keys()))
                            self.powerups.append(PowerUp(alien.x, alien.y, power_type))

                        self.aliens.remove(alien)
                        self.player_bullets.remove(bullet)
                        self.screen_shake = min(10, 3 + self.player.combo // 5)
                        break
                    else:
                        # Alien damaged but not destroyed
                        self.player_bullets.remove(bullet)
                        break

        # Update alien movement
        if current_time - self.alien_move_timer > self.alien_move_delay:
            self.alien_move_timer = current_time
            move_down = False

            # Move all aliens
            for alien in self.aliens:
                if alien.move(self.aliens, current_time):
                    move_down = True

            # Increase speed as aliens decrease
            if len(self.aliens) > 0:
                self.alien_move_delay = max(100, 500 - (self.wave * 50))

        # Alien shooting
        if current_time - self.alien_shoot_timer > self.alien_shoot_delay and self.aliens:
            self.alien_shoot_timer = current_time
            # Weighted random: higher chance for aliens at bottom rows
            weights = []
            for alien in self.aliens:
                weight = 1 + (alien.y / HEIGHT) * 3  # Bottom aliens 4x more likely
                weights.append(weight)

            shooting_alien = random.choices(self.aliens, weights=weights, k=1)[0]
            if shooting_alien.can_shoot(current_time):
                self.alien_bullets.append(Bullet(
                    shooting_alien.x + shooting_alien.width // 2,
                    shooting_alien.y + shooting_alien.height,
                    5,  # speed - positive for downward movement
                    RED,  # color
                    True  # is_alien flag
                ))
                self.alien_shoot_delay = max(500, 2000 - (self.wave * 200))

        # Update alien bullets
        for bullet in self.alien_bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.alien_bullets.remove(bullet)
                continue

            # Check collision with player
            if not self.player.shield_active and bullet.get_rect().colliderect(self.player.get_rect()):
                self.alien_bullets.remove(bullet)
                if self.player.take_damage():
                    self.screen_shake = 15
                    self.player.combo = 0
                    if self.player.lives <= 0:
                        self.game_state = "game_over"
                        self.save_high_score(self.player.score, self.wave)

        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.y > HEIGHT:
                self.powerups.remove(powerup)
                continue

            # Check collision with player
            if powerup.get_rect().colliderect(self.player.get_rect()):
                self.powerups.remove(powerup)
                self.player.activate_powerup(powerup.type)

                # Special handling for bomb
                if powerup.type == 'bomb':
                    # Destroy all aliens on screen
                    for alien in self.aliens[:]:
                        for _ in range(20):
                            self.particles.append(Particle(
                                alien.x + alien.width // 2,
                                alien.y + alien.height // 2,
                                alien.color
                            ))
                        self.player.score += alien.score_value * 2
                        self.aliens.remove(alien)
                    self.screen_shake = 30

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

        # Check magnet powerup
        if self.player.magnet_active:
            magnet_rect = self.player.get_magnet_rect()
            for powerup in self.powerups[:]:
                if magnet_rect and magnet_rect.colliderect(powerup.get_rect()):
                    # Pull powerup toward player
                    dx = self.player.x + self.player.width // 2 - powerup.x
                    dy = self.player.y - powerup.y
                    dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
                    powerup.x += dx / dist * 5
                    powerup.y += dy / dist * 5

        # Check if aliens reached bottom
        for alien in self.aliens:
            if alien.y + alien.height >= self.player.y - 30:
                self.game_state = "game_over"
                self.save_high_score(self.player.score, self.wave)
                break

        # Check if all aliens are destroyed
        if not self.aliens:
            self.wave += 1
            self.create_wave()
            # Bonus points for completing wave
            wave_bonus = 100 * self.wave
            self.player.score += wave_bonus
            self.current_score_multiplier = min(3, 1 + self.wave // 3)
            self.multiplier_timer = current_time

            # Increase player speed slightly each wave
            self.player.base_speed += 0.2

        # Update score multiplier
        if current_time - self.multiplier_timer > 10000:  # 10 second multiplier duration
            self.current_score_multiplier = 1

        # Decay screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self):
        # Fill background
        screen.fill(BLACK)

        # Draw stars
        for star in self.stars:
            star.draw(screen)

        # Create game surface for screen shake
        game_surface = pygame.Surface((WIDTH, HEIGHT))
        game_surface.fill(BLACK)

        # Draw stars on game surface
        for star in self.stars:
            star.draw(game_surface)

        # Draw game objects on game surface
        self.player.draw(game_surface)

        for alien in self.aliens:
            alien.draw(game_surface)

        for bullet in self.player_bullets:
            bullet.draw(game_surface)

        for bullet in self.alien_bullets:
            bullet.draw(game_surface)

        for powerup in self.powerups:
            powerup.draw(game_surface)

        for particle in self.particles:
            particle.draw(game_surface)

        # Apply screen shake and blit game surface
        if self.screen_shake > 0:
            shake_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_y = random.randint(-self.screen_shake, self.screen_shake)
            screen.blit(game_surface, (shake_x, shake_y))
        else:
            screen.blit(game_surface, (0, 0))

        # Draw UI (not affected by screen shake)
        self.draw_ui()

        # Draw game state overlays
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "paused":
            self.draw_pause()
        elif self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "win":
            self.draw_win()
        elif self.game_state == "help":
            self.draw_help()
        elif self.game_state == "high_scores":
            self.draw_high_scores()

    def draw_ui(self):
        # Score with multiplier indicator
        score_color = YELLOW if self.current_score_multiplier > 1 else WHITE
        score_text = font_score.render(f"SCORE: {self.player.score:06d}", True, score_color)
        screen.blit(score_text, (10, 10))

        if self.current_score_multiplier > 1:
            multiplier_text = font_small.render(f"x{self.current_score_multiplier}", True, ORANGE)
            screen.blit(multiplier_text, (score_text.get_width() + 20, 15))

        # Lives
        lives_text = font_small.render(f"LIVES: {self.player.lives}", True, GREEN)
        screen.blit(lives_text, (10, 45))

        # Wave
        wave_text = font_small.render(f"WAVE: {self.wave}", True, CYAN)
        screen.blit(wave_text, (10, 80))

        # Combo
        if self.player.combo > 1:
            combo_color = PINK if self.player.combo > 10 else ORANGE
            combo_text = font_small.render(f"COMBO x{self.player.combo}", True, combo_color)
            screen.blit(combo_text, (WIDTH - combo_text.get_width() - 10, 10))

        # Active powerups
        y_offset = 120
        for powerup_name, powerup_data in self.player.powerups.items():
            if powerup_data['active']:
                remaining = powerup_data['timer'] // 1000 + 1
                powerup_info = PowerUp.TYPES[powerup_name]
                powerup_text = font_small.render(f"{powerup_info['name']}: {remaining}s", True, powerup_info['color'])
                screen.blit(powerup_text, (10, y_offset))
                y_offset += 25

        # Shield indicator
        if self.player.shield_active:
            shield_text = font_small.render("🛡 ACTIVE", True, BLUE)
            screen.blit(shield_text, (WIDTH - shield_text.get_width() - 10, 45))

        # Play time
        time_text = font_small.render(f"TIME: {self.total_play_time}s", True, WHITE)
        screen.blit(time_text, (WIDTH - time_text.get_width() - 10, 80))

        # Controls hint
        if self.game_state == "playing":
            controls = "SPACE:Shoot  ←→:Move  P:Pause  ESC:Menu"
            controls_text = font_small.render(controls, True, (150, 150, 150))
            screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 30))

    def draw_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title = font_large.render("SPACE INVADERS", True, GREEN)
        title2 = font_large.render("DELUXE", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        screen.blit(title2, (WIDTH // 2 - title2.get_width() // 2, 160))

        for i, option in enumerate(self.menu_options):
            color = GREEN if i == self.menu_selection else WHITE
            option_text = font_medium.render(option, True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 280 + i * 50))

            if i == self.menu_selection:
                pygame.draw.rect(screen, GREEN,
                                 (WIDTH // 2 - option_text.get_width() // 2 - 20,
                                  280 + i * 50 - 5,
                                  option_text.get_width() + 40,
                                  option_text.get_height() + 10), 2)

        # High score display
        if self.high_scores["scores"]:
            high_score = self.high_scores["scores"][0]
            high_text = font_small.render(f"HIGH SCORE: {high_score['score']}", True, YELLOW)
            screen.blit(high_text, (WIDTH // 2 - high_text.get_width() // 2, 500))

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pause_text = font_large.render("PAUSED", True, YELLOW)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))

        continue_text = font_medium.render("Press P to continue", True, WHITE)
        screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 30))

        menu_text = font_small.render("Press ESC for menu", True, WHITE)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 70))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))

        score_text = font_medium.render(f"Final Score: {self.player.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 10))

        wave_text = font_medium.render(f"You made it to wave {self.wave}", True, CYAN)
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, HEIGHT // 2 + 30))

        time_text = font_small.render(f"Total Time: {self.total_play_time} seconds", True, WHITE)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 70))

        restart_text = font_medium.render("Press R to restart or ESC for menu", True, GREEN)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 120))

    def draw_win(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 50, 0, 220))
        screen.blit(overlay, (0, 0))

        win_text = font_large.render("MISSION COMPLETE!", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 80))

        score_text = font_medium.render(f"Final Score: {self.player.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 10))

        wave_text = font_medium.render(f"You conquered wave {self.wave}", True, CYAN)
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, HEIGHT // 2 + 30))

        time_text = font_small.render(f"Total Time: {self.total_play_time} seconds", True, WHITE)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 70))

        restart_text = font_medium.render("Press R to restart or ESC for menu", True, GREEN)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 120))

    def draw_help(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        help_title = font_medium.render("HOW TO PLAY", True, GREEN)
        screen.blit(help_title, (WIDTH // 2 - help_title.get_width() // 2, 50))

        instructions = [
            "← → or A D : Move your spaceship",
            "SPACE : Shoot lasers",
            "P : Pause game",
            "ESC : Return to menu",
            "",
            "OBJECTIVE:",
            "• Destroy all aliens before they reach you",
            "• Collect power-ups for special abilities",
            "• Build combos by killing aliens quickly",
            "• Survive as many waves as possible",
            "",
            "POWER-UPS:",
            "⚡ RAPID FIRE : Shoots much faster",
            "✦ TRIPLE SHOT : Fires 3 bullets at once",
            "🛡 SHIELD : Temporary invincibility",
            "⚡ SPEED BOOST : Move faster",
            "🧲 SCORE MAGNET : Attracts power-ups",
            "💣 BOMB : Destroys all aliens on screen",
            "",
            "SCORING:",
            "• Basic aliens: 10-50 points",
            "• Combo multiplier: Up to 3x",
            "• Wave completion bonus",
            "• Power-up collection bonus"
        ]

        y = 120
        for line in instructions:
            if line.startswith("•") or line.startswith("OBJECTIVE:") or line.startswith(
                    "POWER-UPS:") or line.startswith("SCORING:"):
                color = YELLOW
                text = font_small.render(line, True, color)
            elif line == "":
                y += 10
                continue
            else:
                color = WHITE
                text = font_small.render(line, True, color)

            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 25

        back_text = font_medium.render("Press ESC or RETURN to go back", True, GREEN)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 80))

    def draw_high_scores(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        title = font_medium.render("HIGH SCORES", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        scores = self.high_scores["scores"][:10]
        y = 120
        for i, score_data in enumerate(scores):
            rank_text = font_small.render(f"{i + 1}.", True, CYAN)
            score_text = font_small.render(f"Score: {score_data['score']:06d}", True, WHITE)
            wave_text = font_small.render(f"Wave: {score_data['wave']}", True, GREEN)
            date_text = font_small.render(score_data['date'], True, (150, 150, 150))
            time_text = font_small.render(f"Time: {score_data['play_time']}s", True, (150, 150, 150))

            screen.blit(rank_text, (100, y))
            screen.blit(score_text, (150, y))
            screen.blit(wave_text, (350, y))
            screen.blit(date_text, (500, y))
            screen.blit(time_text, (650, y))
            y += 30

        if not scores:
            no_scores = font_medium.render("No scores yet! Play a game.", True, WHITE)
            screen.blit(no_scores, (WIDTH // 2 - no_scores.get_width() // 2, HEIGHT // 2))

        back_text = font_medium.render("Press ESC or RETURN to go back", True, GREEN)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 80))


def main():
    # Import math for star twinkling
    import math

    game = Game()

    while True:
        game.handle_events()
        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
