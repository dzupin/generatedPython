# PROMPT USED:
# Write Space Invaders game in python using pygame library, make it visually appealing and polished but make sure to generate all graphic and sound files in python. Don't assume that user can download images and sound from internet, instead all resources for game should be generated in game. Also feel free to use external files (e.g. json) to store game parameters, progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Make sure to include in python generated sound and if possible also music, but music is optional.# Execution inststuction:
# COMMAND to execute Max:
# /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --parallel 1  --temp 1.0 --top_p 1.0 --chat-template-kwargs '{"reasoning_effort":"max"}'  --spec-type draft-dspark   --spec-draft-n-max 3 --fit off  -md /AI/models/dspark-DeepSeek-V4-Flash-0731-BF16.gguf  --model /AI/models/Huihui-DeepSeek-V4-Flash-Q2-0731.gguf
# MODELS used:
# /AI/models/dspark-DeepSeek-V4-Flash-0731-BF16.gguf   and  /AI/models/Huihui-DeepSeek-V4-Flash-Q2-0731.gguf
#STATS: 12.078 generated tokens, time elapsed  6min:38s  30.28 t/s


"""
Space Invaders (self-contained)
--------------------------------
- All graphics generated procedurally with pygame surfaces.
- All sounds AND music generated procedurally with numpy (no external files).
- Game parameters, progress, and stats stored in JSON files.
- Features: destructible barriers, multiple levels, bonus system,
  mystery ship, combo bonus, high-score persistence, pause, screens.
"""

import pygame
import pygame.gfxdraw
import numpy as np
import json, math, os, random, sys

# ------------------------------------------------------------------ #
#  CONFIGURATION (saved/loaded as JSON)
# ------------------------------------------------------------------ #
CONFIG_FILE = "space_invaders_config.json"
STATS_FILE = "space_invaders_stats.json"

DEFAULT_CONFIG = {
    "width": 800,
    "height": 600,
    "fps": 60,
    "player_speed": 6,
    "bullet_speed": 10,
    "alien_bullet_speed": 7,
    "alien_speed": 2.0,        # base speed (px per frame)
    "alien_drop": 24,          # drop distance when hitting edge
    "alien_rows": 5,           # starting rows
    "alien_cols": 10,
    "alien_fire_delay": 60,    # frames between alien shots (base)
    "barrier_count": 4,
    "barrier_width": 70,
    "barrier_height": 40,
    "lives": 3,
    "extra_life_score": 2000,  # every 2000 points -> extra life
    "mystery_delay": [360, 720],
    "mystery_speed": 3,
    "mystery_scores": [50, 100, 150, 200, 300],
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            cfg = {**DEFAULT_CONFIG, **cfg}
            return cfg
        except Exception:
            pass
    cfg = dict(DEFAULT_CONFIG)
    save_config(cfg)
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def load_stats():
    stats = {"high_score": 0, "games_played": 0, "total_score": 0,
             "total_kills": 0, "best_level": 1, "total_time": 0.0}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE) as f:
                stats.update(json.load(f))
        except Exception:
            pass
    return stats

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

# ------------------------------------------------------------------ #
#  AUDIO GENERATION (numpy -> pygame Sound)
# ------------------------------------------------------------------ #
SAMPLE_RATE = 44100

def make_tone(freq, duration, wave="square", vol=0.5, decay=True):
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n) / SAMPLE_RATE
    if wave == "square":
        w = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == "sine":
        w = np.sin(2 * np.pi * freq * t)
    elif wave == "saw":
        w = 2 * (t * freq - np.floor(0.5 + t * freq))
    elif wave == "triangle":
        w = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    else:  # noise
        w = np.random.uniform(-1, 1, n)

    env = np.exp(-6 * t) if decay else np.ones(n)
    attack = int(0.008 * SAMPLE_RATE)
    env[:attack] *= np.linspace(0, 1, attack)
    data = (w * env * vol * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(data)

def make_explosion(duration=0.25, vol=0.6):
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n) / SAMPLE_RATE
    noise = np.random.uniform(-1, 1, n)
    env = np.exp(-12 * t)
    # mix descending frequency
    freq = 400 * np.exp(-8 * t)
    tone = np.sign(np.sin(2 * np.pi * freq * t))
    data = (0.6 * noise * env + 0.4 * tone * env) * vol * 32767
    return pygame.sndarray.make_sound(data.astype(np.int16))

