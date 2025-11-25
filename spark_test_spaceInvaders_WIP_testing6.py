# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-122B-A10B-Q6HALO.gguf  --mmproj /AI/models/Qwen3.5-122B-A10B_mmproj-F32.gguf

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

# Save file path
SAVE_FILE = "space_invaders_save.json"

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
COMBO_COLOR = (255, 215, 0)
SCORE_TEXT_COLOR = (255, 255, 255)

# Powerup Types
POWERUP_RAPID = "RAPID"
POWERUP_SPREAD = "SPREAD"
POWERUP_SHIELD = "SHIELD"


# --- SAVE SYSTEM ---
class SaveManager:
    def __init__(self, filename):
        self.filename = filename
        self.data = {
            "high_score": 0,
            "total_games": 0,
            "total_kills": 0,
            "max_combo": 0,
            "settings": {
                "volume": 0.5,
                "music": True,
                "sfx": True
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except:
                pass

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def update_high_score(self, score):
        if score > self.data["high_score"]:
            self.data["high_score"] = score
            self.save()
        return score > self.data.get("old_high_score", 0)

    def increment_game(self):
        self.data["total_games"] += 1
        self.save()

    def increment_kills(self, count):
        self.data["total_kills"] += count
        self.save()

    def update_max_combo(self, combo):
        if combo > self.data["max_combo"]:
            self.data["max_combo"] = combo
            self.save()


# --- AUDIO SYSTEM ---
class SoundManager:
    def __init__(self, volume=0.5):
        pygame.mixer.init(44100, -16, 2, 512)
        self.channels = [pygame.mixer.Channel(i) for i in range(6)]
        self.sample_rate = 44100
        self.volume = volume

    def set_volume(self, vol):
        self.volume = vol
        for channel in self.channels:
            channel.set_volume(min(1.0, vol))

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
        self.channels[0].play(self.create_tone(880, 0.1, 0.15 * self.volume, 'square'))
        self.channels[1].play(self.create_tone(1100, 0.1, 0.15 * self.volume, 'square'))

    def play_enemy_shoot(self):
        self.channels[2].play(self.create_tone(200, 0.2, 0.1 * self.volume, 'sawtooth'))

    def play_explosion(self):
        duration = 0.25
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-16384, 16384) for _ in range(samples * 2)]
        self.channels[3].play(pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        ))

    def play_powerup(self):
        self.channels[4].play(self.create_tone(600, 0.1, 0.2 * self.volume, 'square'))
        self.channels[4].play(self.create_tone(800, 0.1, 0.2 * self.volume, 'square'))

    def play_combo(self, combo):
        base_freq = 440 + combo * 50
        self.channels[5].play(self.create_tone(base_freq, 0.08, 0.1 * self.volume, 'square'))

    def play_level_complete(self):
        for i in range(3):
            self.channels[5].play(self.create_tone(440 + i * 100, 0.15, 0.2 * self.volume, 'square'))

    def play_new_high_score(self):
        self.channels[5].play(self.create_tone(880, 0.2, 0.3 * self.volume, 'square'))
        self.channels[5].play(self.create_tone(1100, 0.2, 0.3 * self.volume, 'square'))


# --- PARTICLE SYSTEM ---
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


class GlowEffect:
    @staticmethod
    def draw_glow(surface, rect, color, intensity=1.5):
        for i in range(3):
            alpha = int(100 / (i + 1) * intensity)
            glow_color = (*color[:3], alpha)
            s = pygame.Surface((rect.width + (i + 1) * 4, rect.height + (i + 1) * 4), pygame.SRCALPHA)
            pygame.draw.rect(s, glow_color, (0, 0, s.get_width(), s.get_height()), border_radius=2)
            surface.blit(s, (rect.x - (i + 1) * 2, rect.y - (i + 1) * 2))


# --- SPRITE GENERATOR ---
def create_pixel_art(width, height, color, pattern):
    surface = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, color, (x * 2, y * 2, 2, 2))
    return surface


# --- STAR BACKGROUND ---
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.2, 2.0)
        self.brightness = random.randint(100, 255)
        self.pulse = 0
        self.pulse_speed = random.uniform(0.05, 0.15)

    def update(self):
        self.y += self.speed
        self.pulse += self.pulse_speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        brightness = min(255, int(self.brightness + math.sin(self.pulse) * 50))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


