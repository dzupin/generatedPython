# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 32768 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Qwen3-VL-235B-A22B-Instruct-UD-Q3_K_XL-00001-of-00003.gguf --mmproj /AI/models/Qwen3-VL-235B-A22B-mmproj-BF16.gguf


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

# Colors
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
COMBO_COLOR = (255, 165, 0)  # Orange

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"
POWERUP_LASER = "LASER"

# New game mechanics
BONUS_MULTIPLIER = 1.5  # Score multiplier for consecutive levels
LIVES_PER_LEVEL = 1     # Extra life per level completed
MAX_COMBO = 15          # Maximum combo value

# --- SPRITE GENERATOR (Procedural Pixel Art) ---
def create_pixel_art(width, height, color, pattern):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, color, (x * 2, y * 2, 2, 2))
    return surface

# Enhanced sprite patterns
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
        self.channels = [pygame.mixer.Channel(i) for i in range(6)]
        self.sample_rate = 44100

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

    def play_shoot(self):
        self.channels[0].play(self.create_tone(880, 0.1, 0.15, 'square'))
        self.channels[1].play(self.create_tone(1100, 0.1, 0.15, 'square'))

    def play_enemy_shoot(self):
        self.channels[2].play(self.create_tone(200, 0.2, 0.1, 'sawtooth'))

    def play_explosion(self):
        duration = 0.25
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-16384, 16384) for _ in range(samples * 2)]
        self.channels[3].play(pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        ))

    def play_powerup(self):
        self.channels[4].play(self.create_tone(600, 0.1, 0.2, 'square'))
        self.channels[5].play(self.create_tone(400, 0.1, 0.2, 'square'))

    def play_combo(self, combo):
        # Higher pitch for higher combo
        freq = 600 + (combo * 50)
        self.channels[4].play(self.create_tone(freq, 0.1, 0.2, 'square'))

    def play_level_up(self):
        for freq in [400, 800, 1200]:
            self.channels[4].play(self.create_tone(freq, 0.15, 0.3, 'square'))
            pygame.time.delay(100)

    def play_laser(self):
        self.channels[2].play(self.create_tone(1000, 0.05, 0.1, 'square'))

# --- CLASSES ---

class Particle:
    def __init__(self, x, y, color, speed=2):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed_mag = random.uniform(1, speed * 2)
        self.vx = math.cos(angle) * speed_mag
        self.vy = math.sin(angle) * speed_mag
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.gravity = 0.1
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * self.life)
        color = (*self.color[:3], alpha) if len(self.color) > 3 else self.color
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

class LaserBeam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.active = True
        self.color = (0, 255, 255)
        self.particles = []

    def update(self):
        self.active = False  # One-shot laser

    def draw(self, surface):
        # Draw laser beam
        pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, 0), self.width)

        # Add particles at the top
        if random.random() < 0.1:
            self.particles.append(Particle(self.x, 0, self.color, speed=1))

        for p in self.particles:
            p.update()
            p.draw(surface)
        self.particles = [p for p in self.particles if p.life > 0]

class Bullet:
    def __init__(self, x, y, is_player=False, speed=BULLET_SPEED):
        self.x, self.y = x, y
        self.width, self.height = 4, 10
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -speed if is_player else ENEMY_BULLET_SPEED
        self.active = True
        self.trail = []
        self.angle = 0
        self.scale = 1.0

    def update(self):
        # Trail effect
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        # Pulsing effect
        self.scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.05)

        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail)))
            s = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (1, 1), 1)
            surface.blit(s, (int(tx) - 1, int(ty) - 1))

        # Draw main bullet with scaling
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        pygame.draw.rect(surface, self.color,
                         (self.x - scaled_width//2, self.y,
                          scaled_width, scaled_height))
        pygame.draw.rect(surface, (255, 255, 200),
                         (self.x - scaled_width//2 + 1, self.y + 1,
                          scaled_width - 2, scaled_height - 2))

