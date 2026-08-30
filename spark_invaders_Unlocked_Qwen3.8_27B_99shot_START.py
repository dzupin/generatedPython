# PROMPT USED:
# Write Space Invaders game in python using pygame library, make it visually appealing and polished but make sure to generate all graphic and sound files in python. Don't assume that user can download images and sound from internet, instead all resources for game should be generated in game. Also feel free to use external files (e.g. json) to store game parameters, progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Make sure to include in python generated sound and if possible also music, but music is optional.# Execution inststuction:
# COMMAND to execute xHigh:
# /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --temp 1.0 --top_p 0.95 --top_k 20 --min_p 0.0 --repeat-penalty 1.0 --presence-penalty 0.0  --spec-type draft-mtp --spec-draft-n-max 7 --chat-template-kwargs '{"reasoning_effort": "xhigh"}' --image-min-tokens 1024 --reasoning-preserve --parallel 1  --model /AI/models/Huihui-Qwen3.8-27B-abliterated-Q6_K_L.gguf  --mmproj /AI/models/mmproj-Qwen3.8-27B-BF16.gguf
# MODELS used:
#  /AI/models/Huihui-Qwen3.8-27B-abliterated-Q6_K_L.gguf  --mmproj /AI/models/mmproj-Qwen3.8-27B-BF16.gguf
#STATS: 51.352 generated tokens, time elapsed  53min:30s  15.99 t/s

# ERROR:
#/usr/bin/python3 /QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_0shot.py
#pygame 2.5.2 (SDL 2.30.0, Python 3.12.3)
#Hello from the pygame community. https://www.pygame.org/contribute.html
#Traceback (most recent call last):
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_0shot.py", line 1711, in <module>
#    main()
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_0shot.py", line 1704, in main
#    Game().run_loop()
#    ^^^^^^
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_0shot.py", line 890, in __init__
#    self.bank = SoundBank(None)  # replaced after config load
#                ^^^^^^^^^^^^^^^
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_0shot.py", line 243, in __init__
#    self.vol_music = cfg["audio"]["music_volume"]
#                     ~~~^^^^^^^^^
#TypeError: 'NoneType' object is not subscriptable
#
#Process finished with exit code 1

# Multiple hidden errors with first reported:
#/usr/bin/python3 /QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_99shot_START.py
#pygame 2.5.2 (SDL 2.30.0, Python 3.12.3)
#Hello from the pygame community. https://www.pygame.org/contribute.html
#Traceback (most recent call last):
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_99shot_START.py", line 1715, in <module>
#    main()
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_99shot_START.py", line 1708, in main
#    Game().run_loop()
#    ^^^^^^
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_99shot_START.py", line 894, in __init__
#    self.bank = SoundBank(None)  # replaced after config load
#                ^^^^^^^^^^^^^^^
#  File "/QA/generatedPython/spark_invaders_Unlocked_Qwen3.8_27B_99shot_START.py", line 247, in __init__
#    self.vol_music = cfg["audio"]["music_volume"]
#                     ~~~^^^^^^^^^
#TypeError: 'NoneType' object is not subscriptable
#
#Process finished with exit code 1



import os
import sys
import json
import math
import random
import array
import colorsys
import datetime

import pygame

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
W, H = 800, 600
FPS = 60
SR = 22050                      # sample rate used for all synthesized audio
TILE = 6                        # bunker tile size (px)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ----------------------------------------------------------------------------
# JSON persistence (config / stats / progress)
# ----------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "player":   {"speed": 300, "bullet_speed": 520, "fire_cooldown": 0.34,
                 "start_lives": 3, "max_lives": 5, "invuln_time": 2.5},
    "invaders": {"base_speed": 46, "step_down": 26, "bullet_speed": 190,
                 "max_bullets": 8, "fire_rate": 0.85, "rows": 5, "cols": 11,
                 "spacing_x": 44, "spacing_y": 34},
    "points":   {"squid": 10, "crab": 20, "octopus": 30, "diver": 50},
    "ufo":      {"min_interval": 11, "max_interval": 21, "speed": 130,
                 "values": [100, 150, 300, 500, 1000]},
    "combo":    {"window": 1.5, "max": 8},
    "powerups": {"chance": 0.16, "drop_speed": 130, "life_chance": 0.07,
                 "double_time": 10, "rapid_time": 8, "shield_time": 8,
                 "score_time": 12, "bomb_value": 40},
    "diver":    {"first_wave": 3, "base_interval": 16, "speed": 150},
    "levels":   {"clear_base": 100, "clear_per_life": 50,
                 "max_rows": 7, "start_offset_per_wave": 6},
    "audio":    {"music_volume": 0.5, "sfx_volume": 0.8},
    "difficulty": {"normal":  {"speed": 1.00, "fire": 1.00, "lives": 3},
                   "hard":    {"speed": 1.22, "fire": 1.35, "lives": 3},
                   "extreme": {"speed": 1.45, "fire": 1.70, "lives": 2}},
}

DEFAULT_STATS = {
    "games_played": 0, "total_score": 0, "high_score": 0, "best_wave": 0,
    "invaders_killed": 0, "bullets_fired": 0, "invaders_hit": 0,
    "powerups_collected": 0, "ufo_kills": 0, "bombs_used": 0,
    "best_combo": 0, "total_play_seconds": 0,
}

DEFAULT_PROGRESS = {
    "high_score": 0, "best_wave": 0, "last_score": 0, "last_wave": 0,
    "last_difficulty": "normal", "last_played": "",
}


def _deep_merge(base, override):
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_json(name, default):
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _deep_merge(default, data) if isinstance(default, dict) else data
    except Exception:
        return json.loads(json.dumps(default))


def save_json(name, obj):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, name)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


# ----------------------------------------------------------------------------
# Audio synthesis (pure-python sample generation -> pygame.mixer.Sound)
# ----------------------------------------------------------------------------
def _phase(f0, f1, dur, t):
    """Exact phase for a linear frequency ramp f0 -> f1 over dur."""
    return 2 * math.pi * (f0 * t + (f1 - f0) * t * t / (2.0 * dur))


def _clamp(v):
    return max(-1.0, min(1.0, v))


def render_sfx(dur, voices):
    """voices: list of (start_time, fn) where fn(t)->float in [-1,1]."""
    n = int(dur * SR)
    out = array.array("h")
    for i in range(n):
        t = i / SR
        v = 0.0
        for t0, fn in voices:
            if t >= t0:
                v += fn(t - t0)
        out.append(int(_clamp(v) * 30000))
    return out


def v_square(f0, f1, dur, vol=0.5, attack=0.004):
    def fn(t):
        if t < 0 or t >= dur:
            return 0.0
        p = _phase(f0, f1, dur, t)
        env = min(1.0, t / attack) * (1.0 - t / dur) ** 1.3
        v = (1.0 if math.sin(p) >= 0 else -1.0) * 0.7 + 0.3 * math.sin(p)
        return v * vol * env
    return fn


def v_sine(f0, f1, dur, vol=0.5, attack=0.003):
    def fn(t):
        if t < 0 or t >= dur:
            return 0.0
        p = _phase(f0, f1, dur, t)
        env = min(1.0, t / attack) * (1.0 - t / dur) ** 1.1
        return math.sin(p) * vol * env
    return fn


def v_noise(dur, vol=0.5, decay=1.8):
    def fn(t):
        if t < 0 or t >= dur:
            return 0.0
        return random.uniform(-1.0, 1.0) * vol * (1.0 - t / dur) ** decay
    return fn


def _arp(freqs, note=0.07, shape="square", vol=0.4):
    voices = []
    t = 0.0
    for f in freqs:
        voices.append((t, (v_square if shape == "square" else v_sine)(f, f, note, vol)))
        t += note * 0.85
    return voices, t + note


MIDI = lambda m: 440.0 * (2.0 ** ((m - 69) / 12.0))

# --- chiptune soundtrack -----------------------------------------------------
_LEAD = [
    [(0, 69), (2, 72), (4, 76), (6, 74), (8, 72), (10, 69), (12, 67), (14, 69)],
    [(0, 72), (2, 76), (4, 79), (6, 76), (8, 74), (10, 72), (12, 74), (14, 76)],
    [(0, 79), (2, 76), (4, 74), (6, 72), (8, 71), (10, 69), (12, 67), (14, 65)],
    [(0, 69), (2, 72), (4, 74), (6, 76), (8, 81), (10, 79), (12, 76), (14, 74)],
]
_BASS = [
    [(0, 45), (2, 45), (4, 48), (6, 48), (8, 43), (10, 43), (12, 41), (14, 41)],
    [(0, 40), (2, 40), (4, 43), (6, 43), (8, 38), (10, 38), (12, 45), (14, 45)],
    [(0, 38), (2, 38), (4, 45), (6, 45), (8, 41), (10, 41), (12, 40), (14, 40)],
    [(0, 45), (2, 45), (4, 40), (6, 40), (8, 45), (10, 45), (12, 40), (14, 40)],
]


