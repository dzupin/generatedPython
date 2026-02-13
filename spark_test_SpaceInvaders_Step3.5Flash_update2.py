# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1  --model  /AI/models/stepfun-ai_Step-3.5-Flash-IQ4_XS-00001-of-00003.gguf

import pygame
import random
import sys
import json
import os
from datetime import datetime
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 70, 200)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - Enhanced")
clock = pygame.time.Clock()

# Load fonts
font_large = pygame.font.SysFont(None, 56)
font_medium = pygame.font.SysFont(None, 42)
font_small = pygame.font.SysFont(None, 28)
font_tiny = pygame.font.SysFont(None, 20)

class Particle:
    """Visual effect particles for explosions"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.randint(20, 40)
        self.gravity = 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size = max(0.5, self.size - 0.05)

    def draw(self):
        if self.life > 0:
            alpha = int(255 * (self.life / 40))
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (self.x - self.size, self.y - self.size))

    def is_alive(self):
        return self.life > 0

class FloatingText:
    """Floating score text effect"""

    def __init__(self, x, y, text, color=YELLOW, size=20):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 60
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.life -= 1

    def draw(self):
        if self.life > 0:
            alpha = int(255 * (self.life / 60))
            text_surf = font_tiny.render(self.text, True, self.color)
            text_surf.set_alpha(alpha)
            screen.blit(text_surf, (self.x, self.y))

    def is_alive(self):
        return self.life > 0

class PowerUp:
    """Collectible power-ups"""
    TYPES = {
        'rapid': {'color': CYAN, 'symbol': 'R', 'duration': 600, 'score': 50},
        'extra_life': {'color': GREEN, 'symbol': '♥', 'duration': 0, 'score': 100},
        'shield': {'color': BLUE, 'symbol': 'S', 'duration': 450, 'score': 75},
        'slow': {'color': ORANGE, 'symbol': '⊘', 'duration': 400, 'score': 60}
    }

    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.speed = 2
        self.wobble = random.uniform(0, 6.28)
        self.wobble_speed = random.uniform(0.05, 0.1)
        self.info = self.TYPES[power_type]

    def update(self):
        self.y += self.speed
        self.wobble += self.wobble_speed

    def draw(self):
        wobble_x = math.sin(self.wobble) * 5
        rect = pygame.Rect(self.x + wobble_x - 12, self.y - 12, 24, 24)
        pygame.draw.rect(screen, self.info['color'], rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=4)

        symbol = font_small.render(self.info['symbol'], True, WHITE)
        screen.blit(symbol, (self.x + wobble_x - symbol.get_width() // 2,
                           self.y - symbol.get_height() // 2))

    def get_rect(self):
        wobble_x = math.sin(self.wobble) * 5
        return pygame.Rect(self.x + wobble_x - 10, self.y - 10, 20, 20)

class Achievement:
    """Achievement system"""
    ACHIEVEMENTS = {
        'first_kill': {'name': 'First Blood', 'desc': 'Destroy your first alien', 'unlocked': False},
        'survivor': {'name': 'Survivor', 'desc': 'Reach 5000 points', 'unlocked': False, 'score': 5000},
        'sharpshooter': {'name': 'Sharpshooter', 'desc': 'Get 10 consecutive hits', 'unlocked': False},
        'destroyer': {'name': 'Destroyer', 'desc': 'Destroy 50 aliens', 'unlocked': False, 'count': 50},
        'speed_run': {'name': 'Speed Runner', 'desc': 'Win a level in under 60 seconds', 'unlocked': False}
    }

    def __init__(self):
        self.unlocked = []
        self.load_achievements()

    def load_achievements(self):
        try:
            with open('achievements.json', 'r') as f:
                data = json.load(f)
                for ach, info in data.items():
                    if info.get('unlocked', False):
                        self.unlocked.append(ach)
        except:
            pass

    def save_achievements(self):
        data = {}
        for ach, info in self.ACHIEVEMENTS.items():
            data[ach] = {'unlocked': ach in self.unlocked}
        with open('achievements.json', 'w') as f:
            json.dump(data, f)

    def check(self, condition, value=None):
        newly_unlocked = []
        for ach, info in self.ACHIEVEMENTS.items():
            if ach not in self.unlocked:
                if condition == 'kill' and ach == 'first_kill':
                    self.unlocked.append(ach)
                    newly_unlocked.append(ach)
                elif condition == 'score' and ach == 'survivor' and value >= info['score']:
                    self.unlocked.append(ach)
                    newly_unlocked.append(ach)
                elif condition == 'consecutive' and ach == 'sharpshooter' and value >= 10:
                    self.unlocked.append(ach)
                    newly_unlocked.append(ach)
                elif condition == 'destroy' and ach == 'destroyer' and value >= info['count']:
                    self.unlocked.append(ach)
                    newly_unlocked.append(ach)
        if newly_unlocked:
            self.save_achievements()
        return newly_unlocked

class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = 5
        self.base_speed = 5
        self.color = GREEN
        self.lives = 3
        self.score = 0
        self.bullets = []
        self.cooldown = 0
        self.base_cooldown = 15
        self.cooldown_time = 15
        self.power_timer = 0
        self.active_power = None
        self.shield_active = 0
        self.consecutive_hits = 0
        self.combo_timer = 0
        self.combo_multiplier = 1

    def draw(self):
        # Draw shield if active
        if self.shield_active > 0:
            shield_rect = pygame.Rect(self.x - 5, self.y - 5,
                                     self.width + 10, self.height + 10)
            pygame.draw.ellipse(screen, (*BLUE, 100), shield_rect)

        # Draw player ship with engine glow
        points = [
            (self.x + self.width // 2, self.y - 10),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)

        # Engine glow
        if self.active_power == 'rapid':
            glow_color = CYAN
        else:
            glow_color = YELLOW
        pygame.draw.polygon(screen, glow_color, [
            (self.x + self.width // 2 - 5, self.y + self.height - 5),
            (self.x + self.width // 2 + 5, self.y + self.height - 5),
            (self.x + self.width // 2, self.y + self.height + 10)
        ])

        # Draw bullets with trail effect
        for bullet in self.bullets:
            if self.active_power == 'rapid':
                pygame.draw.rect(screen, CYAN, (bullet[0] - 1, bullet[1], 6, 12))
            else:
                pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], 4, 10))

    def move(self, keys):
        speed = self.speed
        if self.active_power == 'slow':
            speed *= 0.6

        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += speed

        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Update power timer
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer == 0:
                self.deactivate_power()

        # Update shield
        if self.shield_active > 0:
            self.shield_active -= 1

        # Update combo
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_multiplier = 1

    def shoot(self):
        if self.cooldown == 0:
            self.bullets.append([self.x + self.width // 2 - 2, self.y])
            self.cooldown = self.cooldown_time

    def activate_power(self, power_type):
        if power_type == 'rapid':
            self.cooldown_time = 5
            self.active_power = 'rapid'
            self.power_timer = PowerUp.TYPES['rapid']['duration']
        elif power_type == 'extra_life':
            self.lives += 1
            return True
        elif power_type == 'shield':
            self.shield_active = 300
            self.active_power = 'shield'
            self.power_timer = PowerUp.TYPES['shield']['duration']
        elif power_type == 'slow':
            self.active_power = 'slow'
            self.power_timer = PowerUp.TYPES['slow']['duration']
        return False

    def deactivate_power(self):
        self.active_power = None
        self.cooldown_time = self.base_cooldown

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] -= 7
            if bullet[1] < 0:
                self.bullets.remove(bullet)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def hit(self):
        if self.shield_active > 0:
            self.shield_active = 0
            return False
        self.lives -= 1
        return True

class Alien:
    def __init__(self, x, y, alien_type):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.alien_type = alien_type
        self.color = self.get_color()
        self.bullets = []
        self.shoot_chance = 0.0005
        self.animation_frame = 0
        self.animation_speed = 30

    def get_color(self):
        colors = [PURPLE, BLUE, RED]
        return colors[self.alien_type]

    def draw(self):
        self.animation_frame = (self.animation_frame + 1) % self.animation_speed

        if self.alien_type == 0:
            # Animated crab alien
            leg_offset = 5 if self.animation_frame < 15 else 0
            pygame.draw.rect(screen, self.color,
                             (self.x, self.y + leg_offset, self.width, self.height - leg_offset))
            pygame.draw.rect(screen, BLACK,
                             (self.x + 10, self.y + 5 + leg_offset, 5, 5))
            pygame.draw.rect(screen, BLACK,
                             (self.x + self.width - 15, self.y + 5 + leg_offset, 5, 5))
        elif self.alien_type == 1:
            # Animated squid alien
            points = [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height),
                (self.x + self.width, self.y + self.height // 2)
            ]
            pygame.draw.polygon(screen, self.color, points)
        else:  # type 2
            # Animated octopus alien
            tentacle_offset = 3 if self.animation_frame < 15 else 0
            pygame.draw.rect(screen, self.color,
                             (self.x + 5, self.y, self.width - 10, self.height))
            pygame.draw.rect(screen, BLACK,
                             (self.x + 10, self.y + 10, 5, 5))
            pygame.draw.rect(screen, BLACK,
                             (self.x + self.width - 15, self.y + 10, 5, 5))
            pygame.draw.rect(screen, self.color,
                             (self.x + 8, self.y + self.height - 5 - tentacle_offset, 6, 5 + tentacle_offset))
            pygame.draw.rect(screen, self.color,
                             (self.x + self.width - 14, self.y + self.height - 5 - tentacle_offset, 6,
                              5 + tentacle_offset))

    def update(self, dx, dy):
        self.x += dx
        self.y += dy

        # Increase shooting chance based on remaining aliens
        base_chance = self.shoot_chance
        if len(alien_grid.aliens) < 20:
            base_chance *= 2
        if len(alien_grid.aliens) < 10:
            base_chance *= 3

        if random.random() < base_chance:
            self.bullets.append([self.x + self.width // 2 - 2, self.y + self.height])

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] += 4
            if bullet[1] > SCREEN_HEIGHT:
                self.bullets.remove(bullet)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class AlienGrid:
    def __init__(self):
        self.level = 1
        self.aliens = []
        self.direction = 1
        self.move_speed = 1
        self.move_down_distance = 20
        self.base_speed = 1
        self.create_grid()

    def create_grid(self):
        self.aliens.clear()
        rows = 4 + min(self.level // 2, 2)  # More rows as levels progress
        cols = 8 + min(self.level // 3, 3)  # More columns as levels progress

        spacing_x = 60
        spacing_y = 50
        start_x = 50
        start_y = 50

        for row in range(rows):
            for col in range(cols):
                alien_type = min(row // 2, 2)
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.aliens.append(Alien(x, y, alien_type))

    def next_level(self):
        self.level += 1
        self.base_speed = min(1 + self.level * 0.2, 4)
        self.create_grid()

    def draw(self):
        for alien in self.aliens:
            alien.draw()
            for bullet in alien.bullets:
                pygame.draw.rect(screen, RED,
                                 (bullet[0], bullet[1], 4, 10))

    def update(self):
        # Check if any alien hits the edge
        hit_edge = False
        for alien in self.aliens:
            if (alien.x <= 0 and self.direction == -1) or \
                    (alien.x + alien.width >= SCREEN_WIDTH and self.direction == 1):
                hit_edge = True
                break

        # Move aliens
        dx = self.move_speed * self.direction
        dy = 0

        if hit_edge:
            self.direction *= -1
            dy = self.move_down_distance

        for alien in self.aliens:
            alien.update(dx, dy)
            alien.update_bullets()

        # Increase speed as aliens are destroyed
        alien_count = len(self.aliens)
        if alien_count == 0:
            return 'level_complete'
        elif alien_count < 5:
            self.move_speed = self.base_speed * 3
        elif alien_count < 10:
            self.move_speed = self.base_speed * 2
        elif alien_count < 20:
            self.move_speed = self.base_speed * 1.5
        else:
            self.move_speed = self.base_speed

        return 'playing'

    def get_aliens_rects(self):
        return [alien.get_rect() for alien in self.aliens]

    def remove_alien(self, alien):
        if alien in self.aliens:
            self.aliens.remove(alien)

class Barrier:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 40)
        self.health = 15
        self.blocks = []
        self.create_blocks()

    def create_blocks(self):
        block_size = 8
        for y in range(0, 40, block_size):
            for x in range(0, 80, block_size):
                # Create barrier with more complex pattern
                if (x < 15 or x > 65) or (y < 12) or (x > 25 and x < 55 and y > 20):
                    continue
                self.blocks.append(pygame.Rect(
                    self.rect.x + x,
                    self.rect.y + y,
                    block_size, block_size
                ))

    def draw(self):
        for block in self.blocks[:]:
            # Draw block with gradient based on health
            health_ratio = len(self.blocks) / 60
            color_intensity = int(100 + 155 * health_ratio)
            block_color = (50, color_intensity, 50)
            pygame.draw.rect(screen, block_color, block)

            # Add subtle highlight
            if health_ratio > 0.5:
                pygame.draw.rect(screen, (100, 255, 100),
                                 (block.x + 1, block.y + 1, block.width - 2, 2))

    def hit(self, x, y):
        for block in self.blocks[:]:
            if block.collidepoint(x, y):
                self.blocks.remove(block)
                self.health -= 1
                return True
        return False

    def is_destroyed(self):
        return len(self.blocks) == 0

def create_barriers():
    barriers = []
    for i in range(4):
        x = 100 + i * 150
        barriers.append(Barrier(x, SCREEN_HEIGHT - 150))
    return barriers

def check_collisions(player, alien_grid, barriers, particles, floating_texts, achievements, game_start_time):
    collision_occurred = False
    points_multiplier = player.combo_multiplier

    # Player bullets vs aliens
    for bullet in player.bullets[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
        for alien in alien_grid.aliens[:]:
            if bullet_rect.colliderect(alien.get_rect()):
                if bullet in player.bullets:
                    player.bullets.remove(bullet)

                # Create explosion particles
                for _ in range(15):
                    particles.append(Particle(
                        alien.x + alien.width // 2,
                        alien.y + alien.height // 2,
                        alien.color
                    ))

                # Add floating score text
                base_points = 10 * (3 - alien.alien_type)
                total_points = base_points * points_multiplier
                floating_texts.append(FloatingText(
                    alien.x + alien.width // 2,
                    alien.y,
                    f"+{total_points}",
                    YELLOW if points_multiplier == 1 else ORANGE
                ))

                alien_grid.remove_alien(alien)
                player.score += total_points
                player.consecutive_hits += 1
                player.combo_timer = 120

                # Check achievements
                new_achievements = achievements.check('kill')
                new_achievements += achievements.check('destroy', len(alien_grid.aliens))
                new_achievements += achievements.check('score', player.score)
                if player.consecutive_hits >= 10:
                    new_achievements += achievements.check('consecutive', player.consecutive_hits)

                collision_occurred = True
                break

    # Alien bullets vs player
    for alien in alien_grid.aliens:
        for bullet in alien.bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
            if bullet_rect.colliderect(player.get_rect()):
                alien.bullets.remove(bullet)
                if player.hit():
                    collision_occurred = True
                    player.consecutive_hits = 0
                    player.combo_multiplier = 1

                    # Create hit particles
                    for _ in range(20):
                        particles.append(Particle(
                            player.x + player.width // 2,
                            player.y + player.height // 2,
                            RED
                        ))

    # Aliens vs player
    for alien in alien_grid.aliens:
        if alien.get_rect().colliderect(player.get_rect()):
            if player.hit():
                collision_occurred = True
                player.consecutive_hits = 0
                player.combo_multiplier = 1

                for _ in range(20):
                    particles.append(Particle(
                        player.x + player.width // 2,
                        player.y + player.height // 2,
                        RED
                    ))

    # Aliens vs barriers
    for barrier in barriers:
        for alien in alien_grid.aliens:
            if alien.get_rect().colliderect(barrier.rect):
                # Damage barrier where alien touches
                for x in range(alien.x, alien.x + alien.width):
                    for y in range(alien.y, alien.y + alien.height):
                        barrier.hit(x, y)

    # Player bullets vs barriers
    for bullet in player.bullets[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
        for barrier in barriers:
            for block in barrier.blocks[:]:
                if bullet_rect.colliderect(block):
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    barrier.hit(block.centerx, block.centery)

                    # Small particle effect
                    for _ in range(3):
                        particles.append(Particle(block.centerx, block.centery, GREEN))
                    break

    # Alien bullets vs barriers
    for alien in alien_grid.aliens:
        for bullet in alien.bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
            for barrier in barriers:
                for block in barrier.blocks[:]:
                    if bullet_rect.colliderect(block):
                        if bullet in alien.bullets:
                            alien.bullets.remove(bullet)
                        barrier.hit(block.centerx, block.centery)

                        for _ in range(3):
                            particles.append(Particle(block.centerx, block.centery, RED))
                        break

    return collision_occurred

def draw_stars():
    """Draw animated starfield background"""
    current_time = pygame.time.get_ticks() / 1000
    for i in range(100):
        x = (i * 13) % SCREEN_WIDTH
        y = (i * 7) % SCREEN_HEIGHT
        brightness = 100 + 155 * abs(math.sin(current_time + i * 0.1))
        color = (brightness, brightness, brightness)
        size = 1 if i % 3 != 0 else 2
        pygame.draw.circle(screen, color, (x, y), size)

def draw_ui(player, achievements, game_start_time, level):
    # Draw score with combo indicator
    score_color = ORANGE if player.combo_multiplier > 1 else WHITE
    score_text = font_medium.render(f"SCORE: {player.score}", True, score_color)
    screen.blit(score_text, (10, 10))

    # Draw combo
    if player.combo_multiplier > 1:
        combo_text = font_small.render(f"COMBO x{player.combo_multiplier}", True, ORANGE)
        screen.blit(combo_text, (10, 50))

    # Draw lives with hearts
    lives_text = font_small.render("LIVES:", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - 200, 10))
    for i in range(player.lives):
        heart = font_small.render("♥", True, RED)
        screen.blit(heart, (SCREEN_WIDTH - 120 + i * 25, 10))

    # Draw active power-up
    if player.active_power:
        power_info = PowerUp.TYPES[player.active_power]
        power_text = font_small.render(f"{power_info['symbol']}{power_info['duration'] // 60}s",
                                       True, power_info['color'])
        screen.blit(power_text, (SCREEN_WIDTH // 2 - power_text.get_width() // 2, 10))

    # Draw level
    level_text = font_small.render(f"LEVEL: {level}", True, CYAN)
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT - 30))

    # Draw achievements unlocked (small icons)
    ach_x = SCREEN_WIDTH - 200
    ach_y = SCREEN_HEIGHT - 30
    for i, ach in enumerate(achievements.unlocked[-3:]):  # Show last 3 unlocked
        if i < 3:
            pygame.draw.rect(screen, GREEN, (ach_x + i * 30, ach_y, 20, 20), 2)

def draw_game_over(screen, player, game_won, achievements, level):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    if game_won:
        title = font_large.render("MISSION COMPLETE!", True, GREEN)
    else:
        title = font_large.render("GAME OVER", True, RED)

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

    score_text = font_medium.render(f"Final Score: {player.score}", True, YELLOW)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))

    level_text = font_medium.render(f"Reached Level: {level}", True, CYAN)
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 270))

    # Show unlocked achievements
    if achievements.unlocked:
        ach_title = font_small.render("Achievements Unlocked:", True, GREEN)
        screen.blit(ach_title, (SCREEN_WIDTH // 2 - ach_title.get_width() // 2, 320))

        for i, ach_key in enumerate(achievements.unlocked[-3:]):  # Show last 3
            if i < 3:
                ach_info = achievements.ACHIEVEMENTS[ach_key]
                ach_text = font_tiny.render(f"• {ach_info['name']}", True, YELLOW)
                screen.blit(ach_text, (SCREEN_WIDTH // 2 - 150, 360 + i * 25))

    restart_text = font_small.render("Press R to restart | Q to quit | M for menu", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 480))

def draw_start_screen():
    screen.fill(BLACK)
    draw_stars()

    title = font_large.render("SPACE INVADERS", True, GREEN)
    subtitle = font_medium.render("Enhanced Edition", True, CYAN)

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 210))

    instructions = [
        "CONTROLS:",
        "← → : Move Ship",
        "SPACE : Shoot",
        "R : Restart (during game)",
        "Q : Quit",
        "",
        "FEATURES:",
        "• Power-ups (collect for bonuses)",
        "• Combo system (consecutive kills)",
        "• Progressive difficulty",
        "• Achievement system",
        "• Visual particle effects",
        "",
        "Press SPACE to start"
    ]

    for i, line in enumerate(instructions):
        color = YELLOW if "Press SPACE" in line else WHITE
        text = font_small.render(line, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 280 + i * 30))

def main():
    player = Player()
    alien_grid = AlienGrid()
    barriers = create_barriers()
    particles = []
    floating_texts = []
    powerups = []
    achievements = Achievement()

    game_state = "start"
    game_over = False
    game_won = False
    level = 1
    game_start_time = 0
    level_start_time = 0

    # Load high score
    try:
        with open('highscore.txt', 'r') as f:
            high_score = int(f.read())
    except:
        high_score = 0

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "start":
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"
                        game_start_time = pygame.time.get_ticks()
                        level_start_time = pygame.time.get_ticks()
                elif game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        player.shoot()
                    if event.key == pygame.K_r:
                        # Reset current level
                        player = Player()
                        alien_grid = AlienGrid()
                        barriers = create_barriers()
                        particles.clear()
                        floating_texts.clear()
                        powerups.clear()
                        level_start_time = pygame.time.get_ticks()
                elif game_state in ["game_over", "level_complete"]:
                    if event.key == pygame.K_r:
                        # Full restart
                        player = Player()
                        alien_grid = AlienGrid()
                        barriers = create_barriers()
                        particles.clear()
                        floating_texts.clear()
                        powerups.clear()
                        level = 1
                        game_state = "playing"
                        game_start_time = pygame.time.get_ticks()
                        level_start_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_m and game_state == "level_complete":
                        game_state = "playing"
                        level += 1
                        alien_grid.next_level()
                        player.x = SCREEN_WIDTH // 2 - player.width // 2
                        barriers = create_barriers()
                        level_start_time = pygame.time.get_ticks()

        if game_state == "playing":
            # Player movement
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update_bullets()

            # Alien movement
            status = alien_grid.update()
            if status == 'level_complete':
                game_state = "level_complete"

            # Update power-ups
            for powerup in powerups[:]:
                powerup.update()
                if powerup.y > SCREEN_HEIGHT:
                    powerups.remove(powerup)
                elif powerup.get_rect().colliderect(player.get_rect()):
                    if powerup.type == 'extra_life':
                        if player.activate_power('extra_life'):
                            floating_texts.append(FloatingText(
                                player.x, player.y - 30, "+1 LIFE", GREEN, 24
                            ))
                    else:
                        player.activate_power(powerup.type)
                        floating_texts.append(FloatingText(
                            player.x, player.y - 30,
                            PowerUp.TYPES[powerup.type]['symbol'],
                            PowerUp.TYPES[powerup.type]['color'], 24
                        ))
                    powerups.remove(powerup)

            # Check collisions
            collision = check_collisions(player, alien_grid, barriers, particles,
                                        floating_texts, achievements, game_start_time)

            # Randomly spawn power-ups from destroyed aliens
            if collision and random.random() < 0.15:  # 15% chance on kill
                power_type = random.choice(['rapid', 'shield', 'slow'])
                powerups.append(PowerUp(
                    random.randint(50, SCREEN_WIDTH - 50),
                    50, power_type
                ))

            # Check lose conditions
            if player.lives <= 0:
                game_state = "game_over"
                game_won = False
                if player.score > high_score:
                    high_score = player.score
                    with open('highscore.txt', 'w') as f:
                        f.write(str(high_score))

            # Check win condition for current level
            if len(alien_grid.aliens) == 0:
                game_state = "level_complete"

            # Check if aliens reached bottom
            for alien in alien_grid.aliens:
                if alien.y + alien.height >= player.y:
                    game_state = "game_over"
                    game_won = False
                    break

            # Update particles
            for particle in particles[:]:
                particle.update()
                if not particle.is_alive():
                    particles.remove(particle)

            # Update floating texts
            for text in floating_texts[:]:
                text.update()
                if not text.is_alive():
                    floating_texts.remove(text)

            # Update combo
            if player.combo_timer > 0:
                if player.consecutive_hits >= 10:
                    player.combo_multiplier = min(3, 1 + (player.consecutive_hits - 10) // 5)
            else:
                player.consecutive_hits = 0
                player.combo_multiplier = 1

        # Drawing
        screen.fill(BLACK)
        draw_stars()

        if game_state == "start":
            draw_start_screen()
        else:
            # Draw game objects
            player.draw()
            alien_grid.draw()
            for barrier in barriers:
                barrier.draw()

            # Draw power-ups
            for powerup in powerups:
                powerup.draw()

            # Draw particles
            for particle in particles:
                particle.draw()

            # Draw floating texts
            for text in floating_texts:
                text.draw()

            # Draw UI
            draw_ui(player, achievements, game_start_time, alien_grid.level)

            # Draw level complete screen
            if game_state == "level_complete":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))

                level_text = font_large.render(f"LEVEL {level} COMPLETE!", True, GREEN)
                screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 200))

                cont_text = font_medium.render("Press M for next level or R to restart", True, YELLOW)
                screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, 300))

            # Draw game over screen
            if game_state == "game_over":
                draw_game_over(screen, player, game_won, achievements, alien_grid.level)

        # Draw high score in corner
        if game_state == "playing":
            high_score_text = font_tiny.render(f"HIGH SCORE: {high_score}", True, (200, 200, 200))
            screen.blit(high_score_text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
