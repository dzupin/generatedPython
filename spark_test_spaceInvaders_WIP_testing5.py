# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Excellent. Python game  is working correctly. Now update the code to make game even more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Also make changes to improve replay of the game, permanent upgrades after receiving special bonuses would be nice have. OR even better, shopping system where user can use point from previous play to purchase enhancements.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --parallel 1  --temp 1.0 --top_p 1.0 --chat-template-kwargs '{"reasoning_effort":"max"}'  --spec-type draft-dspark   --spec-draft-n-max 3 --fit off  -md /AI/models/dspark-DeepSeek-V4-Flash-0731-BF16.gguf  --model /AI/models/Huihui-DeepSeek-V4-Flash-Q2-0731.gguf



"""
SPACE INVADERS — Modern Remake (Meta-Progression Edition)
==========================================================
A polished, addictive Space Invaders with:

  • Destructible barriers (upgradeable to take extra hits)
  • Several levels with increasing difficulty
  • Bonus system: combo multiplier, level-clear bonus, 4 power-ups
  • Synthesized sound effects (no external audio files)
  • Persistent stats in space_invaders_stats.json
  • PERMANENT UPGRADE SHOP — spend meta-points earned in previous
    runs to permanently enhance future games (more lives, speed,
    bullets, shields, score boost, drops, combo cap, strong barriers)

  • Addictive visual enhancements: screen shake, glowing explosions,
    floating score popups, level-intro banner, combo flashes,
    engine trails, animated HUD.

Controls:
  Left/Right or A/D .... move
  Space ................ shoot  (hold with rapid-fire power-up)
  P .................... pause
  Enter/Space .......... start / continue
  S .................... shop (main menu)
  Up/Down .............. shop selection
  Esc .................. back from shop

Requires: pygame, numpy
  pip install pygame numpy
"""

import pygame
import pygame.sndarray
import numpy as np
import random
import math
import json
import os

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
SCREEN_W = 900
SCREEN_H = 700
FPS = 60

PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 14
ENEMY_BULLET_SPEED = 6
ENEMY_BASE_SPEED = 1.8
ENEMY_DROP = 22
MAX_PLAYER_BULLETS = 4
BRICK_SIZE = 10
BARRIER_ROWS = 5
BARRIER_COLS = 8

STATS_FILE = "space_invaders_stats.json"

# Colors
BLACK = (0, 0, 0)
BG_TOP = (6, 10, 30)
BG_BOTTOM = (18, 8, 40)
PLAYER_COLOR = (80, 220, 255)
PLAYER_GLOW = (120, 240, 255)
ENEMY_COLORS = [(255, 70, 70), (255, 150, 60), (200, 60, 220)]
BARRIER_COLOR = (60, 220, 140)
PLAYER_BULLET_COLOR = (255, 255, 120)
ENEMY_BULLET_COLOR = (255, 90, 170)
POWERUP_COLOR = (120, 255, 120)
TEXT_COLOR = (220, 220, 240)
HUD_COLOR = (150, 150, 200)
COMBO_COLOR = (255, 200, 80)
GOLD = (255, 210, 90)

POWERUP_KINDS = ['shield', 'rapid', 'life', 'multi']

# Shop upgrade catalogue: key, name, base cost, max level, description
SHOP_ITEMS = [
    {'key': 'lives',    'name': 'Extra Lives',       'base': 200, 'max': 5,
     'desc': 'Start each run with more lives'},
    {'key': 'speed',    'name': 'Engine Speed',      'base': 150, 'max': 5,
     'desc': 'Faster ship movement'},
    {'key': 'bullets',  'name': 'Extra Bullets',     'base': 250, 'max': 3,
     'desc': 'Fire more bullets at once'},
    {'key': 'shield',   'name': 'Starting Shield',   'base': 300, 'max': 3,
     'desc': 'Begin with an energy shield'},
    {'key': 'score',    'name': 'Score Boost',       'base': 400, 'max': 5,
     'desc': '+10% score per level'},
    {'key': 'drop',     'name': 'Lucky Drops',       'base': 350, 'max': 5,
     'desc': 'More power-up drops'},
    {'key': 'combo',    'name': 'Combo Master',      'base': 500, 'max': 3,
     'desc': 'Higher combo multiplier cap'},
    {'key': 'barrier',  'name': 'Strong Barriers',   'base': 300, 'max': 3,
     'desc': 'Barriers take extra hits'},
]


