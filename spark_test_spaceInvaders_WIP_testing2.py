# PROMPT USED:
# Write Space Invaders game in python using pygame library, make it visually appealing and polished but make sure to generate all graphic and sound files in python. Don't assume that user can download images and sound from internet, instead all resources for game should be generated in game. Also feel free to use external files (e.g. json) to store game parameters, progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Make sure to include in python generated sound and if possible also music, but music is optional.
# Execution inststuction:
# COMMAND to execute High:
# /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --parallel 1  --temp 1.0 --top_p 1.0 --chat-template-kwargs '{"reasoning_effort":"max"}'  --spec-type draft-dspark   --spec-draft-n-max 3 --fit off  -md /AI/models/dspark-DeepSeek-V4-Flash-0731-BF16.gguf --mmproj /AI/models/mmproj-DeepSeek-V4-Flash-Vision-Exp-f32.gguf  --model /AI/models/DeepSeek-V4-Flash-Vision-Exp-Ablit-IQ2XXS.gguf
#STATS: 12.594 generated tokens, time elapsed  7min:09s  29.33 t/s


"""
SPACE INVADERS
A polished retro arcade shooter.
 - All graphics & audio synthesized at runtime (no asset downloads).
 - Uses config.json for parameters and progress.json for stats/high-score.
 - Features: destructible barriers, multiple levels, combo bonus system,
   mystery bonus ship, power-ups, synthesized music.
"""
import math
import random
import json
import os
import sys
import array
import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False

# ---------------------------------------------------------------------------
# Configuration (written/read from config.json)
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "window": {"width": 960, "height": 720, "fps": 60},
    "player": {
        "speed": 6.0, "lives": 3, "bullet_speed": 13, "fire_cooldown": 0.30,
        "rapid_fire_mult": 0.45, "rapid_duration": 6.0, "double_duration": 8.0
    },
    "alien": {
        "base_speed": 0.55, "speed_per_level": 0.12,
        "fire_chance": 0.004, "fire_chance_per_level": 0.001,
        "max_rows": 7, "max_cols": 13,
        "points": {"crab": 10, "squid": 20, "octopus": 30, "mystery": 100}
    },
    "barrier": {"count": 4, "rows": 14, "cols": 18, "hp": 3, "block_size": 9},
    "bonus": {
        "mystery_chance": 0.002, "powerup_chance": 0.06,
        "combo_mult_step": 0.1, "combo_max_mult": 5.0,
        "combo_reset_on_hit": True
    },
    "level": {"base": 1, "max": 12, "lives_gain": 1},
    "audio": {"volume": 0.6, "music_volume": 0.45},
    "save_file": "progress.json",
    "config_file": "config.json"
}


