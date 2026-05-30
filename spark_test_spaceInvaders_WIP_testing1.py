# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/GRM-Qwen2.6-27B-Opus-Heretic-Abliterated-MTP.i1-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

"""
Space Invaders - Complete Game
No external resources needed.
Saves stats to 'space_invaders_stats.json'
"""

import pygame
import json
import os
import math
import random
from collections import deque

# ========================
# CONFIGURATION
# ========================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

STATS_FILE = os.path.join(os.path.dirname(__file__) or '.', 'space_invaders_stats.json')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (180, 50, 255)
DARK_BLUE = (20, 30, 60)
STAR_COLOR = (200, 200, 220)

# Player settings
PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 7
PLAYER_SHOOT_COOLDOWN = 15
PLAYER_SIZE = 32

# Alien settings
ALIEN_BULLET_SPEED = 3
ALIENT_SHOOT_CHANCE_BASE = 0.005

# Barrier settings
NUM_BARRIERS = 4
BARRIER_WIDTH = 60
BARRIER_HEIGHT = 45


# ========================
# SOUND SYSTEM (Generated Audio)
# ========================

class SoundSystem:
    """Generates and manages game sounds using raw wave data."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        if self.enabled:
            # Initialize mixer for 16-bit stereo audio
            try:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                self._generate_sounds()
                self._generate_music()
            except pygame.error:
                self.enabled = False
                print("Warning: Sound system failed to initialize.")
        else:
            self._generate_sounds()
            self.music_sound = None

    def _make_wave(self, freq, duration_ms, volume=0.15, wave_type='square'):
        """Create a simple waveform sound."""
        sample_rate = 22050
        num_samples = int(sample_rate * duration_ms / 1000)
        import array
        samples = array.array('h')  # 'h' is 16-bit signed integer
        for i in range(num_samples):
            t = i / sample_rate
            # Envelope to prevent clicking
            envelope = 1.0 - (i / num_samples) ** 0.5
            if wave_type == 'square':
                val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                val = 2.0 * (i % int(sample_rate / freq)) / (sample_rate / freq) - 1.0
            elif wave_type == 'sine':
                val = math.sin(2 * math.pi * freq * t)
            else:
                val = math.sin(2 * math.pi * freq * t)

            # Scale to 16-bit range (-32768 to 32767)
            val = int(val * volume * 32767 * envelope)
            samples.append(val)

        # Create buffer for stereo (duplicate samples for left and right channels)
        # Pygame expects a sequence of buffers (one per channel)
        buffer = samples.tobytes()
        # Pass as a tuple of buffers (left channel, right channel)
        return pygame.mixer.Sound(buffer=buffer + buffer)

    def _generate_music(self):
        """Generate a simple looping background melody."""
        sample_rate = 22050
        duration_ms = 2000  # 2 seconds loop
        num_samples = int(sample_rate * duration_ms / 1000)
        import array
        samples = array.array('h')

        # Simple melody notes (frequencies)
        notes = [261.63, 329.63, 392.00, 523.25]  # C4, E4, G4, C5
        note_duration = num_samples // len(notes)

        for i in range(num_samples):
            t = i / sample_rate
            note_idx = i // note_duration
            freq = notes[note_idx]

            # Simple sine wave for music
            val = math.sin(2 * math.pi * freq * t)

            # Low volume for background
            volume = 0.05
            val = int(val * volume * 32767)
            samples.append(val)

        # Create buffer for stereo (duplicate samples for left and right channels)
        buffer = samples.tobytes()
        self.music_sound = pygame.mixer.Sound(buffer=buffer + buffer)

    def _generate_sounds(self):
        try:
            self.shoot = self._make_wave(800, 50, 0.15, 'square')
            self.alien_shoot = self._make_wave(300, 60, 0.12, 'sawtooth')
            self.explosion = self._make_wave(100, 200, 0.20, 'sawtooth')
            self.player_explosion = self._make_wave(80, 350, 0.25, 'sawtooth')
            self.bonus = self._make_wave(1200, 100, 0.15, 'sine')
            self.level_up = self._make_wave(600, 250, 0.18, 'sine')
            self.barrier_hit = self._make_wave(500, 30, 0.10, 'square')
            self.game_over = self._make_wave(200, 500, 0.25, 'sawtooth')
        except Exception:
            self.enabled = False

    def play(self, sound_name):
        try:
            if self.enabled:
                sound = getattr(self, sound_name, None)
                if sound:
                    sound.play()
        except Exception:
            pass

    def start_music(self):
        """Start the background music loop."""
        if self.enabled and self.music_sound:
            # Find an available channel and play the music loop
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.music_sound, loops=-1)  # -1 means loop forever

    def stop(self):
        if self.enabled:
            pygame.mixer.music.stop()
            pygame.mixer.stop()


# ========================
# STATS MANAGER
# ========================

class StatsManager:
    """Manages game statistics, saves to JSON file."""

    def __init__(self):
        self.stats = self._load()

    def _load(self):
        default = {
            'high_score': 0,
            'total_games': 0,
            'games_won': 0,
            'best_level': 1,
            'total_time_seconds': 0,
            'total_aliens_killed': 0,
        }
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    loaded = json.load(f)
                    for key in default:
                        if key not in loaded:
                            loaded[key] = default[key]
                    return loaded
        except Exception:
            pass
        return default

    def save(self):
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            pass

    def update(self, score, level, time_seconds, aliens_killed, won=False):
        self.stats['total_games'] += 1
        if score > self.stats['high_score']:
            self.stats['high_score'] = score
        if won:
            self.stats['games_won'] += 1
        if level > self.stats['best_level']:
            self.stats['best_level'] = level
        self.stats['total_time_seconds'] += time_seconds
        self.stats['total_aliens_killed'] += aliens_killed
        self.save()


# ========================
# PARTICLE SYSTEM
# ========================

class Particle:
    def __init__(self, x, y, color, speed_x, speed_y, life, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.03
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        size = max(1, int(self.size * alpha))
        color = (
            min(255, int(self.color[0] * alpha)),
            min(255, int(self.color[1] * alpha)),
            min(255, int(self.color[2] * alpha)),
        )
        pygame.draw.rect(surface, color, (int(self.x), int(self.y), size, size))

    def is_alive(self):
        return self.life > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_explosion(self, x, y, color=RED, count=20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            life = random.randint(15, 40)
            self.particles.append(Particle(
                x, y, color,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life,
                random.randint(1, 4)
            ))

    def emit_trail(self, x, y, color=BLUE, count=2):
        for _ in range(count):
            self.particles.append(Particle(
                x + random.uniform(-2, 2),
                y,
                color,
                random.uniform(-0.5, 0.5),
                random.uniform(0.5, 1.5),
                random.randint(5, 15),
                1
            ))

    def update(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


# ========================
# STAR BACKGROUND
# ========================

class StarField:
    def __init__(self, num_stars=150):
        self.stars = []
        for _ in range(num_stars):
            self.stars.append({
                'x': random.uniform(0, SCREEN_WIDTH),
                'y': random.uniform(0, SCREEN_HEIGHT),
                'size': random.uniform(0.5, 2.5),
                'speed': random.uniform(0.1, 0.8),
                'brightness': random.uniform(100, 255),
                'twinkle_speed': random.uniform(0.02, 0.08),
                'twinkle_offset': random.uniform(0, 2 * math.pi),
            })
        self.time = 0

    def update(self):
        self.time += 1
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = -5
                star['x'] = random.uniform(0, SCREEN_WIDTH)

    def draw(self, surface):
        for star in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(self.time * star['twinkle_speed'] + star['twinkle_offset'])
            brightness = int(star['brightness'] * twinkle)
            color = (brightness, brightness, min(255, brightness + 20))
            pygame.draw.circle(surface, color,
                               (int(star['x']), int(star['y'])),
                               int(star['size']))


# ========================
# SPRITE DRAWING FUNCTIONS
# ========================

def draw_player(surface, x, y, invincible_timer):
    """Draw the player spaceship using geometric shapes."""
    center_x = x + PLAYER_SIZE / 2
    center_y = y + PLAYER_SIZE / 2

    # Invincibility flash
    if invincible_timer > 0 and invincible_timer % 6 < 3:
        return  # Skip drawing for flash effect

    # Engine glow
    glow_size = 3 + int(2 * math.sin(pygame.time.get_ticks() * 0.01))
    glow_color = (255, 100, 50)
    for i in range(3):
        s = glow_size + i * 3
        a = max(0, 100 - i * 30)
        pygame.draw.rect(surface, (glow_color[0], glow_color[1], glow_color[2], a),
                         (center_x - s / 2, center_y + PLAYER_SIZE / 2 - 2, s, s + 4))

    # Engine flame
    flame_h = 6 + int(3 * math.sin(pygame.time.get_ticks() * 0.015))
    flame_rect = pygame.Rect(center_x - 4, center_y + PLAYER_SIZE / 2 - 2, 8, flame_h)
    pygame.draw.rect(surface, ORANGE, flame_rect)
    flame_rect2 = pygame.Rect(center_x - 2, center_y + PLAYER_SIZE / 2, 4, flame_h - 2)
    pygame.draw.rect(surface, YELLOW, flame_rect2)

    # Main body
    body_rect = pygame.Rect(x + 8, y + 6, PLAYER_SIZE - 16, PLAYER_SIZE - 8)
    pygame.draw.rect(surface, BLUE, body_rect)
    pygame.draw.rect(surface, CYAN, body_rect, 1)

    # Cockpit
    cockpit = pygame.Rect(x + 12, y + 8, PLAYER_SIZE - 24, 10)
    pygame.draw.rect(surface, (100, 200, 255), cockpit)

    # Wings
    wing_left = [(x, y + PLAYER_SIZE - 8), (x + 8, y + PLAYER_SIZE - 8),
                 (x + 10, y + PLAYER_SIZE - 4), (x + 14, y + PLAYER_SIZE - 4)]
    wing_right = [(x + PLAYER_SIZE, y + PLAYER_SIZE - 8),
                  (x + PLAYER_SIZE - 8, y + PLAYER_SIZE - 8),
                  (x + PLAYER_SIZE - 10, y + PLAYER_SIZE - 4),
                  (x + PLAYER_SIZE - 14, y + PLAYER_SIZE - 4)]

    pygame.draw.polygon(surface, CYAN, wing_left)
    pygame.draw.polygon(surface, CYAN, wing_right)
    pygame.draw.polygon(surface, BLUE, wing_left, 1)
    pygame.draw.polygon(surface, BLUE, wing_right, 1)

    # Top details
    pygame.draw.line(surface, CYAN, (center_x, y + 2), (center_x, y + 6), 2)
    pygame.draw.circle(surface, MAGENTA, (center_x, y + 3), 2)


def draw_alien(surface, x, y, alien_type, anim_frame):
    """Draw aliens using pixel-art style rectangles."""
    colors = {
        0: (MAGENTA, MAGENTA, (200, 100, 255)),  # Top row
        1: (CYAN, CYAN, (0, 200, 200)),
        2: (GREEN, GREEN, (0, 200, 0)),
        3: (YELLOW, YELLOW, (255, 255, 50)),
        4: (RED, RED, (200, 50, 50)),
    }
    primary, secondary, eye = colors.get(alien_type, (WHITE, WHITE, RED))

    s = 3  # pixel size

    # Different alien shapes
    if alien_type <= 1:
        # Classic invader shape
        pixels = [
            (3, 0), (4, 0), (5, 0), (6, 0),
            (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4),
            (1, 5), (2, 5), (7, 5), (8, 5),
            (1, 6), (2, 5), (7, 5), (8, 6),
        ]
    elif alien_type <= 3:
        # Squid-like shape
        pixels = [
            (4, 0), (5, 0),
            (3, 1), (4, 1), (5, 1), (6, 1),
            (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4),
            (1, 5), (2, 5), (3, 5), (6, 5), (7, 5), (8, 5),
            (2, 6), (3, 6), (6, 6), (7, 6),
        ]
    else:
        # Crab-like shape
        pixels = [
            (2, 0), (3, 0), (6, 0), (7, 0),
            (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4),
            (2, 5), (3, 5), (6, 5), (7, 5),
        ]

    # Animation: shift certain pixels
    offset_pixels = []
    for px, py in pixels:
        if anim_frame == 1:
            if py >= 5 and px <= 3:
                px -= 1
            elif py >= 5 and px >= 6:
                px += 1
        offset_pixels.append((px, py))

    # Draw body
    for px, py in offset_pixels:
        draw_x = x + px * s
        draw_y = y + py * s
        pygame.draw.rect(surface, primary, (draw_x, draw_y, s, s))

    # Draw eyes
    eye_pixels = [(3, 3), (6, 3)]
    for px, py in eye_pixels:
        draw_x = x + px * s
        draw_y = y + py * s
        pygame.draw.rect(surface, eye, (draw_x, draw_y, s, s))
        pygame.draw.rect(surface, BLACK, (draw_x + 1, draw_y + 1, 1, 1))


def draw_mystery_ship(surface, x, y, anim_frame):
    """Draw the bonus mystery ship."""
    s = 3
    pixels = [
        (4, 0), (5, 0), (6, 0),
        (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
        (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2),
        (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3),
        (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4),
        (1, 5), (2, 5), (9, 5), (10, 5),
        (2, 6), (3, 6), (8, 6), (9, 6),
    ]

    for px, py in pixels:
        draw_x = x + px * s
        draw_y = y + py * s
        color = MAGENTA if (px + py + anim_frame) % 3 == 0 else PURPLE
        pygame.draw.rect(surface, color, (draw_x, draw_y, s, s))

    # Lights
    for i in range(3):
        lx = x + (2 + i * 4) * s
        ly = y + 2 * s
        bright = 255 if anim_frame % 2 == i % 2 else 100
        pygame.draw.rect(surface, (bright, bright, 0), (lx, ly, s, s))


# ========================
# GAME CLASSES
# ========================

class Bullet:
    def __init__(self, x, y, speed, color=WHITE, is_player=True):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.is_player = is_player
        self.width = 3
        self.height = 12

    def update(self):
        self.y -= self.speed if self.is_player else -self.speed

    def draw(self, surface):
        if self.is_player:
            # Glowing player bullet
            for i in range(3):
                alpha_size = self.width + i
                color = [self.color[0], self.color[1], self.color[2]]
                if i > 0:
                    color = [min(255, c) for c in [color[0] * 0.5, color[1] * 0.5, color[2] * 0.5]]
                rect = pygame.Rect(
                    self.x - alpha_size / 2 + self.width / 2,
                    self.y - i * 2,
                    alpha_size,
                    self.height + i * 2
                )
                pygame.draw.rect(surface, color, rect)
        else:
            # Alien bullet - zigzag style
            zigzag = int(math.sin(self.y * 0.1) * 2)
            rect = pygame.Rect(self.x + zigzag, self.y, self.width, self.height)
            pygame.draw.rect(surface, RED, rect)
            pygame.draw.rect(surface, YELLOW, (self.x + zigzag + 1, self.y + 2, 1, self.height - 4))

    def is_off_screen(self):
        return self.y < -20 or self.y > SCREEN_HEIGHT + 20

    def get_rect(self):
        return pygame.Rect(self.x - self.width / 2, self.y, self.width, self.height)


class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BARRIER_WIDTH
        self.height = BARRIER_HEIGHT
        self.pixel_size = 3
        self.pixels = set()
        self.hits = 0
        self._generate_shape()

    def _generate_shape(self):
        """Generate an arched barrier shape."""
        cx = BARRIER_WIDTH / 2
        cy = BARRIER_HEIGHT / 2

        for px in range(0, BARRIER_WIDTH, self.pixel_size):
            for py in range(0, BARRIER_HEIGHT, self.pixel_size):
                nx = px / BARRIER_WIDTH
                ny = py / BARRIER_HEIGHT

                # Main arch shape
                in_shape = True

                # Bottom cutout
                if ny > 0.7 and 0.2 < nx < 0.8:
                    in_shape = False

                # Top rounding
                if ny < 0.1:
                    if not (0.2 < nx < 0.8):
                        in_shape = False

                # Side rounding
                if ny < 0.3:
                    dist = math.sqrt((nx - 0.5) ** 2 + (ny - 0.5) ** 2)
                    if nx < 0.1 or nx > 0.9:
                        in_shape = False

                if in_shape:
                    self.pixels.add((px, py))

    def hit(self, x, y, radius=3):
        """Remove pixels near hit point, return True if hit."""
        px = x - self.x
        py = y - self.y
        removed = False
        to_remove = []
        for p in self.pixels:
            dist = math.sqrt((p[0] - px) ** 2 + (p[1] - py) ** 2)
            if dist <= radius:
                to_remove.append(p)
                removed = True
        for p in to_remove:
            self.pixels.discard(p)
        return removed

    def draw(self, surface):
        for px, py in self.pixels:
            # Color based on position (gradient)
            nx = px / BARRIER_WIDTH
            ny = py / BARRIER_HEIGHT
            r = int(50 + 100 * (1 - ny))
            g = int(200 + 55 * ny)
            b = int(50 + 100 * nx)
            color = (r, g, b)
            pygame.draw.rect(surface, color,
                             (self.x + px, self.y + py, self.pixel_size, self.pixel_size))


class BonusItem:
    """Power-up items that drop from aliens."""
    TYPES = ['life', 'rapid_fire', 'shield', 'points', 'slow']

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(self.TYPES)
        self.size = 16
        self.speed = 1.5
        self.time = 0
        self.glow = 0

    def update(self):
        self.y += self.speed
        self.time += 1
        self.glow = 0.5 + 0.5 * math.sin(self.time * 0.1)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 20

    def get_rect(self):
        return pygame.Rect(self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y)
        s = self.size

        # Glow effect
        glow_r = s + int(3 * self.glow)
        glow_color = self._get_color(40)
        pygame.draw.circle(surface, glow_color, (cx, cy), glow_r, 1)

        # Main circle
        color = self._get_color(150)
        pygame.draw.circle(surface, color, (cx, cy), s / 2)
        pygame.draw.circle(surface, WHITE, (cx, cy), s / 2, 1)

        # Icon
        icon_color = WHITE
        if self.type == 'life':
            # Heart
            pygame.draw.circle(surface, icon_color, (cx - 2, cy - 1), 2)
            pygame.draw.circle(surface, icon_color, (cx + 2, cy - 1), 2)
            points = [(cx - 2, cy + 1), (cx, cy + 4), (cx + 2, cy + 1),
                      (cx + 2, cy - 1), (cx - 2, cy - 1)]
            pygame.draw.lines(surface, icon_color, False, points, 1)
        elif self.type == 'rapid_fire':
            # Lightning bolt
            points = [(cx - 1, cy - 4), (cx + 2, cy - 1), (cx, cy - 1),
                      (cx + 1, cy + 4), (cx - 2, cy + 1), (cx, cy + 1)]
            pygame.draw.lines(surface, icon_color, False, points, 1)
        elif self.type == 'shield':
            # Shield
            points = [(cx, cy - 4), (cx + 4, cy - 2), (cx + 4, cy + 2),
                      (cx, cy + 4), (cx - 4, cy + 2), (cx - 4, cy - 2)]
            pygame.draw.lines(surface, icon_color, True, points, 1)
        elif self.type == 'points':
            # Star
            points = [(cx, cy - 4), (cx + 2, cy - 1), (cx + 4, cy - 1),
                      (cx + 2, cy + 1), (cx + 3, cy + 4), (cx, cy + 2),
                      (cx - 3, cy + 4), (cx - 2, cy + 1), (cx - 4, cy - 1),
                      (cx - 2, cy - 1)]
            pygame.draw.polygon(surface, icon_color, points)
        elif self.type == 'slow':
            # Clock
            pygame.draw.circle(surface, icon_color, (cx, cy), 3, 1)
            pygame.draw.line(surface, icon_color, (cx, cy), (cx, cy - 2), 1)
            pygame.draw.line(surface, icon_color, (cx, cy), (cx + 1, cy), 1)

    def _get_color(self, intensity):
        colors = {
            'life': (255, 50, 50),
            'rapid_fire': (255, 255, 0),
            'shield': (50, 150, 255),
            'points': (255, 200, 0),
            'slow': (0, 255, 200),
        }
        base = colors.get(self.type, WHITE)
        return tuple(min(255, int(c * intensity / 255)) for c in base)


# ========================
# MAIN GAME CLASS
# ========================

class SpaceInvadersGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Python Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 16)
        self.font_large = pygame.font.SysFont('arial', 32, bold=True)
        self.font_title = pygame.font.SysFont('arial', 48, bold=True)
        self.font_small = pygame.font.SysFont('arial', 12)

        self.sound = None  # Defer initialization to run()
        self.stats = StatsManager()
        self.particles = ParticleSystem()
        self.stars = StarField()

        self.reset_game()
        self.running = True
        self.game_state = 'menu'  # menu, playing, paused, gameover, levelup

    def reset_game(self):
        """Initialize/reset all game objects."""
        # Player
        self.player_x = SCREEN_WIDTH / 2 - PLAYER_SIZE / 2
        self.player_y = SCREEN_HEIGHT - 70
        self.player_speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.level = 1
        self.invincible_timer = 0
        self.shoot_cooldown = 0
        self.rapid_fire_timer = 0
        self.shield_timer = 0
        self.slow_timer = 0

        # Aliens
        self.aliens = []
        self.alien_direction = 1
        self.alien_speed = 0.5
        self.alien_step_down = 0
        self.alien_anim_frame = 0
        self.alien_move_timer = 0
        self.aliens_killed = 0

        # Bullets
        self.player_bullets = []
        self.alien_bullets = []

        # Barriers
        self.barriers = self._create_barriers()

        # Bonus items
        self.bonus_items = []

        # Mystery ship
        self.mystery_ship = None
        self.mystery_timer = random.randint(300, 900)

        # Level transition
        self.level_transition_timer = 0

        # Game timing
        self.start_time = pygame.time.get_ticks()
        self.total_time_seconds = 0

    def _create_barriers(self):
        """Create game barriers."""
        barriers = []
        spacing = SCREEN_WIDTH / (NUM_BARRIERS + 1)
        for i in range(NUM_BARRIERS):
            x = int(spacing * (i + 1) - BARRIER_WIDTH / 2)
            y = SCREEN_HEIGHT - 140
            barriers.append(Barrier(x, y))
        return barriers

    def _create_alien_wave(self):
        """Create a new wave of aliens for current level."""
        self.aliens = []
        self.alien_direction = 1
        self.alien_step_down = 0
        self.alien_anim_frame = 0

        rows = min(5, 3 + self.level // 3)
        cols = min(11, 8 + self.level // 2)
        alien_speed_base = 0.4 + self.level * 0.05

        self.alien_speed = min(2.0, alien_speed_base)

        start_x = 60
        start_y = 50
        spacing_x = 45
        spacing_y = 38

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                alien_type = min(4, row)  # 5 types max
                points = (5 - alien_type) * 10 + self.level * 5
                self.aliens.append({
                    'x': x, 'y': y,
                    'type': alien_type,
                    'points': points,
                    'width': 30, 'height': 22,
                    'alive': True,
                    'row': row, 'col': col,
                })

    def handle_input(self):
        """Process input based on game state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == 'playing':
                        self.game_state = 'paused'
                    elif self.game_state == 'paused':
                        self.game_state = 'playing'

                if self.game_state == 'menu':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_game()

                elif self.game_state == 'gameover':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.game_state = 'menu'

                elif self.game_state == 'playing':
                    if event.key == pygame.K_SPACE and self.shoot_cooldown <= 0:
                        self._player_shoot()

        keys = pygame.key.get_pressed()
        if self.game_state == 'playing':
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_x = max(0, self.player_x - self.player_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_x = min(SCREEN_WIDTH - PLAYER_SIZE, self.player_x + self.player_speed)

    def start_game(self):
        """Start or restart the game."""
        self.reset_game()
        self._create_alien_wave()
        self.game_state = 'playing'
        self.start_time = pygame.time.get_ticks()

    def _player_shoot(self):
        """Fire player bullet."""
        cooldown = PLAYER_SHOOT_COOLDOWN // 2 if self.rapid_fire_timer > 0 else PLAYER_SHOOT_COOLDOWN
        self.shoot_cooldown = cooldown
        bx = self.player_x + PLAYER_SIZE / 2
        by = self.player_y
        self.player_bullets.append(Bullet(bx, by, PLAYER_BULLET_SPEED, CYAN, True))
        self.sound.play('shoot')

    def update(self):
        """Main game update loop."""
        self.stars.update()
        self.particles.update()

        if self.game_state != 'playing':
            return

        # Update timers
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1

        # Player engine particles
        if random.random() < 0.3:
            self.particles.emit_trail(
                self.player_x + PLAYER_SIZE / 2,
                self.player_y + PLAYER_SIZE,
                ORANGE, 1
            )

        # Update player bullets
        for bullet in self.player_bullets:
            bullet.update()

        # Update alien bullets
        for bullet in self.alien_bullets:
            bullet.update()

        # Remove off-screen bullets
        self.player_bullets = [b for b in self.player_bullets if not b.is_off_screen()]
        self.alien_bullets = [b for b in self.alien_bullets if not b.is_off_screen()]

        # Move aliens
        self._move_aliens()

        # Alien shooting
        slow_factor = 0.5 if self.slow_timer > 0 else 1.0
        for alien in self.aliens:
            if alien['alive']:
                # Reduced shooting frequency for better balance
                shoot_chance = ALIENT_SHOOT_CHANCE_BASE * min(self.level * 0.5, 3) * slow_factor
                if random.random() < shoot_chance:
                    bx = alien['x'] + alien['width'] / 2
                    by = alien['y'] + alien['height']
                    self.alien_bullets.append(Bullet(bx, by, ALIEN_BULLET_SPEED, RED, False))
                    self.sound.play('alien_shoot')

        # Check collisions - player bullets vs aliens
        for bullet in self.player_bullets:
            bullet_rect = bullet.get_rect()
            for alien in self.aliens:
                if alien['alive']:
                    alien_rect = pygame.Rect(alien['x'], alien['y'], alien['width'], alien['height'])
                    if bullet_rect.colliderect(alien_rect):
                        alien['alive'] = False
                        bullet.y = -100
                        self.score += alien['points']
                        self.aliens_killed += 1
                        self.sound.play('explosion')
                        self.particles.emit_explosion(
                            alien['x'] + alien['width'] / 2,
                            alien['y'] + alien['height'] / 2,
                            (255, 200, 100), 15
                        )
                        # Chance to drop bonus
                        if random.random() < 0.12:
                            self.bonus_items.append(BonusItem(
                                alien['x'] + alien['width'] / 2,
                                alien['y']
                            ))
                        break

            # Player bullets vs barriers
            if bullet.y > 0:  # Not already destroyed
                for barrier in self.barriers:
                    bar_rect = pygame.Rect(barrier.x, barrier.y, barrier.width, barrier.height)
                    if bullet_rect.colliderect(bar_rect):
                        if barrier.hit(bullet.x, bullet.y):
                            bullet.y = -100
                            self.sound.play('barrier_hit')
                            self.particles.emit_explosion(bullet.x, bullet.y, GREEN, 5)
                            break

            # Player bullets vs mystery ship
            if self.mystery_ship and bullet.y > 0:
                ms_rect = pygame.Rect(
                    self.mystery_ship['x'],
                    self.mystery_ship['y'],
                    self.mystery_ship['width'],
                    self.mystery_ship['height']
                )
                if bullet_rect.colliderect(ms_rect):
                    self.score += 150 + self.level * 50
                    self.sound.play('bonus')
                    self.particles.emit_explosion(
                        self.mystery_ship['x'] + self.mystery_ship['width'] / 2,
                        self.mystery_ship['y'] + self.mystery_ship['height'] / 2,
                        MAGENTA, 30
                    )
                    bullet.y = -100
                    self.mystery_ship = None

        # Check collisions - alien bullets vs player/barriers
        for bullet in self.alien_bullets:
            bullet_rect = bullet.get_rect()

            # Vs barriers
            for barrier in self.barriers:
                bar_rect = pygame.Rect(barrier.x, barrier.y, barrier.width, barrier.height)
                if bullet_rect.colliderect(bar_rect):
                    if barrier.hit(bullet.x, bullet.y):
                        bullet.y = SCREEN_HEIGHT + 100
                        self.sound.play('barrier_hit')
                        self.particles.emit_explosion(bullet.x, bullet.y, GREEN, 5)
                        break

            # Vs player
            player_rect = pygame.Rect(self.player_x, self.player_y, PLAYER_SIZE, PLAYER_SIZE)
            if bullet_rect.colliderect(player_rect):
                if self.invincible_timer > 0 or self.shield_timer > 0:
                    bullet.y = SCREEN_HEIGHT + 100
                    self.particles.emit_explosion(bullet.x, bullet.y, CYAN, 8)
                else:
                    self._player_hit()
                    bullet.y = SCREEN_HEIGHT + 100
                    break

        # Check collisions - aliens vs player (game over)
        for alien in self.aliens:
            if alien['alive']:
                if alien['y'] + alien['height'] >= self.player_y:
                    self._game_over()
                    return

        # Check collisions - aliens vs barriers
        for alien in self.aliens:
            if alien['alive']:
                alien_rect = pygame.Rect(alien['x'], alien['y'], alien['width'], alien['height'])
                for barrier in self.barriers:
                    bar_rect = pygame.Rect(barrier.x, barrier.y, barrier.width, barrier.height)
                    if alien_rect.colliderect(bar_rect):
                        # Remove overlapping barrier pixels
                        for px in range(barrier.width):
                            for py in range(barrier.height):
                                if (px, py) in barrier.pixels:
                                    abs_x = barrier.x + px
                                    abs_y = barrier.y + py
                                    # Fixed: Use collidepoint instead of contains
                                    if alien_rect.collidepoint(abs_x, abs_y):
                                        barrier.pixels.discard((px, py))

        # Check if all aliens dead - next level
        if not any(a['alive'] for a in self.aliens):
            self._next_level()

        # Mystery ship
        self.mystery_timer -= 1
        if self.mystery_timer <= 0 and self.mystery_ship is None:
            direction = random.choice([-1, 1])
            self.mystery_ship = {
                'x': -60 if direction > 0 else SCREEN_WIDTH + 10,
                'y': 20,
                'width': 36, 'height': 20,
                'speed': direction * 2,
                'anim': 0,
            }
            self.mystery_timer = random.randint(400, 800)

        if self.mystery_ship:
            self.mystery_ship['x'] += self.mystery_ship['speed']
            self.mystery_ship['anim'] += 1
            if (self.mystery_ship['speed'] > 0 and self.mystery_ship['x'] > SCREEN_WIDTH + 60) or \
                    (self.mystery_ship['speed'] < 0 and self.mystery_ship['x'] < -60):
                self.mystery_ship = None

        # Bonus items
        for item in self.bonus_items:
            item.update()

        # Bonus items vs player
        player_rect = pygame.Rect(self.player_x, self.player_y, PLAYER_SIZE, PLAYER_SIZE)
        for item in self.bonus_items:
            if player_rect.colliderect(item.get_rect()):
                self._apply_bonus(item.type)
                item.y = SCREEN_HEIGHT + 100
                self.sound.play('bonus')

        # Remove off-screen bonuses
        self.bonus_items = [b for b in self.bonus_items if not b.is_off_screen()]

    def _move_aliens(self):
        """Move aliens in formation."""
        speed = self.alien_speed

        # Check if any alien is at edge
        move_down = False
        for alien in self.aliens:
            if not alien['alive']:
                continue
            if self.alien_direction > 0 and alien['x'] + alien['width'] >= SCREEN_WIDTH - 10:
                move_down = True
                break
            if self.alien_direction < 0 and alien['x'] <= 10:
                move_down = True
                break

        if move_down:
            self.alien_direction *= -1
            self.alien_step_down += 1
            # Small step down when hitting edge
            for alien in self.aliens:
                if alien['alive']:
                    alien['y'] += 8
        else:
            # Normal horizontal movement only
            step = speed * (2 - self.alien_step_down * 0.1)
            step = max(0.3, step)  # Minimum speed

            for alien in self.aliens:
                if alien['alive']:
                    alien['x'] += step * self.alien_direction

        # Animation
        self.alien_move_timer += 1
        if self.alien_move_timer >= 30:
            self.alien_move_timer = 0
            self.alien_anim_frame = 1 - self.alien_anim_frame

    def _player_hit(self):
        """Handle player getting hit."""
        self.lives -= 1
        self.sound.play('player_explosion')
        self.particles.emit_explosion(
            self.player_x + PLAYER_SIZE / 2,
            self.player_y + PLAYER_SIZE / 2,
            BLUE, 25
        )

        if self.lives <= 0:
            self._game_over()
        else:
            self.invincible_timer = 120  # 2 seconds
            self.player_x = SCREEN_WIDTH / 2 - PLAYER_SIZE / 2
            self.shield_timer = 60  # Brief shield after hit

    def _game_over(self):
        """Handle game over."""
        self.game_state = 'gameover'
        self.total_time_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
        self.sound.play('game_over')
        self.stats.update(self.score, self.level, self.total_time_seconds, self.aliens_killed)

    def _next_level(self):
        """Transition to next level."""
        self.level += 1
        self.level_transition_timer = 120
        self.sound.play('level_up')
        self.player_bullets = []
        self.alien_bullets = []
        self.mystery_ship = None
        self._create_alien_wave()
        # Regenerate some barrier
        for barrier in self.barriers:
            barrier._generate_shape()
            # Remove some for visual variety
            remove_count = len(barrier.pixels) // 3
            for _ in range(remove_count):
                if barrier.pixels:
                    barrier.pixels.pop()

    def _apply_bonus(self, bonus_type):
        """Apply a bonus power-up."""
        if bonus_type == 'life':
            self.lives = min(self.lives + 1, 5)
        elif bonus_type == 'rapid_fire':
            self.rapid_fire_timer = 600  # 10 seconds
        elif bonus_type == 'shield':
            self.shield_timer = 300  # 5 seconds
        elif bonus_type == 'points':
            self.score += 500
        elif bonus_type == 'slow':
            self.slow_timer = 300  # 5 seconds

    def draw(self):
        """Draw everything on screen."""
        # Background
        self.screen.fill(DARK_BLUE)
        self.stars.draw(self.screen)

        # Grid lines (subtle)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (30, 40, 60), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (30, 40, 60), (0, y), (SCREEN_WIDTH, y))

        if self.game_state == 'menu':
            self._draw_menu()
        elif self.game_state == 'playing':
            self._draw_game()
        elif self.game_state == 'paused':
            self._draw_game()
            self._draw_pause_overlay()
        elif self.game_state == 'gameover':
            self._draw_game()
            self._draw_gameover_overlay()

        pygame.display.flip()

    def _draw_menu(self):
        """Draw main menu."""
        # Title with glow
        title_color = CYAN
        title = self.font_title.render("SPACE INVADERS", True, title_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, 150))
        pygame.draw.rect(self.screen, (10, 10, 30, 200),
                         (title_rect.x - 10, title_rect.y - 10,
                          title_rect.width + 20, title_rect.height + 20),
                         border_radius=10)
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_large.render("PYTHON EDITION", True, BLUE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH / 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # Instructions
        instructions = [
            "← → or A/D to Move",
            "SPACE to Shoot",
            "ESCAPE to Pause",
            "",
            "Destroy all aliens to advance!",
            "Collect bonus power-ups!",
            "Watch for the mystery ship!"
        ]

        y_pos = 260
        for line in instructions:
            color = YELLOW if "!" in line else WHITE
            text = self.font.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos += 25

        # Start prompt
        blink = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)
        start_color = (int(255 * blink), int(255 * blink), 0)
        start_text = self.font_large.render("PRESS SPACE TO START", True, start_color)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH / 2, 480))
        self.screen.blit(start_text, start_rect)

        # High score
        hs_text = self.font.render(f"HIGH SCORE: {self.stats.stats['high_score']}", True, GREEN)
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH / 2, 520))
        self.screen.blit(hs_text, hs_rect)

        # Stats
        stats_text = self.font_small.render(
            f"Games: {self.stats.stats['total_games']} | "
            f"Best Level: {self.stats.stats['best_level']} | "
            f"Aliens Killed: {self.stats.stats['total_aliens_killed']}",
            True, (100, 100, 150)
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH / 2, 550))
        self.screen.blit(stats_text, stats_rect)

        # Animated aliens
        t = pygame.time.get_ticks()
        for i in range(5):
            ax = 100 + i * 140
            ay = 350 + int(10 * math.sin(t * 0.002 + i))
            draw_alien(self.screen, ax, ay, i, t // 500 % 2)

    def _draw_game(self):
        """Draw the game scene."""
        # Barriers
        for barrier in self.barriers:
            barrier.draw(self.screen)

        # Aliens
        for alien in self.aliens:
            if alien['alive']:
                draw_alien(self.screen, alien['x'], alien['y'],
                           alien['type'], self.alien_anim_frame)

        # Mystery ship
        if self.mystery_ship:
            draw_mystery_ship(self.screen,
                              self.mystery_ship['x'],
                              self.mystery_ship['y'],
                              self.mystery_ship['anim'] // 10)

        # Player bullets
        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        # Alien bullets
        for bullet in self.alien_bullets:
            bullet.draw(self.screen)

        # Bonus items
        for item in self.bonus_items:
            item.draw(self.screen)

        # Player
        if self.shield_timer > 0:
            # Shield visual
            shield_alpha = 0.3 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)
            shield_rect = pygame.Rect(
                self.player_x - 4, self.player_y - 4,
                PLAYER_SIZE + 8, PLAYER_SIZE + 8
            )
            shield_color = (int(100 * shield_alpha), int(200 * shield_alpha), int(255 * shield_alpha))
            pygame.draw.rect(self.screen, shield_color, shield_rect, 2, border_radius=5)

        draw_player(self.screen, self.player_x, self.player_y, self.invincible_timer)

        # Particles
        self.particles.draw(self.screen)

        # HUD
        self._draw_hud()

    def _draw_hud(self):
        """Draw heads-up display."""
        # Top bar background
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 30)
        pygame.draw.rect(self.screen, (10, 15, 30), bar_rect)
        pygame.draw.line(self.screen, (50, 70, 100), (0, 30), (SCREEN_WIDTH, 30))

        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 8))

        # Level
        level_text = self.font.render(f"LEVEL: {self.level}", True, CYAN)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 8))

        # Lives
        lives_text = self.font.render(f"LIVES:", True, GREEN)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 8))
        for i in range(self.lives):
            lx = SCREEN_WIDTH - 70 + i * 20
            ly = 8
            # Draw mini ship
            pygame.draw.rect(self.screen, BLUE, (lx, ly + 4, 12, 10))
            pygame.draw.rect(self.screen, CYAN, (lx - 2, ly + 8, 16, 6))

        # Active power-ups
        py = 35
        powerups = []
        if self.rapid_fire_timer > 0:
            powerups.append(("RAPID FIRE", YELLOW, self.rapid_fire_timer))
        if self.shield_timer > 0:
            powerups.append(("SHIELD", BLUE, self.shield_timer))
        if self.slow_timer > 0:
            powerups.append(("SLOW TIME", CYAN, self.slow_timer))

        for name, color, timer in powerups:
            text = self.font_small.render(f"{name}: {timer // 60 + 1}s", True, color)
            self.screen.blit(text, (SCREEN_WIDTH - 140, py))
            py += 15

        # Level transition message
        if self.level_transition_timer > 0:
            alpha = min(255, self.level_transition_timer * 3)
            text_color = (0, int(255 * (alpha / 255)), 0)
            level_text = self.font_large.render(f"LEVEL {self.level}!", True, text_color)
            rect = level_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            self.screen.blit(level_text, rect)
            self.level_transition_timer -= 1

    def _draw_pause_overlay(self):
        """Draw pause overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))

        text = self.font_title.render("PAUSED", True, WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30))
        self.screen.blit(text, rect)

        sub = self.font.render("Press ESC to continue", True, YELLOW)
        rect = sub.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20))
        self.screen.blit(sub, rect)

    def _draw_gameover_overlay(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Game Over title
        text = self.font_title.render("GAME OVER", True, RED)
        rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80))
        self.screen.blit(text, rect)

        # Stats
        stats_lines = [
            f"Final Score: {self.score}",
            f"Level Reached: {self.level}",
            f"Aliens Killed: {self.aliens_killed}",
            f"High Score: {max(self.score, self.stats.stats['high_score'])}",
        ]

        y = SCREEN_HEIGHT / 2 - 30
        for line in stats_lines:
            is_last = line.startswith("High")
            color = YELLOW if is_last else WHITE
            text = self.font_large.render(line, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH / 2, y))
            self.screen.blit(text, rect)
            y += 35

        # Restart prompt
        blink = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)
        prompt_color = (int(255 * blink), int(255 * blink), 0)
        prompt = self.font.render("Press SPACE for Main Menu", True, prompt_color)
        rect = prompt.get_rect(center=(SCREEN_WIDTH / 2, y + 20))
        self.screen.blit(prompt, rect)

    def run(self):
        """Main game loop."""
        # Initialize sound after display is created
        self.sound = SoundSystem()

        # Start background music
        self.sound.start_music()

        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


# ========================
# ENTRY POINT
# ========================

if __name__ == '__main__':
    game = SpaceInvadersGame()
    game.run()
