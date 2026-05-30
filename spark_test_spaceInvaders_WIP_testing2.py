# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/GRM-Qwen2.6-27B-Opus-Heretic-Abliterated-MTP.Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

"""
Space Invaders - A complete implementation in Python using Pygame
No external asset files required. All graphics and sounds are generated programmatically.
"""

import pygame
import math
import json
import os
import random
import wave
import struct
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 50, 50)
COLOR_GREEN = (50, 255, 50)
COLOR_BLUE = (50, 50, 255)
COLOR_YELLOW = (255, 255, 50)
COLOR_ORANGE = (255, 165, 0)
COLOR_PURPLE = (200, 50, 255)
COLOR_CYAN = (0, 255, 255)
COLOR_DARK_BLUE = (10, 10, 60)

# File paths for saving game data
STATS_FILE = "space_invaders_stats.json"
HIGH_SCORE_FILE = "space_invaders_highscores.json"


# ============================================================================
# SOUND SYSTEM - Programmatic Sound Generation
# ============================================================================

class SoundGenerator:
    """Generates and plays sounds without external files."""

    @staticmethod
    def _generate_wave(frequency, duration, volume=0.3, sample_rate=44100,
                       wave_type='sine', fade_out=False):
        """Generate audio data as bytes."""
        num_samples = int(duration * sample_rate)
        buffer = bytearray()

        for i in range(num_samples):
            t = i / sample_rate
            time_factor = i / num_samples

            if wave_type == 'sine':
                sample = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                sample = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'sawtooth':
                sample = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            elif wave_type == 'noise':
                sample = random.random() * 2 - 1
            elif wave_type == 'triangle':
                sample = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.25)) - 1) - 1

            # Apply fade out
            if fade_out:
                sample *= (1 - time_factor)

            # Apply volume
            sample *= volume
            sample *= 32767  # Scale to 16-bit

            buffer.extend(struct.pack('<h', int(sample)))

        return buffer

    @staticmethod
    def _play_sound(buffer):
        """Play audio buffer through pygame mixer."""
        if pygame.mixer.get_init():
            sound = pygame.sound.make_sound(buffer)
            sound.play()

    @classmethod
    def play_shoot(cls):
        """Player shooting sound."""
        buf = cls._generate_wave(800, 0.1, volume=0.4, wave_type='sine', fade_out=True)
        cls._play_sound(buf)

    @classmethod
    def play_enemy_shoot(cls):
        """Enemy shooting sound."""
        buf = cls._generate_wave(300, 0.15, volume=0.3, wave_type='square', fade_out=True)
        cls._play_sound(buf)

    @classmethod
    def play_explosion(cls):
        """Explosion sound."""
        buf = cls._generate_wave(150, 0.3, volume=0.5, wave_type='noise', fade_out=True)
        cls._play_sound(buf)

    @classmethod
    def play_big_explosion(cls):
        """Bigger explosion for bonus ship."""
        buf = cls._generate_wave(100, 0.5, volume=0.6, wave_type='noise', fade_out=True)
        cls._play_sound(buf)

    @classmethod
    def play_level_up(cls):
        """Level up jingle."""
        buf = bytearray()
        frequencies = [523, 659, 784, 1047]  # C major arpeggio
        for freq in frequencies:
            segment = cls._generate_wave(freq, 0.15, volume=0.4, wave_type='sine', fade_out=False)
            buf.extend(segment)
        cls._play_sound(buf)

    @classmethod
    def play_bonus(cls):
        """Bonus pickup sound."""
        buf = bytearray()
        for freq in [600, 800, 1200]:
            segment = cls._generate_wave(freq, 0.1, volume=0.35, wave_type='sine', fade_out=False)
            buf.extend(segment)
        cls._play_sound(buf)

    @classmethod
    def play_game_over(cls):
        """Game over sound."""
        buf = bytearray()
        frequencies = [400, 350, 300, 200, 150]
        for freq in frequencies:
            segment = cls._generate_wave(freq, 0.2, volume=0.4, wave_type='sine', fade_out=False)
            buf.extend(segment)
        cls._play_sound(buf)

    @classmethod
    def play_start(cls):
        """Game start sound."""
        buf = bytearray()
        frequencies = [261, 329, 392, 523]
        for freq in frequencies:
            segment = cls._generate_wave(freq, 0.2, volume=0.4, wave_type='sine', fade_out=False)
            buf.extend(segment)
        cls._play_sound(buf)


# ============================================================================
# PARTICLE SYSTEM
# ============================================================================

class Particle:
    """A single particle for visual effects."""

    def __init__(self, x, y, color, speed, angle, lifetime, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.angle = angle
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # slight gravity
        self.lifetime -= 1

    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        if alpha > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)),
                               max(1, int(self.size * alpha)))

    def is_alive(self):
        return self.lifetime > 0

    @classmethod
    def create_explosion(cls, x, y, color, count=20):
        """Create an explosion of particles."""
        particles = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            lifetime = random.randint(20, 50)
            size = random.randint(1, 4)
            c = color
            if random.random() < 0.5:
                c = COLOR_WHITE
            particles.append(cls(x, y, c, speed, angle, lifetime, size))
        return particles


