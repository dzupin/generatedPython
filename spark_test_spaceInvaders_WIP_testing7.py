# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.6-27B-heretic-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

import pygame
import random
import math
import json
import os
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Invaders")
clock = pygame.time.Clock()
FONT = pygame.font.Font(pygame.font.get_default_font(), 22)
FONT_LARGE = pygame.font.Font(pygame.font.get_default_font(), 32)

DATA_FILE = "game_data.json"

BLACK = (0, 0, 0)
DARK_BG = (5, 2, 15)
WHITE = (255, 255, 255)
CYAN = (0, 240, 255)
NEON_GREEN = (0, 255, 100)
NEON_PINK = (255, 0, 180)
YELLOW = (255, 240, 0)
ORANGE = (255, 140, 0)
RED = (255, 40, 40)
PURPLE = (180, 60, 255)

def make_sound(freq, duration, fade_out=True):
    sample_rate = 22050
    samples = int(sample_rate * duration)
    data = bytearray()
    for i in range(samples):
        t = i / sample_rate
        if fade_out and i > samples * 0.6:
            gain = (samples - i) / (samples * 0.4)
        else:
            gain = 1.0
        val = math.sin(2 * math.pi * freq * t)
        v = int(val * gain * 15000)
        v = max(-32768, min(32767, v))
        data += v.to_bytes(2, 'little', signed=True)
    return pygame.mixer.Sound(buffer=data)

try:
    pygame.mixer.init(22050, -16, 1, 512)
    SND_SHOOT = make_sound(880, 0.06)
    SND_HIT = make_sound(320, 0.1)
    SND_EXPLODE = make_sound(120, 0.2)
    SND_POWERUP = make_sound(600, 0.18)
    SND_LEVELUP = make_sound(440, 0.3)
    SND_LOSE = make_sound(150, 0.4)
except Exception:
    SND_SHOOT = SND_HIT = SND_EXPLODE = SND_POWERUP = SND_LEVELUP = SND_LOSE = None

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"high_score": 0, "best_combo": 0, "last_level": 1}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

class StarLayer:
    def __init__(self, count, speed_base, size_range, alpha):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                "x": random.random() * WIDTH,
                "y": random.random() * HEIGHT,
                "size": random.uniform(*size_range),
                "speed": speed_base + random.random() * 0.6,
                "phase": random.uniform(0, 6.28),
                "alpha": alpha
            })

    def update(self, boost=0.0):
        for s in self.stars:
            s["y"] += s["speed"] + boost
            if s["y"] > HEIGHT:
                s["y"] = 0
                s["x"] = random.random() * WIDTH

    def draw(self, surface, t):
        for s in self.stars:
            bright = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 0.002 + s["phase"]))
            a = int(s["alpha"] * bright * 255)
            c = min(255, int(220 + bright * 35))
            color = (c, c, min(255, c + 20), a)
            pygame.draw.circle(surface, color, (int(s["x"]), int(s["y"])), max(1, int(s["size"])))

class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=None, trail=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size or max(1, int(random.uniform(1.2, 2.8)))
        self.trail = trail

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        if self.trail:
            self.vy += 0.02 * dt * 60
        self.life -= dt
        if self.life < 0:
            self.life = 0

    def draw(self, surface):
        if self.life <= 0:
            return
        t = self.life / self.max_life
        if self.trail:
            alpha = int(180 * t)
            pygame.draw.circle(surface, (*self.color[:3], alpha), (int(self.x), int(self.y)), int(self.size * t))
        else:
            alpha = int(255 * t)
            r, g, b = self.color
            img = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(img, (r, g, b, alpha), (self.size, self.size), self.size)
            surface.blit(img, (self.x - self.size, self.y - self.size))

