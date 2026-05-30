# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type mtp --spec-draft-n-max 3 --model /AI/models/Qwen3.6-27B-uncensored-heretic-v2-Native-MTP-Preserved-NVFP4-MLP-Only-Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

import pygame
import random
import math
import struct
import sys

# ================= CONFIGURATION =================
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
COLORS = {
    'bg': (8, 8, 20),
    'player': (50, 255, 150),
    'bullet_p': (255, 255, 100),
    'bullet_e': (255, 80, 80),
    'bonus': [(255, 200, 50), (100, 255, 200), (255, 100, 150), (200, 150, 255)],
    'text': (220, 220, 240),
    'barrier': (80, 180, 255),
    'enemy': [(255, 100, 255), (255, 150, 50), (100, 255, 200)],
    'mystery': (255, 50, 50)
}
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
font_big = pygame.font.Font(None, 48)
font_bold = pygame.font.SysFont('arial', 28, bold=True)


# ================= SOUND GENERATION =================
def make_tone(freq, duration, vol=0.35):
    sr = 44100
    n = int(sr * duration)
    buf = b''.join(struct.pack('<h', int(vol * 32767 * math.sin(2 * math.pi * freq * i / sr))) for i in range(n))
    return pygame.mixer.Sound(buffer=buf)


def make_noise(duration, vol=0.3):
    sr = 44100
    n = int(sr * duration)
    buf = b''.join(struct.pack('<h', int(random.randint(-32767, 32767) * vol)) for _ in range(n))
    return pygame.mixer.Sound(buffer=buf)


SFX = {
    'shoot_p': make_tone(880, 0.08, 0.4),
    'shoot_e': make_tone(440, 0.1, 0.3),
    'explode': make_noise(0.15, 0.35),
    'bonus': make_tone(1200, 0.12, 0.4),
    'levelup': make_tone(600, 0.15, 0.35),
    'hit': make_noise(0.08, 0.2),
    'mystery': make_tone(1500, 0.2, 0.5),
    'combo': make_tone(1100, 0.05, 0.3)
}


# ================= CLASSES =================
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 40, 30
        self.base_speed = 5
        self.speed = self.base_speed
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.shoot_cd = 0
        self.base_shoot_rate = 0.3
        self.shoot_rate = self.base_shoot_rate
        self.shield = 0
        self.alive = True
        self.triple = 0
        self.laser = 0
        self.magnet = 0
        self.speed_boost = 0
        self.buff_timers = {'triple': 0, 'laser': 0, 'speed': 0, 'shield': 0, 'magnet': 0}

    def update(self, dt, keys, upgrades):
        if not self.alive: return
        spd = self.speed * (1 + upgrades.get('move', 0) * 0.2)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.x -= spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += spd
        self.x = max(20, min(SCREEN_W - 20 - self.w, self.x))
        self.rect.x = self.x
        self.shoot_cd -= dt
        if self.shield > 0: self.shield -= dt
        if self.triple > 0: self.triple -= dt
        if self.laser > 0: self.laser -= dt
        if self.magnet > 0: self.magnet -= dt
        if self.speed_boost > 0:
            self.speed_boost -= dt
            if self.speed_boost <= 0: self.speed = self.base_speed
        rate = self.base_shoot_rate * (1 - upgrades.get('reload', 0) * 0.15)
        self.shoot_rate = max(0.1, rate)

    def draw(self, surf, offset_x=0, offset_y=0):
        if not self.alive: return
        cx = self.x + self.w / 2 + offset_x
        py = self.y + offset_y
        pygame.draw.polygon(surf, COLORS['player'],
                            [(cx, py), (cx + self.w, py + self.h),
                             (cx + self.w - 10, py + self.h - 8), (cx + 10, py + self.h - 8), (cx, py + self.h)])
        pygame.draw.ellipse(surf, (200, 255, 255), (cx + 15, py + 10, 10, 10))
        if self.shield > 0:
            pulse = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.008)
            pygame.draw.circle(surf, (100, 200, 255, 80), (cx + self.w / 2, py + 15), int(28 * pulse), 2)


