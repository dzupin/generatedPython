# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

#  /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --temp 1.0 --top_p 0.95 --top_k 20 --min_p 0.0 --repeat-penalty 1.0 --presence-penalty 0.0  --spec-type draft-mtp --spec-draft-n-max 7 --chat-template-kwargs '{"reasoning_effort": "xhigh"}' --image-min-tokens 1024 --reasoning-preserve --parallel 1  --model /AI/models/Qwen3.8-27B-UD-Q6_K_XL.gguf  --mmproj /AI/models/mmproj-Qwen3.8-27B-BF16.gguf


"""
SPACE INVADERS - deluxe addictive edition. Zero external asset files.

All sprites are pixel art built in code, all sounds are synthesized from
raw PCM data at startup.  Persistence (allowed external files):

    si_stats.json          lifetime stats + unlocked achievements
    si_save.json           snapshot of the current run (for "Continue")
    si_barrier_0..3.png    pixel-damaged barriers, saved with the run
    si_config.json         settings (mute)

Run:   python space_invaders.py          (needs: pip install pygame)

Controls:  Arrows/A-D move - Space fire - P pause - M mute - C continue
           Enter start/confirm - Esc menu/quit (auto-saves)
"""

import array
import json
import math
import os
import random
import sys
import time

import pygame

# ------------------------------------------------------------------ basics
W, H = 800, 600
FPS = 60
HUD_H = 40
SAMPLE_RATE = 22050
SCALE = 3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_FILE = os.path.join(BASE_DIR, "si_stats.json")
SAVE_FILE = os.path.join(BASE_DIR, "si_save.json")
CONFIG_FILE = os.path.join(BASE_DIR, "si_config.json")
BARRIER_FILES = [os.path.join(BASE_DIR, f"si_barrier_{i}.png") for i in range(4)]
BARRIER_X = [69, 269, 469, 669]
BARRIER_Y = H - 128

WHITE   = (235, 242, 255)
CYAN    = (0, 235, 230)
GREEN   = (80, 235, 130)
MAGENTA = (255, 95, 205)
LIME    = (150, 235, 70)
ORANGE  = (255, 170, 45)
YELLOW  = (255, 225, 60)
RED     = (255, 75, 75)
BLUE    = (110, 170, 255)
GOLD    = (255, 210, 60)
BARRIER_C = (60, 220, 130)

THEMES = [CYAN, GREEN, MAGENTA, ORANGE, BLUE, YELLOW, LIME]

MIXER_OK = False
SFX = {}
ALIEN_SURFS = []
SHIP_SURF = None
SHIP_SMALL = None
UFO_SURFS = ()
BULLET_P = None
BULLET_A = None

# ------------------------------------------------------------- pixel art
SHIP_ART = [
    "......#......",
    ".....###.....",
    ".....###.....",
    "#############",
    "##.#######.##",
    "#############",
]

SQUID_A = ["...##...", "..####..", ".######.", "##o##o##",
           "########", ".#.##.#.", "#.#..#.#", "..#..#.."]
SQUID_B = ["...##...", "..####..", ".######.", "##o##o##",
           "########", "..#..#..", ".#.##.#.", "#.#..#.#"]
CRAB_A = ["..#.....#..", ".#.......#.", "###.###.###", "###########",
          "#.o###o.#..", "#.#.....#..", "#...#.#...#", ".#.....#..."]
CRAB_B = ["..#.....#..", ".#.......#.", "###.###.###", "###########",
          "#.o###o.#..", "..#.....#..", ".##..#..##.", ".#......#.."]
OCTO_A = ["...######...", "..########..", ".##########.", "###oo##oo###",
          "############", "..###..###..", ".##......##.", "##........##"]
OCTO_B = ["...######...", "..########..", ".##########.", "###oo##oo###",
          "############", "...##..##...", "..###..###..", ".##......##."]
UFO_ART = [".....###.....", "..#########..", ".############",
           "##o###o###o##", "..##.....##.."]

BOSS_A = ["...##############...", "..################..", ".##################.",
          "####################", "####################", "##o##############o##",
          "####################", "####################", ".###.########.###...",
          "##..##..##..##......"]
BOSS_B = ["...##############...", "..################..", ".##################.",
          "####################", "####################", "#o##############o###",
          "####################", "####################", ".####.######.####...",
          "..##..##..##..##...."]

ALIEN_DEFS = [
    (MAGENTA, [SQUID_A, SQUID_B], 30),
    (LIME,    [CRAB_A,  CRAB_B],  20),
    (CYAN,    [OCTO_A,  OCTO_B],  10),
]

POWER_KINDS = {
    "D": dict(label="DOUBLE SHOT", color=CYAN),
    "R": dict(label="RAPID FIRE",  color=ORANGE),
    "M": dict(label="2X SCORE",    color=YELLOW),
    "S": dict(label="SHIELD",      color=GREEN),
    "L": dict(label="EXTRA SHIP",  color=WHITE),
}
POWER_WEIGHTS = [30, 25, 20, 15, 10]
PU_LETTER = {"D": "D", "R": "R", "M": "2X", "S": "S", "L": "+"}

ACH = {
    "first_blood": "FIRST BLOOD",
    "combo10":     "KILLER INSTINCT",
    "wave5":       "VETERAN",
    "wave10":      "ELITE WARRIOR",
    "boss":        "BOSS HUNTER",
    "rich":        "25K IN A RUN",
    "near20":      "SPLIT SECOND",
    "gold":        "GOLD RUSH",
}

