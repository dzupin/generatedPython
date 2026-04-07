# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# Provided Python code is working correctly. Treat this code as starting point. Analyze code of the game and propose few more visual especially in UI , but focus should be placed on play-ability improvements to make game more addictive. I am thinking in a redirection  of earning points that can be then use for upgrades in next games.
# Excellent. They are all very good suggestion. I also agree with implementation order. Please implement as many as possible of your suggestions into the game code. Ideally all of them. Also feel free to adjust and tweak your suggestion further if needed. Provide complete updated code  that I can use as single copy and paste replacement of my current game.



# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-397B-A17B-UD-TQ1_0.gguf  --mmproj /AI/models/Qwen3.5-397B-A17B-mmproj-BF16.gguf

import pygame
import random
import math
import json
import os

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5
MAX_ENEMY_BULLETS = 6
NUM_ENEMIES_ROWS = 4
NUM_ENEMIES_COLS = 8
HIGH_SCORE_FILE = "high_scores.json"

# Colors - Enhanced neon palette
BG_COLOR = (10, 12, 25)
PLAYER_COLOR = (0, 255, 200)
ENEMY_1_COLOR = (255, 69, 0)  # Orange
ENEMY_2_COLOR = (0, 255, 127)  # Green
ENEMY_3_COLOR = (138, 43, 226)  # Purple
TEXT_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 255, 0)
ENEMY_BULLET_COLOR = (255, 100, 100)
UFO_COLOR = (200, 200, 255)
BARRIER_COLOR = (100, 255, 100)
POWERUP_COLOR = (255, 215, 0)  # Gold

# Enhanced explosion colors for variety
EXPLOSION_COLORS = [
    (255, 255, 0),  # Yellow
    (255, 200, 0),  # Orange-yellow
    (255, 100, 0),  # Orange-red
    (255, 50, 0),  # Deep orange
    (100, 255, 100),  # Green (for barrier hits)
    (255, 255, 255)  # White (for special effects)
]

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"
POWERUP_BOMB = "BOMB"
POWERUP_SCORE = "SCORE"


