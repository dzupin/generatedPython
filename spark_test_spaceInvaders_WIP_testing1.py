# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-27B-heretic.i1-Q6_K.gguf  --mmproj /AI/models/Qwen3.5-27B-mmproj-F32.gguf


import pygame
import random
import math
import sys

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

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"


# --- SPRITE GENERATOR (Procedural Pixel Art) ---
def create_pixel_art(width, height, color, pattern):
    """
    Creates a pygame Surface from a binary pattern list of lists.
    1 = color, 0 = transparent.
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, color, (x * 2, y * 2, 2, 2))
    return surface


# Define Sprites as Binary Maps
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
        self.channels[5].play(self.create_tone(900, 0.1, 0.2, 'square'))

    def play_combo(self):
        self.channels[6].play(self.create_tone(1200, 0.05, 0.1, 'square'))
        self.channels[7].play(self.create_tone(1500, 0.05, 0.1, 'square'))


# --- VISUAL ENHANCEMENT CLASSES ---

class StarField:
    def __init__(self, density=100):
        self.stars = []
        self.nebula = []
        self.time = 0
        for _ in range(density):
            self.stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'speed': random.uniform(0.1, 0.5),
                'size': random.randint(1, 2),
                'brightness': random.randint(150, 255)
            })
        for _ in range(20):
            self.nebula.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'radius': random.randint(30, 80),
                'color': (
                    random.randint(50, 100),
                    random.randint(30, 80),
                    random.randint(80, 150)
                ),
                'speed': random.uniform(0.05, 0.2),
                'angle': random.uniform(0, math.pi * 2)
            })

    def update(self, dt):
        self.time += dt
        # Update stars
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WIDTH)

        # Update nebula
        for neb in self.nebula:
            neb['x'] += math.cos(neb['angle']) * neb['speed']
            neb['y'] += math.sin(neb['angle']) * neb['speed']
            if neb['x'] < -100: neb['x'] = WIDTH + 100
            if neb['x'] > WIDTH + 100: neb['x'] = -100
            if neb['y'] < -100: neb['y'] = HEIGHT + 100
            if neb['y'] > HEIGHT + 100: neb['y'] = -100

    def draw(self, surface):
        # Draw nebula (background layer)
        for neb in self.nebula:
            alpha = int(100 * (1 + math.sin(self.time * 0.02 + neb['x'] * 0.01)) * 0.5)
            color = (*neb['color'], alpha)
            s = pygame.Surface((neb['radius'] * 2, neb['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (neb['radius'], neb['radius']), neb['radius'])
            surface.blit(s, (neb['x'] - neb['radius'], neb['y'] - neb['radius']))

        # Draw stars
        for star in self.stars:
            alpha = int(star['brightness'] * (0.7 + 0.3 * math.sin(self.time * 0.01 + star['x'] * 0.05)))
            color = (alpha, alpha, alpha)
            pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), star['size'])


class Particle:
    def __init__(self, x, y, base_color, speed=2, particle_type="normal"):
        self.x, self.y = x, y
        self.base_color = base_color
        self.particle_type = particle_type
        angle = random.uniform(0, math.pi * 2)
        speed_mag = random.uniform(1, speed * 2)
        self.vx = math.cos(angle) * speed_mag
        self.vy = math.sin(angle) * speed_mag
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.04)
        self.size = random.randint(2, 5)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)
        self.color_phase = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity
        self.life -= self.decay
        self.rotation += self.rot_speed
        self.color_phase += 0.05

    def draw(self, surface):
        if self.life <= 0:
            return

        # Color transition based on life and type
        if self.particle_type == "powerup":
            r = int(255 * (0.5 + 0.5 * math.sin(self.color_phase)))
            g = int(215 * (0.5 + 0.5 * math.sin(self.color_phase + 2)))
            b = int(0 * (0.5 + 0.5 * math.sin(self.color_phase + 4)))
            color = (r, g, b)
        elif self.particle_type == "explosion":
            # Explosion: white -> yellow -> red -> black
            life_factor = 1 - self.life
            if life_factor < 0.3:
                color = (255, 255, 255)  # White
            elif life_factor < 0.6:
                color = (255, int(255 * (1 - (life_factor - 0.3) / 0.3)), 0)  # Yellow to red
            else:
                color = (int(255 * (1 - (life_factor - 0.6) / 0.4)), 0, 0)  # Red to black
        else:  # normal
            life_factor = 1 - self.life
            r = int(self.base_color[0] * (0.7 + 0.3 * life_factor))
            g = int(self.base_color[1] * (0.7 + 0.3 * life_factor))
            b = int(self.base_color[2] * (0.7 + 0.3 * life_factor))
            color = (r, g, b)

        alpha = int(255 * self.life)
        color = (*color, alpha)

        # Draw rotating particle
        size = self.size * self.life
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (size, size), size)
        rotated = pygame.transform.rotate(s, self.rotation)
        surface.blit(rotated, (int(self.x) - rotated.get_width() // 2, int(self.y) - rotated.get_height() // 2))


class FloatingText:
    def __init__(self, x, y, text, color, size=20, life=1.5):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.size = size
        self.life = life
        self.font = pygame.font.SysFont("Arial", size, bold=True)
        self.vy = -30
        self.alpha = 255
        self.scale = 1.0
        self.scale_speed = 2.0

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt
        self.alpha = int(255 * (self.life / 1.5))
        self.scale = 1.0 + math.sin((1.5 - self.life) * 5) * 0.3

    def draw(self, surface):
        if self.life <= 0:
            return
        text_surf = self.font.render(self.text, True, self.color)
        text_surf = pygame.transform.scale(text_surf,
                                           (int(text_surf.get_width() * self.scale),
                                            int(text_surf.get_height() * self.scale)))
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y - text_surf.get_height() // 2))


# --- CLASSES ---

class Bullet:
    def __init__(self, x, y, is_player=False, speed=BULLET_SPEED, angle=0):
        self.x, self.y = x, y
        self.width, self.height = 4, 10
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -speed * math.cos(math.radians(angle)) if is_player else ENEMY_BULLET_SPEED
        self.velocity_x = speed * math.sin(math.radians(angle)) if is_player else 0
        self.active = True
        self.trail = []  # For visual trail
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        # Trail effect
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)

        # Remove if off screen or too old
        if (self.y < -50 or self.y > HEIGHT + 50 or
                self.x < -50 or self.x > WIDTH + 50 or
                pygame.time.get_ticks() - self.creation_time > 5000):
            self.active = False

    def draw(self, surface):
        # Draw trail with fading
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail)) * (1 - i / len(self.trail)))
            size = 2 + i * 0.5
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (size, size), size)
            surface.blit(s, (int(tx) - size, int(ty) - size))

        # Draw main bullet with glow
        glow_size = 4
        glow_surf = pygame.Surface((self.width + glow_size * 2, self.height + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 255, 200, 100),
                         (glow_size, glow_size, self.width, self.height), border_radius=2)
        surface.blit(glow_surf, (self.x - self.width // 2 - glow_size, self.y - glow_size))
        pygame.draw.rect(surface, self.color, self.rect)


class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice([POWERUP_RAPID, POWERUP_SPREAD, POWERUP_SHIELD])
        self.base_size = 20
        self.size = self.base_size
        self.pulse_scale = 1.0
        self.pulse_speed = 3.0
        self.angle = 0
        self.rect = pygame.Rect(x, y, self.base_size, self.base_size)
        self.active = True
        self.vy = 1.5
        self.hover_offset = 0
        self.hover_speed = 2.0

    def update(self):
        self.y += self.vy
        self.hover_offset = math.sin(pygame.time.get_ticks() * 0.005 * self.hover_speed) * 4
        self.rect.topleft = (self.x, self.y + self.hover_offset)
        self.angle += 0.15
        self.pulse_scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.003 * self.pulse_speed) * 0.3
        if self.y > HEIGHT + 20:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        size = self.base_size * self.pulse_scale
        offset = (self.base_size - size) / 2

        # Draw outer glow
        glow_size = size * 0.3
        glow_surf = pygame.Surface((size + glow_size * 2, size + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*POWERUP_COLOR, 100),
                            (glow_size, glow_size, size, size))
        surface.blit(glow_surf, (self.x - glow_size, self.y + self.hover_offset - glow_size))

        # Draw main powerup
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(s, POWERUP_COLOR, (0, 0, size, size))
        pygame.draw.ellipse(s, (255, 255, 255, 180),
                            (size * 0.1, size * 0.1, size * 0.8, size * 0.8))

        # Add symbol
        text_map = {POWERUP_RAPID: "⚡", POWERUP_SPREAD: "🔺", POWERUP_SHIELD: "🛡️"}
        txt = self.font.render(text_map[self.type], True, (0, 0, 0))
        txt = pygame.transform.rotate(txt, self.angle * 180 / math.pi)
        s.blit(txt, (size // 2 - txt.get_width() // 2, size // 2 - txt.get_height() // 2))

        surface.blit(s, (self.x, self.y + self.hover_offset))

    @property
    def font(self):
        return pygame.font.SysFont("Arial", int(16 * self.pulse_scale), bold=True)


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
        self.pulse = 0

    def create_segments(self):
        segment_width = 4
        segment_height = 4
        for row in range(self.height // segment_height):
            for col in range(self.width // segment_width):
                # Create a pattern for the barrier (arches)
                is_hole = (col % 4 == 1 and row < 3) or (col % 4 == 1 and row > 7)
                if not is_hole:
                    self.segments.append({
                        'x': self.x + col * segment_width,
                        'y': self.y + row * segment_height,
                        'width': segment_width,
                        'height': segment_height,
                        'active': True
                    })

    def update(self):
        self.pulse += 0.05
        active_segments = [s for s in self.segments if s['active']]
        if not active_segments:
            self.active = False
            return
        # Recalculate bounding box
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
                    segment['active'] = False
                    # Create particles on hit
                    return True
        return False

    def draw(self, surface):
        pulse_intensity = math.sin(self.pulse) * 0.3 + 0.7
        for segment in self.segments:
            if segment['active']:
                # Pulse effect
                pulse = math.sin(self.pulse + segment['x'] * 0.05) * 0.2 + 0.8
                color = (
                    int(BARRIER_COLOR[0] * pulse),
                    int(BARRIER_COLOR[1] * pulse),
                    int(BARRIER_COLOR[2] * pulse)
                )
                pygame.draw.rect(surface, color,
                                 (segment['x'], segment['y'], segment['width'], segment['height']))


class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2 - 16, HEIGHT - 60
        self.width, self.height = 32, 32  # Scaled up
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
        self.afterimages = []  # For trail effect
        self.max_afterimages = 5

    def update(self, keys, current_time):
        # Store position for afterimage
        self.afterimages.append((self.x, self.y, current_time))
        if len(self.afterimages) > self.max_afterimages:
            self.afterimages.pop(0)

        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

        # Combo decay
        if current_time - self.combo_timer > 1200:
            self.combo = max(0, self.combo - 1)
            if self.combo == 0:
                self.combo_timer = current_time

        # Shield decay
        if self.shield_active and current_time - self.shield_timer > 12000:
            self.shield_active = False

    def shoot(self, game, current_time):
        if current_time - self.last_shot > self.shoot_delay:
            # Check for Spread Shot
            if POWERUP_SPREAD in self.powerups:
                for angle_offset in [-20, 0, 20]:
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
            game.sound_manager.play_shoot()

    def draw(self, surface):
        # Draw afterimages (trail)
        for i, (ax, ay, atime) in enumerate(self.afterimages):
            age = pygame.time.get_ticks() - atime
            if age > 300:  # Fade out after 300ms
                continue
            alpha = int(150 * (1 - age / 300))
            size = self.width * (0.7 + 0.3 * (1 - age / 300))
            surf = pygame.transform.scale(SPRITE_PLAYER, (int(size), int(size)))
            surf.set_alpha(alpha)
            # FIXED: Draw with top-left at (ax, ay) instead of centering
            surface.blit(surf, (ax, ay))

        # Draw Shield if active
        if self.shield_active:
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.2 + 0.8
            radius = self.width // 2 + 5
            pygame.draw.circle(surface, (100, 255, 255, int(150 * pulse)),
                               (self.x + self.width // 2, self.y + self.height // 2),
                               int(radius * pulse), 2)

        # Draw Sprite (Scaled)
        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))

        # Engine Glow with pulse
        glow_size = 6 + int(math.sin(pygame.time.get_ticks() * 0.015) * 3)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 200, 0, 100), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (self.x + self.width // 2 - glow_size, self.y + self.height - glow_size // 2))


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

        self.score_value *= level  # Higher score for higher levels

        self.animation_offset = random.randint(0, 10)
        self.active = True
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(1500, 4000) // level
        self.is_on_cooldown = False
        self.hit_flash = 0  # For flash when shooting
        self.pulse_offset = random.uniform(0, math.pi * 2)

    def draw(self, surface, time):
        # Animation offset (wobble)
        sine_offset = math.sin(time * 0.04 + self.animation_offset) * 2.5
        pulse = math.sin(time * 0.01 + self.pulse_offset) * 0.1 + 0.9

        # Draw scaled sprite with pulse
        sprite_width = int(self.width * pulse)
        sprite_height = int(self.height * pulse)
        scaled_sprite = pygame.transform.scale(self.sprite, (sprite_width, sprite_height))

        # Draw flash effect if recently shot
        flash_alpha = 0
        if self.hit_flash > 0:
            flash_alpha = int(200 * (self.hit_flash / 0.2))
            self.hit_flash -= 0.016  # Assuming ~60fps

        # Draw base sprite
        surface.blit(scaled_sprite,
                     (self.x + sine_offset - (sprite_width - self.width) // 2,
                      self.y + sine_offset - (sprite_height - self.height) // 2))

        # Draw flash overlay
        if flash_alpha > 0:
            flash_surf = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, flash_alpha))
            surface.blit(flash_surf,
                         (self.x + sine_offset - (sprite_width - self.width) // 2,
                          self.y + sine_offset - (sprite_height - self.height) // 2))

        # Update rect for collision (using wobbly position)
        self.rect = pygame.Rect(self.x + sine_offset, self.y + sine_offset,
                                self.width + 5, self.height + 5)

    def trigger_shot_flash(self):
        self.hit_flash = 0.2  # Flash for 200ms


class UFO:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.y = 50
        self.speed = 6
        self.move_down_step = 20
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(12000, 25000)
        self.active = True
        self.score_value = 500
        self.pulse_offset = random.uniform(0, math.pi * 2)

        self.x = 20
        self.direction = 1
        self.rect = pygame.Rect(0, self.y, self.width, self.height)
        self.engine_glow = 0

    def update(self):
        self.x += self.speed * self.direction
        self.engine_glow = (self.engine_glow + 0.1) % (math.pi * 2)

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
        # Pulse effect
        pulse = math.sin(pygame.time.get_ticks() * 0.003 + self.pulse_offset) * 0.1 + 0.9
        scaled_width = int(self.width * pulse)
        scaled_height = int(self.height * pulse)

        # Draw sprite with pulse
        scaled_sprite = pygame.transform.scale(SPRITE_UFO, (scaled_width, scaled_height))
        surface.blit(scaled_sprite,
                     (self.x + (self.width - scaled_width) // 2,
                      self.y + (self.height - scaled_height) // 2))

        # Engine glow
        glow_size = 8 + int(math.sin(self.engine_glow) * 4)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (200, 200, 255, 100), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf,
                     (self.x + self.width // 2 - glow_size,
                      self.y + self.height - glow_size // 2))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.sound_manager = SoundManager()

        self.state = "START"
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.ufo = None
        self.particles = []
        self.floating_texts = []
        self.star_field = StarField(120)
        self.barriers = []
        self.background_color = BG_COLOR
        self.color_shift_direction = 1
        self.color_shift_speed = 0.2

        self.enemy_direction = 1
        self.enemy_move_speed = 2  # Base speed
        self.enemy_drop_distance = 10
        self.last_enemy_move_time = 0

        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(18000, 35000)

        self.init_enemies()
        self.init_barriers()
        self.level_up_timer = 0
        self.show_level_up = False

    def init_enemies(self):
        self.enemies = []
        padding_x, padding_y, start_x, start_y = 10, 15, 50, 60
        for row in range(NUM_ENEMIES_ROWS):
            for col in range(NUM_ENEMIES_COLS):
                x = start_x + col * (40 + padding_x)
                y = start_y + row * (40 + padding_y)
                self.enemies.append(Invader(x, y, row, col, self.level))
        self.enemy_move_speed = 2 + (self.level * 0.4)

    def init_barriers(self):
        self.barriers = []
        barrier_spacing = WIDTH // (4 + 1)
        for i in range(4):
            barrier_x = barrier_spacing * (i + 1) - 30
            barrier_y = HEIGHT - 120
            self.barriers.append(Barrier(barrier_x, barrier_y))

    def spawn_explosion(self, x, y, color, count=15, particle_type="explosion"):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, speed=3, particle_type=particle_type))

    def add_floating_text(self, x, y, text, color):
        self.floating_texts.append(FloatingText(x, y, text, color))

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
        self.floating_texts = []
        self.ufo = None
        self.state = "PLAYING"
        self.background_color = BG_COLOR
        self.color_shift_direction = 1

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

            # Pause
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

    def update_logic(self):
        dt = self.clock.get_time() / 1000.0  # Delta time in seconds
        current_time = pygame.time.get_ticks()

        # Update star field
        self.star_field.update(dt)

        # Update background color slowly
        if self.color_shift_direction == 1:
            self.background_color = (
                min(25, self.background_color[0] + self.color_shift_speed * dt),
                min(30, self.background_color[1] + self.color_shift_speed * dt * 0.8),
                max(10, self.background_color[2] - self.color_shift_speed * dt * 0.5)
            )
            if self.background_color[0] >= 25:
                self.color_shift_direction = -1
        else:
            self.background_color = (
                max(10, self.background_color[0] - self.color_shift_speed * dt),
                max(12, self.background_color[1] - self.color_shift_speed * dt * 0.8),
                min(25, self.background_color[2] + self.color_shift_speed * dt * 0.5)
            )
            if self.background_color[0] <= 10:
                self.color_shift_direction = 1

        if self.state == "PLAYING":
            # UFO
            if self.ufo_spawn_time == 0:
                self.ufo_spawn_time = current_time
            elif current_time - self.ufo_spawn_time > self.ufo_spawn_interval:
                self.ufo = UFO()
                self.ufo_spawn_time = current_time
                self.ufo_spawn_interval = random.randint(18000, 35000)

            if self.ufo and self.ufo.active:
                self.ufo.update()
                if random.random() < 0.004:
                    b = Bullet(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height, is_player=False)
                    self.enemy_bullets.append(b)
                    self.sound_manager.play_enemy_shoot()
                if not self.ufo.active:
                    self.ufo = None

            # Enemy Movement (Smooth)
            move_step = self.enemy_move_speed * self.enemy_direction * dt * 60  # Frame rate independent

            edge_reached = False
            for enemy in self.enemies:
                if enemy.active:
                    enemy.x += move_step
                    # Check edges
                    if (enemy.x + enemy.width > WIDTH - 30 and self.enemy_direction == 1) or \
                            (enemy.x < 30 and self.enemy_direction == -1):
                        edge_reached = True
                        break

            if edge_reached:
                self.enemy_direction *= -1
                for enemy in self.enemies:
                    enemy.y += self.enemy_drop_distance
                    enemy.x += self.enemy_move_speed * self.enemy_direction * 15  # Compensate for edge hit

            # Enemy Shooting
            bullets_to_add = 0
            for enemy in self.enemies:
                if enemy.active and not enemy.is_on_cooldown:
                    if current_time - enemy.last_shot_time > enemy.shot_cooldown:
                        if random.random() < 0.025 + (self.level * 0.008):
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
                            enemy.trigger_shot_flash()  # Trigger visual flash
                            self.sound_manager.play_enemy_shoot()

            for enemy in self.enemies:
                if enemy.is_on_cooldown and (current_time - enemy.last_shot_time > enemy.shot_cooldown * 1.8):
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
                    # Collision with Player
                    if p.rect.colliderect(self.player.rect):
                        self.player.powerups.append(p.type)
                        if p.type == POWERUP_SHIELD:
                            self.player.shield_active = True
                            self.player.shield_timer = current_time
                        self.sound_manager.play_powerup()
                        self.spawn_explosion(p.x, p.y, POWERUP_COLOR, count=8, particle_type="powerup")
                        self.add_floating_text(p.x, p.y, "POWER UP!", POWERUP_COLOR)
                        self.powerups.remove(p)

            # Update Barriers
            for barrier in self.barriers:
                barrier.update()

            # COLLISIONS
            # 1. Player Bullets vs Enemies
            for b in self.player_bullets[:]:
                hit = False
                for enemy in self.enemies:
                    if enemy.active and b.rect.colliderect(enemy.rect):
                        enemy.active = False
                        b.active = False
                        score_gain = enemy.score_value * max(1, self.player.combo)
                        self.score += score_gain
                        self.player.combo = min(self.player.combo + 1, 15)
                        self.player.combo_timer = current_time
                        self.sound_manager.play_combo()
                        self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color)
                        self.add_floating_text(enemy.x, enemy.y, f"+{score_gain}", (255, 255, 0))

                        # Chance for Powerup
                        if random.random() < 0.12:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))

                        hit = True
                        break

                if not hit:
                    # Bullet vs Barrier
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR, count=5)
                            self.sound_manager.play_powerup()  # Reuse small sound
                            break

                    if not b.active:
                        # Bullet vs Enemy Bullet
                        for eb in self.enemy_bullets[:]:
                            if b.rect.colliderect(eb.rect):
                                b.active = False
                                eb.active = False
                                self.spawn_explosion(b.x, b.y, (255, 255, 255), count=3)
                                break

            # 2. Enemy Bullets vs Player
            for b in self.enemy_bullets[:]:
                if b.rect.colliderect(self.player.rect):
                    b.active = False
                    if self.player.shield_active:
                        self.player.shield_active = False
                        self.spawn_explosion(self.player.x, self.player.y, (100, 255, 255), count=10)
                        self.screen_shake = 5
                    else:
                        self.player_hit()
                    break

            # 3. Enemy Bullets vs Barriers
            for b in self.enemy_bullets[:]:
                for barrier in self.barriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, count=5)
                        break

            # 4. Enemies vs Player (Game Over)
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color, count=12)
                    enemy.active = False
                    break

            # 5. UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        score_gain = self.ufo.score_value
                        self.score += score_gain
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2,
                                             UFO_COLOR, count=20)
                        self.sound_manager.play_explosion()
                        self.add_floating_text(self.ufo.x, self.ufo.y, f"+{score_gain}", (255, 215, 0))
                        self.ufo.active = False
                        self.ufo = None
                        break

            # Level Complete
            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 0.5
                self.init_enemies()
                self.score += 1000 * self.level
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), count=30)
                self.show_level_up = True
                self.level_up_timer = current_time
                self.sound_manager.play_powerup()

            # Particles
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

            # Floating Texts - FIXED: Changed 'fx' to 'ft'
            for ft in self.floating_texts[:]:
                ft.update(dt)
                if ft.life <= 0:
                    self.floating_texts.remove(ft)

            # Level up timer
            if self.show_level_up and current_time - self.level_up_timer > 3000:
                self.show_level_up = False

    def player_hit(self):
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color, count=15
        )
        self.sound_manager.play_explosion()
        self.player.lives -= 1
        self.player.combo = 0
        self.player.powerups = []  # Lose powerups on death
        self.player.shield_active = False

        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score

    def draw(self):
        # Background
        self.screen.fill(self.background_color)

        # Star field
        self.star_field.draw(self.screen)

        if self.state == "START":
            self.draw_start_screen()
        elif self.state == "PLAYING":
            self.draw_game()
        elif self.state == "PAUSE":
            self.draw_pause_screen()
        elif self.state in ["GAMEOVER", "VICTORY"]:
            self.draw_end_screen()

        # Draw floating texts last so they appear on top
        for ft in self.floating_texts:
            ft.draw(self.screen)

        pygame.display.flip()

    def draw_start_screen(self):
        # Title with pulse
        pulse = math.sin(pygame.time.get_ticks() * 0.003) * 0.1 + 0.9
        title_size = int(72 * pulse)
        title_font = pygame.font.SysFont("Arial", title_size, bold=True)
        title_surf = title_font.render("NEON INVADERS", True, PLAYER_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(title_surf, title_rect)

        # Subtitle
        subtitle_surf = self.large_font.render("Press SPACE to Start", True, TEXT_COLOR)
        subtitle_rect = subtitle_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(subtitle_surf, subtitle_rect)

        # Controls
        controls = [
            "← → : Move",
            "SPACE : Shoot",
            "P : Pause",
            "ESC : Quit"
        ]
        for i, text in enumerate(controls):
            ctrl_surf = self.font.render(text, True, (200, 200, 200))
            ctrl_rect = ctrl_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60 + i * 25))
            self.screen.blit(ctrl_surf, ctrl_rect)

        # High score
        hs_surf = self.font.render(f"HIGH SCORE: {self.high_score}", True, POWERUP_COLOR)
        hs_rect = hs_surf.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(hs_surf, hs_rect)

    def draw_game(self):
        # Draw game elements
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

        # HUD with enhancements
        self.draw_hud()

        # Level up banner
        if self.show_level_up:
            self.draw_level_up_banner()

    def draw_hud(self):
        # Score with pulse
        score_pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.1 + 0.9
        score_size = int(24 * score_pulse)
        score_font = pygame.font.SysFont("Arial", score_size, bold=True)
        score_surf = score_font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        score_rect = score_surf.get_rect(topleft=(15, 10))
        self.screen.blit(score_surf, score_rect)

        # Lives with ship icons
        lives_text = self.font.render("LIVES:", True, TEXT_COLOR)
        self.screen.blit(lives_text, (WIDTH - 180, 10))
        for i in range(self.player.lives):
            ship_surf = pygame.transform.scale(SPRITE_PLAYER, (24, 24))
            self.screen.blit(ship_surf, (WIDTH - 120 + i * 28, 8))

        # Level
        level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
        level_rect = level_surf.get_rect(topright=(WIDTH - 15, 10))
        self.screen.blit(level_surf, level_rect)

        # Combo with visual indicator
        if self.player.combo > 1:
            combo_size = int(24 + self.player.combo * 2)
            combo_font = pygame.font.SysFont("Arial", combo_size, bold=True)
            combo_color = (255, 215, 0) if self.player.combo < 5 else (255, 100, 0)
            combo_surf = combo_font.render(f"COMBO: x{self.player.combo}", True, combo_color)
            combo_rect = combo_surf.get_rect(topright=(WIDTH - 15, 40))
            self.screen.blit(combo_surf, combo_rect)

        # Powerups
        powerup_text = ""
        if POWERUP_RAPID in self.player.powerups: powerup_text += "⚡ "
        if POWERUP_SPREAD in self.player.powerups: powerup_text += "🔺 "
        if self.player.shield_active: powerup_text += "🛡️ "
        pu_surf = self.font.render(f"POWERUPS: {powerup_text or 'NONE'}", True, POWERUP_COLOR)
        pu_rect = pu_surf.get_rect(bottomleft=(15, HEIGHT - 10))
        self.screen.blit(pu_surf, pu_rect)

    def draw_level_up_banner(self):
        # Semi-transparent background
        banner_surf = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
        banner_surf.fill((0, 0, 0, 180))
        self.screen.blit(banner_surf, (0, HEIGHT // 2 - 60))

        # Level up text
        pulse = math.sin(pygame.time.get_ticks() * 0.008) * 0.2 + 0.9
        title_size = int(48 * pulse)
        title_font = pygame.font.SysFont("Arial", title_size, bold=True)
        title_surf = title_font.render(f"LEVEL {self.level}!", True, (255, 255, 100))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        self.screen.blit(title_surf, title_rect)

        # Bonus text
        bonus_surf = self.large_font.render("+1000 POINTS!", True, (255, 215, 0))
        bonus_rect = bonus_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(bonus_surf, bonus_rect)

    def draw_pause_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_surf = self.title_font.render("PAUSED", True, (200, 200, 255))
        pause_rect = pause_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(pause_surf, pause_rect)

        # Instructions
        resume_surf = self.large_font.render("Press P to Resume", True, TEXT_COLOR)
        resume_rect = resume_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(resume_surf, resume_rect)

        quit_surf = self.font.render("Press ESC to Return to Menu", True, (180, 180, 180))
        quit_rect = quit_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        self.screen.blit(quit_surf, quit_rect)

    def draw_end_screen(self):
        # Determine state
        is_game_over = self.state == "GAMEOVER"
        title_text = "GAME OVER" if is_game_over else "LEVEL COMPLETE!"
        title_color = (255, 50, 50) if is_game_over else (50, 255, 50)
        subtitle_text = f"Final Score: {self.score}"

        # Background gradient effect
        for y in range(HEIGHT):
            color_val = int(20 * (y / HEIGHT))
            color = (color_val // 3, color_val // 4, color_val // 2)
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        # Title with pulse
        pulse = math.sin(pygame.time.get_ticks() * 0.004) * 0.15 + 0.85
        title_size = int(72 * pulse)
        title_font = pygame.font.SysFont("Arial", title_size, bold=True)
        title_surf = title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(title_surf, title_rect)

        # Score
        score_surf = self.large_font.render(subtitle_text, True, TEXT_COLOR)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(score_surf, score_rect)

        # High score
        if is_game_over and self.score == self.high_score:
            hs_surf = self.large_font.render("NEW HIGH SCORE!", True, POWERUP_COLOR)
            hs_rect = hs_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            self.screen.blit(hs_surf, hs_rect)
        elif not is_game_over:
            hs_surf = self.font.render(f"High Score: {self.high_score}", True, POWERUP_COLOR)
            hs_rect = hs_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            self.screen.blit(hs_surf, hs_rect)

        # Instructions
        instr_surf = self.font.render("Press SPACE to Play Again | ESC for Menu", True, (200, 200, 200))
        instr_rect = instr_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 110))
        self.screen.blit(instr_surf, instr_rect)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Limit FPS and get delta time
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    # For powerup sound effect sequence
                    self.sound_manager.create_tone(800, 0.05, 0.1, 'square').play()

            self.handle_input()
            self.update_logic()
            self.draw()
        pygame.quit()


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.2, 1.5)
        self.brightness = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


if __name__ == "__main__":
    game = Game()
    game.run()