# ----------------------------------------------------------------------------
# Persistent stats
# ----------------------------------------------------------------------------
def load_stats():
    defaults = {
        'high_score': 0, 'games_played': 0,
        'total_kills': 0, 'best_level': 1, 'total_score': 0,
        'meta_points': 0,
        'upgrades': {item['key']: 0 for item in SHOP_ITEMS},
    }
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                defaults.update({k: data.get(k, v) for k, v in defaults.items()})
                # ensure every upgrade key exists
                for item in SHOP_ITEMS:
                    defaults['upgrades'].setdefault(item['key'], 0)
        except Exception:
            pass
    return defaults


def save_stats(stats):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass


# ----------------------------------------------------------------------------
# Sound manager — synthesized with numpy, works with mono or stereo mixer
# ----------------------------------------------------------------------------
class SoundManager:
    def __init__(self):
        self.available = True
        self.sounds = {}
        try:
            pygame.mixer.init()
        except Exception:
            self.available = False
            return

        self.sounds['shoot']        = self._synth(600, 0.07, 0.30, 'square')
        self.sounds['enemy_shoot']  = self._synth(300, 0.10, 0.20, 'sine')
        self.sounds['explosion']    = self._noise(0.30, 0.40)
        self.sounds['hit']          = self._synth(900, 0.05, 0.20, 'square')
        self.sounds['powerup']      = self._synth(800, 0.15, 0.30, 'sine')
        self.sounds['level_clear']  = self._arpeggio([523, 659, 784, 1047], 0.15, 0.30)
        self.sounds['game_over']    = self._arpeggio([400, 300, 200, 100], 0.40, 0.30)

    def play(self, name):
        if self.available and name in self.sounds:
            self.sounds[name].play()

    def _make_sound(self, data):
        init = pygame.mixer.get_init()
        if init is None:
            return None
        channels = init[2]                       # (frequency, format, channels)
        data = data.reshape(-1, 1)               # n samples, 1 channel
        if channels > 1:
            data = np.repeat(data, channels, axis=1)   # upmix mono -> stereo
        return pygame.sndarray.make_sound(data)

    def _synth(self, freq, duration, vol, waveform):
        sr = 44100
        n = int(sr * duration)
        t = np.linspace(0, duration, n, False)
        if waveform == 'square':
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform == 'triangle':
            wave = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
        else:
            wave = np.sin(2 * np.pi * freq * t)

        env = np.ones(n)
        attack = min(int(0.01 * sr), n)
        env[:attack] = np.linspace(0, 1, attack)
        env *= np.exp(-3.0 * t / duration)
        data = (wave * env * vol * 32767).astype(np.int16)
        return self._make_sound(data)

    def _noise(self, duration, vol):
        sr = 44100
        n = int(sr * duration)
        t = np.linspace(0, duration, n, False)
        noise = np.random.randn(n)
        env = np.exp(-4.0 * t / duration)
        data = (noise * env * vol * 32767).astype(np.int16)
        return self._make_sound(data)

    def _arpeggio(self, freqs, dur, vol):
        sr = 44100
        total = np.zeros(0)
        for f in freqs:
            n = int(sr * dur)
            t = np.linspace(0, dur, n, False)
            wave = np.sin(2 * np.pi * f * t) * np.exp(-3 * t / dur)
            total = np.concatenate([total, wave])
        data = (total * vol * 32767).astype(np.int16)
        return self._make_sound(data)


# ----------------------------------------------------------------------------
# Starfield background
# ----------------------------------------------------------------------------
class Starfield:
    def __init__(self):
        self.stars = []
        for _ in range(160):
            self.stars.append([
                random.randrange(SCREEN_W), random.randrange(SCREEN_H),
                random.choice([1, 2, 3]), random.randrange(40, 220)
            ])

    def update(self):
        for s in self.stars:
            s[1] += s[3] * 0.012
            if s[1] > SCREEN_H:
                s[1] = 0

    def draw(self, surf):
        for x, y, r, sp in self.stars:
            b = int(255 * r / 3) + 40
            c = (min(255, int(255 * r / 3)),
                 min(255, int(255 * r / 3)),
                 min(255, b))
            pygame.draw.circle(surf, c, (int(x), int(y)), r)