class FloatingText:
    def __init__(self, x, y, text, color, size=18):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(pygame.font.get_default_font(), size)
        self.life = 1.2
        self.max_life = self.life

    def update(self, dt):
        self.y -= 40 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        t = self.life / self.max_life
        alpha = int(255 * min(1.0, t * 2))
        img = self.font.render(self.text, True, self.color)
        img.set_alpha(alpha)
        rect = img.get_rect(center=(self.x, self.y))
        surface.blit(img, rect)

class PowerUp:
    TYPES = {
        "R": {"name": "Rapid", "color": CYAN, "duration": 9},
        "S": {"name": "Spread", "color": NEON_GREEN, "duration": 8},
        "B": {"name": "Shield", "color": PURPLE, "duration": 0},
        "M": {"name": "Multi+", "color": YELLOW, "duration": 10},
    }

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.key = random.choice(list(self.TYPES.keys()))
        info = self.TYPES[self.key]
        self.color = info["color"]
        self.vy = 1.6
        self.age = 0
        self.trail_timer = 0

    def update(self, dt, particles, game):
        self.age += dt
        self.rect.y += self.vy * dt * 60
        self.trail_timer += dt
        if self.trail_timer > 0.02:
            self.trail_timer = 0
            particles.append(Particle(
                self.rect.centerx + random.uniform(-4, 4),
                self.rect.bottom,
                random.uniform(-0.4, 0.4), random.uniform(0.3, 0.8),
                self.color, 0.35, size=2, trail=True
            ))
        if self.rect.top > HEIGHT:
            return False
        if self.rect.bottom > HEIGHT - 20:
            self.vy *= -0.4
        return True

    def draw(self, surface):
        pulse = 0.9 + 0.1 * math.sin(self.age * 6)
        r = int(12 * pulse)
        pygame.draw.circle(surface, (20, 20, 40), self.rect.center, r)
        pygame.draw.circle(surface, self.color, self.rect.center, r - 2)
        pygame.draw.circle(surface, WHITE, self.rect.center, r - 4, 1)
        t = pygame.font.Font(pygame.font.get_default_font(), 16).render(self.key, True, WHITE)
        surface.blit(t, t.get_rect(center=self.rect.center))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 24, HEIGHT - 50, 48, 28)
        self.speed = 8
        self.cooldown = 0
        self.lives = 3
        self.shield = 0
        self.powerups = {"R": 0, "S": 0, "M": 0}
        self.invuln_timer = 0

    def update(self, dt, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.shield > 0:
            self.shield -= dt
        for k in self.powerups:
            if self.powerups[k] > 0:
                self.powerups[k] -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def draw(self, surface, t):
        if self.invuln_timer > 0 and int(t * 10) % 2 == 0:
            return
        cx = self.rect.centerx
        top = self.rect.top
        bot = self.rect.bottom

        glow = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        pygame.draw.polygon(glow, (0, 180, 255, 30), [
            (cx + 5, top - 3),
            (self.rect.left - 5, bot + 3),
            (self.rect.right + 5, bot + 3)
        ])
        surface.blit(glow, (self.rect.left - 5, self.rect.top - 5))

        pts = [(cx, top), (self.rect.left, bot), (self.rect.right, bot)]
        pygame.draw.polygon(surface, CYAN, pts)
        pygame.draw.polygon(surface, NEON_GREEN, [
            (cx, top + 5),
            (self.rect.left + 7, bot - 3),
            (self.rect.right - 7, bot - 3)
        ])

        flicker = random.randint(0, 14)
        ey = bot + 7 + random.randint(0, 4)
        pygame.draw.polygon(surface, (0, 160 + flicker, 255), [
            (cx - 5, bot), (cx + 5, bot), (cx, ey)
        ])

        if self.shield > 0:
            pulse = 0.6 + 0.4 * math.sin(t * 0.006)
            r = 28
            alpha = int(80 * pulse)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (PURPLE[0], PURPLE[1], PURPLE[2], alpha), (r, r), r)
            pygame.draw.circle(s, (180, 180, 255, int(160 * pulse)), (r, r), r - 3)
            rect = s.get_rect(center=self.rect.center)
            surface.blit(s, rect)

