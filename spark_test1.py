"""
SPACE INVADERS — fully self-contained pygame game.
All graphics are drawn procedurally, all sound effects + music are synthesized
with numpy (no downloaded assets). Progress/stats are saved to a JSON file.
"""
import os, json, math, random, time, sys
import numpy as np
import pygame
import pygame.sndarray

# ---------------------------- CONFIG ----------------------------
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
SAVE_FILE = "space_invaders_save.json"
SAMPLE_RATE = 44100

# Visual palette
BG_COLOR      = (8, 10, 22)
STAR_COLOR    = (150, 170, 200)
PLAYER_COLOR  = (70, 200, 255)
BARRIER_COLOR = (90, 200, 120)
BULLET_COLOR  = (255, 120, 60)
TEXT_COLOR    = (220, 230, 245)
ACCENT_COLOR  = (255, 80, 120)

ALIEN_COLORS = [(90, 220, 120), (60, 200, 220), (240, 120, 200)]

# ---------------------------- SAVE / LOAD ----------------------------
def default_save():
    return {
        "high_score": 0,
        "games_played": 0,
        "total_kills": 0,
        "total_time": 0.0,
        "best_level": 1,
        "unlocked_level": 1,
    }

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            d = default_save()
            d.update(data)
            return d
        except Exception:
            pass
    return default_save()

def save_stats(stats):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

# ---------------------------- SOUND SYNTHESIS ----------------------------
def _array_to_sound(arr):
    """Converts a numpy array to a pygame Sound object, ensuring stereo compatibility."""
    arr = np.clip(arr, -1.0, 1.0)
    data = (arr * 32767).astype(np.int16)
    # FIX: Ensure array is 2D for stereo mixers by duplicating mono channel
    if data.ndim == 1:
        data = np.column_stack((data, data))
    return pygame.sndarray.make_sound(data)

def synth_tone(freq, dur, amp=0.35, kind="square"):
    """A single tone with a soft attack + exponential decay."""
    n = int(SAMPLE_RATE * dur)
    t = np.arange(n) / SAMPLE_RATE
    if kind == "square":
        sig = np.sign(np.sin(2 * np.pi * freq * t))
    elif kind == "saw":
        sig = 2.0 * ((freq * t) % 1.0) - 1.0
    elif kind == "triangle":
        sig = 2.0 * np.abs(2.0 * ((freq * t) % 1.0) - 1.0) - 1.0
    else:  # sine
        sig = np.sin(2 * np.pi * freq * t)
    env = np.minimum(1.0, t * 90.0) * np.exp(-4.0 * t)
    return amp * sig * env

def synth_sweep(f0, f1, dur, amp=0.35, kind="square"):
    """Frequency sweep with decaying envelope (shoot / crash effects)."""
    n = int(SAMPLE_RATE * dur)
    t = np.arange(n) / SAMPLE_RATE
    freq = np.linspace(f0, f1, n)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    if kind == "square":
        sig = np.sign(np.sin(phase))
    else:
        sig = np.sin(phase)
    env = np.minimum(1.0, t * 90.0) * np.exp(-3.2 * t)
    return amp * sig * env

def synth_noise(dur, amp=0.5):
    """Filtered white-noise burst (explosion)."""
    n = int(SAMPLE_RATE * dur)
    noise = np.random.uniform(-1, 1, n)
    t = np.arange(n) / SAMPLE_RATE
    env = np.minimum(1.0, t * 160.0) * np.exp(-6.5 * t)
    k = max(1, int(SAMPLE_RATE * 0.0006))
    kern = np.ones(k) / k
    noise = np.convolve(noise, kern, mode="same")
    return amp * noise * env

def _concat(sounds):
    return np.concatenate(sounds) if sounds else np.zeros(1)

def make_sfx():
    """Build every sound effect the game needs."""
    sfx = {}
    sfx["shoot"]     = _array_to_sound(synth_sweep(520, 140, 0.10, 0.28))
    sfx["invader"]   = _array_to_sound(synth_tone(190, 0.09, 0.20))
    sfx["explosion"] = _array_to_sound(synth_noise(0.38, 0.45))
    sfx["player_hit"]= _array_to_sound(synth_sweep(950, 60, 0.55, 0.4))
    bonus = _concat([synth_tone(f, 0.13, 0.30, "triangle") for f in (523, 659, 784, 1047)])
    sfx["bonus"] = _array_to_sound(bonus)
    fanfare = _concat([synth_tone(f, 0.16, 0.30, "square") for f in (523, 659, 784, 1047)])
    sfx["level_clear"] = _array_to_sound(fanfare)
    return sfx

