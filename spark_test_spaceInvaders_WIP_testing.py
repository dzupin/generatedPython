# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

#  /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.6-35B-A3B-Uncensored.Q6_K_P.gguf  --mmproj /AI/models/Qwen3.6-35B-A3B-Uncensored.mmproj.f16.gguf


import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# ================= CONSTANTS =================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (10, 10, 15)
CYAN = (0, 255, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)
PURPLE = (180, 50, 255)
WHITE = (240, 240, 255)
GRAY = (100, 100, 120)

# Game Constants
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_BULLET_SPEED = 4
ALIEN_ROW = 5
ALIEN_COL = 10
ALIEN_WIDTH = 30
ALIEN_HEIGHT = 25
ALIEN_PADDING = 15
ALIEN_DROP = 20
COOLDOWN = 15  # frames between player shots


# ================= CLASSES =================

class Starfield:
    def __init__(self):
        self.stars = []
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(0.1, 0.5)
            size = random.randint(1, 2)
            brightness = random.randint(150, 255)
            self.stars.append([x, y, speed, size, brightness])

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
            star[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for star in self.stars:
            pygame.draw.circle(surface, (star[4], star[4], star[4]), (int(star[0]), int(star[1])), star[3])


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = PLAYER_SPEED
        self.cooldown = 0
        self.rect = pygame.Rect(x - self.width // 2, y - self.height, self.width, self.height)

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = COOLDOWN
            return Bullet(self.x, self.y - self.height // 2, -BULLET_SPEED, CYAN)
        return None

    def update_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        # Engine glow
        glow_surf = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 150, 255, 40), (self.width // 2, self.height), 20)  # FIXED LINE
        surface.blit(glow_surf, (self.x - self.width // 2 - 5, self.y - self.height // 2 - 5))

        # Main body
        pygame.draw.polygon(surface, CYAN, [
            (self.x, self.y - self.height // 2),
            (self.x - self.width // 2, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height // 2)
        ])
        # Cockpit
        pygame.draw.circle(surface, WHITE, (self.x, self.y - self.height // 4), 4)


class Alien:
    def __init__(self, x, y, alien_type):
        self.x = x
        self.y = y
        self.width = ALIEN_WIDTH
        self.height = ALIEN_HEIGHT
        self.alien_type = alien_type
        self.colors = [GREEN, PURPLE, YELLOW]
        self.color = self.colors[alien_type % 3]
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)

    def update(self):
        # CRITICAL FIX: Sync collision rect with visual position
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2

    def draw(self, surface):
        cx, cy = self.x, self.y
        w, h = self.width // 2, self.height // 2

        base = self.color
        dark = tuple(max(0, c - 80) for c in base)

        pygame.draw.rect(surface, base, (cx - w, cy - h // 2, w * 2, h))
        pygame.draw.rect(surface, dark, (cx - w // 2, cy - h, w * 1.5, h // 2))
        pygame.draw.circle(surface, (0, 0, 0), (cx - w // 3, cy - h // 4), 3)
        pygame.draw.circle(surface, (0, 0, 0), (cx + w // 3, cy - h // 4), 3)
        pygame.draw.rect(surface, base, (cx - w, cy + h // 2, 4, h // 2))
        pygame.draw.rect(surface, base, (cx + w - 4, cy + h // 2, 4, h // 2))


class Bullet:
    def __init__(self, x, y, dy, color):
        self.x = x
        self.y = y
        self.dy = dy
        self.color = color
        self.width = 4
        self.height = 12
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
        self.active = True

    def update(self):
        self.y += self.dy
        self.rect.centery = self.y
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface):
        glow = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color[:3], 100), (0, 0, self.width + 8, self.height + 8))
        surface.blit(glow, (self.x - self.width // 2 - 4, self.y - self.height // 2 - 4))
        pygame.draw.rect(surface, self.color, self.rect)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 4)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle * 0.5) * speed
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(1, 3)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.size *= 0.95

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        col = (*self.color, alpha)
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), max(1, int(self.size)))

    def is_dead(self):
        return self.life <= 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas,monospace", 24)
        self.big_font = pygame.font.SysFont("consolas,monospace", 48)

        self.state = "MENU"
        self.score = 0
        self.lives = 3
        self.level = 1

        self.stars = Starfield()
        self.player = None
        self.aliens = []
        self.bullets = []
        self.particles = []

        self.alien_dir = 1
        self.alien_speed = 1
        self.alien_move_timer = 0
        self.alien_move_delay = 40
        self.alien_shoot_timer = 0
        self.alien_shoot_delay = 60

        self.keys = pygame.key.get_pressed()
        self.run()

    def spawn_aliens(self):
        self.aliens = []
        start_x = (SCREEN_WIDTH - (ALIEN_COL * (ALIEN_WIDTH + ALIEN_PADDING))) // 2 + ALIEN_WIDTH // 2
        for row in range(ALIEN_ROW):
            for col in range(ALIEN_COL):
                x = start_x + col * (ALIEN_WIDTH + ALIEN_PADDING)
                y = 50 + row * (ALIEN_HEIGHT + ALIEN_PADDING)
                self.aliens.append(Alien(x, y, row))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU" or self.state == "GAME_OVER":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_game()
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.append(bullet)

        self.keys = pygame.key.get_pressed()

    def reset_game(self):
        self.state = "PLAYING"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.spawn_aliens()
        self.bullets = []
        self.particles = []
        self.alien_speed = 1 + self.level * 0.2
        self.alien_shoot_delay = max(20, 60 - self.level * 5)

    def update(self):
        self.stars.update()

        if self.state != "PLAYING":
            return

        self.player.move(self.keys)
        self.player.update_cooldown()

        # Aliens movement
        self.alien_move_timer += 1
        if self.alien_move_timer >= self.alien_move_delay:
            self.alien_move_timer = 0
            hit_edge = False
            for alien in self.aliens:
                if (alien.x + alien.width // 2 >= SCREEN_WIDTH and self.alien_dir > 0) or \
                        (alien.x - alien.width // 2 <= 0 and self.alien_dir < 0):
                    hit_edge = True
                    break

            if hit_edge:
                self.alien_dir *= -1
                for alien in self.aliens:
                    alien.y += ALIEN_DROP
            else:
                for alien in self.aliens:
                    alien.x += self.alien_speed * self.alien_dir * 2

            # Update rects for all aliens after movement
            for alien in self.aliens:
                alien.update()

        # Alien shooting
        self.alien_shoot_timer += 1
        if self.alien_shoot_timer >= self.alien_shoot_delay and self.aliens:
            self.alien_shoot_timer = 0
            shooter = random.choice(self.aliens)
            self.bullets.append(Bullet(shooter.x, shooter.y + shooter.height // 2, ALIEN_BULLET_SPEED, RED))

        # Update bullets
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.active]

        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

        self.check_collisions()

        if not self.aliens:
            self.level += 1
            self.spawn_aliens()
            self.alien_speed += 0.3
            self.alien_move_delay = max(10, self.alien_move_delay - 3)
            self.alien_shoot_delay = max(15, self.alien_shoot_delay - 3)
        elif any(a.y + a.height // 2 >= self.player.y for a in self.aliens):
            self.state = "GAME_OVER"

    def check_collisions(self):
        for bullet in self.bullets[:]:
            if bullet.dy < 0:
                for alien in self.aliens[:]:
                    if bullet.rect.colliderect(alien.rect):
                        self.create_explosion(alien.x, alien.y, alien.color)
                        self.aliens.remove(alien)
                        self.bullets.remove(bullet)
                        self.score += 10 * (3 - (alien.alien_type % 3))
                        break

        for bullet in self.bullets[:]:
            if bullet.dy > 0:
                if bullet.rect.colliderect(self.player.rect):
                    self.create_explosion(self.player.x, self.player.y, CYAN)
                    self.bullets.remove(bullet)
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = "GAME_OVER"
                    break

    def create_explosion(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def draw(self):
        self.screen.fill(BLACK)
        self.stars.draw(self.screen)

        if self.state == "PLAYING":
            self.player.draw(self.screen)
            for alien in self.aliens:
                alien.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for p in self.particles:
                p.draw(self.screen)

            score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
            lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
            level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (10, 35))
            self.screen.blit(level_text, (10, 60))

        elif self.state == "MENU":
            title = self.big_font.render("SPACE INVADERS", True, CYAN)
            sub = self.font.render("Press ENTER or SPACE to start", True, WHITE)
            instructions = [
                "LEFT/RIGHT or A/D to move",
                "SPACE to shoot",
                "Destroy aliens before they reach you!"
            ]
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 300))
            y_offset = 380
            for line in instructions:
                t = self.font.render(line, True, GRAY)
                self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, y_offset))
                y_offset += 30

        elif self.state == "GAME_OVER":
            go_text = self.big_font.render("GAME OVER", True, RED)
            sc_text = self.font.render(f"FINAL SCORE: {self.score}", True, WHITE)
            restart = self.font.render("Press ENTER or SPACE to restart", True, WHITE)
            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 200))
            self.screen.blit(sc_text, (SCREEN_WIDTH // 2 - sc_text.get_width() // 2, 300))
            self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 380))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game()