class Bullet:
    def __init__(self, x, y, dy, owner, is_laser=False):
        self.x, self.y = x, y
        self.dy = dy
        self.owner = owner
        self.is_laser = is_laser
        self.w = 6 if is_laser else 3
        self.h = 18 if is_laser else 12
        self.rect = pygame.Rect(x - self.w / 2, y, self.w, self.h)
        self.color = (255, 255, 200) if is_laser else (COLORS['bullet_p'] if owner == 'player' else COLORS['bullet_e'])
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 4: self.trail.pop(0)
        self.y += self.dy
        self.rect.y = self.y
        return self.y < -30 or self.y > SCREEN_H + 30

    def draw(self, surf, off_x=0, off_y=0):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail)))
            r, g, b = self.color[:3]
            surf.set_alpha(alpha)
            pygame.draw.rect(surf, (r, g, b), (tx + off_x - self.w / 2, ty + off_y, self.w, self.h * 0.6))
        surf.set_alpha(255)
        pygame.draw.rect(surf, self.color, (self.x + off_x - self.w / 2, self.y + off_y, self.w, self.h))


class Enemy:
    def __init__(self, x, y, row):
        self.x, self.y = x, y
        self.w, self.h = 36, 28
        self.row = row
        self.type = row % 3
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.alive = True
        self.color = COLORS['enemy'][self.type]
        self.pulse = 0

    def draw(self, surf, off_x=0, off_y=0):
        if not self.alive: return
        self.pulse += 0.05
        glow = 1 + 0.1 * math.sin(self.pulse)
        wx, wy = self.x + off_x, self.y + off_y
        pygame.draw.rect(surf, self.color, (wx + 2, wy + 4, int(self.w * glow), self.h - 8))
        pygame.draw.rect(surf, self.color, (wx, wy + 12, 4, 12))
        pygame.draw.rect(surf, self.color, (wx + self.w - 4, wy + 12, 4, 12))
        pygame.draw.rect(surf, (0, 0, 0), (wx + 10, wy + 8, 4, 4))
        pygame.draw.rect(surf, (0, 0, 0), (wx + self.w - 14, wy + 8, 4, 4))


class BarrierBlock:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 8, 8
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.hp = 3

    def hit(self):
        self.hp -= 1
        return self.hp <= 0

    def draw(self, surf, off_x=0, off_y=0):
        if self.hp <= 0: return
        damage = 3 - self.hp
        r = max(50, 80 - damage * 20)
        g = max(120, 180 - damage * 40)
        pygame.draw.rect(surf, (r, g, 255), (self.x + off_x, self.y + off_y, self.w, self.h))


class Barrier:
    def __init__(self, x, y):
        self.blocks = []
        grid = [
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                if val:
                    self.blocks.append(BarrierBlock(x + c * 8, y + r * 8))

    def draw(self, surf, off_x=0, off_y=0):
        for b in self.blocks: b.draw(surf, off_x, off_y)


class MysteryShip:
    def __init__(self):
        self.y = 30
        self.x = -60
        self.w, self.h = 50, 20
        self.speed = 3
        self.dir = 1
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.alive = True
        self.pulse = 0

    def update(self):
        self.x += self.speed * self.dir
        self.rect.x = self.x
        self.pulse += 0.1
        return self.x > SCREEN_W + 60

    def draw(self, surf, off_x=0, off_y=0):
        wx, wy = self.x + off_x, self.y + off_y
        pygame.draw.ellipse(surf, COLORS['mystery'], (wx, wy, self.w, self.h))
        glow = 1 + 0.3 * math.sin(self.pulse)
        pygame.draw.ellipse(surf, (255, 200, 200), (wx + 10, wy + 5, 30, 10), int(2 * glow))


class Bonus:
    def __init__(self, x, y, btype):
        self.x, self.y = x, y
        self.dy = 1.5
        self.dx = 0
        self.w, self.h = 24, 24
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.type = btype
        self.timer = 0
        self.idx = {'triple': 0, 'speed': 1, 'shield': 2, 'life': 3, 'score': 3, 'magnet': 1, 'laser': 2}.get(btype, 0)
        self.color = COLORS['bonus'][self.idx]

    def update(self, magnet_on, px, py):
        self.timer += 1
        if magnet_on:
            dx, dy = px - self.x, py - self.y
            dist = max(1, math.hypot(dx, dy))
            self.dx += (dx / dist) * 0.15
            self.dy += (dy / dist) * 0.15
        self.x += self.dx
        self.y += self.dy
        self.rect.x, self.rect.y = self.x, self.y
        self.dx *= 0.95
        self.dy *= 0.95
        return self.y > SCREEN_H + 40

    def draw(self, surf, off_x=0, off_y=0):
        cx, cy = self.x + off_x + 12, self.y + off_y + 12
        pulse = 1 + 0.2 * math.sin(self.timer * 0.12)
        r = int(12 * pulse)
        pygame.draw.circle(surf, self.color, (cx, cy), r, 2)
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 5)
        txt = font_bold.render(self.type[0].upper(), True, (20, 20, 30))
        surf.blit(txt, (cx - 6, cy - 6))