def load_config():
    cfg_file = DEFAULT_CONFIG["config_file"]
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file) as f:
                user = json.load(f)
            for k, v in user.items():
                if isinstance(cfg.get(k), dict) and isinstance(v, dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
        except Exception:
            pass
    else:
        try:
            with open(cfg_file, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
        except Exception:
            pass
    return cfg


def load_progress():
    save_file = DEFAULT_CONFIG["save_file"]
    if os.path.exists(save_file):
        try:
            with open(save_file) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "high_score": 0, "best_level": 0, "games_played": 0,
        "total_shots": 0, "total_kills": 0, "total_time": 0.0
    }


def save_progress(p):
    try:
        with open(DEFAULT_CONFIG["save_file"], "w") as f:
            json.dump(p, f, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Audio synthesis (no external sound files needed)
# ---------------------------------------------------------------------------
def samples_to_buffer(samples):
    if HAS_NUMPY:
        arr = (np.clip(np.asarray(samples, dtype=float), -1.0, 1.0) * 32767).astype(np.int16)
        return arr.tobytes()
    arr = array.array("h", (int(max(-1.0, min(1.0, s)) * 32767) for s in samples))
    return arr.tobytes()


def gen_tone(freq, dur, wave="square", vol=0.5, decay=True):
    rate = 22050
    n = int(rate * dur)
    if HAS_NUMPY:
        t = np.arange(n) / rate
        if wave == "square":
            sig = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave == "saw":
            sig = 2 * ((t * freq) % 1.0) - 1.0
        elif wave == "triangle":
            sig = 2 * np.abs(2 * ((t * freq) % 1.0) - 1.0) - 1.0
        else:
            sig = np.sin(2 * np.pi * freq * t)
        if decay:
            sig *= np.exp(-t / (dur * 0.15 + 1e-6))
        sig *= vol
        return samples_to_buffer(sig)
    samples = []
    for i in range(n):
        t = i / rate
        if wave == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == "saw":
            v = 2 * ((t * freq) % 1.0) - 1.0
        elif wave == "triangle":
            v = 2 * abs(2 * ((t * freq) % 1.0) - 1.0) - 1.0
        else:
            v = math.sin(2 * math.pi * freq * t)
        if decay:
            v *= math.exp(-t / (dur * 0.15 + 1e-6))
        samples.append(v * vol)
    return samples_to_buffer(samples)


def gen_noise(dur, vol=0.5, decay=True):
    rate = 22050
    n = int(rate * dur)
    if HAS_NUMPY:
        sig = np.random.uniform(-1, 1, n)
        if decay:
            sig *= np.exp(-np.arange(n) / (rate * dur * 0.15 + 1e-6))
        sig *= vol
        return samples_to_buffer(sig)
    samples = [random.uniform(-1, 1) for _ in range(n)]
    for i in range(n):
        if decay:
            samples[i] *= math.exp(-(i / rate) / (dur * 0.15 + 1e-6))
        samples[i] *= vol
    return samples_to_buffer(samples)


def gen_sweep(f0, f1, dur, vol=0.5, wave="square"):
    rate = 22050
    n = int(rate * dur)
    if HAS_NUMPY:
        t = np.arange(n) / rate
        freq = f0 + (f1 - f0) * (t / dur)
        sig = np.sign(np.sin(2 * np.pi * freq * t))
        sig *= np.exp(-t / (dur * 0.2 + 1e-6))
        sig *= vol
        return samples_to_buffer(sig)
    samples = []
    phase = 0.0
    for i in range(n):
        t = i / rate
        freq = f0 + (f1 - f0) * (t / dur)
        phase += 2 * math.pi * freq / rate
        v = (1.0 if math.sin(phase) >= 0 else -1.0)
        v *= math.exp(-t / (dur * 0.2 + 1e-6)) * vol
        samples.append(v)
    return samples_to_buffer(samples)


def generate_music():
    """Synthesize a short looping chiptune melody + bass, all in Python."""
    rate = 22050
    bpm = 120
    beat = 60.0 / bpm
    melody = [
        (523.25, 0.5), (587.33, 0.5), (659.25, 0.5), (587.33, 0.5),
        (523.25, 0.5), (587.33, 0.5), (659.25, 1.0),
        (698.46, 0.5), (659.25, 0.5), (587.33, 0.5), (523.25, 0.5),
        (440.0, 1.0), (440.0, 0.5), (523.25, 0.5), (587.33, 1.0), (659.25, 1.0),
    ]
    bass = [
        (130.81, 0.5), (130.81, 0.5), (98.0, 0.5), (130.81, 0.5),
        (130.81, 0.5), (130.81, 0.5), (98.0, 0.5), (130.81, 0.5),
        (130.81, 0.5), (130.81, 0.5), (98.0, 0.5), (130.81, 0.5),
        (98.0, 0.5), (98.0, 0.5), (87.31, 0.5), (98.0, 0.5),
    ]
    total_beats = sum(m[1] for m in melody)
    total_dur = total_beats * beat
    n = int(rate * total_dur)
    buf = [0.0] * n

    pos = 0.0
    for freq, beats in melody:
        dur = beats * beat
        start = int(pos * rate)
        end = min(n, int((pos + beats) * rate))
        for i in range(start, end):
            t = (i - start) / rate
            env = math.exp(-t / (dur * 0.4 + 1e-6))
            buf[i] += 0.35 * (1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0) * env
        pos += beats

    pos = 0.0
    for freq, beats in bass:
        dur = beats * beat
        start = int(pos * rate)
        end = min(n, int((pos + beats) * rate))
        for i in range(start, end):
            t = (i - start) / rate
            env = math.exp(-t / (dur * 0.5 + 1e-6))
            buf[i] += 0.22 * (1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0) * env
        pos += beats

    maxv = max(abs(v) for v in buf) if buf else 1.0
    buf = [v / maxv for v in buf]
    return samples_to_buffer(buf)


# ---------------------------------------------------------------------------
# Procedural graphics generation
# ---------------------------------------------------------------------------
def make_glow(surf, center, radius, color, alpha):
    for i in range(radius, 1, -3):
        a = int(alpha * (i / radius))
        pygame.draw.circle(surf, (*color, a), center, i)


def make_background(w, h):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        r = int(8 + 4 * t)
        g = int(10 + 6 * t)
        b = int(34 + 12 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf


def make_player_ship():
    surf = pygame.Surface((72, 72), pygame.SRCALPHA)
    make_glow(surf, (36, 46), 30, (0, 220, 255), 80)
    # engine glow
    make_glow(surf, (36, 62), 16, (0, 120, 255), 120)
    # wings
    pygame.draw.polygon(surf, (0, 180, 240), [(36, 8), (10, 52), (28, 58)])
    pygame.draw.polygon(surf, (0, 180, 240), [(36, 8), (62, 52), (44, 58)])
    # body
    pygame.draw.polygon(surf, (0, 220, 255), [(36, 8), (22, 50), (36, 64), (50, 50)])
    # cockpit
    pygame.draw.polygon(surf, (255, 255, 255), [(36, 14), (31, 36), (36, 40), (41, 36)])
    # engine flame
    pygame.draw.polygon(surf, (0, 160, 255), [(30, 62), (36, 70), (42, 62)])
    pygame.draw.polygon(surf, (180, 240, 255), [(32, 62), (36, 66), (40, 62)])
    return surf


# Classic alien sprite patterns
CRAB = [
    "..X.....X..",
    "X..X...X..X",
    "XXXXX.XXXXX",
    "..X.....X..",
    ".XXXXX.XXXX",
    "XX.XXX.XXX.",
    ".X.....X...",
    "X.......X..",
]
SQUID = [
    "..XX...XX..",
    ".XXXX.XXXX.",
    "XX....X..XX",
    "..X..X..X..",
    ".XXXX.XXXX.",
    "X..X...X..X",
    "X.........X",
    "X.........X",
]
OCT = [
    "XX...XX...XX",
    "XX..XXX..XX.",
    "XX.XXXXX.XX.",
    "...XXXXX...",
    ".XXXX.XXXX.",
    "XXX...X..XX.",
    "X.....X...X.",
    "X.........X.",
]


def make_alien(pattern, color, scale=3, glow=True):
    rows = len(pattern)
    cols = max(len(line) for line in pattern)
    surf = pygame.Surface((cols * scale, rows * scale), pygame.SRCALPHA)
    if glow:
        make_glow(surf, (cols * scale // 2, rows * scale // 2),
                  cols * scale // 2 + 4, color, 40)
    for r, line in enumerate(pattern):
        for c, ch in enumerate(line):
            if ch == "X":
                pygame.draw.rect(surf, color, (c * scale, r * scale, scale, scale))
    return surf


def make_mystery_ship():
    surf = pygame.Surface((48, 24), pygame.SRCALPHA)
    make_glow(surf, (24, 12), 22, (255, 40, 40), 60)
    pygame.draw.polygon(surf, (255, 60, 60), [(24, 2), (8, 14), (40, 14)])
    pygame.draw.polygon(surf, (255, 180, 60), [(8, 14), (16, 22), (32, 22), (40, 14)])
    pygame.draw.rect(surf, (255, 255, 255), (18, 6, 12, 4))
    return surf


def shield_pattern(rows, cols):
    pattern = []
    for r in range(rows):
        line = []
        yf = r / (rows - 1)  # 0..1
        wf = 0.22 + 0.78 * math.sin(math.pi * 0.5 * yf)  # narrow top, wide bottom
        half = cols / 2.0
        for c in range(cols):
            dx = abs(c - (cols - 1) / 2.0) / half
            present = dx <= wf
            # bottom center notch (classic shield)
            if yf > 0.55 and abs(c - (cols - 1) / 2.0) < cols * 0.14:
                present = False
            line.append(1 if present else 0)
        pattern.append(line)
    return pattern


def make_powerup_image(ptype, size=40):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    colors = {
        "rapid": (255, 180, 40),
        "double": (80, 200, 255),
        "shield": (60, 220, 120),
        "life": (255, 80, 120),
        "score": (200, 120, 255),
    }
    color = colors.get(ptype, (255, 255, 255))
    make_glow(surf, (size // 2, size // 2), size // 2, color, 60)
    pygame.draw.rect(surf, color, (8, 8, size - 16, size - 16), border_radius=8)
    pygame.draw.rect(surf, (255, 255, 255), (8, 8, size - 16, size - 16), 2, border_radius=8)
    label = {"rapid": "R", "double": "D", "shield": "S", "life": "+", "score": "$"}
    fnt = pygame.font.Font(None, 24)
    txt = fnt.render(label.get(ptype, "?"), True, (255, 255, 255))
    surf.blit(txt, (size // 2 - txt.get_width() // 2, size // 2 - txt.get_height() // 2))
    return surf


# ---------------------------------------------------------------------------
# Game objects
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, cfg, screen_h):
        self.cfg = cfg
        self.image = make_player_ship()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (cfg["window"]["width"] // 2, screen_h - 24)
        self.x = float(self.rect.x)
        self.lives = cfg["player"]["lives"]
        self.fire_timer = 0.0
        self.rapid_timer = 0.0
        self.double_timer = 0.0
        self.shield = False

    def update(self, dt, keys, width):
        speed = self.cfg["player"]["speed"]
        if keys[pygame.K_LEFT]:
            self.x -= speed * dt * 60
        if keys[pygame.K_RIGHT]:
            self.x += speed * dt * 60
        self.x = max(10, min(width - self.rect.width - 10, self.x))
        self.rect.x = int(self.x)
        self.fire_timer = max(0.0, self.fire_timer - dt)
        self.rapid_timer = max(0.0, self.rapid_timer - dt)
        self.double_timer = max(0.0, self.double_timer - dt)
        if self.rapid_timer <= 0:
            self.rapid_timer = 0
        if self.double_timer <= 0:
            self.double_timer = 0

    def can_fire(self):
        return self.fire_timer <= 0.0

    def fire(self):
        self.fire_timer = self.cfg["player"]["fire_cooldown"]
        if self.rapid_timer > 0:
            self.fire_timer *= self.cfg["player"]["rapid_fire_mult"]

    def reset_timers(self):
        self.rapid_timer = 0
        self.double_timer = 0
        self.shield = False


class Alien:
    def __init__(self, x, y, typ, image, points, level):
        self.x = float(x)
        self.y = float(y)
        self.typ = typ
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.points = points
        self.alive = True


class Bullet:
    def __init__(self, x, y, owner, speed, width, height):
        self.owner = owner
        if owner == "player":
            self.rect = pygame.Rect(x, y, 4, 16)
            self.vx = 0
            self.vy = -speed
            self.color = (0, 255, 255)
        else:
            self.rect = pygame.Rect(x, y, 6, 12)
            self.vx = 0
            self.vy = speed
            self.color = (255, 80, 60)

    def update(self, dt):
        self.rect.y += self.vy * dt * 60
        self.rect.x += self.vx * dt * 60

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)


class Barrier:
    def __init__(self, x, y, rows, cols, hp, block_size):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.block_size = block_size
        pattern = shield_pattern(rows, cols)
        self.grid = [[hp if pattern[r][c] else 0 for c in range(cols)] for r in range(rows)]

    def hit(self, rect):
        hit_any = False
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    bx = self.x + c * self.block_size
                    by = self.y + r * self.block_size
                    block = pygame.Rect(bx, by, self.block_size, self.block_size)
                    if block.colliderect(rect):
                        self.grid[r][c] -= 1
                        hit_any = True
        return hit_any

    def draw(self, screen):
        colors = {3: (0, 220, 90), 2: (0, 180, 80), 1: (0, 130, 60)}
        for r in range(self.rows):
            for c in range(self.cols):
                hp = self.grid[r][c]
                if hp > 0:
                    bx = self.x + c * self.block_size
                    by = self.y + r * self.block_size
                    pygame.draw.rect(screen, colors[hp], (bx, by, self.block_size, self.block_size))
                    pygame.draw.rect(screen, (0, 255, 120), (bx, by, self.block_size, self.block_size), 1)


class PowerUp:
    def __init__(self, x, y, ptype, image, speed=2.5):
        self.x = float(x)
        self.y = float(y)
        self.ptype = ptype
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.vy = speed

    def update(self, dt):
        self.y += self.vy * dt * 60
        self.rect.y = int(self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Particle:
    def __init__(self, x, y, color, vx, vy, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.life -= dt

    def draw(self, screen):
        if self.life <= 0:
            return
        a = int(255 * (self.life / self.max_life))
        r = max(1, int(4 * (self.life / self.max_life)))
        pygame.draw.circle(screen, (*self.color, a), (int(self.x), int(self.y)), r)


class Starfield:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.bg = make_background(w, h)
        self.stars = []
        for _ in range(120):
            self.stars.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "b": random.uniform(0.3, 1.0),
                "tw": random.uniform(0.0, 2 * math.pi),
                "speed": random.uniform(0.5, 2.5),
                "r": random.uniform(1, 2.5),
            })

    def draw(self, screen, dt):
        screen.blit(self.bg, (0, 0))
        for s in self.stars:
            s["tw"] += s["speed"] * dt
            a = int(120 + 120 * math.sin(s["tw"]))
            color = (a, a, a)
            pygame.draw.circle(screen, color, (int(s["x"]), int(s["y"])), int(s["r"]))


# ---------------------------------------------------------------------------
# Main game controller
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.cfg = load_config()
        self.progress = load_progress()
        pygame.init()
        pygame.mixer.init()
        self.width = self.cfg["window"]["width"]
        self.height = self.cfg["window"]["height"]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("SPACE INVADERS")
        self.clock = pygame.time.Clock()
        self.fps = self.cfg["window"]["fps"]

        self.volume = self.cfg["audio"]["volume"]
        self.music_volume = self.cfg["audio"]["music_volume"]
        self.sounds = self._build_sounds()
        self.music = pygame.mixer.Sound(buffer=generate_music())
        self.music.set_volume(self.music_volume)
        self.music_on = True

        self.font_big = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.starfield = Starfield(self.width, self.height)

        # sprites
        self.alien_images = {
            0: make_alien(CRAB, (0, 220, 90), scale=3),
            1: make_alien(SQUID, (180, 60, 220), scale=3),
            2: make_alien(OCT, (60, 120, 255), scale=3),
        }
        self.mystery_image = make_mystery_ship()
        self.power_images = {
            "rapid": make_powerup_image("rapid"),
            "double": make_powerup_image("double"),
            "shield": make_powerup_image("shield"),
            "life": make_powerup_image("life"),
            "score": make_powerup_image("score"),
        }

        self.state = "MENU"
        self.level = 1
        self.score = 0
        self.combo = 0
        self.multiplier = 1.0
        self.lives = self.cfg["player"]["lives"]
        self.shake = 0.0
        self.level_clear_bonus = 0

        self.reset_game()

    # -- audio ------------------------------------------------------------
    def _build_sounds(self):
        def S(buf, vol=1.0):
            snd = pygame.mixer.Sound(buffer=buf)
            snd.set_volume(self.volume * vol)
            return snd

        return {
            "shoot": S(gen_tone(700, 0.08, wave="square", vol=0.5)),
            "alien_hit": S(gen_tone(220, 0.12, wave="square", vol=0.5)),
            "player_hit": S(gen_noise(0.35, vol=0.6)),
            "mystery": S(gen_sweep(400, 900, 0.5, vol=0.4)),
            "powerup": S(gen_tone(600, 0.18, wave="sine", vol=0.6)),
            "levelup": S(gen_tone(400, 0.25, wave="saw", vol=0.6, decay=False)),
            "gameover": S(gen_tone(160, 0.6, wave="saw", vol=0.5, decay=False)),
        }

    # -- level / game setup -----------------------------------------------
    def reset_game(self):
        self.score = 0
        self.combo = 0
        self.multiplier = 1.0
        self.lives = self.cfg["player"]["lives"]
        self.level = 1
        self.shots_fired = 0
        self.kills = 0
        self.elapsed = 0.0
        self.player = Player(self.cfg, self.height)
        self.start_level()

    def start_level(self):
        self.level_clear_bonus = 0
        self.player.reset_timers()
        self.player.lives = self.lives
        self.aliens = []
        self.alien_bullets = []
        self.player_bullets = []
        self.powerups = []
        self.particles = []
        self.mystery = None
        self.mystery_timer = 0.0
        self.fleet_dir = 1
        self.fleet_timer = 0.0
        self.fleet_down = False

        # Build alien fleet
        rows = min(self.cfg["alien"]["max_rows"], 4 + self.level // 2)
        cols = min(self.cfg["alien"]["max_cols"], 10 + self.level // 3)
        spacing_x = 52
        spacing_y = 46
        start_x = (self.width - (cols - 1) * spacing_x) // 2
        start_y = 70
        pts_map = self.cfg["alien"]["points"]
        for r in range(rows):
            for c in range(cols):
                typ = 2 if r == 0 else (1 if r < 3 else 0)
                img = self.alien_images[typ]
                alien = Alien(start_x + c * spacing_x, start_y + r * spacing_y, typ, img,
                              pts_map["crab"] if typ == 0 else pts_map["squid"] if typ == 1 else pts_map["octopus"],
                              self.level)
                self.aliens.append(alien)

        # Build barriers
        self.barriers = []
        bar_count = self.cfg["barrier"]["count"]
        bs = self.cfg["barrier"]["block_size"]
        bar_rows = self.cfg["barrier"]["rows"]
        bar_cols = self.cfg["barrier"]["cols"]
        bar_w = bar_cols * bs
        gap = self.width // (bar_count + 1)
        for i in range(bar_count):
            bx = gap * (i + 1) - bar_w // 2
            by = self.height - 180
            self.barriers.append(Barrier(bx, by, bar_rows, bar_cols,
                                         self.cfg["barrier"]["hp"], bs))

        # speed scaling
        self.speed_mult = 1 + self.cfg["alien"]["speed_per_level"] * (self.level - 1)
        self.alien_fire_chance = self.cfg["alien"]["fire_chance"] + \
            self.cfg["alien"]["fire_chance_per_level"] * (self.level - 1)
        self.alien_bullet_speed = 8 + self.level * 1.2

        # state -> playing after a brief intro
        self.state = "LEVEL_INTRO"
        self.intro_timer = 1.2

    def alive_aliens(self):
        return [a for a in self.aliens if a.alive]

    def fleet_bounds(self):
        alive = self.alive_aliens()
        if not alive:
            return 0, 0, 0, 0
        xs = [a.x for a in alive]
        ys = [a.y for a in alive]
        return min(xs), max(xs), min(ys), max(ys)

    # -- main loop ---------------------------------------------------------
    def run(self):
        self.music.play(loops=-1)
        running = True
        while running:
            dt = self.clock.tick(self.fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        self.state = "PAUSED" if self.state == "PLAYING" else "PLAYING"
                    elif event.key == pygame.K_m:
                        self.music_on = not self.music_on
                        self.music.set_volume(self.music_volume if self.music_on else 0)
                    elif event.key == pygame.K_RETURN:
                        if self.state == "MENU":
                            self.reset_game()
                            self.state = "LEVEL_INTRO"
                        elif self.state == "GAME_OVER":
                            self.reset_game()
                            self.state = "LEVEL_INTRO"
                        elif self.state == "PAUSED":
                            self.state = "PLAYING"

            keys = pygame.key.get_pressed()
            if self.state == "PLAYING":
                self.update(dt, keys)
            self.draw(dt, keys)

        # persist final progress
        self._persist_progress()
        pygame.quit()

    def _persist_progress(self):
        self.progress["high_score"] = max(self.progress.get("high_score", 0), self.score)
        self.progress["best_level"] = max(self.progress.get("best_level", 0), self.level)
        self.progress["games_played"] = self.progress.get("games_played", 0) + 1
        self.progress["total_shots"] = self.progress.get("total_shots", 0) + self.shots_fired
        self.progress["total_kills"] = self.progress.get("total_kills", 0) + self.kills
        self.progress["total_time"] = self.progress.get("total_time", 0.0) + self.elapsed
        save_progress(self.progress)

    # -- update ------------------------------------------------------------
    def update(self, dt, keys):
        self.elapsed += dt
        self.shake = max(0.0, self.shake - dt * 20)

        # player
        self.player.update(dt, keys, self.width)
        if keys[pygame.K_SPACE] and self.player.can_fire():
            self.fire_player_bullet()
            self.shots_fired += 1

        # alien fleet movement
        self.update_fleet(dt)

        # alien firing
        if random.random() < self.alien_fire_chance * dt * 60:
            self.fire_alien_bullet()

        # mystery bonus ship
        if self.mystery is None:
            self.mystery_timer += dt
            if self.mystery_timer > 6.0:
                self.mystery_timer = 0.0
                if random.random() < self.cfg["bonus"]["mystery_chance"] * 20:
                    self.spawn_mystery()
        else:
            self.mystery["x"] += self.mystery["dir"] * self.mystery["speed"] * dt * 60
            self.mystery["rect"].x = int(self.mystery["x"])
            if self.mystery["rect"].x < -50 or self.mystery["rect"].x > self.width:
                self.mystery = None

        # bullets
        self.update_bullets(dt)

        # powerups
        self.update_powerups(dt)

        # particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # check level clear
        if not self.alive_aliens():
            bonus = self.lives * 100 + self.level * 50
            self.score += bonus
            self.last_bonus = bonus
            self.sounds["levelup"].play()
            self.level += 1
            self.start_level()  # <-- this rebuilds the fleet & sets LEVEL_INTRO

        # combo decay? keep until hit

    def fire_player_bullet(self):
        self.player.fire()
        bx = self.player.rect.centerx - 2
        by = self.player.rect.top - 8
        speed = self.cfg["player"]["bullet_speed"]
        self.player_bullets.append(Bullet(bx, by, "player", speed, self.width, self.height))
        if self.player.double_timer > 0:
            self.player_bullets.append(Bullet(bx - 8, by, "player", speed, self.width, self.height))
            self.player_bullets.append(Bullet(bx + 8, by, "player", speed, self.width, self.height))
        self.sounds["shoot"].play()

    def update_fleet(self, dt):
        alive = self.alive_aliens()
        if not alive:
            return
        # movement speed increases as fewer aliens remain
        speed = self.cfg["alien"]["base_speed"] * self.speed_mult
        speed *= 1 + (1 - len(alive) / max(1, len(self.aliens))) * 3.0
        interval = max(0.05, 1.0 / speed)
        self.fleet_timer += dt
        if self.fleet_timer >= interval:
            self.fleet_timer = 0.0
            step = 12 * self.fleet_dir
            minx, maxx, _, _ = self.fleet_bounds()
            # move
            for a in alive:
                a.x += step
                a.rect.x = int(a.x)
            minx, maxx, _, _ = self.fleet_bounds()
            if maxx > self.width - 40:
                self.fleet_dir = -1
                self.fleet_down = True
            elif minx < 20:
                self.fleet_dir = 1
                self.fleet_down = True
            if self.fleet_down:
                self.fleet_down = False
                # step down
                miny = min(a.y for a in alive)
                maxy = max(a.y for a in alive)
                for a in alive:
                    a.y += 18
                    a.rect.y = int(a.y)

    def fire_alien_bullet(self):
        alive = self.alive_aliens()
        if not alive:
            return
        # pick a bottom-most alien in a random column
        target = random.choice(alive)
        self.alien_bullets.append(Bullet(target.rect.centerx, target.rect.bottom,
                                         "alien", self.alien_bullet_speed, self.width, self.height))

    def spawn_mystery(self):
        from_left = random.random() < 0.5
        x = -40 if from_left else self.width + 40
        rect = self.mystery_image.get_rect()
        rect.y = 60
        rect.x = int(x)
        self.mystery = {"x": float(x), "rect": rect, "dir": 1 if from_left else -1,
                        "speed": 3.5}
        self.sounds["mystery"].play()

    def update_bullets(self, dt):
        # player bullets
        for b in self.player_bullets:
            b.update(dt)
        # alien bullets
        for b in self.alien_bullets:
            b.update(dt)

        # player bullet collisions
        for b in list(self.player_bullets):
            if b.rect.bottom < 0:
                self.player_bullets.remove(b)
                continue
            # mystery
            if self.mystery and b.rect.colliderect(self.mystery["rect"]):
                pts = self.cfg["alien"]["points"]["mystery"] + self.level * 20
                self.score += int(pts * self.multiplier)
                self.spawn_particles(self.mystery["rect"].centerx, self.mystery["rect"].centery, (255, 60, 60), 14)
                self.sounds["alien_hit"].play()
                self.mystery = None
                self.player_bullets.remove(b)
                continue
            # aliens
            hit = False
            for a in self.alive_aliens():
                if b.rect.colliderect(a.rect):
                    a.alive = False
                    self.kills += 1
                    self.combo += 1
                    self.multiplier = min(self.cfg["bonus"]["combo_max_mult"],
                                          1 + self.combo * self.cfg["bonus"]["combo_mult_step"])
                    gain = int(a.points * self.multiplier)
                    self.score += gain
                    self.spawn_particles(a.rect.centerx, a.rect.centery, (0, 255, 120), 10)
                    self.sounds["alien_hit"].play()
                    # power-up drop
                    if random.random() < self.cfg["bonus"]["powerup_chance"]:
                        self.drop_powerup(a.rect.centerx, a.rect.centery)
                    self.player_bullets.remove(b)
                    hit = True
                    break
            if hit:
                continue
            # barriers
            for bar in self.barriers:
                if bar.hit(b.rect):
                    self.player_bullets.remove(b)
                    break

        # alien bullet collisions
        for b in list(self.alien_bullets):
            if b.rect.top > self.height:
                self.alien_bullets.remove(b)
                continue
            # player
            if b.rect.colliderect(self.player.rect):
                self.on_player_hit()
                self.alien_bullets.remove(b)
                continue
            # barriers
            for bar in self.barriers:
                if bar.hit(b.rect):
                    self.alien_bullets.remove(b)
                    break

    def drop_powerup(self, x, y):
        ptype = random.choice(["rapid", "double", "shield", "life", "score"])
        img = self.power_images[ptype]
        self.powerups.append(PowerUp(x, y, ptype, img))

    def on_player_hit(self):
        if self.player.shield:
            self.player.shield = False
            self.sounds["powerup"].play()
            self.shake = 4
            return
        self.lives -= 1
        self.player.lives = self.lives
        self.shake = 12
        self.sounds["player_hit"].play()
        self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (0, 220, 255), 18)
        if self.cfg["bonus"]["combo_reset_on_hit"]:
            self.combo = 0
            self.multiplier = 1.0
        if self.lives <= 0:
            self.state = "GAME_OVER"
            self.sounds["gameover"].play()
            self._persist_progress()

    def update_powerups(self, dt):
        for p in self.powerups:
            p.update(dt)
        for p in list(self.powerups):
            if p.rect.top > self.height:
                self.powerups.remove(p)
                continue
            if p.rect.colliderect(self.player.rect):
                self.apply_powerup(p.ptype)
                self.powerups.remove(p)

    def apply_powerup(self, ptype):
        self.sounds["powerup"].play()
        if ptype == "rapid":
            self.player.rapid_timer = self.cfg["player"]["rapid_duration"]
        elif ptype == "double":
            self.player.double_timer = self.cfg["player"]["double_duration"]
        elif ptype == "shield":
            self.player.shield = True
        elif ptype == "life":
            self.lives += 1
            self.player.lives = self.lives
        elif ptype == "score":
            self.score += 500

    def spawn_particles(self, x, y, color, count):
        for _ in range(count):
            vx = random.uniform(-140, 140)
            vy = random.uniform(-140, 140)
            self.particles.append(Particle(x, y, color, vx, vy, random.uniform(0.2, 0.7)))

    # -- drawing ------------------------------------------------------------
    def draw(self, dt, keys):
        self.starfield.draw(self.screen, dt)
        shake_x = random.randint(-int(self.shake), int(self.shake)) if self.shake else 0
        shake_y = random.randint(-int(self.shake), int(self.shake)) if self.shake else 0

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "GAME_OVER":
            self.draw_game_over()
        elif self.state == "PAUSED":
            self.draw_playing(shake_x, shake_y)
            self.draw_centered_text("PAUSED", self.font_big, (255, 255, 255))
        elif self.state == "LEVEL_INTRO":
            self.draw_playing(shake_x, shake_y)
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.state = "PLAYING"
            self.draw_centered_text(f"LEVEL {self.level}", self.font_big, (0, 255, 255))
            if getattr(self, "last_bonus", 0) > 0:
                b = self.font_small.render(f"BONUS +{self.last_bonus}", True, (255, 220, 60))
                self.screen.blit(b, (self.width // 2 - b.get_width() // 2,
                                     self.height // 2 + 60))
        else:
            self.draw_playing(shake_x, shake_y)

        pygame.display.flip()

    def draw_playing(self, shake_x, shake_y):
        # barriers
        for bar in self.barriers:
            bar.draw(self.screen)
        # powerups
        for p in self.powerups:
            p.draw(self.screen)
        # aliens
        for a in self.alive_aliens():
            self.screen.blit(a.image, a.rect)
        # mystery
        if self.mystery:
            self.screen.blit(self.mystery_image, self.mystery["rect"])
        # player
        self.screen.blit(self.player.image, self.player.rect)
        # bullets
        for b in self.player_bullets:
            b.draw(self.screen)
        for b in self.alien_bullets:
            b.draw(self.screen)
        # particles
        for p in self.particles:
            p.draw(self.screen)
        # HUD
        self.draw_hud()

    def draw_hud(self):
        text = f"SCORE {self.score}"
        s = self.font_med.render(text, True, (255, 255, 255))
        self.screen.blit(s, (16, 16))
        s = self.font_small.render(f"LEVEL {self.level}", True, (0, 255, 255))
        self.screen.blit(s, (16, 58))
        s = self.font_small.render(f"MULT x{self.multiplier:.1f}  COMBO {self.combo}", True, (255, 220, 60))
        self.screen.blit(s, (16, 84))
        # lives
        for i in range(self.lives):
            pygame.draw.circle(self.screen, (0, 220, 255), (self.width - 40 - i * 28, 30), 10)
        # high score
        hs = self.font_small.render(f"HI {self.progress.get('high_score', 0)}", True, (180, 180, 180))
        self.screen.blit(hs, (self.width - hs.get_width() - 16, 58))
        # status icons
        if self.player.shield:
            pygame.draw.circle(self.screen, (60, 220, 120), (self.width - 40, 58), 10)
        if self.player.rapid_timer > 0:
            pygame.draw.circle(self.screen, (255, 180, 40), (self.width - 70, 58), 10)
        if self.player.double_timer > 0:
            pygame.draw.circle(self.screen, (80, 200, 255), (self.width - 100, 58), 10)

    def draw_menu(self):
        title = self.font_big.render("SPACE", True, (0, 220, 255))
        title2 = self.font_big.render("INVADERS", True, (255, 60, 60))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 160))
        self.screen.blit(title2, (self.width // 2 - title2.get_width() // 2, 230))
        # demo aliens
        for i, img in enumerate(self.alien_images.values()):
            self.screen.blit(img, (self.width // 2 + i * 90 - 130, 330))
        hs = self.font_med.render(f"HIGH SCORE: {self.progress.get('high_score', 0)}", True, (255, 255, 255))
        self.screen.blit(hs, (self.width // 2 - hs.get_width() // 2, 420))
        instr = self.font_small.render("Press ENTER to start   |   P pause   |   M music   |   ESC quit",
                                       True, (180, 180, 180))
        self.screen.blit(instr, (self.width // 2 - instr.get_width() // 2, 480))
        # animated footer
        blink = 120 + 120 * math.sin(pygame.time.get_ticks() / 300)
        s = self.font_small.render("PRESS ENTER", True, (blink, blink, blink))
        self.screen.blit(s, (self.width // 2 - s.get_width() // 2, 540))

    def draw_game_over(self):
        txt = self.font_big.render("GAME OVER", True, (255, 60, 60))
        self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, 180))
        sc = self.font_med.render(f"FINAL SCORE: {self.score}", True, (255, 255, 255))
        self.screen.blit(sc, (self.width // 2 - sc.get_width() // 2, 280))
        lvl = self.font_med.render(f"LEVEL REACHED: {self.level}", True, (0, 255, 255))
        self.screen.blit(lvl, (self.width // 2 - lvl.get_width() // 2, 330))
        stats = self.font_small.render(
            f"SHOTS {self.shots_fired}   KILLS {self.kills}   ACCURACY "
            f"{int(100 * self.kills / max(1, self.shots_fired))}%", True, (200, 200, 200))
        self.screen.blit(stats, (self.width // 2 - stats.get_width() // 2, 380))
        hs = self.font_med.render(f"HIGH SCORE: {self.progress.get('high_score', 0)}", True, (255, 220, 60))
        self.screen.blit(hs, (self.width // 2 - hs.get_width() // 2, 430))
        blink = 120 + 120 * math.sin(pygame.time.get_ticks() / 300)
        s = self.font_small.render("PRESS ENTER TO RETRY", True, (blink, blink, blink))
        self.screen.blit(s, (self.width // 2 - s.get_width() // 2, 500))

    def draw_centered_text(self, text, font, color):
        s = font.render(text, True, color)
        self.screen.blit(s, (self.width // 2 - s.get_width() // 2, self.height // 2 - s.get_height() // 2))


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

