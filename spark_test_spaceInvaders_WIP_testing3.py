# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2  --model /AI/models/Qwen3.5-35B-A3B-heretic-v2-Native-MTP-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-35B-A3B-mmproj-F32.gguf

import pygame
import json
import os
import random
import sys
import math

# ==================== CONFIGURATION ====================
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
FONT_NAME = None  # Will use system default if None
STATS_FILE = "space_invaders_stats.json"

# Colors
BG_COLOR = (8, 8, 24)
PLAYER_COLOR = (0, 255, 220)
ALIEN_COLORS = [(80, 255, 80), (255, 200, 40), (255, 80, 80), (80, 80, 255)]
BARRIER_COLOR = (40, 180, 80)
BULLET_COLOR = (255, 255, 50)
BONUS_COLOR = (255, 50, 180)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)

# Game Constants
PLAYER_SPEED = 300
BULLET_SPEED = 400
ALIEN_BASE_SPEED = 40
ALIEN_DROP = 20
BARRIER_POSITIONS = [(150, 500), (300, 500), (500, 500), (650, 500)]
BARRIER_BLOCK_SIZE = 6
BARRIER_BLOCKS_X = 12
BARRIER_BLOCKS_Y = 6
MAX_LIVES = 5
BONUS_LIFE_THRESHOLD = 5000
UFO_INTERVAL_MIN, UFO_INTERVAL_MAX = 5, 12  # seconds
UFO_SPEED = 150
UFO_POINTS = 150

# ==================== INITIALIZATION ====================
# Initialize Pygame and Mixer BEFORE defining sounds
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(6)


# ==================== SOUND GENERATION ====================
def make_sound(freq, duration, decay=3.0, volume=0.25):
    """Generate a simple PCM sound without external files."""
    sample_rate = 22050
    samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        wave = math.sin(2 * math.pi * freq * t)
        envelope = math.exp(-t * decay)
        val = volume * wave * envelope
        samples.append(max(0, min(255, int(val * 128 + 128))) & 0xFF)
    return pygame.mixer.Sound(buffer=bytes(samples))


# Pre-generate sounds (Now safe because mixer is initialized)
SOUNDS = {
    "shoot": make_sound(880, 0.08, decay=5),
    "alien_shoot": make_sound(300, 0.12, decay=4),
    "explosion": make_sound(150, 0.2, decay=8),
    "bonus": make_sound(1200, 0.15, decay=2),
    "level_up": make_sound(440, 0.3, decay=6),
    "hit": make_sound(200, 0.05, decay=10),
    "game_over": make_sound(100, 0.4, decay=3)
}


