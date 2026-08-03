# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/GRM-Qwen2.6-27B-Opus-Heretic-Abliterated-MTP.i1-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

import pygame
import math
import array
import json
import os
import random
from enum import Enum

# ================= CONFIGURATION =================
WIDTH, HEIGHT = 800, 600
FPS = 60
STATS_FILE = "space_invaders_stats.json"


# ================= SOUND GENERATOR =================
def make_sound(freq, duration, wave_type='sine', vol=0.3):
    """Procedurally generate a short sound effect."""
    sample_rate = 22050
    length = int(sample_rate * duration)
    samples = array.array('h')
    for i in range(length):
        t = i / sample_rate
        # Envelope: quick attack, slow decay
        env = 1.0 if i < length * 0.05 else max(0, 1.0 - (i - length * 0.05) / (length * 0.95))
        if wave_type == 'sine':
            val = math.sin(2 * math.pi * freq * t)
        elif wave_type == 'square':
            val = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
        elif wave_type == 'saw':
            val = 2 * (t * freq % 1) - 1
        else:
            val = 0
        samples.append(int(val * env * 16000 * vol))
    return pygame.mixer.Sound(buffer=samples.tobytes())


# ================= GAME OBJECTS =================
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0: return
        alpha = self.life / self.max_life
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size * alpha))


class Bullet:
    def __init__(self, x, y, dy, is_player):
        self.x, self.y = x, y
        self.dy = dy
        self.w, self.h = 4, 10
        self.is_player = is_player
        self.color = (255, 255, 100) if is_player else (255, 50, 50)
        self.alive = True

    def update(self):
        self.y += self.dy
        if self.y < 0 or self.y > HEIGHT: self.alive = False

    def draw(self, surf):
        if self.alive: pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Barrier:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.bsize = 6
        self.cols, self.rows = 12, 6
        self.blocks = [[True] * self.cols for _ in range(self.rows)]
        self.color = (0, 180, 255)

    def draw(self, surf):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.blocks[r][c]:
                    pygame.draw.rect(surf, self.color,
                                     (self.x + c * self.bsize, self.y + r * self.bsize, self.bsize, self.bsize))

    def check_hit(self, rect):
        hit = False
        for r in range(self.rows):
            for c in range(self.cols):
                if self.blocks[r][c]:
                    block = pygame.Rect(self.x + c * self.bsize, self.y + r * self.bsize, self.bsize, self.bsize)
                    if rect.colliderect(block):
                        self.blocks[r][c] = False
                        hit = True
        return hit


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 40, 20
        self.speed = 6
        self.cooldown = 0
        self.max_cd = 15
        self.powerups = {}  # key: type, value: frames remaining
        self.color = (0, 255, 100)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.x = max(10, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x = min(WIDTH - 10 - self.w, self.x + self.speed)
        if self.cooldown > 0: self.cooldown -= 1
        # Clean expired powerups
        self.powerups = {k: v - 1 for k, v in self.powerups.items() if v > 0}

    def draw(self, surf):
        # Ship body
        pts = [(self.x + self.w / 2, self.y), (self.x, self.y + self.h),
               (self.x + self.w, self.y + self.h), (self.x + self.w - 6, self.y + self.h - 6),
               (self.x + 6, self.y + self.h - 6)]
        pygame.draw.polygon(surf, self.color, pts)
        # Engine glow
        if random.random() > 0.4:
            pygame.draw.circle(surf, (255, 120, 0), (self.x + self.w // 2, self.y + self.h + 3), 4)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def shoot(self):
        cd = self.max_cd // 2 if 'rapid_fire' in self.powerups else self.max_cd
        if self.cooldown <= 0:
            self.cooldown = cd
            return True
        return False


class Enemy:
    def __init__(self, x, y, row, level):
        self.x, self.y = x, y
        self.w, self.h = 30, 20
        self.row = row
        self.level = level
        self.points = 10 + row * 5
        self.alive = True
        # Color based on row type
        self.color = [(255, 100, 100), (255, 200, 50), (100, 200, 255)][row % 3]

    def draw(self, surf):
        if not self.alive: return
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h), border_radius=4)
        # Eyes
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 8, self.y + 8), 3)
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 22, self.y + 8), 3)
        pygame.draw.circle(surf, (0, 0, 0), (self.x + 8, self.y + 8), 1)
        pygame.draw.circle(surf, (0, 0, 0), (self.x + 22, self.y + 8), 1)

    def get_rect(self): return pygame.Rect(self.x, self.y, self.w, self.h)


