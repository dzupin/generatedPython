# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-27B-Q8_0.gguf  --mmproj /AI/models/Qwen3.5-27B-mmproj-F32.gguf


import pygame
import random
import math
import json
import os

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 7
BULLET_SPEED = 12
ENEMY_BULLET_SPEED = 6
MAX_ENEMY_BULLETS = 8
NUM_ENEMIES_ROWS = 5
NUM_ENEMIES_COLS = 10

# Colors
BG_COLOR = (5, 5, 15)
PLAYER_COLOR = (0, 255, 200)
ENEMY_1_COLOR = (255, 69, 0)
ENEMY_2_COLOR = (0, 255, 127)
ENEMY_3_COLOR = (138, 43, 226)
TEXT_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 255, 200)
ENEMY_BULLET_COLOR = (255, 50, 50)
UFO_COLOR = (200, 200, 255)
BARRIER_COLOR = (100, 255, 100)
POWERUP_COLOR = (255, 215, 0)

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"
POWERUP_BOMB = "BOMB"

# High Score File
HIGH_SCORE_FILE = "highscores.json"


# --- SPRITE GENERATOR (Procedural Pixel Art) ---
def create_pixel_art(width, height, color, pattern):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    # Create a glow layer
    glow_surface = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)

    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                # Main pixel
                pygame.draw.rect(surface, color, (x * 2, y * 2, 2, 2))
                # Glow pixel
                pygame.draw.rect(glow_surface, (*color, 50), (x * 2, y * 2, 2, 2))

    surface.blit(glow_surface, (-2, -2), special_flags=pygame.BLEND_RGBA_ADD)
    return surface


# Define Sprites
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
        pygame.mixer.init(44100, -16, 2, 128)  # Increased channels
        self.sample_rate = 44100
        self.enabled = True

    def create_tone(self, freq, duration, vol=0.3, wave_type='square', fade_out=True):
        if not self.enabled: return None

        samples = int(self.sample_rate * duration)
        buffer = [0] * (samples * 2)
        max_sample = 32767
        for s in range(samples):
            t = float(s) / self.sample_rate

            # Envelope (Attack/Release)
            env = 1.0
            if fade_out:
                env = 1.0 - (s / samples)

            if wave_type == 'square':
                value = 1 if (t * freq) % 1 < 0.5 else -1
            elif wave_type == 'sawtooth':
                value = 2 * ((t * freq) % 1) - 1
            else:
                value = math.sin(2 * math.pi * freq * t)

            sample_val = int(max_sample * vol * value * env)
            buffer[s * 2] = sample_val
            buffer[s * 2 + 1] = sample_val

        return pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        )

    def play_shoot(self):
        # Punchier sound
        c1 = self.create_tone(880, 0.15, 0.1, 'square')
        c2 = self.create_tone(1200, 0.15, 0.1, 'square')
        if c1: c1.play()
        if c2: c2.play()

    def play_enemy_shoot(self):
        c = self.create_tone(150, 0.3, 0.1, 'sawtooth')
        if c: c.play()

    def play_explosion(self):
        # Noise burst
        duration = 0.2
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-20000, 20000) for _ in range(samples * 2)]
        sound = pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        )
        sound.play()

    def play_powerup(self):
        # Rising arpeggio
        tones = [500, 600, 750, 900]
        for freq in tones:
            t = self.create_tone(freq, 0.05, 0.2, 'square', fade_out=False)
            if t: t.play()

    def play_combo(self):
        c = self.create_tone(1500, 0.05, 0.15, 'square')
        if c: c.play()


# --- CLASSES ---

class Particle:
    def __init__(self, x, y, color, speed=2, gravity=0.1):
        self.x, self.y = x, y
        self.base_color = color
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed_mag = random.uniform(0.5, speed * 2)
        self.vx = math.cos(angle) * speed_mag
        self.vy = math.sin(angle) * speed_mag
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.gravity = gravity
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay

        # Color fade out (turn to white/grey at end)
        if self.life < 0.3:
            gray_val = int(255 * self.life)
            self.color = (gray_val, gray_val, gray_val)
        else:
            self.color = self.base_color

    def draw(self, surface):
        if self.life <= 0: return
        s = pygame.Surface((self.size * 2 + 2, self.size * 2 + 2), pygame.SRCALPHA)
        # Additive blending for glow
        pygame.draw.circle(s, (*self.color, int(255 * self.life)), (self.size + 1, self.size + 1), self.size)
        surface.blit(s, (int(self.x) - self.size - 1, int(self.y) - self.size - 1), special_flags=pygame.BLEND_RGBA_ADD)


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = 1.0
        self.vy = -1
        self.decay = 0.02
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.active = True

    def update(self):
        self.y += self.vy
        self.life -= self.decay
        if self.life <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active: return
        alpha = int(255 * self.life)
        color = (*self.color[:3], alpha) if len(self.color) > 3 else self.color

        # Create surface with alpha
        surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        # Font rendering with transparency is tricky in pygame without antialiasing hacks
        # We'll just use standard render and accept slight opacity issues or just use opaque text
        txt_surf = self.font.render(self.text, True, self.color)
        txt_rect = txt_surf.get_rect(center=(self.x, self.y))
        surface.blit(txt_surf, txt_rect)


