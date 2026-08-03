# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.6-27B-heretic-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import math
import random
import struct
import wave
import io
import json
import os
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 9
INVADER_SPEED_START = 1.5
INVADER_DROP_DISTANCE = 25
BULLET_SIZE = 4
PLAYER_SIZE = 40
INVADER_SIZE = 32
BARREL_SIZE = 60
MAX_COMBO = 10
COMBO_DECAY_TIME = 120  # Frames

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 9, 9)
NEON_BLUE = (0, 247, 255)
NEON_PURPLE = (201, 9, 255)
NEON_YELLOW = (255, 253, 0)
DARK_BG = (10, 10, 15)
# FIX 1: Define YELLOW explicitly to avoid NameError
YELLOW = (255, 255, 0)

# --- Data Persistence ---
DATA_FILE = "game_data.json"


def load_data():
    default_data = {"high_score": 0, "unlocked_levels": 1, "volume": 0.5}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                loaded_data = json.load(f)
                # FIX 2: Merge loaded data with defaults to ensure all keys exist
                return {**default_data, **loaded_data}
        except:
            pass
    return default_data


def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass


# --- Audio System (Synthesized) ---
class SoundEngine:
    def __init__(self, volume=0.5):
        self.volume = volume
        self.sample_rate = 22050
        self.sounds = {}
        self._generate_sounds()
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1, buffer=512)

    def _generate_sounds(self):
        def create_tone(freq, duration, type='sine', vol=0.5, slide=0):
            t = 0
            samples = []
            while t < duration:
                current_freq = freq + (slide * t)
                if type == 'sine':
                    val = int(vol * 127 * math.sin(2 * math.pi * current_freq * t))
                elif type == 'square':
                    val = int(vol * 127 * (1 if math.sin(2 * math.pi * current_freq * t) > 0 else -1))
                elif type == 'noise':
                    val = int(vol * 127 * (random.random() * 2 - 1))
                else:
                    val = 0

                if t > duration * 0.8:
                    val = int(val * (1 - (t - duration * 0.8) / (duration * 0.2)))

                samples.append(val)
                t += 1.0 / self.sample_rate

            data = struct.pack('%dh' % len(samples), *samples)
            return data

        self.sounds['shoot'] = create_tone(800, 0.1, 'square', 0.3, -400)
        self.sounds['explosion'] = create_tone(100, 0.3, 'noise', 0.6)
        self.sounds['kill'] = create_tone(400, 0.15, 'square', 0.4, -200)
        self.sounds['mystery'] = create_tone(1200, 0.2, 'sine', 0.4, 400)
        self.sounds['powerup'] = create_tone(600, 0.4, 'sine', 0.5, 200)
        self.sounds['levelup'] = create_tone(500, 0.8, 'sine', 0.4, 300)
        self.sounds['gameover'] = create_tone(150, 1.5, 'square', 0.6, -100)
        self.sounds['hit'] = create_tone(200, 0.05, 'square', 0.3)

    def play(self, name, pitch_mod=1.0):
        if name not in self.sounds: return
        try:
            buffer = self.sounds[name]
            wav_file = io.BytesIO()
            w = wave.open(wav_file, 'w')
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self.sample_rate)
            w.writeframes(buffer)
            w.close()
            wav_file.seek(0)
            sound = pygame.mixer.Sound(wav_file)
            sound.set_volume(self.volume)
            sound.play()
        except:
            pass

    def set_volume(self, vol):
        self.volume = vol


# --- Visual Effects ---

class Particle:
    def __init__(self, x, y, color, speed=2, life=30):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * random.uniform(1, speed)
        self.vy = math.sin(angle) * random.uniform(1, speed)
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0.5, self.size * 0.95)

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


class Bullet:
    def __init__(self, x, y, direction, color, is_enemy=False):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, 12)
        self.direction = direction
        self.color = color
        self.active = True
        self.is_enemy = is_enemy
        self.trail = []

    def update(self, speed):
        self.rect.y += self.direction * speed
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 5:
            self.trail.pop(0)

        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        for i, pos in enumerate(self.trail):
            alpha = i / len(self.trail)
            size = max(1, int(BULLET_SIZE * alpha))
            color = tuple(int(c * alpha) for c in self.color)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), size)

        pygame.draw.rect(screen, self.color, self.rect)
        glow_rect = self.rect.inflate(6, 6)
        # FIX: Ensure color tuple is valid for outline
        if len(self.color) == 3:
            pygame.draw.rect(screen, (self.color[0], self.color[1], self.color[2]), glow_rect, 1)


class PowerUp:
    def __init__(self, x, y, p_type):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = p_type
        self.color = NEON_YELLOW if p_type == 'shield' else NEON_PURPLE if p_type == 'rapid' else NEON_BLUE
        self.active = True

    def update(self):
        self.rect.y += 2
        if self.rect.top > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx, self.rect.centery), 4)


