# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type mtp --spec-draft-n-max 3 --model /AI/models/Qwen3.6-27B-uncensored-heretic-v2-Native-MTP-Preserved-NVFP4-MLP-Only-Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import random
import math
import json
import os
import array
from pygame.locals import *
from enum import Enum
from dataclasses import dataclass

# ================= CONFIGURATION =================
WIDTH, HEIGHT = 800, 600
FPS = 60
STATS_FILE = "space_invaders_stats.json"

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'CYAN': (0, 255, 255),
    'GREEN': (0, 255, 100),
    'RED': (255, 50, 50),
    'YELLOW': (255, 255, 0),
    'PINK': (255, 100, 200),
    'ORANGE': (255, 165, 0),
    'DARK': (20, 20, 30),
    'SHIELD': (100, 200, 255),
    'MULTI': (255, 215, 0)
}


# ================= SOUND GENERATOR =================
def create_sound(freq=440, duration=0.1, volume=0.5, wave='sine'):
    """Generate a sound programmatically using waveforms."""
    sample_rate = 44100
    length = int(sample_rate * duration)
    arr = array.array('h')
    for i in range(length):
        t = i / sample_rate
        if wave == 'sine':
            val = int(32767 * volume * math.sin(2 * math.pi * freq * t))
        elif wave == 'square':
            val = int(32767 * volume * (1 if math.sin(2 * math.pi * freq * t) > 0 else -1))
        elif wave == 'noise':
            val = int(32767 * volume * (random.random() * 2 - 1))
        arr.append(val)
    return pygame.mixer.Sound(array=arr)


# ================= GRAPHIC GENERATOR =================
def create_surface(width, height, draw_func):
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    draw_func(s, width, height)
    return s