class Bullet:
    def __init__(self, x, y, is_player=False, speed=BULLET_SPEED, vx=0):
        self.x, self.y = x, y
        self.width, self.height = 4, 12
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -speed if is_player else ENEMY_BULLET_SPEED
        self.velocity_x = vx
        self.active = True
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -50 or self.y > HEIGHT + 50 or self.x < -50 or self.x > WIDTH + 50:
            self.active = False

    def draw(self, surface):
        # Draw trail with additive blending for glow
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail)))
            s = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (1, 1), 1)
            surface.blit(s, (int(tx) - 1, int(ty) - 1), special_flags=pygame.BLEND_RGBA_ADD)

        # Draw main bullet
        # Glow
        s = pygame.Surface((self.width + 2, self.height + 2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, 150), (0, 0, self.width + 2, self.height + 2))
        surface.blit(s, (self.x - self.width // 2 - 1, self.y - 1), special_flags=pygame.BLEND_RGBA_ADD)
        # Core
        pygame.draw.rect(surface, (255, 255, 255), self.rect)


class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice([POWERUP_RAPID, POWERUP_SPREAD, POWERUP_SHIELD, POWERUP_BOMB])
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
        self.pulse += 0.1
        if self.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        # Pulsing glow
        glow_radius = 10 + math.sin(self.pulse) * 3

        s = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, 100), (self.width, self.height), int(glow_radius))
        pygame.draw.circle(s, (*self.color, 255), (self.width, self.height), self.width // 2)
        surface.blit(s, (self.x - self.width // 2, self.y - self.height // 2), special_flags=pygame.BLEND_RGBA_ADD)

        # Text
        text_map = {POWERUP_RAPID: "R", POWERUP_SPREAD: "S", POWERUP_SHIELD: "H", POWERUP_BOMB: "B"}
        txt = pygame.font.SysFont("Arial", 14, bold=True).render(text_map[self.type], True, (0, 0, 0))
        s.blit(txt, (self.width - txt.get_width() // 2, self.height - txt.get_height() // 2))


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
                        'active': True
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
                    segment['active'] = False
                    return True
        return False

    def draw(self, surface):
        for segment in self.segments:
            if segment['active']:
                pygame.draw.rect(surface, BARRIER_COLOR,
                                 (segment['x'], segment['y'], segment['width'], segment['height']))


class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2 - 16, HEIGHT - 60
        self.width, self.height = 32, 32
        self.color = PLAYER_COLOR
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 300
        self.active = True
        self.lives = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.move_dir = 0  # For thrust particles

        # Powerups
        self.powerups = []
        self.shield_active = False
        self.shield_timer = 0
        self.combo = 0
        self.combo_timer = 0

    def update(self, keys, current_time):
        old_x = self.x
        self.move_dir = 0

        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
            self.move_dir = -1
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
            self.move_dir = 1

        self.rect.topleft = (self.x, self.y)

        if current_time - self.combo_timer > 1500:
            self.combo = 0

        if self.shield_active and current_time - self.shield_timer > 8000:
            self.shield_active = False

    def shoot(self, game, current_time):
        if current_time - self.last_shot > self.shoot_delay:
            bullet_x = self.x + self.width // 2
            bullet_y = self.y

            # Check for Spread Shot
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
                bullet = Bullet(bullet_x, bullet_y, is_player=True)
                game.player_bullets.append(bullet)

            self.last_shot = current_time
            game.sound_manager.play_shoot()

            # Shoot particles
            game.spawn_particles(bullet_x, bullet_y, PLAYER_COLOR, 5, 0)

    def draw(self, surface):
        # Shield
        if self.shield_active:
            angle = math.sin(pygame.time.get_ticks() * 0.01) * 0.02
            pygame.draw.circle(surface, (100, 255, 255), (self.x + self.width // 2, self.y + self.height // 2),
                               self.width // 2 + 5, 2)

        # Draw Sprite
        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))


class Invader:
    def __init__(self, x, y, row, col, level):
        self.x, self.y = x, y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        self.level = level
        self.flash_time = 0

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

    def draw(self, surface, time):
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 3

        # Flash effect on hit
        if self.flash_time > 0:
            self.flash_time -= 1
            surface.fill((255, 255, 255))  # Flash screen momentarily? No, just tint sprite
            # Draw white sprite over normal
            s = pygame.Surface((self.width + 5, self.height + 5), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, 100), (0, 0, self.width + 5, self.height + 5))
            surface.blit(s, (self.x + sine_offset, self.y))

        scaled_sprite = pygame.transform.scale(self.sprite, (self.width + 5, self.height + 5))
        surface.blit(scaled_sprite, (self.x + sine_offset, self.y))

        self.rect = pygame.Rect(self.x + sine_offset, self.y, self.width + 5, self.height + 5)


class UFO:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.y = 50
        self.speed = 5
        self.move_down_step = 20
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(10000, 20000)
        self.active = True
        self.score_value = 500
        self.x = 20
        self.direction = 1
        self.rect = pygame.Rect(0, self.y, self.width, self.height)

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

    def draw(self, surface):
        scaled_sprite = pygame.transform.scale(SPRITE_UFO, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))


# --- HIGH SCORE MANAGER ---
class HighScoreManager:
    def __init__(self):
        self.high_score = 0
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
            except:
                self.high_score = 0

    def save(self, score):
        if score > self.high_score:
            self.high_score = score
            try:
                with open(HIGH_SCORE_FILE, 'w') as f:
                    json.dump({'high_score': self.high_score}, f)
            except:
                pass

    def get(self):
        return self.high_score


# --- MAIN GAME ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.sound_manager = SoundManager()
        self.score_manager = HighScoreManager()

        self.state = "START"
        self.score = 0
        self.level = 1
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.ufo = None
        self.particles = []
        self.floating_texts = []

        # Parallax Stars
        self.stars = []
        for _ in range(50):  # Layer 1 (Slow)
            self.stars.append(Star(speed_range=(0.2, 1.0)))
        for _ in range(30):  # Layer 2 (Fast)
            self.stars.append(Star(speed_range=(1.0, 3.0)))

        self.barriers = []
        self.enemy_direction = 1
        self.enemy_move_speed = 2
        self.enemy_drop_distance = 10

        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(20000, 40000)

        self.init_enemies()
        self.init_barriers()

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

    def spawn_particles(self, x, y, color, count=15, gravity=0.1):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, speed=3, gravity=gravity))

    def spawn_explosion(self, x, y, color, count=25, gravity=0.05):
        self.spawn_particles(x, y, color, count, gravity)

        # Shockwave
        # (Could add a shockwave class, but particles work for now)

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
        elif self.state in ["GAMEOVER"]:
            if keys[pygame.K_SPACE]:
                self.reset_game()
            elif keys[pygame.K_ESCAPE]:
                self.state = "START"

    def update_logic(self):
        current_time = pygame.time.get_ticks()
        for star in self.stars:
            star.update()

        # Thrust particles
        if self.state == "PLAYING":
            if self.player.move_dir != 0 or self.player.last_shot > 0:
                if random.random() < 0.5:
                    # Emit from back
                    px = self.player.x + self.player.width // 2
                    py = self.player.y + self.player.height
                    # Add slight randomness
                    px += random.randint(-5, 5)
                    self.spawn_particles(px, py, PLAYER_COLOR, 1, 0.2)

        if self.state == "PLAYING":
            # UFO Logic
            if self.ufo_spawn_time == 0:
                self.ufo_spawn_time = current_time
            elif current_time - self.ufo_spawn_time > self.ufo_spawn_interval:
                self.ufo = UFO()
                self.ufo_spawn_time = current_time
                self.ufo_spawn_interval = random.randint(20000, 40000)

            if self.ufo and self.ufo.active:
                self.ufo.update()
                if random.random() < 0.005:
                    b = Bullet(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height, is_player=False)
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

            # Update Projectiles
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
                        if p.type not in self.player.powerups:
                            self.player.powerups.append(p.type)
                            if p.type == POWERUP_SHIELD:
                                self.player.shield_active = True
                                self.player.shield_timer = current_time
                            elif p.type == POWERUP_BOMB:
                                # Instant Clear
                                self.enemy_bullets = []
                                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), 100)
                                self.score += 500
                                self.floating_texts.append(FloatingText(WIDTH // 2, HEIGHT // 2, "CLEAR!", (255, 0, 0)))
                                for e in self.enemies:
                                    if e.active:
                                        e.active = False
                                        self.spawn_explosion(e.x, e.y, e.color)
                                self.sound_manager.play_explosion()
                                # Remove immediately
                                self.powerups.remove(p)
                                continue

                            self.sound_manager.play_powerup()
                            self.spawn_explosion(p.x, p.y, POWERUP_COLOR, 10, 0)
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
                        points = enemy.score_value * max(1, self.player.combo)
                        self.score += points
                        self.player.combo = min(self.player.combo + 1, 15)
                        self.player.combo_timer = current_time

                        # Floating Text
                        self.floating_texts.append(FloatingText(
                            enemy.x + enemy.width // 2,
                            enemy.y,
                            str(points),
                            (255, 255, 0)
                        ))

                        self.sound_manager.play_combo()
                        self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color)
                        self.sound_manager.play_explosion()

                        if random.random() < 0.08:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))
                        hit = True
                        break

                if not hit:
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR, 5)
                            self.sound_manager.play_powerup()
                            break

                    if not b.active:
                        for eb in self.enemy_bullets[:]:
                            if b.rect.colliderect(eb.rect):
                                b.active = False
                                eb.active = False
                                self.spawn_explosion(b.x, b.y, (255, 255, 255), 8)
                                break

            # 2. Enemy Bullets vs Player
            for b in self.enemy_bullets[:]:
                if b.rect.colliderect(self.player.rect):
                    b.active = False
                    if self.player.shield_active:
                        self.player.shield_active = False
                        self.spawn_explosion(self.player.x + self.player.width // 2, self.player.y, (100, 255, 255))
                        self.sound_manager.play_powerup()
                    else:
                        self.player_hit()
                    break

            # 3. Enemy Bullets vs Barriers
            for b in self.enemy_bullets[:]:
                for barrier in self.barriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, 5)
                        break

            # 4. Enemy vs Player
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    break

            # 5. UFO
            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2,
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
                self.floating_texts.append(FloatingText(WIDTH // 2, HEIGHT // 2, "LEVEL UP!", (255, 255, 255)))
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), 50)

            # Particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            # Floating Text
            for ft in self.floating_texts:
                ft.update()
            self.floating_texts = [ft for ft in self.floating_texts if ft.active]

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

        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            self.score_manager.save(self.score)

    def draw(self):
        # Background
        bg_surface = pygame.Surface((WIDTH, HEIGHT))
        bg_surface.fill(BG_COLOR)

        # Stars
        for star in self.stars:
            star.draw(bg_surface)

        self.screen.blit(bg_surface, (0, 0))

        if self.state == "START":
            self.draw_menu("NEON INVADERS", "Press SPACE to Start", f"High Score: {self.score_manager.get()}")
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
            for ft in self.floating_texts:
                ft.draw(self.screen)
            self.draw_hud()
        elif self.state == "PAUSE":
            self.draw_menu("PAUSED", "Press P to Resume")
        elif self.state == "GAMEOVER":
            self.draw_menu("GAME OVER", f"Score: {self.score}", f"Best: {self.score_manager.get()}")

        pygame.display.flip()

    def draw_menu(self, title, sub1, sub2=""):
        # 1. Create Text Surface (Use White for better contrast against Cyan glow)
        title_surf = self.large_font.render(title, True, TEXT_COLOR)

        # 2. Create Glow Surface (Cyan) - 20px larger than text
        s = pygame.Surface((title_surf.get_width() + 20, title_surf.get_height() + 20), pygame.SRCALPHA)

        # 3. Draw Glow Rectangle centered inside the surface (10px padding on all sides)
        # This ensures it aligns with the text when s is blitted at (x-10, y-10)
        pygame.draw.rect(s, (*PLAYER_COLOR, 100), (10, 10, title_surf.get_width(), title_surf.get_height()))

        # 4. Calculate Center Position
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))

        # 5. Draw Glow FIRST (Background)
        # Offset by 10px to account for padding
        self.screen.blit(s, (title_rect.x - 10, title_rect.y - 10), special_flags=pygame.BLEND_RGBA_ADD)

        # 6. Draw Text SECOND (Foreground)
        self.screen.blit(title_surf, title_rect)

        # Draw Subtext
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
        pu_surf = self.font.render(f"PU: {powerup_text or '-'}", True, POWERUP_COLOR)

        self.screen.blit(score_surf, (15, 10))
        self.screen.blit(lives_surf, (WIDTH - 160, 10))
        self.screen.blit(level_surf, (WIDTH // 2 - 60, 10))
        self.screen.blit(combo_surf, (15, 35))
        self.screen.blit(pu_surf, (WIDTH - 160, 35))

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


class Star:
    def __init__(self, speed_range=(0.5, 1.5)):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(speed_range[0], speed_range[1])
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