def render_music(events, total_dur):
    """events: (start, dur, freq, kind, vol); kinds: lead/bass/kick/hat."""
    n = int(total_dur * SR)
    buf = [0.0] * n
    for t0, dur, freq, kind, vol in events:
        i0 = int(t0 * SR)
        nd = int(dur * SR)
        for k in range(nd):
            i = i0 + k
            if i >= n:
                break
            t = k / SR
            p = 2.0 * math.pi * freq * t
            if kind == "lead":
                env = min(1.0, t / 0.004) * math.exp(-t * 9.0)
                s = (1.0 if math.sin(p) >= 0 else -1.0) * 0.6 + 0.4 * math.sin(p)
            elif kind == "bass":
                env = min(1.0, t / 0.004) * math.exp(-t * 4.0)
                s = math.asin(math.sin(p)) * (2.0 / math.pi)
            elif kind == "kick":
                pk = _phase(120.0, 45.0, 0.13, min(t, 0.13))
                env = (1.0 - t / dur) ** 2.0
                s = math.sin(pk)
            else:  # hat
                env = (1.0 - t / dur) ** 3.0
                s = random.uniform(-1.0, 1.0)
            buf[i] += s * vol * env
    peak = max(1e-6, max(abs(x) for x in buf))
    scale = 0.72 / peak
    out = array.array("h")
    for x in buf:
        out.append(int(_clamp(x * scale) * 30000))
    return out


class _NullSound:
    """Fallback if the machine has no audio device - game still runs."""
    def play(self, *a, **k): pass
    def stop(self): pass
    def set_volume(self, v): pass
    def set_num_repeats(self, n): pass


class SoundBank:
    def __init__(self, cfg):
        self.ok = pygame.mixer.get_init() is not None
        self.muted = False
        self.vol_music = cfg["audio"]["music_volume"]
        self.vol_sfx = cfg["audio"]["sfx_volume"]
        self.sfx = {}
        self.music = _NullSound()
        self.ufo = _NullSound()
        if not self.ok:
            return
        S = pygame.mixer.Sound
        def snd(arr):
            return S(buffer=arr.tobytes())

        # --- sound effects ---
        arp, dur = _arp([523.25, 659.25, 783.99, 1046.5], 0.07, "square", 0.35)
        self.sfx["powerup"]   = snd(render_sfx(dur + 0.1, arp))
        arp, dur = _arp([660.0, 880.0, 1318.5], 0.09, "square", 0.4)
        self.sfx["life"]      = snd(render_sfx(dur + 0.1, arp))
        arp, dur = _arp([523.25, 659.25, 783.99, 1046.5, 1318.5], 0.08, "square", 0.35)
        self.sfx["levelup"]   = snd(render_sfx(dur + 0.1, arp))
        arp, dur = _arp([392.0, 311.13, 261.63, 196.0], 0.16, "square", 0.4)
        self.sfx["gameover"]  = snd(render_sfx(dur + 0.1, arp))
        arp, dur = _arp([1568.0, 1244.5, 1046.5, 783.99], 0.06, "square", 0.35)
        self.sfx["ufo_kill"]  = snd(render_sfx(dur + 0.08, arp))
        self.sfx["shoot"]     = snd(render_sfx(0.10, [(0, v_square(950, 300, 0.10, 0.30))]))
        self.sfx["inv_die"]   = snd(render_sfx(0.16, [(0, v_square(620, 170, 0.14, 0.35)),
                                                      (0, v_noise(0.10, 0.25, 2.5))]))
        self.sfx["explode"]   = snd(render_sfx(0.7,  [(0, v_noise(0.7, 0.85, 1.6)),
                                                      (0, v_sine(90, 38, 0.6, 0.6))]))
        self.sfx["bomb"]      = snd(render_sfx(0.9,  [(0, v_noise(0.9, 0.9, 1.4)),
                                                      (0, v_sine(140, 30, 0.8, 0.8))]))
        self.sfx["shield"]    = snd(render_sfx(0.18, [(0, v_square(1250, 900, 0.10, 0.25)),
                                                      (0, v_sine(1568, 1568, 0.16, 0.25))]))
        self.sfx["select"]    = snd(render_sfx(0.06, [(0, v_square(880, 880, 0.05, 0.3))]))
        self.sfx["step1"]     = snd(render_sfx(0.09, [(0, v_square(96, 96, 0.08, 0.5))]))
        self.sfx["step2"]     = snd(render_sfx(0.09, [(0, v_square(82, 82, 0.08, 0.5))]))

        # combo blips (pitch rises with chain)
        self.combo_blips = []
        for i in range(8):
            f = 440.0 * (1.0 + 0.15 * i)
            self.combo_blips.append(snd(render_sfx(0.07, [(0, v_square(f, f * 1.3, 0.06, 0.25))])))

        # UFO warble (looped while the saucer is on screen)
        def warble(t):
            if t < 0 or t >= 0.6:
                return 0.0
            om = 2.0 * math.pi * 4.5 * t
            f = 430.0 + 240.0 * math.sin(om)
            phase = 2.0 * math.pi * (430.0 * t + 240.0 * (1.0 - math.cos(om)) / (2.0 * math.pi * 4.5))
            return math.sin(phase) * 0.30
        n = int(0.6 * SR)
        arr = array.array("h", (int(warble(i / SR) * 30000) for i in range(n)))
        self.ufo = snd(arr)
        self.ufo.set_num_repeats(-1)

        # --- looping chiptune music (original composition, A minor) ---
        step = 0.1  # 16th note @ 150 BPM -> 4 bars = 6.4 s loop
        events = []
        for b in range(4):
            for st, m in _LEAD[b]:
                events.append(((b * 16 + st) * step, 0.16, MIDI(m), "lead", 0.50))
            for st, m in _BASS[b]:
                events.append(((b * 16 + st) * step, 0.19, MIDI(m), "bass", 0.45))
            for st in (0, 8):
                events.append(((b * 16 + st) * step, 0.13, 0.0, "kick", 0.55))
            for st in (2, 6, 10, 14):
                events.append(((b * 16 + st) * step, 0.05, 0.0, "hat", 0.14))
        self.music = snd(render_music(events, 64 * step))
        self.music.set_num_repeats(-1)
        self.set_volumes()

    def set_volumes(self):
        if not self.ok:
            return
        base = 0.0 if self.muted else 1.0
        self.music.set_volume(self.vol_music * base)
        for s in self.sfx.values():
            s.set_volume(self.vol_sfx * base)
        for s in self.combo_blips:
            s.set_volume(self.vol_sfx * base)
        self.ufo.set_volume(self.vol_sfx * 0.8 * base)

    def toggle_mute(self):
        self.muted = not self.muted
        self.set_volumes()
        return self.muted

    def play(self, name):
        if self.ok and not self.muted and name in self.sfx:
            self.sfx[name].play()

    def play_combo(self, n):
        if self.ok and not self.muted:
            self.combo_blips[min(n, len(self.combo_blips) - 1)].play()

    def play_music(self):
        if self.ok and not self.muted:
            self.music.play()

    def stop_music(self):
        if self.ok:
            self.music.stop()


# ----------------------------------------------------------------------------
# Procedural graphics
# ----------------------------------------------------------------------------
def pixel_art(pattern, palette, scale=3):
    h, w = len(pattern), len(pattern[0])
    s = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            col = palette.get(ch)
            if col:
                s.fill(col, (x * scale, y * scale, scale, scale))
    return s


