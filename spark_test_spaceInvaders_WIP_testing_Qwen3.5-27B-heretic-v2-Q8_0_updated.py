# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
# Update the code to make provided python game more addictive and more fun for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user (but please do not use screen shaking effects)  and therefore more addictive to play. Also check possibility for taking advantage of upgrades for player  in new games by using achievements in previous game. I want to introduce rewards for user playing game multiple times.  Don't use any external files for graphic and sound assets, (saving game progress to external file is fine ) in your enhancements. Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-27B-heretic-v2-Q8_0.gguf  --mmproj /AI/models/Qwen3.5-27B-mmproj-F32.gguf

import pygame
import random
import math
import json
import os
import time

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5
MAX_ENEMY_BULLETS = 6
NUM_ENEMIES_ROWS = 4
NUM_ENEMIES_COLS = 8
SAVE_FILE = "neon_invaders_save.json"

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
FOUNT_COLOR = (0, 255, 0)  # Green for text

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"

# Upgrade Definitions
UPGRADES = [
    {
        "id": "starter_shield",
        "name": "Starter Shield",
        "desc": "Start each game with a Shield",
        "req_score": 0,
        "req_plays": 5,
        "color": (0, 255, 255)
    },
    {
        "id": "rapid_start",
        "name": "Rapid Start",
        "desc": "Start with faster fire rate",
        "req_score": 5000,
        "req_plays": 0,
        "color": (255, 100, 100)
    },
    {
        "id": "extra_life",
        "name": "Extra Life",
        "desc": "Start with 4 Lives",
        "req_score": 10000,
        "req_plays": 0,
        "color": (255, 0, 0)
    },
    {
        "id": "neon_skin",
        "name": "Neon Skin",
        "desc": "Unlock Cyberpunk Ship Color",
        "req_score": 50000,
        "req_plays": 0,
        "color": (255, 100, 255)
    }
]


# --- SPRITE GENERATOR (Procedural Pixel Art) ---
def create_pixel_art(width, height, color, pattern):
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
        self.channels[1].play(self.create_tone(1100, 0.05, 0.1, 'square'))

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
        # Play a pleasant arpeggio for powerup
        self.channels[4].play(self.create_tone(600, 0.05, 0.2, 'square'))
        pygame.time.set_timer(pygame.USEREVENT + 1, 80, 1)
        pygame.time.set_timer(pygame.USEREVENT + 2, 160, 1)

    def play_combo(self):
        self.channels[5].play(self.create_tone(1200, 0.05, 0.1, 'square'))
        self.channels[6].play(self.create_tone(1500, 0.05, 0.1, 'square'))

    def play_level_up(self):
        self.channels[7].play(self.create_tone(400, 0.1, 0.2, 'sawtooth'))
        pygame.time.set_timer(pygame.USEREVENT + 3, 100, 1)


# --- CLASSES ---

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = 1.0
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.velocity_y = -2
        self.rendered = self.font.render(text, True, color)
        self.rect = self.rendered.get_rect(center=(x, y))

    def update(self):
        self.y += self.velocity_y
        self.life -= 0.03
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        if self.life <= 0:
            return False
        # Fade out
        alpha = int(255 * self.life)
        s = pygame.Surface((self.rendered.get_width(), self.rendered.get_height()), pygame.SRCALPHA)
        s.blit(self.rendered, (0, 0))
        s.set_alpha(alpha)
        surface.blit(s, (int(self.x) - self.rendered.get_width() // 2, int(self.y)))
        return True


class Particle:
    def __init__(self, x, y, color, speed=3):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed_mag = random.uniform(1, speed * 2)
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
        if self.life <= 0:
            return
        alpha = int(255 * self.life)
        color = (*self.color[:3], alpha) if len(self.color) > 3 else self.color
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
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
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail)))
            color = (*self.color[:3], alpha)
            s = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (1, 1), 1)
            surface.blit(s, (int(tx) - 1, int(ty) - 1))

        # Draw main bullet
        pygame.draw.rect(surface, self.color, self.rect)
        # Glow
        pygame.draw.rect(surface, (255, 255, 200), self.rect.inflate(-1, -1))