def make_music():
    """A small chiptune loop."""
    bass_seq = [131, 131, 131, 131, 165, 165, 165, 165,
                196, 196, 196, 196, 131, 131, 131, 131]
    lead_seq = [523, 659, 784, 659, 587, 659, 587, 523,
                523, 659, 784, 659, 880, 784, 659, 587]
    beat = 0.28
    parts = []
    for i, (b, l) in enumerate(zip(bass_seq, lead_seq)):
        parts.append(synth_tone(b, beat, 0.16, "triangle"))
        if l:
            parts.append(synth_tone(l, beat, 0.13, "square"))
        else:
            parts.append(np.zeros(int(SAMPLE_RATE * beat)))
    song = _concat(parts)
    return _array_to_sound(song)

# ---------------------------- SPRITE GENERATION ----------------------------
def make_player_sprite():
    s = pygame.Surface((48, 32), pygame.SRCALPHA)
    pygame.draw.polygon(s, PLAYER_COLOR, [(6, 28), (20, 22), (20, 30)])
    pygame.draw.polygon(s, PLAYER_COLOR, [(42, 28), (28, 22), (28, 30)])
    pygame.draw.polygon(s, PLAYER_COLOR, [(18, 30), (30, 30), (30, 16), (24, 8), (18, 16)])
    pygame.draw.rect(s, (220, 240, 255), (22, 6, 4, 8))
    pygame.draw.circle(s, (255, 200, 60), (24, 20), 3)
    pygame.draw.circle(s, (70, 200, 255, 90), (24, 28), 12, 1)
    return s

def draw_alien(surf, color, frame, kind):
    s = pygame.Surface((52, 40), pygame.SRCALPHA)
    if kind == 0:
        pygame.draw.ellipse(s, color, (10, 8, 32, 22))
        pygame.draw.circle(s, (255, 255, 255), (20, 15), 3)
        pygame.draw.circle(s, (255, 255, 255), (32, 15), 3)
        pygame.draw.line(s, color, (20, 10), (16, 2), 2)
        pygame.draw.line(s, color, (32, 10), (36, 2), 2)
        if frame == 0:
            pygame.draw.line(s, color, (18, 30), (12, 36), 3)
            pygame.draw.line(s, color, (34, 30), (40, 36), 3)
        else:
            pygame.draw.line(s, color, (18, 30), (24, 36), 3)
            pygame.draw.line(s, color, (34, 30), (28, 36), 3)
    elif kind == 1:
        pygame.draw.ellipse(s, color, (4, 6, 44, 26))
        pygame.draw.circle(s, (255, 255, 255), (18, 18), 3)
        pygame.draw.circle(s, (255, 255, 255), (34, 18), 3)
        if frame == 0:
            for x in (16, 24, 32, 40): pygame.draw.line(s, color, (x, 32), (x - 6, 38), 2)
        else:
            for x in (16, 24, 32, 40): pygame.draw.line(s, color, (x, 32), (x + 6, 38), 2)
    else:
        pygame.draw.ellipse(s, color, (14, 4, 24, 16))
        pygame.draw.ellipse(s, color, (10, 16, 32, 18))
        if frame == 0:
            pygame.draw.line(s, color, (22, 34), (18, 38), 3)
            pygame.draw.line(s, color, (30, 34), (34, 38), 3)
        else:
            pygame.draw.line(s, color, (22, 34), (26, 38), 3)
            pygame.draw.line(s, color, (30, 34), (26, 38), 3)
    return s

def make_alien_sprites():
    sprites = {}
    for kind in range(3):
        sprites[kind] = [draw_alien(None, ALIEN_COLORS[kind], f, kind) for f in (0, 1)]
    return sprites

def make_barrier_sprite():
    s = pygame.Surface((18, 18), pygame.SRCALPHA)
    pygame.draw.rect(s, BARRIER_COLOR, (0, 0, 18, 18))
    return s

def make_bullet_sprite():
    s = pygame.Surface((6, 16), pygame.SRCALPHA)
    pygame.draw.rect(s, BULLET_COLOR, (0, 2, 6, 14))
    return s