def draw_player(s, w, h):
    pygame.draw.polygon(s, COLORS['CYAN'], [(w // 2, 0), (w, h), (0, h)])
    pygame.draw.rect(s, COLORS['WHITE'], (w // 2 - 4, 5, 8, 10))
    pygame.draw.circle(s, COLORS['YELLOW'], (w // 2, 12), 3)


def draw_invader(s, w, h, row_type):
    if row_type == 0:
        pygame.draw.rect(s, COLORS['PINK'], (4, 4, 16, 8))
        pygame.draw.rect(s, COLORS['PINK'], (0, 8, 6, 4))
        pygame.draw.rect(s, COLORS['PINK'], (18, 8, 6, 4))
        pygame.draw.rect(s, COLORS['PINK'], (6, 12, 4, 4))
        pygame.draw.rect(s, COLORS['PINK'], (14, 12, 4, 4))
    elif row_type == 1:
        pygame.draw.rect(s, COLORS['GREEN'], (2, 2, 20, 10))
        pygame.draw.rect(s, COLORS['GREEN'], (0, 6, 4, 4))
        pygame.draw.rect(s, COLORS['GREEN'], (20, 6, 4, 4))
        pygame.draw.rect(s, COLORS['GREEN'], (4, 10, 16, 4))
        pygame.draw.rect(s, COLORS['GREEN'], (0, 12, 6, 4))
        pygame.draw.rect(s, COLORS['GREEN'], (18, 12, 6, 4))
    else:
        pygame.draw.rect(s, COLORS['YELLOW'], (0, 2, 24, 8))
        pygame.draw.rect(s, COLORS['YELLOW'], (2, 6, 20, 6))
        pygame.draw.rect(s, COLORS['YELLOW'], (0, 10, 8, 4))
        pygame.draw.rect(s, COLORS['YELLOW'], (16, 10, 8, 4))
        pygame.draw.rect(s, COLORS['YELLOW'], (4, 14, 6, 2))
        pygame.draw.rect(s, COLORS['YELLOW'], (14, 14, 6, 2))
    pygame.draw.rect(s, COLORS['BLACK'], (8, 6, 4, 4))
    pygame.draw.rect(s, COLORS['BLACK'], (12, 6, 4, 4))


def draw_mystery(s, w, h):
    pygame.draw.ellipse(s, COLORS['ORANGE'], (0, 2, w, h - 4))
    pygame.draw.circle(s, COLORS['RED'], (w // 4, h // 2), 4)
    pygame.draw.circle(s, COLORS['RED'], (3 * w // 4, h // 2), 4)
    pygame.draw.circle(s, COLORS['WHITE'], (w // 2, h // 2), 3)


def draw_powerup(s, w, h, ptype):
    color = {'LIFE': COLORS['RED'], 'SHIELD': COLORS['SHIELD'],
             'RAPID': COLORS['CYAN'], 'MULTI': COLORS['MULTI']}[ptype]
    pygame.draw.circle(s, color, (w // 2, h // 2), w // 2 - 2)
    pygame.draw.circle(s, COLORS['WHITE'], (w // 2, h // 2), w // 4)


SURFACES = {
    'player': create_surface(30, 20, draw_player),
    'invader0': create_surface(24, 16, lambda s, w, h: draw_invader(s, w, h, 0)),
    'invader1': create_surface(24, 16, lambda s, w, h: draw_invader(s, w, h, 1)),
    'invader2': create_surface(24, 16, lambda s, w, h: draw_invader(s, w, h, 2)),
    'mystery': create_surface(30, 18, draw_mystery),
    'powerup': create_surface(16, 16, lambda s, w, h: draw_powerup(s, w, h, 'LIFE'))
}


# ================= STATISTICS HANDLER =================
class StatsManager:
    def __init__(self):
        self.data = self.load()

    def load(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {"high_score": 0, "games_played": 0, "best_level": 1, "total_time": 0}

    def save(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def record(self, score, level, time):
        self.data["games_played"] += 1
        self.data["total_time"] += time
        if score > self.data["high_score"]:
            self.data["high_score"] = score
        if level > self.data["best_level"]:
            self.data["best_level"] = level
        self.save()


# ================= GAME ENTITIES =================
class Particle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, random.randint(2, 6), random.randint(2, 6))
        self.vel = [random.uniform(-3, 3), random.uniform(-3, 3)]
        self.life = random.uniform(0.5, 1.5)
        self.color = color
        self.age = 0

    def update(self, dt):
        self.age += dt
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        return self.age < self.life

    def draw(self, screen):
        alpha = int(255 * (1 - self.age / self.life))
        s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        screen.blit(s, self.rect)


class Bullet:
    def __init__(self, x, y, dy, is_player=True):
        self.rect = pygame.Rect(x, y, 4, 12)
        self.dy = dy
        self.is_player = is_player
        self.color = COLORS['WHITE'] if is_player else COLORS['RED']

    def update(self):
        self.rect.y += self.dy
        return self.rect.bottom < 0 or self.rect.top > HEIGHT


class Barrier:
    def __init__(self, x, y):
        self.blocks = []
        for row in range(15):
            for col in range(25):
                if row > 8 and col > 7 and col < 17: continue
                self.blocks.append(pygame.Rect(x + col * 4, y + row * 4, 4, 4))

    def draw(self, screen):
        for b in self.blocks:
            pygame.draw.rect(screen, COLORS['GREEN'], b)

    def get_hit(self, rect):
        hits = []
        for b in self.blocks:
            if b.colliderect(rect):
                hits.append(b)
                # Degrade surrounding blocks
                for nb in self.blocks:
                    if nb != b and abs(nb.x - b.x) <= 4 and abs(nb.y - b.y) <= 4:
                        hits.append(nb)
                break
        self.blocks = [b for b in self.blocks if b not in hits]
        return len(hits) > 0


class Invader:
    def __init__(self, x, y, row_type):
        self.rect = pygame.Rect(x, y, 24, 16)
        self.surface = SURFACES[f'invader{row_type}']
        self.row_type = row_type
        self.points = [30, 20, 10][row_type]

    def draw(self, screen):
        screen.blit(self.surface, self.rect)


class MysteryShip:
    def __init__(self):
        self.rect = pygame.Rect(-30, 10, 30, 18)
        self.surface = SURFACES['mystery']
        self.speed = 4
        self.active = True

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.active = False

    def draw(self, screen):
        screen.blit(self.surface, self.rect)


class PowerUp:
    TYPES = ['LIFE', 'SHIELD', 'RAPID', 'MULTI']

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 8, y, 16, 16)
        self.p_type = random.choice(self.TYPES)
        self.surface = SURFACES['powerup']
        self.dy = 2

    def update(self):
        self.rect.y += self.dy
        return self.rect.top > HEIGHT

    def draw(self, screen):
        screen.blit(self.surface, self.rect)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, HEIGHT - 40, 30, 20)
        self.surface = SURFACES['player']
        self.speed = 6
        self.shoot_cd = 0
        self.base_cd = 0.3
        self.active_powerups = {}
        self.lives = 3
        self.invincible = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] or keys[K_a]: self.rect.x -= self.speed
        if keys[K_RIGHT] or keys[K_d]: self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self.shoot_cd -= dt
        if self.invincible > 0: self.invincible -= dt

        # Powerup timers
        now = pygame.time.get_ticks()
        for p in self.active_powerups:
            if now > self.active_powerups[p]:
                del self.active_powerups[p]

        rapid = 'RAPID' in self.active_powerups
        self.cd = self.base_cd / (2 if rapid else 1)

    def draw(self, screen):
        if self.invincible > 0 and int(pygame.time.get_ticks() / 100) % 2: return
        screen.blit(self.surface, self.rect)
        # Draw active powerups indicators
        y = HEIGHT - 20
        for p in self.active_powerups:
            if p == 'SHIELD':
                pygame.draw.circle(screen, COLORS['SHIELD'], (self.rect.centerx, self.rect.centery), 25, 2)
            elif p == 'MULTI':
                pygame.draw.rect(screen, COLORS['MULTI'], (10, y, 100, 15))
                pygame.draw.rect(screen, COLORS['BLACK'], (10, y, min(100, (
                            pygame.time.get_ticks() - self.active_powerups['MULTI']) / 1000 * 100), 15))
                y += 20


class StarField:
    def __init__(self):
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 2)) for _ in range(150)]

    def update(self):
        for s in self.stars:
            s[1] += s[2]
            if s[1] > HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, WIDTH)

    def draw(self, screen):
        for x, y, size in self.stars:
            alpha = int(100 + 155 * (size / 2))
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((255, 255, 255, alpha))
            screen.blit(s, (x, y))


# ================= MAIN GAME =================
class SpaceInvaders:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders - Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)

        # Sounds
        self.snd_shoot = create_sound(880, 0.05, 0.3, 'square')
        self.snd_explosion = create_sound(150, 0.2, 0.6, 'noise')
        self.snd_powerup = create_sound(600, 0.15, 0.4, 'sine')
        self.snd_levelup = create_sound(523, 0.4, 0.5, 'sine')
        self.snd_gameover = create_sound(220, 0.5, 0.6, 'square')

        self.stats = StatsManager()
        self.state = Enum('State', ['MENU', 'PLAYING', 'LEVEL_COMPLETE', 'GAME_OVER'])
        self.current_state = self.state.MENU
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.invaders = []
        self.bullets = []
        self.barriers = [Barrier(150, HEIGHT - 120), Barrier(300, HEIGHT - 120),
                         Barrier(450, HEIGHT - 120), Barrier(600, HEIGHT - 120)]
        self.particles = []
        self.powerups = []
        self.mystery = None
        self.level = 1
        self.score = 0
        self.multiplier = 1
        self.invader_speed = 1
        self.invader_step = 0
        self.invader_dir = 1
        self.mystery_timer = random.randint(5000, 15000)
        self.invader_shoot_timer = 0
        self.game_start_time = pygame.time.get_ticks()
        self.stars = StarField()
        self.shake = 0

    def spawn_invaders(self):
        self.invaders = []
        for row in range(5):
            for col in range(11):
                self.invaders.append(Invader(50 + col * 40, 50 + row * 30, row % 3))

    def update(self, dt):
        self.stars.update()
        self.player.update(dt)

        # Screen shake decay
        if self.shake > 0: self.shake -= dt * 20

        if self.current_state == self.state.PLAYING:
            # Mystery ship
            self.mystery_timer -= dt * 1000
            if self.mystery_timer <= 0:
                self.mystery = MysteryShip()
                self.mystery_timer = random.randint(8000, 20000)
            if self.mystery and self.mystery.active:
                self.mystery.update()
                if not self.mystery.active: self.mystery = None

            # Invader movement
            move_step = self.invader_speed * (1 + (self.level - 1) * 0.15)
            hit_edge = False
            for inv in self.invaders:
                inv.rect.x += move_step * self.invader_dir
                if inv.rect.left <= 10 or inv.rect.right >= WIDTH - 10:
                    hit_edge = True
                    break
            if hit_edge:
                self.invader_dir *= -1
                for inv in self.invaders:
                    inv.rect.y += 15

            # Invader shooting
            self.invader_shoot_timer -= dt
            if self.invader_shoot_timer <= 0 and self.invaders:
                shooter = random.choice(self.invaders)
                self.bullets.append(Bullet(shooter.rect.centerx, shooter.rect.bottom, 5))
                self.snd_shoot.play()
                self.invader_shoot_timer = max(0.5, 1.5 - self.level * 0.1)

            # Update bullets
            for b in self.bullets[:]:
                if b.update():
                    self.bullets.remove(b)
                    continue

                # Bullet vs Invaders
                if b.is_player:
                    for inv in self.invaders[:]:
                        if b.rect.colliderect(inv.rect):
                            self.bullets.remove(b)
                            self.invaders.remove(inv)
                            self.score += inv.points * self.multiplier
                            self.snd_explosion.play()
                            self.shake = 5
                            for _ in range(8):
                                self.particles.append(Particle(inv.rect.centerx, inv.rect.centery, COLORS['YELLOW']))
                            break
                    # Bullet vs Mystery
                    if self.mystery and b.rect.colliderect(self.mystery.rect):
                        self.bullets.remove(b)
                        self.score += random.choice([100, 150, 300])
                        self.snd_explosion.play()
                        self.shake = 8
                        self.powerups.append(PowerUp(self.mystery.rect.centerx, self.mystery.rect.centery))
                        self.mystery = None
                    # Bullet vs Barriers
                    for br in self.barriers:
                        if b.rect.collidelist([bl.rect for bl in br.blocks]) >= 0:
                            self.bullets.remove(b)
                            break
                else:
                    # Invader bullet vs Player
                    if b.rect.colliderect(self.player.rect):
                        if self.player.invincible <= 0 and 'SHIELD' not in self.player.active_powerups:
                            self.player.lives -= 1
                            self.player.invincible = 1.5
                            self.snd_explosion.play()
                            self.shake = 10
                            self.bullets.remove(b)
                    # Invader bullet vs Barriers
                    for br in self.barriers:
                        if br.get_hit(b.rect):
                            self.bullets.remove(b)
                            break

            # Update powerups
            for p in self.powerups[:]:
                if p.update():
                    self.powerups.remove(p)
                    continue
                if p.rect.colliderect(self.player.rect):
                    self.powerups.remove(p)
                    self.snd_powerup.play()
                    if p.p_type == 'LIFE':
                        self.player.lives += 1
                    elif p.p_type == 'SHIELD':
                        self.player.active_powerups['SHIELD'] = pygame.time.get_ticks() + 5000
                    elif p.p_type == 'RAPID':
                        self.player.active_powerups['RAPID'] = pygame.time.get_ticks() + 8000
                    elif p.p_type == 'MULTI':
                        self.multiplier = 2
                        self.player.active_powerups['MULTI'] = pygame.time.get_ticks() + 10000

                        def reset_multi():
                            self.multiplier = 1
                        # Simple timer handling via powerup dict cleanup in player.update()

            # Update particles
            self.particles = [p for p in self.particles if p.update(dt)]

            # Check level complete
            if not self.invaders:
                self.current_state = self.state.LEVEL_COMPLETE
                self.snd_levelup.play()
                self.level += 1
                self.spawn_invaders()

            # Check game over
            if self.player.lives <= 0:
                self.current_state = self.state.GAME_OVER
                self.snd_gameover.play()
                elapsed = (pygame.time.get_ticks() - self.game_start_time) / 1000
                self.stats.record(self.score, self.level, int(elapsed))

            # Shooting
            if pygame.key.get_pressed()[K_SPACE] and self.player.shoot_cd <= 0:
                self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.top, -8, True))
                self.player.shoot_cd = self.player.cd
                self.snd_shoot.play()

        # Shooting in menu/gameover for restart
        if self.current_state in [self.state.MENU, self.state.GAME_OVER]:
            keys = pygame.key.get_pressed()
            if keys[K_RETURN] or keys[K_SPACE]:
                self.reset_game()
                self.spawn_invaders()
                self.current_state = self.state.PLAYING
                self.game_start_time = pygame.time.get_ticks()

    def draw(self):
        # Apply screen shake
        shake_offset = (0, 0)
        if self.shake > 0:
            shake_offset = (random.uniform(-self.shake, self.shake), random.uniform(-self.shake, self.shake))
            self.screen = pygame.transform.offset(self.screen, *shake_offset)
        self.screen.fill(COLORS['DARK'])

        self.stars.draw(self.screen)

        if self.current_state == self.state.MENU:
            self.draw_text("SPACE INVADERS", WIDTH // 2, HEIGHT // 3, 48, COLORS['CYAN'])
            self.draw_text("PRESS SPACE OR ENTER TO START", WIDTH // 2, HEIGHT // 2, 24, COLORS['WHITE'])
            self.draw_text(f"HIGH SCORE: {self.stats.data['high_score']}", WIDTH // 2, HEIGHT // 2 + 40, 24,
                           COLORS['YELLOW'])
            self.draw_text(f"GAMES PLAYED: {self.stats.data['games_played']}", WIDTH // 2, HEIGHT // 2 + 70, 20,
                           COLORS['GRAY'])
            return

        # Draw game entities
        for br in self.barriers: br.draw(self.screen)
        for inv in self.invaders: inv.draw(self.screen)
        if self.mystery and self.mystery.active: self.mystery.draw(self.screen)
        for p in self.powerups: p.draw(self.screen)
        for b in self.bullets:
            pygame.draw.rect(self.screen, b.color, b.rect)
        for pt in self.particles: pt.draw(self.screen)
        self.player.draw(self.screen)

        # UI
        self.draw_text(f"SCORE: {self.score}", 20, 20, 24, COLORS['WHITE'])
        self.draw_text(f"LIVES: {'❤️' * self.player.lives}", WIDTH - 150, 20, 24, COLORS['RED'])
        self.draw_text(f"LEVEL: {self.level}", WIDTH // 2, 20, 24, COLORS['CYAN'])
        if self.multiplier > 1:
            self.draw_text("2X BONUS", WIDTH // 2, 50, 20, COLORS['MULTI'])

        if self.current_state == self.state.LEVEL_COMPLETE:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.screen.blit(s, (0, 0))
            self.draw_text(f"LEVEL {self.level - 1} COMPLETE!", WIDTH // 2, HEIGHT // 2, 48, COLORS['GREEN'])
            self.draw_text("PREPARING NEXT WAVE...", WIDTH // 2, HEIGHT // 2 + 60, 24, COLORS['WHITE'])
            pygame.time.delay(2000)
            self.current_state = self.state.PLAYING

        if self.current_state == self.state.GAME_OVER:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (0, 0))
            self.draw_text("GAME OVER", WIDTH // 2, HEIGHT // 3, 48, COLORS['RED'])
            self.draw_text(f"FINAL SCORE: {self.score}", WIDTH // 2, HEIGHT // 2, 28, COLORS['WHITE'])
            self.draw_text(f"LEVEL REACHED: {self.level}", WIDTH // 2, HEIGHT // 2 + 40, 24, COLORS['CYAN'])
            self.draw_text("PRESS SPACE TO PLAY AGAIN", WIDTH // 2, HEIGHT // 2 + 80, 24, COLORS['YELLOW'])

        pygame.display.flip()

    def draw_text(self, text, x, y, size, color):
        s = pygame.font.SysFont("Arial", size, bold=True).render(text, True, color)
        self.screen.blit(s, s.get_rect(center=(x, y)))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = SpaceInvaders()
    game.run()