def make_noise(duration=0.15, vol=0.4):
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n) / SAMPLE_RATE
    noise = np.random.uniform(-1, 1, n)
    env = np.exp(-10 * t)
    data = (noise * env * vol * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(data)

# --- Music: a little looping chiptune melody ----------------------- #
def build_music(vol=0.35):
    # note frequencies (A minor pentatonic-ish, upbeat)
    seq = [
        (392, 0.15), (330, 0.15), (523, 0.3),
        (392, 0.15), (330, 0.15), (440, 0.3),
        (392, 0.15), (330, 0.15), (262, 0.15), (330, 0.3),
        (440, 0.15), (330, 0.15), (392, 0.4),
        (349, 0.15), (294, 0.15), (523, 0.3),
        (392, 0.15), (330, 0.15), (440, 0.4),
    ]
    parts = []
    for freq, dur in seq:
        n = int(SAMPLE_RATE * dur)
        t = np.arange(n) / SAMPLE_RATE
        w = np.sign(np.sin(2 * np.pi * freq * t))
        # gentle envelope so notes don't click
        env = np.ones(n)
        a = int(0.005 * SAMPLE_RATE); r = int(0.05 * SAMPLE_RATE)
        env[:a] *= np.linspace(0, 1, a)
        env[-r:] *= np.linspace(1, 0, r)
        # add a second harmonic for warmth
        w2 = 0.3 * np.sin(2 * np.pi * (freq * 2) * t)
        parts.append((w + w2) * env * vol)
    music = np.concatenate(parts)
    data = (music * 32767).astype(np.int16)
    # make it loop-friendly: return sound + duration
    snd = pygame.sndarray.make_sound(data)
    return snd, music.shape[0] / SAMPLE_RATE

# ------------------------------------------------------------------ #
#  GRAPHICS GENERATION
# ------------------------------------------------------------------ #
def make_background(w, h):
    bg = pygame.Surface((w, h))
    bg.fill((5, 8, 20))
    # gradient
    for y in range(h):
        t = y / h
        c = (int(5 + 8 * t), int(8 + 12 * t), int(20 + 40 * t))
        pygame.draw.line(bg, c, (0, y), (w, y))
    # stars
    for _ in range(220):
        x = random.randrange(w); y = random.randrange(h)
        r = random.choice([1, 1, 1, 2, 2, 3])
        bright = random.randrange(120, 255)
        col = (bright, bright, min(255, bright + 30))
        pygame.draw.circle(bg, col, (x, y), r)
    return bg

def make_alien_sprite(frame, color, size=24):
    s = pygame.Surface((size, size * 2), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    cx = size // 2
    top = size // 2
    # body
    body_c = color
    # draw classic invader using rects/polygons
    # head
    pygame.draw.polygon(s, body_c, [(cx - 4, top), (cx - 2, top - 4),
                                    (cx + 2, top - 4), (cx + 4, top)])
    # eyes
    pygame.draw.circle(s, (255, 255, 255), (cx - 3, top - 1), 2)
    pygame.draw.circle(s, (255, 255, 255), (cx + 3, top - 1), 2)
    pygame.draw.circle(s, (0, 0, 0), (cx - 3, top - 1), 1)
    pygame.draw.circle(s, (0, 0, 0), (cx + 3, top - 1), 1)
    # body (trapezoid)
    pygame.draw.polygon(s, body_c, [(cx - 6, top + 2), (cx + 6, top + 2),
                                    (cx + 8, top + 6), (cx - 8, top + 6)])
    # legs
    if frame == 0:
        pygame.draw.polygon(s, body_c, [(cx - 7, top + 7), (cx - 2, top + 7),
                                        (cx - 9, top + 12), (cx - 9, top + 14)])
        pygame.draw.polygon(s, body_c, [(cx + 7, top + 7), (cx + 2, top + 7),
                                        (cx + 9, top + 12), (cx + 9, top + 14)])
    else:
        pygame.draw.polygon(s, body_c, [(cx - 2, top + 7), (cx - 7, top + 7),
                                        (cx - 7, top + 14), (cx - 9, top + 14)])
        pygame.draw.polygon(s, body_c, [(cx + 2, top + 7), (cx + 7, top + 7),
                                        (cx + 7, top + 14), (cx + 9, top + 14)])
    # glow outline
    pygame.draw.polygon(s, (255, 255, 255), [(cx - 4, top), (cx - 2, top - 4),
                                             (cx + 2, top - 4), (cx + 4, top)], 1)
    return s

def make_player_sprite():
    s = pygame.Surface((40, 32), pygame.SRCALPHA)
    cx = 20
    # engine glow
    pygame.draw.circle(s, (255, 120, 40), (cx, 30), 6)
    pygame.draw.circle(s, (255, 60, 20), (cx, 30), 3)
    # gun
    pygame.draw.rect(s, (150, 220, 255), (cx - 2, 2, 4, 12))
    # body (trapezoid)
    pygame.draw.polygon(s, (60, 200, 255), [(cx - 14, 26), (cx + 14, 26),
                                            (cx + 8, 10), (cx - 8, 10)])
    pygame.draw.polygon(s, (120, 240, 255), [(cx - 10, 26), (cx + 10, 26),
                                             (cx + 6, 12), (cx - 6, 12)])
    # wing tips
    pygame.draw.polygon(s, (40, 160, 220), [(cx - 20, 26), (cx - 10, 26),
                                            (cx - 14, 12)])
    pygame.draw.polygon(s, (40, 160, 220), [(cx + 20, 26), (cx + 10, 26),
                                            (cx + 14, 12)])
    # cockpit
    pygame.draw.circle(s, (200, 255, 255), (cx, 14), 3)
    return s

def make_mystery_ship():
    s = pygame.Surface((30, 20), pygame.SRCALPHA)
    cx = 15
    pygame.draw.polygon(s, (255, 60, 60), [(cx - 12, 8), (cx + 12, 8),
                                           (cx + 7, 16), (cx - 7, 16)])
    pygame.draw.polygon(s, (255, 160, 60), [(cx - 8, 8), (cx + 8, 8),
                                            (cx + 6, 15), (cx - 6, 15)])
    pygame.draw.circle(s, (255, 255, 0), (cx - 4, 11), 2)
    pygame.draw.circle(s, (255, 255, 0), (cx + 4, 11), 2)
    pygame.draw.rect(s, (255, 220, 120), (cx - 2, 0, 4, 8))
    return s

def make_bullet_sprite():
    s = pygame.Surface((6, 16), pygame.SRCALPHA)
    pygame.draw.rect(s, (200, 255, 255), (1, 0, 4, 16))
    pygame.draw.rect(s, (255, 255, 255), (2, 0, 2, 16))
    pygame.draw.circle(s, (255, 255, 255), (3, 0), 2)
    return s

def make_alien_bullet_sprite():
    s = pygame.Surface((8, 14), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 80, 80), (4, 2), 3)
    pygame.draw.rect(s, (255, 120, 120), (1, 4, 6, 8))
    pygame.draw.circle(s, (255, 200, 200), (4, 12), 2)
    return s

def make_barrier_brick(c):
    s = pygame.Surface((5, 5), pygame.SRCALPHA)
    pygame.draw.rect(s, c, (0, 0, 5, 5))
    pygame.draw.rect(s, (c[0] + 40, c[1] + 40, c[2] + 40), (0, 0, 5, 1))
    return s

def make_ui_font(size):
    return pygame.font.Font(None, size)

# ------------------------------------------------------------------ #
#  GAME
# ------------------------------------------------------------------ #
class SpaceInvaders:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
        pygame.init()
        self.cfg = load_config()
        self.stats = load_stats()
        self.W = self.cfg["width"]
        self.H = self.cfg["height"]
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        # sounds
        self.snd_shoot = make_tone(700, 0.06, "square", 0.35)
        self.snd_invader = make_tone(320, 0.12, "square", 0.35)
        self.snd_hit = make_tone(200, 0.1, "saw", 0.4)
        self.snd_explosion = make_explosion(0.3, 0.5)
        self.snd_mystery = make_tone(150, 0.5, "saw", 0.4, decay=False)
        self.snd_levelup = make_tone(520, 0.2, "triangle", 0.5)
        self.snd_life = make_tone(900, 0.25, "sine", 0.5)
        self.snd_gameover = make_tone(120, 0.8, "saw", 0.5)
        self.music, self.music_len = build_music(0.3)
        self.music_chan = pygame.mixer.find_channel()
        self.music_chan.play(self.music, loops=-1)

        # graphics
        self.bg = make_background(self.W, self.H)
        self.player_spr = make_player_sprite()
        self.mystery_spr = make_mystery_ship()
        self.bullet_spr = make_bullet_sprite()
        self.ab_spr = make_alien_bullet_sprite()
        # alien colors per row (cooler palette)
        self.alien_colors = [(230, 80, 80), (230, 160, 60),
                             (180, 90, 220), (90, 200, 230),
                             (160, 220, 160)]
        self.alien_frames = [make_alien_sprite(f, (255, 255, 255), 24)
                             for f in range(2)]
        # tint alien frames per row
        self.alien_sprs = []
        for color in self.alien_colors:
            f0 = make_alien_sprite(0, color)
            f1 = make_alien_sprite(1, color)
            self.alien_sprs.append([f0, f1])

        self.brick_light = make_barrier_brick((80, 200, 120))
        self.brick_dark = make_barrier_brick((50, 130, 80))

        self.font_small = make_ui_font(22)
        self.font_mid = make_ui_font(34)
        self.font_big = make_ui_font(64)

        self.reset()
        self.state = "menu"   # menu | playing | gameover | paused
        self.menu_t = 0.0

    # --------------------------------------------------------------- #
    def reset(self):
        c = self.cfg
        self.score = 0
        self.lives = c["lives"]
        self.level = 1
        self.kills = 0
        self.combo = 0
        self.combo_timer = 0
        self.player = pygame.Rect(c["width"] // 2 - 20, c["height"] - 70, 40, 32)
        self.bullets = []          # player bullets
        self.ab_bullets = []       # alien bullets
        self.barriers = []
        self.make_barriers()
        self.mystery = None
        self.mystery_timer = random.randint(c["mystery_delay"][0],
                                            c["mystery_delay"][1])
        self.make_aliens()
        self.alien_dir = 1
        self.alien_frame = 0
        self.alien_anim = 0
        self.fire_timer = 0
        self.effects = []          # particles / text floats
        self.flash = 0
        self.shake = 0
        self.time_playing = 0.0

    def make_barriers(self):
        c = self.cfg
        n = c["barrier_count"]
        bw = c["barrier_width"]
        bh = c["barrier_height"]
        y = self.H - 110
        spacing = self.W // (n + 1)
        for i in range(n):
            x = spacing * (i + 1) - bw // 2
            bricks = []
            cols = bw // 5
            rows = bh // 5
            for r in range(rows):
                for col in range(cols):
                    # make shape look like a wall (leave holes)
                    if r < 2 and col < 3:
                        continue
                    if r == rows - 1 and col < 4:
                        continue
                    bricks.append([x + col * 5, y + r * 5, 5, 5, True])
            self.barriers.append(bricks)

    def make_aliens(self):
        c = self.cfg
        rows = min(c["alien_rows"] + self.level - 1, 7)
        cols = c["alien_cols"]
        y0 = 60
        self.aliens = []
        for r in range(rows):
            for col in range(cols):
                x = 60 + col * 50
                y = y0 + r * 45
                self.aliens.append([x, y, r, True])
        self.alien_speed = c["alien_speed"] * (1 + 0.12 * (self.level - 1))
        self.alien_fire = max(12, c["alien_fire_delay"] - 4 * (self.level - 1))

    # --------------------------------------------------------------- #
    def update(self):
        dt = 1.0 / self.cfg["fps"]
        self.time_playing += dt

        # anim counters
        self.alien_anim += 1
        self.alien_frame = (self.alien_anim // 8) % 2
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        self.update_effects(dt)
        self.update_mystery()
        self.update_aliens()
        self.update_bullets()
        self.update_firing()
        self.check_collisions()

        # player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.x -= self.cfg["player_speed"]
        if keys[pygame.K_RIGHT]:
            self.player.x += self.cfg["player_speed"]
        self.player.x = max(0, min(self.W - self.player.width, self.player.x))

        if self.flash > 0:
            self.flash -= dt
        if self.shake > 0:
            self.shake -= dt

    def update_aliens(self):
        # determine if any alien at edge -> drop & reverse
        minx = min([a[0] for a in self.aliens if a[3]], default=9999)
        maxx = max([a[0] for a in self.aliens if a[3]], default=-9999)
        if maxx >= self.W - 40 or minx <= 40:
            self.alien_dir *= -1
            for a in self.aliens:
                if a[3]:
                    a[1] += self.cfg["alien_drop"]
        for a in self.aliens:
            if a[3]:
                a[0] += self.alien_dir * self.alien_speed

        # game over if aliens reach bottom
        if any(a[1] >= self.H - 40 for a in self.aliens if a[3]):
            self.end_game()

    def update_bullets(self):
        c = self.cfg
        # player bullets move up
        for b in self.bullets:
            b[1] -= c["bullet_speed"]
        self.bullets = [b for b in self.bullets if b[1] > 0]

        # alien bullets move down
        for b in self.ab_bullets:
            b[1] += c["alien_bullet_speed"]
        self.ab_bullets = [b for b in self.ab_bullets if b[1] < self.H]

    def update_firing(self):
        # alien fire
        self.fire_timer += 1
        if self.fire_timer >= self.alien_fire and self.aliens:
            alive = [a for a in self.aliens if a[3]]
            if alive:
                shooter = random.choice(alive)
                x = shooter[0] + 12
                y = shooter[1] + 34
                self.ab_bullets.append([x, y])
                self.fire_timer = 0
        # mystery ship
        if self.mystery:
            self.mystery[0] += self.cfg["mystery_speed"]
            if self.mystery[0] > self.W + 40:
                self.mystery = None

    def update_mystery(self):
        if not self.mystery:
            self.mystery_timer -= 1
            if self.mystery_timer <= 0:
                y = 30
                x = -40 if random.random() < 0.5 else self.W + 40
                self.mystery = [x, y, random.choice(self.cfg["mystery_scores"])]
                self.snd_mystery.play()
                self.mystery_timer = random.randint(
                    self.cfg["mystery_delay"][0], self.cfg["mystery_delay"][1])

    def check_collisions(self):
        # player bullets vs aliens
        new_bullets = []
        for b in self.bullets:
            hit = False
            bx, by = b
            for a in self.aliens:
                if not a[3]:
                    continue
                if bx + 6 > a[0] and bx < a[0] + 40 and by + 16 > a[1] and by < a[1] + 40:
                    a[3] = False
                    hit = True
                    self.kills += 1
                    # combo bonus
                    self.combo += 1
                    self.combo_timer = 2.0
                    pts = 10 * self.combo
                    self.score += pts
                    self.add_effect((bx, by), "+%d" % pts, (255, 255, 120))
                    self.add_particles(bx + 6, by + 8, (200, 80, 80), 12)
                    self.snd_hit.play()
                    self.flash = 0.08
                    self.shake = 0.1
                    if not any(a[3] for a in self.aliens):
                        self.level_up()
                    break
            if not hit:
                new_bullets.append(b)
        self.bullets = new_bullets

        # bullets vs barriers (both sides)
        self.bullets = self.collide_barriers(self.bullets, True)
        self.ab_bullets = self.collide_barriers(self.ab_bullets, False)

        # alien bullets vs player
        pr = self.player
        new_ab = []
        for b in self.ab_bullets:
            bx, by = b
            if bx + 8 > pr.x and bx < pr.x + pr.width and by + 14 > pr.y and by < pr.y + pr.height:
                self.lose_life()
            else:
                new_ab.append(b)
        self.ab_bullets = new_ab

        # player bullets vs mystery ship
        if self.mystery:
            mx, my, mscore = self.mystery
            for b in self.bullets:
                if b[0] + 6 > mx and b[0] < mx + 30 and b[1] + 16 > my and b[1] < my + 20:
                    self.score += mscore
                    self.add_effect((mx, my), "+%d" % mscore, (255, 120, 120))
                    self.add_particles(mx + 15, my + 10, (255, 60, 60), 10)
                    self.snd_explosion.play()
                    self.mystery = None
                    break

    def collide_barriers(self, bullets, is_player):
        result = []
        for b in bullets:
            bx, by = b
            destroyed = False
            for brk in self.barriers:
                for cell in brk:
                    if not cell[4]:
                        continue
                    if bx + 6 > cell[0] and bx < cell[0] + cell[3] and \
                       by + 16 > cell[1] and by < cell[1] + cell[2]:
                        cell[4] = False
                        # remove a few neighbors for chunk damage
                        destroyed = True
                        self.add_particles(bx + 3, by + 8, (120, 200, 160), 4)
                        break
                if destroyed:
                    break
            if not destroyed:
                result.append(b)
        return result

    def lose_life(self):
        self.lives -= 1
        self.add_particles(self.player.centerx, self.player.centery,
                           (200, 200, 255), 18)
        self.snd_explosion.play()
        self.shake = 0.4
        self.flash = 0.2
        if self.lives <= 0:
            self.end_game()
        else:
            self.snd_life.play()

    def level_up(self):
        self.level += 1
        self.score += 500 + 100 * self.level
        self.add_effect((self.W // 2, 120), "LEVEL %d" % self.level,
                        (120, 255, 120), big=True)
        self.snd_levelup.play()
        self.make_aliens()
        self.make_barriers()
        self.bullets.clear()
        self.ab_bullets.clear()
        self.flash = 0.15

    def end_game(self):
        self.snd_gameover.play()
        self.state = "gameover"
        # update stats
        self.stats["games_played"] += 1
        self.stats["total_score"] += self.score
        self.stats["total_kills"] += self.kills
        self.stats["best_level"] = max(self.stats["best_level"], self.level)
        self.stats["high_score"] = max(self.stats["high_score"], self.score)
        self.stats["total_time"] += self.time_playing
        save_stats(self.stats)

    # --------------------------------------------------------------- #
    def add_effect(self, pos, text, color, big=False):
        self.effects.append({
            "pos": pos, "text": text, "color": color,
            "life": 1.2 if not big else 2.0, "big": big, "vy": -1})

    def add_particles(self, x, y, color, n):
        for _ in range(n):
            ang = random.uniform(0, math.pi * 2)
            sp = random.uniform(1, 6)
            self.effects.append({
                "type": "particle", "pos": [x, y],
                "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp,
                "color": color, "life": random.uniform(0.4, 0.9),
                "size": random.randint(2, 5)})

    def update_effects(self, dt):
        for e in self.effects:
            e["life"] -= dt
            if e.get("type") == "particle":
                e["pos"][0] += e["vx"] * dt * 60
                e["pos"][1] += e["vy"] * dt * 60
            else:
                e["pos"] = (e["pos"][0], e["pos"][1] + e["vy"] * dt * 60)
        self.effects = [e for e in self.effects if e["life"] > 0]

    # --------------------------------------------------------------- #
    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        s = self.screen

        # shake effect
        if self.shake > 0:
            ox = random.randint(-3, 3)
            oy = random.randint(-3, 3)
            s.blit(self.screen, (ox, oy))  # simple re-draw offset below
        # (we draw everything on screen then offset at the end if shake)

        # barriers
        for brk in self.barriers:
            for cell in brk:
                if cell[4]:
                    s.blit(self.brick_light, (cell[0], cell[1]))
                else:
                    s.blit(self.brick_dark, (cell[0], cell[1]))

        # aliens
        for a in self.aliens:
            if a[3]:
                row = a[2]
                spr = self.alien_sprs[min(row, len(self.alien_sprs) - 1)][self.alien_frame]
                s.blit(spr, (a[0], a[1]))

        # mystery ship
        if self.mystery:
            s.blit(self.mystery_spr, (self.mystery[0], self.mystery[1]))

        # bullets
        for b in self.bullets:
            s.blit(self.bullet_spr, (b[0], b[1]))
        for b in self.ab_bullets:
            s.blit(self.ab_spr, (b[0], b[1]))

        # player
        s.blit(self.player_spr, (self.player.x, self.player.y))

        # particles / effects
        for e in self.effects:
            if e.get("type") == "particle":
                pygame.draw.circle(s, e["color"], (int(e["pos"][0]),
                                                   int(e["pos"][1])),
                                   e["size"])
            else:
                f = self.font_big if e.get("big") else self.font_mid
                txt = f.render(e["text"], True, e["color"])
                a = int(255 * (e["life"] / 1.2))
                txt.set_alpha(max(0, min(255, a)))
                s.blit(txt, (int(e["pos"][0]) - txt.get_width() // 2,
                             int(e["pos"][1]) - txt.get_height() // 2))

        # HUD
        self.draw_hud()

        # flash overlay
        if self.flash > 0:
            ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            ov.fill((255, 255, 255, int(120 * (self.flash / 0.15))))
            s.blit(ov, (0, 0))

    def draw_hud(self):
        s = self.screen
        # score
        t = self.font_small.render("SCORE %d" % self.score, True, (255, 255, 255))
        s.blit(t, (10, 10))
        # level
        t = self.font_small.render("LEVEL %d" % self.level, True, (120, 255, 120))
        s.blit(t, (self.W // 2 - 40, 10))
        # lives
        for i in range(self.lives):
            s.blit(self.player_spr, (10 + i * 45, 40))
        # combo
        if self.combo >= 3 and self.combo_timer > 0:
            t = self.font_mid.render("COMBO x%d" % self.combo, True,
                                     (255, 200, 80))
            s.blit(t, (self.W - 180, 10))
        # high score
        t = self.font_small.render("BEST %d" % self.stats["high_score"],
                                   True, (255, 200, 200))
        s.blit(t, (self.W - 120, 50))

    def draw_menu(self):
        self.screen.blit(self.bg, (0, 0))
        s = self.screen
        title = self.font_big.render("SPACE INVADERS", True, (120, 220, 255))
        s.blit(title, (self.W // 2 - title.get_width() // 2, 120))
        sub = self.font_mid.render("All graphics & audio generated in Python",
                                   True, (200, 200, 200))
        s.blit(sub, (self.W // 2 - sub.get_width() // 2, 200))
        # animated alien parade
        for i in range(5):
            spr = self.alien_sprs[i][self.alien_frame]
            x = self.W // 2 - 120 + i * 50
            y = 300 + math.sin(self.menu_t * 2 + i) * 6
            s.blit(spr, (x, y))
        info = self.font_small.render(
            "Press SPACE / ENTER to start   |   P to pause   |   ESC to quit",
            True, (255, 255, 255))
        s.blit(info, (self.W // 2 - info.get_width() // 2, self.H - 60))
        hi = self.font_mid.render("HIGH SCORE: %d" % self.stats["high_score"],
                                  True, (255, 220, 100))
        s.blit(hi, (self.W // 2 - hi.get_width() // 2, 380))
        games = self.font_small.render(
            "Games played: %d   Best level: %d" %
            (self.stats["games_played"], self.stats["best_level"]),
            True, (180, 180, 180))
        s.blit(games, (self.W // 2 - games.get_width() // 2, 420))
        self.menu_t += 1 / self.cfg["fps"]

    def draw_gameover(self):
        self.draw()
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        self.screen.blit(ov, (0, 0))
        s = self.screen
        t = self.font_big.render("GAME OVER", True, (255, 80, 80))
        s.blit(t, (self.W // 2 - t.get_width() // 2, 150))
        sc = self.font_mid.render("Final Score: %d" % self.score,
                                  True, (255, 255, 255))
        s.blit(sc, (self.W // 2 - sc.get_width() // 2, 240))
        lv = self.font_small.render("Reached Level %d" % self.level,
                                    True, (200, 200, 200))
        s.blit(lv, (self.W // 2 - lv.get_width() // 2, 300))
        if self.score >= self.stats["high_score"] and self.score > 0:
            t = self.font_mid.render("NEW HIGH SCORE!", True, (255, 220, 100))
            s.blit(t, (self.W // 2 - t.get_width() // 2, 340))
        msg = self.font_small.render("Press SPACE to play again, ESC to quit",
                                     True, (255, 255, 255))
        s.blit(msg, (self.W // 2 - msg.get_width() // 2, self.H - 60))

    def draw_paused(self):
        self.draw()
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        self.screen.blit(ov, (0, 0))
        t = self.font_big.render("PAUSED", True, (200, 200, 255))
        self.screen.blit(t, (self.W // 2 - t.get_width() // 2, 200))

    # --------------------------------------------------------------- #
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.cfg["fps"]) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            self.reset()
                            self.state = "playing"
                            self.music_chan.play(self.music, loops=-1)
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    elif self.state == "playing":
                        if event.key == pygame.K_SPACE:
                            self.fire()
                        elif event.key == pygame.K_p:
                            self.state = "paused"
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    elif self.state == "paused":
                        if event.key == pygame.K_p:
                            self.state = "playing"
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    elif self.state == "gameover":
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            self.reset()
                            self.state = "playing"
                            self.music_chan.play(self.music, loops=-1)
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            if self.state == "playing":
                self.update()
                self.draw()
            elif self.state == "menu":
                self.draw_menu()
            elif self.state == "paused":
                self.draw_paused()
            elif self.state == "gameover":
                self.draw_gameover()

            pygame.display.flip()

        pygame.quit()

    def fire(self):
        if len(self.bullets) < 4:
            x = self.player.centerx - 3
            y = self.player.y - 16
            self.bullets.append([x, y])
            self.snd_shoot.play()

def main():
    # silence numpy warnings
    import warnings
    warnings.simplefilter("ignore")
    g = SpaceInvaders()
    g.run()

if __name__ == "__main__":
    main()