def make_explosion_frames():
    frames = []
    for i in range(8):
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        r = int(4 + i * 3.2)
        pygame.draw.circle(s, (255, 200, 60), (24, 24), r)
        frames.append(s)
    return frames

def make_powerup_sprites():
    sprites = {}
    s = pygame.Surface((34, 30), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 80, 120), (17, 10), 8)
    sprites["life"] = s
    s = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 230, 90), (15, 15), 12)
    sprites["score"] = s
    s = pygame.Surface((34, 34), pygame.SRCALPHA)
    pygame.draw.circle(s, (120, 200, 255), (17, 17), 14)
    sprites["rapid"] = s
    return sprites

def make_background(w, h, n=140):
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill(BG_COLOR)
    for _ in range(n):
        x, y = random.randint(0, w), random.randint(0, h)
        pygame.draw.circle(bg, STAR_COLOR, (x, y), random.choice([1, 1, 2]))
    return bg

# ---------------------------- GAME OBJECTS ----------------------------
class Alien:
    def __init__(self, kind, x, y, points):
        self.kind, self.x, self.y, self.points = kind, x, y, points

class Bullet:
    def __init__(self, x, y, dy):
        self.x, self.y, self.dy = x, y, dy

class Explosion:
    def __init__(self, x, y):
        self.x, self.y, self.t = x, y, 0

class Powerup:
    def __init__(self, x, y, kind):
        self.x, self.y, self.kind, self.t = x, y, kind, 0