def add_glow(surf, color, size=3, alpha=150):
    """Blur+re-scale the sprite to make a soft colored halo (build time only)."""
    w, h = surf.get_size()
    small = pygame.Surface((max(2, w // 4), max(2, h // 4)), pygame.SRCALPHA)
    small.blit(surf, (0, 0))
    glow = pygame.transform.smoothscale(small, (w + size * 2, h + size * 2))
    for y in range(glow.get_height()):
        for x in range(glow.get_width()):
            a = glow.get_at((x, y)).a
            if a:
                glow.set_at((x, y), (color[0], color[1], color[2], min(255, a * alpha // 255)))
    out = pygame.Surface((w + size * 2, h + size * 2), pygame.SRCALPHA)
    out.blit(glow, (0, 0))
    out.blit(surf, (size, size))
    return out


def hsv(h, s=0.75, v=0.95):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def shadow_text(text, font, color, shadow=(10, 10, 25)):
    t = font.render(text, True, color)
    s = font.render(text, True, shadow)
    out = s.copy()
    out.blit(t, (2, 2))
    return out


class SpriteBank:
    """Pre-renders every sprite the game needs (once, at startup)."""
    def __init__(self):
        # -- pixel patterns ------------------------------------------------
        self.SQUID = [
            "..X.....X..", "...X...X...", "..XXXXXXX..", ".XX.XXX.XX.",
            "XXXXXXXXXXX", "..X.X.X.X..", ".X..XXX..X.", "X.X.....X.X"]
        self.SQUID2 = [
            "..X.....X..", "X..X...X..X", "X.XXXXXXX.X", "XXX.XXX.XXX",
            "XXXXXXXXXXX", ".X.XXXX.X.X", "..X.....X..", ".X.......X."]
        self.CRAB = [
            "..X..X..X..", ".X.XXX.X.X.", "XXXXXXXXXXX", "XX.XXXXX.XX",
            "XXXXXXXXXXX", "X.XXXXXXX.X", "X.X.....X.X", "..XX...XX.."]
        self.CRAB2 = [
            "..X..X..X..", ".X.XXX.X.X.", "XXXXXXXXXXX", "XX.XXXXX.XX",
            "XXXXXXXXXXX", ".X.XXXX.X.X", "..X.X.X.X..", ".X.X...X.X."]
        self.OCTO = [
            "...XXXXX...", "XXX.XXX.XXX", "XXXXXXXXXXX", "XX.XXXXX.XX",
            "XXXXXXXXXXX", "..XXX.XXX..", ".XX.X.X.XX.", "X..XX.XX..X"]
        self.OCTO2 = [
            "...XXXXX...", "XXX.XXX.XXX", "XXXXXXXXXXX", "XX.XXXXX.XX",
            "XXXXXXXXXXX", "..XX...XX..", ".X.X...X.X.", "X.X.....X.X"]
        self.SHIP = [
            ".....C.....", "....CCC....", "....CCC....", ".XXXXXXXXX.",
            "XXXXXXXXXXX", "XXXXXXXXXXX", "X.XXX.XXX.X"]
        self.SAUCER = [
            "...XXXXX...", "..XXXXXXX..", "XXXXXXXXXXX", "XOOXOOXOOXO", ".XXXXXXXXX."]
        self.DART = [
            ".....X.....", "....XXX....", "...XXXXX...", ".XXXXXXXXX.", "..XX.X.XX.."]
        self.ZIG1 = ["XX...", ".XX..", "..XX.", "...XX", "..XX.", ".XX..",
                     "XX...", ".XX..", "..XX.", "...XX", "..XX.", ".XX.."]
        self.ZIG2 = ["...XX", "..XX.", ".XX..", "XX...", ".XX..", "..XX.",
                     "...XX", "..XX.", ".XX..", "XX...", ".XX..", "..XX."]

        # -- invaders (per-type frames, per-wave palette shift) ------------
        base = {"A": (0.36, 10), "B": (0.52, 20), "C": (0.88, 30)}
        self.invader_base = base
        self.invader_imgs = {}
        for t, (hue, pts) in base.items():
            pat = {"A": (self.SQUID, self.SQUID2),
                   "B": (self.CRAB, self.CRAB2),
                   "C": (self.OCTO, self.OCTO2)}[t]
            col = hsv(hue)
            dark = tuple(int(c * 0.55) for c in col)
            self.invader_imgs[t] = [
                pixel_art(p, {".": None, "X": col}, 3) for p in pat]
            self.invader_pts[t] = pts
            self.invader_col[t] = col
        self.diver_img = add_glow(pixel_art(self.DART, {".": None, "X": (255, 150, 50)}, 3),
                                  (255, 140, 40), 2, 130)
        self.diver_col = (255, 150, 50)

        # -- player ---------------------------------------------------------
        ship = pixel_art(self.SHIP, {".": None, "X": (80, 170, 255), "C": (190, 250, 255)}, 3)
        self.player_img = add_glow(ship, (70, 160, 255), 2, 110)
        self.player_life = pygame.transform.scale(ship, (18, 12))
        try:
            pygame.display.set_icon(ship)
        except Exception:
            pass

        # -- bullets ---------------------------------------------------------
        pb = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(pb, (0, 170, 255, 90), (0, 0, 6, 16), border_radius=3)
        pygame.draw.rect(pb, (170, 240, 255, 220), (1, 2, 4, 12), border_radius=2)
        pygame.draw.rect(pb, (255, 255, 255, 255), (2, 3, 2, 10))
        self.player_bullet = pb
        eb1 = pixel_art(self.ZIG1, {".": None, "X": (255, 200, 70)}, 2)
        eb2 = pixel_art(self.ZIG2, {".": None, "X": (255, 200, 70)}, 2)
        self.enemy_bullets = [add_glow(eb1, (255, 150, 40), 1, 100),
                              add_glow(eb2, (255, 150, 40), 1, 100)]
        self.saucer_on = add_glow(pixel_art(self.SAUCER, {".": None, "X": (255, 120, 160),
                                                          "O": (255, 255, 255)}, 4),
                                  (255, 90, 140), 3, 150)
        self.saucer_off = add_glow(pixel_art(self.SAUCER, {".": None, "X": (255, 120, 160),
                                                           "O": (120, 40, 70)}, 4),
                                   (255, 90, 140), 3, 150)

        # -- power-up badges --------------------------------------------------
        font = pygame.font.Font(None, 26)
        specs = [("double", "D", (90, 200, 255)), ("rapid", "R", (255, 170, 60)),
                 ("shield", "S", (110, 240, 140)), ("bomb", "B", (255, 90, 90)),
                 ("score", "x2", (255, 220, 90)), ("life", "1UP", (255, 130, 200))]
        self.power_icons = {}
        for key, label, col in specs:
            s = pygame.Surface((34, 34), pygame.SRCALPHA)
            pygame.draw.rect(s, tuple(int(c * 0.35) for c in col), (3, 3, 28, 28),
                             border_radius=8)
            pygame.draw.rect(s, col, (3, 3, 28, 28), width=2, border_radius=8)
            pygame.draw.rect(s, (255, 255, 255, 90), (6, 6, 22, 6), border_radius=3)
            f = font if label != "1UP" else pygame.font.Font(None, 16)
            txt = f.render(label, True, (255, 255, 255))
            s.blit(txt, txt.get_rect(center=(17, 19)))
            self.power_icons[key] = add_glow(s, col, 2, 120)

    def invader_image(self, t, frame, wave):
        hue = (self.invader_base[t][0] + wave * 0.055) % 1.0
        return self.invader_imgs[t][frame]  # palette is baked per-type; wave
    def recolor_wave(self, wave):
        """Re-bake invader palettes with a hue shift for the current wave."""
        for t, (hue, pts) in self.invader_base.items():
            col = hsv(hue + wave * 0.055)
            pat = {"A": (self.SQUID, self.SQUID2),
                   "B": (self.CRAB, self.CRAB2),
                   "C": (self.OCTO, self.OCTO2)}[t]
            self.invader_imgs[t] = [pixel_art(p, {".": None, "X": col}, 3) for p in pat]
            self.invader_col[t] = col


# ----------------------------------------------------------------------------
# Background: parallax stars + generated nebulae
# ----------------------------------------------------------------------------
class Background:
    def __init__(self):
        self.bg = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            c = (int(4 + 6 * t), int(6 + 8 * t), int(16 + 18 * t))
            self.bg.fill(c, (0, y, W, 1))
        self.nebulae = []
        for col, (x, y) in [((120, 60, 200), (180, 150)), ((40, 120, 220), (620, 420)),
                            ((30, 180, 160), (420, 90))]:
            s = pygame.Surface((420, 420), pygame.SRCALPHA)
            for r in range(200, 0, -6):
                a = int(14 * (1 - r / 200))
                pygame.draw.circle(s, (col[0], col[1], col[2], max(0, a)),
                                   (210, 210), r)
            small = pygame.transform.smoothscale(s, (105, 105))
            s = pygame.transform.smoothscale(small, (420, 420))
            self.nebulae.append([pygame.Vector2(x - 210, y - 210), s,
                                 random.uniform(-4, 4), random.uniform(2, 6)])
        self.stars = []
        for layer in range(3):
            n = [40, 26, 14][layer]
            for _ in range(n):
                self.stars.append({
                    "x": random.uniform(0, W), "y": random.uniform(0, H),
                    "speed": [6, 14, 26][layer],
                    "size": [1, 1, 2][layer],
                    "tw": random.uniform(0, math.tau),
                    "alpha": [110, 160, 235][layer],
                })

    def update(self, dt):
        for s in self.stars:
            s["y"] += s["speed"] * dt
            s["tw"] += dt * random.uniform(1.0, 2.5)
            if s["y"] > H:
                s["y"] = -2
                s["x"] = random.uniform(0, W)
        for n in self.nebulae:
            n[0].x += n[2] * dt
            if n[0].x < -420: n[0].x = W
            if n[0].x > W: n[0].x = -420

    def draw(self, screen, t):
        screen.blit(self.bg, (0, 0))
        for pos, img, _, _ in self.nebulae:
            screen.blit(img, (int(pos.x), int(pos.y)))
        for s in self.stars:
            a = int(s["alpha"] * (0.65 + 0.35 * math.sin(s["tw"])))
            screen.fill((min(255, a), min(255, a), 255),
                        (int(s["x"]), int(s["y"]), s["size"], s["size"]))


# ----------------------------------------------------------------------------
# Simple particle / float-text helpers
# ----------------------------------------------------------------------------
class Particles:
    MAX = 380
    def __init__(self):
        self.items = []
        self.rings = []

    def burst(self, x, y, color, n=22, speed=220, size=3, life=0.55):
        for _ in range(n):
            if len(self.items) >= self.MAX:
                self.items.pop(0)
            a = random.uniform(0, math.tau)
            v = random.uniform(0.2, 1.0) * speed
            self.items.append({"x": x, "y": y, "vx": math.cos(a) * v,
                               "vy": math.sin(a) * v, "life": life * random.uniform(0.5, 1.2),
                               "max": life, "size": size * random.uniform(0.6, 1.4),
                               "col": color})

    def spark(self, x, y, color=(200, 255, 255), n=5, speed=120):
        self.burst(x, y, color, n=n, speed=speed, size=2, life=0.3)

    def ring(self, x, y, color, max_r=140):
        self.rings.append({"x": x, "y": y, "r": 6, "max_r": max_r, "col": color})

    def update(self, dt):
        for p in self.items:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vx"] *= (1 - 2.2 * dt)
            p["vy"] *= (1 - 2.2 * dt)
            p["life"] -= dt
        self.items = [p for p in self.items if p["life"] > 0]
        for r in self.rings:
            r["r"] += 480 * dt
        self.rings = [r for r in self.rings if r["r"] < r["max_r"]]

    def draw(self, surf):
        for r in self.rings:
            a = int(220 * (1 - r["r"] / r["max_r"]))
            pygame.draw.circle(surf, r["col"], (int(r["x"]), int(r["y"])),
                               int(r["r"]), max(1, int(4 * (1 - r["r"] / r["max_r"]))) )
        for p in self.items:
            f = max(0.0, p["life"] / p["max"])
            s = max(1, int(p["size"] * f))
            surf.fill(p["col"], (int(p["x"] - s / 2), int(p["y"] - s / 2), s, s))


class FloatTexts:
    def __init__(self, font):
        self.font = font
        self.items = []

    def add(self, x, y, text, color=(255, 255, 255), size=20, life=0.9):
        f = self.font
        s = f.render(text, True, color)
        sh = f.render(text, True, (8, 8, 20))
        full = sh.copy()
        full.blit(s, (1, 1))
        self.items.append({"x": x, "y": y, "life": life, "max": life, "img": full})

    def update(self, dt):
        for t in self.items:
            t["y"] -= 34 * dt
            t["life"] -= dt
        self.items = [t for t in self.items if t["life"] > 0]

    def draw(self, surf):
        for t in self.items:
            img = t["img"].copy()
            img.set_alpha(int(255 * max(0.0, t["life"] / t["max"])))
            surf.blit(img, (int(t["x"] - img.get_width() / 2), int(t["y"])))


# ----------------------------------------------------------------------------
# Bunker (destructible barrier)
# ----------------------------------------------------------------------------
class Bunker:
    CW, CH = 22, 16
    def __init__(self, x, y):
        self.x, self.y, self.ts = x, y, TILE
        self.w, self.h = self.CW * TILE, self.CH * TILE
        self.alive = [[self._shape(x, y) for x in range(self.CW)] for y in range(self.CH)]
        self.dirty = True
        self.img = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

    def _shape(self, x, y):
        if x < 0 or y < 0 or x >= self.CW or y >= self.CH:
            return False
        if y == 0: return 4 <= x < 18
        if y == 1: return 3 <= x < 19
        if y == 2: return 2 <= x < 20
        return True

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def _rebuild(self):
        if not self.dirty:
            return
        self.img.fill((0, 0, 0, 0))
        bright, dark = (70, 235, 150), (25, 120, 80)
        for y in range(self.CH):
            for x in range(self.CW):
                if self.alive[y][x]:
                    px, py = self.x + x * TILE, self.y + y * TILE
                    self.img.fill(bright, (px - self.x, py - self.y, TILE, TILE))
                    self.img.fill(dark, (px - self.x + TILE - 1, py - self.y, 1, TILE))
                    self.img.fill(dark, (px - self.x, py - self.y + TILE - 1, TILE, 1))
        self.dirty = False

    def hit_tiles(self, rx0, ry0, rx1, ry1):
        """Return list of tile coords of alive tiles overlapping a pixel rect."""
        tx0 = max(0, int((rx0 - self.x) // TILE) - 1)
        ty0 = max(0, int((ry0 - self.y) // TILE) - 1)
        tx1 = min(self.CW - 1, int((rx1 - self.x) // TILE) + 1)
        ty1 = min(self.CH - 1, int((ry1 - self.y) // TILE) + 1)
        out = []
        for ty in range(ty0, ty1 + 1):
            for tx in range(tx0, tx1 + 1):
                if self.alive[ty][tx]:
                    out.append((tx, ty))
        return out

    def erode(self, px, py, radius=1.6):
        """Destroy tiles within radius (in tiles) of a pixel point. Returns hit?"""
        cx = (px - self.x) / TILE
        cy = (py - self.y) / TILE
        r = int(math.ceil(radius))
        hit = False
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= radius * radius:
                    tx, ty = int(cx) + dx, int(cy) + dy
                    if 0 <= tx < self.CW and 0 <= ty < self.CH and self.alive[ty][tx]:
                        self.alive[ty][tx] = False
                        hit = True
        if hit:
            self.dirty = True
        return hit

    def destroy_rect(self, r):
        tiles = self.hit_tiles(r.left - 2, r.top - 2, r.right + 2, r.bottom + 2)
        if not tiles:
            return False
        for tx, ty in tiles:
            self.alive[ty][tx] = False
        self.dirty = True
        return True

    def draw(self, surf):
        self._rebuild()
        surf.blit(self.img, (self.x, self.y))


# ----------------------------------------------------------------------------
# Entities
# ----------------------------------------------------------------------------
class Bullet:
    __slots__ = ("x", "y", "vx", "vy", "alive", "owner")
    def __init__(self, x, y, vx, vy, owner):
        self.x, self.y, self.vx, self.vy, self.owner, self.alive = x, y, vx, vy, owner, True
    @property
    def rect(self):
        w = 6 if self.owner == "player" else 12
        h = 16 if self.owner == "player" else 24
        return pygame.Rect(int(self.x - w / 2), int(self.y - h / 2), w, h)


class Invader:
    __slots__ = ("type", "col", "row", "x", "y", "alive", "phase")
    def __init__(self, t, col, row):
        self.type, self.col, self.row, self.alive = t, col, row, True
        self.x = self.y = 0
        self.phase = random.uniform(0, math.tau)


class Formation:
    def __init__(self, level, cfg, bank):
        iv = cfg["invaders"]
        self.level = level
        self.cfg = cfg
        self.bank = bank
        self.rows = min(iv["rows"] + (level - 1) // 3, iv["max_rows"] if "max_rows" in iv else 7)
        self.cols = iv["cols"]
        self.dx = 1.0
        self.oy = 84 + min((level - 1) * cfg["levels"]["start_offset_per_wave"], 60)
        self.spawn_t = 0.0          # >0 while dropping in
        self.fire_t = random.uniform(0.6, 1.4)
        self.anim_t = 0.0
        self.step_t = 0.0
        self.total = self.rows * self.cols
        types = []
        for r in range(self.rows):
            if r == 0: t = "A"
            elif r <= 2: t = "B"
            else: t = "C"
            types.append(t)
        self.invaders = [Invader(types[r], c, r) for r in range(self.rows) for c in range(self.cols)]
        self._place()

    def _place(self):
        iv = self.cfg["invaders"]
        fx = iv["spacing_x"]
        fy = iv["spacing_y"]
        ox = (W - (self.cols - 1) * fx) / 2
        for inv in self.invaders:
            inv.x = ox + inv.col * fx
            inv.y = self.oy + inv.row * fy

    def update(self, dt, g):
        if self.spawn_t > 0:
            self.spawn_t -= dt
            self.oy += 70 * dt
            self._place()
            return
        alive = [i for i in self.invaders if i.alive]
        if not alive:
            return
        ratio = len(alive) / self.total
        iv = self.cfg["invaders"]
        dmod = g.diff_mod()
        speed = iv["base_speed"] * dmod["speed"] * (1 + 0.13 * (self.level - 1)) \
                * (0.5 + 1.3 * (1 - ratio))
        self.anim_t += dt * (0.8 + 2.2 * (1 - ratio))
        self.step_t += dt
        if self.step_t >= max(0.22, 0.5 - 0.35 * (1 - ratio)):
            self.step_t = 0.0
            self.bank.play("step1" if self.step_flag else "step2")
            self.step_flag = not self.step_flag
        self.xoff = getattr(self, "xoff", 0.0)
        self.xoff += self.dx * speed * dt
        mx = 18
        if self.xoff > mx:
            self.xoff = mx
            self.dx = -1.0
            self._step_down()
        elif self.xoff < -mx:
            self.xoff = -mx
            self.dx = 1.0
            self._step_down()
        for inv in self.invaders:
            if inv.alive:
                inv.x += self.dx * speed * dt
                inv.y = self.oy + inv.row * iv["spacing_y"]

    def _step_down(self):
        self.oy += self.cfg["invaders"]["step_down"]

    def rect_of(self, inv):
        w, h = 33, 24
        return pygame.Rect(int(inv.x - w / 2), int(inv.y - h / 2), w, h)

    def lowest_in_column(self, col):
        best = None
        for inv in self.invaders:
            if inv.alive and inv.col == col and (best is None or inv.y > best.y):
                best = inv
        return best

    def invader_at_rect(self, r):
        for inv in self.invaders:
            if inv.alive and self.rect_of(inv).colliderect(r):
                return inv
        return None

    def alive_count(self):
        return sum(1 for i in self.invaders if i.alive)


class UFO:
    def __init__(self, level, cfg):
        self.cfg = cfg
        side = random.choice([-1, 1])
        self.x = -60 if side < 0 else W + 60
        self.vx = cfg["ufo"]["speed"] * (1 + 0.05 * level) * (-side)
        self.y = 64
        self.alive = True
        self.value = random.choices(cfg["ufo"]["values"],
                                    weights=[30, 25, 20, 15, 10])[0]
    @property
    def rect(self):
        return pygame.Rect(int(self.x - 22), int(self.y - 10), 44, 20)


class Diver:
    """Fast sine-wave attacker that appears from wave 3 on."""
    def __init__(self, level, cfg):
        self.cfg = cfg
        self.x = random.uniform(80, W - 80)
        self.y = -20
        self.t = 0.0
        self.ampl = random.uniform(30, 70)
        self.freq = random.uniform(2.2, 3.4)
        self.speed = cfg["diver"]["speed"] * (1 + 0.07 * level)
        self.base_x = self.x
        self.shot = False
        self.alive = True
    @property
    def rect(self):
        return pygame.Rect(int(self.x - 16), int(self.y - 8), 32, 16)


class PowerUp:
    TYPES = ["double", "rapid", "shield", "bomb", "score", "life"]
    def __init__(self, x, y, kind, cfg):
        self.x, self.y, self.kind = x, y, kind
        self.cfg = cfg
        self.t = random.uniform(0, math.tau)
        self.alive = True
    @property
    def rect(self):
        return pygame.Rect(int(self.x - 17), int(self.y - 17), 34, 34)


# ----------------------------------------------------------------------------
# Main game
# ----------------------------------------------------------------------------
class Game:
    S_MENU, S_PLAY, S_CLEAR, S_OVER = range(4)
    DIFFS = ["normal", "hard", "extreme"]

    def __init__(self):
        pygame.mixer.pre_init(SR, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("SPACE INVADERS  ·  procedural edition")
        self.clock = pygame.time.Clock()
        self.world = pygame.Surface((W, H), pygame.SRCALPHA)
        self.flash_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 20)
        self.font_l = pygame.font.Font(None, 34)
        self.font_xl = pygame.font.Font(None, 56)
        self.bank = SoundBank(None)  # replaced after config load
        self.sprites = SpriteBank()
        self.bg = Background()

        self.cfg = load_json("config.json", DEFAULT_CONFIG)
        self.stats = load_json("stats.json", DEFAULT_STATS)
        self.progress = load_json("progress.json", DEFAULT_PROGRESS)
        save_json("config.json", self.cfg)
        save_json("stats.json", self.stats)
        self.bank = SoundBank(self.cfg)

        self.state = self.S_MENU
        self.diff = self.DIFFS[0]
        self.t = 0.0
        self.paused = False
        self.toast_msg, self.toast_t = "", 0.0
        self.menu_blink = 0.0
        self.particles = Particles()
        self.texts = FloatTexts(self.font_l)
        self.flash_a = 0
        self.shake = 0

        self.score = 0
        self.hi = self.progress["high_score"]
        self.new_hi = False
        self.level = 1
        self.lives = 0
        self.combo_n = 0
        self.combo_t = 0.0
        self.best_combo_run = 0
        self.run = None
        self.bullets, self.enemy_bullets = [], []
        self.powerups = []
        self.bunkers = []
        self.ufo = None
        self.ufo_t = random.uniform(12, 20)
        self.diver = None
        self.diver_t = 8.0
        self.effects = {}
        self.respawn_t = 0.0
        self.over_t = 0.0
        self.clear_t = 0.0
        self.clear_bonus = 0
        self.run_stats = {}
        self.player = pygame.Rect(W // 2 - 17, H - 72, 34, 22)
        self.fire_cd = 0.0
        self.running = True

    # ------------------------------------------------------------------ utils
    def diff_mod(self):
        return self.cfg["difficulty"][self.diff]

    def toast(self, msg):
        self.toast_msg, self.toast_t = msg, 1.6

    def add_score(self, pts, x, y, color=(255, 255, 255)):
        mult = 2 if self.effects.get("score", 0) > 0 else 1
        total = pts * mult
        self.score += total
        if self.score > self.hi:
            if not self.new_hi:
                self.new_hi = True
                self.toast("NEW HIGH SCORE!")
            self.hi = self.score
        if pts > 0:
            label = f"+{total}"
            if mult == 2:
                label += " x2"
            self.texts.add(x, y, label, color)
        return total

    def register_kill(self, x, y):
        cfg_c = self.cfg["combo"]
        self.combo_n += 1
        self.combo_t = cfg_c["window"]
        self.best_combo_run = max(self.best_combo_run, self.combo_n)
        mult = min(max(1, self.combo_n // 3), cfg_c["max"])
        if self.combo_n >= 2:
            self.bank.play_combo(self.combo_n)
        return mult

    # ------------------------------------------------------------------ flow
    def start_game(self):
        self.diff_mod_lives = self.diff_mod()["lives"]
        self.lives = self.cfg["player"]["start_lives"] if self.diff == "normal" else self.diff_mod()["lives"]
        self.lives = min(self.lives, self.cfg["player"]["max_lives"])
        self.score = 0
        self.new_hi = False
        self.level = 1
        self.combo_n = self.combo_t = 0
        self.best_combo_run = 0
        self.effects = {}
        self.powerups.clear()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.ufo = self.diver = None
        self.ufo_t = random.uniform(10, 18)
        self.respawn_t = 0
        self.player.center = (W // 2, H - 62)
        self.fire_cd = 0
        self.run_stats = {"shots": 0, "hits": 0, "kills": 0, "pups": 0,
                          "ufo": 0, "bombs": 0, "play_t": 0.0}
        self.setup_wave(self.level)
        self.state = self.S_PLAY
        self.bank.play_music()
        self.toast(f"WAVE 1  ·  {self.diff.upper()}")

    def setup_wave(self, level):
        self.level = level
        self.bunkers = [Bunker(34, 400), Bunker(234, 400), Bunker(434, 400), Bunker(634, 400)]
        self.run = Formation(level, self.cfg, self.bank)
        self.run.xoff = 0.0
        self.run.step_flag = False
        self.run.spawn_t = 1.1
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.powerups.clear()
        self.ufo = None
        self.ufo_t = random.uniform(self.cfg["ufo"]["min_interval"],
                                    self.cfg["ufo"]["max_interval"])
        self.diver = None
        self.diver_t = max(6.0, self.cfg["diver"]["base_interval"] - level)
        self.sprites.recolor_wave(level)
        self.player.center = (W // 2, H - 62)
        self.effects = {}

    def end_game(self):
        rs = self.run_stats
        self.stats["games_played"] += 1
        self.stats["total_score"] += self.score
        self.stats["high_score"] = max(self.stats["high_score"], self.score)
        self.stats["best_wave"] = max(self.stats["best_wave"], self.level)
        self.stats["invaders_killed"] += rs["kills"]
        self.stats["bullets_fired"] += rs["shots"]
        self.stats["invaders_hit"] += rs["hits"]
        self.stats["powerups_collected"] += rs["pups"]
        self.stats["ufo_kills"] += rs["ufo"]
        self.stats["bombs_used"] += rs["bombs"]
        self.stats["best_combo"] = max(self.stats["best_combo"], self.best_combo_run)
        self.stats["total_play_seconds"] = int(self.stats["total_play_seconds"] + rs["play_t"])
        self.progress["high_score"] = max(self.progress["high_score"], self.score)
        self.progress["best_wave"] = max(self.progress["best_wave"], self.level)
        self.progress["last_score"] = self.score
        self.progress["last_wave"] = self.level
        self.progress["last_difficulty"] = self.diff
        self.progress["last_played"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_json("stats.json", self.stats)
        save_json("progress.json", self.progress)
        self.state = self.S_OVER
        self.over_t = 0.0
        self.bank.play("gameover")
        self.bank.stop_music()
        self.bank.ufo.stop()

    def go_menu(self):
        self.state = self.S_MENU
        self.bank.stop_music()
        self.bank.ufo.stop()
        self.particles = Particles()
        self.texts = FloatTexts(self.font_l)
        self.shake = 0

    # ------------------------------------------------------------------ player
    def player_kill(self):
        self.lives -= 1
        self.bank.play("explode")
        self.particles.burst(self.player.centerx, self.player.centery,
                             (120, 200, 255), n=34, speed=280, size=4, life=0.8)
        self.particles.ring(self.player.centerx, self.player.centery, (120, 200, 255), 90)
        self.shake = max(self.shake, 9)
        self.flash_a = 90
        self.respawn_t = 1.3
        self.effects.clear()
        if self.lives <= 0:
            self.over_t = 1.2
        elif self.lives == self.cfg["player"]["max_lives"] - 0 and self.lives == 2 and self.diff == "normal":
            pass

    def use_bomb(self):
        self.bank.play("bomb")
        self.shake = max(self.shake, 12)
        self.flash_a = 160
        self.particles.ring(W // 2, H // 2, (255, 220, 120), 320)
        for b in self.enemy_bullets:
            self.particles.spark(b.x, b.y, (255, 200, 90), 3, 90)
        self.enemy_bullets.clear()
        val = self.cfg["powerups"]["bomb_value"]
        if self.run and self.run.alive_count():
            for inv in self.run.invaders:
                if inv.alive:
                    inv.alive = False
                    self.run_stats["kills"] += 1
                    self.particles.burst(inv.x, inv.y, self.sprites.invader_col[inv.type],
                                         n=10, speed=180, size=3, life=0.5)
            self.add_score(val * 20, W // 2, 240, (255, 220, 120))
            self.check_wave_clear()
        if self.diver and self.diver.alive:
            self.diver.alive = False
            self.add_score(50, self.diver.x, self.diver.y, (255, 150, 50))
        if self.ufo and self.ufo.alive:
            self.ufo.alive = False
            self.bank.ufo.stop()
            self.add_score(self.ufo.value, self.ufo.x, self.ufo.y, (255, 120, 160))
        self.run_stats["bombs"] += 1

    def apply_powerup(self, kind):
        self.run_stats["pups"] += 1
        c = self.cfg["powerups"]
        if kind == "double":
            self.effects["double"] = c["double_time"]
            self.toast("DOUBLE SHOT!")
        elif kind == "rapid":
            self.effects["rapid"] = c["rapid_time"]
            self.toast("RAPID FIRE!")
        elif kind == "shield":
            self.effects["shield"] = c["shield_time"]
            self.toast("SHIELD UP!")
        elif kind == "score":
            self.effects["score"] = c["score_time"]
            self.toast("SCORE x2!")
        elif kind == "bomb":
            self.use_bomb()
        elif kind == "life":
            if self.lives < self.cfg["player"]["max_lives"]:
                self.lives += 1
                self.bank.play("life")
                self.toast("+1 LIFE!")
            else:
                self.add_score(200, self.player.centerx, self.player.top - 20, (255, 130, 200))
                self.toast("FULL LIVES: +200")
        if kind != "bomb":
            self.bank.play("powerup")
        self.particles.burst(self.player.centerx, self.player.centery,
                             (255, 255, 255), n=14, speed=160, size=2, life=0.4)

    def check_wave_clear(self):
        if self.state == self.S_PLAY and self.run and self.run.alive_count() == 0:
            bonus = self.cfg["levels"]["clear_base"] * self.level \
                + self.cfg["levels"]["clear_per_life"] * self.lives
            self.clear_bonus = bonus
            self.score += bonus
            if self.score > self.hi:
                self.new_hi = True
                self.hi = self.score
            self.state = self.S_CLEAR
            self.clear_t = 2.4
            self.bank.play("levelup")
            self.particles.burst(W // 2, H // 2, (120, 255, 190), n=40, speed=260, size=3, life=0.9)

    # ------------------------------------------------------------------ update
    def update(self, dt):
        self.t += dt
        self.menu_blink += dt
        if self.toast_t > 0:
            self.toast_t -= dt
        self.shake = max(0.0, self.shake - 40 * dt)
        self.flash_a = max(0, self.flash_a - 300 * dt)
        self.bg.update(dt)
        self.particles.update(dt)
        self.texts.update(dt)

        if self.state == self.S_MENU:
            return
        if self.state == self.S_CLEAR:
            self.clear_t -= dt
            if self.clear_t <= 0:
                self.setup_wave(self.level + 1)
                self.state = self.S_PLAY
                self.toast(f"WAVE {self.level + 1}")
            return
        if self.state == self.S_OVER:
            self.over_t += dt
            return
        if self.paused:
            return

        # ---------------- playing ----------------
        rs = self.run_stats
        rs["play_t"] += dt
        d = self.diff_mod()

        # combo timer
        if self.combo_t > 0:
            self.combo_t -= dt
            if self.combo_t <= 0:
                self.combo_n = 0

        # effect timers
        for k in list(self.effects):
            self.effects[k] -= dt
            if self.effects[k] <= 0:
                del self.effects[k]

        # --- player movement / firing ---
        if self.respawn_t > 0:
            self.respawn_t -= dt
            if self.respawn_t <= 0:
                self.player.center = (W // 2, H - 62)
        else:
            spd = self.cfg["player"]["speed"]
            mv = 0
            if pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]:
                mv -= 1
            if pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]:
                mv += 1
            self.player.x = max(14, min(W - 14 - self.player.w, self.player.x + mv * spd * dt))
            self.fire_cd -= dt
            want = pygame.key.get_pressed()[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
            if want and self.fire_cd <= 0:
                cd = self.cfg["player"]["fire_cooldown"]
                if "rapid" in self.effects:
                    cd *= 0.42
                self.fire_cd = cd
                bspd = self.cfg["player"]["bullet_speed"]
                top = self.player.top
                if "double" in self.effects:
                    for off in (-6, 6):
                        self.bullets.append(Bullet(self.player.centerx + off, top, 0, -bsp, "player"))
                    rs["shots"] += 2
                else:
                    self.bullets.append(Bullet(self.player.centerx, top, 0, -bsp, "player"))
                    rs["shots"] += 1
                self.bank.play("shoot")
                self.particles.spark(self.player.centerx, top - 6, (180, 240, 255), 3, 70)

        # --- formation ---
        self.run.update(dt, self)
        if self.run.spawn_t <= 0:
            # invaders erode bunkers they touch
            for inv in self.run.invaders:
                if inv.alive:
                    r = self.run.rect_of(inv)
                    for b in self.bunkers:
                        if b.rect.colliderect(r):
                            b.destroy_rect(r)
            # invaders reaching the player line
            for inv in self.run.invaders:
                if inv.alive and inv.y > H - 100:
                    self.end_game()
                    return
            # enemy fire
            self.run.fire_t -= dt
            if self.run.fire_t <= 0:
                iv = self.cfg["invaders"]
                rate = iv["fire_rate"] * d["fire"] * (1 + 0.18 * (self.level - 1))
                self.run.fire_t = random.uniform(0.6, 1.4) / min(rate, 4.0)
                if len(self.enemy_bullets) < iv["max_bullets"] + self.level:
                    col = random.randrange(self.run.cols)
                    shooter = self.run.lowest_in_column(col)
                    if shooter:
                        r = self.run.rect_of(shooter)
                        self.enemy_bullets.append(
                            Bullet(r.centerx, r.bottom, 0,
                                   iv["bullet_speed"] + 12 * self.level, "enemy"))
                        self.run_stats and None  # (no sound - keeps it classic & calm)

        # --- UFO ---
        if self.ufo is None:
            self.ufo_t -= dt
            if self.ufo_t <= 0 and self.run.spawn_t <= 0:
                self.ufo = UFO(self.level, self.cfg)
                self.bank.ufo.play()
        else:
            u = self.ufo
            u.x += u.vx * dt
            if u.x < -70 or u.x > W + 70:
                self.ufo = None
                self.bank.ufo.stop()
                self.ufo_t = random.uniform(self.cfg["ufo"]["min_interval"],
                                            self.cfg["ufo"]["max_interval"])

        # --- diver ---
        if self.level >= self.cfg["diver"]["first_wave"]:
            if self.diver is None:
                self.diver_t -= dt
                if self.diver_t <= 0 and self.run.spawn_t <= 0:
                    self.diver = Diver(self.level, self.cfg)
            else:
                dv = self.diver
                dv.t += dt
                dv.y += dv.speed * dt
                dv.x = dv.base_x + math.sin(dv.t * dv.freq) * dv.ampl
                if not dv.shot and dv.y > 140:
                    dv.shot = True
                    self.enemy_bullets.append(Bullet(dv.x, dv.y + 12, 0, 260, "enemy"))
                if dv.y > H + 30:
                    self.diver = None
                    self.diver_t = max(5.0, self.cfg["diver"]["base_interval"] - self.level)

        # --- bullets ---
        for b in self.bullets:
            b.y += b.vy * dt
            if b.y < -20:
                b.alive = False
                continue
            r = b.rect
            # vs UFO
            if self.ufo and self.ufo.alive and r.colliderect(self.ufo.rect):
                b.alive = False
                self.ufo.alive = False
                self.bank.ufo.stop()
                self.bank.play("ufo_kill")
                rs["ufo"] += 1
                self.particles.burst(self.ufo.x, self.ufo.y, (255, 120, 170), n=30,
                                     speed=260, size=3, life=0.7)
                self.particles.ring(self.ufo.x, self.ufo.y, (255, 120, 170), 110)
                self.add_score(self.ufo.value, self.ufo.x, self.ufo.y - 14, (255, 120, 170))
                self.shake = max(self.shake, 5)
                self.ufo = None
                self.ufo_t = random.uniform(self.cfg["ufo"]["min_interval"],
                                            self.cfg["ufo"]["max_interval"])
                continue
            # vs diver
            if self.diver and self.diver.alive and r.colliderect(self.diver.rect):
                b.alive = False
                self.diver.alive = False
                rs["kills"] += 1
                rs["hits"] += 1
                mult = self.register_kill(self.diver.x, self.diver.y)
                self.add_score(self.cfg["points"]["diver"] * mult,
                               self.diver.x, self.diver.y - 12, (255, 150, 50))
                self.particles.burst(self.diver.x, self.diver.y, (255, 150, 50), n=18,
                                     speed=200, size=3, life=0.5)
                self.diver = None
                self.diver_t = max(5.0, self.cfg["diver"]["base_interval"] - self.level)
                continue
            # vs formation
            if self.run.spawn_t <= 0:
                inv = self.run.invader_at_rect(r)
                if inv:
                    b.alive = False
                    inv.alive = False
                    rs["kills"] += 1
                    rs["hits"] += 1
                    col = self.sprites.invader_col[inv.type]
                    self.particles.burst(inv.x, inv.y, col, n=16, speed=190, size=3, life=0.5)
                    self.bank.play("inv_die")
                    base = self.cfg["points"][{"A": "squid", "B": "crab", "C": "octopus"}[inv.type]]
                    mult = self.register_kill(inv.x, inv.y)
                    self.add_score(base * mult, inv.x, inv.y - 12, col)
                    if random.random() < self.cfg["powerups"]["chance"] * (
                            0.4 + 0.6 * (inv.type == "C")):
                        life_p = self.cfg["powerups"]["life_chance"]
                        kind = "life" if random.random() < life_p else random.choice(
                            ["double", "rapid", "shield", "bomb", "score", "score",
                             "double", "rapid"])
                        self.powerups.append(PowerUp(inv.x, inv.y, kind, self.cfg))
                    self.check_wave_clear()
                    continue
            # vs bunkers
            for bk in self.bunkers:
                if r.colliderect(bk.rect) and bk.hit_tiles(r.left, r.top, r.right, r.bottom):
                    b.alive = False
                    bk.erode(b.x, b.y, 1.7)
                    self.particles.spark(b.x, b.y, (120, 255, 180), 5, 90)
                    break
        self.bullets = [b for b in self.bullets if b.alive]

        for b in self.enemy_bullets:
            b.y += b.vy * dt
            if b.y > H - 24:
                b.alive = False
                continue
            r = b.rect
            # vs shield
            if "shield" in self.effects and self.respawn_t <= 0:
                sr_ = pygame.Rect(self.player.centerx - 26, self.player.top - 16, 52, 52)
                if r.colliderect(sr_):
                    b.alive = False
                    self.bank.play("shield")
                    self.particles.spark(b.x, b.y, (120, 255, 170), 6, 110)
                    continue
            # vs player
            if self.respawn_t <= 0 and r.colliderect(self.player):
                b.alive = False
                self.player_kill()
                continue
            # vs bunkers
            for bk in self.bunkers:
                if r.colliderect(bk.rect) and bk.hit_tiles(r.left, r.top, r.right, r.bottom):
                    b.alive = False
                    bk.erode(b.x, b.y, 1.5)
                    self.particles.spark(b.x, b.y, (120, 255, 180), 4, 80)
                    break
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        # --- invader vs player body collision ---
        if self.respawn_t <= 0:
            for inv in self.run.invaders:
                if inv.alive and self.run.rect_of(inv).colliderect(self.player):
                    inv.alive = False
                    rs["kills"] += 1
                    self.player_kill()
                    break

        # --- power-ups falling ---
        for p in self.powerups:
            p.t += dt * 3
            p.y += self.cfg["powerups"]["drop_speed"] * dt
            p.x += math.sin(p.t) * 20 * dt
            if p.y > H + 20:
                p.alive = False
                continue
            if self.respawn_t <= 0 and p.rect.colliderect(self.player):
                p.alive = False
                self.apply_powerup(p.kind)
        self.powerups = [p for p in self.powerups if p.alive]

        # --- death / respawn ---
        if self.respawn_t > 0 and self.lives > 0 and self.respawn_t < 1.3:
            pass
        if self.over_t > 0:
            self.over_t -= dt
            if self.over_t <= 0:
                self.end_game()

    # ------------------------------------------------------------------ draw
    def draw(self):
        self.screen.fill((5, 7, 18))
        self.bg.draw(self.screen, self.t)
        w = self.world
        w.fill((0, 0, 0, 0))

        if self.state == self.S_MENU:
            self._draw_menu(w)
        else:
            self._draw_play_world(w)

        ox = random.uniform(-1, 1) * self.shake if self.shake > 0 else 0
        oy = random.uniform(-1, 1) * self.shake if self.shake > 0 else 0
        self.screen.blit(w, (int(ox), int(oy)))
        self.particles.draw(w)
        self.texts.draw(w)
        self.screen.blit(w, (int(ox), int(oy)))  # particles & texts with shake too

        if self.flash_a > 0:
            self.flash_surf.fill((255, 255, 255, int(self.flash_a)))
            self.screen.blit(self.flash_surf, (0, 0))

        if self.state != self.S_MENU:
            self._draw_hud()
        if self.state == self.S_CLEAR:
            self._draw_clear_banner()
        if self.state == self.S_OVER:
            self._draw_game_over()
        if self.paused and self.state == self.S_PLAY:
            self._draw_pause()
        if self.toast_t > 0:
            img = shadow_text(self.toast_msg, self.font_l, (255, 240, 170)).copy()
            img.set_alpha(int(255 * min(1.0, self.toast_t)))
            self.screen.blit(img, img.get_rect(midtop=(W // 2, 46)))

        pygame.display.flip()

    def _draw_play_world(self, w):
        # ground line
        pygame.draw.line(w, (0, 190, 220), (0, H - 24), (W, H - 24), 2)
        for bk in self.bunkers:
            bk.draw(w)
        # player
        if self.respawn_t <= 0 or int(self.t * 14) % 2 == 0:
            if self.respawn_t <= 0:
                img = self.sprites.player_img
                w.blit(img, img.get_rect(center=(self.player.centerx, self.player.centery)))
                # thruster flame
                fl = 6 + 5 * abs(math.sin(self.t * 30))
                pygame.draw.polygon(w, (255, 170, 60),
                                    ((self.player.centerx - 5, self.player.bottom - 2),
                                     (self.player.centerx + 5, self.player.bottom - 2),
                                     (self.player.centerx, self.player.bottom + fl)))
                if "shield" in self.effects:
                    a = int(70 + 40 * math.sin(self.t * 6))
                    pygame.draw.circle(w, (110, 240, 160, a),
                                       (self.player.centerx, self.player.centery), 28, 2)
        # bullets
        for b in self.bullets:
            w.blit(self.sprites.player_bullet,
                   (int(b.x - 3), int(b.y - 8)))
        frame = int(self.t * 14) % 2
        for b in self.enemy_bullets:
            w.blit(self.sprites.enemy_bullets[frame], (int(b.x - 8), int(b.y - 12)))
        # formation
        if self.run:
            f = int(self.run.anim_t * 3) % 2
            alpha_scale = max(0.0, min(1.0, self.run.spawn_t / 0.5)) if self.run.spawn_t > 0 else 1.0
            for inv in self.run.invaders:
                if inv.alive:
                    img = self.sprites.invader_imgs[inv.type][f]
                    if alpha_scale < 1.0:
                        img = img.copy()
                        img.set_alpha(int(255 * (1 - alpha_scale)))
                    w.blit(img, img.get_rect(center=(int(inv.x), int(inv.y))))
        # diver
        if self.diver and self.diver.alive:
            img = self.sprites.diver_img
            w.blit(img, img.get_rect(center=(int(self.diver.x), int(self.diver.y))))
        # ufo
        if self.ufo and self.ufo.alive:
            img = self.sprites.saucer_on if int(self.t * 8) % 2 == 0 else self.sprites.saucer_off
            w.blit(img, img.get_rect(center=(int(self.ufo.x), int(self.ufo.y))))
        # powerups
        for p in self.powerups:
            img = self.sprites.power_icons[p.kind]
            yy = int(p.y + math.sin(p.t * 2) * 3)
            w.blit(img, img.get_rect(center=(int(p.x), yy)))

    def _draw_hud(self):
        s = self.screen
        pygame.draw.line(s, (30, 60, 90), (0, 40), (W, 40), 1)
        s.blit(shadow_text(f"SCORE {self.score:06d}", self.font_l, (235, 240, 255)), (12, 6))
        s.blit(shadow_text(f"WAVE {self.level:02d}", self.font_l, (120, 235, 170)),
               (W // 2 - 40, 8))
        s.blit(shadow_text(f"HI {self.hi:06d}", self.font, (255, 220, 120)),
               (W - 118, 12))
        # lives
        for i in range(self.lives):
            s.blit(self.sprites.player_life, (14 + i * 22, H - 20))
        # active effects
        i = 0
        for key, left in sorted(self.effects.items()):
            total = {"double": 10, "rapid": 8, "shield": 8, "score": 12}[key]
            x = W - 44 - i * 40
            icon = self.sprites.power_icons[key]
            small = pygame.transform.scale(icon, (24, 24))
            s.blit(small, (x, 8))
            frac = max(0.0, min(1.0, left / total))
            pygame.draw.rect(s, (60, 70, 90), (x, 34, 24, 4), border_radius=2)
            pygame.draw.rect(s, (255, 230, 120), (x, 34, int(24 * frac), 4), border_radius=2)
            i += 1
        # combo
        if self.combo_n >= 2 and self.combo_t > 0:
            pulse = 1 + 0.08 * math.sin(self.t * 12)
            f = pygame.font.Font(None, int(24 * pulse))
            s.blit(shadow_text(f"CHAIN x{self.combo_n}", f, (255, 210, 90)), (14, 48))

    def _draw_clear_banner(self):
        s = self.screen
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 120))
        s.blit(dim, (0, 0))
        c = self.screen.get_rect().center
        s.blit(shadow_text(f"WAVE {self.level} CLEARED", self.font_xl, (140, 255, 190)),
               s.get_rect().copy().move(0, -40).union((0, 0, 0, 1)).topleft)
        s.blit(shadow_text(f"WAVE {self.level} CLEARED", self.font_xl, (140, 255, 190)),
               (W // 2 - 240, H // 2 - 90))
        s.blit(shadow_text(f"BONUS  +{self.clear_bonus}", self.font_l, (255, 225, 130)),
               (W // 2 - 110, H // 2 - 20))
        s.blit(shadow_text("GET READY ...", self.font, (180, 200, 240)),
               (W // 2 - 60, H // 2 + 40))

    def _draw_game_over(self):
        s = self.screen
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((5, 0, 15, 170))
        s.blit(dim, (0, 0))
        rs = self.run_stats
        acc = (rs["hits"] / rs["shots"] * 100) if rs["shots"] else 0.0
        mins, secs = divmod(int(rs["play_t"]), 60)
        panel = [
            ("GAME OVER", self.font_xl, (255, 110, 110)),
            (f"FINAL SCORE   {self.score:06d}", self.font_l, (240, 240, 255)),
        ]
        if self.new_hi:
            blink = int(self.over_t * 2) % 2 == 0
            if blink:
                panel.append(("★ NEW HIGH SCORE ★", self.font_l, (255, 220, 90)))
        panel += [
            (f"WAVE REACHED   {self.level}      DIFFICULTY   {self.diff.upper()}",
             self.font, (150, 220, 180)),
            (f"KILLS {rs['kills']}    ACCURACY {acc:3.0f}%    CHAIN {self.best_combo_run}    UFO {rs['ufo']}    TIME {mins}:{secs:02d}",
             self.font, (190, 200, 235)),
            (f"LIFETIME:  {self.stats['games_played']} GAMES   {self.stats['invaders_killed']} KILLS   HI {self.stats['high_score']}",
             self.font, (140, 150, 190)),
        ]
        y = H // 2 - 130
        for txt, fnt, col in panel:
            img = shadow_text(txt, fnt, col)
            s.blit(img, img.get_rect(center=(W // 2, y)))
            y += 46 if fnt is self.font_xl else 34
        if self.over_t > 1.0:
            hint = shadow_text("ENTER  MENU        R  RETRY", self.font_l, (230, 230, 255))
            hint.set_alpha(int(160 + 95 * math.sin(self.over_t * 4)))
            s.blit(hint, hint.get_rect(center=(W // 2, H // 2 + 130)))

    def _draw_pause(self):
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 10, 160))
        self.screen.blit(dim, (0, 0))
        t = shadow_text("PAUSED", self.font_xl, (240, 240, 255))
        self.screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 20)))
        h = shadow_text("P RESUME      ESC MENU", self.font, (180, 200, 240))
        self.screen.blit(h, h.get_rect(center=(W // 2, H // 2 + 30)))

    def _draw_menu(self, w):
        s = self.screen
        # animated legend
        f = int(self.t * 2) % 2
        rows = [("A", "10 PTS", (255, 300)), ("B", "20 PTS", (255, 336)),
                ("C", "30 PTS", (255, 372))]
        for t, label, (x, y) in rows:
            img = self.sprites.invader_imgs[t][f]
            bob = math.sin(self.t * 2 + x * 0.02) * 4
            w.blit(img, img.get_rect(center=(x, int(y + bob))))
            s.blit(shadow_text(label, self.font, (220, 225, 250)), (x + 26, y - 10 + int(bob)))
        ufo_img = self.sprites.saucer_on if int(self.t * 6) % 2 == 0 else self.sprites.saucer_off
        w.blit(ufo_img, ufo_img.get_rect(center=(255, 412)))
        s.blit(shadow_text("??? BONUS !!!", self.font, (255, 150, 190)), (285, 404))
        # title
        fnt = pygame.font.Font(None, 72)
        title = fnt.render("SPACE INVADERS", True, (235, 245, 255))
        title = pygame.transform.scale(title, (title.get_width() * 2, title.get_height() * 2))
        sh = fnt.render("SPACE INVADERS", True, (20, 40, 90))
        sh = pygame.transform.scale(sh, (sh.get_width() * 2, sh.get_height() * 2))
        full = sh.copy()
        full.blit(title, (6, 6))
        s.blit(full, full.get_rect(midtop=(W // 2, 60)))
        sub = shadow_text("ALL ART & SOUND GENERATED IN PYTHON  ·  NO ASSETS",
                          self.font, (140, 220, 200))
        s.blit(sub, sub.get_rect(midtop=(W // 2, 205)))
        # difficulty
        label = shadow_text("DIFFICULTY", self.font, (170, 180, 220))
        s.blit(label, label.get_rect(midtop=(W // 2, 250)))
        names = {"normal": "NORMAL", "hard": "HARD", "extreme": "EXTREME"}
        cols = {"normal": (120, 235, 160), "hard": (255, 190, 90), "extreme": (255, 110, 110)}
        x0 = W // 2 - 170
        for i, dname in enumerate(self.DIFFS):
            col = cols[dname]
            sel = dname == self.diff
            txt = shadow_text(("▸ " if sel else "") + names[dname],
                              self.font_l if sel else self.font,
                              col if sel else (150, 155, 185))
            s.blit(txt, txt.get_rect(center=(x0 + i * 120, 292)))
            if sel:
                pygame.draw.rect(s, col, (x0 + i * 120 - 44, 310, 88, 3), border_radius=2)
        # start prompt
        if int(self.menu_blink * 2) % 2 == 0:
            p = shadow_text("PRESS  ENTER  TO  START", self.font_l, (255, 240, 170))
            s.blit(p, p.get_rect(center=(W // 2, 350)))
        hi = self.progress["high_score"]
        st = self.stats
        line = (f"HI {hi:06d}    WAVE {st['best_wave']:02d}    "
                f"KILLS {st['invaders_killed']}    GAMES {st['games_played']}")
        s.blit(shadow_text(line, self.font, (150, 210, 235)),
               (W // 2 - 260, H - 120))
        ctrl = shadow_text("←/→ MOVE    SPACE FIRE    P PAUSE    M MUTE    "
                           f"{'MUTED' if self.bank.muted else 'SOUND ON'}",
                           self.font, (130, 140, 180))
        s.blit(ctrl, ctrl.get_rect(center=(W // 2, H - 60)))
        # power-up legend
        s.blit(shadow_text("POWER-UPS", self.font, (150, 160, 200)), (W // 2 - 130, H - 100))
        px = W // 2 - 90
        for key in ["double", "rapid", "shield", "bomb", "score", "life"]:
            icon = pygame.transform.scale(self.sprites.power_icons[key], (18, 18))
            s.blit(icon, (px, H - 96))
            px += 26

    # ------------------------------------------------------------------ input
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    self.toast("MUTED" if self.bank.toggle_mute() else "SOUND ON")
                if self.state == self.S_MENU:
                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        self.bank.play("select")
                        self.start_game()
                    elif e.key in (pygame.K_LEFT, pygame.K_a):
                        self.bank.play("select")
                        i = (self.DIFFS.index(self.diff) - 1) % 3
                        self.diff = self.DIFFS[i]
                    elif e.key in (pygame.K_RIGHT, pygame.K_d):
                        self.bank.play("select")
                        i = (self.DIFFS.index(self.diff) + 1) % 3
                        self.diff = self.DIFFS[i]
                    elif e.key == pygame.K_ESCAPE:
                        self.running = False
                elif self.state == self.S_PLAY:
                    if e.key == pygame.K_p:
                        self.paused = not self.paused
                    elif e.key == pygame.K_ESCAPE:
                        self.go_menu()
                    elif e.key == pygame.K_SPACE:
                        pass  # held-shoot handled in update
                elif self.state == self.S_OVER:
                    if self.over_t > 1.0:
                        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                            self.go_menu()
                        elif e.key == pygame.K_r:
                            self.bank.play("select")
                            self.start_game()
                elif self.state == self.S_CLEAR:
                    if e.key == pygame.K_ESCAPE:
                        self.go_menu()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if self.state == self.S_MENU:
                    self.start_game()

    # ------------------------------------------------------------------ loop
    def run_loop(self):
        while self.running:
            dt = min(1 / 30, self.clock.tick(FPS) / 1000.0)
            self.handle_events()
            self.update(dt)
            self.draw()
        save_json("stats.json", self.stats)
        save_json("progress.json", self.progress)
        pygame.quit()
        sys.exit(0)


def main():
    try:
        Game().run_loop()
    except pygame.error as ex:
        print("pygame error:", ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
