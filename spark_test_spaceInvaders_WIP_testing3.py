# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --temp 1.0 --top_p 0.95 --top_k 20 --min_p 0.0 --repeat-penalty 1.0 --presence-penalty 0.0  --spec-type draft-mtp --spec-draft-n-max 7 --chat-template-kwargs '{"reasoning_effort": "xhigh"}' --image-min-tokens 1024 --reasoning-preserve --parallel 1  --model /AI/models/Huihui-Qwen3.8-27B-abliterated-Q6_K_L.gguf  --mmproj /AI/models/mmproj-Qwen3.8-27B-BF16.gguf


import pygame
import math
import random
import json
import os
from array import array

WIDTH, HEIGHT = 800, 600
FPS = 60

POWERUP_COLORS = {
    '2X': (255, 210, 0),
    'RAPID': (0, 200, 255),
    'DOUBLE': (0, 255, 120),
    'SHIELD': (120, 255, 120),
    '1UP': (255, 120, 220),
}

POWERUP_LABELS = {
    '2X': '2X',
    'RAPID': 'SPD',
    'DOUBLE': 'DUAL',
    'SHIELD': 'WALL',
    '1UP': '1UP',
}


def get_stats_file():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, 'space_invaders_stats.json')
        if os.access(script_dir, os.W_OK):
            return path
    except Exception:
        pass
    return os.path.join(os.path.expanduser('~'), 'space_invaders_stats.json')


STATS_FILE = get_stats_file()


def load_stats():
    stats = {
        'best_score': 0,
        'games_played': 0,
        'max_level': 0,
        'total_kills': 0,
        'total_bonuses': 0,
        'total_powerups': 0,
        'total_time': 0
    }

    try:
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k in stats:
                stats[k] = data.get(k, stats[k])
    except Exception:
        pass

    return stats


def save_stats(stats):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