# --- GAME OBJECTS ---
class Bullet:
    def __init__(self, x, y, is_player=False, speed=BULLET_SPEED):
        self.x, self.y = x, y
        self.width, self.height = 4, 10
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -speed if is_player else ENEMY_BULLET_SPEED
        self.velocity_x = 0
        self.active = True
        self.trail = []
        self.glow_intensity = 1.0

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.y += self.velocity_y
        self.x += self.velocity_x
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            glow_color = (*self.color[:3], alpha)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, glow_color, (2, 2), 2)
            surface.blit(s, (int(tx) - 2, int(ty) - 2))

        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (255, 255, 200), self.rect.inflate(-1, -1))
        GlowEffect.draw_glow(surface, self.rect, self.color, 0.5)


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
        self.pulse = 0

    def update(self):
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        self.angle += 0.05
        self.pulse += 0.1
        if self.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        pulse_scale = 1 + math.sin(self.pulse) * 0.15
        scaled_w = int(self.width * pulse_scale)
        scaled_h = int(self.height * pulse_scale)

        s = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, self.color, (0, 0, scaled_w, scaled_h))
        pygame.draw.ellipse(s, (255, 255, 255), (4, 4, scaled_w - 8, scaled_h - 8))

        text_map = {POWERUP_RAPID: "R", POWERUP_SPREAD: "S", POWERUP_SHIELD: "H"}
        txt = pygame.font.SysFont("Arial", 16, bold=True).render(text_map[self.type], True, (0, 0, 0))
        s.blit(txt, (scaled_w // 2 - txt.get_width() // 2, scaled_h // 2 - txt.get_height() // 2))

        GlowEffect.draw_glow(surface, pygame.Rect(self.x, self.y, scaled_w, scaled_h), POWERUP_COLOR, 1.5)
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
                        'hit_count': 0
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
                    segment['hit_count'] += 1
                    return True
        return False

    def draw(self, surface):
        for segment in self.segments:
            if segment['active']:
                color = BARRIER_COLOR
                if segment['y'] % 10 == 0:
                    color = (150, 255, 150)
                pygame.draw.rect(surface, color, (segment['x'], segment['y'], segment['width'], segment['height']))
                if segment['hit_count'] > 0:
                    damage_alpha = min(200, segment['hit_count'] * 40)
                    damage_color = (255, damage_alpha, damage_alpha)
                    pygame.draw.rect(surface, damage_color, (segment['x'], segment['y'], segment['width'], segment['height']), 1)


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
        self.powerups = []
        self.shield_active = False
        self.shield_timer = 0
        self.combo = 0
        self.combo_timer = 0

    def update(self, keys, current_time):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

        if current_time - self.combo_timer > 1000:
            self.combo = 0

        if self.shield_active and current_time - self.shield_timer > 10000:
            self.shield_active = False

    def shoot(self, game, current_time):
        if current_time - self.last_shot > self.shoot_delay:
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
        if self.shield_active:
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3
            pygame.draw.circle(surface, (100, 255, 255),
                               (self.x + self.width // 2, self.y + self.height // 2),
                               self.width // 2 + 5 + pulse, 2)

        scaled_sprite = pygame.transform.scale(SPRITE_PLAYER, (self.width, self.height))
        surface.blit(scaled_sprite, (self.x, self.y))

        glow_size = 5 + int(math.sin(pygame.time.get_ticks() * 0.02) * 3)
        pygame.draw.circle(surface, (255, 200, 0), (self.x + self.width // 2, self.y + self.height), glow_size)

        GlowEffect.draw_glow(surface, self.rect, PLAYER_COLOR, 0.8)


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
        self.health = 1
        self.max_health = 1 + (level // 3)

    def draw(self, surface, time):
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 3
        scaled_sprite = pygame.transform.scale(self.sprite, (self.width + 5, self.height + 5))
        surface.blit(scaled_sprite, (self.x + sine_offset, self.y))

        self.rect = pygame.Rect(self.x + sine_offset, self.y, self.width + 5, self.height + 5)

        if self.health > 1:
            health_bar_width = self.width + 5
            health_bar_height = 4
            pygame.draw.rect(surface, (100, 100, 100),
                             (self.x + sine_offset, self.y - 8, health_bar_width, health_bar_height))
            health_ratio = self.health / self.max_health
            health_color = (255, int(255 * health_ratio), 0)
            pygame.draw.rect(surface, health_color,
                             (self.x + sine_offset, self.y - 8, health_bar_width * health_ratio, health_bar_height))


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
        self.pulse += 0.1

    def draw(self, surface):
        pulse_scale = 1 + math.sin(self.pulse) * 0.1
        scaled_sprite = pygame.transform.scale(SPRITE_UFO, (int(self.width * pulse_scale), int(self.height * pulse_scale)))
        surface.blit(scaled_sprite, (self.x, self.y))
        GlowEffect.draw_glow(surface, self.rect, UFO_COLOR, 1.0)


class ScorePopup:
    def __init__(self, x, y, score, combo=1):
        self.x, self.y = x, y
        self.score = score
        self.combo = combo
        self.life = 1.0
        self.decay = 0.02
        self.dy = -1

    def update(self):
        self.y += self.dy
        self.life -= self.decay
        self.dy -= 0.02

    def draw(self, surface, font):
        if self.life <= 0:
            return
        color = (255, 215, 0)
        text = f"+{self.score * self.combo}"
        if self.combo > 1:
            text = f"{text} x{self.combo}"
        surf = font.render(text, True, color)
        alpha = int(255 * self.life)
        surf.set_alpha(alpha)
        surface.blit(surf, (self.x - surf.get_width() // 2, self.y))


# --- MAIN GAME CLASS ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.score_font = pygame.font.SysFont("Arial", 36, bold=True)

        save_manager = SaveManager(SAVE_FILE)
        self.sound_manager = SoundManager(save_manager.data["settings"]["volume"])
        self.save_manager = save_manager

        self.state = "START"
        self.score = 0
        self.high_score = save_manager.data["high_score"]
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
        self.score_popups = []

        self.enemy_direction = 1
        self.enemy_move_speed = 2
        self.enemy_drop_distance = 10
        self.last_enemy_move_time = 0

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

    def spawn_explosion(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def spawn_score_popup(self, x, y, score, combo=1):
        self.score_popups.append(ScorePopup(x, y, score, combo))

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
        self.score_popups = []
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
                        self.spawn_explosion(p.x, p.y, POWERUP_COLOR, 20)

            # Update Barriers
            for barrier in self.barriers:
                barrier.update()

            # COLLISIONS
            for b in self.player_bullets[:]:
                hit = False
                for enemy in self.enemies:
                    if enemy.active and b.rect.colliderect(enemy.rect):
                        enemy.health -= 1
                        b.active = False
                        if enemy.health <= 0:
                            enemy.active = False
                            base_score = enemy.score_value
                            self.score += base_score * max(1, self.player.combo)
                            self.player.combo = min(self.player.combo + 1, 10)
                            self.player.combo_timer = current_time
                            self.sound_manager.play_combo(self.player.combo)
                            self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color, 20)
                            self.sound_manager.play_explosion()
                            self.spawn_score_popup(enemy.x + enemy.width // 2, enemy.y, base_score, self.player.combo)
                            if random.random() < 0.1:
                                self.powerups.append(PowerUp(enemy.x, enemy.y))
                            self.save_manager.increment_kills(1)
                        else:
                            self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color, 8)
                            self.spawn_score_popup(enemy.x, enemy.y, enemy.score_value, 1)
                        hit = True
                        break

                if not hit:
                    for barrier in self.barriers:
                        if barrier.active and barrier.take_damage(b.rect):
                            b.active = False
                            self.spawn_explosion(b.x, b.y, BARRIER_COLOR, 8)
                            break
                    if not b.active:
                        for eb in self.enemy_bullets[:]:
                            if b.rect.colliderect(eb.rect):
                                b.active = False
                                eb.active = False
                                self.spawn_explosion(b.x, b.y, (255, 255, 255), 10)
                                break

            for b in self.enemy_bullets[:]:
                if b.rect.colliderect(self.player.rect):
                    b.active = False
                    if self.player.shield_active:
                        self.player.shield_active = False
                        self.spawn_explosion(self.player.x, self.player.y, (100, 255, 255), 15)
                    else:
                        self.player_hit()
                    break

            for b in self.enemy_bullets[:]:
                for barrier in self.barriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, 8)
                        break

            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color, 15)
                    enemy.active = False
                    break

            if self.ufo and self.ufo.active:
                for b in self.player_bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2, UFO_COLOR, 25)
                        self.sound_manager.play_explosion()
                        self.spawn_score_popup(self.ufo.x + self.ufo.width // 2, self.ufo.y, self.ufo.score_value, self.player.combo)
                        self.ufo.active = False
                        self.ufo = None
                        break

            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 1
                self.init_enemies()
                self.score += 1000
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), 30)
                self.sound_manager.play_level_complete()

            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            for popup in self.score_popups[:]:
                popup.update()
                if popup.life <= 0:
                    self.score_popups.remove(popup)

    def player_hit(self):
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color,
            30
        )
        self.sound_manager.play_explosion()
        self.player.lives -= 1
        self.player.combo = 0
        self.player.powerups = []
        self.player.shield_active = False
        self.save_manager.increment_game()

        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            new_high = self.save_manager.update_high_score(self.score)
            self.save_manager.update_max_combo(self.player.combo)
            if new_high:
                self.sound_manager.play_new_high_score()

    def draw(self):
        bg_surface = pygame.Surface((WIDTH, HEIGHT))
        bg_surface.fill(BG_COLOR)

        for star in self.stars:
            star.draw(bg_surface)

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
            for popup in self.score_popups:
                popup.draw(self.screen, self.score_font)

            self.draw_hud()
        elif self.state == "PAUSE":
            self.draw_menu("PAUSED", "Press P to Resume | ESC to Quit")
        elif self.state in ["GAMEOVER", "VICTORY"]:
            title = "GAME OVER" if self.state == "GAMEOVER" else "LEVEL COMPLETE!"
            color = (255, 50, 50) if self.state == "GAMEOVER" else (50, 255, 50)
            self.draw_menu(title, f"Score: {self.score}", f"High Score: {self.save_manager.data['high_score']}")

        pygame.display.flip()

    def draw_menu(self, title, sub1, sub2=""):
        title_surf = self.large_font.render(title, True, PLAYER_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(title_surf, title_rect)

        sub1_surf = self.font.render(sub1, True, TEXT_COLOR)
        sub1_rect = sub1_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.screen.blit(sub1_surf, title_rect)

        if sub2:
            sub2_surf = self.font.render(sub2, True, (200, 200, 200))
            sub2_rect = sub2_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            self.screen.blit(sub2_surf, sub2_rect)

    def draw_hud(self):
        score_surf = self.score_font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, TEXT_COLOR)
        level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
        combo_surf = self.score_font.render(f"COMBO: x{self.player.combo}", True, COMBO_COLOR)

        powerup_text = ""
        if POWERUP_RAPID in self.player.powerups: powerup_text += "R "
        if POWERUP_SPREAD in self.player.powerups: powerup_text += "S "
        if self.player.shield_active: powerup_text += "H "
        pu_surf = self.font.render(f"PU: {powerup_text or '-'}", True, POWERUP_COLOR)

        self.screen.blit(score_surf, (15, 10))
        self.screen.blit(lives_surf, (WIDTH - 160, 10))
        self.screen.blit(level_surf, (WIDTH // 2 - 60, 10))
        self.screen.blit(combo_surf, (15, 40))
        self.screen.blit(pu_surf, (WIDTH - 160, 40))

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


# --- SPRITES ---
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

SPRITE_PLAYER = create_pixel_art(16, 16, PLAYER_COLOR, PLAYER_MAP)
SPRITE_ENEMY_1 = create_pixel_art(20, 16, ENEMY_1_COLOR, ENEMY_1_MAP)
SPRITE_ENEMY_2 = create_pixel_art(20, 16, ENEMY_2_COLOR, ENEMY_2_MAP)
SPRITE_ENEMY_3 = create_pixel_art(20, 16, ENEMY_3_COLOR, ENEMY_3_MAP)
SPRITE_UFO = create_pixel_art(22, 14, UFO_COLOR, UFO_MAP)


if __name__ == "__main__":
    game = Game()
    game.run()