# ============================================================================
# GAME ENTITIES
# ============================================================================

class Bullet:
    """Represents a bullet on screen."""

    def __init__(self, x, y, direction, speed=7, is_player=True):
        self.x = x
        self.y = y
        self.direction = direction  # -1 = up, 1 = down
        self.speed = speed
        self.is_player = is_player
        self.width = 3
        self.height = 12
        self.active = True

    def update(self):
        self.y += self.direction * self.speed
        if self.y < -20 or self.y > SCREEN_HEIGHT + 20:
            self.active = False

    def draw(self, screen):
        if self.active:
            color = COLOR_CYAN if self.is_player else COLOR_RED
            pygame.draw.line(screen, color, (self.x, self.y),
                             (self.x, self.y + self.height * self.direction), self.width)

    def get_rect(self):
        return pygame.Rect(self.x - 1, self.y, self.width, self.height)


class Player:
    """The player's spaceship."""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.width = 40
        self.height = 30
        self.speed = 5
        self.bullet_speed = 8
        self.fire_rate = 15  # Frames between shots
        self.fire_timer = 0
        self.lives = 3
        self.shield = False
        self.shield_timer = 0
        self.three_way_shot = False
        self.three_way_timer = 0
        self.double_speed = False
        self.double_speed_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.visible = True

    def update(self, keys):
        # Movement
        current_speed = self.speed * (2 if self.double_speed else 1)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.width // 2, self.x - current_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(SCREEN_WIDTH - self.width // 2, self.x + current_speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(SCREEN_HEIGHT - 100, self.y - current_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(SCREEN_HEIGHT - 20, self.y + current_speed)

        # Shooting
        self.fire_timer = max(0, self.fire_timer - 1)

        # Power-up timers
        self.shield_timer = max(0, self.shield_timer - 1)
        if self.shield_timer <= 0:
            self.shield = False
        self.three_way_timer = max(0, self.three_way_timer - 1)
        if self.three_way_timer <= 0:
            self.three_way_shot = False
        self.double_speed_timer = max(0, self.double_speed_timer - 1)
        if self.double_speed_timer <= 0:
            self.double_speed = False
        self.invincible_timer = max(0, self.invincible_timer - 1)
        if self.invincible_timer <= 0:
            self.invincible = False

        # Flicker when invincible
        self.visible = (self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0) or not self.invincible

    def shoot(self):
        """Return list of bullets fired."""
        if self.fire_timer > 0:
            return []

        self.fire_timer = self.fire_rate
        bullets = []

        bullets.append(Bullet(self.x, self.y - self.height // 2, -1, self.bullet_speed, True))

        if self.three_way_shot:
            bullets.append(Bullet(self.x, self.y - self.height // 2, -1, self.bullet_speed, True))
            bullets[-1].x += 15
            bullets[-1].vx = -2
            bullets.append(Bullet(self.x, self.y - self.height // 2, -1, self.bullet_speed, True))
            bullets[-1].x -= 15
            bullets[-1].vx = 2

        return bullets

    def activate_shield(self, duration=300):
        self.shield = True
        self.shield_timer = duration

    def activate_three_way(self, duration=300):
        self.three_way_shot = True
        self.three_way_timer = duration

    def activate_double_speed(self, duration=300):
        self.double_speed = True
        self.double_speed_timer = duration

    def make_invincible(self, duration=120):
        self.invincible = True
        self.invincible_timer = duration

    def draw(self, screen):
        if not self.visible:
            return

        # Draw shield if active
        if self.shield:
            shield_alpha = min(255, self.shield_timer * 2)
            shield_color = (0, 255, 255)
            pygame.draw.ellipse(screen, shield_color,
                                (self.x - 30, self.y - 25, 60, 50), 2)

        # Draw spaceship
        # Main body
        pygame.draw.polygon(screen, COLOR_GREEN, [
            (self.x, self.y - self.height // 2),
            (self.x - self.width // 2, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height // 2)
        ])

        # Wings
        pygame.draw.polygon(screen, COLOR_CYAN, [
            (self.x - self.width // 2, self.y + self.height // 2),
            (self.x - self.width // 2 - 8, self.y + self.height // 2 + 8),
            (self.x - 5, self.y + self.height // 2 + 2)
        ])
        pygame.draw.polygon(screen, COLOR_CYAN, [
            (self.x + self.width // 2, self.y + self.height // 2),
            (self.x + self.width // 2 + 8, self.y + self.height // 2 + 8),
            (self.x + 5, self.y + self.height // 2 + 2)
        ])

        # Engine flame
        flame_length = 5 + random.randint(0, 8)
        pygame.draw.polygon(screen, COLOR_ORANGE, [
            (self.x - 5, self.y + self.height // 2 + 2),
            (self.x, self.y + self.height // 2 + 2 + flame_length),
            (self.x + 5, self.y + self.height // 2 + 2)
        ])

        # Cockpit
        pygame.draw.circle(screen, COLOR_WHITE, (self.x, self.y - 3), 4)

        # Power-up indicators
        indicator_y = self.y - self.height // 2 - 12
        if self.three_way_shot:
            pygame.draw.rect(screen, COLOR_PURPLE, (self.x - 8, indicator_y, 16, 4))
        if self.double_speed:
            pygame.draw.rect(screen, COLOR_YELLOW, (self.x - 8, indicator_y - 6, 16, 4))

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)


class Alien:
    """An alien invader."""

    def __init__(self, x, y, alien_type=0):
        self.x = x
        self.y = y
        self.alien_type = alien_type  # 0, 1, or 2 (different types)
        self.width = 30
        self.height = 25
        self.active = True
        self.animation_frame = 0

        # Points based on type
        self.points = [30, 20, 10][alien_type]
        self.colors = [COLOR_PURPLE, COLOR_ORANGE, COLOR_RED]
        self.color = self.colors[alien_type]

    def update(self):
        self.animation_frame = (self.animation_frame + 1) % 60

    def draw(self, screen):
        if not self.active:
            return

        # Draw alien based on type
        cx, cy = int(self.x), int(self.y)

        if self.alien_type == 0:  # Squid-like (top row, most points)
            # Body
            pygame.draw.ellipse(screen, self.color, (cx - 12, cy - 8, 24, 20))
            # Eyes
            pygame.draw.circle(screen, COLOR_WHITE, (cx - 5, cy - 2), 3)
            pygame.draw.circle(screen, COLOR_WHITE, (cx + 5, cy - 2), 3)
            pygame.draw.circle(screen, COLOR_BLACK, (cx - 5, cy - 2), 1)
            pygame.draw.circle(screen, COLOR_BLACK, (cx + 5, cy - 2), 1)
            # Tentacles
            tentacle_offset = math.sin(self.animation_frame * 0.2) * 3
            for dx in [-8, 0, 8]:
                pygame.draw.line(screen, self.color, (cx + dx, cy + 10),
                                 (cx + dx + tentacle_offset, cy + 16), 2)

        elif self.alien_type == 1:  # Crab-like (middle row)
            # Body
            pygame.draw.ellipse(screen, self.color, (cx - 14, cy - 6, 28, 18))
            # Eyes
            pygame.draw.circle(screen, COLOR_WHITE, (cx - 6, cy - 1), 3)
            pygame.draw.circle(screen, COLOR_WHITE, (cx + 6, cy - 1), 3)
            pygame.draw.circle(screen, COLOR_BLACK, (cx - 6, cy - 1), 1)
            pygame.draw.circle(screen, COLOR_BLACK, (cx + 6, cy - 1), 1)
            # Claws
            claw_offset = math.sin(self.animation_frame * 0.15) * 3
            pygame.draw.line(screen, self.color, (cx - 14, cy - 4), (cx - 20, cy - 8 + claw_offset), 2)
            pygame.draw.line(screen, self.color, (cx + 14, cy - 4), (cx + 20, cy - 8 + claw_offset), 2)
            pygame.draw.line(screen, self.color, (cx - 14, cy + 2), (cx - 18, cy + 8 + claw_offset), 2)
            pygame.draw.line(screen, self.color, (cx + 14, cy + 2), (cx + 18, cy + 8 + claw_offset), 2)

        else:  # Octopus-like (bottom row, least points)
            # Body
            pygame.draw.ellipse(screen, self.color, (cx - 10, cy - 10, 20, 22))
            # Eyes
            pygame.draw.circle(screen, COLOR_BLACK, (cx - 4, cy - 4), 2)
            pygame.draw.circle(screen, COLOR_BLACK, (cx + 4, cy - 4), 2)
            # Tentacles
            for dx in [-6, -2, 2, 6]:
                wave = math.sin(self.animation_frame * 0.25 + dx) * 4
                pygame.draw.line(screen, self.color, (cx + dx, cy + 10),
                                 (cx + dx + wave, cy + 18), 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)


class BonusShip:
    """The mystery/bonus ship that flies across the top."""

    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 50
        self.direction = 1
        self.speed = 2
        self.points = random.choice([100, 150, 200, 300, 500])
        self.width = 40
        self.height = 20

    def activate(self):
        self.active = True
        self.direction = random.choice([-1, 1])
        self.x = 0 if self.direction == 1 else SCREEN_WIDTH
        self.points = random.choice([100, 150, 200, 300, 500])
        self.speed = 2 + random.uniform(0.5, 1.5)

    def update(self):
        if self.active:
            self.x += self.direction * self.speed
            if (self.direction == 1 and self.x > SCREEN_WIDTH + 50) or \
                    (self.direction == -1 and self.x < -50):
                self.active = False

    def draw(self, screen):
        if not self.active:
            return

        cx, cy = int(self.x), int(self.y)

        # Glow effect
        glow_color = (255, 100, 255, 100)
        pygame.draw.ellipse(screen, (255, 150, 255), (cx - 25, cy - 18, 50, 36), 2)

        # Main body
        pygame.draw.ellipse(screen, COLOR_PURPLE, (cx - 20, cy - 10, 40, 20))
        pygame.draw.ellipse(screen, COLOR_WHITE, (cx - 10, cy - 6, 20, 12))

        # Detail lines
        pygame.draw.line(screen, COLOR_YELLOW, (cx - 15, cy), (cx + 15, cy), 1)

        # Point indicator
        font = pygame.font.SysFont('arial', 12, bold=True)
        text = font.render(str(self.points), True, COLOR_YELLOW)
        text_rect = text.get_rect(center=(cx, cy + 18))
        screen.blit(text, text_rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)


class PowerUp:
    """A power-up that drops from destroyed bonus ships."""

    TYPES = {
        'shield': {'color': COLOR_CYAN, 'letter': 'S', 'points': 0},
        'threeway': {'color': COLOR_PURPLE, 'letter': 'W', 'points': 0},
        'speed': {'color': COLOR_YELLOW, 'letter': 'D', 'points': 0},
        'life': {'color': COLOR_GREEN, 'letter': '1', 'points': 0},
        'points': {'color': COLOR_ORANGE, 'letter': '+', 'points': 1000},
    }

    def __init__(self, x, y, ptype=None):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        self.active = True
        self.type = ptype or random.choice(list(self.TYPES.keys()))
        self.animation = 0

    def update(self):
        self.y += self.speed
        self.animation += 1
        if self.y > SCREEN_HEIGHT + 20:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        cx, cy = int(self.x), int(self.y)
        info = self.TYPES[self.type]

        # Pulsing border
        pulse = math.sin(self.animation * 0.2) * 2
        pygame.draw.rect(screen, info['color'],
                         (cx - 12 - pulse, cy - 12 - pulse, 24 + 2 * pulse, 24 + 2 * pulse), 2)

        # Fill
        pygame.draw.rect(screen, (info['color'][0] // 4, info['color'][1] // 4, info['color'][2] // 4),
                         (cx - 12, cy - 12, 24, 24))

        # Letter
        font = pygame.font.SysFont('arial', 14, bold=True)
        text = font.render(info['letter'], True, info['color'])
        text_rect = text.get_rect(center=(cx, cy))
        screen.blit(text, text_rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)


class Barrier:
    """Destructible barrier/shield for the player to hide behind."""

    def __init__(self, x, y, width=60, height=40):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.blocks = []
        self._build_barrier()

    def _build_barrier():
        """Build a barrier with destructible blocks."""
        # Build arch shape
        blocks = []
        block_size = 4
        for row in range(self.height // block_size):
            for col in range(self.width // block_size):
                bx = self.x + col * block_size
                by = self.y + row * block_size

                # Create arch shape - remove blocks in the arch
                is_arch = False
                if row >= (self.height // block_size - 4):
                    # Bottom arch
                    center = (self.width // block_size) // 2
                    if center - 2 <= col <= center + 2:
                        is_arch = True

                if not is_arch:
                    blocks.append({'x': bx, 'y': by, 'active': True})
        self.blocks = blocks

    def hit(self, x, y, radius=8):
        """Remove blocks within radius of hit point. Return True if hit."""
        hit = False
        for block in self.blocks:
            if block['active']:
                dx = block['x'] - x
                dy = block['y'] - y
                if (dx * dx + dy * dy) < (radius * radius):
                    block['active'] = False
                    hit = True
        return hit

    def draw(self, screen):
        for block in self.blocks:
            if block['active']:
                pygame.draw.rect(screen, COLOR_GREEN,
                                 (block['x'], block['y'], 4, 4))

    def get_active_blocks(self):
        return sum(1 for b in self.blocks if b['active'])


# ============================================================================
# LEVEL MANAGER
# ============================================================================

class LevelManager:
    """Manages level configuration and progression."""

    LEVEL_CONFIGS = [
        {
            'name': 'First Contact',
            'alien_speed': 1,
            'alien_fire_rate': 180,
            'alien_drop_distance': 20,
            'rows': 4,
            'cols': 8,
        },
        {
            'name': 'Escalation',
            'alien_speed': 1.5,
            'alien_fire_rate': 150,
            'alien_drop_distance': 25,
            'rows': 5,
            'cols': 10,
        },
        {
            'name': 'Invasion',
            'alien_speed': 2,
            'alien_fire_rate': 120,
            'alien_drop_distance': 30,
            'rows': 5,
            'cols': 10,
        },
        {
            'name': 'Onslaught',
            'alien_speed': 2.5,
            'alien_fire_rate': 100,
            'alien_drop_distance': 35,
            'rows': 5,
            'cols': 11,
        },
        {
            'name': 'Final Battle',
            'alien_speed': 3,
            'alien_fire_rate': 80,
            'alien_drop_distance': 40,
            'rows': 5,
            'cols': 11,
        },
        {
            'name': 'Beyond',
            'alien_speed': 3.5,
            'alien_fire_rate': 70,
            'alien_drop_distance': 35,
            'rows': 6,
            'cols': 12,
        },
        {
            'name': 'Overload',
            'alien_speed': 4,
            'alien_fire_rate': 60,
            'alien_drop_distance': 40,
            'rows': 6,
            'cols': 12,
        },
        {
            'name': 'Endgame',
            'alien_speed': 4.5,
            'alien_fire_rate': 50,
            'alien_drop_distance': 45,
            'rows': 6,
            'cols': 13,
        },
    ]

    def __init__(self):
        self.current_level = 0
        self.max_level = len(self.LEVEL_CONFIGS) - 1

    def get_config(self, level=None):
        level = level if level is not None else self.current_level
        level = min(max(0, level), self.max_level)
        config = self.LEVEL_CONFIGS[level].copy()
        # Scale up beyond max level
        if level > self.max_level:
            config['alien_speed'] += (level - self.max_level) * 0.5
            config['alien_fire_rate'] = max(30, config['alien_fire_rate'] - (level - self.max_level) * 10)
        return config

    def advance_level(self):
        self.current_level += 1

    def get_level_name(self):
        level = min(self.current_level, self.max_level)
        return self.LEVEL_CONFIGS[level]['name']


# ============================================================================
# SAVE SYSTEM
# ============================================================================

class SaveSystem:
    """Handles saving and loading game statistics."""

    @staticmethod
    def load_stats():
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {
            'total_games': 0,
            'total_wins': 0,
            'total_deaths': 0,
            'highest_level': 0,
            'total_score': 0,
            'total_aliens_killed': 0,
            'total_time': 0,
        }

    @staticmethod
    def save_stats(stats):
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)

    @staticmethod
    def load_highscores():
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return []

    @staticmethod
    def save_highscore(score, level):
        highscores = SaveSystem.load_highscores()
        entry = {
            'score': score,
            'level': level,
            'date': pygame.time.get_ticks() // 1000  # seconds since epoch (approx)
        }
        highscores.append(entry)
        highscores.sort(key=lambda x: x['score'], reverse=True)
        highscores = highscores[:10]  # Keep top 10
        SaveSystem.save_highscores(highscores)

    @staticmethod
    def save_highscores(highscores):
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(highscores, f, indent=2)


# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class SpaceInvadersGame:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=16, channels=2, buffer=4096)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 16)
        self.big_font = pygame.font.SysFont('arial', 36, bold=True)
        self.small_font = pygame.font.SysFont('arial', 12)

        # Load saved data
        self.stats = SaveSystem.load_stats()
        self.highscores = SaveSystem.load_highscores()

        # Game state
        self.game_state = 'menu'  # menu, playing, paused, game_over, level_transition
        self.running = True

        # Game objects
        self.level_manager = LevelManager()
        self.player = Player()
        self.aliens = []
        self.player_bullets = []
        self.alien_bullets = []
        self.barriers = []
        self.particles = []
        self.powerups = []
        self.bonus_ship = BonusShip()

        # Game variables
        self.score = 0
        self.level = 1
        self.alien_direction = 1
        self.alien_move_timer = 0
        self.alien_fire_timer = 0
        self.level_transition_timer = 0
        self.bonus_timer = 0

        # Background stars
        self.stars = []
        for _ in range(150):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.2, 1),
                'brightness': random.randint(100, 255),
                'size': random.randint(1, 2),
            })

        # Start sound
        SoundGenerator.play_start()

    def init_level(self):
        """Initialize a new level."""
        config = self.level_manager.get_config(self.level_manager.current_level)

        # Create alien grid
        self.aliens = []
        spacing_x = 55
        spacing_y = 45
        start_x = SCREEN_WIDTH // 2 - (config['cols'] - 1) * spacing_x // 2
        start_y = 80

        for row in range(config['rows']):
            for col in range(config['cols']):
                alien_type = min(2, row)  # Type based on row
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.aliens.append(Alien(x, y, alien_type))

        # Create barriers
        self.barriers = []
        barrier_spacing = SCREEN_WIDTH / 5
        for i in range(4):
            bx = barrier_spacing * (i + 1) - 30
            by = SCREEN_HEIGHT - 130
            self.barriers.append(Barrier(bx, by))

        # Clear bullets
        self.player_bullets = []
        self.alien_bullets = []

        # Reset alien movement
        self.alien_direction = 1
        self.alien_move_timer = 0
        self.alien_fire_timer = 0

        # Reset bonus ship
        self.bonus_ship.active = False
        self.bonus_timer = 300 + random.randint(0, 200)

        # Reset powerups
        self.powerups = []

        # Player position
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT - 50

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.game_state == 'menu':
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.start_game()
                    if event.key == pygame.K_h:
                        self.game_state = 'highscores'
                    if event.key == pygame.K_s:
                        self.game_state = 'stats'

                elif self.game_state == 'highscores':
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        self.game_state = 'menu'

                elif self.game_state == 'stats':
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        self.game_state = 'menu'

                elif self.game_state == 'playing':
                    if event.key == pygame.K_SPACE:
                        bullets = self.player.shoot()
                        if bullets:
                            self.player_bullets.extend(bullets)
                            SoundGenerator.play_shoot()
                    if event.key == pygame.K_p:
                        self.game_state = 'paused'
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'paused'

                elif self.game_state == 'paused':
                    if event.key in [pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN]:
                        self.game_state = 'playing'
                    if event.key == pygame.K_q:
                        self.game_state = 'menu'

                elif self.game_state == 'game_over':
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.start_game()
                    if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        self.game_state = 'menu'

                elif self.game_state == 'level_transition':
                    pass

    def start_game(self):
        """Start a new game."""
        self.score = 0
        self.level = 1
        self.player = Player()
        self.level_manager.current_level = 0
        self.game_state = 'playing'
        self.init_level()
        SoundGenerator.play_start()

    def update_stars(self):
        """Update background stars."""
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, SCREEN_WIDTH)

    def draw_stars(self):
        """Draw background stars."""
        for star in self.stars:
            pygame.draw.circle(self.screen, (star['brightness'], star['brightness'],
                                             star['brightness'] + 50),
                               (star['x'], star['y']), star['size'])

    def update(self):
        self.update_stars()

        if self.game_state == 'playing':
            self.update_game()
        elif self.game_state == 'level_transition':
            self.level_transition_timer -= 1
            if self.level_transition_timer <= 0:
                self.game_state = 'playing'

    def update_game(self):
        """Update game logic."""
        keys = pygame.key.get_pressed()

        # Update player
        self.player.update(keys)

        # Update aliens
        config = self.level_manager.get_config()
        active_aliens = [a for a in self.aliens if a.active]

        # Alien movement
        self.alien_move_timer += 1
        move_interval = max(5, 60 - len(active_aliens))  # Speed up as aliens die
        if self.alien_move_timer >= move_interval:
            self.alien_move_timer = 0
            should_drop = False

            # Check if any alien is at the edge
            for alien in active_aliens:
                if (self.alien_direction == 1 and alien.x + alien.width // 2 >= SCREEN_WIDTH - 10) or \
                        (self.alien_direction == -1 and alien.x - alien.width // 2 <= 10):
                    should_drop = True
                    break

            for alien in active_aliens:
                if should_drop:
                    alien.y += config['alien_drop_distance']
                    # Check if alien reached player
                    if alien.y + alien.height // 2 >= self.player.y - self.player.height // 2:
                        self.game_over()
                else:
                    alien.x += self.alien_direction * config['alien_speed']

            if should_drop:
                self.alien_direction *= -1

            # Animate aliens
            for alien in self.aliens:
                alien.update()

        # Alien shooting
        self.alien_fire_timer += 1
        if self.alien_fire_timer >= config['alien_fire_rate'] and active_aliens:
            self.alien_fire_timer = 0
            shooter = random.choice(active_aliens)
            bullet = Bullet(shooter.x, shooter.y + shooter.height // 2, 1, 4, False)
            self.alien_bullets.append(bullet)
            SoundGenerator.play_enemy_shoot()

        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.update()
            if hasattr(bullet, 'vx'):
                bullet.x += bullet.vx
            if not bullet.active:
                self.player_bullets.remove(bullet)
                continue

            # Check collision with aliens
            for alien in self.aliens:
                if alien.active and bullet.get_rect().colliderect(alien.get_rect()):
                    alien.active = False
                    bullet.active = False
                    self.score += alien.points
                    self.stats['total_aliens_killed'] += 1
                    SoundGenerator.play_explosion()
                    self.particles.extend(Particle.create_explosion(alien.x, alien.y, alien.color, 15))

                    # Chance to drop power-up from aliens
                    if random.random() < 0.05:
                        self.powerups.append(PowerUp(alien.x, alien.y))
                    break

            # Check collision with bonus ship
            if self.bonus_ship.active and bullet.get_rect().colliderect(self.bonus_ship.get_rect()):
                self.score += self.bonus_ship.points
                bullet.active = False
                self.bonus_ship.active = False
                SoundGenerator.play_big_explosion()
                self.particles.extend(Particle.create_explosion(
                    self.bonus_ship.x, self.bonus_ship.y, COLOR_PURPLE, 30))
                # Drop power-up
                self.powerups.append(PowerUp(self.bonus_ship.x, self.bonus_ship.y))

            # Check collision with barriers
            for barrier in self.barriers:
                if bullet.get_rect().collidepoint(int(bullet.x), int(bullet.y)):
                    barrier.hit(bullet.x, bullet.y, 6)
                    bullet.active = False
                    self.particles.extend(Particle.create_explosion(
                        bullet.x, bullet.y, COLOR_GREEN, 5))

        # Update alien bullets
        for bullet in self.alien_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.alien_bullets.remove(bullet)
                continue

            # Check collision with player
            if self.player.visible or not self.player.invincible:
                if bullet.get_rect().colliderect(self.player.get_rect()):
                    if not self.player.invincible:
                        if self.player.shield:
                            self.player.shield = False
                            self.player.shield_timer = 0
                            SoundGenerator.play_explosion()
                            self.particles.extend(Particle.create_explosion(
                                bullet.x, bullet.y, COLOR_CYAN, 10))
                        else:
                            self.player.lives -= 1
                            SoundGenerator.play_big_explosion()
                            self.particles.extend(Particle.create_explosion(
                                self.player.x, self.player.y, COLOR_GREEN, 25))
                            if self.player.lives <= 0:
                                self.game_over()
                            else:
                                self.player.make_invincible()
                    bullet.active = False

            # Check collision with barriers
            for barrier in self.barriers:
                if bullet.get_rect().collidepoint(int(bullet.x), int(bullet.y)):
                    barrier.hit(bullet.x, bullet.y, 6)
                    bullet.active = False
                    self.particles.extend(Particle.create_explosion(
                        bullet.x, bullet.y, COLOR_GREEN, 5))

        # Update bonus ship
        self.bonus_timer -= 1
        if self.bonus_timer <= 0 and not self.bonus_ship.active:
            if random.random() < 0.3:
                self.bonus_ship.activate()
                SoundGenerator.play_bonus()
                self.bonus_timer = 300 + random.randint(200, 600)
        self.bonus_ship.update()

        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update()
            if not powerup.active:
                self.powerups.remove(powerup)
                continue

            # Check collision with player
            if powerup.get_rect().colliderect(self.player.get_rect()):
                if powerup.type == 'shield':
                    self.player.activate_shield()
                elif powerup.type == 'threeway':
                    self.player.activate_three_way()
                elif powerup.type == 'speed':
                    self.player.activate_double_speed()
                elif powerup.type == 'life':
                    self.player.lives = min(5, self.player.lives + 1)
                elif powerup.type == 'points':
                    self.score += 1000
                SoundGenerator.play_bonus()
                powerup.active = False

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

        # Check if level is complete
        if not any(a.active for a in self.aliens):
            self.level_up()

    def level_up(self):
        """Advance to the next level."""
        self.level += 1
        self.level_manager.advance_level()
        self.score += 1000  # Level clear bonus

        # Bonus life every 3 levels
        if self.level % 3 == 0:
            self.player.lives += 1

        SoundGenerator.play_level_up()
        self.game_state = 'level_transition'
        self.level_transition_timer = 120  # 2 seconds at 60 FPS

    def game_over(self):
        """Handle game over."""
        self.game_state = 'game_over'
        SoundGenerator.play_game_over()

        # Update stats
        self.stats['total_games'] += 1
        if self.level > 1:
            self.stats['total_wins'] += 1
        self.stats['total_deaths'] += 1
        self.stats['highest_level'] = max(self.stats['highest_level'], self.level_manager.current_level + 1)
        self.stats['total_score'] += self.score
        SaveSystem.save_stats(self.stats)

        # Save high score
        SaveSystem.save_highscore(self.score, self.level_manager.current_level + 1)

    def draw(self):
        self.screen.fill(COLOR_DARK_BLUE)
        self.draw_stars()

        if self.game_state == 'menu':
            self.draw_menu()
        elif self.game_state == 'highscores':
            self.draw_highscores()
        elif self.game_state == 'stats':
            self.draw_stats()
        elif self.game_state == 'playing':
            self.draw_game()
            self.draw_hud()
        elif self.game_state == 'paused':
            self.draw_game()
            self.draw_hud()
            self.draw_pause_screen()
        elif self.game_state == 'game_over':
            self.draw_game()
            self.draw_game_over_screen()
        elif self.game_state == 'level_transition':
            self.draw_game()
            self.draw_level_transition()

        pygame.display.flip()

    def draw_menu(self):
        # Title
        title = self.big_font.render("SPACE INVADERS", True, COLOR_CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font.render("A Classic Reimagined", True, COLOR_WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(subtitle, subtitle_rect)

        # Instructions
        instructions = [
            "ARROWS / WASD - Move",
            "SPACE - Fire",
            "P / ESC - Pause",
        ]
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, COLOR_YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 25))
            self.screen.blit(text, text_rect)

        # Menu options
        blink = (pygame.time.get_ticks() // 500) % 2
        if blink:
            start_text = self.big_font.render("PRESS ENTER TO START", True, COLOR_GREEN)
        else:
            start_text = self.big_font.render("PRESS ENTER TO START", True, COLOR_WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.screen.blit(start_text, start_rect)

        other_text = self.font.render("H - High Scores  |  S - Stats", True, COLOR_WHITE)
        other_rect = other_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))
        self.screen.blit(other_text, other_rect)

        # Draw decorative aliens
        demo_y = SCREEN_HEIGHT // 2 - 160
        demo_x = SCREEN_WIDTH // 2
        for i, atype in enumerate([0, 1, 2]):
            a = Alien(demo_x, demo_y + i * 35, atype)
            a.draw(self.screen)
            text = self.font.render(f"= {a.points} pts", True, a.color)
            self.screen.blit(text, (demo_x + 35, demo_y + i * 35 - 5))

        # Bonus ship
        bs = BonusShip()
        bs.x = SCREEN_WIDTH // 2
        bs.y = demo_y + 3 * 35 + 10
        bs.active = True
        bs.draw(self.screen)
        text = self.font.render(f"= ??? pts", True, COLOR_PURPLE)
        self.screen.blit(text, (demo_x + 35, demo_y + 3 * 35 + 5))

    def draw_game(self):
        # Draw barriers
        for barrier in self.barriers:
            barrier.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw aliens
        for alien in self.aliens:
            alien.draw(self.screen)

        # Draw bullets
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
        for bullet in self.alien_bullets:
            bullet.draw(self.screen)

        # Draw bonus ship
        self.bonus_ship.draw(self.screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw top border
        pygame.draw.line(self.screen, COLOR_CYAN, (0, 0), (SCREEN_WIDTH, 0), 2)

    def draw_hud(self):
        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.font.render(f"LEVEL: {self.level}", True, COLOR_YELLOW)
        self.screen.blit(level_text, (10, 30))

        # Level name
        level_name = self.level_manager.get_level_name()
        name_text = self.small_font.render(level_name, True, COLOR_CYAN)
        self.screen.blit(name_text, (10, 48))

        # Lives
        lives_text = self.font.render(f"LIVES: {self.player.lives}", True, COLOR_GREEN)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 130, 10))

        # High score
        highscore = self.highscores[0]['score'] if self.highscores else 0
        hs_text = self.font.render(f"HIGH: {highscore}", True, COLOR_WHITE)
        self.screen.blit(hs_text, (SCREEN_WIDTH - 130, 30))

        # Power-up indicators
        if self.player.three_way_shot:
            pw_text = self.small_font.render(f"3-WAY: {self.player.three_way_timer // 60}s", True, COLOR_PURPLE)
            self.screen.blit(pw_text, (SCREEN_WIDTH - 130, 48))
        if self.player.double_speed:
            pw_text = self.small_font.render(f"SPEED: {self.player.double_speed_timer // 60}s", True, COLOR_YELLOW)
            self.screen.blit(pw_text, (SCREEN_WIDTH - 130, 62))
        if self.player.shield:
            pw_text = self.small_font.render(f"SHIELD: {self.player.shield_timer // 60}s", True, COLOR_CYAN)
            self.screen.blit(pw_text, (SCREEN_WIDTH - 130, 76))

        # Bottom border with info
        pygame.draw.line(self.screen, COLOR_CYAN, (0, SCREEN_HEIGHT - 2), (SCREEN_WIDTH, SCREEN_HEIGHT - 2), 2)

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        text = self.big_font.render("PAUSED", True, COLOR_WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(text, text_rect)

        text2 = self.font.render("Press P or ESC to resume", True, COLOR_YELLOW)
        text2_rect = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text2, text2_rect)

        text3 = self.font.render("Press Q to quit to menu", True, COLOR_WHITE)
        text3_rect = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(text3, text3_rect)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(160)
        self.screen.blit(overlay, (0, 0))

        text = self.big_font.render("GAME OVER", True, COLOR_RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(text, text_rect)

        text = self.font.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        self.screen.blit(text, text_rect)

        text = self.font.render(f"Level Reached: {self.level}", True, COLOR_YELLOW)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text, text_rect)

        if self.score > 0 and self.highscores and self.score >= self.highscores[-1]['score']:
            text = self.font.render("NEW HIGH SCORE!", True, COLOR_GREEN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(text, text_rect)

        blink = (pygame.time.get_ticks() // 500) % 2
        text = self.font.render("Press ENTER to play again  |  ESC for menu",
                                True, COLOR_WHITE if blink else COLOR_CYAN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(text, text_rect)

    def draw_level_transition(self):
        progress = 1 - (self.level_transition_timer / 120)
        alpha = int(128 * progress)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(alpha)
        self.screen.blit(overlay, (0, 0))

        scale = 1 + 0.5 * math.sin(progress * math.pi)
        text = self.big_font.render(f"LEVEL {self.level}", True, COLOR_GREEN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(text, text_rect)

        level_name = self.level_manager.get_level_name()
        text2 = self.font.render(level_name, True, COLOR_YELLOW)
        text2_rect = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text2, text2_rect)

        if self.level % 3 == 0 and self.level > 0:
            text3 = self.small_font.render("BONUS LIFE!", True, COLOR_GREEN)
            text3_rect = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(text3, text3_rect)

    def draw_highscores(self):
        self.screen.fill(COLOR_DARK_BLUE)

        title = self.big_font.render("HIGH SCORES", True, COLOR_CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        for i, hs in enumerate(self.highscores):
            y = 120 + i * 35
            score_text = self.font.render(f"{i + 1}. {hs['score']} pts", True,
                                          COLOR_YELLOW if i == 0 else COLOR_WHITE)
            level_text = self.font.render(f"Level {hs.get('level', '?')}", True, COLOR_GREEN)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, y))
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 + 100, y))

        if not self.highscores:
            text = self.font.render("No scores yet!", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(text, text_rect)

        text = self.font.render("Press ESC to go back", True, COLOR_YELLOW)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(text, text_rect)

    def draw_stats(self):
        self.screen.fill(COLOR_DARK_BLUE)

        title = self.big_font.render("GAME STATISTICS", True, COLOR_CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)

        stats_lines = [
            f"Games Played: {self.stats['total_games']}",
            f"Games Won: {self.stats['total_wins']}",
            f"Times Defeated: {self.stats['total_deaths']}",
            f"Highest Level: {self.stats['highest_level']}",
            f"Total Score Earned: {self.stats['total_score']}",
            f"Total Aliens Killed: {self.stats['total_aliens_killed']}",
        ]

        for i, line in enumerate(stats_lines):
            text = self.font.render(line, True, COLOR_WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 150, 100 + i * 35))

        text = self.font.render("Press ESC to go back", True, COLOR_YELLOW)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(text, text_rect)

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    game = SpaceInvadersGame()
    game.run()