class SFX:
    def __init__(self):
        self.enabled = False
        self.sounds = {}

        try:
            # If the mixer was not initialized by main(), try to initialize it now.
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(44100, -16, 2, 512)

            init = pygame.mixer.get_init()
            if not init:
                print("[SFX] mixer is not initialized")
                return

            self.freq, self.format, self.channels = init
            self.sr = int(self.freq)

            try:
                pygame.mixer.set_num_channels(16)
            except Exception:
                pass

            print(
                f"[SFX] mixer ok: "
                f"{self.freq} Hz, "
                f"format={self.format}, "
                f"channels={self.channels}"
            )

            self._build()
            self.enabled = any(s is not None for s in self.sounds.values())

            # Short test beep so you know sound initialization worked.
            if self.enabled:
                self.play("select", 0.5)

        except Exception as e:
            print(f"[SFX] init failed: {e}")
            self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def play(self, name, volume=0.6):
        if not self.enabled:
            return

        snd = self.sounds.get(name)
        if snd is None:
            return

        try:
            snd.set_volume(max(0.0, min(1.0, volume)))
            snd.play()
        except Exception:
            pass

    def _build(self):
        def mono_to_pcm(samples):
            """
            Convert generated 16-bit mono samples into the exact PCM format
            currently used by pygame.mixer.
            """
            fmt = self.format

            if fmt == -16:
                converted = array("h", samples)
            elif fmt == -32:
                converted = array("i", (int(s) * 32768 for s in samples))
            elif fmt == 16:
                converted = array("H", (int(s) + 32768 for s in samples))
            elif fmt == 8:
                converted = array(
                    "B",
                    (max(0, min(255, (int(s) + 32768) // 257)) for s in samples)
                )
            else:
                converted = array("h", samples)

            if self.channels == 2:
                stereo = array(converted.typecode)
                for s in converted:
                    stereo.append(s)
                    stereo.append(s)
                converted = stereo

            return converted

        def finish(samples):
            try:
                pcm = mono_to_pcm(samples)

                # Try several buffer styles because pygame versions/builds
                # can be picky here.
                for buf in (bytearray(pcm), pcm.tobytes(), pcm):
                    try:
                        snd = pygame.mixer.Sound(buffer=buf)
                        if snd.get_length() > 0:
                            snd.set_volume(1.0)
                            return snd
                    except Exception:
                        continue
            except Exception:
                pass

            return None

        def tone(freq, duration, volume=0.4, shape="sine", slide_to=None, decay=0.0):
            n = max(1, int(self.sr * duration))
            a = array("h", [0]) * n

            for i in range(n):
                t = i / self.sr
                frac = i / n

                if slide_to is not None:
                    f = freq + (slide_to - freq) * frac
                else:
                    f = freq

                if shape == "sine":
                    v = math.sin(2.0 * math.pi * f * t)
                elif shape == "square":
                    v = 1.0 if math.sin(2.0 * math.pi * f * t) >= 0.0 else -1.0
                else:
                    v = 0.0

                fade_in = min(1.0, i / (0.005 * self.sr) + 1e-6)
                fade_out = min(1.0, (n - i) / (0.05 * self.sr) + 1e-6)
                env = min(fade_in, fade_out)

                if decay > 0:
                    env *= max(0.0, (1.0 - frac) ** decay)

                sample = int(v * volume * env * 32767)
                a[i] = max(-32768, min(32767, sample))

            return a

        def noise(duration, volume=0.4, lowpass=0.2):
            n = max(1, int(self.sr * duration))
            a = array("h", [0]) * n
            last = 0.0

            for i in range(n):
                white = random.uniform(-1.0, 1.0)
                last += lowpass * (white - last)

                env = min(1.0, (n - i) / (0.05 * self.sr) + 1e-6)
                env *= max(0.0, (1.0 - i / n) ** 1.2)

                sample = int(last * volume * env * 32767)
                a[i] = max(-32768, min(32767, sample))

            return a

        def mix(*parts):
            if not parts:
                return array("h", [0])

            max_len = max(len(p) for p in parts)
            out = array("h", [0]) * max_len

            for p in parts:
                for i in range(len(p)):
                    v = out[i] + p[i]
                    if v > 32767:
                        v = 32767
                    elif v < -32768:
                        v = -32768
                    out[i] = v

            return out

        def seq(*parts):
            out = array("h")
            for p in parts:
                out.extend(p)
            return out

        self.sounds["shoot"] = finish(
            tone(900, 0.08, 0.35, "square", 220, 1.2)
        )

        self.sounds["step1"] = finish(
            tone(130, 0.06, 0.55, "square", 85, 1.5)
        )

        self.sounds["step2"] = finish(
            tone(100, 0.06, 0.55, "square", 60, 1.5)
        )

        self.sounds["hit"] = finish(
            mix(
                tone(500, 0.12, 0.45, "square", 130, 2.0),
                noise(0.12, 0.35, 0.4)
            )
        )

        self.sounds["player"] = finish(
            mix(
                noise(0.6, 0.8, 0.2),
                tone(180, 0.55, 0.6, "sine", 40, 1.5)
            )
        )

        self.sounds["shield"] = finish(
            tone(1600, 0.05, 0.3, "square", 700, 2.0)
        )

        self.sounds["bonus"] = finish(
            seq(
                tone(660, 0.08, 0.4, "square"),
                tone(880, 0.08, 0.4, "square"),
                tone(1320, 0.12, 0.45, "square")
            )
        )

        self.sounds["level"] = finish(
            seq(
                tone(523, 0.08, 0.35, "square"),
                tone(659, 0.08, 0.35, "square"),
                tone(784, 0.08, 0.35, "square"),
                tone(1046, 0.15, 0.4, "square")
            )
        )

        self.sounds["gameover"] = finish(
            seq(
                tone(392, 0.15, 0.4, "sine"),
                tone(330, 0.15, 0.4, "sine"),
                tone(262, 0.15, 0.4, "sine"),
                tone(196, 0.3, 0.45, "sine")
            )
        )

        self.sounds["select"] = finish(
            tone(1200, 0.06, 0.3, "square", 700, 2.0)
        )

        self.sounds["ufo"] = finish(
            tone(600, 0.15, 0.3, "sine", 900, 0.5)
        )


def make_font(size, bold=True):
    try:
        return pygame.font.SysFont('arial', size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def make_background():
    bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    top = (8, 10, 32)
    bottom = (28, 8, 50)

    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(bg, (r, g, b), (0, y), (WIDTH, y))

    for _ in range(8):
        radius = random.randint(80, 180)
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        col = random.choice([
            (40, 20, 70),
            (20, 40, 80),
            (70, 20, 60)
        ])

        neb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        for i in range(radius, 0, -1):
            alpha = int(18 * (i / radius))
            pygame.draw.circle(
                neb,
                (col[0], col[1], col[2], alpha),
                (radius, radius),
                i
            )

        bg.blit(neb, (x - radius, y - radius))

    return bg


def make_player_sprite():
    s = pygame.Surface((40, 26), pygame.SRCALPHA)

    pygame.draw.ellipse(s, (0, 150, 255, 45), (-2, -2, 44, 30))
    pygame.draw.polygon(s, (10, 220, 255), [
        (20, 2),
        (34, 24),
        (26, 24),
        (22, 12),
        (18, 12),
        (14, 24),
        (6, 24)
    ])
    pygame.draw.polygon(s, (0, 110, 200), [
        (20, 6),
        (30, 22),
        (25, 22),
        (22, 13),
        (18, 13),
        (15, 22),
        (10, 22)
    ])
    pygame.draw.rect(s, (220, 255, 255), (18, 8, 4, 8))
    pygame.draw.rect(s, (255, 80, 120), (8, 18, 4, 4))
    pygame.draw.rect(s, (255, 80, 120), (28, 18, 4, 4))

    return s


def make_invader_sprite(kind, frame, color):
    s = pygame.Surface((32, 24), pygame.SRCALPHA)

    dark = tuple(max(0, c - 80) for c in color)
    light = tuple(min(255, c + 60) for c in color)

    pygame.draw.ellipse(s, (*color, 35), (0, 0, 32, 24))

    if kind == 0:
        pygame.draw.polygon(s, color, [
            (16, 3),
            (28, 11),
            (26, 19),
            (6, 19),
            (4, 11)
        ])
        pygame.draw.polygon(s, dark, [
            (16, 6),
            (24, 11),
            (22, 17),
            (10, 17),
            (8, 11)
        ])

        pygame.draw.circle(s, (255, 255, 255), (11, 12), 3)
        pygame.draw.circle(s, dark, (11, 12), 1)
        pygame.draw.circle(s, (255, 255, 255), (21, 12), 3)
        pygame.draw.circle(s, dark, (21, 12), 1)

        if frame == 0:
            legs = [(7, 19), (13, 19), (19, 19), (25, 19)]
        else:
            legs = [(9, 19), (15, 19), (21, 19), (27, 19)]

        for x, y in legs:
            pygame.draw.line(s, light, (x, y), (x, y + 4), 2)

    elif kind == 1:
        pygame.draw.ellipse(s, color, (4, 5, 24, 14))
        pygame.draw.ellipse(s, dark, (8, 8, 16, 8))

        pygame.draw.circle(s, (255, 255, 255), (11, 11), 3)
        pygame.draw.circle(s, dark, (11, 11), 1)
        pygame.draw.circle(s, (255, 255, 255), (21, 11), 3)
        pygame.draw.circle(s, dark, (21, 11), 1)

        if frame == 0:
            pygame.draw.line(s, light, (10, 5), (8, 0), 2)
            pygame.draw.line(s, light, (22, 5), (24, 0), 2)
        else:
            pygame.draw.line(s, light, (10, 5), (12, 0), 2)
            pygame.draw.line(s, light, (22, 5), (20, 0), 2)

        if frame == 0:
            legs = [(8, 19), (14, 19), (18, 19), (24, 19)]
        else:
            legs = [(10, 19), (16, 19), (20, 19), (26, 19)]

        for x, y in legs:
            pygame.draw.line(s, light, (x, y), (x, y + 4), 2)

    else:
        pygame.draw.rect(s, color, (5, 6, 22, 14), border_radius=3)
        pygame.draw.rect(s, dark, (8, 9, 16, 8), border_radius=2)

        pygame.draw.circle(s, (255, 255, 255), (11, 12), 3)
        pygame.draw.circle(s, dark, (11, 12), 1)
        pygame.draw.circle(s, (255, 255, 255), (21, 12), 3)
        pygame.draw.circle(s, dark, (21, 12), 1)

        if frame == 0:
            legs = [(8, 20), (14, 20), (18, 20), (24, 20)]
        else:
            legs = [(10, 20), (16, 20), (20, 20), (26, 20)]

        for x, y in legs:
            pygame.draw.line(s, light, (x, y), (x, y + 3), 2)

    return s


def make_bullet_sprite(color):
    s = pygame.Surface((8, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*color, 80), (0, 0, 8, 18))
    pygame.draw.rect(s, color, (3, 2, 2, 14), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (3, 4, 2, 8))
    return s


def make_bomb_sprite(color):
    s = pygame.Surface((10, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*color, 80), (0, 0, 10, 20))

    for y in range(2, 18, 4):
        pygame.draw.rect(s, color, (4, y, 2, 4))

    pygame.draw.rect(s, (255, 255, 255), (4, 4, 2, 3))
    return s


def make_ufo_sprite():
    s = pygame.Surface((52, 24), pygame.SRCALPHA)

    pygame.draw.ellipse(s, (255, 100, 100, 50), (0, 0, 52, 24))
    pygame.draw.ellipse(s, (255, 120, 120), (4, 8, 44, 14))
    pygame.draw.ellipse(s, (255, 180, 180), (12, 4, 28, 10))

    for x in [10, 18, 26, 34, 42]:
        pygame.draw.circle(s, (255, 255, 255), (x, 16), 2)

    return s


def make_powerup_sprite(kind):
    s = pygame.Surface((34, 26), pygame.SRCALPHA)
    rect = s.get_rect()
    color = POWERUP_COLORS[kind]
    label = POWERUP_LABELS[kind]

    pygame.draw.rect(s, (*color, 220), rect, border_radius=7)
    pygame.draw.rect(s, (255, 255, 255, 120), rect, 2, border_radius=7)

    font = make_font(13, True)
    text = font.render(label, True, (255, 255, 255))
    shadow = font.render(label, True, (0, 0, 0))

    pos = text.get_rect(center=s.get_rect().center)
    s.blit(shadow, pos.move(1, 1))
    s.blit(text, pos)

    return s


class Shield:
    def __init__(self, x, y):
        self.w = 72
        self.h = 48
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.shield = self._make_base()

    def _make_base(self):
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        pygame.draw.rect(s, (0, 180, 120, 190), s.get_rect(), border_radius=8)
        pygame.draw.rect(s, (0, 255, 150, 255), s.get_rect().inflate(-6, -6), border_radius=6)
        pygame.draw.rect(s, (170, 255, 225, 210), s.get_rect().inflate(-14, -14), border_radius=4)

        self._clear_rect(s, self.w // 2 - 10, self.h // 2, 20, self.h // 2)
        self._clear_rect(s, 0, self.h - 16, 10, 16)
        self._clear_rect(s, self.w - 10, self.h - 16, 10, 16)

        return s

    def _clear_rect(self, s, x, y, w, h):
        for py in range(max(0, y), min(self.h, y + h)):
            for px in range(max(0, x), min(self.w, x + w)):
                if s.get_at((px, py))[3] > 0:
                    s.set_at((px, py), (0, 0, 0, 0))

    def _clear_circle(self, cx, cy, radius):
        cx = int(cx)
        cy = int(cy)
        radius = int(radius)

        for dy in range(-radius, radius + 1):
            y = cy + dy
            if 0 <= y < self.h:
                for dx in range(-radius, radius + 1):
                    x = cx + dx
                    if 0 <= x < self.w and dx * dx + dy * dy <= radius * radius:
                        if self.shield.get_at((x, y))[3] > 0:
                            self.shield.set_at((x, y), (0, 0, 0, 0))

    def repair(self):
        self.shield = self._make_base()

    def is_solid_at(self, point):
        x = point[0] - self.rect.x
        y = point[1] - self.rect.y

        if 0 <= x < self.w and 0 <= y < self.h:
            return self.shield.get_at((int(x), int(y)))[3] > 25

        return False

    def damage(self, point, radius=9):
        cx = point[0] - self.rect.x
        cy = point[1] - self.rect.y

        self._clear_circle(cx, cy, radius)

        for _ in range(4):
            rx = cx + random.randint(-radius, radius)
            ry = cy + random.randint(-radius, radius)
            self._clear_circle(rx, ry, 2)

        return True


class Bullet:
    def __init__(self, x, y, game):
        self.rect = pygame.Rect(int(x) - 4, int(y) - 18, 8, 18)
        self.vel = pygame.Vector2(0, -520)
        self.alive = True
        self.game = game

    def update(self, dt):
        self.rect.y += int(round(self.vel.y * dt))

        if self.rect.bottom < 0:
            self.alive = False
            return

        for shield in self.game.shields:
            if self.rect.colliderect(shield.rect):
                for p in (
                    (self.rect.centerx, self.rect.top + 2),
                    self.rect.center,
                    (self.rect.centerx, self.rect.bottom - 2)
                ):
                    if shield.is_solid_at(p):
                        shield.damage(p, 8)
                        self.game.explosion(p, (0, 255, 150), 6, 80)
                        self.game.sfx.play('shield', 0.4)
                        self.alive = False
                        return

        for inv in self.game.invaders.invaders:
            if inv.alive and self.rect.colliderect(inv.rect):
                self.game.kill_invader(inv)
                self.alive = False
                return

        if self.game.ufo and self.rect.colliderect(self.game.ufo.rect):
            self.game.hit_ufo()
            self.alive = False


class Bomb:
    def __init__(self, x, y, game):
        self.rect = pygame.Rect(int(x) - 5, int(y), 10, 20)
        self.vel = pygame.Vector2(0, 170 + game.level * 12)
        self.alive = True
        self.game = game

    def update(self, dt):
        self.rect.y += int(round(self.vel.y * dt))

        if self.rect.top > HEIGHT:
            self.alive = False
            return

        for shield in self.game.shields:
            if self.rect.colliderect(shield.rect):
                for p in (
                    (self.rect.centerx, self.rect.top + 2),
                    self.rect.center,
                    (self.rect.centerx, self.rect.bottom - 2)
                ):
                    if shield.is_solid_at(p):
                        shield.damage(p, 9)
                        self.game.explosion(p, (0, 255, 150), 8, 90)
                        self.game.sfx.play('shield', 0.45)
                        self.alive = False
                        return

        if self.game.player.invuln <= 0 and self.rect.colliderect(self.game.player.rect):
            self.game.player.hit()
            self.alive = False
            return


class PowerUp:
    def __init__(self, x, y, kind, game):
        self.rect = pygame.Rect(int(x) - 17, int(y), 34, 26)
        self.base_x = int(x)
        self.kind = kind
        self.vel = pygame.Vector2(0, 95)
        self.alive = True
        self.t = random.uniform(0, 10)
        self.sprite = game.powerup_sprites[kind]
        self.game = game

    def update(self, dt):
        self.t += dt
        self.rect.y += int(self.vel.y * dt)
        self.rect.x = int(self.base_x + 8 * math.sin(self.t * 3.0) - 17)

        if self.rect.top > HEIGHT:
            self.alive = False
            return

        if self.rect.colliderect(self.game.player.rect):
            self.alive = False
            self.game.apply_powerup(self.kind, self.rect.center)


class UFO:
    def __init__(self, game, direction):
        self.game = game
        self.rect = pygame.Rect(
            -60 if direction > 0 else WIDTH + 10,
            46,
            52,
            24
        )
        self.vel = pygame.Vector2(direction * 120, 0)
        self.alive = True
        self.score = random.choice(
            [50, 100, 150, 300] + ([500] if game.level > 5 else [])
        )
        self.sound_timer = 0.5

    def update(self, dt):
        self.rect.x += int(round(self.vel.x * dt))

        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.alive = False
            return

        self.sound_timer -= dt
        if self.sound_timer <= 0:
            self.game.sfx.play('ufo', 0.3)
            self.sound_timer = 0.55


class Player:
    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(WIDTH // 2 - 20, HEIGHT - 56, 40, 26)
        self.speed = 340
        self.cooldown = 0.0
        self.invuln = 0.0

    def update(self, dt):
        self.invuln = max(0.0, self.invuln - dt)

        if self.cooldown > 0:
            self.cooldown -= dt

        keys = pygame.key.get_pressed()
        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1

        self.rect.x += int(self.speed * dx * dt)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if keys[pygame.K_SPACE] and self.cooldown <= 0:
            self.shoot()

    def shoot(self):
        top_y = self.rect.top + 4

        if self.game.double_timer > 0:
            self.game.bullets.append(Bullet(self.rect.centerx - 12, top_y, self.game))
            self.game.bullets.append(Bullet(self.rect.centerx + 12, top_y, self.game))
            delay = 0.3 if self.game.rapid_timer > 0 else 0.6
        else:
            self.game.bullets.append(Bullet(self.rect.centerx, top_y, self.game))
            delay = 0.14 if self.game.rapid_timer > 0 else 0.42

        self.cooldown = delay
        self.game.sfx.play('shoot', 0.45)

        self.game.particles.append({
            'pos': pygame.Vector2(self.rect.centerx, top_y),
            'vel': pygame.Vector2(0, -40),
            'life': 0.08,
            'max': 0.08,
            'color': (200, 255, 255),
            'size': 4
        })

    def hit(self):
        if self.invuln > 0:
            return

        self.game.lives -= 1
        self.game.explosion(self.rect.center, (0, 255, 255), 35, 220)
        self.game.explosion(self.rect.center, (255, 160, 60), 20, 160)
        self.game.sfx.play('player')
        self.game.shake = 8
        self.invuln = 2.0

        if self.game.lives <= 0:
            self.game.game_over()

    def draw(self, screen):
        if self.invuln > 0 and (pygame.time.get_ticks() // 100) % 2 == 0:
            return

        screen.blit(self.game.player_sprite, self.rect)


class Invader:
    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(int(x), int(y), 32, 24)
        self.kind = kind
        self.alive = True


class Invaders:
    def __init__(self, level, game):
        self.game = game

        self.cols = 10
        self.rows = 5

        if level >= 3:
            self.rows = 6
        if level >= 6:
            self.rows = 7
        if level >= 10:
            self.rows = 8

        self.spacing_x = 44
        self.spacing_y = 36

        total_width = (self.cols - 1) * self.spacing_x
        self.start_x = (WIDTH - total_width) // 2
        self.start_y = 80

        self.invaders = []

        for r in range(self.rows):
            if r == 0:
                kind = 0
            elif r < self.rows // 2:
                kind = 1
            else:
                kind = 2

            for c in range(self.cols):
                x = self.start_x + c * self.spacing_x
                y = self.start_y + r * self.spacing_y
                self.invaders.append(Invader(x, y, kind))

        self.initial = len(self.invaders)
        self.dir = 1
        self.base_speed = 22 + level * 4
        self.frame = 0
        self.frame_timer = 0.0
        self.move_x = 0.0
        self.bomb_timer = random.uniform(1.5, 3.0)

    def update(self, dt):
        game = self.game

        if not self.invaders:
            return

        speed = self.base_speed * (1.0 + 0.9 * (1.0 - len(self.invaders) / self.initial))

        self.move_x += speed * dt * self.dir
        step = int(self.move_x)

        if step != 0:
            for inv in self.invaders:
                inv.rect.x += step

            self.move_x -= step

            left_limit = 30
            right_limit = WIDTH - 30
            hit_edge = False

            for inv in self.invaders:
                if inv.rect.right > right_limit:
                    inv.rect.right = right_limit
                    hit_edge = True

                if inv.rect.left < left_limit:
                    inv.rect.left = left_limit
                    hit_edge = True

            if hit_edge:
                self.dir *= -1
                self.move_x = 0.0

                for inv in self.invaders:
                    inv.rect.y += 18

                game.sfx.play('step1' if self.dir > 0 else 'step2', 0.45)

                for inv in self.invaders:
                    for shield in game.shields:
                        if inv.rect.colliderect(shield.rect):
                            for p in (
                                    (inv.rect.centerx, inv.rect.bottom),
                                    inv.rect.center,
                                    (inv.rect.centerx, inv.rect.top)
                            ):
                                if shield.is_solid_at(p):
                                    shield.damage(p, 10)
                                    break

                if any(inv.rect.bottom >= game.player.rect.top - 4 for inv in self.invaders):
                    game.game_over()
                    return

        self.frame_timer += dt
        if self.frame_timer > 0.35:
            self.frame ^= 1
            self.frame_timer = 0.0

        self.bomb_timer -= dt
        if self.bomb_timer <= 0:
            self.spawn_bomb()

            count_factor = len(self.invaders) / self.initial
            self.bomb_timer = random.uniform(
                max(0.35, 2.0 * count_factor - 0.4),
                max(0.8, 3.4 * count_factor)
            )

    def spawn_bomb(self):
        if not self.invaders:
            return

        candidates = sorted(self.invaders, key=lambda i: i.rect.bottom)
        n = min(3, len(candidates))
        inv = random.choice(candidates[-n:])

        self.game.bombs.append(Bomb(inv.rect.centerx, inv.rect.bottom, self.game))

    def draw(self, screen):
        for inv in self.invaders:
            sprite = self.game.invader_sprites[inv.kind][self.frame]
            screen.blit(sprite, (inv.rect.x, inv.rect.y))


class Game:
    def __init__(self, screen, sfx, stats):
        self.screen = screen
        self.sfx = sfx
        self.stats = stats
        self.running = True

        self.bg = make_background()

        self.stars = []
        for _ in range(120):
            layer = random.randint(0, 2)

            r = min(255, 100 + layer * 40)
            g = min(255, 100 + layer * 40)
            b = min(255, 160 + layer * 50)

            self.stars.append([
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                8 + layer * 14,
                (r, g, b),
                1 + layer // 2
            ])

        self.fonts = {
            'small': make_font(18),
            'medium': make_font(26),
            'large': make_font(44),
            'title': make_font(62)
        }

        self.player_sprite = make_player_sprite()
        self.mini_player = pygame.transform.scale(self.player_sprite, (20, 13))
        self.bullet_sprite = make_bullet_sprite((140, 255, 255))
        self.bomb_sprite = make_bomb_sprite((255, 140, 80))
        self.ufo_sprite = make_ufo_sprite()
        self.powerup_sprites = {kind: make_powerup_sprite(kind) for kind in POWERUP_COLORS}
        self.powerup_weights = {
            '2X': 25,
            'RAPID': 25,
            'DOUBLE': 20,
            'SHIELD': 15,
            '1UP': 15
        }

        self.player = Player(self)

        self.shields = []
        self.bullets = []
        self.bombs = []
        self.powerups = []
        self.particles = []
        self.popups = []

        self.ufo = None
        self.ufo_timer = random.uniform(18, 30)

        self.level = 1
        self.pending_level = 2
        self.intro_timer = 0

        self.score = 0
        self.lives = 3
        self.kills = 0
        self.bonus_count = 0
        self.powerups_collected = 0
        self.life_threshold = 10000

        self.multiplier = 1
        self.multi_timer = 0
        self.rapid_timer = 0
        self.double_timer = 0

        self.shake = 0
        self.session_time = 0

        self.setup_level(1)
        self.state = 'menu'

    def setup_level(self, level):
        self.level = level

        self.player.rect.x = WIDTH // 2 - self.player.rect.width // 2
        self.player.rect.y = HEIGHT - 56
        self.player.cooldown = 0.0
        self.player.invuln = 1.2

        self.bullets = []
        self.bombs = []
        self.powerups = []
        self.ufo = None
        self.ufo_timer = random.uniform(15, 28)

        shield_y = HEIGHT - 132
        xs = [110, 270, 430, 590]
        self.shields = [Shield(x, shield_y) for x in xs]

        palettes = [
            [(255, 90, 210), (0, 230, 170), (255, 210, 90)],
            [(255, 130, 80), (255, 210, 90), (90, 210, 255)],
            [(90, 255, 255), (255, 90, 120), (255, 255, 90)],
            [(255, 90, 90), (90, 255, 90), (90, 120, 255)]
        ]

        self.invader_colors = palettes[(level - 1) % len(palettes)]
        self.invader_sprites = [
            [make_invader_sprite(kind, frame, self.invader_colors[kind]) for frame in (0, 1)]
            for kind in range(3)
        ]

        self.invaders = Invaders(level, self)

        self.multiplier = 1
        self.multi_timer = 0
        self.rapid_timer = 0
        self.double_timer = 0
        self.shake = 0

    def start_game(self):
        self.score = 0
        self.lives = 3
        self.kills = 0
        self.bonus_count = 0
        self.powerups_collected = 0
        self.life_threshold = 10000
        self.session_time = 0

        self.setup_level(1)
        self.state = 'playing'
        self.sfx.play('select')

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            if self.state in ('playing', 'paused', 'level_intro'):
                self.game_over()
            self.running = False
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_m:
            self.sfx.toggle()
            return

        if self.state == 'menu':
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == 'playing':
            if event.key == pygame.K_p:
                self.state = 'paused'
                self.sfx.play('select', 0.3)
            elif event.key == pygame.K_ESCAPE:
                self.state = 'paused'

        elif self.state == 'paused':
            if event.key in (pygame.K_p, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.state = 'playing'
                self.sfx.play('select', 0.3)

        elif self.state == 'gameover':
            if event.key == pygame.K_RETURN:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = 'menu'

    def update(self, dt):
        self.update_stars(dt)
        self.update_particles(dt)
        self.update_popups(dt)

        if self.state == 'playing':
            self.session_time += dt
            self.update_timers(dt)
            self.player.update(dt)

            if self.state == 'playing':
                self.invaders.update(dt)

            if self.state == 'playing':
                for b in self.bullets:
                    b.update(dt)

                for b in self.bombs:
                    b.update(dt)

                for bomb in self.bombs:
                    if not bomb.alive:
                        continue

                    for bullet in self.bullets:
                        if bullet.alive and bomb.rect.colliderect(bullet.rect):
                            bomb.alive = False
                            bullet.alive = False
                            self.explosion(bomb.rect.center, (255, 255, 255), 10, 120)
                            self.sfx.play('shield', 0.35)
                            break

                if self.state == 'playing':
                    for p in self.powerups:
                        p.update(dt)

                    if self.ufo:
                        self.ufo.update(dt)
                    else:
                        self.ufo_timer -= dt
                        if self.ufo_timer <= 0:
                            direction = random.choice([-1, 1])
                            self.ufo = UFO(self, direction)
                            self.ufo_timer = random.uniform(18, 32)

                self.bullets = [b for b in self.bullets if b.alive]
                self.bombs = [b for b in self.bombs if b.alive]
                self.powerups = [p for p in self.powerups if p.alive]
                self.invaders.invaders = [i for i in self.invaders.invaders if i.alive]

                if self.ufo and not self.ufo.alive:
                    self.ufo = None

                if self.state == 'playing' and not self.invaders.invaders:
                    self.level_complete()

        elif self.state == 'level_intro':
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.state = 'playing'

    def update_timers(self, dt):
        if self.multi_timer > 0:
            self.multi_timer -= dt
            if self.multi_timer <= 0:
                self.multi_timer = 0
                self.multiplier = 1

        if self.rapid_timer > 0:
            self.rapid_timer = max(0.0, self.rapid_timer - dt)

        if self.double_timer > 0:
            self.double_timer = max(0.0, self.double_timer - dt)

        if self.shake > 0:
            self.shake = max(0.0, self.shake - 60 * dt)

    def update_stars(self, dt):
        for star in self.stars:
            star[0] -= star[2] * dt
            if star[0] < -5:
                star[0] = WIDTH + 5
                star[1] = random.randint(0, HEIGHT)

    def update_particles(self, dt):
        if not self.particles:
            return

        new = []

        for p in self.particles:
            p['life'] -= dt
            if p['life'] <= 0:
                continue

            if 'ring' in p:
                p['radius'] += 200 * dt
            else:
                p['pos'] += p['vel'] * dt
                p['vel'] *= 0.95

            new.append(p)

        self.particles = new

    def update_popups(self, dt):
        new = []

        for p in self.popups:
            p['pos'] += p['vel'] * dt
            p['life'] -= dt
            if p['life'] > 0:
                new.append(p)

        self.popups = new

    def explosion(self, pos, color, n=20, speed=180):
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            v = random.uniform(30, speed)
            life = random.uniform(0.25, 0.6)

            self.particles.append({
                'pos': pygame.Vector2(pos),
                'vel': pygame.Vector2(math.cos(angle) * v, math.sin(angle) * v),
                'life': life,
                'max': life,
                'color': color,
                'size': random.randint(2, 5)
            })

        self.particles.append({
            'ring': True,
            'pos': pygame.Vector2(pos),
            'life': 0.22,
            'max': 0.22,
            'color': color,
            'radius': 4
        })

    def add_popup(self, text, pos, color, size='medium', life=1.0):
        self.popups.append({
            'text': text,
            'pos': pygame.Vector2(pos),
            'vel': pygame.Vector2(0, -35),
            'color': color,
            'font': self.fonts.get(size, self.fonts['medium']),
            'life': life,
            'max': life
        })

    def add_score(self, points, pos=None, color=None, apply_mult=True, popup=True):
        points = int(points * (self.multiplier if apply_mult else 1))
        self.score += points

        if pos is not None and popup and points != 0:
            if color is None:
                color = (255, 255, 255)
            self.add_popup(f"+{points}", pos, color, 'small', 0.8)

        while self.score >= self.life_threshold:
            self.lives += 1
            self.life_threshold += 10000
            self.bonus_count += 1
            self.add_popup(
                "1UP BONUS",
                (self.player.rect.centerx, self.player.rect.top - 24),
                (255, 120, 220),
                'medium',
                1.2
            )
            self.sfx.play('bonus')

    def kill_invader(self, inv):
        inv.alive = False
        self.kills += 1

        base = (30, 20, 10)[inv.kind]
        color = self.invader_colors[inv.kind]

        self.explosion(inv.rect.center, color, 22, 170)
        self.add_score(base, inv.rect.center, color)
        self.sfx.play('hit')

        chance = min(0.12, 0.04 + 0.005 * self.level)
        if random.random() < chance:
            kind = random.choices(
                list(self.powerup_weights.keys()),
                weights=list(self.powerup_weights.values())
            )[0]

            if kind == '1UP' and self.lives >= 8:
                kind = '2X'

            self.powerups.append(PowerUp(inv.rect.centerx, inv.rect.top, kind, self))

    def hit_ufo(self):
        if not self.ufo:
            return

        score = self.ufo.score
        pos = self.ufo.rect.center

        self.explosion(pos, (255, 120, 120), 35, 220)
        self.add_score(score, pos, (255, 120, 120), apply_mult=False)
        self.add_popup(f"UFO +{score}", pos, (255, 120, 120), 'medium')
        self.sfx.play('bonus')
        self.bonus_count += 1
        self.ufo.alive = False

    def apply_powerup(self, kind, pos):
        self.powerups_collected += 1
        color = POWERUP_COLORS[kind]

        self.add_score(25, pos, color, apply_mult=False, popup=False)

        if kind == '2X':
            self.multiplier = 2
            self.multi_timer = 12.0
            self.add_popup("SCORE 2X", pos, color, 'medium', 1.2)

        elif kind == 'RAPID':
            self.rapid_timer = 10.0
            self.add_popup("RAPID FIRE", pos, color, 'medium', 1.2)

        elif kind == 'DOUBLE':
            self.double_timer = 15.0
            self.add_popup("DOUBLE SHOT", pos, color, 'medium', 1.2)

        elif kind == 'SHIELD':
            for shield in self.shields:
                shield.repair()
            self.add_popup("SHIELDS REPAIRED", pos, color, 'medium', 1.2)

        elif kind == '1UP':
            self.lives += 1
            self.life_threshold = max(self.life_threshold, self.score + 10000)
            self.add_popup("EXTRA LIFE", pos, color, 'large', 1.4)

        self.bonus_count += 1

    def level_complete(self):
        bonus = 100 * self.level
        self.add_score(bonus, (WIDTH // 2, HEIGHT // 2 - 20), (255, 220, 120), apply_mult=False)
        self.bonus_count += 1
        self.sfx.play('level')

        self.pending_level = self.level + 1
        self.setup_level(self.pending_level)

        self.add_popup(
            f"LEVEL {self.level} CLEARED",
            (WIDTH // 2, HEIGHT // 2 - 80),
            (140, 255, 255),
            'large',
            2.0
        )

        self.intro_timer = 2.0
        self.state = 'level_intro'

    def game_over(self):
        if self.state == 'gameover':
            return

        self.state = 'gameover'
        self.sfx.play('gameover')

        self.stats['games_played'] = self.stats.get('games_played', 0) + 1
        self.stats['best_score'] = max(self.stats.get('best_score', 0), self.score)
        self.stats['max_level'] = max(self.stats.get('max_level', 0), self.level)
        self.stats['total_kills'] = self.stats.get('total_kills', 0) + self.kills
        self.stats['total_bonuses'] = self.stats.get('total_bonuses', 0) + self.bonus_count
        self.stats['total_powerups'] = self.stats.get('total_powerups', 0) + self.powerups_collected
        self.stats['total_time'] = self.stats.get('total_time', 0) + self.session_time

        save_stats(self.stats)

    def draw_stars(self):
        for star in self.stars:
            x, y, speed, color, size = star

            r = max(0, min(255, color[0]))
            g = max(0, min(255, color[1]))
            b = max(0, min(255, color[2]))

            pygame.draw.circle(
                self.screen,
                (r, g, b),
                (int(x), int(y)),
                size
            )

    def draw_particles(self):
        for p in self.particles:
            alpha = p['life'] / p['max']

            if 'ring' in p:
                radius = int(p['radius'])
                if radius < 1:
                    continue
                width = max(1, int(4 * alpha))
                pygame.draw.circle(
                    self.screen,
                    p['color'],
                    (int(p['pos'].x), int(p['pos'].y)),
                    radius,
                    width
                )
            else:
                size = max(1, int(p['size'] * alpha))
                pygame.draw.circle(
                    self.screen,
                    p['color'],
                    (int(p['pos'].x), int(p['pos'].y)),
                    size
                )

    def draw_popups(self):
        for p in self.popups:
            alpha = int(255 * max(0.0, min(1.0, p['life'] / p['max'])))
            surf = p['font'].render(p['text'], True, p['color'])
            if alpha < 255:
                surf.set_alpha(alpha)
            rect = surf.get_rect(center=(int(p['pos'].x), int(p['pos'].y)))
            self.screen.blit(surf, rect)

    def draw_hud(self):
        bar = pygame.Surface((WIDTH, 38), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 110))
        self.screen.blit(bar, (0, 0))

        score_surf = self.fonts['medium'].render(f"SCORE {self.score:06d}", True, (255, 255, 255))
        self.screen.blit(score_surf, (16, 5))

        hi = max(self.stats.get('best_score', 0), self.score)
        hi_surf = self.fonts['medium'].render(f"HI {hi:06d}", True, (255, 220, 120))
        self.screen.blit(hi_surf, (WIDTH - hi_surf.get_width() - 16, 5))

        level_surf = self.fonts['medium'].render(f"LEVEL {self.level}", True, (140, 255, 255))
        self.screen.blit(level_surf, (WIDTH // 2 - level_surf.get_width() // 2, 5))

        for i in range(max(0, self.lives)):
            self.screen.blit(self.mini_player, (18 + i * 26, HEIGHT - 32))

        x = WIDTH - 210
        y = 44

        if self.multi_timer > 0:
            rect = pygame.Rect(x, y, 62, 22)
            pygame.draw.rect(self.screen, POWERUP_COLORS['2X'], rect, border_radius=6)
            text = self.fonts['small'].render(f"2X {int(self.multi_timer)}", True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=rect.center))
            x += 70

        if self.rapid_timer > 0:
            rect = pygame.Rect(x, y, 70, 22)
            pygame.draw.rect(self.screen, POWERUP_COLORS['RAPID'], rect, border_radius=6)
            text = self.fonts['small'].render(f"SPD {int(self.rapid_timer)}", True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=rect.center))
            x += 78

        if self.double_timer > 0:
            rect = pygame.Rect(x, y, 70, 22)
            pygame.draw.rect(self.screen, POWERUP_COLORS['DOUBLE'], rect, border_radius=6)
            text = self.fonts['small'].render(f"DUAL {int(self.double_timer)}", True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=rect.center))

    def _overlay(self, alpha=170):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 20, alpha))
        self.screen.blit(s, (0, 0))


    def draw_playfield(self):
        self.screen.blit(self.bg, (0, 0))
        self.draw_stars()

        for shield in self.shields:
            self.screen.blit(shield.shield, shield.rect)

        for p in self.powerups:
            self.screen.blit(p.sprite, p.rect)

        self.invaders.draw(self.screen)

        if self.ufo:
            self.screen.blit(self.ufo_sprite, self.ufo.rect)

        for bomb in self.bombs:
            self.screen.blit(self.bomb_sprite, bomb.rect)

        for bullet in self.bullets:
            self.screen.blit(self.bullet_sprite, bullet.rect)

        self.player.draw(self.screen)
        self.draw_particles()
        self.draw_popups()
        self.draw_hud()

    def draw_menu(self):
        self.screen.blit(self.bg, (0, 0))
        self.draw_stars()

        title = "SPACE INVADERS"
        font = self.fonts['title']
        total_width = sum(font.size(c)[0] for c in title)

        x = WIDTH // 2 - total_width // 2
        y = 70

        colors = [
            (0, 255, 255),
            (255, 120, 220),
            (255, 220, 120),
            (120, 255, 180)
        ]

        for i, c in enumerate(title):
            shadow = font.render(c, True, (0, 0, 0))
            surf = font.render(c, True, colors[i % len(colors)])
            self.screen.blit(shadow, (x + 3, y + 3))
            self.screen.blit(surf, (x, y))
            x += font.size(c)[0]

        for kind in range(3):
            frame = (pygame.time.get_ticks() // 400) % 2
            sprite = self.invader_sprites[kind][frame]
            self.screen.blit(sprite, (WIDTH // 2 - 78 + kind * 50, 175))

        lines = [
            f"BEST SCORE: {self.stats.get('best_score', 0)}",
            f"GAMES: {self.stats.get('games_played', 0)}   MAX LEVEL: {self.stats.get('max_level', 0)}",
            f"KILLS: {self.stats.get('total_kills', 0)}   BONUS: {self.stats.get('total_bonuses', 0)}",
            f"TIME: {int(self.stats.get('total_time', 0)) // 60}m {int(self.stats.get('total_time', 0)) % 60}s"
        ]

        y = 250
        for line in lines:
            surf = self.fonts['medium'].render(line, True, (220, 220, 255))
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
            y += 36

        instr = [
            "ARROWS / A D  MOVE",
            "SPACE  SHOOT",
            "P  PAUSE    M  MUTE"
        ]

        y = 430
        for line in instr:
            surf = self.fonts['small'].render(line, True, (180, 180, 220))
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
            y += 26

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            surf = self.fonts['large'].render("PRESS ENTER TO START", True, (255, 255, 120))
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 510))

    def draw_pause(self):
        self.draw_playfield()
        self._overlay()

        surf = self.fonts['title'].render("PAUSED", True, (255, 255, 255))
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - 60))

        surf = self.fonts['medium'].render("P TO RESUME", True, (200, 200, 220))
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 + 10))

    def draw_gameover(self):
        self.draw_playfield()
        self._overlay(180)

        surf = self.fonts['title'].render("GAME OVER", True, (255, 80, 120))
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 130))

        lines = [
            f"SCORE: {self.score}",
            f"BEST: {self.stats.get('best_score', 0)}",
            f"LEVEL: {self.level}",
            f"KILLS: {self.kills}   BONUS: {self.bonus_count}"
        ]

        y = 260
        for line in lines:
            surf = self.fonts['medium'].render(line, True, (230, 230, 255))
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
            y += 40

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            surf = self.fonts['large'].render("PRESS ENTER TO PLAY AGAIN", True, (255, 255, 120))
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 470))

        surf = self.fonts['small'].render("ESC FOR MENU", True, (180, 180, 220))
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 520))

    def draw_level_intro(self):
        self.draw_playfield()
        self._overlay(120)

        surf = self.fonts['title'].render(f"LEVEL {self.level}", True, (140, 255, 255))
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - 80))

        surf = self.fonts['large'].render("GET READY", True, (255, 255, 255))
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2))

    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_playfield()
        elif self.state == 'paused':
            self.draw_pause()
        elif self.state == 'gameover':
            self.draw_gameover()
        elif self.state == 'level_intro':
            self.draw_level_intro()


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    try:
        pygame.mixer.set_num_channels(16)
    except Exception:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")

    sfx = SFX()
    stats = load_stats()
    game = Game(screen, sfx, stats)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = min(0.05, clock.tick(FPS) / 1000.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            game.handle_event(event)

            if not game.running:
                running = False

        if not running:
            break

        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
