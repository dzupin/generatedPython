# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/Qwen3.6-27B-uncensored-heretic-v2-Native-MTP-Preserved-NVFP4-MLP-Only-Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import sys
import math
import random
import struct
import wave
import io
import json
import os

# ================= CONFIGURATION =================
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
FONT_PATH = pygame.font.match_font("consolas")
STATS_FILE = "space_invaders_stats.json"


# ================= SOUND GENERATION =================
def generate_sound(freq, duration, wave_type='sine', volume=128):
    """Generate a simple WAV sound programmatically and return a pygame Sound object."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'square':
                value = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            elif wave_type == 'saw':
                value = 2 * (t * freq - math.floor(t * freq + 0.5))
            else:
                value = random.uniform(-1, 1)
            # Attack/Decay envelope
            env = 1.0 - (i / num_samples)
            value *= volume * env
            # Clamp to 16-bit signed integer
            sample = max(-32767, min(32767, int(value * 32767)))
            wav_file.writeframes(struct.pack('<h', sample))
    buf.seek(0)
    return pygame.mixer.Sound(buf)


# ================= GAME OBJECTS =================
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.2, 1.5)
        self.size = random.randint(1, 2)
        self.alpha = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, (self.alpha, self.alpha, self.alpha), (int(self.x), int(self.y)), self.size)


class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 60
        self.width, self.height = 40, 20
        self.speed = 6
        self.shoot_cooldown = 0
        self.rapid_fire = False
        self.multi_shot = False

    def draw(self, surface):
        # Ship body
        points = [(self.x, self.y - 10), (self.x - 18, self.y + 10), (self.x + 18, self.y + 10)]
        pygame.draw.polygon(surface, (0, 255, 255), points)
        # Cockpit
        pygame.draw.ellipse(surface, (200, 255, 255), (self.x - 6, self.y - 4, 12, 8))
        # Engine glow
        glow_size = 4 + random.randint(0, 3)
        pygame.draw.circle(surface, (255, 140, 0), (self.x, self.y + 12), glow_size)
        pygame.draw.circle(surface, (255, 255, 100), (self.x, self.y + 12), glow_size // 2)


class Enemy:
    def __init__(self, x, y, row):
        self.x, self.y = x, y
        self.row = row
        self.width, self.height = 30, 20
        self.alive = True
        self.shoot_timer = random.randint(60, 180)

    def draw(self, surface):
        if not self.alive: return
        colors = [(204, 204, 0), (0, 255, 0), (0, 128, 255)]
        color = colors[self.row % 3]
        # Body
        pygame.draw.rect(surface, color, (self.x - 15, self.y - 10, 30, 20))
        # Eyes
        for offset in (-8, 8):
            pygame.draw.circle(surface, (255, 255, 255), (self.x + offset, self.y - 5), 4)
            pygame.draw.circle(surface, (0, 0, 0), (self.x + offset + 1, self.y - 6), 2)
        # Antennae
        pygame.draw.line(surface, color, (self.x - 10, self.y - 10), (self.x - 15, self.y - 18), 2)
        pygame.draw.line(surface, color, (self.x + 10, self.y - 10), (self.x + 15, self.y - 18), 2)


class Bullet:
    def __init__(self, x, y, dy, is_enemy=False):
        self.x, self.y = x, y
        self.dy = dy
        self.width, self.height = 4, 12
        self.is_enemy = is_enemy
        self.alive = True

    def draw(self, surface):
        if not self.alive: return
        color = (255, 50, 50) if self.is_enemy else (0, 255, 255)
        pygame.draw.rect(surface, color, (self.x - 2, self.y - 6, 4, 12))
        # Glow trail
        pygame.draw.rect(surface, (255, 255, 255), (self.x - 1, self.y - 5, 2, 10), 1)


class Barrier:
    def __init__(self, x, y):
        self.base_x, self.base_y = x, y
        self.blocks = []
        self.recreate()

    def recreate(self):
        self.blocks = []
        for row in range(5):
            for col in range(10):
                self.blocks.append({'x': self.base_x + col * 8, 'y': self.base_y + row * 8, 'hp': 3})

    def draw(self, surface):
        for b in self.blocks:
            if b['hp'] > 0:
                # Color shifts based on damage
                alpha = int(b['hp'] * 85)
                r, g = 0, alpha
                pygame.draw.rect(surface, (r, g, 120), (b['x'], b['y'], 8, 8))
                pygame.draw.rect(surface, (0, 255, 200), (b['x'], b['y'], 8, 8), 1)


class PowerUp:
    TYPES = ['RAPID', 'MULTI', 'SHIELD', 'LIFE']
    COLORS = {'RAPID': (255, 100, 0), 'MULTI': (255, 0, 255), 'SHIELD': (0, 255, 100), 'LIFE': (255, 50, 50)}

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice(self.TYPES)
        self.speed = 2.5
        self.width, self.height = 24, 24
        self.alive = True
        self.bob_timer = 0

    def update(self):
        self.y += self.speed
        self.bob_timer += 0.1
        if self.y > SCREEN_HEIGHT + 30:
            self.alive = False

    def draw(self, surface):
        if not self.alive: return
        color = self.COLORS[self.type]
        offset_y = math.sin(self.bob_timer) * 3
        pygame.draw.rect(surface, color, (self.x - 12, self.y - 12 + offset_y, 24, 24), border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), (self.x - 12, self.y - 12 + offset_y, 24, 24), 2, border_radius=4)
        # Icon
        icon = self.type[0]
        text = pygame.font.SysFont(None, 20).render(icon, True, (255, 255, 255))
        surface.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2 + offset_y))


# ================= MAIN GAME CLASS =================
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Pure Python")
        self.clock = pygame.time.Clock()

        self.state = 'MENU'  # MENU, PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE
        self.score = 0
        self.level = 1
        self.lives = 3
        self.high_score = self.load_stats()['high_score']

        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.barriers = []
        self.powerups = []
        self.stars = [Star() for _ in range(120)]

        self.enemy_dir = 1
        self.enemy_move_timer = 0
        self.enemy_shoot_timer = 0
        self.rapid_timer = 0
        self.multi_timer = 0

        self.sounds = {
            'shoot': generate_sound(880, 0.1, 'sine'),
            'explosion': generate_sound(120, 0.3, 'saw'),
            'enemy_hit': generate_sound(600, 0.1, 'square'),
            'powerup': generate_sound(1000, 0.25, 'sine'),
            'level_up': generate_sound(400, 0.5, 'sine'),
            'game_over': generate_sound(200, 0.8, 'square')
        }

        self.font_small = pygame.font.SysFont(None, 24)
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_huge = pygame.font.SysFont(None, 64)

        self.init_level()

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {'high_score': 0, 'total_games': 0, 'max_level': 1}

    def save_stats(self):
        stats = self.load_stats()
        stats['high_score'] = max(stats['high_score'], self.score)
        stats['total_games'] = stats.get('total_games', 0) + 1
        stats['max_level'] = max(stats.get('max_level', 1), self.level)
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f)

    def init_level(self):
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.barriers = []
        self.enemy_dir = 1
        self.enemy_move_timer = 0
        self.enemy_shoot_timer = 0
        self.rapid_timer = 0
        self.multi_timer = 0

        # Create barriers
        for i in range(4):
            self.barriers.append(Barrier(150 + i * 150, SCREEN_HEIGHT - 100))

        # Create enemies
        rows = 5
        cols = 11
        for r in range(rows):
            for c in range(cols):
                self.enemies.append(Enemy(60 + c * 55, 60 + r * 45, r))

        # Reset player
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT - 60
        self.player.shoot_cooldown = 0
        self.player.rapid_fire = False
        self.player.multi_shot = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.state == 'MENU':
                        self.state = 'PLAYING'
                        self.score = 0
                        self.lives = 3
                        self.level = 1
                        self.init_level()
                    elif self.state == 'GAME_OVER':
                        self.state = 'MENU'
                    elif self.state == 'LEVEL_COMPLETE':
                        self.level += 1
                        self.state = 'PLAYING'
                        self.init_level()
                if event.key == pygame.K_p:
                    if self.state == 'PLAYING':
                        self.state = 'PAUSED'
                    elif self.state == 'PAUSED':
                        self.state = 'PLAYING'
            if event.type == pygame.MOUSEBUTTONDOWN and self.state == 'MENU':
                self.state = 'PLAYING'
                self.score = 0
                self.lives = 3
                self.level = 1
                self.init_level()

    def update(self):
        if self.state != 'PLAYING': return

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player.x -= self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.x += self.player.speed
        self.player.x = max(20, min(SCREEN_WIDTH - 20, self.player.x))

        # Shooting
        self.player.shoot_cooldown -= 1
        shoot_delay = 8 if self.player.rapid_fire else 18
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.player.shoot_cooldown <= 0:
            self.player.shoot_cooldown = shoot_delay
            self.sounds['shoot'].play()
            if self.player.multi_shot:
                self.bullets.append(Bullet(self.player.x, self.player.y, -8, False))
                self.bullets.append(Bullet(self.player.x - 12, self.player.y + 5, -8, False))
                self.bullets.append(Bullet(self.player.x + 12, self.player.y + 5, -8, False))
            else:
                self.bullets.append(Bullet(self.player.x, self.player.y, -8, False))

        # Update bullets
        for b in self.bullets[:]:
            b.y += b.dy
            if b.y < -20 or b.y > SCREEN_HEIGHT + 20:
                b.alive = False
                self.bullets.remove(b)
                continue

            # Bullet vs Barrier
            for barrier in self.barriers:
                for blk in barrier.blocks[:]:
                    if abs(b.x - blk['x']) < 8 and abs(b.y - blk['y']) < 8:
                        blk['hp'] -= 1
                        if blk['hp'] <= 0:
                            barrier.blocks.remove(blk)
                        b.alive = False
                        self.bullets.remove(b)
                        break
                if not b.alive: break

            # Bullet vs Enemy
            if b.alive and not b.is_enemy:
                for e in self.enemies:
                    if e.alive and abs(b.x - e.x) < e.width / 2 + 4 and abs(b.y - e.y) < e.height / 2 + 4:
                        e.alive = False
                        b.alive = False
                        self.score += 10 * (e.row + 1)
                        self.sounds['enemy_hit'].play()
                        # Drop powerup chance
                        if random.random() < 0.12:
                            self.powerups.append(PowerUp(e.x, e.y))
                        self.bullets.remove(b)
                        break

            # Bullet vs Player
            if b.alive and b.is_enemy:
                if abs(b.x - self.player.x) < self.player.width / 2 and abs(
                        b.y - self.player.y) < self.player.height / 2:
                    self.lives -= 1
                    b.alive = False
                    self.sounds['explosion'].play()
                    self.bullets.remove(b)
                    if self.lives <= 0:
                        self.state = 'GAME_OVER'
                        self.sounds['game_over'].play()
                        self.save_stats()
                    break

        # Enemy movement
        self.enemy_move_timer += 1
        move_speed = max(4, 18 - self.level * 2)
        if self.enemy_move_timer >= move_speed:
            self.enemy_move_timer = 0
            rightmost = max((e.x for e in self.enemies if e.alive), default=0)
            leftmost = min((e.x for e in self.enemies if e.alive), default=0)

            if self.enemy_dir == 1 and rightmost >= SCREEN_WIDTH - 30:
                self.enemy_dir = -1
                for e in self.enemies:
                    if e.alive: e.y += 15
            elif self.enemy_dir == -1 and leftmost <= 30:
                self.enemy_dir = 1
                for e in self.enemies:
                    if e.alive: e.y += 15
            else:
                for e in self.enemies:
                    if e.alive: e.x += self.enemy_dir * 12

            # Check if enemies reached player
            for e in self.enemies:
                if e.alive and e.y >= self.player.y - 10:
                    self.lives = 0
                    self.state = 'GAME_OVER'
                    self.sounds['game_over'].play()
                    self.save_stats()

        # Enemy shooting
        self.enemy_shoot_timer += 1
        shoot_interval = max(25, 70 - self.level * 6)
        if self.enemy_shoot_timer >= shoot_interval:
            self.enemy_shoot_timer = 0
            alive_enemies = [e for e in self.enemies if e.alive]
            if alive_enemies and len([b for b in self.bullets if b.is_enemy]) < 6:
                shooter = random.choice(alive_enemies)
                self.bullets.append(Bullet(shooter.x, shooter.y, 5, True))

        # Update powerups
        for p in self.powerups[:]:
            p.update()
            if not p.alive:
                self.powerups.remove(p)
                continue
            if abs(p.x - self.player.x) < 24 and abs(p.y - self.player.y) < 24:
                p.alive = False
                self.powerups.remove(p)
                self.sounds['powerup'].play()
                self.score += 50
                if p.type == 'RAPID':
                    self.player.rapid_fire = True
                    self.rapid_timer = 400
                elif p.type == 'MULTI':
                    self.player.multi_shot = True
                    self.multi_timer = 400
                elif p.type == 'SHIELD':
                    for b in self.barriers:
                        b.recreate()
                elif p.type == 'LIFE':
                    self.lives += 1

        # Timers
        if self.rapid_timer > 0:
            self.rapid_timer -= 1
            if self.rapid_timer == 0: self.player.rapid_fire = False
        if self.multi_timer > 0:
            self.multi_timer -= 1
            if self.multi_timer == 0: self.player.multi_shot = False

        # Check level complete
        if all(not e.alive for e in self.enemies):
            self.state = 'LEVEL_COMPLETE'
            self.sounds['level_up'].play()
            self.save_stats()

        # Update stars
        for s in self.stars: s.update()

    def draw(self):
        self.screen.fill((5, 8, 20))
        for s in self.stars: s.draw(self.screen)

        if self.state in ('PLAYING', 'PAUSED'):
            for b in self.barriers: b.draw(self.screen)
            for p in self.powerups: p.draw(self.screen)
            for e in self.enemies: e.draw(self.screen)
            self.player.draw(self.screen)
            for b in self.bullets: b.draw(self.screen)

            # HUD
            score_text = self.font_small.render(f"SCORE: {self.score}", True, (255, 255, 255))
            lives_text = self.font_small.render(f"LIVES: {self.lives}", True, (255, 255, 255))
            level_text = self.font_small.render(f"LEVEL: {self.level}", True, (255, 255, 255))
            self.screen.blit(score_text, (15, 15))
            self.screen.blit(lives_text, (SCREEN_WIDTH - 140, 15))
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 15))

            if self.player.rapid_fire:
                t = self.font_small.render(f"RAPID: {self.rapid_timer // 60}s", True, (255, 100, 0))
                self.screen.blit(t, (15, 45))
            if self.player.multi_shot:
                t = self.font_small.render(f"MULTI: {self.multi_timer // 60}s", True, (255, 0, 255))
                self.screen.blit(t, (15, 70))

            if self.state == 'PAUSED':
                pause_text = self.font_large.render("PAUSED", True, (255, 255, 255))
                self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                resume_text = self.font_small.render("Press P to resume", True, (200, 200, 200))
                self.screen.blit(resume_text,
                                 (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        elif self.state == 'MENU':
            title = self.font_huge.render("SPACE INVADERS", True, (0, 255, 255))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
            start = self.font_small.render("PRESS SPACE or CLICK TO START", True, (255, 255, 255))
            self.screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 300))
            controls = self.font_small.render("ARROWS/WASD: Move | SPACE/W: Shoot | P: Pause", True, (150, 150, 150))
            self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 350))
            high = self.font_small.render(f"HIGH SCORE: {self.high_score}", True, (255, 215, 0))
            self.screen.blit(high, (SCREEN_WIDTH // 2 - high.get_width() // 2, 400))

        elif self.state == 'GAME_OVER':
            title = self.font_huge.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
            score = self.font_large.render(f"FINAL SCORE: {self.score}", True, (255, 255, 255))
            self.screen.blit(score, (SCREEN_WIDTH // 2 - score.get_width() // 2, 280))
            press = self.font_small.render("PRESS SPACE TO CONTINUE", True, (200, 200, 200))
            self.screen.blit(press, (SCREEN_WIDTH // 2 - press.get_width() // 2, 350))

        elif self.state == 'LEVEL_COMPLETE':
            title = self.font_huge.render(f"LEVEL {self.level} CLEAR!", True, (0, 255, 0))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
            score = self.font_large.render(f"SCORE: {self.score}", True, (255, 255, 255))
            self.screen.blit(score, (SCREEN_WIDTH // 2 - score.get_width() // 2, 280))
            press = self.font_small.render("PRESS SPACE FOR NEXT LEVEL", True, (200, 200, 200))
            self.screen.blit(press, (SCREEN_WIDTH // 2 - press.get_width() // 2, 350))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit()