# --- Game Entities ---

class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE // 2
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = PLAYER_SPEED
        self.color = NEON_GREEN
        self.bullets = []
        self.cooldown = 0
        self.lives = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.powerups = {'shield': 0, 'rapid': 0, 'triple': 0}
        self.shield_active = False

    def move(self, direction):
        if direction == 1 and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        elif direction == -1 and self.x > 0:
            self.x -= self.speed
        self.rect.x = self.x
        self.rect.y = self.y

    def shoot(self, sound_gen):
        if self.cooldown <= 0:
            speed_mod = 1.0
            if self.powerups['rapid'] > 0:
                speed_mod = 0.6

            if self.powerups['triple'] > 0:
                self.bullets.append(Bullet(self.rect.centerx, self.rect.top, -1, NEON_BLUE, False))
                self.bullets.append(Bullet(self.rect.left + 5, self.rect.top + 5, -1, NEON_BLUE, False))
                self.bullets.append(Bullet(self.rect.right - 5, self.rect.top + 5, -1, NEON_BLUE, False))
            else:
                self.bullets.append(Bullet(self.rect.centerx, self.rect.top, -1, NEON_GREEN, False))

            self.cooldown = 20 if speed_mod == 1.0 else 12
            sound_gen.play('shoot')

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        for key in self.powerups:
            if self.powerups[key] > 0:
                self.powerups[key] -= 1
                if key == 'shield' and self.powerups[key] == 0:
                    self.shield_active = False

        for b in self.bullets:
            b.update(BULLET_SPEED)
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self, screen):
        if self.shield_active:
            pygame.draw.circle(screen, NEON_YELLOW, (self.rect.centerx, self.rect.centery), 35, 2)
            pygame.draw.circle(screen, NEON_YELLOW, (self.rect.centerx, self.rect.centery), 30, 1)

        center_x = self.rect.centerx
        center_y = self.rect.centery

        points = [
            (center_x, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

        pygame.draw.rect(screen, WHITE, (center_x - 5, self.rect.top - 10, 10, 10))

        for b in self.bullets:
            b.draw(screen)


class Invader:
    def __init__(self, x, y, type_id, level):
        self.rect = pygame.Rect(x, y, INVADER_SIZE, INVADER_SIZE)
        self.type_id = type_id
        self.base_color = [NEON_RED, NEON_BLUE, NEON_PURPLE][type_id % 3]
        self.color = self.base_color
        self.alive = True
        self.level = level
        self.health = 1 + (level // 3)
        self.is_boss = (level % 5 == 0 and self.type_id == 0 and x == SCREEN_WIDTH // 2 - INVADER_SIZE // 2)

        if self.is_boss:
            self.health = 10
            self.rect.width = INVADER_SIZE * 2
            self.rect.height = int(INVADER_SIZE * 1.5)

        self.bob_timer = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.bob_timer += 0.1

    def draw(self, screen):
        if not self.alive: return

        dist = abs(self.rect.bottom - SCREEN_HEIGHT)
        intensity = min(1.0, dist / 200)
        r, g, b = self.base_color
        current_color = (r, int(g * intensity + 255 * (1 - intensity)), b)

        cx, cy = self.rect.centerx, self.rect.centery
        w, h = self.rect.width, self.rect.height
        bob_offset = math.sin(self.bob_timer) * 3

        if self.type_id == 0:
            points = [(cx, cy - h // 2 + bob_offset), (cx - w // 2, cy), (cx - w // 2, cy + h // 2),
                      (cx + w // 2, cy + h // 2), (cx + w // 2, cy)]
            pygame.draw.polygon(screen, current_color, points)
        elif self.type_id == 1:
            points = [(cx - w // 2, cy - h // 4), (cx + w // 2, cy - h // 4), (cx + w // 2, cy + h // 4),
                      (cx - w // 2, cy + h // 4)]
            pygame.draw.polygon(screen, current_color, points)
            pygame.draw.line(screen, current_color, (cx - w // 2, cy + h // 4), (cx - w // 2, cy + h // 2), 2)
            pygame.draw.line(screen, current_color, (cx + w // 2, cy + h // 4), (cx + w // 2, cy + h // 2), 2)
        else:
            points = [(cx - w // 3, cy - h // 2 + bob_offset), (cx + w // 3, cy - h // 2 + bob_offset),
                      (cx + w // 2, cy), (cx + w // 2, cy + h // 2), (cx - w // 2, cy + h // 2), (cx - w // 2, cy)]
            pygame.draw.polygon(screen, current_color, points)

        pygame.draw.polygon(screen, WHITE, points, 1)

        pygame.draw.circle(screen, BLACK, (int(cx - w / 4), int(cy - h / 6)), 2)
        pygame.draw.circle(screen, BLACK, (int(cx + w / 4), int(cy - h / 6)), 2)

        if self.is_boss:
            bar_w = self.rect.width
            bar_h = 4
            hp_ratio = self.health / 10
            pygame.draw.rect(screen, NEON_RED, (self.rect.x, self.rect.top - 10, bar_w, bar_h))
            pygame.draw.rect(screen, NEON_GREEN, (self.rect.x, self.rect.top - 10, bar_w * hp_ratio, bar_h))


class Barrier:
    def __init__(self, x, y):
        self.blocks = []
        self.width = BARREL_SIZE
        self.height = BARREL_SIZE // 2
        rows = 4
        cols = 6
        block_w = self.width // cols
        block_h = self.height // rows

        for r in range(rows):
            for c in range(cols):
                if (r == 0 and c == 0) or (r == 0 and c == cols - 1) or \
                        (r == rows - 1 and c == 0) or (r == rows - 1 and c == cols - 1):
                    continue
                bx = x + c * block_w
                by = y + r * block_h
                self.blocks.append(pygame.Rect(bx, by, block_w - 1, block_h - 1))

    def draw(self, screen):
        for block in self.blocks:
            color = (0, 200 + (len(self.blocks) % 55), 0)
            pygame.draw.rect(screen, color, block)
            pygame.draw.rect(screen, (0, 150, 0), block.inflate(-2, -2))

    def check_collision(self, rect):
        hit = False
        for block in self.blocks[:]:
            if rect.colliderect(block):
                self.blocks.remove(block)
                hit = True
                break
        return hit


# --- Main Game ---

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Space Invaders: Enhanced")
        self.clock = pygame.time.Clock()

        self.font = self._get_font('Consolas', 24)
        self.big_font = self._get_font('Consolas', 48)

        self.data = load_data()
        self.sound = SoundEngine(self.data['volume'])

        self.reset_game()
        self.running = True
        self.game_over = False
        self.paused = False
        self.flash_timer = 0

    def _get_font(self, name, size):
        try:
            return pygame.font.SysFont(name, size)
        except pygame.error:
            try:
                return pygame.font.SysFont('Arial', size)
            except pygame.error:
                return pygame.font.Font(None, size)

    def reset_game(self):
        self.player = Player()
        self.invaders = []
        self.enemy_bullets = []
        self.powerups = []
        self.particles = []
        self.level = 1
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.high_score = self.data['high_score']
        self.invader_direction = 1
        self.invader_step_timer = 0
        self.invader_step_delay = 60
        self.create_invaders()
        self.create_bunkers()
        self.flash_timer = 0

    def create_invaders(self):
        self.invaders = []
        rows = 5 + (self.level // 2)
        if rows > 8: rows = 8
        cols = 10
        start_x = 100
        start_y = 50
        gap = 10 + (self.level * 0.5)

        for r in range(rows):
            for c in range(cols):
                type_id = r
                x = start_x + c * (INVADER_SIZE + gap)
                y = start_y + r * (INVADER_SIZE + gap)
                self.invaders.append(Invader(x, y, type_id, self.level))

    def create_bunkers(self):
        self.bunkers = []
        positions = [100, 300, 500, 700]
        for x in positions:
            self.bunkers.append(Barrier(x, SCREEN_HEIGHT - 150))

    def trigger_flash(self):
        self.flash_timer = 5

    def update(self):
        if self.game_over or self.paused:
            return

        if self.flash_timer > 0:
            self.flash_timer -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT]:
            self.player.move(1)
        if keys[pygame.K_SPACE]:
            self.player.shoot(self.sound)
        if keys[pygame.K_p]:
            self.paused = not self.paused
            pygame.time.delay(100)

        if self.combo > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        self.player.update()

        move_down = False
        current_delay = max(5, 60 - (self.level * 3) - (len(self.invaders) // 2))

        self.invader_step_timer += 1
        if self.invader_step_timer >= current_delay:
            self.invader_step_timer = 0

            hit_edge = False
            for inv in self.invaders:
                if not inv.alive: continue
                if (inv.rect.right >= SCREEN_WIDTH - 10 and self.invader_direction == 1) or \
                        (inv.rect.left <= 10 and self.invader_direction == -1):
                    hit_edge = True
                    break

            if hit_edge:
                self.invader_direction *= -1
                move_down = True
            else:
                for inv in self.invaders:
                    inv.move(self.invader_direction * (1 + self.level * 0.2), 0)

            if move_down:
                for inv in self.invaders:
                    inv.move(0, INVADER_DROP_DISTANCE)
                    if inv.rect.bottom >= self.player.rect.bottom:
                        self.trigger_game_over()

        if random.random() < 0.01 + (self.level * 0.005):
            shooters = [inv for inv in self.invaders if inv.alive]
            if shooters:
                shooter = random.choice(shooters)
                self.enemy_bullets.append(Bullet(shooter.rect.centerx, shooter.rect.bottom, 1, NEON_RED, True))

        for b in self.enemy_bullets[:]:
            b.update(BULLET_SPEED * 0.8)

            if b.rect.colliderect(self.player.rect):
                if self.player.shield_active:
                    b.active = False
                    self.sound.play('hit')
                else:
                    b.active = False
                    self.trigger_flash()
                    self.sound.play('explosion')
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.trigger_game_over()
                    else:
                        self.enemy_bullets.clear()
                        self.player.bullets.clear()
                        self.player.rect.x = SCREEN_WIDTH // 2 - self.player.width // 2
                        break

            for bunker in self.bunkers:
                if bunker.check_collision(b.rect):
                    b.active = False
                    self.trigger_flash()
                    break

        for b in self.player.bullets[:]:
            hit_inv = False
            for inv in self.invaders:
                if inv.alive and b.rect.colliderect(inv.rect):
                    inv.health -= 1
                    b.active = False
                    if inv.health <= 0:
                        inv.alive = False
                        self.trigger_flash()
                        self.sound.play('kill')
                        self.create_explosion(inv.rect.centerx, inv.rect.centery, inv.base_color)

                        self.combo += 1
                        if self.combo_timer <= 0:
                            self.combo_timer = COMBO_DECAY_TIME

                        score_mult = 1 + (self.combo * 0.1)
                        points = int(10 * (inv.type_id + 1) * score_mult)
                        self.score += points

                        if random.random() < 0.05:
                            p_type = random.choice(['shield', 'rapid', 'triple'])
                            self.powerups.append(PowerUp(inv.rect.centerx, inv.rect.centery, p_type))

                    hit_inv = True
                    break

            if not hit_inv:
                for bunker in self.bunkers:
                    if bunker.check_collision(b.rect):
                        b.active = False
                        self.trigger_flash()
                        break

        for p in self.powerups[:]:
            p.update()
            if p.rect.colliderect(self.player.rect):
                p.active = False
                self.sound.play('powerup')
                self.trigger_flash()
                if p.type == 'shield':
                    self.player.shield_active = True
                    self.player.powerups['shield'] = 600
                else:
                    self.player.powerups[p.type] = 600

            if not p.active:
                self.powerups.remove(p)

        self.enemy_bullets = [b for b in self.enemy_bullets if b.active]
        self.player.bullets = [b for b in self.player.bullets if b.active]

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        if len([i for i in self.invaders if i.alive]) == 0:
            self.level += 1
            self.sound.play('levelup')
            self.create_invaders()
            self.bunkers.clear()
            self.create_bunkers()
            self.invader_step_delay = max(10, 60 - self.level * 5)
            self.trigger_flash()

    def create_explosion(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def trigger_game_over(self):
        self.game_over = True
        self.sound.play('gameover')
        if self.score > self.high_score:
            self.high_score = self.score
            self.data['high_score'] = self.score
            save_data(self.data)

    def draw(self):
        self.screen.fill(DARK_BG)

        for _ in range(30):
            sx = random.randint(0, SCREEN_WIDTH)
            sy = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, (50, 50, 60), (sx, sy), 1)

        self.player.draw(self.screen)
        for inv in self.invaders:
            inv.draw(self.screen)
        for b in self.enemy_bullets:
            b.draw(self.screen)
        for bunker in self.bunkers:
            bunker.draw(self.screen)
        for p in self.powerups:
            p.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, NEON_GREEN)
        # FIX 1: Use defined YELLOW constant
        high_score_text = self.font.render(f"High: {self.high_score}", True, YELLOW)

        combo_color = NEON_YELLOW if self.combo > 0 else WHITE
        combo_text = self.font.render(f"Combo: x{self.combo}", True, combo_color)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        self.screen.blit(high_score_text, (10, 40))
        self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - 40, 40))

        if self.flash_timer > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.set_alpha(100 * (self.flash_timer / 5))
            flash_surf.fill(WHITE)
            self.screen.blit(flash_surf, (0, 0))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            go_text = self.big_font.render("GAME OVER", True, NEON_RED)
            final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, NEON_BLUE)

            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            pause_text = self.big_font.render("PAUSED", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))

        for i in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0), (0, i), (SCREEN_WIDTH, i), 1)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                    self.game_over = False
                if event.key == pygame.K_m:
                    current_vol = self.data['volume']
                    new_vol = 0.0 if current_vol > 0 else 0.5
                    self.data['volume'] = new_vol
                    self.sound.set_volume(new_vol)
                    save_data(self.data)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
