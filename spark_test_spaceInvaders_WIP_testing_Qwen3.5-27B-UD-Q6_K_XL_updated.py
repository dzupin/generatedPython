# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
# Update the code to make provided python game more addictive and more fun for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user (but please do not use screen shaking effects)  and therefore more addictive to play. Also check possibility for taking advantage of upgrades for player  in new games by using achievements in previous game. I want to introduce rewards for user playing game multiple times.  Don't use any external files for graphic and sound assets, (saving game progress to external file is fine ) in your enhancements. Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-27B-UD-Q6_K_XL.gguf  --mmproj /AI/models/Qwen3.5-27B-mmproj-F32.gguf

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

# --- COLORS ---
BG_COLOR = (5, 5, 15)
PLAYER_COLOR = (0, 255, 200)
ENEMY_1_COLOR = (255, 69, 0)
ENEMY_2_COLOR = (0, 255, 127)
ENEMY_3_COLOR = (138, 43, 226)
TEXT_COLOR = (240, 240, 240)
BULLET_COLOR = (255, 255, 200)
ENEMY_BULLET_COLOR = (255, 50, 50)
UFO_COLOR = (200, 200, 255)
BARRIER_COLOR = (50, 200, 50)
POWERUP_COLOR = (255, 215, 0)
COIN_COLOR = (255, 215, 0)
SHOP_BG = (20, 20, 35)
UI_BG = (10, 10, 20, 180)

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"

# --- FILE HANDLING ---
SAVE_FILE = "neon_save.json"


def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "total_coins": 0,
        "max_lives": 3,
        "score_mult": 1.0,
        "start_shield": False,
        "damage_mult": 1.0
    }


def save_save(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)


# --- SPRITE GENERATOR (Procedural Pixel Art) ---
def create_pixel_art(width, height, color, pattern):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, color, (x * 2, y * 2, 2, 2))
    return surface


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
        self.channels = [pygame.mixer.Channel(i) for i in range(5)]
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
        self.channels[0].play(self.create_tone(800, 0.1, 0.1, 'sawtooth'))

    def play_enemy_shoot(self):
        self.channels[2].play(self.create_tone(150, 0.2, 0.1, 'sawtooth'))

    def play_explosion(self):
        duration = 0.3
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-8000, 8000) for _ in range(samples * 2)]
        self.channels[3].play(pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        ))

    def play_powerup(self):
        for i in range(3):
            self.channels[4].play(self.create_tone(600 + (i * 200), 0.1, 0.2, 'square'))
            pygame.time.set_timer(pygame.USEREVENT, (i + 1) * 100, 1)

    def play_ui_click(self):
        self.channels[4].play(self.create_tone(400, 0.05, 0.2, 'square'))


# --- VISUAL EFFECTS ---

class GlowRenderer:
    @staticmethod
    def draw_glow(surface, color, rect, radius=15, intensity=0.5):
        # Draw multiple layers for glow
        for r in range(radius, 0, -5):
            alpha = int(255 * intensity * (r / radius) * 0.4)
            s = pygame.Surface((rect.width + r * 2, rect.height + r * 2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color[:3], alpha), (0, 0, rect.width + r * 2, rect.height + r * 2), border_radius=5)
            surface.blit(s, (rect.x - r, rect.y - r))

    @staticmethod
    def draw_glow_circle(surface, color, pos, radius=15, intensity=0.5):
        for r in range(radius, 0, -5):
            alpha = int(255 * intensity * (r / radius) * 0.4)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color[:3], alpha), (r, r), r)
            surface.blit(s, (pos[0] - r, pos[1] - r))


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0
        self.decay = 0.02
        self.font = pygame.font.SysFont("Arial", 18, bold=True)

    def update(self):
        self.y -= 1
        self.life -= self.decay

    def draw(self, surface):
        if self.life <= 0: return
        alpha = int(255 * self.life)
        s = pygame.Surface((1, 1), pygame.SRCALPHA)
        text_surf = self.font.render(self.text, True, self.color)
        # Apply alpha
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (self.x, self.y))