class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice([POWERUP_RAPID, POWERUP_SPREAD, POWERUP_SHIELD])
        self.width, self.height = 24, 24
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
        self.active = True
        self.color = POWERUP_COLOR
        self.vy = 2
        self.angle = 0

    def update(self):
        self.y += self.vy
        self.rect.topleft = (self.x - self.width // 2, self.y - self.height // 2)
        self.angle += 0.2
        if self.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(s, self.color, (0, 0, self.width, self.height))
        pygame.draw.ellipse(s, (255, 255, 255), (2, 2, self.width - 4, self.height - 4), 2)

        text_map = {POWERUP_RAPID: "R", POWERUP_SPREAD: "S", POWERUP_SHIELD: "H"}
        txt = pygame.font.SysFont("Arial", 16, bold=True).render(text_map[self.type], True, (0, 0, 0))
        txt = pygame.transform.rotate(txt, self.angle * 180 / math.pi)
        s.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - txt.get_height() // 2))
        surface.blit(s, (int(self.x - self.width // 2), int(self.y - self.height // 2)))


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
                color = BARRIER_COLOR
                if segment['y'] % 10 == 0:
                    color = (150, 255, 150)
                pygame.draw.rect(surface, color, (segment['x'], segment['y'], segment['width'], segment['height']))


class Player:
    def __init__(self, upgrades=None):
        self.upgrades = upgrades or {}
        self.x, self.y = WIDTH // 2 - 16, HEIGHT - 60
        self.width, self.height = 32, 32
        self.color = PLAYER_COLOR
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 350
        self.active = True
        self.lives = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Apply Upgrades
        if self.upgrades.get("extra_life"):
            self.lives = 4
        if self.upgrades.get("rapid_start"):
            self.shoot_delay = 200
        if self.upgrades.get("neon_skin"):
            self.color = (255, 0, 255)  # Cyberpunk Purple
        if self.upgrades.get("starter_shield"):
            self.shield_active = True
            self.shield_timer = pygame.time.get_ticks()
        else:
            self.shield_active = False
            self.shield_timer = 0

        # Powerups
        self.powerups = []
        self.shield_timer = pygame.time.get_ticks() if self.shield_active else 0
        self.combo = 0
        self.combo_timer = 0

    def update(self, keys, current_time):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

        # Combo decay
        if current_time - self.combo_timer > 2000:  # Longer combo window for addictiveness
            self.combo = 0

        # Shield decay
        if self.shield_active and current_time - self.shield_timer > 10000:
            self.shield_active = False

    def shoot(self, game, current_time):
        if current_time - self.last_shot > self.shoot_delay:
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
                bullet_x = self.x + self.width // 2
                bullet_y = self.y
                bullet = Bullet(bullet_x, bullet_y, is_player=True)
                game.player_bullets.append(bullet)

            self.last_shot = current_time
            game.sound_manager.play_shoot()

    def draw(self, surface):
        # Draw Shield if active
        if self.shield_active:
            pygame.draw.circle(surface, (100, 255, 255),
                               (int(self.x + self.width // 2), int(self.y + self.height // 2)),
                               self.width // 2 + 5, 2)

        # Draw Sprite (Scaled) with Glow
        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))

        # Glow Effect
        glow_surf = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        glow_color = (*self.color[:3], 100)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, self.width + 10, self.height + 10))
        surface.blit(glow_surf, (self.x - 5, self.y - 5))

        surface.blit(scaled_sprite, (int(self.x), int(self.y)))

        # Engine Glow
        glow_size = 5 + int(math.sin(pygame.time.get_ticks() * 0.02) * 2)
        pygame.draw.circle(surface, (255, 200, 0), (int(self.x + self.width // 2), int(self.y + self.height)),
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

    def draw(self, surface, time):
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 3
        scaled_sprite = pygame.transform.scale(self.sprite, (self.width + 5, self.height + 5))
        surface.blit(scaled_sprite, (int(self.x + sine_offset), int(self.y)))
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
        surface.blit(scaled_sprite, (int(self.x), int(self.y)))


class PersistenceManager:
    def __init__(self):
        self.total_score = 0
        self.games_played = 0
        self.max_level = 1
        self.unlocked_upgrades = []

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.total_score = data.get('total_score', 0)
                    self.games_played = data.get('games_played', 0)
                    self.max_level = data.get('max_level', 1)
                    self.unlocked_upgrades = data.get('unlocked_upgrades', [])
            except:
                pass
        else:
            self.save()  # Create initial file

    def save(self):
        data = {
            'total_score': self.total_score,
            'games_played': self.games_played,
            'max_level': self.max_level,
            'unlocked_upgrades': self.unlocked_upgrades
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)

    def get_active_upgrades(self):
        active_upgrades = {}
        for upgrade in UPGRADES:
            if upgrade['id'] in self.unlocked_upgrades:
                active_upgrades[upgrade['id']] = True
        return active_upgrades

    def add_score(self, score):
        self.total_score += score
        self.save()

    def add_game(self):
        self.games_played += 1
        self.save()

    def update_level(self, level):
        if level > self.max_level:
            self.max_level = level
            self.save()


# --- GAME LOGIC ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.warning_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.sound_manager = SoundManager()
        self.persistence = PersistenceManager()
        self.persistence.load()

        self.state = "START"
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
        self.stars = [Star() for _ in range(80)]
        self.barriers = []

        self.enemy_direction = 1
        self.enemy_move_speed = 2
        self.enemy_drop_distance = 10
        self.last_enemy_move_time = 0

        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(20000, 40000)

        self.flash_alpha = 0
        self.flash_timer = 0
        self.screen_shake = 0  # Add this line

        self.init_enemies()
        self.init_barriers()
        self.player = Player()

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
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def reset_game(self):
        upgrades = self.persistence.get_active_upgrades()
        self.player = Player(upgrades=upgrades)
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
        self.floating_texts = []
        self.ufo = None
        self.state = "PLAYING"
        self.persistence.add_game()

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
            if keys[pygame.K_SPACE]:
                self.reset_game()
            elif keys[pygame.K_ESCAPE]:
                self.state = "START"

    def update_logic(self):
        current_time = pygame.time.get_ticks()
        for star in self.stars:
            star.update()

        if self.state == "PLAYING":
            # UFO Spawning
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

            # Enemy Movement (Smooth)
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
                        self.sound_manager.play_powerup()
                        self.powerups.remove(p)
                        self.spawn_explosion(p.x, p.y, POWERUP_COLOR)

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
                        self.persistence.add_score(points)
                        self.player.combo = min(self.player.combo + 1, 20)
                        self.player.combo_timer = current_time
                        self.sound_manager.play_combo()
                        self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color)
                        self.sound_manager.play_explosion()
                        self.floating_texts.append(
                            FloatingText(enemy.x + enemy.width // 2, enemy.y, f"+{points}", (255, 255, 0)))

                        if random.random() < 0.15:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))
                        hit = True
                        break

                if not hit:
                    # Bullet vs Barrier
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                            break

                    if not b.active:
                        # Bullet vs Enemy Bullet
                        for eb in self.enemy_bullets[:]:
                            if b.rect.colliderect(eb.rect):
                                b.active = False
                                eb.active = False
                                self.spawn_explosion(b.x, b.y, (255, 255, 255))
                                break

            # 2. Enemy Bullets vs Barriers (Moved before Player for protection)
            for b in self.enemy_bullets[:]:
                for barrier in self.barriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                        break

            # 3. Enemy Bullets vs Player
            for b in self.enemy_bullets[:]:
                if b.active and b.rect.colliderect(self.player.rect):
                    if self.player.shield_active:
                        self.player.shield_active = False
                        self.spawn_explosion(self.player.x, self.player.y, (100, 255, 255))
                        self.flash_alpha = 100
                        self.flash_timer = current_time
                        b.active = False
                    else:
                        self.player_hit()
                        b.active = False
                    break

            # 4. Enemies vs Player (Game Over)
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color)
                    enemy.active = False
                    break

            # 5. UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        # Capture coordinates BEFORE setting ufo to None
                        ufo_x = self.ufo.x + self.ufo.width // 2
                        ufo_y = self.ufo.y + self.ufo.height // 2

                        self.score += self.ufo.score_value
                        self.persistence.add_score(self.ufo.score_value)
                        self.spawn_explosion(self.ufo.x, self.ufo.y, UFO_COLOR)
                        self.sound_manager.play_explosion()
                        self.ufo.active = False
                        self.ufo = None

                        # Create Floating Text after ufo is None
                        self.floating_texts.append(FloatingText(ufo_x, ufo_y, "BOSS!", (255, 0, 255)))
                        break

            # Level Complete
            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 1
                self.init_enemies()
                self.score += 1000
                self.persistence.add_score(1000)
                self.persistence.update_level(self.level)
                self.sound_manager.play_level_up()
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255))

            # Particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            # Floating Texts
            for t in self.floating_texts:
                t.update()
            self.floating_texts = [t for t in self.floating_texts if t.life > 0]

            # Flash Decay
            if self.flash_alpha > 0:
                self.flash_alpha = max(0, self.flash_alpha - 10)

            # Flash Decay (for hit effects)
            if self.flash_alpha > 0:
                self.flash_alpha = max(0, self.flash_alpha - 10)

            # Screen Shake Decay (if used)
            if self.screen_shake > 0:
                self.screen_shake -= 0.5
                if self.screen_shake < 0:
                    self.screen_shake = 0

    def player_hit(self):
        self.spawn_explosion(self.player.x + self.player.width // 2, self.player.y + self.player.height // 2,
                             self.player.color)
        self.sound_manager.play_explosion()
        self.player.lives -= 1
        self.player.combo = 0
        self.player.powerups = []
        self.player.shield_active = False
        self.flash_alpha = 100
        self.flash_timer = pygame.time.get_ticks()
        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score
                self.persistence.max_level = max(self.persistence.max_level, self.level)
                self.persistence.save()

    def draw(self):
        # Background
        bg_surface = pygame.Surface((WIDTH, HEIGHT))
        bg_surface.fill(BG_COLOR)

        # Stars
        for star in self.stars:
            star.draw(bg_surface)

        # Apply Background
        self.screen.blit(bg_surface, (0, 0))

        if self.state == "START":
            self.draw_menu("NEON INVADERS", "Press SPACE to Start", "Arrows: Move | Space: Shoot | P: Pause")
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
            for t in self.floating_texts:
                t.draw(self.screen)
            self.draw_hud()
        elif self.state == "PAUSE":
            self.draw_menu("PAUSED", "Press P to Resume | ESC to Quit")
        elif self.state in ["GAMEOVER", "VICTORY"]:
            title = "GAME OVER" if self.state == "GAMEOVER" else "LEVEL COMPLETE!"
            color = (255, 50, 50) if self.state == "GAMEOVER" else (50, 255, 50)
            self.draw_menu(title, f"Score: {self.score}", "High Score: " + str(self.high_score))

        # Flash Effect for explosions/hits (not a permanent overlay)
        if self.flash_alpha > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, self.flash_alpha))
            self.screen.blit(flash, (0, 0))
            self.flash_alpha -= 10
            if self.flash_alpha < 0:
                self.flash_alpha = 0

        pygame.display.flip()

    def draw_menu(self, title="NEON INVADERS", sub1="Press SPACE to Start", sub2=""):
        # Draw Progress to Upgrades
        upg_text = f"Progress: {self.persistence.total_score} Score"
        upg_surf = pygame.font.SysFont("Arial", 14).render(upg_text, True, (100, 100, 100))
        self.screen.blit(upg_surf, (10, HEIGHT - 30))

        if title == "NEON INVADERS":
            # List Unlocked Upgrades
            y_offset = HEIGHT // 2 + 80
            for i, u in enumerate(UPGRADES):
                unlocked = u['id'] in self.persistence.unlocked_upgrades
                color = (0, 255, 0) if unlocked else (150, 0, 0)
                status = "[UNLOCKED]" if unlocked else "[LOCKED]"
                text = f"{status} {u['name']}"
                surf = pygame.font.SysFont("Arial", 16).render(text, True, color)
                self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y_offset + (i * 20)))

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
        pu_surf = self.font.render(f"PU: {powerup_text or '-'}", True, POWERUP_COLOR)

        self.screen.blit(score_surf, (15, 10))
        self.screen.blit(lives_surf, (WIDTH - 160, 10))
        self.screen.blit(level_surf, (WIDTH // 2 - 60, 10))
        self.screen.blit(combo_surf, (15, 35))
        self.screen.blit(pu_surf, (WIDTH - 160, 35))

        # Draw Next Reward Progress
        next_reward = next((u for u in UPGRADES if u['id'] not in self.persistence.unlocked_upgrades), None)
        if next_reward:
            req = next_reward['req_score']
            progress = min(100, (self.persistence.total_score / req) * 100) if req > 0 else 100
            next_surf = pygame.font.SysFont("Arial", 12).render(f"Next: {next_reward['name']} ({int(progress)}%)", True,
                                                                (255, 0, 0))
            self.screen.blit(next_surf, (WIDTH // 2 - next_surf.get_width() // 2, HEIGHT - 20))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type in [pygame.USEREVENT + 1, pygame.USEREVENT + 2]:
                    self.sound_manager.create_tone(900, 0.05, 0.2, 'square').play()
                if event.type == pygame.USEREVENT + 3:
                    self.sound_manager.create_tone(600, 0.1, 0.2, 'square').play()

            self.handle_input()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)
        self.persistence.save()
        pygame.quit()


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.2, 1.5)
        self.brightness = random.randint(50, 255)

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