class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choices(
            [POWERUP_RAPID, POWERUP_SPREAD, POWERUP_SHIELD, POWERUP_LASER],
            weights=[0.3, 0.3, 0.3, 0.1],
            k=1
        )[0]
        self.width, self.height = 20, 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.active = True
        self.color = POWERUP_COLOR
        self.vy = 2
        self.angle = 0
        self.pulse = 0

    def update(self):
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        self.angle += 0.1
        self.pulse = math.sin(pygame.time.get_ticks() * 0.02) * 2
        if self.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        # Pulsing size
        scale = 1.0 + self.pulse * 0.1
        scaled_width = int(self.width * scale)
        scaled_height = int(self.height * scale)

        s = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)

        # Glowing effect
        glow_size = 3
        pygame.draw.ellipse(s, (*self.color[:3], 100),
                           (glow_size, glow_size, scaled_width - glow_size*2, scaled_height - glow_size*2))

        # Main body
        pygame.draw.ellipse(s, self.color,
                           (0, 0, scaled_width, scaled_height))

        # Inner highlight
        pygame.draw.ellipse(s, (255, 255, 255),
                           (4, 4, scaled_width - 8, scaled_height - 8))

        # Rotate text inside
        text_map = {
            POWERUP_RAPID: "R",
            POWERUP_SPREAD: "S",
            POWERUP_SHIELD: "H",
            POWERUP_LASER: "L"
        }
        txt = self.font.render(text_map[self.type], True, (0, 0, 0))
        txt = pygame.transform.rotate(txt, self.angle * 180 / math.pi)
        s.blit(txt, (scaled_width // 2 - txt.get_width() // 2,
                     scaled_height // 2 - txt.get_height() // 2))

        surface.blit(s, (self.x - (scaled_width - self.width) // 2,
                         self.y - (scaled_height - self.height) // 2))

    @property
    def font(self):
        return pygame.font.SysFont("Arial", int(14 * (1 + self.pulse * 0.1)), bold=True)

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
        self.hit_effect = 0

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
                        'health': 3  # Make barriers more durable
                    })

    def update(self):
        active_segments = [s for s in self.segments if s['active']]
        if not active_segments:
            self.active = False
            return

        # Visual hit effect
        self.hit_effect = max(0, self.hit_effect - 0.1)

        # Recalculate bounding box
        min_x = min(s['x'] for s in active_segments)
        min_y = min(s['y'] for s in active_segments)
        max_x = max(s['x'] + s['width'] for s in active_segments)
        max_y = max(s['y'] + s['height'] for s in active_segments)
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def take_damage(self, bullet_rect):
        for segment in self.segments:
            if segment['active']:
                seg_rect = pygame.Rect(segment['x'], segment['y'],
                                      segment['width'], segment['height'])
                if bullet_rect.colliderect(seg_rect):
                    segment['health'] -= 1
                    if segment['health'] <= 0:
                        segment['active'] = False
                        self.hit_effect = 5
                    return True
        return False

    def draw(self, surface):
        for segment in self.segments:
            if segment['active']:
                # Gradient effect with damage indication
                if segment['health'] < 3:
                    color = (255, 255 * (segment['health'] / 3), 100 * (segment['health'] / 3))
                else:
                    color = BARRIER_COLOR

                pygame.draw.rect(surface, color,
                                 (segment['x'], segment['y'],
                                  segment['width'], segment['height']))

        # Simplified hit effect without alpha
        if self.hit_effect > 0:
            # Just draw a slightly different color to indicate hit
            hit_color = (50, 255, 50)  # Lighter green
            pygame.draw.rect(surface, hit_color, (self.x, self.y, self.width, self.height))


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

        # Enhanced powerups
        self.powerups = []
        self.shield_active = False
        self.shield_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.laser_cooldown = 0
        self.laser_active = False

    def update(self, keys, current_time):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

        # Combo decay
        if current_time - self.combo_timer > 1000:
            self.combo = 0

        # Shield decay
        if self.shield_active and current_time - self.shield_timer > 10000:
            self.shield_active = False

        # Laser cooldown
        if current_time - self.laser_cooldown > 2000:
            self.laser_active = False

    def shoot(self, game, current_time):
        if POWERUP_RAPID in self.powerups:
            self.shoot_delay = 150
        else:
            self.shoot_delay = 350

        if current_time - self.last_shot > self.shoot_delay:
            # Laser powerup
            if POWERUP_LASER in self.powerups and not self.laser_active:
                laser = LaserBeam(self.x + self.width // 2, self.y)
                game.player_bullets.append(laser)
                self.laser_active = True
                self.laser_cooldown = current_time
                game.sound_manager.play_laser()
                return

            # Spread Shot
            if POWERUP_SPREAD in self.powerups:
                for angle_offset in [-15, 0, 15]:
                    bx = self.x + self.width // 2
                    by = self.y
                    b = Bullet(bx, by, is_player=True)
                    rad = math.radians(angle_offset)
                    b.velocity_y = -BULLET_SPEED * math.cos(rad)
                    b.velocity_x = BULLET_SPEED * math.sin(rad)
                    game.player_bullets.append(b)
            else:
                bullet_x = self.x + self.width // 2
                bullet_y = self.y
                bullet = Bullet(bullet_x, bullet_y, is_player=True)
                game.player_bullets.append(bullet)

            self.last_shot = current_time
            game.sound_manager.play_shoot()

    def draw(self, surface):
        # Draw Shield if active
        if self.shield_active:
            shield_radius = self.width // 2 + 5
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 255, 255, 150),
                              (shield_radius, shield_radius), shield_radius, 2)
            surface.blit(shield_surface, (self.x + self.width//2 - shield_radius,
                                         self.y + self.height//2 - shield_radius))

        # Draw Sprite (Scaled)
        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))

        # Enhanced Engine Glow
        glow_size = 5 + int(math.sin(pygame.time.get_ticks() * 0.02) * 2)
        glow_color = (255, 200, 0) if not self.laser_active else (0, 255, 255)
        pygame.draw.circle(surface, glow_color,
                          (self.x + self.width // 2, self.y + self.height), glow_size)

        # Powerup indicators
        if POWERUP_LASER in self.powerups:
            laser_indicator = pygame.Surface((20, 5), pygame.SRCALPHA)
            pygame.draw.rect(laser_indicator, (0, 255, 255, 150), (0, 0, 20, 5))
            surface.blit(laser_indicator, (self.x + 5, self.y - 10))

class Invader:
    def __init__(self, x, y, row, col, level):
        self.x, self.y = x, y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        self.level = level

        # Assign sprite based on row
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
        self.health = 1  # Base health
        self.max_health = 1

        # Increase health for higher levels
        if level > 3:
            self.max_health = 2
            self.health = 2
        if level > 6:
            self.max_health = 3
            self.health = 3

        self.rect = pygame.Rect(x, y, self.width, self.height)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.active = False
            return True
        return False

    def draw(self, surface, time):
        # Animation offset (wobble)
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 3

        # Draw scaled sprite
        scaled_sprite = pygame.transform.scale(self.sprite, (self.width + 5, self.height + 5))
        surface.blit(scaled_sprite, (self.x + sine_offset, self.y))

        # Health bar
        if self.max_health > 1:
            health_width = self.width * (self.health / self.max_health)
            pygame.draw.rect(surface, (255, 0, 0),
                            (self.x + sine_offset, self.y - 5, self.width, 3))
            pygame.draw.rect(surface, (0, 255, 0),
                            (self.x + sine_offset, self.y - 5, health_width, 3))

        # Update rect for collision (using wobbly position)
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
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        # UFO gets faster over time
        elapsed = pygame.time.get_ticks() - self.spawn_time
        speed_multiplier = 1.0 + (elapsed / 10000)  # Speed up over 10 seconds
        self.speed = 6 * min(speed_multiplier, 2.0)

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

    def draw(self, surface):
        # Flicker effect
        if (pygame.time.get_ticks() % 200) < 100:
            scaled_sprite = pygame.transform.scale(SPRITE_UFO, (self.width, self.height))
            surface.blit(scaled_sprite, (self.x, self.y))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.2, 1.5)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        # Simple white stars
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.size)



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.sound_manager = SoundManager()

        self.state = "START"
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.ufo = None
        self.particles = []
        self.stars = [Star() for _ in range(120)]
        self.barriers = []

        self.enemy_direction = 1
        self.enemy_move_speed = 2
        self.enemy_drop_distance = 10
        self.last_enemy_move_time = 0

        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(20000, 40000)

        self.screen_shake = 0
        self.game_over_animation = 0
        self.victory_animation = 0
        self.last_combo_display = 0

        self.init_enemies()
        self.init_barriers()

    def load_high_score(self):
        try:
            with open('highscore.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        with open('highscore.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)

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

    def spawn_explosion(self, x, y, color):
        for _ in range(12):
            self.particles.append(Particle(x, y, color))

    def reset_game(self):
        self.player = Player()
        self.score, self.level = 0, 1
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
        self.game_over_animation = 0
        self.victory_animation = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.state == "START":
            if keys[pygame.K_SPACE]:
                self.reset_game()
        elif self.state == "PLAYING":
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_SPACE]:
                self.player.shoot(self, current_time)
            self.player.update(keys, current_time)

            if keys[pygame.K_p]:
                self.state = "PAUSE"
        elif self.state == "PAUSE":
            if keys[pygame.K_p]:
                self.state = "PLAYING"
            elif keys[pygame.K_ESCAPE]:
                self.state = "START"
        elif self.state in ["GAMEOVER", "VICTORY"]:
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.reset_game()
            elif keys[pygame.K_ESCAPE]:
                self.state = "START"

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
                            b = Bullet(enemy.x + enemy.width // 2,
                                     enemy.y + enemy.height, is_player=False)
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
                        self.sound_manager.play_powerup()
                        self.powerups.remove(p)
                        self.spawn_explosion(p.x, p.y, POWERUP_COLOR)

            # Update Barriers
            for barrier in self.barriers:
                barrier.update()

            # COLLISIONS
            # Player Bullets vs Enemies
            for b in self.player_bullets[:]:
                hit = False
                for enemy in self.enemies:
                    if enemy.active and b.rect.colliderect(enemy.rect):
                        if enemy.take_damage():
                            b.active = False
                            self.score += enemy.score_value * max(1, self.player.combo)
                            self.player.combo = min(self.player.combo + 1, MAX_COMBO)
                            self.player.combo_timer = current_time
                            self.sound_manager.play_combo(self.player.combo)
                            self.spawn_explosion(enemy.x + enemy.width // 2,
                                                enemy.y + enemy.height // 2, enemy.color)
                            self.sound_manager.play_explosion()

                            if random.random() < 0.15:
                                self.powerups.append(PowerUp(enemy.x, enemy.y))

                        hit = True
                        break

                if not hit:
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                            break

                    if not b.active:
                        for eb in self.enemy_bullets[:]:
                            if b.rect.colliderect(eb.rect):
                                b.active = False
                                eb.active = False
                                self.spawn_explosion(b.x, b.y, (255, 255, 255))
                                break

            # Enemy Bullets vs Player
            for b in self.enemy_bullets[:]:
                if b.rect.colliderect(self.player.rect):
                    b.active = False
                    if self.player.shield_active:
                        self.player.shield_active = False
                        self.spawn_explosion(self.player.x, self.player.y, (100, 255, 255))
                        self.screen_shake = 5
                    else:
                        self.player_hit()
                    break

            # Enemy Bullets vs Barriers
            for b in self.enemy_bullets[:]:
                for barrier in self.barriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                        break

            # Enemies vs Player
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color)
                    enemy.active = False
                    break

            # UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value * max(1, self.player.combo)
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2,
                                            self.ufo.y + self.ufo.height // 2, UFO_COLOR)
                        self.sound_manager.play_explosion()
                        self.ufo.active = False
                        self.ufo = None
                        break

            # Level Complete
            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 1
                self.player.lives += LIVES_PER_LEVEL
                self.score += int(1000 * BONUS_MULTIPLIER * self.level)
                self.sound_manager.play_level_up()
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255))
                self.init_enemies()

            # Particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            # Screen Shake
            if self.screen_shake > 0:
                self.screen_shake -= 0.5
                if self.screen_shake < 0: self.screen_shake = 0

    def player_hit(self):
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color
        )
        self.sound_manager.play_explosion()
        self.player.lives -= 1
        self.player.combo = 0
        self.player.powerups = []
        self.player.shield_active = False
        self.screen_shake = 10

        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def draw(self):
        # Screen Shake Effect
        shake_offset = (random.randint(-int(self.screen_shake), int(self.screen_shake)),
                        random.randint(-int(self.screen_shake), int(self.screen_shake)))

        # Background
        bg_surface = pygame.Surface((WIDTH, HEIGHT))
        bg_surface.fill(BG_COLOR)

        # Stars
        for star in self.stars:
            star.draw(bg_surface)

        # Apply Shake
        self.screen.blit(bg_surface, shake_offset)

        if self.state == "START":
            self.draw_menu("NEON INVADERS", "Press SPACE to Start",
                          "Arrows: Move | Space: Shoot | P: Pause | L: Laser (Powerup)")
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

            # HUD
            self.draw_hud()

            # Combo display
            if self.player.combo > 0 and pygame.time.get_ticks() - self.last_combo_display < 1000:
                combo_text = self.big_font.render(f"COMBO x{self.player.combo}", True, COMBO_COLOR)
                combo_text.set_alpha(int(255 * (1 - (pygame.time.get_ticks() - self.last_combo_display) / 1000)))
                text_rect = combo_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
                self.screen.blit(combo_text, text_rect)
        elif self.state == "PAUSE":
            self.draw_menu("PAUSED", "Press P to Resume | ESC to Quit")
        elif self.state == "GAMEOVER":
            self.draw_menu("GAME OVER", f"Final Score: {self.score}", "High Score: " + str(self.high_score))
        elif self.state == "VICTORY":
            self.draw_menu("STAGE CLEAR", f"Score: {self.score}", "High Score: " + str(self.high_score))

        # Enhanced Vignette
        self.draw_vignette()

        pygame.display.flip()

    def draw_menu(self, title, sub1, sub2=""):
        # Background fade effect
        bg_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*BG_COLOR[:3], 200), (0, 0, WIDTH, HEIGHT))

        self.screen.blit(bg_surface, (0, 0))

        # Title with glow effect
        title_surf = self.big_font.render(title, True, PLAYER_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

        # Glow behind text
        glow = self.big_font.render(title, True, (100, 255, 255))
        glow.set_alpha(100)
        glow_rect = glow.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        self.screen.blit(glow, glow_rect)
        self.screen.blit(title_surf, title_rect)

        # Subtext
        sub1_surf = self.font.render(sub1, True, TEXT_COLOR)
        sub1_rect = sub1_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(sub1_surf, sub1_rect)

        if sub2:
            sub2_surf = self.font.render(sub2, True, (200, 200, 200))
            sub2_rect = sub2_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            self.screen.blit(sub2_surf, sub2_rect)

    def draw_hud(self):
        # Score
        score_surf = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        score_rect = score_surf.get_rect(topleft=(15, 10))
        # Glow effect
        pygame.draw.rect(self.screen, (100, 255, 100, 100), score_rect.inflate(4, 4))
        self.screen.blit(score_surf, score_rect)

        # Lives
        lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, TEXT_COLOR)
        lives_rect = lives_surf.get_rect(topleft=(WIDTH - 160, 10))
        pygame.draw.rect(self.screen, (255, 100, 100, 100), lives_rect.inflate(4, 4))
        self.screen.blit(lives_surf, lives_rect)

        # Level
        level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
        level_rect = level_surf.get_rect(center=(WIDTH // 2, 10))
        pygame.draw.rect(self.screen, (100, 100, 255, 100), level_rect.inflate(4, 4))
        self.screen.blit(level_surf, level_rect)

        # Combo
        combo_surf = self.font.render(f"COMBO: x{self.player.combo}", True, COMBO_COLOR)
        combo_rect = combo_surf.get_rect(topleft=(15, 35))
        self.screen.blit(combo_surf, combo_rect)

        # Powerups
        powerup_text = ""
        if POWERUP_RAPID in self.player.powerups: powerup_text += "R "
        if POWERUP_SPREAD in self.player.powerups: powerup_text += "S "
        if self.player.shield_active: powerup_text += "H "
        if POWERUP_LASER in self.player.powerups: powerup_text += "L "
        pu_surf = self.font.render(f"PU: {powerup_text or '-'}", True, POWERUP_COLOR)
        pu_rect = pu_surf.get_rect(topleft=(WIDTH - 160, 35))
        self.screen.blit(pu_surf, pu_rect)

        # Laser cooldown indicator
        if POWERUP_LASER in self.player.powerups:
            current_time = pygame.time.get_ticks()
            cooldown_left = max(0, 2000 - (current_time - self.player.laser_cooldown))
            cooldown_pct = cooldown_left / 2000
            cooldown_width = 100 * cooldown_pct
            pygame.draw.rect(self.screen, (50, 50, 50),
                            (WIDTH - 150, 60, 100, 10))
            pygame.draw.rect(self.screen, (0, 255, 255),
                            (WIDTH - 150, 60, cooldown_width, 10))

    def draw_vignette(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        radius = WIDTH
        pygame.draw.circle(overlay, (0, 0, 0, 100), (WIDTH // 2, HEIGHT // 2), radius)
        self.screen.blit(overlay, (0, 0))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    self.sound_manager.create_tone(800, 0.05, 0.1, 'square').play()

            self.handle_input()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