# ----------------------------------------------------------------- utils
def build_sprite(rows, color, accent=WHITE, scale=SCALE):
    w = max(len(r) for r in rows)
    s = pygame.Surface((w * scale, len(rows) * scale), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                s.fill(color, (x * scale, y * scale, scale, scale))
            elif ch == "o":
                s.fill(accent, (x * scale, y * scale, scale, scale))
    return s


def make_barrier_surface():
    s = pygame.Surface((62, 40), pygame.SRCALPHA)
    pygame.draw.rect(s, BARRIER_C, (0, 0, 62, 40), border_radius=7)
    pygame.draw.rect(s, (150, 255, 195), (4, 2, 54, 4), border_radius=2)
    pygame.draw.rect(s, (0, 0, 0, 0), (24, 18, 14, 22))
    pygame.draw.rect(s, (0, 0, 0, 0), (0, 27, 9, 13))
    pygame.draw.rect(s, (0, 0, 0, 0), (53, 27, 9, 13))
    return s


_font_cache = {}


def get_font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(None, size)
        _font_cache[size] = f
    return f


def render_text(s, size, color=WHITE, scale=1):
    surf = get_font(size).render(s, True, color)
    if scale != 1:
        surf = pygame.transform.scale(surf, (surf.get_width() * scale,
                                             surf.get_height() * scale))
    return surf


def glow_text(s, size, color, glow, scale=1):
    f = get_font(size)
    main = f.render(s, True, color)
    if scale != 1:
        main = pygame.transform.scale(main, (main.get_width() * scale,
                                             main.get_height() * scale))
    g = f.render(s, True, glow)
    gw, gh = g.get_width(), g.get_height()
    blur = pygame.transform.smoothscale(g, (max(1, gw // 3), max(1, gh // 3)))
    blur = pygame.transform.scale(blur, (gw + 24, gh + 24))
    out = pygame.Surface((gw + 24, gh + 24), pygame.SRCALPHA)
    out.blit(blur, (0, 0))
    out.blit(main, ((gw + 24 - main.get_width()) // 2,
                    (gh + 24 - main.get_height()) // 2))
    return out

# ------------------------------------------------------ synthesized sound
class _DummySound:
    def play(self, *a, **k): pass
    def set_volume(self, v): pass


def _tone(freq, dur, wave="square", vol=1.0, f_end=None, attack=0.004):
    n = int(SAMPLE_RATE * dur)
    out, phase, atk = [], 0.0, max(1, int(SAMPLE_RATE * attack))
    for i in range(n):
        f = freq if f_end is None else freq + (f_end - freq) * (i / n)
        phase += f / SAMPLE_RATE
        p = phase - int(phase)
        if wave == "square":
            s = 1.0 if p < 0.5 else -1.0
        elif wave == "saw":
            s = 2.0 * p - 1.0
        elif wave == "tri":
            s = 4.0 * abs(p - 0.5) - 1.0
        else:
            s = math.sin(2.0 * math.pi * p)
        env = min(1.0, i / atk) * (1.0 - i / n) ** 1.5
        out.append(s * vol * env)
    return out


def _noise(dur, vol=1.0, decay=2.0):
    n = int(SAMPLE_RATE * dur)
    return [(random.random() * 2 - 1) * vol * (1 - i / n) ** decay for i in range(n)]


def _mix(*parts):
    n = max(len(p) for p in parts)
    out = [0.0] * n
    for p in parts:
        for i, v in enumerate(p):
            out[i] += v
    return out


def _seq(*parts, gap=0.0):
    g = int(SAMPLE_RATE * gap)
    out = []
    for p in parts:
        out.extend(p)
        out.extend([0.0] * g)
    return out


def _sound(samples, vol=0.5):
    if not MIXER_OK:
        return _DummySound()
    try:
        freq, size, ch = pygame.mixer.get_init()
        buf = array.array("h")
        offset = 32768 if size > 0 else 0
        for s in samples:
            v = int(max(-1.0, min(1.0, s * vol)) * 32767) + offset
            if ch == 1:
                buf.append(v)
            else:
                buf.append(v); buf.append(v)
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception:
        return _DummySound()


def build_sounds():
    global SFX
    SFX = {
        "shoot":     _sound(_tone(880, 0.14, "square", 0.5, f_end=180), 0.35),
        "invader":   _sound(_mix(_noise(0.18, 0.8, 2.5), _tone(320, 0.12, "saw", 0.3, f_end=60)), 0.5),
        "chip":      _sound(_noise(0.08, 0.5, 3.0), 0.35),
        "explode":   _sound(_mix(_noise(0.55, 1.0, 1.6), _tone(160, 0.5, "saw", 0.5, f_end=40),
                                 _tone(70, 0.6, "tri", 0.5, f_end=30)), 0.7),
        "step0":     _sound(_tone(120, 0.09, "square", 0.6), 0.30),
        "step1":     _sound(_tone(112, 0.09, "square", 0.6), 0.30),
        "step2":     _sound(_tone(104, 0.09, "square", 0.6), 0.30),
        "step3":     _sound(_tone(96, 0.09, "square", 0.6), 0.30),
        "power":     _sound(_seq(_tone(440, 0.06, "square", 0.5), _tone(554, 0.06, "square", 0.5),
                                 _tone(659, 0.06, "square", 0.5), _tone(880, 0.10, "square", 0.55), gap=0.02), 0.45),
        "extra":     _sound(_seq(_tone(523, 0.08, "square", 0.5), _tone(659, 0.08, "square", 0.5),
                                 _tone(784, 0.08, "square", 0.5), _tone(1046, 0.18, "square", 0.55), gap=0.03), 0.5),
        "shield":    _sound(_tone(1500, 0.22, "sine", 0.6, f_end=300), 0.4),
        "bonus":     _sound(_seq(_tone(1200, 0.05, "square", 0.5), _tone(1600, 0.07, "square", 0.5), gap=0.02), 0.4),
        "bonus_hit": _sound(_seq(_tone(880, 0.06, "square", 0.5), _tone(1174, 0.06, "square", 0.5),
                                 _tone(1568, 0.12, "square", 0.55), gap=0.03), 0.5),
        "clear":     _sound(_seq(_tone(523, 0.09, "square", 0.5), _tone(659, 0.09, "square", 0.5),
                                 _tone(784, 0.09, "square", 0.5), _tone(1046, 0.20, "square", 0.55), gap=0.04), 0.5),
        "select":    _sound(_tone(700, 0.06, "square", 0.4), 0.3),
        "lose":      _sound(_seq(_tone(392, 0.15, "square", 0.5), _tone(330, 0.15, "square", 0.5),
                                 _tone(262, 0.30, "square", 0.55), gap=0.08), 0.5),
        "whoosh":    _sound(_mix(_tone(1400, 0.09, "sine", 0.3, f_end=500), _noise(0.08, 0.15, 3.0)), 0.3),
        "boss_hit":  _sound(_mix(_tone(180, 0.08, "square", 0.6, f_end=70), _noise(0.05, 0.4, 3.0)), 0.5),
        "boss_dead": _sound(_mix(_noise(0.8, 1.0, 1.4), _tone(90, 0.7, "saw", 0.6, f_end=28),
                                 _tone(523, 0.5, "sine", 0.3, f_end=1568)), 0.7),
        "achieve":   _sound(_seq(_tone(988, 0.07, "sine", 0.5), _tone(1319, 0.14, "sine", 0.5), gap=0.05), 0.45),
        "combo_up":  _sound(_tone(700, 0.08, "square", 0.5, f_end=1500), 0.4),
        "frenzy":    _sound(_seq(_tone(600, 0.08, "saw", 0.4, f_end=950), _tone(500, 0.11, "saw", 0.4, f_end=820), gap=0.05), 0.4),
    }

# ------------------------------------------------------------ entities
class Star:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.size = random.choice((1, 1, 1, 2))
        self.speed = random.uniform(6, 26)
        self.tw = random.uniform(1.5, 4.0)
        self.ph = random.uniform(0, math.tau)


class Particle:
    def __init__(self, x, y, vx, vy, life, color, size=3):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max_life = life
        self.color, self.size = color, size


class Popup:
    def __init__(self, x, y, text, color, big=False):
        self.x, self.y = x, y
        self.color = color
        self.surf = glow_text(text, 30, color, color) if big else render_text(text, 20, color)
        self.life = self.dur = 1.2


class Flash:
    def __init__(self, x, y, max_t, color):
        self.x, self.y, self.t, self.max_t, self.color = x, y, 0.0, max_t, color


class Bullet:
    __slots__ = ("x", "y", "vx", "vy", "friendly", "rewarded")

    def __init__(self, x, y, vy, friendly, vx=0.0):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.friendly, self.rewarded = friendly, False

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 2, int(self.y), 5, 12)

    @property
    def tip(self):
        return (self.x, self.y) if self.friendly else (self.x, self.y + 12)


SPX, SPY = 44, 34


class Invader:
    __slots__ = ("row", "col", "type", "alive", "gold", "w", "h")

    def __init__(self, row, col, itype):
        self.row, self.col, self.type, self.alive = row, col, itype, True
        self.gold = False
        self.w = ALIEN_SURFS[itype][0].get_width()
        self.h = ALIEN_SURFS[itype][0].get_height()

    def rect(self, ox, oy):
        return pygame.Rect(ox + self.col * SPX + (SPX - self.w) // 2,
                           oy + self.row * SPY, self.w, self.h)


class InvaderGrid:
    def __init__(self, boss_wave=False):
        self.ox, self.oy, self.dir, self.frame = 0, 0, 1, 0
        self.invaders = []
        self.x0 = (W - 10 * SPX) // 2
        self.y0 = 128 if boss_wave else 88
        for r in range(5):
            t = 0 if r == 0 else (1 if r < 3 else 2)
            for c in range(11):
                self.invaders.append(Invader(r, c, t))

    def alive(self):
        return [i for i in self.invaders if i.alive]

    def step(self):
        dx = 10 * self.dir
        for inv in self.alive():
            r = inv.rect(self.ox + dx, self.oy)
            if r.x < 14 or r.right > W - 14:
                self.dir *= -1
                self.oy += 16
                break
        else:
            self.ox += dx
        self.frame ^= 1

    def step_interval(self, level):
        a, total = len(self.alive()), len(self.invaders)
        prog = 1.0 - a / total
        base = max(0.055, 0.34 - 0.033 * (level - 1))
        iv = base * (1.0 - 0.65 * prog)
        if a <= 5:
            iv *= 0.55
        return iv


class Barrier:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.surf = make_barrier_surface()
        self.w, self.h = self.surf.get_size()
        self.rect = pygame.Rect(x, y, self.w, self.h)

    def point_solid(self, sx, sy):
        rx, ry = int(sx) - self.x, int(sy) - self.y
        if 0 <= rx < self.w and 0 <= ry < self.h:
            return self.surf.get_at((rx, ry)).a > 40
        return False

    def damage(self, sx, sy, r=8):
        rx, ry = int(sx) - self.x, int(sy) - self.y
        if not (0 <= rx < self.w and 0 <= ry < self.h):
            return
        hole = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        hole.fill((255, 255, 255, 255))
        pygame.draw.circle(hole, (0, 0, 0, 0), (rx, ry), r)
        for _ in range(4):
            pygame.draw.circle(hole, (0, 0, 0, 0),
                               (rx + random.randint(-r, r) // 2,
                                ry + random.randint(-r, r) // 2), max(2, r // 2))
        self.surf.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class PowerUp:
    def __init__(self, x, y, kind):
        self.x, self.y, self.kind, self.t = x, y, kind, 0.0


class BonusShip:
    def __init__(self, level):
        self.dir = 1 if random.random() < 0.5 else -1
        self.x = -60.0 if self.dir > 0 else W + 60.0
        self.base_y = random.uniform(95, 130)
        self.speed = random.uniform(120, 165) + 12 * level
        self.val = random.choices((100, 300, 500, 1000), weights=(45, 30, 18, 7))[0]
        self.t = 0.0
        self.rect = pygame.Rect(0, 0, 40, 16)


class Boss:
    def __init__(self, level):
        self.level = level
        self.max_hp = self.hp = 10 + 2 * level
        self.t = random.uniform(0, 6.28)
        self.fire_t = random.uniform(1.2, 1.8)
        self.hit_t = 0.0
        self.x = W / 2
        self.y = 54
        self.w, self.h = 80, 40

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w / 2), self.y, self.w, self.h)


class Player:
    W, H = 39, 18

    def __init__(self):
        self.x = W / 2 - self.W / 2
        self.y = H - 56
        self.cooldown = 0.0
        self.invincible = 0.0
        self.powers = {"D": 0.0, "R": 0.0, "M": 0.0}
        self.plvl = {"D": 0, "R": 0, "M": 0}
        self.shield = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), self.y, self.W, self.H)


# ----------------------------------------------------------------- game
class Game:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
        pygame.init()
        global MIXER_OK, ALIEN_SURFS, SHIP_SURF, SHIP_SMALL, UFO_SURFS, BULLET_P, BULLET_A
        MIXER_OK = pygame.mixer.get_init() is not None
        build_sounds()

        pygame.display.set_caption("Space Invaders Deluxe - Pure Python/Pygame")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()

        SHIP_SURF = build_sprite(SHIP_ART, CYAN)
        SHIP_SMALL = pygame.transform.scale(SHIP_SURF, (26, 12))
        ALIEN_SURFS = [(build_sprite(a0, col), build_sprite(a1, col))
                       for col, (a0, a1), _ in ALIEN_DEFS]
        self.surf_gold = [(build_sprite(a0, GOLD), build_sprite(a1, GOLD))
                          for _, (a0, a1), _ in ALIEN_DEFS]
        self.surf_frenzy = [(build_sprite(a0, (255, 80, 80)), build_sprite(a1, (255, 80, 80)))
                            for _, (a0, a1), _ in ALIEN_DEFS]
        self.boss_surfs = (build_sprite(BOSS_A, (200, 90, 255), scale=4),
                           build_sprite(BOSS_B, (200, 90, 255), scale=4))
        self.boss_white = (build_sprite(BOSS_A, WHITE, WHITE, scale=4),
                           build_sprite(BOSS_B, WHITE, WHITE, scale=4))
        UFO_SURFS = (build_sprite(UFO_ART, ORANGE),
                     build_sprite([r.replace("o", "#") for r in UFO_ART], ORANGE))
        BULLET_P = pygame.Surface((4, 10), pygame.SRCALPHA)
        BULLET_P.fill((120, 255, 250)); pygame.draw.rect(BULLET_P, (255, 255, 255), (1, 0, 2, 4))
        BULLET_A = pygame.Surface((4, 10), pygame.SRCALPHA)
        BULLET_A.fill((255, 120, 60)); pygame.draw.rect(BULLET_A, (255, 230, 120), (1, 4, 2, 6))

        self.bg = self._make_background()
        self.stars = [Star() for _ in range(90)]
        self.world = pygame.Surface((W, H))

        self.stats = self._load_stats()
        self.saved = self._load_save()
        cfg = self._load_config()
        self.muted = bool(cfg.get("muted", False))
        if self.muted and pygame.mixer.get_init():
            pygame.mixer.set_volume(0.0)

        self.state = "menu"
        self.state_t = 0.0
        self.paused = False
        self.time = 0.0
        self.menu_t = 0.0
        self.menu_inv_x = -100
        self.step_i = 0
        self.theme = THEMES[0]

        # run / fx state
        self.score = self.lives = self.level = self.kills = 0
        self.combo = 0
        self.combo_t = 0.0
        self.combo_mult = 1
        self.bosses_run = self.gold_run = self.near_run = 0
        self.invasion = False
        self.new_high = False
        self.toasts = []
        self.vig = None
        self.booms = []
        self.time_scale = 1.0
        self.ts_active = False
        self.ts_t = 0.0
        self.frenzy_on = False
        self.boss = None

    # ------------------------------------------------------------ assets
    def _make_background(self):
        bg = pygame.Surface((W, H))
        top, bot = (10, 12, 34), (26, 10, 46)
        for y in range(H):
            t = y / H
            c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            pygame.draw.line(bg, c, (0, y), (W, y))
        neb = pygame.Surface((W, H), pygame.SRCALPHA)
        cols = [(90, 40, 160), (30, 70, 170), (150, 40, 120), (40, 120, 160)]
        for _ in range(7):
            pygame.draw.circle(neb, random.choice(cols) + (random.randint(14, 26),),
                               (random.randint(0, W), random.randint(0, H)),
                               random.randint(70, 170))
        neb = pygame.transform.scale(pygame.transform.smoothscale(neb, (W // 4, H // 4)), (W, H))
        bg.blit(neb, (0, 0))
        return bg

    def _star(self, surf, cx, cy, r, color):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        pygame.draw.polygon(surf, color, pts)

    # ----------------------------------------------------- persistence
    def _default_stats(self):
        return dict(high=0, games=0, kills=0, max_wave=1, total_score=0, best_combo=1,
                    bosses=0, goldens=0, near_misses=0, ach={})

    def _load_stats(self):
        try:
            with open(STATS_FILE) as f:
                d = json.load(f)
            base = self._default_stats(); base.update(d)
            base.setdefault("ach", {})
            return base
        except Exception:
            return self._default_stats()

    def _save_stats(self):
        try:
            tmp = STATS_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump(self.stats, f, indent=2)
            os.replace(tmp, STATS_FILE)
        except Exception:
            pass

    def _load_save(self):
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
            if d.get("ok"):
                return d
        except Exception:
            pass
        return None

    def _write_save(self):
        try:
            tmp = SAVE_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump(dict(ok=True, score=self.score, level=self.level,
                               lives=self.lives, kills=self.kills, ts=time.time()), f)
            os.replace(tmp, SAVE_FILE)
            for b, path in zip(self.barriers, BARRIER_FILES):
                pygame.image.save(b.surf, path)
        except Exception:
            pass

    def _drop_save(self):
        for p in [SAVE_FILE] + BARRIER_FILES:
            try:
                os.remove(p)
            except OSError:
                pass

    def _load_config(self):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self):
        try:
            tmp = CONFIG_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump({"muted": self.muted}, f)
            os.replace(tmp, CONFIG_FILE)
        except Exception:
            pass

    # ------------------------------------------------------- run control
    def start_new(self):
        self.score, self.lives, self.level, self.kills = 0, 3, 1, 0
        self.next_extra = 10000
        self.run_start_high = self.stats["high"]
        self.combo, self.combo_t, self.combo_mult = 0, 0.0, 1
        self.bosses_run = self.gold_run = self.near_run = 0
        self.autosave_t = 5.0
        self._drop_save()
        self.setup_wave(1)
        self.state = "play"
        SFX["select"].play()

    def start_continue(self):
        s = self._load_save()
        if not s:
            return
        self.score = s.get("score", 0)
        self.lives = max(1, s.get("lives", 3))
        self.level = max(1, s.get("level", 1))
        self.kills = s.get("kills", 0)
        self.next_extra = (self.score // 10000 + 1) * 10000
        self.run_start_high = self.stats["high"]
        self.combo, self.combo_t, self.combo_mult = 0, 0.0, 1
        self.bosses_run = self.gold_run = self.near_run = 0
        self.autosave_t = 5.0
        self.setup_wave(self.level, restore_barriers=True)
        self.state = "play"
        SFX["select"].play()

    def setup_wave(self, level, restore_barriers=False):
        boss_wave = level % 5 == 0
        self.grid = InvaderGrid(boss_wave)
        self.boss = Boss(level) if boss_wave else None
        self.frenzy_on = False
        self.theme = THEMES[(level - 1) % len(THEMES)]
        self.grid_timer = 0.0
        self.fire_timer = random.uniform(1.2, 2.0)
        self.bullets, self.alien_bullets = [], []
        self.powerups = []
        self.bonus = None
        self.bonus_timer = random.uniform(12, 20)
        self.particles, self.popups, self.flashes, self.booms = [], [], [], []
        self.player = Player()
        self.player.invincible = 1.5
        self.wave_t = 1.8
        self.banner = f"WAVE {level}" + ("  -  BOSS INCOMING" if boss_wave else "")
        # one golden invader per wave
        self.grid.invaders[random.randrange(len(self.grid.invaders))].gold = True
        if level == 5:
            self._ach("wave5")
        if level == 10:
            self._ach("wave10")
        self.barriers = []
        for i, x in enumerate(BARRIER_X):
            b = Barrier(x, BARRIER_Y)
            if restore_barriers:
                try:
                    surf = pygame.image.load(BARRIER_FILES[i]).convert_alpha()
                    if surf.get_size() == b.surf.get_size():
                        b.surf = surf
                except Exception:
                    pass
            self.barriers.append(b)

    def _game_over(self, invasion=False):
        self.state = "over"
        self.state_t = 4.5
        self.invasion = invasion
        self.new_high = self.score > self.run_start_high
        self.stats["games"] += 1
        self.stats["kills"] += self.kills
        self.stats["total_score"] += self.score
        self.stats["max_wave"] = max(self.stats["max_wave"], self.level)
        self.stats["bosses"] += self.bosses_run
        self.stats["goldens"] += self.gold_run
        self.stats["near_misses"] += self.near_run
        self._save_stats()
        self._drop_save()
        self.saved = None
        SFX["lose"].play()

    def _ach(self, aid):
        ach = self.stats.setdefault("ach", {})
        if aid in ach:
            return
        ach[aid] = 1
        self._save_stats()
        self.toasts.append([aid, 0.0])
        if len(self.toasts) > 3:
            self.toasts.pop(0)
        SFX["achieve"].play()

    def _vig(self, color, dur=0.8):
        self.vig = {"color": color, "t": dur, "max": dur}

    # ------------------------------------------------------------- update
    def _update_ts(self, dt):
        if self.ts_active:
            self.ts_t -= dt
            self.time_scale += (0.18 - self.time_scale) * min(1.0, dt * 10)
            if self.ts_t <= 0:
                self.ts_active = False
        else:
            self.time_scale += (1.0 - self.time_scale) * min(1.0, dt * 4)

    def update(self, dt):
        self.time += dt
        self._update_ts(dt)
        gdt = dt * self.time_scale
        for s in self.stars:
            s.y += s.speed * gdt
            if s.y > H + 2:
                s.y = -2
                s.x = random.randint(0, W)
        if self.toasts:
            for t in self.toasts[:]:
                t[1] += dt
                if t[1] > 3.4:
                    self.toasts.remove(t)
        if self.vig:
            self.vig["t"] -= dt
            if self.vig["t"] <= 0:
                self.vig = None

        if self.state == "menu":
            self.menu_t += dt
            self.menu_inv_x += 34 * dt
            if self.menu_inv_x > W + 40:
                self.menu_inv_x = -300
            return

        if self.state in ("clear", "over"):
            self.state_t -= dt
            self._update_fx(gdt)
            if self.state_t <= 0:
                if self.state == "clear":
                    self.level += 1
                    self.setup_wave(self.level)
                    self.state = "play"
                else:
                    self.state = "menu"
            return

        if self.paused:
            return
        self._update_fx(gdt)
        self._update_player(gdt)
        if self.state != "play":
            return
        self._update_grid(gdt)
        if self.state != "play":
            return
        self._update_bullets(gdt)
        if self.state != "play":
            return
        self._update_entities(gdt)
        self.autosave_t -= dt
        if self.autosave_t <= 0:
            self.autosave_t = 5.0
            self._write_save()

    def _m_mult(self):
        p = self.player
        return 1 + (p.plvl["M"] if p.powers["M"] > 0 else 0)

    def _update_player(self, dt):
        p = self.player
        keys = pygame.key.get_pressed()
        mv = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        if mv:
            p.x = max(12.0, min(W - 12 - Player.W, p.x + mv * 340 * dt))
        if p.cooldown > 0:
            p.cooldown -= dt
        if p.invincible > 0:
            p.invincible -= dt
        for k in list(p.powers):
            if p.powers[k] > 0:
                p.powers[k] = max(0.0, p.powers[k] - dt)
        if keys[pygame.K_SPACE]:
            self._player_fire()

    def _player_fire(self):
        p = self.player
        if p.cooldown > 0:
            return
        d = p.plvl["D"] if p.powers["D"] > 0 else 0
        count = 1 + d
        if len(self.bullets) >= 2 * count:
            return
        if p.powers["R"] > 0:
            p.cooldown = 0.16 if p.plvl["R"] == 1 else 0.10
        else:
            p.cooldown = 0.42
        SFX["shoot"].play()
        if count == 1:
            offs = [Player.W / 2 - 2]
        elif count == 2:
            offs = [7, Player.W - 11]
        else:
            offs = [7, Player.W / 2 - 2, Player.W - 11]
        for o in offs:
            self.bullets.append(Bullet(p.x + o, p.y - 2, -540, True))

    def _update_grid(self, dt):
        g = self.grid
        if self.wave_t > 0:
            self.wave_t -= dt
            return
        self.grid_timer -= dt
        if self.grid_timer <= 0:
            g.step()
            self.grid_timer = g.step_interval(self.level)
            if self.grid_timer > 0.07:
                SFX[f"step{self.step_i}"].play()
            self.step_i = (self.step_i + 1) % 4
            p = self.player
            for inv in g.alive():
                r = inv.rect(g.ox, g.oy)
                if r.bottom >= p.y - 4:
                    self._game_over(invasion=True)
                    return
                for b in self.barriers:
                    if r.colliderect(b.rect) and b.point_solid(r.centerx, r.bottom):
                        b.damage(r.centerx, r.bottom, 10)
                        self._chip(r.centerx, r.bottom, BARRIER_C, 4)
        self.fire_timer -= dt
        if self.fire_timer <= 0:
            iv = random.uniform(0.55, 1.05) * max(0.35, 1.0 - 0.065 * (self.level - 1))
            if self.frenzy_on:
                iv *= 0.6
            self.fire_timer = iv
            if len(self.alien_bullets) < min(5, 2 + self.level // 2):
                self._alien_fire()

    def _alien_fire(self):
        g = self.grid
        alive = g.alive()
        if not alive:
            return
        if random.random() < min(0.55, 0.10 + 0.08 * self.level):
            target = min(alive, key=lambda i: abs(i.rect(g.ox, g.oy).centerx - (self.player.x + 20)))
        else:
            target = random.choice(alive)
        r = target.rect(g.ox, g.oy)
        speed = min(400, 190 + 16 * self.level)
        self.alien_bullets.append(Bullet(r.centerx - 2, r.bottom, speed, False))

    def _update_bullets(self, dt):
        g = self.grid
        for b in self.bullets[:]:
            b.x += b.vx * dt
            b.y += b.vy * dt
            if b.y < HUD_H - 12:
                self.bullets.remove(b)
                continue
            if self.boss and b.rect.colliderect(self.boss.rect):
                self.bullets.remove(b)
                self._boss_hit()
                if self.state != "play":
                    return
                continue
            if self.bonus and b.rect.colliderect(self.bonus.rect):
                self._bonus_hit()
                self.bullets.remove(b)
                continue
            killed = False
            for inv in g.alive():
                if inv.rect(g.ox, g.oy).colliderect(b.rect):
                    self._invader_killed(inv)
                    killed = True
                    break
            if killed:
                self.bullets.remove(b)
                if self.state != "play":
                    return
                continue
            for bar in self.barriers:
                if bar.point_solid(b.x, b.y):
                    bar.damage(b.x, b.y, 7)
                    self._chip(b.x, b.y, BARRIER_C)
                    SFX["chip"].play()
                    self.bullets.remove(b)
                    break
        if self.state != "play":
            return
        p = self.player
        pcx, pcy = p.rect.center
        for b in self.alien_bullets[:]:
            b.x += b.vx * dt
            b.y += b.vy * dt
            if b.y > H - 34 or b.x < -20 or b.x > W + 20:
                self.alien_bullets.remove(b)
                continue
            tx, ty = b.tip
            blocked = False
            for bar in self.barriers:
                if bar.point_solid(tx, ty):
                    bar.damage(tx, ty, 7)
                    self._chip(tx, ty, BARRIER_C)
                    SFX["chip"].play()
                    blocked = True
                    break
            if blocked:
                self.alien_bullets.remove(b)
                continue
            if p.invincible <= 0 and b.rect.colliderect(p.rect):
                if p.shield > 0:
                    p.shield -= 1
                    SFX["shield"].play()
                    self._flash(b.x, b.y + 6, 0.45, (80, 220, 255))
                    self._chip(b.x, b.y + 6, (120, 230, 255), 8)
                else:
                    self._player_dead()
                    if self.state != "play":
                        return
                self.alien_bullets.remove(b)
                continue
            # near-miss reward
            if not b.rewarded and p.invincible <= 0:
                d2 = (tx - pcx) ** 2 + (ty - pcy) ** 2
                if d2 < 36 * 36:
                    b.rewarded = True
                    self.near_run += 1
                    npts = 5 * self._m_mult()
                    self._add_score(npts, (tx, ty - 12), f"NEAR +{npts}")
                    self._chip(tx, ty, (120, 240, 255), 4)
                    SFX["whoosh"].play()
                    if self.near_run >= 20:
                        self._ach("near20")

    def _update_entities(self, dt):
        p = self.player
        g = self.grid
        for pu in self.powerups[:]:
            pu.y += 64 * dt
            pu.t += dt
            pr = pygame.Rect(pu.x - 12, pu.y - 12, 24, 24)
            if pr.colliderect(p.rect.inflate(16, 10)):
                self._apply_power(pu)
                self.powerups.remove(pu)
            elif pu.y > H - 38:
                self.powerups.remove(pu)
        if self.bonus:
            bo = self.bonus
            bo.t += dt
            bo.x += bo.dir * bo.speed * dt
            yy = bo.base_y + math.sin(bo.t * 5) * 10
            bo.rect = pygame.Rect(int(bo.x) - 20, int(yy) - 8, 40, 16)
            if bo.x < -80 or bo.x > W + 80:
                self.bonus = None
        else:
            self.bonus_timer -= dt
            if self.bonus_timer <= 0:
                self.bonus = BonusShip(self.level)
                self.bonus_timer = random.uniform(14, 24)
                SFX["bonus"].play()
        # boss
        if self.boss:
            bo = self.boss
            bo.t += dt
            if bo.hit_t > 0:
                bo.hit_t -= dt
            amp = min(300, 220 + 6 * self.level)
            bo.x = W / 2 + math.sin(bo.t * (0.8 + 0.04 * self.level)) * amp
            bo.fire_t -= dt
            if bo.fire_t <= 0:
                bo.fire_t = max(0.7, 1.5 - 0.05 * self.level)
                base_a = math.atan2(p.rect.centery - (bo.y + bo.h), p.rect.centerx - bo.x)
                sp = min(330, 210 + 12 * self.level)
                for da in (-0.3, 0.0, 0.3):
                    a = base_a + da
                    self.alien_bullets.append(Bullet(bo.x - 2, bo.y + bo.h - 2,
                                                     math.sin(a) * sp, False,
                                                     vx=math.cos(a) * sp))
        # golden sparkle
        for inv in g.alive():
            if inv.gold and random.random() < 0.06:
                r = inv.rect(g.ox, g.oy)
                self.particles.append(Particle(r.x + random.randint(0, r.w), r.y + random.randint(0, r.h),
                                               0, -20, 0.4, (255, 220, 90), 2))
        # frenzy trigger
        alive_n = len(g.alive())
        if not self.frenzy_on and 0 < alive_n <= 5:
            self.frenzy_on = True
            self._popup(W / 2, 250, "FRENZY!", RED, big=True)
            self._vig(RED, 0.5)
            SFX["frenzy"].play()
        if p.invincible <= 0:
            for inv in g.alive():
                if inv.rect(g.ox, g.oy).colliderect(p.rect):
                    self._player_dead()
                    if self.state != "play":
                        return
                    break

    def _update_fx(self, dt):
        for pt in self.particles[:]:
            pt.x += pt.vx * dt
            pt.y += pt.vy * dt
            pt.vy += 140 * dt
            pt.life -= dt
            if pt.life <= 0:
                self.particles.remove(pt)
        for pp in self.popups[:]:
            pp.y -= 26 * dt
            pp.life -= dt
            if pp.life <= 0:
                self.popups.remove(pp)
        for fl in self.flashes[:]:
            fl.t += dt
            if fl.t > fl.max_t:
                self.flashes.remove(fl)
        for bm in self.booms[:]:
            bm["t"] -= dt
            if bm["t"] <= 0:
                r = bm.pop("r")
                self._flash(bm["x"], bm["y"], 0.5, (255, 200, 120))
                self._explode(bm["x"], bm["y"], ORANGE, 14, spread=0.9)
                self.booms.remove(bm)

    # ------------------------------------------------------ scoring & fx
    def _add_score(self, n, pos, label=None):
        self.score += n
        while self.score >= self.next_extra:
            self.next_extra += 10000
            if self.lives < 5:
                self.lives += 1
                self._popup(W / 2, H / 2, "EXTRA SHIP!", WHITE, big=True)
                self._vig(YELLOW, 0.7)
                SFX["extra"].play()
        if self.score >= 25000:
            self._ach("rich")
        if self.score > self.stats["high"]:
            self.stats["high"] = self.score
            self._save_stats()
        if label:
            self._popup(pos[0], pos[1], label, WHITE)

    def _invader_killed(self, inv):
        g = self.grid
        inv.alive = False
        self.kills += 1
        if self.time - self.combo_t < 1.4:
            self.combo += 1
        else:
            self.combo = 1
        self.combo_t = self.time
        self.stats["best_combo"] = max(self.stats["best_combo"], self.combo)
        new_mult = min(5, 1 + self.combo // 4)
        if new_mult > self.combo_mult:
            SFX["combo_up"].play()
            self._popup(W / 2, 300, f"MULTIPLIER x{new_mult}!", YELLOW, big=True)
        self.combo_mult = new_mult
        base = 150 if inv.gold else ALIEN_DEFS[inv.type][2]
        pts = base * self._m_mult() * new_mult
        r = inv.rect(g.ox, g.oy)
        col = GOLD if inv.gold else ALIEN_DEFS[inv.type][0]
        self._add_score(pts, (r.centerx, r.top), f"+{pts}")
        if inv.gold:
            self.gold_run += 1
            self._ach("gold")
        self._ach("first_blood")
        if self.combo >= 10:
            self._ach("combo10")
        self._explode(r.centerx, r.centery, col, 18 if inv.gold else 16)
        self._flash(r.centerx, r.centery, 0.35, col)
        SFX["invader"].play()
        if not self.powerups and random.random() < 0.13:
            kind = random.choices(list(POWER_KINDS), weights=POWER_WEIGHTS)[0]
            self.powerups.append(PowerUp(r.centerx, r.centery, kind))
        if not g.alive() and self.boss is None:
            self._wave_clear()

    def _wave_clear(self):
        bonus = 200 + 100 * self.lives
        self._add_score(bonus, (W / 2, H / 2 - 60), f"WAVE BONUS +{bonus}")
        SFX["clear"].play()
        for _ in range(2):
            kind = random.choices(list(POWER_KINDS), weights=POWER_WEIGHTS)[0]
            self.powerups.append(PowerUp(random.randint(80, W - 80), BARRIER_Y - 80, kind))
        self.state = "clear"
        self.state_t = 2.4
        self._write_save()

    def _player_dead(self):
        p = self.player
        self.lives -= 1
        self._explode(p.x + p.W / 2, p.y + p.H / 2, WHITE, 34, spread=1.0)
        self._flash(p.x + p.W / 2, p.y + 6, 0.6, (255, 200, 120))
        SFX["explode"].play()
        self.ts_active = True          # cinematic slow-mo (no screen shake)
        self.ts_t = 0.9
        self._vig(RED, 0.9)
        p.powers = {"D": 0.0, "R": 0.0, "M": 0.0}
        p.plvl = {"D": 0, "R": 0, "M": 0}
        p.shield = 0
        self.combo = 0
        self.combo_mult = 1
        if self.lives <= 0:
            self._game_over()
        else:
            p.invincible = 2.5
            p.x = W / 2 - p.W / 2

    def _bonus_hit(self):
        bo = self.bonus
        cx, cy = bo.rect.center
        val = bo.val * self._m_mult() * self.combo_mult
        self._add_score(val, (cx, cy - 14), f"+{val}")
        if random.random() < 0.25:
            kind = random.choices(list(POWER_KINDS), weights=POWER_WEIGHTS)[0]
            self.powerups.append(PowerUp(cx, cy, kind))
            self._popup(cx, cy + 18, "PICKUP DROPPED!", GREEN)
        self._explode(cx, cy, ORANGE, 22)
        self._flash(cx, cy, 0.5, ORANGE)
        SFX["bonus_hit"].play()
        self.bonus = None

    def _boss_hit(self):
        bo = self.boss
        bo.hp -= 1
        bo.hit_t = 0.12
        r = bo.rect
        self._chip(r.centerx + random.randint(-30, 30), r.centery + random.randint(-10, 10),
                   (220, 150, 255), 8)
        SFX["boss_hit"].play()
        if bo.hp <= 0:
            self._boss_dead()

    def _boss_dead(self):
        bo = self.boss
        val = (300 + 60 * (self.level // 5)) * self._m_mult() * self.combo_mult
        self._add_score(val, (bo.rect.centerx, bo.rect.top), f"BOSS +{val}")
        self.booms = []
        for i in range(7):
            self.booms.append({"t": i * 0.11,
                               "x": bo.rect.centerx + random.randint(-40, 40),
                               "y": bo.rect.centery + random.randint(-16, 16),
                               "r": random.randint(26, 56)})
        self._vig(ORANGE, 1.0)
        SFX["boss_dead"].play()
        for _ in range(3):
            kind = random.choices(list(POWER_KINDS), weights=POWER_WEIGHTS)[0]
            self.powerups.append(PowerUp(bo.rect.centerx + random.randint(-60, 60),
                                         bo.rect.centery + random.randint(-10, 30), kind))
        self.bosses_run += 1
        self._ach("boss")
        self.boss = None
        if not self.grid.alive():
            self._wave_clear()

    def _apply_power(self, pu):
        p = self.player
        info = POWER_KINDS[pu.kind]
        if pu.kind in ("D", "R", "M"):
            p.plvl[pu.kind] = min(2, p.plvl[pu.kind] + 1)
            p.powers[pu.kind] = {"D": 12.0, "R": 10.0, "M": 12.0}[pu.kind]
        elif pu.kind == "S":
            p.shield = min(2, p.shield + 1)
        else:
            if self.lives < 5:
                self.lives += 1
            SFX["extra"].play()
            self._vig(YELLOW, 0.7)
        if pu.kind != "L":
            SFX["power"].play()
        tag = f"  LV{p.plvl[pu.kind]}" if pu.kind in ("D", "R", "M") else ""
        self._popup(p.x + p.W / 2, p.y - 14, info["label"] + tag, info["color"])
        self._flash(p.x + p.W / 2, p.y + 6, 0.4, info["color"])

    def _explode(self, x, y, color, n, spread=0.6):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            sp = random.uniform(40, 240) * spread
            self.particles.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp - 40,
                                           random.uniform(0.35, 0.8), color))

    def _chip(self, x, y, color, n=6):
        for _ in range(n):
            self.particles.append(Particle(x, y, random.uniform(-90, 90), random.uniform(-130, -10),
                                           random.uniform(0.2, 0.45), color))

    def _popup(self, x, y, text, color, big=False):
        self.popups.append(Popup(x, y, text, color, big))

    def _flash(self, x, y, max_t, color):
        self.flashes.append(Flash(x, y, max_t, color))

    # -------------------------------------------------------------- drawing
    def _draw_stars(self, surf):
        for s in self.stars:
            tw = 0.55 + 0.45 * math.sin(self.time * s.tw + s.ph)
            c = (int(170 * tw), int(195 * tw), int(255 * tw))
            surf.fill(c, (int(s.x), int(s.y), s.size, s.size))

    def _draw_world(self):
        wd = self.world
        self.screen.fill((0, 0, 0))
        wd.blit(self.bg, (0, 0))
        self._draw_stars(wd)
        pygame.draw.line(wd, self.theme, (0, HUD_H), (W, HUD_H), 2)

        for b in self.barriers:
            wd.blit(b.surf, (b.x, b.y))

        g = self.grid
        for inv in g.invaders:
            if not inv.alive:
                continue
            if inv.gold:
                frames = self.surf_gold[inv.type]
            elif self.frenzy_on:
                frames = self.surf_frenzy[inv.type]
            else:
                frames = ALIEN_SURFS[inv.type]
            x = g.ox + inv.col * SPX + (SPX - inv.w) // 2
            y = g.oy + inv.row * SPY
            wd.blit(frames[g.frame], (x, y))

        if self.boss:
            bo = self.boss
            fr = int(bo.t * 10) % 2
            wd.blit(self.boss_white[fr] if bo.hit_t > 0 else self.boss_surfs[fr],
                    (bo.rect.x, bo.y))
            frac = max(0.0, bo.hp / bo.max_hp)
            bx, bw = bo.rect.centerx - 45, 90
            pygame.draw.rect(wd, (30, 10, 30), (bx, bo.y - 12, bw, 7))
            c = (int(60 + 195 * (1 - frac)), int(230 - 160 * (1 - frac)), 120)
            pygame.draw.rect(wd, c, (bx, bo.y - 12, int(bw * frac), 7))
            pygame.draw.rect(wd, WHITE, (bx, bo.y - 12, bw, 7), 1)

        if self.bonus:
            bo = self.bonus
            wd.blit(UFO_SURFS[int(bo.t * 8) % 2], bo.rect)
            q = render_text("???", 14, ORANGE)
            wd.blit(q, (int(bo.x) - q.get_width() // 2, bo.rect.top - 20))

        for pu in self.powerups:
            info = POWER_KINDS[pu.kind]
            pulse = 1 + 0.12 * math.sin(pu.t * 6)
            box = pygame.Surface((34, 34), pygame.SRCALPHA)
            r = int(15 * pulse)
            pygame.draw.ellipse(box, (10, 14, 30, 220), (17 - r, 17 - r, 2 * r, 2 * r))
            pygame.draw.ellipse(box, info["color"], (17 - r, 17 - r, 2 * r, 2 * r), 2)
            lt = render_text(PU_LETTER[pu.kind], 14 if pu.kind == "M" else 18, info["color"])
            box.blit(lt, (17 - lt.get_width() // 2, 17 - lt.get_height() // 2))
            wd.blit(box, (int(pu.x) - 17, int(pu.y) - 17))

        for b in self.bullets:
            wd.blit(BULLET_P, (int(b.x) - 2, int(b.y)))
        for b in self.alien_bullets:
            wd.blit(BULLET_A, (int(b.x) - 2, int(b.y)))

        p = self.player
        if self.state in ("play", "clear") and (p.invincible <= 0 or int(self.time * 12) % 2 == 0):
            wd.blit(SHIP_SURF, (int(p.x), p.y))
            if self.state == "play" and random.random() < 0.8:
                flame = random.randint(3, 7)
                pygame.draw.polygon(wd, ORANGE,
                                    [(p.x + 8, p.y + p.H), (p.x + 14, p.y + p.H + flame), (p.x + 20, p.y + p.H)])
                pygame.draw.polygon(wd, YELLOW,
                                    [(p.x + 10, p.y + p.H), (p.x + 14, p.y + p.H + max(2, flame - 2)), (p.x + 18, p.y + p.H)])
            if p.shield > 0:
                r = p.rect.inflate(16, 14)
                a = 120 + int(80 * math.sin(self.time * 6))
                sh = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                pygame.draw.ellipse(sh, (80, 220, 255, a), (0, 0, r.w, r.h), 2)
                if p.shield == 2:
                    pygame.draw.ellipse(sh, (80, 220, 255, a), (4, 4, r.w - 8, r.h - 8), 1)
                wd.blit(sh, r)

        for pt in self.particles:
            k = max(0.0, pt.life / pt.max_life)
            c = tuple(max(0, min(255, int(v * k) + 40)) for v in pt.color)
            s = max(1, int(pt.size * k) + 1)
            wd.fill(c, (int(pt.x), int(pt.y), s, s))

        for fl in self.flashes:
            k = max(0.0, 1.0 - fl.t / fl.max_t)
            r = int(8 + (1 - k) * 44)
            fs = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(fs, (fl.color[0], fl.color[1], fl.color[2], int(170 * k)), (r, r), r)
            wd.blit(fs, (int(fl.x) - r, int(fl.y) - r), special_flags=pygame.BLEND_ADD)

        for pp in self.popups:
            age = pp.dur - pp.life
            f = 1.0 + 1.3 * max(0.0, (0.15 - age) / 0.15)
            s = pp.surf
            if f > 1.01:
                s = pygame.transform.scale(s, (int(s.get_width() * f), int(s.get_height() * f)))
            s.set_alpha(int(255 * max(0.0, min(1.0, pp.life / 0.5))))
            wd.blit(s, (int(pp.x) - s.get_width() // 2, int(pp.y)))

        if self.wave_t > 0 and self.state == "play":
            t = glow_text(self.banner, 46 if not self.boss else 40, WHITE,
                          RED if self.boss else self.theme, scale=2)
            t.set_alpha(int(255 * min(1.0, self.wave_t / 0.4)))
            wd.blit(t, (W // 2 - t.get_width() // 2, 190))

        self.screen.blit(wd, (0, 0))

    def _draw_hud(self):
        top = pygame.Surface((W, HUD_H), pygame.SRCALPHA)
        top.fill((6, 10, 26, 215))
        self.screen.blit(top, (0, 0))
        s = render_text(f"SCORE {self.score:06d}", 20, WHITE, 2)
        self.screen.blit(s, (14, 8))
        hi = render_text(f"HI {max(self.stats['high'], self.score):06d}", 20, GREEN, 2)
        self.screen.blit(hi, (W // 2 - hi.get_width() // 2, 8))
        lv = render_text(f"WAVE {self.level}", 20, self.theme, 2)
        self.screen.blit(lv, (W - 14 - lv.get_width(), 8))

        bot = pygame.Surface((W, 30), pygame.SRCALPHA)
        bot.fill((6, 10, 26, 215))
        self.screen.blit(bot, (0, H - 30))
        for i in range(max(0, self.lives - 1)):
            self.screen.blit(SHIP_SMALL, (16 + i * 32, H - 22))

        x = W - 16

        def icon(letter, color, frac=None, pips=0):
            nonlocal x
            box = pygame.Surface((34, 22), pygame.SRCALPHA)
            pygame.draw.rect(box, (20, 26, 50, 255), (0, 0, 34, 22), border_radius=5)
            pygame.draw.rect(box, color, (0, 0, 34, 22), 2, border_radius=5)
            lt = render_text(letter, 13 if len(letter) > 1 else 16, color)
            box.blit(lt, (15 - lt.get_width() // 2, 11 - lt.get_height() // 2))
            for i in range(pips):
                pygame.draw.rect(box, color, (28, 4 + i * 5, 4, 3))
            self.screen.blit(box, (x - 34, H - 26))
            if frac is not None:
                pygame.draw.rect(self.screen, (40, 46, 80), (x - 34, H - 3, 34, 3))
                pygame.draw.rect(self.screen, color, (x - 34, H - 3, int(34 * max(0.0, frac)), 3))
            x -= 42

        p = self.player
        if self.state in ("play", "clear", "over"):
            if p.powers["M"] > 0:
                icon("2X", YELLOW, p.powers["M"] / 12, pips=p.plvl["M"])
            if p.powers["R"] > 0:
                icon("R", ORANGE, p.powers["R"] / 10, pips=p.plvl["R"])
            if p.powers["D"] > 0:
                icon("D", CYAN, p.powers["D"] / 12, pips=p.plvl["D"])
            if p.shield > 0:
                icon("S", GREEN, pips=p.shield)

        if self.combo >= 2 and self.time - self.combo_t < 1.4:
            frac = max(0.0, (1.4 - (self.time - self.combo_t)) / 1.4)
            cx0 = W // 2 - 90
            pygame.draw.rect(self.screen, (40, 46, 80), (cx0, H - 8, 180, 5))
            pygame.draw.rect(self.screen, YELLOW if self.combo_mult > 1 else ORANGE,
                             (cx0, H - 8, int(180 * frac), 5))
            ct = render_text(f"COMBO x{self.combo}   MULT x{self.combo_mult}", 14, YELLOW, 2)
            self.screen.blit(ct, (W // 2 - ct.get_width() // 2, H - 27))

    def _draw_toasts(self):
        y = HUD_H + 10
        for aid, t in self.toasts:
            k = min(min(1.0, t * 5), max(0.0, (3.4 - t) * 3))
            name = ACH.get(aid, aid)
            box = pygame.Surface((252, 46), pygame.SRCALPHA)
            pygame.draw.rect(box, (10, 14, 30, 230), (0, 0, 252, 46), border_radius=8)
            pygame.draw.rect(box, YELLOW, (0, 0, 252, 46), 2, border_radius=8)
            self._star(box, 22, 23, 11, YELLOW)
            t1 = render_text("ACHIEVEMENT UNLOCKED", 12, YELLOW)
            t2 = render_text(name, 18, WHITE, 2)
            box.blit(t1, (42, 5))
            box.blit(t2, (42, 20))
            box.set_alpha(int(255 * k))
            self.screen.blit(box, (int(W - 256 + (1 - k) * 24), y))
            y += 54

    def _draw_vignette(self):
        if not self.vig:
            return
        k = max(0.0, self.vig["t"] / self.vig["max"])
        c = self.vig["color"]
        v = pygame.Surface((W, H), pygame.SRCALPHA)
        for i in range(6):
            a = int(90 * k * (6 - i) / 6)
            pygame.draw.rect(v, (c[0], c[1], c[2], a), (i * 7, i * 7, W - i * 14, H - i * 14), 7)
        self.screen.blit(v, (0, 0), special_flags=pygame.BLEND_ADD)

    def _draw_menu(self):
        self.screen.blit(self.bg, (0, 0))
        self._draw_stars(self.screen)

        tcol = THEMES[int(self.menu_t * 0.8) % len(THEMES)]
        t = glow_text("SPACE INVADERS", 54, WHITE, tcol, scale=2)
        pulse = 1 + 0.015 * math.sin(self.menu_t * 2)
        if abs(pulse - 1) > 0.001:
            t = pygame.transform.scale(t, (int(t.get_width() * pulse), int(t.get_height() * pulse)))
        self.screen.blit(t, (W // 2 - t.get_width() // 2, 62))
        sub = render_text("DELUXE - BOSSES - COMBOS - ACHIEVEMENTS", 18, tcol)
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 160))

        frame = int(self.menu_t * 3) % 2
        for i, ty in enumerate((0, 1, 2)):
            self.screen.blit(ALIEN_SURFS[ty][frame], (self.menu_inv_x + i * 46, 198))
        self.screen.blit(UFO_SURFS[int(self.menu_t * 6) % 2], (self.menu_inv_x + 148, 204))

        table = [("30 PTS", ALIEN_SURFS[0][0]), ("20 PTS", ALIEN_SURFS[1][0]),
                 ("10 PTS", ALIEN_SURFS[2][0]), ("?????", UFO_SURFS[0]),
                 ("150 PTS", self.surf_gold[0][0]), ("BOSS?", self.boss_surfs[0])]
        y = 248
        for label, spr in table:
            self.screen.blit(spr, (185, y))
            lt = render_text(label, 20, GOLD if "150" in label else (RED if "BOSS" in label else WHITE), 2)
            self.screen.blit(lt, (250, y + max(0, (spr.get_height() - lt.get_height()) // 2)))
            y += 34

        tip = render_text("STACK POWER-UPS (LV1-3) - GRAZE BULLETS FOR NEAR-MISS PTS - KEEP COMBOS ALIVE", 18, (150, 160, 200))
        self.screen.blit(tip, (W // 2 - tip.get_width() // 2, 452))
        c1 = render_text("ARROWS / A D   MOVE        SPACE   FIRE", 20, WHITE)
        c2 = render_text("P  PAUSE      M  MUTE      ESC  MENU", 20, BLUE)
        self.screen.blit(c1, (W // 2 - c1.get_width() // 2, 478))
        self.screen.blit(c2, (W // 2 - c2.get_width() // 2, 504))

        if int(self.menu_t * 2) % 2 == 0:
            st = glow_text("PRESS ENTER TO START", 30, WHITE, GREEN)
            self.screen.blit(st, (W // 2 - st.get_width() // 2, 534))

        if self.saved:
            cs = render_text(f"CONTINUE   WAVE {self.saved.get('level', 1)}  -  SCORE {self.saved.get('score', 0)}   [PRESS C]", 18, YELLOW)
            self.screen.blit(cs, (W // 2 - cs.get_width() // 2, 562))

        sl = render_text(f"HIGH {self.stats['high']:06d}    GAMES {self.stats['games']}    "
                         f"BEST WAVE {self.stats['max_wave']}    BEST COMBO x{self.stats['best_combo']}",
                         16, (140, 150, 190))
        self.screen.blit(sl, (W // 2 - sl.get_width() // 2, H - 52))
        sl2 = render_text(f"ACHIEVEMENTS {len(self.stats.get('ach', {}))}/{len(ACH)}    "
                          f"BOSSES {self.stats['bosses']}    GOLDENS {self.stats['goldens']}    "
                          f"NEAR MISS {self.stats['near_misses']}", 16, (140, 150, 190))
        self.screen.blit(sl2, (W // 2 - sl2.get_width() // 2 + 10, H - 30))
        self._star(self.screen, W // 2 - sl2.get_width() // 2 - 10, H - 22, 7, YELLOW)

    def _draw_wave_clear(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 90))
        self.screen.blit(ov, (0, 0))
        t1 = glow_text("WAVE CLEAR!", 40, WHITE, GREEN, scale=2)
        self.screen.blit(t1, (W // 2 - t1.get_width() // 2, 210))
        t2 = render_text("GRAB THE DROPS - NEXT WAVE INCOMING...", 22, YELLOW, 2)
        self.screen.blit(t2, (W // 2 - t2.get_width() // 2, 290))

    def _draw_game_over(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))
        title = "THE INVADERS HAVE LANDED!" if self.invasion else "GAME OVER"
        t = glow_text(title, 42, RED, (255, 40, 40), scale=2)
        self.screen.blit(t, (W // 2 - t.get_width() // 2, 175))
        y = 285
        for ln in (f"SCORE  {self.score:06d}",
                   f"WAVE {self.level}     KILLS {self.kills}     BOSSES {self.bosses_run}"):
            lt = render_text(ln, 24, WHITE, 2)
            self.screen.blit(lt, (W // 2 - lt.get_width() // 2, y))
            y += 42
        if self.new_high and int(self.time * 3) % 2 == 0:
            nh = glow_text("NEW HIGH SCORE!", 28, YELLOW, YELLOW)
            self.screen.blit(nh, (W // 2 - nh.get_width() // 2, y + 8))
            y += 48
        if int(self.time * 2) % 2 == 0:
            bt = render_text("PRESS ENTER", 22, CYAN, 2)
            self.screen.blit(bt, (W // 2 - bt.get_width() // 2, y + 30))

    def _draw_pause(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        self.screen.blit(ov, (0, 0))
        t = glow_text("PAUSED", 40, WHITE, BLUE, scale=2)
        self.screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 45))
        s = render_text("P  RESUME      ESC  MENU", 20, WHITE)
        self.screen.blit(s, (W // 2 - s.get_width() // 2, H // 2 + 25))

    def draw(self):
        if self.state == "menu":
            self._draw_menu()
        else:
            self._draw_world()
            self._draw_hud()
            self._draw_vignette()
            if self.state == "clear":
                self._draw_wave_clear()
            if self.state == "over":
                self._draw_game_over()
            if self.paused and self.state == "play":
                self._draw_pause()
            self._draw_toasts()
        if self.muted:
            m = render_text("MUTED (M)", 16, (150, 150, 170))
            self.screen.blit(m, (W - m.get_width() - 8, HUD_H + 6))
        pygame.display.flip()

    # -------------------------------------------------------------- events
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if self.state == "play" and not self.paused:
                    self._write_save()
                self._quit()
            elif ev.type == pygame.KEYDOWN:
                self._on_key(ev.key)
            elif ev.type == pygame.WINDOWFOCUSLOST:
                if self.state == "play" and not self.paused:
                    self.paused = True

    def _on_key(self, key):
        if key == pygame.K_m:
            self.muted = not self.muted
            if pygame.mixer.get_init():
                pygame.mixer.set_volume(0.0 if self.muted else 1.0)
            self._save_config()
            return
        if self.state == "menu":
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.start_new()
            elif key == pygame.K_c and self.saved:
                self.start_continue()
            elif key == pygame.K_ESCAPE:
                self._quit()
        elif self.state == "play":
            if key == pygame.K_p:
                self.paused = not self.paused
                if self.paused:
                    self._write_save()
            elif key == pygame.K_ESCAPE:
                self.paused = False
                self._write_save()
                self.saved = self._load_save()
                self.state = "menu"
        elif self.state == "over":
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = "menu"

    def _quit(self):
        self._save_stats()
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    try:
        Game().run()
    except KeyboardInterrupt:
        pygame.quit()