# ==================== GRAPHICS HELPERS ====================
def draw_rounded_rect(surface, color, rect, radius=4):
    """Draw a rectangle with rounded corners."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_spaceship(surface, rect):
    """Draw player ship procedurally."""
    points = [
        (rect.centerx, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom)
    ]
    pygame.draw.polygon(surface, PLAYER_COLOR, points)
    # Cockpit highlight
    pygame.draw.polygon(surface, (150, 255, 255), [
        (rect.centerx - 3, rect.top + 10),
        (rect.centerx, rect.top + 18),
        (rect.centerx + 3, rect.top + 10)
    ])


def draw_alien(surface, rect, color, row):
    """Draw alien shapes based on row."""
    cx, cy = rect.centerx, rect.centery
    # Body
    pygame.draw.rect(surface, color, (rect.x + 2, rect.y + 4, rect.width - 4, rect.height - 6))
    # Eyes
    eye_color = (0, 0, 0)
    pygame.draw.circle(surface, eye_color, (cx - 4, cy - 2), 1)
    pygame.draw.circle(surface, eye_color, (cx + 4, cy - 2), 1)
    # Legs/Details based on row
    if row == 0:
        pygame.draw.polygon(surface, color,
                            [(rect.left, rect.bottom), (rect.left + 4, rect.bottom - 4), (rect.left + 8, rect.bottom)])
        pygame.draw.polygon(surface, color, [(rect.right, rect.bottom), (rect.right - 4, rect.bottom - 4),
                                             (rect.right - 8, rect.bottom)])
    elif row == 1:
        pygame.draw.rect(surface, color, (rect.left + 2, rect.bottom - 4, 4, 4))
        pygame.draw.rect(surface, color, (rect.right - 6, rect.bottom - 4, 4, 4))
    elif row == 2:
        pygame.draw.circle(surface, color, (cx, rect.bottom - 2), 2)
    else:
        pygame.draw.polygon(surface, color, [(cx - 4, rect.bottom), (cx, rect.bottom - 3), (cx + 4, rect.bottom)])


def draw_barrier_block(surface, rect):
    pygame.draw.rect(surface, BARRIER_COLOR, rect)
    pygame.draw.rect(surface, (60, 220, 100), rect, width=1)


def draw_ufo(surface, rect):
    cx, cy = rect.centerx, rect.centery
    pygame.draw.ellipse(surface, BONUS_COLOR, rect)
    pygame.draw.ellipse(surface, (255, 100, 200), (rect.left + 4, rect.top + 2, rect.width - 8, rect.height // 2))
    # Lights
    for i in range(4):
        x = rect.left + 6 + i * 6
        pygame.draw.circle(surface, (255, 255, 255), (x, cy), 1)


# ==================== ENTITIES ====================
class Particle:
    def __init__(self, x, y, color, speed=100):
        angle = random.uniform(0, 2 * math.pi)
        vel = random.uniform(0.3, 1.0) * speed
        self.x, self.y = x, y
        self.vx = math.cos(angle) * vel
        self.vy = math.sin(angle * 1.5) * vel  # Slightly biased upward
        self.life = random.uniform(0.3, 0.6)
        self.color = color
        self.size = random.uniform(1.5, 3.0)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.size *= 0.95

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - 15, SCREEN_HEIGHT - 60, 30, 24)
        self.lives = 3
        self.shoot_timer = 0
        self.shoot_cooldown = 0.25
        self.invulnerable = 0

    def update(self, dt, keys):
        if self.invulnerable > 0:
            self.invulnerable -= dt
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move = 1
        self.rect.x += move * PLAYER_SPEED * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.shoot_timer -= dt
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_cooldown
            return True
        return False

    def take_damage(self):
        if self.invulnerable <= 0:
            self.lives -= 1
            self.invulnerable = 1.5
            return True
        return False

    def draw(self, surface):
        if self.invulnerable <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
            draw_spaceship(surface, self.rect)


class Bullet:
    def __init__(self, x, y, is_player=True):
        self.rect = pygame.Rect(x - 2, y - 4, 4, 8)
        self.is_player = is_player
        self.speed = -BULLET_SPEED if is_player else BULLET_SPEED // 2

    def update(self, dt):
        self.rect.y += self.speed * dt
        return self.rect.bottom > SCREEN_HEIGHT and not self.is_player or self.rect.top < 0 and self.is_player

    def draw(self, surface):
        color = BULLET_COLOR if self.is_player else (255, 150, 100)
        pygame.draw.rect(surface, color, self.rect)


class Barrier:
    def __init__(self, base_x, base_y):
        self.blocks = []
        for r in range(BARRIER_BLOCKS_Y):
            for c in range(BARRIER_BLOCKS_X):
                # Create classic stepped shape
                if r < 2 and (c < 2 or c >= BARRIER_BLOCKS_X - 2):
                    continue
                if r < 3 and (c == 3 or c == BARRIER_BLOCKS_X - 4):
                    continue
                self.blocks.append(pygame.Rect(
                    base_x + c * BARRIER_BLOCK_SIZE,
                    base_y + r * BARRIER_BLOCK_SIZE,
                    BARRIER_BLOCK_SIZE, BARRIER_BLOCK_SIZE
                ))

    def check_collision(self, bullet):
        for i, block in enumerate(self.blocks):
            if block.colliderect(bullet.rect):
                self.blocks.pop(i)
                return True
        return False

    def draw(self, surface):
        for block in self.blocks:
            draw_barrier_block(surface, block)


class BonusAlien:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH + 40, 30, 32, 16)
        self.speed = -UFO_SPEED
        self.alive = True

    def update(self, dt):
        self.rect.x += self.speed * dt
        if self.rect.right < 0:
            self.alive = False

    def draw(self, surface):
        draw_ufo(surface, self.rect)


# ==================== GAME CLASS ====================
class SpaceInvaders:
    # Default stats with all required keys
    DEFAULT_STATS = {
        "high_score": 0,
        "total_games": 0,
        "highest_level": 1,
        "total_score": 0
    }

    def __init__(self):
        # pygame.init() and mixer are already called at module level now
        # But we keep display setup here
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 24)
        self.big_font = pygame.font.Font(FONT_NAME, 48)
        self.stats = self.load_stats()
        self.reset_game()
        self.state = "MENU"  # MENU, PLAYING, LEVEL_TRANS, GAME_OVER
        self.transition_timer = 0
        self.ufo_timer = random.uniform(UFO_INTERVAL_MIN, UFO_INTERVAL_MAX)
        self.lives_bonus_timer = 0
        self.particles = []
        # FIX: Use lists instead of tuples so we can modify coordinates
        self.stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)] for _ in range(100)]

    def load_stats(self):
        """Load stats from file, ensuring all required keys exist."""
        default_stats = self.DEFAULT_STATS.copy()

        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge loaded stats with defaults to ensure all keys exist
                    for key in default_stats:
                        if key not in loaded:
                            loaded[key] = default_stats[key]
                    return loaded
            except:
                pass

        return default_stats

    def save_stats(self):
        self.stats["total_score"] += self.score
        if self.score > self.stats["high_score"]:
            self.stats["high_score"] = self.score
        if self.level > self.stats["highest_level"]:
            self.stats["highest_level"] = self.level
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f)
        except:
            pass

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.lives = 3
        self.player = Player()
        self.bullets = []
        self.aliens = []
        self.barriers = [Barrier(x, y) for x, y in BARRIER_POSITIONS]
        self.bonus = None
        self.alien_dir = 1
        self.alien_move_timer = 0
        self.alien_shot_timer = 0
        self.create_aliens()

    def create_aliens(self):
        rows = min(3 + self.level // 2, 8)
        cols = 10
        spacing = 45
        start_x = (SCREEN_WIDTH - cols * spacing) // 2
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(start_x + c * spacing, 60 + r * 35, 30, 24)
                self.aliens.append({
                    "rect": rect,
                    "row": r,
                    "color": ALIEN_COLORS[r % len(ALIEN_COLORS)],
                    "alive": True,
                    "shot_timer": random.uniform(0.5, 2.0)
                })

    def spawn_particles(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self, dt):
        # Stars background
        for s in self.stars:
            s[1] += 15 * dt
            if s[1] > SCREEN_HEIGHT:
                s[1] = -5
                s[0] = random.randint(0, SCREEN_WIDTH)

        # Particles
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update(dt)

        if self.state == "PLAYING":
            self.handle_player(dt)
            self.handle_bullets(dt)
            self.handle_aliens(dt)
            self.handle_barriers()
            self.handle_bonus(dt)
            self.check_level_state()

        elif self.state == "LEVEL_TRANS":
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.level += 1
                self.reset_game()
                self.state = "PLAYING"
                self.ufo_timer = random.uniform(UFO_INTERVAL_MIN, UFO_INTERVAL_MAX)

        elif self.state == "GAME_OVER":
            self.save_stats()
            self.stats["total_games"] += 1
            self.state = "MENU"

    def handle_player(self, dt):
        keys = pygame.key.get_pressed()
        if self.player.update(dt, keys):
            self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.bottom - 5))
            SOUNDS["shoot"].play()

    def handle_bullets(self, dt):
        new_bullets = []
        for b in self.bullets:
            off_screen = b.update(dt)
            if not off_screen:
                new_bullets.append(b)
        self.bullets = new_bullets

        # Collisions
        to_remove = []
        for b in self.bullets:
            # Player bullet hits alien
            if b.is_player:
                for alien in self.aliens:
                    if alien["alive"] and alien["rect"].colliderect(b.rect):
                        alien["alive"] = False
                        self.score += 10 * self.level
                        self.spawn_particles(alien["rect"].centerx, alien["rect"].centery, alien["color"])
                        SOUNDS["explosion"].play()
                        to_remove.append(b)
                        break
            # Enemy bullet hits player
            else:
                if self.player.rect.colliderect(b.rect) and self.player.invulnerable <= 0:
                    self.player.take_damage()
                    self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, PLAYER_COLOR, 12)
                    SOUNDS["hit"].play()
                    to_remove.append(b)
            # Bonus alien hit
            if self.bonus and self.bonus.alive and b.is_player and self.bonus.rect.colliderect(b.rect):
                self.score += UFO_POINTS
                self.spawn_particles(self.bonus.rect.centerx, self.bonus.rect.centery, BONUS_COLOR, 15)
                SOUNDS["bonus"].play()
                self.bonus.alive = False
                to_remove.append(b)

        # Check life bonus
        if self.score >= self.lives_bonus_timer + BONUS_LIFE_THRESHOLD and self.player.lives < MAX_LIVES:
            self.player.lives += 1
            self.lives_bonus_timer = self.score

        for b in to_remove:
            self.bullets.remove(b)

    def handle_aliens(self, dt):
        if not self.aliens or all(not a["alive"] for a in self.aliens):
            return

        self.alien_shot_timer -= dt
        # Move aliens
        move_down = False
        for a in self.aliens:
            if a["alive"]:
                if self.alien_dir == 1 and a["rect"].right >= SCREEN_WIDTH - 10:
                    move_down = True
                elif self.alien_dir == -1 and a["rect"].left <= 10:
                    move_down = True

        speed = ALIEN_BASE_SPEED + (self.level * 8)
        for a in self.aliens:
            if a["alive"]:
                a["rect"].x += speed * self.alien_dir * dt if not move_down else 0
                if move_down:
                    a["rect"].y += ALIEN_DROP
                    self.alien_dir *= -1

        # Shooting
        if self.alien_shot_timer <= 0:
            alive_aliens = [a for a in self.aliens if a["alive"]]
            if alive_aliens:
                shooter = random.choice(alive_aliens)
                self.bullets.append(Bullet(shooter["rect"].centerx, shooter["rect"].bottom))
                SOUNDS["alien_shoot"].play()
                self.alien_shot_timer = max(0.15, 2.0 - self.level * 0.2)

        # Check if aliens reached bottom
        for a in self.aliens:
            if a["alive"] and a["rect"].bottom >= self.player.rect.top:
                self.state = "GAME_OVER"
                SOUNDS["game_over"].play()

    def handle_barriers(self):
        for barrier in self.barriers:
            for b in self.bullets:
                if barrier.check_collision(b):
                    self.spawn_particles(b.rect.centerx, b.rect.centery, BARRIER_COLOR, 4)
                    self.bullets.remove(b)
                    break

    def handle_bonus(self, dt):
        if not self.bonus or not self.bonus.alive:
            self.ufo_timer -= dt
            if self.ufo_timer <= 0:
                self.bonus = BonusAlien()
                self.ufo_timer = random.uniform(UFO_INTERVAL_MIN, UFO_INTERVAL_MAX)
        if self.bonus:
            self.bonus.update(dt)

    def check_level_state(self):
        if all(not a["alive"] for a in self.aliens):
            self.state = "LEVEL_TRANS"
            self.transition_timer = 2.5
            SOUNDS["level_up"].play()

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Stars
        for s in self.stars:
            pygame.draw.circle(self.screen, (40, 40, 60), (s[0], s[1]), 1)

        # Barriers
        for barrier in self.barriers:
            barrier.draw(self.screen)

        # Aliens
        for a in self.aliens:
            if a["alive"]:
                draw_alien(self.screen, a["rect"], a["color"], a["row"])

        # Bonus
        if self.bonus and self.bonus.alive:
            self.bonus.draw(self.screen)

        # Player
        self.player.draw(self.screen)

        # Bullets
        for b in self.bullets:
            b.draw(self.screen)

        # Particles
        for p in self.particles:
            p.draw(self.screen)

        # UI
        self.draw_ui()

        # States
        if self.state == "MENU":
            self.draw_overlay("SPACE INVADERS", "PRESS ANY KEY TO START", GRAY)
        elif self.state == "LEVEL_TRANS":
            self.draw_overlay(f"LEVEL {self.level} COMPLETE!", "GET READY...", WHITE)
        elif self.state == "GAME_OVER":
            self.draw_overlay("GAME OVER", "PRESS ANY KEY FOR MENU", (255, 80, 80))

        pygame.display.flip()

    def draw_ui(self):
        score_surf = self.font.render(f"SCORE: {self.score}", True, WHITE)
        level_surf = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, WHITE)
        high_surf = self.font.render(f"HIGH: {self.stats['high_score']}", True, GRAY)

        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(level_surf, (10, 40))
        self.screen.blit(lives_surf, (10, 70))
        self.screen.blit(high_surf, (10, 100))

        # Lives as icons
        for i in range(self.player.lives):
            rect = pygame.Rect(SCREEN_WIDTH - 200 + i * 25, 10, 15, 12)
            draw_spaceship(self.screen, rect)

        # Bonus indicator
        if self.bonus and self.bonus.alive:
            ufo_surf = self.font.render(f"+{UFO_POINTS}", True, BONUS_COLOR)
            self.screen.blit(ufo_surf, (self.bonus.rect.centerx - 15, self.bonus.rect.top - 15))

    def draw_overlay(self, title, subtitle, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        t_surf = self.big_font.render(title, True, color)
        s_surf = self.font.render(subtitle, True, WHITE)
        t_rect = t_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        s_rect = s_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(t_surf, t_rect)
        self.screen.blit(s_surf, s_rect)

    def run(self):
        last_time = pygame.time.get_ticks()
        while True:
            dt = (pygame.time.get_ticks() - last_time) / 1000.0
            last_time = pygame.time.get_ticks()
            dt = min(dt, 0.05)  # Cap delta time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_stats()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.state in ["MENU", "GAME_OVER"]:
                        self.reset_game()
                        self.state = "PLAYING"
                        SOUNDS["shoot"].play()  # Start sound

            self.update(dt)
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = SpaceInvaders()
    game.run()