class Particle:
    def __init__(self, x, y, color, ptype='debris'):
        self.x, self.y = x, y
        self.ptype = ptype
        if ptype == 'debris':
            self.vx = random.uniform(-2.5, 2.5)
            self.vy = random.uniform(-3, -0.5)
            self.life = 1.0
            self.decay = random.uniform(0.025, 0.045)
        elif ptype == 'ring':
            self.r = 2
            self.max_r = random.uniform(15, 30)
            self.life = 1.0
            self.decay = 0.04
        elif ptype == 'glow':
            self.vx, self.vy = 0, 0
            self.life = 1.0
            self.decay = 0.03
        self.color = color

    def update(self):
        if self.ptype == 'debris':
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.96
            self.vy *= 0.96
        elif self.ptype == 'ring':
            self.r += 1.5
            if self.r > self.max_r: self.life = 0
        elif self.ptype == 'glow':
            self.r += 0.5
            if self.r > 20: self.life = 0
        self.life -= self.decay
        return self.life <= 0

    def draw(self, surf, off_x=0, off_y=0):
        alpha = int(self.life * 255)
        r, g, b = self.color[:3]
        if self.ptype == 'debris':
            pygame.draw.circle(surf, (r, g, b, alpha), (int(self.x + off_x), int(self.y + off_y)), 2)
        elif self.ptype == 'ring':
            pygame.draw.circle(surf, (r, g, b, alpha), (int(self.x + off_x), int(self.y + off_y)), int(self.r), 2)
        elif self.ptype == 'glow':
            pygame.draw.circle(surf, (r, g, b, int(alpha * 0.5)), (int(self.x + off_x), int(self.y + off_y)),
                               int(self.r))


