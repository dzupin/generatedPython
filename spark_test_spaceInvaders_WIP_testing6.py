# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.6-27B-heretic-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf
import pygame
import random
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON INVADERS")
clock = pygame.time.Clock()

# Color Palette
BLACK = (0, 0, 0)
DEEP_SPACE = (10, 10, 20)
WHITE = (255, 255, 255)
RED = (255, 50, 80)
GREEN = (50, 255, 100)
BLUE = (50, 150, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 255)

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_WIN = 3


class Particle:
    """Explosion particle with fade-out"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 45)
        self.max_life = self.life
        self.color = color
        self.size = random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.96

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        # Draw glow behind
        pygame.draw.circle(surf, (*self.color, 50), (int(self.x), int(self.y)), int(self.size) + 4)
        # Draw core
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size))


class Bullet:
    def __init__(self, x, y, dy, color):
        self.rect = pygame.Rect(x, y, 4, 12)
        self.dy = dy
        self.color = color
        self.active = True

    def update(self):
        self.rect.y += self.dy
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.active = False

    def draw(self, surf):
        # Neon glow effect
        pygame.draw.rect(surf, (*self.color, 40), self.rect.inflate(12, 18))
        pygame.draw.rect(surf, self.color, self.rect)
        pygame.draw.rect(surf, WHITE, self.rect, 1)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.width = 36
        self.height = 20
        self.speed = 8
        self.color = CYAN
        self.cooldown = 0
        self.lives = 3
        self.invulnerable = 0

    def update(self, keys):
        if self.invulnerable > 0:
            self.invulnerable -= 1

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))

    def draw(self, surf):
        # Blink when hit
        if self.invulnerable > 0 and pygame.time.get_ticks() // 80 % 2 == 0:
            return

        # Engine glow
        glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 60), (15, 15), 14)
        surf.blit(glow_surf, (self.x - 15, self.y - 15))

        # Ship body (polygon)
        points = [
            (self.x, self.y - 18),
            (self.x - 18, self.y + 8),
            (self.x, self.y + 4),
            (self.x + 18, self.y + 8)
        ]
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, WHITE, points, 2)

        # Thruster flame (animated)
        flame_h = random.randint(6, 12)
        pygame.draw.polygon(surf, YELLOW, [
            (self.x - 6, self.y + 8),
            (self.x + 6, self.y + 8),
            (self.x, self.y + 8 + flame_h)
        ])


class Alien:
    def __init__(self, x, y, row, col):
        self.rect = pygame.Rect(x, y, 28, 18)
        self.row = row
        self.col = col
        self.color = [RED, YELLOW, GREEN, CYAN, PURPLE][row % 5]
        self.points = [10, 20, 30, 40, 50][row % 5]
        self.alive = True
        self.anim_frame = 0

    def draw(self, surf, cx, cy):
        if not self.alive:
            return

        # Glow
        pygame.draw.ellipse(surf, (*self.color, 30), pygame.Rect(cx - 16, cy - 12, 32, 24))

        # Body
        pygame.draw.ellipse(surf, self.color, pygame.Rect(cx - 12, cy - 9, 24, 18))

        # Eyes
        pygame.draw.circle(surf, BLACK, (cx - 5, cy), 3)
        pygame.draw.circle(surf, BLACK, (cx + 5, cy), 3)

        # Legs (animated toggle)
        leg_off = 4 if self.anim_frame % 2 == 0 else -4
        pygame.draw.rect(surf, self.color, (cx - 10, cy + 8 + leg_off, 4, 4))
        pygame.draw.rect(surf, self.color, (cx + 6, cy + 8 + leg_off, 4, 4))

        # Antenna
        pygame.draw.line(surf, self.color, (cx - 8, cy - 12), (cx - 8, cy - 16), 2)
        pygame.draw.line(surf, self.color, (cx + 8, cy - 12), (cx + 8, cy - 16), 2)


class BunkerBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 6, 6)
        self.alive = True

    def draw(self, surf):
        if self.alive:
            pygame.draw.rect(surf, GREEN, self.rect)
            pygame.draw.rect(surf, WHITE, self.rect, 1)


class Game:
    def __init__(self):
        self.state = STATE_MENU
        self.score = 0
        self.level = 1
        self.stars = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(150)]
        self.particles = []
        self.bullets = []
        self.alien_bullets = []
        self.aliens = []
        self.bunkers = []
        self.player = Player()
        self.alien_dir = 1
        self.alien_speed = 1.0
        self.alien_drop = 18
        self.alien_anim_timer = 0
        self.reset_level()

    def reset_level(self):
        self.bullets = []
        self.alien_bullets = []
        self.particles = []
        self.alien_dir = 1
        self.alien_speed = 1.0 + self.level * 0.25
        self.aliens = []
        for r in range(5):
            for c in range(11):
                x = 50 + c * 42
                y = 50 + r * 36
                self.aliens.append(Alien(x, y, r, c))
        self.create_bunkers()

    def create_bunkers(self):
        self.bunkers = []
        bunker_centers = [120, 310, 490, 680]
        for bx in bunker_centers:
            for row in range(4):
                for col in range(6):
                    self.bunkers.append(BunkerBlock(bx + col * 8, 460 + row * 8))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.state == STATE_PLAYING:
                    self.bullets.append(Bullet(self.player.x, self.player.y, -9, CYAN))
                elif event.key == pygame.K_r:
                    if self.state in (STATE_GAMEOVER, STATE_WIN):
                        self.state = STATE_MENU
                        self.score = 0
                        self.level = 1
                        self.player.lives = 3
                        self.reset_level()
                elif event.key == pygame.K_RETURN and self.state == STATE_MENU:
                    self.state = STATE_PLAYING
        return True

    def create_explosion(self, x, y, color):
        for _ in range(12):
            self.particles.append(Particle(x, y, color))

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Update bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.active]

        for ab in self.alien_bullets:
            ab.update()
        self.alien_bullets = [ab for ab in self.alien_bullets if ab.active]

        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Alien movement logic
        alive_aliens = [a for a in self.aliens if a.alive]
        if not alive_aliens:
            self.level += 1
            self.reset_level()
            return

        # Check if any alive alien hit the screen edge
        hit_edge = False
        for a in alive_aliens:
            if (self.alien_dir > 0 and a.rect.right >= WIDTH - 20) or \
                    (self.alien_dir < 0 and a.rect.left <= 20):
                hit_edge = True
                break

        if hit_edge:
            self.alien_dir *= -1
            for a in alive_aliens:
                a.rect.y += self.alien_drop
        else:
            for a in alive_aliens:
                a.rect.x += self.alien_dir * self.alien_speed

        # Alien shooting (only bottom-most per column)
        if random.random() < 0.008 * self.level:
            cols = {}
            for a in alive_aliens:
                c = a.col
                if c not in cols or a.rect.y > cols[c].rect.y:
                    cols[c] = a
            shooters = list(cols.values())
            if shooters:
                shooter = random.choice(shooters)
                self.alien_bullets.append(Bullet(shooter.rect.centerx, shooter.rect.bottom, 5.5, RED))

        # Collision: Player bullets -> Aliens
        for b in self.bullets[:]:
            hit = False
            for a in alive_aliens:
                if a.rect.colliderect(b.rect):
                    a.alive = False
                    self.score += a.points
                    self.create_explosion(a.rect.centerx, a.rect.centery, a.color)
                    hit = True
                    break
            if not hit:
                for bk in self.bunkers[:]:
                    if bk.rect.colliderect(b.rect):
                        bk.alive = False
                        self.create_explosion(bk.rect.centerx, bk.rect.centery, GREEN)
                        hit = True
                        break
            if hit:
                b.active = False

        # Collision: Alien bullets -> Player / Bunkers
        for ab in self.alien_bullets[:]:
            player_rect = pygame.Rect(self.player.x - 18, self.player.y - 18, 36, 36)
            if player_rect.colliderect(ab.rect):
                self.player.lives -= 1
                self.player.invulnerable = 90
                self.create_explosion(self.player.x, self.player.y, CYAN)
                ab.active = False
                if self.player.lives <= 0:
                    self.state = STATE_GAMEOVER
                continue

            for bk in self.bunkers[:]:
                if bk.rect.colliderect(ab.rect):
                    bk.alive = False
                    self.create_explosion(bk.rect.centerx, bk.rect.centery, GREEN)
                    ab.active = False

        # Check win condition
        if not any(a.alive for a in self.aliens):
            self.state = STATE_WIN

    def draw_scanlines(self, surf):
        """Procedural CRT scanline overlay"""
        for y in range(0, HEIGHT, 2):
            pygame.draw.line(surf, (0, 0, 0, 40), (0, y), (WIDTH, y), 1)

    def draw(self):
        screen.fill(DEEP_SPACE)

        # Draw static stars (simple position list)
        for sx, sy in self.stars:
            pygame.draw.circle(screen, WHITE, (sx, sy), 1)

        # Draw bunkers
        for bk in self.bunkers:
            bk.draw(screen)

        # Draw aliens
        for a in self.aliens:
            a.draw(screen, a.rect.centerx, a.rect.centery)

        # Draw player
        self.player.draw(screen)

        # Draw bullets
        for b in self.bullets:
            b.draw(screen)
        for ab in self.alien_bullets:
            ab.draw(screen)

        # Draw particles
        for p in self.particles:
            p.draw(screen)

        # UI Text
        font = pygame.font.SysFont("consolas", 32, bold=True)
        score_txt = font.render(f"SCORE: {self.score}  LEVEL: {self.level}", True, WHITE)
        screen.blit(score_txt, (10, 10))

        lives_txt = font.render(f"LIVES: {self.player.lives}", True, WHITE)
        screen.blit(lives_txt, (WIDTH - 110, 10))

        # State overlays
        if self.state == STATE_MENU:
            title = font.render("NEON INVADERS", True, CYAN)
            sub = font.render("Press ENTER to Start  |  Arrows/WASD to Move  |  SPACE to Shoot", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

        elif self.state == STATE_GAMEOVER:
            title = font.render("GAME OVER", True, RED)
            sub = font.render("Press R to Restart", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

        elif self.state == STATE_WIN:
            title = font.render("WAVE COMPLETE", True, GREEN)
            sub = font.render("Press R for Next Level", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

        # CRT Effect
        self.draw_scanlines(screen)

        pygame.display.flip()

    def run(self):
        while True:
            if not self.handle_events():
                break
            if self.state == STATE_PLAYING:
                self.update()
            self.draw()
            clock.tick(60)


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