# --- SPRITE GENERATOR (Procedural Pixel Art) ---
def create_pixel_art(width, height, color, pattern):
    """Creates a pygame Surface from a binary pattern."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, color, (x * 2, y * 2, 2, 2))
    return surface


# Define Sprites as Binary Maps (Enhanced patterns)
PLAYER_MAP = [
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

ENEMY_1_MAP = [
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

ENEMY_2_MAP = [
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 0, 1, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 1, 1, 0, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]

ENEMY_3_MAP = [
    [0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 0, 1, 1, 1],
    [1, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 1, 0, 0, 0, 1, 0, 0]
]

UFO_MAP = [
    [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
    [0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
]

# Pre-generate Sprites
SPRITE_PLAYER = create_pixel_art(16, 16, PLAYER_COLOR, PLAYER_MAP)
SPRITE_ENEMY_1 = create_pixel_art(20, 16, ENEMY_1_COLOR, ENEMY_1_MAP)
SPRITE_ENEMY_2 = create_pixel_art(20, 16, ENEMY_2_COLOR, ENEMY_2_MAP)
SPRITE_ENEMY_3 = create_pixel_art(20, 16, ENEMY_3_COLOR, ENEMY_3_MAP)
SPRITE_UFO = create_pixel_art(22, 14, UFO_COLOR, UFO_MAP)


# --- AUDIO SYSTEM ---
class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 512)
        self.channels = [pygame.mixer.Channel(i) for i in range(8)]
        self.sample_rate = 44100
        self.muted = False

    def create_tone(self, freq, duration, vol=0.3, wave_type='square'):
        samples = int(self.sample_rate * duration)
        buffer = [0] * (samples * 2)
        max_sample = 32767
        for s in range(samples):
            t = float(s) / self.sample_rate
            if wave_type == 'square':
                value = 1 if (t * freq) % 1 < 0.5 else -1
                sample_val = int(max_sample * vol * value)
            elif wave_type == 'sawtooth':
                value = 2 * ((t * freq) % 1) - 1
                sample_val = int(max_sample * vol * value)
            else:
                value = math.sin(2 * math.pi * freq * t)
                sample_val = int(max_sample * vol * value)

            buffer[s * 2] = sample_val
            buffer[s * 2 + 1] = sample_val
        return pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        )

    def play_shoot(self, pitch=880):
        if self.muted:
            return
        self.channels[0].play(self.create_tone(pitch, 0.08, 0.12, 'square'))

    def play_enemy_shoot(self):
        if self.muted:
            return
        self.channels[1].play(self.create_tone(200, 0.15, 0.08, 'sawtooth'))

    def play_explosion(self, pitch=150):
        if self.muted:
            return
        duration = 0.2
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-16384, 16384) for _ in range(samples * 2)]
        self.channels[2].play(pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        ))

    def play_powerup(self, pitch=600):
        if self.muted:
            return
        self.channels[3].play(self.create_tone(pitch, 0.12, 0.15, 'square'))

    def play_combo(self, combo):
        if self.muted:
            return
        pitch = 800 + (combo * 50)
        self.channels[4].play(self.create_tone(pitch, 0.06, 0.1, 'square'))

    def play_level_up(self):
        if self.muted:
            return
        for i, freq in enumerate([523, 659, 784, 1046]):
            pygame.time.set_timer(pygame.USEREVENT + 1, 150 * (i + 1), 1)
            self.channels[5].play(self.create_tone(freq, 0.2, 0.15, 'square'))

    def play_game_over(self):
        if self.muted:
            return
        for i, freq in enumerate([392, 370, 349, 330]):
            pygame.time.set_timer(pygame.USEREVENT + 2, 200 * (i + 1), 1)
            self.channels[6].play(self.create_tone(freq, 0.3, 0.1, 'sawtooth'))


# --- CLASSES ---

class Particle:
    def __init__(self, x, y, color, speed=3, size=3, particle_type='normal'):
        self.x, self.y = x, y
        self.color = color
        self.particle_type = particle_type  # 'normal', 'arc', 'spark'

        angle = random.uniform(0, math.pi * 2)
        speed_mag = random.uniform(1, speed)

        # Enhanced trajectory with arcs
        self.vx = math.cos(angle) * speed_mag
        self.vy = math.sin(angle) * speed_mag
        self.arc_strength = random.uniform(0.5, 2.0) if particle_type == 'arc' else 0

        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.gravity = 0.1
        self.size = size
        self.initial_size = size
        self.trail = []
        self.max_trail = 10
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.1, 0.1)

    def update(self):
        # Store position for trail
        self.trail.append((self.x, self.y, self.life))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

        # Add arc effect for special particles
        if self.particle_type == 'arc':
            self.vx += math.cos(self.life * math.pi) * self.arc_strength
            self.vy += math.sin(self.life * math.pi) * self.arc_strength

        self.vy += self.gravity
        self.life -= self.decay
        self.size = self.initial_size * self.life
        self.rotation += self.rotation_speed

    def draw(self, surface):
        if self.life <= 0:
            return

        # Draw trail first
        for i, (tx, ty, trail_life) in enumerate(self.trail):
            trail_alpha = int(150 * (i / len(self.trail)) * trail_life)
            trail_size = max(1, int(self.size * (i / len(self.trail))))
            trail_color = (*self.color[:3], trail_alpha)

            s = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, trail_color, (trail_size, trail_size), trail_size)
            surface.blit(s, (int(tx) - trail_size, int(ty) - trail_size))

        # Draw main particle with glow
        alpha = int(255 * self.life)
        color = (*self.color[:3], alpha) if len(self.color) > 3 else self.color

        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (int(self.size), int(self.size)), int(self.size))

        # Inner white core for brightness
        pygame.draw.circle(s, (255, 255, 255, alpha), (int(self.size), int(self.size)), int(self.size * 0.4))

        surface.blit(s, (int(self.x) - int(self.size), int(self.y) - int(self.size)))


class Bullet:
    def __init__(self, x, y, is_player=False, speed=BULLET_SPEED, angle=0):
        self.x, self.y = x, y
        self.width, self.height = 6, 12
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)

        # Enhanced velocity with angle support
        rad = math.radians(angle)
        self.velocity_x = BULLET_SPEED * math.sin(rad) if is_player else 0
        self.velocity_y = -speed * math.cos(rad) if is_player else ENEMY_BULLET_SPEED

        if not is_player:
            self.velocity_y = abs(self.velocity_y)

        self.active = True
        self.trail = []
        self.glow_intensity = 0

    def update(self):
        # Trail effect
        self.trail.append((self.x, self.y, self.glow_intensity))
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)

        # Pulsing glow
        self.glow_intensity = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 255

        if self.y < -50 or self.y > HEIGHT + 50 or self.x < -50 or self.x > WIDTH + 50:
            self.active = False

    def draw(self, surface):
        # Draw trail with fading
        for i, (tx, ty, glow) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            trail_color = (*self.color[:3], alpha)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, trail_color, (2, 2), 2)
            surface.blit(s, (int(tx) - 2, int(ty) - 2))

        # Draw main bullet with glow
        pygame.draw.rect(surface, self.color, self.rect)

        # Enhanced glow effect
        glow_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(surface, (255, 255, 200), glow_rect, 1)


class PowerUp:
    def __init__(self, x, y, power_type=None):
        self.x, self.y = x, y
        self.type = power_type if power_type else random.choice([
            POWERUP_RAPID, POWERUP_SPREAD, POWERUP_SHIELD,
            POWERUP_BOMB, POWERUP_SCORE
        ])
        self.width, self.height = 24, 24
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.active = True
        self.color = POWERUP_COLOR
        self.vy = 2
        self.angle = 0
        self.pulse = 0

    def update(self):
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        self.angle += 0.05
        self.pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255

        if self.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        # Rotating diamond shape with glow
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Outer glow - fixed alpha value
        pulse_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 200)
        pygame.draw.ellipse(s, (255, 255, 100, pulse_alpha), (0, 0, self.width, self.height))

        # Inner shape - RGB color only
        points = [
            (self.width // 2, 2),
            (self.width - 2, self.height // 2),
            (self.width // 2, self.height - 2),
            (2, self.height // 2)
        ]
        pygame.draw.polygon(s, self.color[:3], points)

        # Letter indicator
        font = pygame.font.SysFont("Arial", 16, bold=True)
        letter = {
            POWERUP_RAPID: "R", POWERUP_SPREAD: "S", POWERUP_SHIELD: "H",
            POWERUP_BOMB: "B", POWERUP_SCORE: "$"
        }.get(self.type, "?")
        txt = font.render(letter, True, (0, 0, 0))
        s.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - txt.get_height() // 2))

        surface.blit(s, (self.x, self.y))


class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.active = True
        self.segments = []
        self.create_segments()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.damage_count = 0

    def create_segments(self):
        segment_width = 4
        segment_height = 4
        for row in range(self.height // segment_height):
            for col in range(self.width // segment_width):
                is_hole = (col % 4 == 1 and row < 3) or (col % 4 == 1 and row > 7)
                if not is_hole:
                    self.segments.append({
                        'x': self.x + col * segment_width,
                        'y': self.y + row * segment_height,
                        'width': segment_width,
                        'height': segment_height,
                        'active': True,
                        'health': 3
                    })

    def update(self):
        active_segments = [s for s in self.segments if s['active']]
        if not active_segments:
            self.active = False
            return

        min_x = min(s['x'] for s in active_segments)
        min_y = min(s['y'] for s in active_segments)
        max_x = max(s['x'] + s['width'] for s in active_segments)
        max_y = max(s['y'] + s['height'] for s in active_segments)
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def take_damage(self, bullet_rect):
        for segment in self.segments:
            if segment['active']:
                seg_rect = pygame.Rect(segment['x'], segment['y'], segment['width'], segment['height'])
                if bullet_rect.colliderect(seg_rect):
                    segment['health'] -= 1
                    if segment['health'] <= 0:
                        segment['active'] = False
                        self.damage_count += 1
                    return True
        return False

    def draw(self, surface):
        for segment in self.segments:
            if segment['active']:
                # Color based on remaining health
                if segment['health'] == 3:
                    color = BARRIER_COLOR
                elif segment['health'] == 2:
                    color = (150, 255, 150)
                else:
                    color = (100, 200, 100)

                pygame.draw.rect(surface, color, (segment['x'], segment['y'], segment['width'], segment['height']))

                # Damage indicator
                if segment['health'] < 3:
                    pygame.draw.rect(surface, (255, 0, 0),
                                     (segment['x'], segment['y'], segment['width'], segment['height']), 1)


class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2 - 16, HEIGHT - 60
        self.width, self.height = 32, 32
        self.color = PLAYER_COLOR
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 350
        self.active = True
        self.lives = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Powerups
        self.powerups = []
        self.shield_active = False
        self.shield_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.bomb_available = False
        self.bomb_timer = 0

        # Visual effects
        self.engine_pulse = 0
        self.hit_flash = 0

    def update(self, keys, current_time):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

        # Combo decay
        if current_time - self.combo_timer > 1500:
            self.combo = 0

        # Shield decay
        if self.shield_active and current_time - self.shield_timer > 8000:
            self.shield_active = False

        # Bomb availability
        if self.bomb_available and current_time - self.bomb_timer > 15000:
            self.bomb_available = False

        # Visual effects
        self.engine_pulse = abs(math.sin(current_time * 0.01)) * 255
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def shoot(self, game, current_time):
        shoot_delay = self.shoot_delay

        # Rapid fire powerup
        if POWERUP_RAPID in self.powerups:
            shoot_delay = 150

        if current_time - self.last_shot > shoot_delay:
            if POWERUP_SPREAD in self.powerups:
                for angle_offset in [-15, 0, 15]:
                    bx = self.x + self.width // 2
                    by = self.y
                    b = Bullet(bx, by, is_player=True, angle=angle_offset)
                    game.player_bullets.append(b)
            else:
                bullet_x = self.x + self.width // 2
                bullet_y = self.y
                bullet = Bullet(bullet_x, bullet_y, is_player=True)
                game.player_bullets.append(bullet)

            self.last_shot = current_time
            game.sound_manager.play_shoot(880 + random.randint(-50, 50))

    def draw(self, surface):
        # Shield effect
        if self.shield_active:
            shield_rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)
            pygame.draw.rect(surface, (100, 255, 255), shield_rect, 2)
            pygame.draw.rect(surface, (100, 255, 255, 100), shield_rect)

        # Hit flash
        if self.hit_flash > 0:
            flash_color = (255, 0, 0, int(255 * self.hit_flash / 20))
            pygame.draw.rect(surface, flash_color, self.rect)

        # Sprite
        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))

        # Engine glow - FIXED: RGB tuple only (3 values)
        time = pygame.time.get_ticks()
        glow_size = 5 + int(abs(math.sin(time * 0.02)) * 2)
        engine_brightness = 200 + int(abs(math.sin(time * 0.01)) * 55)
        engine_color = (255, engine_brightness, 0)
        pygame.draw.circle(surface, engine_color,
                           (self.x + self.width // 2, self.y + self.height),
                           glow_size)


class Invader:
    def __init__(self, x, y, row, col, level):
        self.x, self.y = x, y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        self.level = level

        if row == 0:
            self.sprite = SPRITE_ENEMY_3
            self.color = ENEMY_3_COLOR
            self.score_value = 30
        elif row < 3:
            self.sprite = SPRITE_ENEMY_2
            self.color = ENEMY_2_COLOR
            self.score_value = 20
        else:
            self.sprite = SPRITE_ENEMY_1
            self.color = ENEMY_1_COLOR
            self.score_value = 10

        self.score_value *= level

        self.animation_offset = random.randint(0, 10)
        self.active = True
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(2000, 5000) // level
        self.is_on_cooldown = False
        self.hit_flash = 0

    def draw(self, surface, time):
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 3

        scaled_sprite = pygame.transform.scale(self.sprite, (self.width + 5, self.height + 5))
        surface.blit(scaled_sprite, (self.x + sine_offset, self.y))

        # Hit flash
        if self.hit_flash > 0:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, int(255 * self.hit_flash / 20)))
            surface.blit(flash_surface, (self.x + sine_offset, self.y))
            self.hit_flash -= 1

        self.rect = pygame.Rect(self.x + sine_offset, self.y, self.width + 5, self.height + 5)


class UFO:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.y = 50
        self.speed = 6
        self.move_down_step = 20
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(10000, 20000)
        self.active = True
        self.score_value = 500
        self.x = 20
        self.direction = 1
        self.rect = pygame.Rect(0, self.y, self.width, self.height)
        self.pulse = 0

    def update(self):
        self.x += self.speed * self.direction

        if self.x < 10:
            self.x = 10
            self.y += self.move_down_step
            self.direction = 1
        elif self.x > WIDTH - self.width - 10:
            self.x = WIDTH - self.width - 10
            self.y += self.move_down_step
            self.direction = -1

        if self.y > HEIGHT - 150:
            self.active = False

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 255

    def draw(self, surface):
        scaled_sprite = pygame.transform.scale(SPRITE_UFO, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))

        # UFO glow - FIXED: RGB color only
        pulse_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 200)
        glow_color = (200, 200, 255)
        pygame.draw.circle(surface, glow_color,
                           (self.x + self.width // 2, self.y + self.height // 2),
                           self.width // 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders - Enhanced")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.sound_manager = SoundManager()

        self.state = "START"
        self.score = 0
        self.high_scores = self.load_high_scores()
        self.level = 1
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.ufo = None
        self.particles = []
        self.stars = [Star() for _ in range(100)]
        self.barriers = []

        self.enemy_direction = 1
        self.enemy_move_speed = 2
        self.enemy_drop_distance = 10
        self.last_enemy_move_time = 0

        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(20000, 40000)

        self.combo_display_time = 0
        self.last_score_display = 0
        self.mega_combo = False

        self.init_enemies()
        self.init_barriers()

    def load_high_scores(self):
        defaults = {"high_score": 0, "total_kills": 0, "levels_completed": 0}
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    loaded_data = json.load(f)
                    defaults.update(loaded_data)
                    return defaults
        except:
            pass
        return defaults

    def save_high_scores(self):
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f)
        except:
            pass

    def init_enemies(self):
        self.enemies = []
        padding_x, padding_y, start_x, start_y = 10, 15, 50, 60
        for row in range(NUM_ENEMIES_ROWS):
            for col in range(NUM_ENEMIES_COLS):
                x = start_x + col * (40 + padding_x)
                y = start_y + row * (40 + padding_y)
                self.enemies.append(Invader(x, y, row, col, self.level))
        self.enemy_move_speed = 2 + (self.level * 0.5)

    def init_barriers(self):
        self.barriers = []
        barrier_spacing = WIDTH // (4 + 1)
        for i in range(4):
            barrier_x = barrier_spacing * (i + 1) - 30
            barrier_y = HEIGHT - 120
            self.barriers.append(Barrier(barrier_x, barrier_y))

    def spawn_explosion(self, x, y, color, count=15, explosion_type='normal'):
        """Create explosion with multiple particle types for visual variety"""
        for i in range(count):
            # Vary particle types for richer effect
            if i % 3 == 0:
                particle_type = 'arc'
                particle_speed = 4
                particle_size = 4
            elif i % 3 == 1:
                particle_type = 'spark'
                particle_speed = 6
                particle_size = 2
            else:
                particle_type = 'normal'
                particle_speed = 3
                particle_size = 3

            # Add color variation
            if explosion_type == 'enemy':
                color_variation = random.choice([color, (255, 200, 0), (255, 100, 0)])
            elif explosion_type == 'mega':
                color_variation = random.choice(EXPLOSION_COLORS)
            else:
                color_variation = color

            self.particles.append(Particle(
                x + random.randint(-5, 5),
                y + random.randint(-5, 5),
                color_variation,
                particle_speed,
                particle_size,
                particle_type
            ))

    def spawn_mega_explosion(self, x, y):
        for color in EXPLOSION_COLORS:
            for _ in range(20):
                self.particles.append(Particle(x, y, color, random.uniform(3, 6), random.randint(3, 6), 'mega'))

    def draw_particle_glow(self, x, y, radius, color):
        """Draw a glow effect around explosion center"""
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color[:3], 100), (radius, radius), radius)
        pygame.draw.circle(glow_surface, (*color[:3], 50), (radius, radius), radius * 0.8)
        self.screen.blit(glow_surface, (x - radius, y - radius), special_flags=pygame.BLEND_ADD)

    def reset_game(self):
        self.player = Player()
        self.score = 0
        self.level = 1
        self.init_enemies()
        self.init_barriers()
        self.enemy_move_speed = 2
        self.enemy_direction = 1
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.particles = []
        self.ufo = None
        self.state = "PLAYING"
        self.combo_display_time = 0
        self.mega_combo = False

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if self.state == "START":
            if keys[pygame.K_SPACE]:
                self.reset_game()
            if keys[pygame.K_m]:
                self.sound_manager.muted = not self.sound_manager.muted

        elif self.state == "PLAYING":
            current_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.player.shoot(self, current_time)

            if keys[pygame.K_b] and self.player.bomb_available:
                self.activate_bomb()
                self.player.bomb_available = False

            self.player.update(keys, current_time)

            if keys[pygame.K_p]:
                self.state = "PAUSE"

        elif self.state == "PAUSE":
            if keys[pygame.K_p]:
                self.state = "PLAYING"
            elif keys[pygame.K_ESCAPE]:
                self.state = "START"

        elif self.state in ["GAMEOVER", "VICTORY"]:
            if keys[pygame.K_SPACE]:
                self.reset_game()
            elif keys[pygame.K_ESCAPE]:
                self.state = "START"

    def activate_bomb(self):
        for bullet in self.enemy_bullets[:]:
            bullet.active = False
            self.spawn_explosion(bullet.x, bullet.y, ENEMY_BULLET_COLOR, 5)

        for enemy in self.enemies:
            if enemy.active:
                enemy.active = False
                self.score += enemy.score_value
                self.spawn_explosion(enemy.x, enemy.y, enemy.color, 10)

        self.sound_manager.play_explosion(100)
        self.spawn_mega_explosion(WIDTH // 2, HEIGHT // 2)

    def update_logic(self):
        current_time = pygame.time.get_ticks()

        for star in self.stars:
            star.update()

        if self.state == "PLAYING":
            # UFO
            if self.ufo_spawn_time == 0:
                self.ufo_spawn_time = current_time
            elif current_time - self.ufo_spawn_time > self.ufo_spawn_interval:
                self.ufo = UFO()
                self.ufo_spawn_time = current_time
                self.ufo_spawn_interval = random.randint(20000, 40000)

            if self.ufo and self.ufo.active:
                self.ufo.update()
                if random.random() < 0.005:
                    b = Bullet(self.ufo.x + self.ufo.width // 2,
                               self.ufo.y + self.ufo.height, is_player=False)
                    self.enemy_bullets.append(b)
                    self.sound_manager.play_enemy_shoot()

                if not self.ufo.active:
                    self.ufo = None

            # Enemy Movement
            move_step = self.enemy_move_speed * self.enemy_direction
            edge_reached = False

            for enemy in self.enemies:
                if enemy.active:
                    enemy.x += move_step
                    if (enemy.x + enemy.width > WIDTH - 30 and self.enemy_direction == 1) or \
                            (enemy.x < 30 and self.enemy_direction == -1):
                        edge_reached = True
                        break

            if edge_reached:
                self.enemy_direction *= -1
                for enemy in self.enemies:
                    enemy.y += self.enemy_drop_distance
                    enemy.x += self.enemy_move_speed * self.enemy_direction * 2

            # Enemy Shooting
            bullets_to_add = 0
            for enemy in self.enemies:
                if enemy.active and not enemy.is_on_cooldown:
                    if current_time - enemy.last_shot_time > enemy.shot_cooldown:
                        if random.random() < 0.03 + (self.level * 0.01):
                            bullets_to_add += 1

            bullets_to_add = min(bullets_to_add, MAX_ENEMY_BULLETS - len(self.enemy_bullets))
            if bullets_to_add > 0 and len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                active_enemies = [e for e in self.enemies if e.active and not e.is_on_cooldown]
                if active_enemies:
                    selected = random.sample(active_enemies, min(len(active_enemies), bullets_to_add))
                    for enemy in selected:
                        if len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                            b = Bullet(enemy.x + enemy.width // 2, enemy.y + enemy.height, is_player=False)
                            self.enemy_bullets.append(b)
                            enemy.last_shot_time = current_time
                            enemy.is_on_cooldown = True
                            self.sound_manager.play_enemy_shoot()

            for enemy in self.enemies:
                if enemy.is_on_cooldown and (current_time - enemy.last_shot_time > enemy.shot_cooldown * 1.5):
                    enemy.is_on_cooldown = False

            # Update Bullets
            for b in self.player_bullets[:]:
                b.update()
                if not b.active:
                    self.player_bullets.remove(b)

            for b in self.enemy_bullets[:]:
                b.update()
                if not b.active:
                    self.enemy_bullets.remove(b)

            # Update Powerups
            for p in self.powerups[:]:
                p.update()
                if not p.active:
                    self.powerups.remove(p)
                else:
                    if p.rect.colliderect(self.player.rect):
                        self.player.powerups.append(p.type)

                        if p.type == POWERUP_SHIELD:
                            self.player.shield_active = True
                            self.player.shield_timer = current_time
                        elif p.type == POWERUP_BOMB:
                            self.player.bomb_available = True
                            self.player.bomb_timer = current_time
                        elif p.type == POWERUP_SCORE:
                            self.score += 500

                        self.sound_manager.play_powerup()
                        self.powerups.remove(p)
                        # Location 4: Powerup Collection - ENHANCED
                        self.spawn_explosion(p.x, p.y, POWERUP_COLOR, count=15, explosion_type='mega')
                        self.draw_particle_glow(p.x, p.y, 20, POWERUP_COLOR)

            # Update Barriers
            for barrier in self.barriers:
                barrier.update()

            # COLLISIONS
            # Player Bullets vs Enemies
            for b in self.player_bullets[:]:
                hit = False
                for enemy in self.enemies:
                    if enemy.active and b.rect.colliderect(enemy.rect):
                        enemy.active = False
                        b.active = False
                        enemy.hit_flash = 20

                        combo_multiplier = max(1, self.player.combo)
                        self.score += enemy.score_value * combo_multiplier

                        self.player.combo = min(self.player.combo + 1, 10)
                        self.player.combo_timer = current_time
                        self.combo_display_time = current_time

                        self.sound_manager.play_combo(self.player.combo)
                        # Location 1: Enemy destroyed - ENHANCED
                        self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color,
                                             count=20, explosion_type='enemy')
                        self.draw_particle_glow(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, 25,
                                                enemy.color)
                        self.sound_manager.play_explosion()

                        if self.player.combo >= 5 and not self.mega_combo:
                            self.mega_combo = True
                            self.spawn_mega_explosion(enemy.x, enemy.y)

                        if random.random() < 0.1:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))

                        hit = True
                        break

                if not hit:
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            # Location 2: Bullet hits barrier - ENHANCED
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR, count=10, explosion_type='barrier')
                            self.draw_particle_glow(b.x, b.y, 20, BARRIER_COLOR)
                            break

                    if not b.active:
                        for eb in self.enemy_bullets[:]:
                            if b.rect.colliderect(eb.rect):
                                b.active = False
                                eb.active = False
                                # Location 3: Bullet collision - ENHANCED
                                self.spawn_explosion(b.x, b.y, (255, 255, 255), count=15, explosion_type='mega')
                                self.draw_particle_glow(b.x, b.y, 15, (255, 255, 255))
                                break

            # Enemy Bullets vs Player
            for b in self.enemy_bullets[:]:
                if b.rect.colliderect(self.player.rect):
                    b.active = False
                    if self.player.shield_active:
                        self.player.shield_active = False
                        # Location 5: Shield blocks bullet - ENHANCED
                        self.spawn_explosion(self.player.x, self.player.y, (100, 255, 255), count=25,
                                             explosion_type='mega')
                        self.draw_particle_glow(self.player.x, self.player.y, 30, (100, 255, 255))
                        self.player.hit_flash = 20
                    else:
                        self.player_hit()
                    break

            # Enemy Bullets vs Barriers
            for b in self.enemy_bullets[:]:
                for barrier in self.barriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        # Location 10: Enemy bullet hits barrier - ENHANCED
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, count=10, explosion_type='barrier')
                        self.draw_particle_glow(b.x, b.y, 20, BARRIER_COLOR)
                        break

            # Enemies vs Player
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    # Location 7: Enemy touches player - ENHANCED
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color, count=20, explosion_type='enemy')
                    self.draw_particle_glow(enemy.x, enemy.y, 25, enemy.color)
                    enemy.active = False
                    break

            # UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        # Location 8: UFO destroyed - ENHANCED
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2,
                                             UFO_COLOR, count=40, explosion_type='mega')
                        self.draw_particle_glow(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2, 40,
                                                UFO_COLOR)
                        self.sound_manager.play_explosion()
                        self.ufo.active = False
                        self.ufo = None
                        break

            # Level Complete
            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 1
                self.init_enemies()
                self.score += 1000
                # Location 9: Level complete - ENHANCED
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), count=50, explosion_type='mega')
                self.draw_particle_glow(WIDTH // 2, HEIGHT // 2, 50, (255, 255, 255))
                self.sound_manager.play_level_up()

            # Particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

    def player_hit(self):
        # Location 6: Player dies - ENHANCED
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color,
            count=30,
            explosion_type='mega'
        )
        self.draw_particle_glow(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            35,
            self.player.color
        )
        self.sound_manager.play_explosion()
        self.player.lives -= 1
        self.player.combo = 0
        self.player.powerups = []
        self.player.shield_active = False
        self.player.hit_flash = 20

        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            current_high = self.high_scores.get("high_score", 0)
            self.high_scores["high_score"] = max(current_high, self.score)

            current_kills = self.high_scores.get("total_kills", 0)
            self.high_scores["total_kills"] = current_kills + (NUM_ENEMIES_COLS * NUM_ENEMIES_ROWS * self.level)

            current_levels = self.high_scores.get("levels_completed", 0)
            self.high_scores["levels_completed"] = current_levels + self.level

            self.save_high_scores()
            self.sound_manager.play_game_over()

    def draw(self):
        # Background
        bg_surface = pygame.Surface((WIDTH, HEIGHT))
        bg_surface.fill(BG_COLOR)

        # Stars
        for star in self.stars:
            star.draw(bg_surface)

        self.screen.blit(bg_surface, (0, 0))

        if self.state == "START":
            self.draw_menu("NEON INVADERS", "Press SPACE to Start",
                           "Arrows: Move | Space: Shoot | B: Bomb | P: Pause | M: Mute")
        elif self.state == "PLAYING":
            self.player.draw(self.screen)

            for barrier in self.barriers:
                if barrier.active:
                    barrier.draw(self.screen)

            for enemy in self.enemies:
                if enemy.active:
                    enemy.draw(self.screen, pygame.time.get_ticks())

            if self.ufo and self.ufo.active:
                self.ufo.draw(self.screen)

            for b in self.player_bullets:
                b.draw(self.screen)

            for b in self.enemy_bullets:
                b.draw(self.screen)

            for p in self.powerups:
                p.draw(self.screen)

            for p in self.particles:
                p.draw(self.screen)

            # Combo display
            if self.player.combo > 0 and pygame.time.get_ticks() - self.combo_display_time < 1000:
                combo_text = f"COMBO x{self.player.combo}!"
                combo_surf = self.large_font.render(combo_text, True, (255, 215, 0))
                combo_rect = combo_surf.get_rect(center=(WIDTH // 2, 100))
                self.screen.blit(combo_surf, combo_rect)

            self.draw_hud()

        elif self.state == "PAUSE":
            self.draw_menu("PAUSED", "Press P to Resume | ESC to Quit")

        elif self.state in ["GAMEOVER", "VICTORY"]:
            title = "GAME OVER" if self.state == "GAMEOVER" else "LEVEL COMPLETE!"
            color = (255, 50, 50) if self.state == "GAMEOVER" else (50, 255, 50)
            self.draw_menu(title, f"Score: {self.score}",
                           f"High Score: {self.high_scores['high_score']}")

        pygame.display.flip()

    def draw_menu(self, title, sub1, sub2=""):
        title_surf = self.large_font.render(title, True, PLAYER_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(title_surf, title_rect)

        sub1_surf = self.font.render(sub1, True, TEXT_COLOR)
        sub1_rect = sub1_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.screen.blit(sub1_surf, sub1_rect)

        if sub2:
            sub2_surf = self.font.render(sub2, True, (200, 200, 200))
            sub2_rect = sub2_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            self.screen.blit(sub2_surf, sub2_rect)

    def draw_hud(self):
        score_surf = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, TEXT_COLOR)
        level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
        combo_surf = self.font.render(f"COMBO: x{self.player.combo}", True, (255, 215, 0))

        powerup_text = ""
        if POWERUP_RAPID in self.player.powerups: powerup_text += "R "
        if POWERUP_SPREAD in self.player.powerups: powerup_text += "S "
        if self.player.shield_active: powerup_text += "H "
        if self.player.bomb_available: powerup_text += "B "
        pu_surf = self.font.render(f"PU: {powerup_text or '-'}", True, POWERUP_COLOR)

        # FIX: Use .get() to prevent KeyError if key is missing
        high_score_val = self.high_scores.get('high_score', 0)
        high_score_surf = self.font.render(f"HI: {high_score_val}", True, (255, 215, 0))

        self.screen.blit(score_surf, (15, 10))
        self.screen.blit(lives_surf, (WIDTH - 160, 10))
        self.screen.blit(level_surf, (WIDTH // 2 - 60, 10))
        self.screen.blit(combo_surf, (15, 35))
        self.screen.blit(pu_surf, (WIDTH - 160, 35))
        self.screen.blit(high_score_surf, (15, 60))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.USEREVENT:
                    pass

            self.handle_input()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)

        self.save_high_scores()
        pygame.quit()


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.2, 1.5)
        self.brightness = random.randint(100, 255)
        self.twinkle = random.uniform(0, math.pi * 2)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
        self.twinkle += 0.02

    def draw(self, surface):
        brightness = int(self.brightness * (0.5 + 0.5 * math.sin(self.twinkle)))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


if __name__ == "__main__":
    game = Game()
    game.run()