class Particle:
    def __init__(self, x, y, color, speed=2):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed_mag = random.uniform(1, speed * 3)
        self.vx = math.cos(angle) * speed_mag
        self.vy = math.sin(angle) * speed_mag
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.06)
        self.gravity = 0.1
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay

    def draw(self, surface):
        if self.life <= 0: return
        alpha = int(255 * self.life)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class Bullet:
    def __init__(self, x, y, is_player=False, speed=BULLET_SPEED):
        self.x, self.y = x, y
        self.width, self.height = 4, 12
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -speed if is_player else ENEMY_BULLET_SPEED
        self.velocity_x = 0
        self.active = True
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6: self.trail.pop(0)

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -100 or self.y > HEIGHT + 100 or self.x < -100 or self.x > WIDTH + 100:
            self.active = False

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail)))
            s = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (1, 1), 1)
            surface.blit(s, (int(tx) - 1, int(ty) - 1))

        GlowRenderer.draw_glow(surface, self.color, self.rect, radius=10, intensity=0.8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect)


class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice([POWERUP_RAPID, POWERUP_SPREAD, POWERUP_SHIELD])
        self.width, self.height = 24, 24
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.active = True
        self.color = POWERUP_COLOR
        self.vy = 2
        self.angle = 0

    def update(self):
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        self.angle += 0.1
        if self.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(s, self.color, (0, 0, self.width, self.height))
        pygame.draw.ellipse(s, (255, 255, 255), (4, 4, self.width - 8, self.height - 8))

        text_map = {POWERUP_RAPID: "R", POWERUP_SPREAD: "S", POWERUP_SHIELD: "H"}
        txt = pygame.font.SysFont("Arial", 14, bold=True).render(text_map[self.type], True, (0, 0, 0))
        txt = pygame.transform.rotate(txt, self.angle * 180 / math.pi)
        s.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - txt.get_height() // 2))

        # Glow
        GlowRenderer.draw_glow(surface, self.color, self.rect, radius=10, intensity=0.6)
        surface.blit(s, (self.x, self.y))