class PowerUp:
    def __init__(self, x, y, level):
        self.x, self.y = x, y
        self.w, self.h = 16, 16
        self.dy = 1.5 + level * 0.1
        self.alive = True
        self.types = ['rapid_fire', 'shield_restore', 'score_x2', 'life']
        self.type = random.choice(self.types)
        self.color = {'rapid_fire': (255, 255, 0), 'shield_restore': (0, 200, 255),
                      'score_x2': (255, 100, 255), 'life': (255, 0, 0)}[self.type]
        self.sym = {'rapid_fire': 'F', 'shield_restore': 'S', 'score_x2': 'x2', 'life': '+'}[self.type]

    def update(self):
        self.y += self.dy
        if self.y > HEIGHT: self.alive = False

    def draw(self, surf):
        if not self.alive: return
        pygame.draw.circle(surf, self.color, (self.x + self.w // 2, self.y + self.h // 2), self.w // 2)
        font = pygame.font.SysFont(None, 14)
        txt = font.render(self.sym, True, (255, 255, 255))
        surf.blit(txt, (self.x + self.w // 2 - txt.get_width() // 2, self.y + self.h // 2 - txt.get_height() // 2))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


# ================= MAIN GAME CLASS =================
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(22050, -16, 1, 512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('freesansbold', 24)
        self.big_font = pygame.font.SysFont('freesansbold', 48)

        # Sounds
        self.snd_shoot = make_sound(880, 0.08, 'square', 0.3)
        self.snd_explode = make_sound(120, 0.2, 'saw', 0.4)
        self.snd_powerup = make_sound(1400, 0.12, 'sine', 0.3)
        self.snd_levelup = make_sound(440, 0.25, 'sine', 0.4)
        self.snd_gameover = make_sound(220, 0.5, 'saw', 0.5)

        # State
        self.state = 'MENU'
        self.score = 0
        self.lives = 3
        self.level = 1
        self.multiplier = 1
        self.star_offset = 0
        self.level_transition = 0
        self.screen_flash = 0

        # Entities
        self.player = None
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.particles = []
        self.powerups = []
        self.barriers = []

        # Enemy movement
        self.enemy_dx = 1
        self.enemy_move_timer = 0
        self.enemy_fire_rate = 30
        self.starfield = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(120)]

        # Stats
        self.stats = self.load_stats()
        self.high_score = self.stats.get('high_score', 0)

        self.reset_game()

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                try:
                    return json.load(f)
                except:
                    pass
        return {'high_score': 0, 'games_played': 0, 'max_level': 1}

    def save_stats(self):
        self.stats['games_played'] = self.stats.get('games_played', 0) + 1
        if self.score > self.stats.get('high_score', 0): self.stats['high_score'] = self.score
        if self.level > self.stats.get('max_level', 1): self.stats['max_level'] = self.level
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.multiplier = 1
        self.state = 'MENU'
        self.start_level()

    def start_level(self):
        self.player = Player(WIDTH // 2 - 20, HEIGHT - 50)
        self.bullets = self.enemy_bullets = self.particles = self.powerups = []
        self.barriers = [Barrier(150, HEIGHT - 120), Barrier(350, HEIGHT - 120), Barrier(550, HEIGHT - 120)]
        self.enemies = []
        rows = min(4 + self.level, 6)
        cols = 8
        for r in range(rows):
            for c in range(cols):
                self.enemies.append(Enemy(100 + c * 50, 60 + r * 40, r, self.level))
        self.enemy_dx = 0.5 + self.level * 0.1
        self.enemy_move_timer = 0
        self.enemy_fire_rate = max(15, 35 - self.level * 3)

    def create_explosion(self, x, y, color, count=10):
        for _ in range(count): self.particles.append(Particle(x, y, color))

    def apply_powerup(self, ptype):
        if ptype == 'rapid_fire':
            self.player.powerups['rapid_fire'] = 300
        elif ptype == 'shield_restore':
            for b in self.barriers: b.blocks = [[True] * b.cols for _ in range(b.rows)]
        elif ptype == 'score_x2':
            self.player.powerups['score_x2'] = 400
        elif ptype == 'life':
            self.lives = min(self.lives + 1, 5)
        self.screen_flash = 10

    def update_enemies(self):
        self.enemy_move_timer += 1
        alive = [e for e in self.enemies if e.alive]
        if not alive: return

        # Dynamic speed: faster as they die
        interval = max(5, 40 - self.level * 4 - max(0, (32 - len(alive))))
        if self.enemy_move_timer >= interval:
            self.enemy_move_timer = 0
            hit_edge = False
            for e in alive:
                if (self.enemy_dx > 0 and e.x + e.w >= WIDTH - 10) or \
                        (self.enemy_dx < 0 and e.x <= 10):
                    hit_edge = True
                    break
            if hit_edge:
                self.enemy_dx *= -1
                for e in alive: e.y += 12
                # Check invasion
                for e in alive:
                    if e.y + e.h >= self.player.y:
                        self.lives = 0
                        self.state = 'GAME_OVER'
                        self.snd_gameover.play()
                        return
            else:
                for e in alive: e.x += self.enemy_dx

    def check_collisions(self):
        # Player bullets
        for b in self.bullets[:]:
            if not b.alive: continue
            for e in self.enemies:
                if e.alive and b.get_rect().colliderect(e.get_rect()):
                    e.alive = False
                    b.alive = False
                    self.score += e.points * self.multiplier
                    self.create_explosion(e.x + e.w / 2, e.y + e.h / 2, e.color)
                    self.snd_explode.play()
                    if random.random() < 0.12: self.powerups.append(PowerUp(e.x, e.y, self.level))
                    break
            if b.alive:
                for bar in self.barriers:
                    if bar.check_hit(b.get_rect()):
                        b.alive = False
                        self.create_explosion(b.x, b.y, bar.color, 5)
                        break

        # Enemy bullets
        for b in self.enemy_bullets[:]:
            if not b.alive: continue
            if b.get_rect().colliderect(self.player.get_rect()):
                b.alive = False
                self.lives -= 1
                self.create_explosion(self.player.x + self.player.w / 2, self.player.y + self.player.h / 2, (0, 255, 0))
                self.snd_explode.play()
                self.screen_flash = 8
                if self.lives <= 0:
                    self.state = 'GAME_OVER'
                    self.snd_gameover.play()
            if b.alive:
                for bar in self.barriers:
                    if bar.check_hit(b.get_rect()):
                        b.alive = False
                        self.create_explosion(b.x, b.y, bar.color, 5)
                        break

        # Player vs Powerups
        for p in self.powerups[:]:
            if p.alive and self.player.get_rect().colliderect(p.get_rect()):
                p.alive = False
                self.apply_powerup(p.type)
                self.snd_powerup.play()

        # Cleanup
        self.bullets = [b for b in self.bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]
        self.powerups = [p for p in self.powerups if p.alive]
        self.particles = [p for p in self.particles if p.life > 0]
        self.enemies = [e for e in self.enemies if e.alive]

        # Level complete?
        if not self.enemies and self.state == 'PLAYING':
            self.level += 1
            self.snd_levelup.play()
            self.start_level()
            self.level_transition = 90

    def draw_ui(self, surf):
        surf.blit(self.font.render(f"Score: {self.score}", True, (255, 255, 255)), (10, 10))
        surf.blit(self.font.render(f"Lives: {self.lives}", True, (255, 255, 255)), (10, 35))
        surf.blit(self.font.render(f"Level: {self.level}", True, (255, 255, 255)), (WIDTH - 140, 10))
        if self.multiplier > 1:
            surf.blit(self.font.render(f"Mult: x{self.multiplier}", True, (255, 200, 0)), (WIDTH - 140, 35))
        y_off = 60
        for k, v in self.player.powerups.items():
            if v > 0:
                surf.blit(self.font.render(f"{k}: {v / 60:.1f}s", True, (150, 255, 150)), (10, y_off))
                y_off += 20

    def draw_menu(self, surf):
        surf.fill((5, 5, 15))
        for sx, sy in self.starfield:
            pygame.draw.circle(surf, (80, 80, 120), (sx, (sy + self.star_offset) % HEIGHT), 1)
        title = self.big_font.render("SPACE INVADERS", True, (0, 255, 100))
        sub = self.font.render("Press ENTER to Start", True, (255, 255, 255))
        stats = self.font.render(f"High Score: {self.stats['high_score']} | Max Level: {self.stats['max_level']}", True,
                                 (180, 180, 255))
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2))
        surf.blit(stats, (WIDTH // 2 - stats.get_width() // 2, HEIGHT // 2 + 40))
        for i in range(3):
            e = Enemy(WIDTH // 2 - 45 + i * 45, HEIGHT // 2 + 100, i % 3, 1)
            e.draw(surf)

    def draw_game_over(self, surf):
        surf.fill((5, 5, 15))
        for sx, sy in self.starfield:
            pygame.draw.circle(surf, (80, 80, 120), (sx, (sy + self.star_offset) % HEIGHT), 1)
        title = self.big_font.render("GAME OVER", True, (255, 50, 50))
        score_t = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart = self.font.render("Press ENTER to Restart", True, (200, 200, 200))
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        surf.blit(score_t, (WIDTH // 2 - score_t.get_width() // 2, HEIGHT // 2))
        surf.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 40))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.state == 'MENU':
                            self.state = 'PLAYING'
                            self.start_level()
                        elif self.state == 'GAME_OVER':
                            self.save_stats()
                            self.reset_game()

            keys = pygame.key.get_pressed()
            self.star_offset += 0.3

            # Update logic
            if self.state == 'PLAYING':
                self.player.update(keys)
                if keys[pygame.K_SPACE] and self.player.shoot():
                    self.bullets.append(Bullet(self.player.x + self.player.w // 2 - 2, self.player.y, -7, True))
                    self.snd_shoot.play()
                self.update_enemies()
                if random.randint(0, self.enemy_fire_rate) == 0:
                    shooters = [e for e in self.enemies if e.alive]
                    if shooters:
                        s = random.choice(shooters)
                        self.enemy_bullets.append(Bullet(s.x + s.w // 2 - 2, s.y + s.h, 3 + self.level * 0.2, False))
                self.check_collisions()
                self.multiplier = 2 if 'score_x2' in self.player.powerups else 1
                for b in self.bullets: b.update()
                for b in self.enemy_bullets: b.update()
                for p in self.powerups: p.update()
                for p in self.particles: p.update()
                if self.level_transition > 0: self.level_transition -= 1

            # Drawing
            self.screen.fill((10, 10, 20))
            for sx, sy in self.starfield:
                pygame.draw.circle(self.screen, (100, 100, 150), (sx, (sy + self.star_offset) % HEIGHT), 1)

            if self.state == 'MENU':
                self.draw_menu(self.screen)
            elif self.state == 'GAME_OVER':
                self.draw_game_over(self.screen)
            else:
                for bar in self.barriers: bar.draw(self.screen)
                for p in self.powerups: p.draw(self.screen)
                for b in self.bullets: b.draw(self.screen)
                for b in self.enemy_bullets: b.draw(self.screen)
                for e in self.enemies: e.draw(self.screen)
                self.player.draw(self.screen)
                for p in self.particles: p.draw(self.screen)
                self.draw_ui(self.screen)
                if self.level_transition > 0:
                    txt = self.big_font.render(f"LEVEL {self.level - 1} COMPLETE!", True, (255, 255, 255))
                    self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))

            # Screen flash effect
            if self.screen_flash > 0:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, self.screen_flash * 15))
                self.screen.blit(overlay, (0, 0))
                self.screen_flash -= 1

            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