# ----------------------------------------------------------------------------
# Floating score popups
# ----------------------------------------------------------------------------
class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 55

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        font = pygame.font.Font(None, 22)
        img = font.render(self.text, True, self.color)
        surf.blit(img, (int(self.x - img.get_width() // 2), int(self.y)))


# ----------------------------------------------------------------------------
# Entities
# ----------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H - 70
        self.width = 34
        self.height = 26
        self.lives = 3
        self.shield = 0          # hits absorbed
        self.rapid_until = 0     # pygame ticks ms
        self.mult = 1            # base score multiplier (upgrade + power-up)
        self.speed = PLAYER_SPEED

    def rect(self):
        return pygame.Rect(int(self.x - 17), int(self.y - 13), self.width, self.height)


class Enemy:
    def __init__(self, x, y, etype):
        self.x = x
        self.y = y
        self.width = 44
        self.height = 34
        self.etype = etype       # 0, 1, 2 => different sprite/score
        self.alive = True
        self.anim = 0


class Bullet:
    def __init__(self, x, y, vy, color):
        self.x = x
        self.y = y
        self.vy = vy
        self.color = color
        self.rect = pygame.Rect(int(x - 2), int(y - 5), 4, 10)

    def update(self):
        self.y += self.vy
        self.rect.y = int(self.y - 5)
        self.rect.x = int(self.x - 2)


class Barrier:
    def __init__(self, x, y, strength=1):
        self.x, self.y = x, y
        self.strength = strength
        self.bricks = []          # [x, y, hp]
        for row in range(BARRIER_ROWS):
            for col in range(BARRIER_COLS):
                if (row == BARRIER_ROWS - 1 and col < 2) or \
                   (row == BARRIER_ROWS - 1 and col >= BARRIER_COLS - 2):
                    continue
                self.bricks.append([x + col * BRICK_SIZE, y + row * BRICK_SIZE, strength])

    def draw(self, surf):
        for bx, by, hp in self.bricks:
            if hp > 0:
                # damaged bricks get darker
                shade = max(0, int(120 * hp / self.strength))
                color = (60 + shade, 220, 140)
                pygame.draw.rect(surf, color, (bx, by, BRICK_SIZE - 1, BRICK_SIZE - 1))

    def hit(self, bullet):
        br = pygame.Rect(bullet.x - 2, bullet.y - 5, 4, 10)
        for i, (bx, by, hp) in enumerate(self.bricks):
            if hp > 0 and br.colliderect(pygame.Rect(bx, by, BRICK_SIZE, BRICK_SIZE)):
                self.bricks[i][2] -= 1
                return True
        return False


class PowerUp:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind = kind
        self.vy = 2
        self.t = 0
        self.rect = pygame.Rect(int(x - 8), int(y - 8), 16, 16)

    def update(self):
        self.y += self.vy
        self.t += 1
        self.rect.y = int(self.y - 8)
        self.rect.x = int(self.x - 8)


class Particle:
    def __init__(self, x, y, color, vel, life):
        self.x, self.y = x, y
        self.vx, self.vy = vel
        self.color = color
        self.life = life
        self.maxlife = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        r = max(1, int(self.life / self.maxlife * 3))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)


# ----------------------------------------------------------------------------
# Main Game
# ----------------------------------------------------------------------------
class Game:
    def __init__(self, screen, sound, stats):
        self.screen = screen
        self.sound = sound
        self.stats = stats
        self.upgrades = self.stats.get('upgrades', {})
        for item in SHOP_ITEMS:
            self.upgrades.setdefault(item['key'], 0)
        self.meta_points = self.stats.get('meta_points', 0)

        self.high_score = self.stats.get('high_score', 0)
        self.surface = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        self.stars = Starfield()
        self.gradient = self._make_gradient()

        self.state = 'menu'
        self.paused = False
        self.menu_anim = 0
        self.game_over_timer = 0
        self.shake = 0
        self.floating = []
        self.shop_sel = 0
        self.reset_round()

    # ---------- setup ----------
    def _make_gradient(self):
        g = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
            g_ = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
            b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
            pygame.draw.line(g, (r, g_, b), (0, y), (SCREEN_W, y))
        return g

    def reset_round(self):
        self.score = 0
        self.level = 1
        self.kills = 0
        self.floating = []
        self.shake = 0
        self.player = Player()
        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.barriers = []
        self.powerups = []
        self.particles = []
        self.enemy_dir = 1
        self.enemy_speed = ENEMY_BASE_SPEED
        self.enemy_anim_timer = 0
        self.enemy_shoot_timer = 0
        self.combo = 1
        self.combo_timer = 0
        self.level_clear_bonus = 0
        self.intro_timer = 2.0
        self.engine_timer = 0

        # apply permanent upgrades
        upg = self.upgrades
        self.player.lives = 3 + upg['lives']
        self.player.mult = 1 + upg['score'] * 0.1
        self.player.shield = upg['shield']
        self.player.speed = PLAYER_SPEED + upg['speed']
        self.max_bullets = MAX_PLAYER_BULLETS + upg['bullets']
        self.combo_cap = 5 + upg['combo']
        self.drop_chance = 0.18 + upg['drop'] * 0.05
        self.barrier_strength = 1 + upg['barrier']

        self.spawn_enemies()
        self.spawn_barriers()

    def spawn_enemies(self):
        cols, rows = 10, 5
        start_x, start_y = 60, 80
        for r in range(rows):
            for c in range(cols):
                etype = 2 if r == 0 else 1 if r < 3 else 0
                self.enemies.append(Enemy(start_x + c * 50, start_y + r * 40, etype))

    def spawn_barriers(self):
        gap = SCREEN_W // 4
        for i in range(4):
            bx = gap // 2 + i * gap - (BARRIER_COLS * BRICK_SIZE) // 2
            by = SCREEN_H - 140
            self.barriers.append(Barrier(bx, by, self.barrier_strength))

    def next_level(self):
        self.level += 1
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.barriers = []
        self.enemy_dir = 1
        self.intro_timer = 1.6
        self.spawn_enemies()
        self.spawn_barriers()
        self.state = 'playing'
        self.add_shake(6)

    # ---------- events ----------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return 'quit'
            if e.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = 'playing'
                        self.reset_round()
                    elif e.key == pygame.K_s:
                        self.state = 'shop'
                        self.shop_sel = 0
                elif self.state == 'shop':
                    if e.key == pygame.K_UP:
                        self.shop_sel = (self.shop_sel - 1) % len(SHOP_ITEMS)
                    elif e.key == pygame.K_DOWN:
                        self.shop_sel = (self.shop_sel + 1) % len(SHOP_ITEMS)
                    elif e.key == pygame.K_RETURN:
                        self.buy_shop()
                    elif e.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                elif self.state == 'playing':
                    if e.key == pygame.K_SPACE:
                        self.player_shoot()
                    elif e.key == pygame.K_p:
                        self.paused = not self.paused
                elif self.state == 'level_clear':
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.next_level()
                elif self.state == 'game_over':
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = 'menu'
        return None

    def player_shoot(self):
        if len(self.player_bullets) < self.max_bullets:
            self.player_bullets.append(
                Bullet(self.player.x, self.player.y - 20, -PLAYER_BULLET_SPEED, PLAYER_BULLET_COLOR))
            self.sound.play('shoot')
            self.add_shake(2)

    # ---------- shop ----------
    def shop_cost(self, item):
        return item['base'] * (self.upgrades[item['key']] + 1)

    def buy_shop(self):
        item = SHOP_ITEMS[self.shop_sel]
        key = item['key']
        if self.upgrades[key] >= item['max']:
            return
        cost = self.shop_cost(item)
        if self.meta_points >= cost:
            self.meta_points -= cost
            self.upgrades[key] += 1
            self.stats['meta_points'] = self.meta_points
            self.stats['upgrades'] = self.upgrades
            save_stats(self.stats)
            self.sound.play('powerup')
            self.add_shake(3)

    # ---------- update ----------
    def update(self, dt):
        self.stars.update()
        if self.state == 'playing' and not self.paused:
            self.update_playing(dt)
        elif self.state == 'menu':
            self.menu_anim += dt
        elif self.state == 'game_over':
            self.game_over_timer += dt

        for ft in self.floating[:]:
            ft.update()
            if ft.life <= 0:
                self.floating.remove(ft)

    def add_shake(self, amt):
        self.shake = max(self.shake, amt)

    def update_playing(self, dt):
        self.enemy_anim_timer += dt
        if self.intro_timer > 0:
            self.intro_timer -= dt

        # player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.x -= self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.x += self.player.speed
        self.player.x = max(20, min(SCREEN_W - 20, self.player.x))

        # rapid-fire power-up
        if pygame.time.get_ticks() < self.player.rapid_until and keys[pygame.K_SPACE]:
            self.player_shoot()

        # engine trail
        self.engine_timer -= dt
        if self.engine_timer <= 0:
            self.spawn_particles(self.player.x, self.player.y + 16, PLAYER_GLOW, 2)
            self.engine_timer = 0.03

        # bullets
        for b in self.player_bullets[:]:
            b.update()
            if b.y < 0:
                self.player_bullets.remove(b)
        for b in self.enemy_bullets[:]:
            b.update()
            if b.y > SCREEN_H:
                self.enemy_bullets.remove(b)

        # enemies
        self.move_enemies(dt)
        if self.intro_timer <= 0:
            self.enemy_shoot(dt)

        # collisions
        self.check_collisions()

        # power-ups
        for p in self.powerups[:]:
            p.update()
            if p.y > SCREEN_H:
                self.powerups.remove(p)
            elif self.player.rect().colliderect(p.rect):
                self.apply_powerup(p)
                self.powerups.remove(p)

        # particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        # combo decay
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 1

        # level cleared?
        if not self.enemies:
            self.state = 'level_clear'
            self.sound.play('level_clear')
            self.add_shake(10)
            self.level_clear_bonus = 100 * self.level + self.score // 10
            self.score += self.level_clear_bonus
            if self.score > self.high_score:
                self.high_score = self.score

    def move_enemies(self, dt):
        if not self.enemies:
            return
        self.enemy_speed = ENEMY_BASE_SPEED + (self.level - 1) * 0.6

        edge = False
        for e in self.enemies:
            if e.x <= 20 or e.x + e.width >= SCREEN_W - 20:
                edge = True
                break
        if edge:
            self.enemy_dir *= -1
            for e in self.enemies:
                e.y += ENEMY_DROP
            for e in self.enemies:
                if e.y + e.height >= SCREEN_H - 80:
                    self.player.lives = 0
                    self.end_game()
                    return

        for e in self.enemies:
            e.x += self.enemy_dir * self.enemy_speed * dt * 60

    def enemy_shoot(self, dt):
        self.enemy_shoot_timer -= dt
        if self.enemy_shoot_timer <= 0:
            alive = [e for e in self.enemies if e.alive]
            if alive:
                e = random.choice(alive)
                self.enemy_bullets.append(
                    Bullet(e.x, e.y + e.height, ENEMY_BULLET_SPEED, ENEMY_BULLET_COLOR))
                self.sound.play('enemy_shoot')
            interval = max(0.3, 1.2 - (self.level - 1) * 0.07)
            self.enemy_shoot_timer = interval * random.uniform(0.5, 1.5)

    # ---------- collisions ----------
    def check_collisions(self):
        for b in self.player_bullets[:]:
            for e in self.enemies[:]:
                if e.alive and b.rect.colliderect(pygame.Rect(e.x, e.y, e.width, e.height)):
                    e.alive = False
                    self.enemies.remove(e)
                    self.kill_enemy(b.x, b.y, e.etype)
                    if b in self.player_bullets:
                        self.player_bullets.remove(b)
                    break

        for b in self.enemy_bullets[:]:
            removed = False
            if self.player.rect().colliderect(b.rect):
                self.hit_player()
                removed = True
            else:
                for br in self.barriers:
                    if br.hit(b):
                        self.sound.play('hit')
                        self.spawn_particles(b.x, b.y, BARRIER_COLOR, 3)
                        removed = True
                        break
            if removed and b in self.enemy_bullets:
                self.enemy_bullets.remove(b)

        for b in self.player_bullets[:]:
            removed = False
            for br in self.barriers:
                if br.hit(b):
                    self.sound.play('hit')
                    self.spawn_particles(b.x, b.y, BARRIER_COLOR, 3)
                    removed = True
                    break
            if removed and b in self.player_bullets:
                self.player_bullets.remove(b)

        for pb in self.player_bullets[:]:
            for eb in self.enemy_bullets[:]:
                if pb.rect.colliderect(eb.rect):
                    self.spawn_particles(pb.x, pb.y, (255, 255, 200), 3)
                    if pb in self.player_bullets:
                        self.player_bullets.remove(pb)
                    if eb in self.enemy_bullets:
                        self.enemy_bullets.remove(eb)
                    break

    def kill_enemy(self, x, y, etype):
        score = {0: 10, 1: 20, 2: 30}[etype]
        self.kills += 1
        if self.combo_timer > 0 and self.combo < self.combo_cap:
            self.combo += 1
        else:
            self.combo = 1
        self.combo_timer = 1.5
        gained = score * self.combo * self.player.mult
        self.score += gained

        # floating score popup
        if self.combo > 1:
            self.floating.append(FloatingText(f"+{gained}  COMBO x{self.combo}", x, y, COMBO_COLOR))
            self.sound.play('powerup')
            self.add_shake(4)
        else:
            self.floating.append(FloatingText(f"+{gained}", x, y, (120, 255, 120)))

        self.spawn_particles(x, y, ENEMY_COLORS[etype], 10)
        self.sound.play('explosion')
        self.add_shake(3)

        # power-up drop
        if random.random() < self.drop_chance:
            kind = random.choice(POWERUP_KINDS)
            self.powerups.append(PowerUp(x, y, kind))

    def hit_player(self):
        if self.player.shield > 0:
            self.player.shield -= 1
            self.sound.play('hit')
            self.spawn_particles(self.player.x, self.player.y, PLAYER_COLOR, 6)
            self.add_shake(5)
        else:
            self.player.lives -= 1
            self.sound.play('explosion')
            self.spawn_particles(self.player.x, self.player.y, PLAYER_COLOR, 14)
            self.add_shake(10)
            if self.player.lives <= 0:
                self.end_game()

    def end_game(self):
        if self.state == 'game_over':
            return
        self.state = 'game_over'
        self.stats['high_score'] = max(self.stats.get('high_score', 0), self.score)
        self.stats['games_played'] = self.stats.get('games_played', 0) + 1
        self.stats['total_kills'] = self.stats.get('total_kills', 0) + self.kills
        self.stats['best_level'] = max(self.stats.get('best_level', 0), self.level)
        self.stats['total_score'] = self.stats.get('total_score', 0) + self.score

        # earn meta-points from this run
        earned = self.score
        self.meta_points += earned
        self.stats['meta_points'] = self.meta_points
        save_stats(self.stats)
        self.sound.play('game_over')

    def apply_powerup(self, p):
        self.sound.play('powerup')
        self.spawn_particles(p.x, p.y, POWERUP_COLOR, 6)
        self.add_shake(4)
        self.floating.append(FloatingText(p.kind.upper() + '!', p.x, p.y, POWERUP_COLOR))
        if p.kind == 'shield':
            self.player.shield = min(3, self.player.shield + 1)
        elif p.kind == 'rapid':
            self.player.rapid_until = pygame.time.get_ticks() + 8000
        elif p.kind == 'life':
            self.player.lives = min(5, self.player.lives + 1)
        elif p.kind == 'multi':
            self.player.mult = min(4, self.player.mult + 1)

    def spawn_particles(self, x, y, color, n):
        for _ in range(n):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            self.particles.append(
                Particle(x, y, color,
                         (math.cos(angle) * speed, math.sin(angle) * speed),
                         random.randint(20, 40)))

    # ---------- drawing ----------
    def draw(self):
        surf = self.surface
        surf.blit(self.gradient, (0, 0))
        self.stars.draw(surf)

        if self.state == 'menu':
            self.draw_menu(surf)
        elif self.state == 'shop':
            self.draw_shop(surf)
        elif self.state == 'playing':
            self.draw_playing(surf)
            if self.paused:
                self._overlay(surf, "PAUSED", "Press P to resume")
        elif self.state == 'level_clear':
            self.draw_playing(surf)
            self._overlay(surf, f"LEVEL {self.level} CLEARED",
                          f"BONUS: {self.level_clear_bonus}   Press Enter / Space")
        elif self.state == 'game_over':
            self.draw_playing(surf)
            self.draw_game_over(surf)

        # floating texts always drawn
        for ft in self.floating:
            ft.draw(surf)

        # screen shake
        if self.shake > 0:
            ox = random.randint(-self.shake, self.shake)
            oy = random.randint(-self.shake, self.shake)
            self.shake = max(0, self.shake - 1)
        else:
            ox, oy = 0, 0
        self.screen.blit(surf, (ox, oy))
        pygame.display.flip()

    def draw_playing(self, surf):
        # barriers with subtle glow
        for br in self.barriers:
            br.draw(surf)

        # player with neon glow
        glow = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*PLAYER_GLOW, 60), (22, 22), 22)
        surf.blit(glow, (int(self.player.x - 22), int(self.player.y - 22)))
        self._draw_player(surf, self.player)

        # enemies
        for e in self.enemies:
            if e.alive:
                self._draw_enemy(surf, e)

        # bullets
        for b in self.player_bullets:
            pygame.draw.rect(surf, b.color, b.rect)
        for b in self.enemy_bullets:
            pygame.draw.circle(surf, b.color, (int(b.x), int(b.y)), 4)

        # power-ups with glow
        for p in self.powerups:
            pg = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(pg, (*POWERUP_COLOR, 70), (14, 14), 14)
            surf.blit(pg, (int(p.x - 14), int(p.y - 14)))
            pygame.draw.circle(surf, POWERUP_COLOR, (int(p.x), int(p.y)), 10)
            pygame.draw.circle(surf, (30, 90, 40), (int(p.x), int(p.y)), 6)
            self._draw_text(surf, p.kind.upper(), int(p.x), int(p.y) - 20, 14, (200, 255, 200), True)

        # particles on additive-style glow surface
        p_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for p in self.particles:
            if p.life <= 0:
                continue
            r = max(1, int(p.life / p.maxlife * 4))
            pygame.draw.circle(p_surf, (*p.color, 150), (int(p.x), int(p.y)), r)
        surf.blit(p_surf, (0, 0))

        self.draw_hud(surf)

        # level intro banner
        if self.intro_timer > 0:
            self._draw_text(surf, f"LEVEL {self.level}", SCREEN_W // 2, 220, 44, PLAYER_GLOW, True)

    def _draw_player(self, surf, player):
        cx, cy = int(player.x), int(player.y)
        pts = [(cx, cy - 15), (cx - 12, cy + 10), (cx + 12, cy + 10)]
        pygame.draw.polygon(surf, PLAYER_COLOR, pts, 0)
        pygame.draw.polygon(surf, (150, 255, 255),
                            [(cx - 6, cy - 9), (cx + 6, cy - 9), (cx, cy - 14)], 0)
        pygame.draw.polygon(surf, PLAYER_COLOR,
                            [(cx - 10, cy - 6), (cx - 16, cy + 10), (cx - 8, cy + 10)], 0)
        pygame.draw.polygon(surf, PLAYER_COLOR,
                            [(cx + 10, cy - 6), (cx + 16, cy + 10), (cx + 8, cy + 10)], 0)
        pygame.draw.circle(surf, PLAYER_GLOW, (cx, cy + 12), 4)

    def _draw_enemy(self, surf, e):
        cx, cy = int(e.x), int(e.y)
        color = ENEMY_COLORS[e.etype]
        anim = int(self.enemy_anim_timer * 4) % 2 == 0

        pygame.draw.polygon(surf, color,
                            [(cx - 18, cy), (cx - 18, cy - 8), (cx + 18, cy - 8), (cx + 18, cy)], 0)
        pygame.draw.circle(surf, color, (cx - 10, cy - 14), 8)
        pygame.draw.circle(surf, color, (cx + 10, cy - 14), 8)
        if anim:
            pygame.draw.line(surf, color, (cx - 12, cy - 20), (cx - 8, cy - 28), 2)
            pygame.draw.line(surf, color, (cx + 12, cy - 20), (cx + 8, cy - 28), 2)
        else:
            pygame.draw.line(surf, color, (cx - 8, cy - 20), (cx - 12, cy - 28), 2)
            pygame.draw.line(surf, color, (cx + 8, cy - 20), (cx + 12, cy - 28), 2)
        pygame.draw.circle(surf, (255, 255, 255), (cx - 6, cy - 6), 3)
        pygame.draw.circle(surf, (255, 255, 255), (cx + 6, cy - 6), 3)

    def draw_hud(self, surf):
        self._draw_text(surf, f"SCORE: {self.score}", 10, 10, 22, HUD_COLOR)
        self._draw_text(surf, f"LEVEL: {self.level}", 10, 34, 22, HUD_COLOR)
        self._draw_text(surf, f"HIGH: {self.high_score}", SCREEN_W - 150, 10, 22, HUD_COLOR)

        for i in range(self.player.lives):
            x = 10 + i * 26
            pygame.draw.polygon(surf, PLAYER_COLOR,
                                [(x, 60), (x - 6, 72), (x + 6, 72)], 0)

        if self.combo > 1 and self.combo_timer > 0:
            self._draw_text(surf, f"COMBO x{self.combo}", SCREEN_W // 2, 10, 26, COMBO_COLOR, True)

        if pygame.time.get_ticks() < self.player.rapid_until:
            self._draw_text(surf, "RAPID FIRE", SCREEN_W // 2, 36, 20, (120, 255, 120), True)
        if self.player.shield > 0:
            self._draw_text(surf, f"SHIELD {self.player.shield}", SCREEN_W // 2, 56, 20, (80, 220, 255), True)
        if self.player.mult > 1:
            self._draw_text(surf, f"SCORE x{self.player.mult:.1f}", SCREEN_W // 2, 76, 20, COMBO_COLOR, True)

    def draw_menu(self, surf):
        y = int(140 + 20 * math.sin(self.menu_anim * 2))
        self._draw_text(surf, "SPACE", SCREEN_W // 2, y - 60, 52, PLAYER_GLOW, True)
        self._draw_text(surf, "INVADERS", SCREEN_W // 2, y, 52, (255, 120, 120), True)

        self._draw_text(surf, f"HIGH SCORE: {self.high_score}", SCREEN_W // 2, y + 70, 26, COMBO_COLOR, True)
        self._draw_text(surf, f"META POINTS: {self.meta_points}", SCREEN_W // 2, y + 96, 26, GOLD, True)

        # upgrade summary
        line = "  |  ".join(f"{SHOP_ITEMS[i]['name']} Lv{self.upgrades[SHOP_ITEMS[i]['key']]}"
                            for i in (0, 1, 2, 3))
        self._draw_text(surf, line, SCREEN_W // 2, y + 128, 18, HUD_COLOR, True)
        line2 = "  |  ".join(f"{SHOP_ITEMS[i]['name']} Lv{self.upgrades[SHOP_ITEMS[i]['key']]}"
                             for i in (4, 5, 6, 7))
        self._draw_text(surf, line2, SCREEN_W // 2, y + 148, 18, HUD_COLOR, True)

        self._draw_text(surf, "Controls:  Arrow/A-D move   Space shoot   P pause",
                        SCREEN_W // 2, y + 190, 20, TEXT_COLOR, True)
        self._draw_text(surf, "ENTER/SPACE: Start    S: Upgrade Shop",
                        SCREEN_W // 2, y + 214, 22, TEXT_COLOR, True)

    def draw_shop(self, surf):
        self._draw_text(surf, "UPGRADE SHOP", SCREEN_W // 2, 40, 44, GOLD, True)
        self._draw_text(surf, f"META POINTS: {self.meta_points}", SCREEN_W // 2, 80, 26, GOLD, True)
        self._draw_text(surf, "Earn points by playing. Spend them on permanent upgrades!",
                        SCREEN_W // 2, 104, 18, TEXT_COLOR, True)

        y = 140
        for idx, item in enumerate(SHOP_ITEMS):
            lvl = self.upgrades[item['key']]
            cost = self.shop_cost(item)
            name = item['name']
            if lvl >= item['max']:
                status = "MAX"
                cost_text = "--"
            else:
                status = f"Lv {lvl}"
                cost_text = str(cost)
            color = (255, 210, 90) if idx == self.shop_sel else TEXT_COLOR
            row_bg = pygame.Surface((SCREEN_W - 120, 46), pygame.SRCALPHA)
            if idx == self.shop_sel:
                row_bg.fill((60, 60, 120, 60))
            else:
                row_bg.fill((30, 30, 60, 40))
            surf.blit(row_bg, (60, y))

            self._draw_text(surf, name, 70, y + 4, 22, color)
            self._draw_text(surf, f"{status}", 250, y + 4, 20, color)
            self._draw_text(surf, f"{cost_text} pts", 360, y + 4, 20,
                            (120, 255, 120) if idx == self.shop_sel else HUD_COLOR)
            self._draw_text(surf, item['desc'], 470, y + 6, 16, HUD_COLOR)
            y += 52

        self._draw_text(surf, "UP/DOWN: select    ENTER: buy    ESC: back",
                        SCREEN_W // 2, y + 8, 20, TEXT_COLOR, True)

    def draw_game_over(self, surf):
        self._draw_text(surf, "GAME OVER", SCREEN_W // 2, SCREEN_H // 2 - 80, 52, (255, 80, 80), True)
        self._draw_text(surf, f"FINAL SCORE: {self.score}", SCREEN_W // 2, SCREEN_H // 2 - 20, 30, TEXT_COLOR, True)
        self._draw_text(surf, f"HIGH SCORE: {self.high_score}", SCREEN_W // 2, SCREEN_H // 2 + 10, 26, COMBO_COLOR, True)
        if self.score >= self.high_score and self.score > 0:
            self._draw_text(surf, "NEW RECORD!", SCREEN_W // 2, SCREEN_H // 2 + 44, 26, (120, 255, 120), True)
        self._draw_text(surf, f"EARNED {self.score} META POINTS", SCREEN_W // 2, SCREEN_H // 2 + 70, 26, GOLD, True)
        self._draw_text(surf, "Spend them in the SHOP (S) for permanent upgrades!",
                        SCREEN_W // 2, SCREEN_H // 2 + 96, 20, TEXT_COLOR, True)
        self._draw_text(surf, "Press ENTER or SPACE to return to menu",
                        SCREEN_W // 2, SCREEN_H // 2 + 130, 22, TEXT_COLOR, True)

    def _overlay(self, surf, title, subtitle):
        s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 140))
        surf.blit(s, (0, 0))
        self._draw_text(surf, title, SCREEN_W // 2, SCREEN_H // 2 - 40, 44, TEXT_COLOR, True)
        self._draw_text(surf, subtitle, SCREEN_W // 2, SCREEN_H // 2 + 10, 22, TEXT_COLOR, True)

    def _draw_text(self, surf, text, x, y, size=24, color=TEXT_COLOR, center=False):
        font = pygame.font.Font(None, size)
        img = font.render(text, True, color)
        if center:
            x = x - img.get_width() // 2
        surf.blit(img, (x, y))


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Space Invaders — Meta-Progression Edition")
    clock = pygame.time.Clock()

    stats = load_stats()
    sound = SoundManager()
    game = Game(screen, sound, stats)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        result = game.handle_events()
        if result == 'quit':
            running = False
        else:
            game.update(dt)
            game.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
