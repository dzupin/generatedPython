# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/Qwen3.6-27B-uncensored-heretic-v2-Native-MTP-Preserved-NVFP4-MLP-Only.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

import pygame
import sys
import math
import random
import json
import io
import wave
import array
import os

# ================= INITIALIZATION (MUST COME FIRST) =================
pygame.init()
pygame.mixer.init()  # Initialize audio system before generating any sounds

# ================= CONFIGURATION =================
WIDTH, HEIGHT = 800, 600
FPS = 60
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "space_invaders_save.json")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (60, 255, 60)
BLUE = (60, 60, 255)
YELLOW = (255, 255, 60)
CYAN = (60, 255, 255)
MAGENTA = (255, 60, 255)
GRAY = (100, 100, 100)


# ================= SOUND GENERATION =================
def generate_sound(freq, duration, volume=10000, fade=True):
    """Generate a sine wave sound programmatically (16-bit PCM)."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit signed
        w.setframerate(44100)
        samples = []
        num_samples = int(44100 * duration)
        for i in range(num_samples):
            t = i / 44100
            v = volume * math.sin(2 * math.pi * freq * t)
            if fade:
                v *= (1 - i / num_samples)
            samples.append(int(v))
        w.writeframes(array.array('h', samples).tobytes())
    buf.seek(0)
    return pygame.mixer.Sound(buf)


# Pre-generate sounds (Safe now because mixer is initialized above)
SFX = {
    "player_shoot": generate_sound(880, 0.1, 8000),
    "enemy_shoot": generate_sound(440, 0.15, 6000),
    "explosion": generate_sound(150, 0.3, 12000),
    "bonus": generate_sound(1200, 0.2, 9000),
    "level_up": generate_sound(600, 0.5, 15000),
    "player_hit": generate_sound(200, 0.2, 10000)
}


# ================= UTILITIES =================
def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"high_score": 0, "max_level": 1, "total_score": 0, "games_played": 0}


def save_save(data):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass


# ================= ENTITIES =================
class Particle:
    def __init__(self, x, y, color, speed, size=2):
        self.x, self.y = x, y
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.color = color
        self.size = size
        self.life = 30 + random.randint(-10, 10)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.95
        self.vy *= 0.95

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(s, (self.x - self.size, self.y - self.size))


class Bullet:
    def __init__(self, x, y, dy, color, is_player=True):
        self.rect = pygame.Rect(x, y, 4, 12)
        self.dy = dy
        self.color = color
        self.is_player = is_player
        self.alive = True

    def update(self):
        self.rect.y += self.dy
        if self.rect.y < -20 or self.rect.y > HEIGHT + 20:
            self.alive = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=2)
        glow = pygame.Surface((8, 16), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 80), glow.get_rect(), border_radius=2)
        screen.blit(glow, (self.rect.x - 2, self.rect.y - 2))


class Bonus:
    TYPES = [
        ("SHIELD", CYAN, "Invincibility (15s)"),
        ("RAPID", YELLOW, "Rapid Fire (10s)"),
        ("MULTI", MAGENTA, "Score x2 (15s)"),
        ("LIFE", GREEN, "Extra Life")
    ]

    def __init__(self, x, y):
        t = random.choice(self.TYPES)
        self.name, self.color, self.desc = t
        self.rect = pygame.Rect(x, y, 24, 24)
        self.vy = 2
        self.alive = True

    def update(self):
        self.rect.y += self.vy
        if self.rect.y > HEIGHT + 30:
            self.alive = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        pygame.draw.circle(screen, BLACK, (self.rect.centerx, self.rect.centery), 8)
        font = pygame.font.SysFont("consolas", 12, bold=True)
        txt = font.render(self.name[:2], True, WHITE)
        screen.blit(txt, (self.rect.x + 4, self.rect.y + 6))


class Block:
    def __init__(self, x, y, size=6):
        self.rect = pygame.Rect(x, y, size, size)
        self.health = 2


class Shield:
    def __init__(self, x, y):
        self.blocks = []
        pattern = [
            "..XXXXXX..",
            ".XXXXXXXX.",
            "XXXXXXXXXX",
            "XXXXXXXXXX",
            "XXXXXXXXXX",
            "XXXXXXXXXX",
            ".XXXXXXXX.",
            "..XXXXXX.."
        ]
        for row, line in enumerate(pattern):
            for col, char in enumerate(line):
                if char == 'X':
                    self.blocks.append(Block(x + col * 6, y + row * 6, 6))

    def update(self, bullets):
        to_remove = []
        for b in bullets:
            for block in self.blocks:
                if block.rect.colliderect(b.rect):
                    if b.is_player:
                        b.alive = False
                    block.health -= 1
                    if block.health <= 0:
                        to_remove.append(block)
                    break
        for block in to_remove:
            self.blocks.remove(block)

    def draw(self, screen):
        for block in self.blocks:
            color = GREEN if block.health == 2 else CYAN
            pygame.draw.rect(screen, color, block.rect, border_radius=2)


class Enemy:
    def __init__(self, x, y, row):
        self.rect = pygame.Rect(x, y, 28, 24)
        self.row = row
        self.type = 0 if row == 0 else (1 if row < 3 else 2)
        self.colors = [MAGENTA, YELLOW, CYAN]
        self.alive = True
        self.shoot_timer = random.randint(60, 180)

    def draw(self, screen, tick):
        if not self.alive: return
        color = self.colors[self.type]
        pygame.draw.rect(screen, color, self.rect, border_radius=3)
        eye_y = self.rect.centery + (2 if (tick // 30) % 2 == 0 else -2)
        pygame.draw.rect(screen, BLACK, (self.rect.x + 6, eye_y, 6, 6))
        pygame.draw.rect(screen, BLACK, (self.rect.x + 16, eye_y, 6, 6))
        leg_offset = 2 if (tick // 20) % 2 == 0 else 0
        pygame.draw.rect(screen, color, (self.rect.x + 4, self.rect.bottom, 4, 4 + leg_offset))
        pygame.draw.rect(screen, color, (self.rect.x + 20, self.rect.bottom, 4, 4 + leg_offset))


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 24)
        self.speed = 6
        self.shoot_cooldown = 0
        self.lives = 3
        self.score = 0
        self.shield_timer = 0
        self.rapid_timer = 0
        self.multi_timer = 0
        self.multiplier = 1
        self.alive = True
        self.invulnerable = 0

    def update(self, keys, screen_width):
        if self.alive:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
            self.rect.x = max(0, min(screen_width - self.rect.width, self.rect.x))
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            if self.invulnerable > 0:
                self.invulnerable -= 1

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 8 if self.rapid_timer > 0 else 15
            return Bullet(self.rect.centerx - 2, self.rect.y - 10, -10, YELLOW, True)
        return None

    def apply_bonus(self, bonus):
        if bonus.name == "SHIELD":
            self.shield_timer = 900
        elif bonus.name == "RAPID":
            self.rapid_timer = 600
        elif bonus.name == "MULTI":
            self.multi_timer = 900
            self.multiplier = 2
        elif bonus.name == "LIFE":
            self.lives += 1

    def update_bonuses(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
        else:
            self.multiplier = 1 if self.multi_timer <= 0 else self.multiplier
        if self.rapid_timer > 0: self.rapid_timer -= 1
        if self.multi_timer > 0:
            self.multi_timer -= 1
        else:
            self.multiplier = 1

    def draw(self, screen, tick):
        if not self.alive: return
        if self.invulnerable > 0 and tick % 10 < 5: return

        color = GREEN
        if self.shield_timer > 0:
            color = CYAN
        elif self.rapid_timer > 0:
            color = YELLOW

        pygame.draw.polygon(screen, color, [
            (self.rect.centerx, self.rect.y),
            (self.rect.right, self.rect.bottom),
            (self.rect.left, self.rect.bottom)
        ])
        pygame.draw.rect(screen, BLACK, (self.rect.centerx - 4, self.rect.y + 8, 8, 8))
        if self.shield_timer > 0:
            glow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (60, 255, 255, 80), glow_surf.get_rect(), border_radius=5)
            screen.blit(glow_surf, (self.rect.x - 5, self.rect.y - 5))


# ================= GAME CLASS =================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.state = "MENU"
        self.load_save_data()
        self.reset_game()
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 1.5)) for _ in
                      range(150)]

    def load_save_data(self):
        self.save_data = load_save()

    def reset_game(self):
        self.level = 1
        self.player = Player(WIDTH // 2 - 16, HEIGHT - 60)
        self.bullets = []
        self.enemies = []
        self.bonuses = []
        self.particles = []
        self.shields = []
        self.enemy_dir = 1
        self.enemy_speed = 0.3
        self.enemy_shoot_chance = 0.002
        self.ticks = 0
        self.screen_shake = 0
        self.create_level()

    def create_level(self):
        self.enemies = []
        rows = min(5, 3 + self.level // 3)
        cols = min(11, 8 + self.level // 2)
        spacing_x, spacing_y = 40, 30
        start_x = (WIDTH - cols * spacing_x) // 2
        for r in range(rows):
            for c in range(cols):
                self.enemies.append(Enemy(start_x + c * spacing_x, 60 + r * spacing_y, r))
        if not self.shields:
            for i in range(4):
                self.shields.append(Shield(120 + i * 180, HEIGHT - 140))
        self.enemy_speed = 0.3 + self.level * 0.15
        self.enemy_shoot_chance = 0.002 + self.level * 0.001

    def spawn_particles(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, random.uniform(1, 4)))

    def handle_menu(self):
        self.screen.fill(BLACK)
        for x, y, s in self.stars:
            pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), int(s))

        title = self.big_font.render("SPACE INVADERS", True, CYAN)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        info = [
            "High Score: {}".format(self.save_data["high_score"]),
            "Max Level: {}".format(self.save_data["max_level"]),
            "Games Played: {}".format(self.save_data["games_played"]),
            "",
            "Press ENTER to Start",
            "ESC to Quit"
        ]
        for i, txt in enumerate(info):
            color = WHITE if i < 3 or i == 3 else YELLOW
            surf = self.font.render(txt, True, color)
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 250 + i * 30))

        if self.ticks % 60 < 30:
            prompt = self.font.render("Press ENTER to Start", True, MAGENTA)
            self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 450))

    def update(self):
        self.ticks += 1
        keys = pygame.key.get_pressed()

        if self.state == "MENU":
            if keys[pygame.K_RETURN]:
                self.reset_game()
                self.state = "PLAYING"
                self.save_data["games_played"] += 1
                save_save(self.save_data)
            if keys[pygame.K_ESCAPE]:
                self.save_data["games_played"] += 1
                save_save(self.save_data)
                pygame.quit()
                sys.exit()
            return

        if self.state == "PAUSED":
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.state = "PLAYING"
            return

        if self.state == "GAMEOVER":
            if keys[pygame.K_RETURN]:
                self.state = "MENU"
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            return

        if keys[pygame.K_SPACE] or keys[pygame.K_p]:
            self.state = "PAUSED"
            return
        if keys[pygame.K_ESCAPE]:
            self.state = "MENU"
            save_save(self.save_data)
            return

        self.player.update(keys, WIDTH)
        self.player.update_bonuses()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            b = self.player.shoot()
            if b:
                self.bullets.append(b)
                SFX["player_shoot"].play()

        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        for b in self.bonuses:
            b.update()
        self.bonuses = [b for b in self.bonuses if b.alive]

        for shield in self.shields:
            shield.update(self.bullets)

        edge_hit = False
        for e in self.enemies:
            e.rect.x += self.enemy_speed * self.enemy_dir
            if e.rect.right >= WIDTH - 20 or e.rect.left <= 20:
                edge_hit = True
        if edge_hit:
            self.enemy_dir *= -1
            for e in self.enemies:
                e.rect.y += 15
                e.rect.x += self.enemy_speed * self.enemy_dir

        for e in self.enemies:
            e.shoot_timer -= 1
            if e.shoot_timer <= 0 and random.random() < self.enemy_shoot_chance:
                self.bullets.append(Bullet(e.rect.centerx, e.rect.bottom, 5, RED, False))
                SFX["enemy_shoot"].play()
                e.shoot_timer = random.randint(60, 180)

        for b in self.bullets:
            if b.is_player:
                for e in self.enemies:
                    if e.rect.colliderect(b.rect):
                        b.alive = False
                        e.alive = False
                        self.player.score += (10 if e.type == 0 else (
                            20 if e.type == 1 else 30)) * self.player.multiplier
                        self.spawn_particles(e.rect.centerx, e.rect.centery, e.colors[e.type])
                        SFX["explosion"].play()
                        if random.random() < 0.12:
                            self.bonuses.append(Bonus(e.rect.centerx, e.rect.centery))
                        break

        for b in self.bullets:
            if not b.is_player and self.player.rect.colliderect(b.rect):
                if self.player.shield_timer > 0 or self.player.invulnerable > 0:
                    b.alive = False
                else:
                    b.alive = False
                    self.player.lives -= 1
                    self.player.invulnerable = 60
                    self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, GREEN, 20)
                    SFX["player_hit"].play()
                    self.screen_shake = 10

        for b in self.bonuses:
            if self.player.rect.colliderect(b.rect):
                b.alive = False
                self.player.apply_bonus(b)
                SFX["bonus"].play()

        for e in self.enemies:
            if e.rect.colliderect(self.player.rect) and self.player.rect.y <= e.rect.y:
                self.player.lives = 0
                self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, GREEN, 30)
            for s in self.shields:
                for block in s.blocks:
                    if e.rect.colliderect(block.rect):
                        block.health = 0

        self.enemies = [e for e in self.enemies if e.alive]
        self.shields = [s for s in self.shields if s.blocks]
        self.bullets = [b for b in self.bullets if b.alive]
        self.bonuses = [b for b in self.bonuses if b.alive]

        if not self.enemies:
            self.level += 1
            if self.level > self.save_data["max_level"]:
                self.save_data["max_level"] = self.level
            SFX["level_up"].play()
            self.create_level()

        if self.player.lives <= 0 or any(e.rect.bottom >= self.player.rect.top for e in self.enemies):
            self.state = "GAMEOVER"
            if self.player.score > self.save_data["high_score"]:
                self.save_data["high_score"] = self.player.score
            self.save_data["total_score"] += self.player.score
            save_save(self.save_data)

        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self):
        offset_x = random.randint(-3, 3) if self.screen_shake > 0 else 0
        offset_y = random.randint(-3, 3) if self.screen_shake > 0 else 0
        self.screen.fill(BLACK)

        for x, y, s in self.stars:
            pygame.draw.circle(self.screen, WHITE, (int(x + offset_x), int(y + offset_y)), int(s))

        if self.state == "MENU":
            self.handle_menu()
            pygame.display.flip()
            return

        for s in self.shields:
            s.draw(self.screen)
        for b in self.bonuses:
            b.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen, self.ticks)
        for p in self.particles:
            p.draw(self.screen)
        self.player.draw(self.screen, self.ticks)

        ui_y = 10
        self.screen.blit(self.font.render(f"SCORE: {self.player.score}", True, WHITE), (10, ui_y))
        self.screen.blit(self.font.render(f"LIVES: {self.player.lives}", True, WHITE), (10, ui_y + 25))
        self.screen.blit(self.font.render(f"LEVEL: {self.level}", True, WHITE), (WIDTH - 140, ui_y))

        bx = WIDTH - 150
        by = ui_y + 25
        if self.player.shield_timer > 0:
            self.screen.blit(self.font.render(f"SHIELD: {self.player.shield_timer // 60}s", True, CYAN), (bx, by))
            by += 20
        if self.player.rapid_timer > 0:
            self.screen.blit(self.font.render(f"RAPID: {self.player.rapid_timer // 60}s", True, YELLOW), (bx, by))
            by += 20
        if self.player.multi_timer > 0:
            self.screen.blit(self.font.render(f"MULTI: {self.player.multi_timer // 60}s", True, MAGENTA), (bx, by))

        if self.state == "PAUSED":
            s = self.font.render("PAUSED - Press SPACE to Resume", True, WHITE)
            self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2))

        if self.state == "GAMEOVER":
            s1 = self.big_font.render("GAME OVER", True, RED)
            s2 = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
            s3 = self.font.render("Press ENTER for Menu / ESC to Quit", True, GRAY)
            self.screen.blit(s1, (WIDTH // 2 - s1.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(s2, (WIDTH // 2 - s2.get_width() // 2, HEIGHT // 2 + 10))
            self.screen.blit(s3, (WIDTH // 2 - s3.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_save(self.save_data)
                    pygame.quit()
                    sys.exit()

            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()