# ---------------------------- GAME ----------------------------
class Game:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 256)
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        self.stats = load_save()
        self.font_big = pygame.font.Font(None, 64)
        self.font_mid = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.bg = make_background(SCREEN_W, SCREEN_H)
        self.player_sprite = make_player_sprite()
        self.alien_sprites = make_alien_sprites()
        self.barrier_sprite = make_barrier_sprite()
        self.bullet_sprite = make_bullet_sprite()
        self.explosion_frames = make_explosion_frames()
        self.powerup_sprites = make_powerup_sprites()

        self.sfx = make_sfx()
        self.music = make_music()

        self.reset(level=1, first=True)
        self.state = "menu"
        self.menu_t = 0.0

    def reset(self, level, first=False):
        self.level, self.score, self.lives = level, 0, 3
        self.lives_max, self.rapid_timer, self.shoot_cooldown = 3, 0, 0
        self.frame_timer, self.alien_dir = 0, 1
        self.alien_speed = 60 + level * 18
        self.alien_fire_timer = 0
        self.alien_fire_interval = max(0.35, 1.4 - level * 0.09)
        self.player_x, self.player_y = SCREEN_W // 2 - 24, SCREEN_H - 70
        self.bullets, self.alien_bullets, self.explosions, self.powerups = [], [], [], []
        self.kills, self.play_time, self.alien_anim, self.hit_flash = 0, 0.0, 0, 0
        self.barriers = {}
        for gi, gx0 in enumerate([60, 250, 440, 630]):
            for row in range(3):
                for col in range(4):
                    self.barriers[(gx0 + col * 18, SCREEN_H - 130 + row * 18)] = True
        self.aliens = []
        cols, rows = min(5 + level // 3, 9), min(3 + level // 3, 7)
        start_x, start_y = SCREEN_W // 2 - (cols * 44) // 2, 60 + level * 6
        for r in range(rows):
            for c in range(cols):
                self.aliens.append(Alien(r % 3, start_x + c * 46, start_y + r * 42, (rows - r) * 10))
        if not first:
            self.state, self.trans_t = "level_transition", 0.0

    def play(self, name, loops=0):
        s = self.sfx.get(name)
        if s: s.play(loops=loops)

    def handle_events(self):
        """Handle discrete input events (one-time presses)."""
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if self.state == "menu" and e.key == pygame.K_RETURN:
                    self.reset(1, True); self.state = "playing"; self.music.play(loops=-1)
                elif self.state == "gameover" and e.key == pygame.K_RETURN:
                    self.reset(self.stats["best_level"], True); self.state = "playing"; self.music.play(loops=-1)
                elif self.state == "level_transition" and e.key == pygame.K_RETURN:
                    self.state = "playing"
                elif self.state == "playing" and (e.key == pygame.K_p or e.key == pygame.K_ESCAPE):
                    self.state = "paused"
                elif self.state == "paused" and (e.key == pygame.K_p or e.key == pygame.K_ESCAPE):
                    self.state = "playing"
                if e.key == pygame.K_SPACE and self.state == "playing":
                    self.shoot()
        return True

    def shoot(self):
        if self.shoot_cooldown > 0: return
        self.bullets.append(Bullet(self.player_x + 21, self.player_y - 10, -12))
        self.play("shoot")
        self.shoot_cooldown = 0.28 if self.rapid_timer > 0 else 0.55

    def update(self, dt):
        # --- CONTINUOUS INPUT HANDLING ---
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            move_speed = 350 * dt  # Pixels per second
            if keys[pygame.K_LEFT]:
                self.player_x = max(10, self.player_x - move_speed)
            if keys[pygame.K_RIGHT]:
                self.player_x = min(SCREEN_W - 58, self.player_x + move_speed)
        # ---------------------------------

        self.play_time += dt
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        if self.rapid_timer > 0: self.rapid_timer -= dt
        self.hit_flash = max(0, self.hit_flash - dt)

        # Player bullets
        for b in self.bullets[:]:
            b.y += b.dy
            if b.y < 0: self.bullets.remove(b); continue
            hit_barrier = False
            for (bx, by) in list(self.barriers.keys()):
                if abs(bx - b.x) < 16 and abs(by - b.y) < 16:
                    self.barriers.pop((bx, by), None); self.bullets.remove(b); hit_barrier = True; break
            if hit_barrier: continue
            for a in self.aliens[:]:
                if abs(a.x + 26 - b.x) < 26 and abs(a.y + 20 - b.y) < 22:
                    self.aliens.remove(a); self.score += a.points; self.kills += 1
                    self.explosions.append(Explosion(a.x + 26, a.y + 20)); self.play("explosion")
                    if random.random() < 0.08:
                        kind = random.choices(["life", "score", "rapid"], [0.3, 0.5, 0.2])[0]
                        self.powerups.append(Powerup(a.x + 26, a.y + 20, kind))
                    self.bullets.remove(b); break

        # Alien bullets
        if self.aliens:
            if self.alien_fire_timer <= 0:
                a = random.choice(self.aliens)
                self.alien_bullets.append(Bullet(a.x + 26, a.y + 34, 6)); self.play("invader")
                self.alien_fire_timer = self.alien_fire_interval
            else: self.alien_fire_timer -= dt

        for b in self.alien_bullets[:]:
            b.y += b.dy
            hit_barrier = False
            for (bx, by) in list(self.barriers.keys()):
                if abs(bx - b.x) < 16 and abs(by - b.y) < 16:
                    self.barriers.pop((bx, by), None); self.alien_bullets.remove(b); hit_barrier = True; break
            if hit_barrier: continue
            if self.hit_flash <= 0 and abs(self.player_x + 24 - b.x) < 26 and abs(self.player_y + 16 - b.y) < 22:
                self.hit_player(); self.alien_bullets.remove(b); break
            if b.y > SCREEN_H: self.alien_bullets.remove(b)

        # Alien group movement
        if self.aliens:
            self.frame_timer += dt
            if self.frame_timer > 0.5: self.frame_timer = 0; self.alien_anim = 1 - self.alien_anim
            min_x, max_x = min(a.x for a in self.aliens), max(a.x + 52 for a in self.aliens)
            if (self.alien_dir > 0 and max_x >= SCREEN_W - 6) or (self.alien_dir < 0 and min_x <= 6):
                self.alien_dir *= -1
                for a in self.aliens: a.y += 16
                self.alien_speed = min(self.alien_speed + 8, 320)
            for a in self.aliens: a.x += self.alien_dir * self.alien_speed * dt
            if any(a.y + 40 >= self.player_y for a in self.aliens): self.lives = 0; self.die()

        # Powerups
        for p in self.powerups[:]:
            p.y += 3
            if abs(self.player_x + 24 - p.x) < 34 and abs(self.player_y + 16 - p.y) < 34:
                if p.kind == "life": self.lives = min(self.lives + 1, 6); self.lives_max = max(self.lives_max, self.lives); self.score += 200
                elif p.kind == "score": self.score += 500
                elif p.kind == "rapid": self.rapid_timer = 12; self.score += 300
                self.play("bonus"); self.powerups.remove(p)
            elif p.y > SCREEN_H: self.powerups.remove(p)

        # Explosions
        for ex in self.explosions[:]:
            ex.t += dt
            if ex.t > 0.3: self.explosions.remove(ex)

        # Level Clear
        if not self.aliens:
            self.score += 1000 + self.level * 200
            self.play("level_clear")
            self.stats["best_level"] = max(self.stats["best_level"], self.level)
            if self.level < 12: self.reset(self.level + 1, False)
            else: self.game_over()

    def hit_player(self):
        self.lives -= 1; self.hit_flash = 0.6; self.play("player_hit")
        self.explosions.append(Explosion(self.player_x + 24, self.player_y + 16))
        if self.lives <= 0: self.die()

    def die(self):
        self.stats["games_played"] += 1; self.stats["total_kills"] += self.kills
        self.stats["total_time"] += self.play_time; self.stats["high_score"] = max(self.stats["high_score"], self.score)
        save_stats(self.stats); self.music.stop(); self.game_over()

    def game_over(self):
        self.state = "gameover"

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        if self.state == "menu": self.draw_menu()
        elif self.state == "playing": self.draw_world(); self.draw_hud()
        elif self.state == "paused": self.draw_world(); self.draw_hud(); self.draw_overlay("PAUSED", "Press P or ESC to resume")
        elif self.state == "level_transition": self.draw_world(); self.draw_hud(); self.draw_center(f"LEVEL {self.level}", "Get ready! Press Enter to start")
        elif self.state == "gameover": self.draw_world(); self.draw_overlay("GAME OVER", "Press Enter to play again")

    def draw_world(self):
        for (bx, by) in self.barriers.keys(): self.screen.blit(self.barrier_sprite, (bx, by))
        for a in self.aliens: self.screen.blit(self.alien_sprites[a.kind][self.alien_anim], (a.x, a.y))
        if self.lives > 0 and self.state != "gameover": self.screen.blit(self.player_sprite, (self.player_x, self.player_y))
        for b in self.bullets + self.alien_bullets: self.screen.blit(self.bullet_sprite, (b.x, b.y))
        for p in self.powerups: self.screen.blit(self.powerup_sprites[p.kind], (p.x - 17, p.y - 17))
        for ex in self.explosions:
            f = min(int(ex.t / 0.3 * 8), 7)
            self.screen.blit(self.explosion_frames[f], (ex.x - 24, ex.y - 24))

    def draw_hud(self):
        txt = f"SCORE {self.score:06d}   HIGH {self.stats['high_score']:06d}   LEVEL {self.level}"
        self.screen.blit(self.font_small.render(txt, True, TEXT_COLOR), (12, 10))
        for i in range(self.lives): self.screen.blit(self.player_sprite, (12 + i * 34, 44))
        if self.rapid_timer > 0: self.screen.blit(self.font_small.render("RAPID", True, ACCENT_COLOR), (400, 44))

    def draw_center(self, title, sub):
        t = self.font_big.render(title, True, ACCENT_COLOR)
        s = self.font_mid.render(sub, True, TEXT_COLOR)
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 190))
        self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, 260))

    def draw_overlay(self, title, sub):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 130)); self.screen.blit(ov, (0, 0))
        self.draw_center(title, sub)

    def draw_menu(self):
        t = self.font_big.render("SPACE INVADERS", True, ACCENT_COLOR)
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 120))
        lines = ["LEFT/RIGHT - move   SPACE - shoot   P/ESC - pause", "Hide behind barriers! Destroy all aliens.", f"High score: {self.stats['high_score']:06d}"]
        for i, l in enumerate(lines): self.screen.blit(self.font_small.render(l, True, TEXT_COLOR), (SCREEN_W // 2 - 190, 220 + i * 30))
        if (int(self.menu_t * 2) % 2 == 0):
            go = self.font_mid.render("PRESS ENTER TO START", True, (255, 230, 120))
            self.screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, 400))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.menu_t += dt
            running = self.handle_events()
            if self.state == "playing": self.update(dt)
            elif self.state == "level_transition": self.trans_t += dt
            self.draw()
            pygame.display.flip()
        pygame.quit()

def main():
    pygame.mixer.init()
    Game().run()

if __name__ == "__main__":
    main()