# ================= GAME ENGINE =================
class Game:
    def __init__(self):
        self.state = 'MENU'
        self.score = 0
        self.lives = 3
        self.level = 1
        self.player = Player(SCREEN_W // 2 - 20, SCREEN_H - 60)
        self.enemies = []
        self.bullets = []
        self.barriers = []
        self.bonuses = []
        self.particles = []
        self.stars = [(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H), random.uniform(0.3, 1.0)) for _ in
                      range(120)]
        self.enemy_dir = 1
        self.enemy_speed = 1
        self.enemy_shoot_rate = 0.01
        self.enemy_move_timer = 0
        self.level_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.multiplier = 1.0
        self.shake_x = self.shake_y = 0
        self.shake_dur = 0
        self.shake_mag = 0
        self.mystery_timer = 0
        self.mystery_ship = None
        self.upgrades = {'reload': 0, 'move': 0, 'shield': 0, 'mult': 0}
        self.init_level()
        self.spawn_barriers()

    def init_level(self):
        self.enemies = []
        for r in range(4):
            for c in range(8):
                self.enemies.append(Enemy(100 + c * 55, 60 + r * 40, r))
        self.enemy_speed = 1 + (self.level - 1) * 0.3
        self.enemy_shoot_rate = 0.01 + (self.level - 1) * 0.005

    def spawn_barriers(self):
        self.barriers = [Barrier(150, 400), Barrier(300, 400), Barrier(450, 400), Barrier(600, 400)]

    def spawn_bonus(self, x=None, y=None):
        types = ['triple', 'speed', 'shield', 'life', 'score', 'magnet', 'laser']
        btype = random.choice(types)
        self.bonuses.append(Bonus(x or random.randint(60, SCREEN_W - 60), y or -30, btype))

    def spawn_particles(self, x, y, color, n=8, ptype='debris'):
        for _ in range(n):
            self.particles.append(Particle(x, y, color, ptype))
        self.particles.append(Particle(x, y, (255, 255, 255), 'ring'))

    def apply_screen_shake(self, duration, magnitude):
        self.shake_dur = duration
        self.shake_mag = magnitude

    def handle_collisions(self):
        for b in self.bullets[:]:
            if b.owner == 'player':
                hit = False
                for e in self.enemies:
                    if e.alive and b.rect.colliderect(e.rect):
                        e.alive = False
                        self.combo += 1
                        self.combo_timer = 1.5
                        self.multiplier = 1 + (self.combo - 1) * 0.25
                        pts = (3 - e.row) * 100 * self.multiplier
                        self.score += int(pts)
                        self.spawn_particles(e.x + e.w / 2, e.y + e.h / 2, e.color, 14)
                        SFX['explode'].play()
                        if self.combo >= 3: SFX['combo'].play()
                        self.bullets.remove(b)
                        self.apply_screen_shake(0.15, 3)
                        hit = True
                        break
                if not hit and self.mystery_ship and b.rect.colliderect(self.mystery_ship.rect):
                    self.score += random.choice([300, 400, 500])
                    self.spawn_particles(self.mystery_ship.x + 25, self.mystery_ship.y + 10, COLORS['mystery'], 20)
                    SFX['mystery'].play()
                    self.apply_screen_shake(0.2, 4)
                    self.bonuses.append(Bonus(self.mystery_ship.x, self.mystery_ship.y + 20,
                                              random.choice(['triple', 'shield', 'speed'])))
                    self.mystery_ship = None
                    self.bullets.remove(b)
            else:
                if self.player.alive and b.rect.colliderect(self.player.rect):
                    if self.player.shield > 0:
                        self.player.shield = 0
                        self.spawn_particles(self.player.x + 20, self.player.y + 15, (100, 200, 255), 8)
                    else:
                        self.lives -= 1
                        self.combo = 0
                        self.multiplier = 1.0
                        self.player.alive = False
                        self.spawn_particles(self.player.x + 20, self.player.y + 15, COLORS['player'], 18)
                        self.apply_screen_shake(0.3, 5)
                        if self.lives <= 0:
                            self.state = 'GAME_OVER'
                        else:
                            self.state, self.level_timer = 'PAUSED', 2.0
                    SFX['hit'].play()
                    self.bullets.remove(b)

        for b in self.bullets[:]:
            hit = False
            for bar in self.barriers:
                for blk in bar.blocks[:]:
                    if blk.hp > 0 and b.rect.colliderect(blk.rect):
                        if blk.hit(): bar.blocks.remove(blk)
                        self.spawn_particles(blk.x + 4, blk.y + 4, COLORS['barrier'], 3)
                        SFX['hit'].play()
                        self.bullets.remove(b)
                        hit = True
                        break
                if hit: break

        for b in self.bonuses[:]:
            if self.player.alive and self.player.rect.colliderect(b.rect):
                self.apply_bonus(b.type)
                self.spawn_particles(b.x + 12, b.y + 12, b.color, 10)
                self.bonuses.remove(b)
                SFX['bonus'].play()

    def apply_bonus(self, btype):
        if btype == 'triple':
            self.player.triple = 7.0
        elif btype == 'speed':
            self.player.speed_boost = self.player.speed = self.player.base_speed * 1.6; self.player.speed = self.player.base_speed * 1.6
        elif btype == 'shield':
            self.player.shield = 5.0
        elif btype == 'life':
            self.lives = min(self.lives + 1, 5)
        elif btype == 'score':
            self.score += 500
        elif btype == 'magnet':
            self.player.magnet = 8.0
        elif btype == 'laser':
            self.player.laser = 5.0

    def update(self, dt):
        if self.state == 'PAUSED':
            self.level_timer -= dt
            if self.level_timer <= 0:
                self.player.alive = True
                self.player.x = SCREEN_W // 2 - 20
                self.player.rect.x = self.player.x
                self.state = 'PLAYING'
            return
        if self.state != 'PLAYING': return

        self.combo_timer -= dt
        if self.combo_timer <= 0:
            self.combo = 0
            self.multiplier = 1.0

        self.player.update(dt, pygame.key.get_pressed(), self.upgrades)

        self.enemy_move_timer += dt
        if self.enemy_move_timer >= max(0.15, 0.3 - self.level * 0.02):
            self.enemy_move_timer = 0
            edge_hit = False
            for e in self.enemies:
                if not e.alive: continue
                e.x += self.enemy_dir * self.enemy_speed
                e.rect.x = e.x
                if e.x <= 20 or e.x + e.w >= SCREEN_W - 20: edge_hit = True
            if edge_hit:
                self.enemy_dir *= -1
                for e in self.enemies:
                    e.y += 12
                    e.rect.y = e.y
                    if e.y + e.h >= self.player.y: self.lives = 0; self.state = 'GAME_OVER'

            for e in self.enemies:
                if e.alive and random.random() < self.enemy_shoot_rate:
                    bx = e.x + e.w // 2
                    self.bullets.append(Bullet(bx, e.y + e.h, 4 + self.level * 0.5, 'enemy'))
                    SFX['shoot_e'].play()

        for b in self.bullets[:]:
            if b.update(): self.bullets.remove(b)
        for b in self.bonuses[:]:
            if b.update(self.player.magnet > 0, self.player.x + 20, self.player.y + 15): self.bonuses.remove(b)
        for p in self.particles[:]:
            if p.update(): self.particles.remove(p)

        if self.shake_dur > 0:
            self.shake_dur -= dt
            self.shake_x = random.uniform(-self.shake_mag, self.shake_mag)
            self.shake_y = random.uniform(-self.shake_mag, self.shake_mag)
        else:
            self.shake_x = self.shake_y = 0

        self.mystery_timer += dt
        if self.mystery_timer > random.uniform(15, 25) and not self.mystery_ship:
            self.mystery_ship = MysteryShip()
            self.mystery_timer = 0
        if self.mystery_ship:
            if self.mystery_ship.update(): self.mystery_ship = None

        self.handle_collisions()

        if all(not e.alive for e in self.enemies):
            self.level += 1
            self.state = 'LEVEL_UP'
            self.level_timer = 2.5
            SFX['levelup'].play()
            upg = random.choice(['reload', 'move', 'shield', 'mult'])
            self.upgrades[upg] += 1

    def draw(self, surf):
        off_x, off_y = int(self.shake_x), int(self.shake_y)
        surf.fill(COLORS['bg'])

        for sx, sy, spd in self.stars:
            sx = (sx + off_x * spd) % SCREEN_W
            sy = (sy + off_y * spd * 0.5) % SCREEN_H
            alpha = int(150 * spd)
            pygame.draw.circle(surf, (255, 255, 255, alpha), (int(sx), int(sy)), 1)

        for bar in self.barriers: bar.draw(surf, off_x, off_y)
        for e in self.enemies: e.draw(surf, off_x, off_y)
        if self.mystery_ship: self.mystery_ship.draw(surf, off_x, off_y)
        for b in self.bonuses: b.draw(surf, off_x, off_y)
        for p in self.particles: p.draw(surf, off_x, off_y)
        self.player.draw(surf, off_x, off_y)
        for b in self.bullets: b.draw(surf, off_x, off_y)
        self.draw_ui(surf)

    def draw_ui(self, surf):
        txt = font.render(f"SCORE: {self.score:07d}  LIVES: {self.lives}  LEVEL: {self.level}", True, COLORS['text'])
        surf.blit(txt, (20, 10))

        # Combo & Multiplier
        if self.combo >= 2:
            mult_col = (255, 255, 255) if self.multiplier > 2 else (255, 200, 100)
            c_txt = font_bold.render(f"COMBO: {self.combo}x  ({self.multiplier:.1f}x)", True, mult_col)
            surf.blit(c_txt, (SCREEN_W - c_txt.get_width() - 20, 10))

        # Active Buffs
        px, py = 20, 40
        buffs = []
        if self.player.triple > 0: buffs.append(("TRIPLE", self.player.triple))
        if self.player.laser > 0: buffs.append(("LASER", self.player.laser))
        if self.player.speed_boost > 0: buffs.append(("SPEED", self.player.speed_boost))
        if self.player.shield > 0: buffs.append(("SHIELD", self.player.shield))
        if self.player.magnet > 0: buffs.append(("MAGNET", self.player.magnet))
        for name, dur in buffs:
            c = (100, 255, 150) if "SHIELD" in name else (255, 200, 50)
            b_txt = font.render(f"{name}: {dur:.1f}s", True, c)
            surf.blit(b_txt, (px, py))
            py += 20

        # Permanent Upgrades
        py += 10
        u_txt = font.render("UPGRADES:", True, (150, 150, 180))
        surf.blit(u_txt, (px, py))
        py += 20
        for k, v in self.upgrades.items():
            if v > 0:
                u_label = font.render(f"+{v} {k.upper()}", True, (100, 180, 255))
                surf.blit(u_label, (px, py))
                py += 18

        if self.state == 'MENU':
            self.draw_overlay("SPACE INVADERS", "PRESS SPACE TO START", "WASD/ARROWS: MOVE  SPACE: SHOOT  ESC: PAUSE")
        elif self.state == 'LEVEL_UP':
            self.draw_overlay("LEVEL COMPLETE!", f"GET READY FOR LEVEL {self.level}", "NEW UPGRADE UNLOCKED!")
        elif self.state == 'GAME_OVER':
            self.draw_overlay("GAME OVER", f"FINAL SCORE: {self.score:07d}", "PRESS SPACE TO RESTART")

    def draw_overlay(self, *lines):
        pygame.draw.rect(screen, (0, 0, 0, 190), (0, 0, SCREEN_W, SCREEN_H))
        y = SCREEN_H // 2 - len(lines) * 22
        for i, l in enumerate(lines):
            f = font_big if i == 0 else font
            t = f.render(l, True, COLORS['text'])
            screen.blit(t, ((SCREEN_W - t.get_width()) // 2, y))
            y += 32

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if self.state in ('MENU', 'GAME_OVER'):
                        self.reset()
                    elif self.state == 'PLAYING' and self.player.alive and self.player.shoot_cd <= 0:
                        bx = self.player.x + self.player.w // 2
                        is_laser = self.player.laser > 0
                        self.bullets.append(Bullet(bx, self.player.y, -8 if is_laser else -7, 'player', is_laser))
                        if self.player.triple > 0:
                            self.bullets.append(Bullet(bx - 8, self.player.y + 2, -6.5, 'player'))
                            self.bullets.append(Bullet(bx + 8, self.player.y + 2, -6.5, 'player'))
                        self.player.shoot_cd = self.player.shoot_rate
                        SFX['shoot_p'].play()
                elif e.key == pygame.K_ESCAPE and self.state == 'PLAYING':
                    self.state, self.level_timer = 'PAUSED', 0.5

    def reset(self):
        self.score = 0;
        self.lives = 3;
        self.level = 1
        self.player = Player(SCREEN_W // 2 - 20, SCREEN_H - 60)
        self.bullets = [];
        self.bonuses = [];
        self.particles = []
        self.combo = 0;
        self.combo_timer = 0;
        self.multiplier = 1.0
        self.mystery_timer = 0;
        self.mystery_ship = None
        self.upgrades = {'reload': 0, 'move': 0, 'shield': 0, 'mult': 0}
        self.init_level();
        self.spawn_barriers()
        self.state = 'PLAYING'


# ================= MAIN LOOP =================
def main():
    game = Game()
    while True:
        dt = clock.tick(FPS) / 1000
        game.handle_events()
        if game.state == 'LEVEL_UP':
            game.level_timer -= dt
            if game.level_timer <= 0:
                game.init_level();
                game.spawn_barriers();
                game.state = 'PLAYING';
                game.spawn_bonus()
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