class Enemy:
    def __init__(self, x, y, row, level):
        self.rect = pygame.Rect(x, y, 32, 26)
        self.row = row
        self.frame = 0
        self.base_points = 10 + row * 5
        self.level = level

    def animate(self):
        self.frame = 1 - self.frame

    def draw(self, surface, t):
        cx, cy = self.rect.centerx, self.rect.centery
        pulse = 0.85 + 0.15 * math.sin(t * 0.004 + self.row)
        c1 = (int(255 * pulse), int(0 + 30 * pulse), int(180 * pulse))
        c2 = YELLOW
        pygame.draw.ellipse(surface, c1, self.rect)
        pygame.draw.circle(surface, c2, (int(cx - 7), int(cy - 4)), 3)
        pygame.draw.circle(surface, c2, (int(cx + 7), int(cy - 4)), 3)
        if self.frame:
            pygame.draw.rect(surface, c1, (cx - 13, cy + 7, 5, 7))
            pygame.draw.rect(surface, c1, (cx + 8, cy + 7, 5, 7))
        else:
            pygame.draw.rect(surface, c1, (cx - 11, cy + 9, 5, 5))
            pygame.draw.rect(surface, c1, (cx + 6, cy + 9, 5, 5))

class Bullet:
    def __init__(self, x, y, dy, is_player=True, spread=False):
        self.x = x
        self.y = y
        self.dy = dy
        self.is_player = is_player
        self.w, self.h = 3, 14
        self.alive = True
        self.trail_timer = 0

    def update(self, dt, particles):
        self.y += self.dy * dt * 60
        self.trail_timer += dt
        if self.trail_timer > 0.02:
            self.trail_timer = 0
            color = CYAN if self.is_player else RED
            particles.append(Particle(
                self.x + random.uniform(-1, 1),
                self.y + (self.h if self.is_player else -self.h),
                random.uniform(-0.3, 0.3), random.uniform(0.1, 0.5),
                color, 0.2, size=2, trail=True
            ))
        if self.y < -15 or self.y > HEIGHT + 15:
            self.alive = False

    def draw(self, surface):
        color = CYAN if self.is_player else RED
        pygame.draw.rect(surface, color, (self.x - self.w, self.y - self.h // 2, self.w * 2, self.h))
        pygame.draw.rect(surface, WHITE, (self.x - 1, self.y - self.h // 2 + 2, 2, self.h - 4))

class Bunker:
    def __init__(self, x, y, block_size=4, grid_w=15, grid_h=10):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.blocks = []
        self._build_shape(grid_w, grid_h)
        self.rect = pygame.Rect(x, y, grid_w * block_size, grid_h * block_size)

    def _build_shape(self, w, h):
        for gy in range(h):
            for gx in range(w):
                cx = gx - (w - 1) / 2
                if gy < 2 and abs(cx) > 4.5:
                    continue
                if gy >= h - 3 and abs(cx) < 3:
                    continue
                self.blocks.append(pygame.Rect(
                    self.x + gx * self.block_size,
                    self.y + gy * self.block_size,
                    self.block_size, self.block_size
                ))

    def draw(self, surface, t):
        pulse = 0.82 + 0.18 * math.sin(t * 0.003)
        base = (0, 170, 90)
        for r in self.blocks:
            c = (int(base[0] * pulse), int(base[1] * pulse), int(base[2] * pulse))
            pygame.draw.rect(surface, c, r)
            pygame.draw.rect(surface, (0, 255, 140), (r.x + 1, r.y + 1, r.w - 2, r.h - 2), 1)

    def erode_at(self, px, py, radius_blocks, particles=None):
        to_remove = []
        for r in self.blocks:
            dx = (px - r.centerx) / self.block_size
            dy = (py - r.centery) / self.block_size
            if dx * dx + dy * dy <= radius_blocks * radius_blocks:
                to_remove.append(r)
                if particles:
                    particles.append(Particle(
                        r.centerx, r.centery,
                        random.uniform(-1.5, 1.5), random.uniform(-1.8, -0.4),
                        (0, 255, 110), 0.35, size=2, trail=True
                    ))
        for r in to_remove:
            if r in self.blocks:
                self.blocks.remove(r)

    def erode_rect(self, rect, particles=None):
        to_remove = []
        for r in self.blocks:
            if r.colliderect(rect):
                to_remove.append(r)
                if particles:
                    particles.append(Particle(
                        r.centerx, r.centery,
                        random.uniform(-1, 1), random.uniform(-1.5, -0.3),
                        (0, 255, 110), 0.3, size=2, trail=True
                    ))
        for r in to_remove:
            if r in self.blocks:
                self.blocks.remove(r)

class Game:
    def __init__(self):
        self.data = load_data()
        self.state = "MENU"
        self.score = 0
        self.level = self.data.get("last_level", 1)
        self.stars = [
            StarLayer(140, 0.25, (0.5, 1.6), 0.9),
            StarLayer(60, 0.6, (1.0, 2.2), 0.6),
        ]
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.particles = []
        self.floating_texts = []
        self.powerups = []
        self.bunkers = []
        self.enemy_dir = 1
        self.step_timer = 0
        self.base_step_interval = 40
        self.drop_dist = 14
        self.shoot_chance = 0.004
        self.combo = 0
        self.combo_timer = 0
        self.multiplier = 1
        self.last_kill_time = 0
        self.t = pygame.time.get_ticks()
        self.star_boost = 0.0
        self.spawn_wave()
        self.init_bunkers()
        self.menu_blink = 0
        self._resume_callback = None

    def spawn_wave(self):
        self.enemies.clear()
        rows, cols = 5, 9
        gap = 10
        total_w = cols * 32 + (cols - 1) * gap
        start_x = (WIDTH - total_w) // 2
        for r in range(rows):
            for c in range(cols):
                x = start_x + c * (32 + gap)
                y = 90 + r * (28 + gap)
                self.enemies.append(Enemy(x, y, r, self.level))

    def init_bunkers(self):
        self.bunkers = []
        bunker_w = 60
        gap = (WIDTH - 4 * bunker_w) // 5
        for i in range(4):
            bx = gap + i * (bunker_w + gap)
            by = HEIGHT - 130
            self.bunkers.append(Bunker(bx, by, block_size=4, grid_w=15, grid_h=10))

    def play(self, snd):
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def explode(self, x, y, base_color, count=22):
        for _ in range(count):
            a = random.uniform(0, 6.28)
            speed = random.uniform(1.6, 4.5)
            vx = math.cos(a) * speed
            vy = math.sin(a) * speed - 1.5
            c = (
                min(255, base_color[0] + random.randint(0, 60)),
                min(255, base_color[1] + random.randint(0, 40)),
                min(255, base_color[2] + random.randint(0, 30))
            )
            self.particles.append(Particle(x, y, vx, vy, c, random.uniform(0.4, 0.9), size=random.uniform(1.5, 3.0)))

    def add_floating_text(self, x, y, text, color=WHITE, size=18):
        self.floating_texts.append(FloatingText(x, y, text, color, size=size))

    def update(self, dt, keys):
        self.t = pygame.time.get_ticks()
        self.menu_blink += dt

        for sl in self.stars:
            sl.update(boost=self.star_boost)
        self.star_boost = max(0.0, self.star_boost - dt * 2.0)

        if self.state == "MENU":
            if keys[pygame.K_RETURN]:
                self.state = "PLAYING"
                self.player = Player()
                self.score = 0
                self.combo = 0
                self.multiplier = 1
                self.combo_timer = 0
                self.level = max(1, self.data.get("last_level", 1))
                self.spawn_wave()
                self.init_bunkers()
            return

        if self.state == "GAME_OVER":
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.life > 0]
            for ft in self.floating_texts:
                ft.update(dt)
            self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]
            if keys[pygame.K_r]:
                self.__init__()
            return

        if self.state == "LEVEL_TRANSITION":
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.life > 0]
            for ft in self.floating_texts:
                ft.update(dt)
            self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]
            return

        self.player.update(dt, keys)

        self.combo_timer += dt
        if self.combo_timer > 1.4 and self.combo > 0:
            self.combo = 0
            self.combo_timer = 0
            self.multiplier = max(1, (self.player.powerups.get("M", 0) > 0) + 1)

        # Player bullets
        surviving_player_bullets = []
        for b in self.bullets:
            b.update(dt, self.particles)
            if not b.alive:
                continue
            hit = False
            # Check bunkers
            if not hit:
                for bunk in self.bunkers:
                    if bunk.rect.collidepoint(b.x, b.y):
                        bunk.erode_at(b.x, b.y, 2.0, self.particles)
                        hit = True
                        break
            # Check enemies
            if not hit:
                for e in self.enemies:
                    if e.rect.collidepoint(b.x, b.y):
                        pts = e.base_points * self.multiplier
                        self.score += pts
                        self.combo += 1
                        self.combo_timer = 0
                        self.last_kill_time = self.t
                        self.multiplier = min(6, 1 + (self.combo // 5) + (1 if self.player.powerups["M"] > 0 else 0))
                        if self.combo > self.data.get("best_combo", 0):
                            self.data["best_combo"] = self.combo
                        label = f"+{pts}"
                        if self.multiplier > 1:
                            label += f" x{self.multiplier}"
                        self.add_floating_text(e.rect.centerx, e.rect.top - 8, label, YELLOW, 18)
                        self.explode(e.rect.centerx, e.rect.centery, NEON_PINK, 24)
                        self.play(SND_EXPLODE)
                        if random.random() < 0.06:
                            self.powerups.append(PowerUp(e.rect.centerx, e.rect.centery))
                        self.enemies.remove(e)
                        hit = True
                        break
            if not hit:
                surviving_player_bullets.append(b)
        self.bullets = surviving_player_bullets

        # Enemy bullets
        surviving_enemy_bullets = []
        for b in self.enemy_bullets:
            b.update(dt, self.particles)
            if not b.alive:
                continue
            hit = False
            # Check bunkers
            if not hit:
                for bunk in self.bunkers:
                    if bunk.rect.collidepoint(b.x, b.y):
                        bunk.erode_at(b.x, b.y, 2.2, self.particles)
                        hit = True
                        break
            # Check player
            if not hit and self.player.invuln_timer <= 0:
                if self.player.rect.collidepoint(b.x, b.y):
                    if self.player.shield > 0:
                        self.player.shield = 0
                        self.explode(self.player.rect.centerx, self.player.rect.centery, PURPLE, 18)
                        self.add_floating_text(self.player.rect.centerx, self.player.rect.top - 10, "SHIELD", PURPLE, 18)
                    else:
                        self.player.lives -= 1
                        self.explode(self.player.rect.centerx, self.player.rect.centery, CYAN, 28)
                        self.add_floating_text(self.player.rect.centerx, self.player.rect.top - 10, "-1", RED, 20)
                    self.player.invuln_timer = 1.2
                    self.play(SND_LOSE)
                    if self.player.lives <= 0:
                        self.game_over()
                    hit = True
            if not hit:
                surviving_enemy_bullets.append(b)
        self.enemy_bullets = surviving_enemy_bullets

        # Particles / texts
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

        # Powerups
        new_powerups = []
        for pu in self.powerups:
            if not pu.update(dt, self.particles, self):
                continue
            new_powerups.append(pu)
            if pu.rect.colliderect(self.player.rect):
                self.apply_powerup(pu)
                self.play(SND_POWERUP)
                self.add_floating_text(pu.rect.centerx, pu.rect.top - 10, "+" + PowerUp.TYPES[pu.key]["name"], PowerUp.TYPES[pu.key]["color"], 20)
        self.powerups = new_powerups

        # Shooting
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.player.cooldown <= 0:
            base_cd = 9 if self.player.powerups["R"] > 0 else 13
            self.player.cooldown = base_cd
            cx = self.player.rect.centerx
            if self.player.powerups["S"] > 0:
                self.bullets.append(Bullet(cx, self.player.rect.top - 4, -8.0, is_player=True))
                self.bullets.append(Bullet(cx - 10, self.player.rect.top - 2, -7.5, is_player=True))
                self.bullets.append(Bullet(cx + 10, self.player.rect.top - 2, -7.5, is_player=True))
            else:
                self.bullets.append(Bullet(cx, self.player.rect.top - 4, -8.0, is_player=True))
            self.play(SND_SHOOT)

        # Enemy movement
        self.step_timer += dt * 1000
        current_interval = max(20, self.base_step_interval - (self.level - 1) * 2.5)
        if self.step_timer >= current_interval:
            self.step_timer = 0
            hit_edge = False
            for e in self.enemies:
                if e.rect.right >= WIDTH - 10 and self.enemy_dir > 0:
                    hit_edge = True
                if e.rect.left <= 10 and self.enemy_dir < 0:
                    hit_edge = True
            if hit_edge:
                self.enemy_dir *= -1
                for e in self.enemies:
                    e.rect.y += self.drop_dist
                    e.animate()
            else:
                for e in self.enemies:
                    e.rect.x += 5 * self.enemy_dir
                    e.animate()

            # Erosion from enemies touching bunkers
            for bunk in self.bunkers:
                for e in self.enemies:
                    bunk.erode_rect(e.rect, self.particles)

            if not self.enemies:
                self.level_up()

        # Enemy shooting
        if self.enemies and random.random() < min(0.014, self.shoot_chance + (self.level - 1) * 0.0004):
            src = random.choice(self.enemies)
            self.enemy_bullets.append(Bullet(src.rect.centerx, src.rect.bottom + 3, 4.6, is_player=False))
            self.play(SND_HIT)

        # Enemies reach bottom or collide with player
        for e in self.enemies:
            if e.rect.colliderect(self.player.rect) or e.rect.bottom >= HEIGHT - 40:
                self.game_over()
                break

    def apply_powerup(self, pu):
        t = PowerUp.TYPES[pu.key]
        if pu.key == "R":
            self.player.powerups["R"] = t["duration"]
        elif pu.key == "S":
            self.player.powerups["S"] = t["duration"]
        elif pu.key == "B":
            self.player.shield = 3.5
        elif pu.key == "M":
            self.player.powerups["M"] = t["duration"]
            self.multiplier = min(6, self.multiplier + 2)

    def level_up(self):
        self.state = "LEVEL_TRANSITION"
        self.star_boost = 3.0
        self.level += 1
        self.base_step_interval = max(22, 40 - (self.level - 1) * 2)
        self.shoot_chance += 0.0005
        self.add_floating_text(WIDTH // 2, HEIGHT // 2 - 40, f"LEVEL {self.level}", NEON_GREEN, 28)
        self.play(SND_LEVELUP)
        self.data["last_level"] = self.level
        save_data(self.data)

        def resume():
            self.spawn_wave()
            self.init_bunkers()
            self.state = "PLAYING"

        self._resume_callback = resume
        pygame.time.set_timer(pygame.USEREVENT, 1200, True)

    def game_over(self):
        self.state = "GAME_OVER"
        self.explode(self.player.rect.centerx, self.player.rect.centery, RED, 45)
        if self.score > self.data.get("high_score", 0):
            self.data["high_score"] = self.score
        save_data(self.data)
        self.add_floating_text(WIDTH // 2, HEIGHT // 2 - 50, "GAME OVER", RED, 28)
        self.add_floating_text(WIDTH // 2, HEIGHT // 2, f"SCORE: {self.score}", WHITE, 24)
        self.add_floating_text(WIDTH // 2, HEIGHT // 2 + 30, "Press R", WHITE, 18)
        self.play(SND_LOSE)

    def draw(self, surface):
        for y in range(HEIGHT):
            r = int(4 + 14 * (y / HEIGHT))
            g = 1
            b = int(20 + 25 * (y / HEIGHT))
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        for sl in self.stars:
            sl.draw(surface, self.t)

        # Bunkers
        for bunk in self.bunkers:
            bunk.draw(surface, self.t)

        # Enemies
        for e in self.enemies:
            e.draw(surface, self.t)

        # Bullets
        for b in self.bullets + self.enemy_bullets:
            b.draw(surface)

        # Powerups
        for pu in self.powerups:
            pu.draw(surface)

        # Particles
        for p in self.particles:
            p.draw(surface)

        # Floating texts
        for ft in self.floating_texts:
            ft.draw(surface)

        # Player
        if self.state in ("PLAYING", "LEVEL_TRANSITION"):
            self.player.draw(surface, self.t)

        self.draw_hud(surface)

        if self.state == "MENU":
            self.draw_menu(surface)
        elif self.state == "GAME_OVER":
            self.draw_game_over(surface)

    def draw_hud(self, surface):
        sc = FONT.render(f"SCORE: {self.score}", True, WHITE)
        hs = FONT.render(f"HIGH: {self.data.get('high_score', 0)}", True, (180, 180, 190))
        lv = FONT.render(f"LVL: {self.level}", True, NEON_GREEN)
        li = FONT.render(f"LIVES: {self.player.lives}", True, CYAN)

        combo_text = ""
        if self.combo > 0:
            combo_text = f"COMBO: {self.combo} x{self.multiplier}"
            combo = FONT.render(combo_text, True, YELLOW)
        else:
            combo = None

        surface.blit(sc, (14, 10))
        surface.blit(hs, (WIDTH // 2 - hs.get_width() // 2, 10))
        surface.blit(lv, (WIDTH // 2 + 80, 10))
        surface.blit(li, (WIDTH - li.get_width() - 14, 10))
        if combo:
            surface.blit(combo, (14, 34))

        px = WIDTH - 14
        for key in ("R", "S", "B", "M"):
            val = self.player.powerups.get(key, 0) if key != "B" else self.player.shield
            if val > 0:
                t = FONT.render(f"{key}", True, PowerUp.TYPES[key]["color"])
                px -= t.get_width() + 4
                surface.blit(t, (px, 10))

    def draw_menu(self, surface):
        bar = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surface.blit(bar, (0, HEIGHT - 140))

        title = FONT_LARGE.render("NEON INVADERS", True, CYAN)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT - 110))

        blink = 0.8 + 0.2 * math.sin(self.menu_blink * 4)
        if blink > 0.5:
            prompt = FONT.render("Press ENTER to Start", True, WHITE)
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 70))

        hs = FONT.render(f"High Score: {self.data.get('high_score', 0)}", True, YELLOW)
        surface.blit(hs, (WIDTH // 2 - hs.get_width() // 2, HEIGHT - 40))

    def draw_game_over(self, surface):
        bar = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 160))
        surface.blit(bar, (0, HEIGHT - 100))

        blink = 0.8 + 0.2 * math.sin(self.menu_blink * 4)
        if blink > 0.5:
            prompt = FONT.render("Press R to Restart", True, WHITE)
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))

def main():
    game = Game()
    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                if game._resume_callback is not None:
                    game._resume_callback()
                    game._resume_callback = None

        keys = pygame.key.get_pressed()
        game.update(dt, keys)
        game.draw(screen)
        pygame.display.flip()

    save_data(game.data)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