class Player:
    def __init__(self, stats):
        self.x, self.y = WIDTH // 2 - 16, HEIGHT - 60
        self.width, self.height = 32, 32
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 350
        self.active = True
        self.lives = stats['max_lives']
        self.max_lives = stats['max_lives']
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.score_mult = stats['score_mult']

        self.powerups = []
        self.shield_active = stats['start_shield']
        self.shield_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.damage_mult = stats['damage_mult']

    def update(self, keys, current_time):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

        if current_time - self.combo_timer > 1500:
            self.combo = 0
        if self.shield_active and current_time - self.shield_timer > 8000:
            self.shield_active = False

    def shoot(self, game, current_time):
        if current_time - self.last_shot > self.shoot_delay:
            if POWERUP_SPREAD in self.powerups:
                for angle_offset in [-20, 0, 20]:
                    bx = self.x + self.width // 2
                    by = self.y
                    b = Bullet(bx, by, is_player=True)
                    rad = math.radians(angle_offset)
                    b.velocity_y = -BULLET_SPEED * math.cos(rad)
                    b.velocity_x = BULLET_SPEED * math.sin(rad)
                    game.player_bullets.append(b)
            else:
                bullet = Bullet(self.x + self.width // 2, self.y, is_player=True)
                game.player_bullets.append(bullet)

            self.last_shot = current_time
            game.sound_manager.play_shoot()

    def draw(self, surface):
        if self.shield_active:
            GlowRenderer.draw_glow_circle(surface, (100, 255, 255),
                                          (self.x + self.width // 2, self.y + self.height // 2), 25, 0.4)
            pygame.draw.circle(surface, (100, 255, 255), (self.x + self.width // 2, self.y + self.height // 2), 20, 2)

        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))

        # Engine Glow
        glow_size = 8 + int(math.sin(pygame.time.get_ticks() * 0.05) * 3)
        GlowRenderer.draw_glow_circle(surface, (255, 100, 0), (self.x + self.width // 2, self.y + self.height),
                                      glow_size, 0.8)


class Invader:
    def __init__(self, x, y, row, col, level):
        self.x, self.y = x, y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        self.level = level
        self.hp = 1 + (level // 3)  # More health on higher levels

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

        self.animation_offset = random.randint(0, 10)
        self.active = True
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(1500, 4000) // max(1, level * 0.8)
        self.is_on_cooldown = False

    def draw(self, surface, time):
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 2
        scaled_sprite = pygame.transform.scale(self.sprite, (self.width + 5, self.height + 5))
        surface.blit(scaled_sprite, (self.x + sine_offset, self.y))
        self.rect = pygame.Rect(self.x + sine_offset, self.y, self.width + 5, self.height + 5)


class UFO:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.y = 50
        self.speed = 6
        self.move_down_step = 20
        self.active = True
        self.score_value = 500
        self.x = 20
        self.direction = 1
        self.rect = pygame.Rect(0, self.y, self.width, self.height)

    def update(self):
        self.x += self.speed * self.direction
        if self.x < 10:
            self.x = 10;
            self.y += self.move_down_step;
            self.direction = 1
        elif self.x > WIDTH - self.width - 10:
            self.x = WIDTH - self.width - 10;
            self.y += self.move_down_step;
            self.direction = -1
        if self.y > HEIGHT - 150: self.active = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        scaled_sprite = pygame.transform.scale(SPRITE_UFO, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))
        GlowRenderer.draw_glow(surface, UFO_COLOR, self.rect, radius=15, intensity=0.5)


class Barrier:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 60, 40
        self.active = True
        self.segments = []
        self.create_segments()
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def create_segments(self):
        seg_w, seg_h = 4, 4
        for r in range(self.height // seg_h):
            for c in range(self.width // seg_w):
                is_hole = (c % 4 == 1 and r < 3) or (c % 4 == 1 and r > 7)
                if not is_hole:
                    self.segments.append(
                        {'x': self.x + c * seg_w, 'y': self.y + r * seg_h, 'w': seg_w, 'h': seg_h, 'active': True})

    def update(self):
        active = [s for s in self.segments if s['active']]
        if not active:
            self.active = False
            return
        self.rect = pygame.Rect(min(s['x'] for s in active), min(s['y'] for s in active),
                                max(s['x'] + s['w'] for s in active) - min(s['x'] for s in active),
                                max(s['y'] + s['h'] for s in active) - min(s['y'] for s in active))

    def take_damage(self, bullet_rect):
        for s in self.segments:
            if s['active'] and bullet_rect.colliderect(pygame.Rect(s['x'], s['y'], s['w'], s['h'])):
                s['active'] = False
                return True
        return False

    def draw(self, surface):
        for s in self.segments:
            if s['active']:
                c = BARRIER_COLOR
                if s['y'] % 10 == 0: c = (150, 255, 150)
                pygame.draw.rect(surface, c, (s['x'], s['y'], s['w'], s['h']))


# --- MAIN GAME LOGIC ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Invaders: Evolution")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.shop_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.sound_manager = SoundManager()

        # Load Save Data
        self.save_data = load_save()

        # Shop Upgrades (Static Costs)
        self.upgrades = {
            "max_lives": {"cost": 100, "max": 10, "desc": "Start with 1 more life"},
            "score_mult": {"cost": 200, "max": 3.0, "desc": "Increase Score Multiplier (+0.1)"},
            "start_shield": {"cost": 500, "max": 1, "desc": "Start game with Shield"}
        }

        # Game State
        self.state = "MENU"  # MENU, PLAYING, PAUSE, GAMEOVER, SHOP
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.player = None
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.ufo = None
        self.particles = []
        self.floating_texts = []
        self.stars = [Star() for _ in range(100)]
        self.barriers = []

        # Mechanics
        self.enemy_direction = 1
        self.enemy_move_speed = 2
        self.enemy_drop_distance = 10
        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(20000, 40000)

        # Visual Flash
        self.flash_timer = 0
        self.flash_color = (255, 255, 255)

        self.init_enemies()
        self.init_barriers()

    def init_enemies(self):
        self.enemies = []
        for row in range(NUM_ENEMIES_ROWS):
            for col in range(NUM_ENEMIES_COLS):
                x = 50 + col * 45
                y = 60 + row * 40
                self.enemies.append(Invader(x, y, row, col, self.level))
        self.enemy_move_speed = 2 + (self.level * 0.5)

    def init_barriers(self):
        self.barriers = []
        for i in range(4):
            self.barriers.append(Barrier((WIDTH // 5) * (i + 1) - 30, HEIGHT - 120))

    def spawn_explosion(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def spawn_text(self, x, y, text, color=(255, 255, 255)):
        self.floating_texts.append(FloatingText(x, y, text, color))

    def reset_game(self):
        self.player = Player(self.save_data)
        self.score = 0
        self.level = 1
        self.init_enemies()
        self.init_barriers()
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.particles = []
        self.floating_texts = []
        self.ufo = None
        self.state = "PLAYING"

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.state == "MENU":
            if keys[pygame.K_SPACE]:
                self.reset_game()
            elif keys[pygame.K_m] or keys[pygame.K_s]:
                self.state = "SHOP"
                self.sound_manager.play_ui_click()
        elif self.state == "SHOP":
            if keys[pygame.K_ESCAPE] or keys[pygame.K_m]:
                self.state = "MENU"
            elif keys[pygame.K_SPACE]:
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
                self.state = "MENU"
        elif self.state == "GAMEOVER":
            if keys[pygame.K_SPACE]:
                self.reset_game()
            elif keys[pygame.K_ESCAPE]:
                self.state = "MENU"

    def update_logic(self):
        current_time = pygame.time.get_ticks()

        # Update Stars
        for star in self.stars:
            star.update()

        # Flash effect decay
        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.state == "PLAYING":
            # --- UFO LOGIC ---
            if self.ufo_spawn_time == 0:
                self.ufo_spawn_time = current_time
            elif current_time - self.ufo_spawn_time > self.ufo_spawn_interval:
                self.ufo = UFO()
                self.ufo_spawn_time = current_time
                self.ufo_spawn_interval = random.randint(20000, 40000)

            if self.ufo and self.ufo.active:
                self.ufo.update()
                if random.random() < 0.01:
                    b = Bullet(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height, is_player=False)
                    self.enemy_bullets.append(b)
                    self.sound_manager.play_enemy_shoot()
                if not self.ufo.active: self.ufo = None

            # --- ENEMY MOVEMENT ---
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

            # --- ENEMY SHOOTING ---
            if len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                active_enemies = [e for e in self.enemies if e.active and not e.is_on_cooldown]
                if active_enemies and random.random() < (0.03 + self.level * 0.005):
                    shooter = random.choice(active_enemies)
                    b = Bullet(shooter.x + shooter.width // 2, shooter.y + shooter.height, is_player=False)
                    self.enemy_bullets.append(b)
                    shooter.last_shot_time = current_time
                    shooter.is_on_cooldown = True
                    self.sound_manager.play_enemy_shoot()

            for enemy in self.enemies:
                if enemy.is_on_cooldown and (current_time - enemy.last_shot_time > enemy.shot_cooldown * 1.5):
                    enemy.is_on_cooldown = False

            # --- BULLETS & POWERUPS ---
            for b in self.player_bullets[:]:
                b.update()
                if not b.active: self.player_bullets.remove(b)

            for b in self.enemy_bullets[:]:
                b.update()
                if not b.active: self.enemy_bullets.remove(b)

            for p in self.powerups[:]:
                p.update()
                if not p.active:
                    self.powerups.remove(p)
                elif p.rect.colliderect(self.player.rect):
                    self.player.powerups.append(p.type)
                    if p.type == POWERUP_SHIELD:
                        self.player.shield_active = True
                        self.player.shield_timer = current_time
                    self.spawn_explosion(p.x, p.y, POWERUP_COLOR)
                    self.sound_manager.play_powerup()
                    self.spawn_text(p.x, p.y, "POWERUP!", POWERUP_COLOR)
                    self.powerups.remove(p)

            # --- COLLISIONS ---
            # Player Bullets vs Enemies
            for b in self.player_bullets[:]:
                hit = False
                for enemy in self.enemies:
                    if enemy.active and b.rect.colliderect(enemy.rect):
                        enemy.hp -= 1
                        if enemy.hp <= 0:
                            enemy.active = False
                            self.spawn_explosion(enemy.x, enemy.y, enemy.color)
                            self.sound_manager.play_explosion()

                            # Score & Combo
                            points = int(enemy.score_value * self.player.combo * self.player.score_mult)
                            self.score += points
                            self.player.combo += 1
                            self.player.combo_timer = current_time
                            self.spawn_text(enemy.x, enemy.y, str(points), BULLET_COLOR)

                            # Coin Chance
                            if random.random() < 0.15:
                                self.spawn_text(enemy.x, enemy.y, "+10 COINS", COIN_COLOR)
                                # Add to save data immediately
                                self.save_data['total_coins'] += 10
                                save_save(self.save_data)

                            if random.random() < 0.1:
                                self.powerups.append(PowerUp(enemy.x, enemy.y))

                            hit = True
                            break

                        # Hit effect
                        b.active = False
                        hit = True

                if not hit:
                    # Bullet vs Barriers
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                            self.spawn_text(b.x, b.y, "Pew!", (200, 200, 200))
                            break

                    # Bullet vs Enemy Bullet
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
                        self.spawn_text(self.player.x, self.player.y, "SHIELD DOWN!", (100, 255, 255))
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

            # Enemy vs Player (Crash)
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    enemy.active = False
                    break

            # UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        self.spawn_explosion(self.ufo.x, self.ufo.y, UFO_COLOR)
                        self.sound_manager.play_explosion()
                        self.spawn_text(self.ufo.x, self.ufo.y, "UFO!", UFO_COLOR)
                        self.ufo.active = False
                        self.ufo = None
                        break

            # Level Complete
            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 1
                self.init_enemies()
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255))
                self.spawn_text(WIDTH // 2 - 50, HEIGHT // 2, "LEVEL " + str(self.level), (0, 255, 0))

            # Particles & Text
            for p in self.particles: p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            for t in self.floating_texts: t.update()
            self.floating_texts = [t for t in self.floating_texts if t.life > 0]

    def player_hit(self):
        self.spawn_explosion(self.player.x, self.player.y, self.player.color, 30)
        self.sound_manager.play_explosion()

        # Screen Flash
        self.flash_timer = 10
        self.flash_color = (255, 0, 0)

        self.player.lives -= 1
        self.player.combo = 0
        self.player.powerups = []
        self.player.shield_active = False

        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            # Save High Score logic if needed
            if self.score > self.high_score:
                self.high_score = self.score

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Draw Stars
        for star in self.stars:
            star.draw(self.screen)

        # Draw Game World
        if self.state in ["PLAYING", "PAUSE"]:
            for b in self.barriers:
                if b.active: b.draw(self.screen)

            for enemy in self.enemies:
                if enemy.active: enemy.draw(self.screen, pygame.time.get_ticks())

            if self.ufo and self.ufo.active:
                self.ufo.draw(self.screen)

            if self.player.active:
                self.player.draw(self.screen)

            for b in self.player_bullets: b.draw(self.screen)
            for b in self.enemy_bullets: b.draw(self.screen)
            for p in self.powerups: p.draw(self.screen)
            for p in self.particles: p.draw(self.screen)

            self.draw_hud()

        # Draw Particles/Text (Global)
        for t in self.floating_texts: t.draw(self.screen)

        # Draw UI States
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "SHOP":
            self.draw_shop()
        elif self.state == "PAUSE":
            self.draw_overlay("PAUSED", "Press P to Resume")
        elif self.state == "GAMEOVER":
            self.draw_overlay("GAME OVER", "Press SPACE to Retry")
            # Show Coins Earned
            coin_text = self.font.render("Earned Coins: " + str(self.save_data.get('total_coins', 0)), True, COIN_COLOR)
            self.screen.blit(coin_text, (WIDTH // 2 - coin_text.get_width() // 2, HEIGHT // 2 + 100))

        # Screen Flash Overlay
        if self.flash_timer > 0:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((*self.flash_color[:3], 150))
            self.screen.blit(s, (0, 0))

        # Vignette
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (0, 0, 0, 150), (WIDTH // 2, HEIGHT // 2), WIDTH)
        self.screen.blit(overlay, (0, 0))

        pygame.display.flip()

    def draw_hud(self):
        # Semi-transparent HUD Bar
        hud_rect = pygame.Rect(0, 0, WIDTH, 40)
        s = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        s.fill(UI_BG)
        self.screen.blit(s, (0, 0))

        score_surf = self.large_font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_surf, (15, 5))

        combo_surf = self.font.render(f"COMBO: x{self.player.combo}", True, COIN_COLOR)
        self.screen.blit(combo_surf, (15 + score_surf.get_width() + 20, 10))

        lives_text = "LIVES: " + "❤" * self.player.lives
        lives_surf = self.font.render(lives_text, True, (255, 50, 50))
        self.screen.blit(lives_surf, (WIDTH - 150, 10))

        # Active Powerups
        pu_text = ""
        if POWERUP_RAPID in self.player.powerups: pu_text += "R"
        if POWERUP_SPREAD in self.player.powerups: pu_text += "S"
        if self.player.shield_active: pu_text += "H"
        if pu_text:
            pu_surf = self.font.render(f"ACTIVE: {pu_text}", True, POWERUP_COLOR)
            self.screen.blit(pu_surf, (WIDTH // 2 - 50, 10))

    def draw_menu(self):
        title = self.large_font.render("NEON INVADERS", True, PLAYER_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        GlowRenderer.draw_glow(self.screen, PLAYER_COLOR, title.get_rect(), radius=20, intensity=0.5)

        sub1 = self.font.render("Press SPACE to Start", True, TEXT_COLOR)
        self.screen.blit(sub1, (WIDTH // 2 - sub1.get_width() // 2, 220))

        sub2 = self.font.render("Press S or M for Shop", True, COIN_COLOR)
        self.screen.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, 250))

        # Show Coins
        coins = self.font.render(f"Coins: {self.save_data['total_coins']}", True, COIN_COLOR)
        self.screen.blit(coins, (WIDTH // 2 - coins.get_width() // 2, 300))

    def draw_shop(self):
        # Background
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        title = self.large_font.render("UPGRADE SHOP", True, COIN_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        sub = self.font.render(f"Coins: {self.save_data['total_coins']} | Press SPACE to Play", True, TEXT_COLOR)
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 100))

        # Upgrade List
        y_pos = 160
        keys = list(self.upgrades.keys())

        for key in keys:
            info = self.upgrades[key]
            current_val = self.save_data.get(key, 0) if key != "start_shield" else self.save_data.get(key, False)

            # Button Rect
            btn_rect = pygame.Rect(WIDTH // 2 - 200, y_pos, 400, 60)
            pygame.draw.rect(self.screen, (40, 40, 60), btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, (60, 60, 80), btn_rect, 2, border_radius=10)

            # Text
            name = key.replace("_", " ").upper()
            val_str = str(current_val) if key != "start_shield" else "ON" if current_val else "OFF"

            txt1 = self.shop_font.render(f"{name}: {val_str}", True, TEXT_COLOR)
            self.screen.blit(txt1, (btn_rect.x + 10, btn_rect.y + 5))

            txt2 = self.small_font.render(info["desc"], True, (150, 150, 150))
            self.screen.blit(txt2, (btn_rect.x + 10, btn_rect.y + 30))

            # Cost
            cost_str = f"Cost: {info['cost']}" if current_val < info['max'] else "MAXED"
            cost_surf = self.font.render(cost_str, True, COIN_COLOR if current_val < info['max'] else (100, 100, 100))
            self.screen.blit(cost_surf, (btn_rect.right - 100, btn_rect.y + 25))

            # Click Logic
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if btn_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, (80, 80, 100), btn_rect, 2, border_radius=10)
                if click[0]:
                    self.handle_shop_click(key, info, current_val)

            y_pos += 70

        y_pos += 20
        quit_txt = self.font.render("Press ESC to Exit Shop", True, (100, 100, 100))
        self.screen.blit(quit_txt, (WIDTH // 2 - quit_txt.get_width() // 2, y_pos))

    def handle_shop_click(self, key, info, current_val):
        if current_val >= info['max']: return

        if self.save_data['total_coins'] >= info['cost']:
            self.save_data['total_coins'] -= info['cost']

            if key == "max_lives":
                self.save_data['max_lives'] += 1
            elif key == "score_mult":
                self.save_data['score_mult'] += 0.1
            elif key == "start_shield":
                self.save_data['start_shield'] = True

            save_save(self.save_data)
            self.sound_manager.play_powerup()

    def draw_overlay(self, title, sub):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))

        t_surf = self.large_font.render(title, True, (255, 50, 50))
        self.screen.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, HEIGHT // 2 - 60))

        s_surf = self.font.render(sub, True, TEXT_COLOR)
        self.screen.blit(s_surf, (WIDTH // 2 - s_surf.get_width() // 2, HEIGHT // 2 + 10))


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.2, 1.0)
        self.brightness = random.randint(100, 255)
        self.layer = random.randint(1, 3)  # Parallax layers

    def update(self):
        self.y += self.speed * self.layer
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


if __name__ == "__main__":
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                # For powerup sound sequence
                game.sound_manager.create_tone(800, 0.05, 0.1, 'square').play()

        game.handle_input()
        game.update_logic()
        game.draw()
        game.clock.tick(FPS)

    pygame.quit()
