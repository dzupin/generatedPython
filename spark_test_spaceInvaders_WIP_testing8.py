# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# //AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.6-27B-AEON-Ultimate-Uncensored-BF16.i1-Q6_K.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import random
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Fixed missing parenthesis
pygame.display.set_caption("Neon Invaders")
clock = pygame.time.Clock()

# Color Palette
BLACK = (10, 12, 16)
WHITE = (240, 240, 255)
TEAL = (29, 209, 161)
ORANGE = (245, 166, 35)
PURPLE = (180, 60, 220)
YELLOW = (255, 230, 109)
RED = (255, 107, 107)
CYAN = (78, 205, 196)

# Fonts (using None ensures it works on all OS without external .ttf files)
font = pygame.font.SysFont(None, 20)
title_font = pygame.font.SysFont(None, 48)

# Pre-render Assets (Procedural Graphics)
INVADER_SURFACES = {}
for t, col in zip(range(3), [CYAN, ORANGE, PURPLE]):
    s = pygame.Surface((30, 24), pygame.SRCALPHA)
    if t == 0:
        pygame.draw.rect(s, col, (5, 0, 20, 12))
        pygame.draw.rect(s, col, (0, 4, 30, 8))
        pygame.draw.rect(s, col, (2, 12, 6, 6))
        pygame.draw.rect(s, col, (22, 12, 6, 6))
    elif t == 1:
        pygame.draw.ellipse(s, col, (5, -2, 20, 16))
        pygame.draw.rect(s, col, (8, 10, 4, 8))
        pygame.draw.rect(s, col, (18, 10, 4, 8))
    else:
        pygame.draw.rect(s, col, (4, 0, 22, 14))
        pygame.draw.rect(s, col, (0, 4, 30, 8))
        pygame.draw.rect(s, col, (2, 12, 5, 6))
        pygame.draw.rect(s, col, (23, 12, 5, 6))
        pygame.draw.rect(s, col, (12, 14, 6, 6))
    pygame.draw.circle(s, BLACK, (10, 6), 2)
    pygame.draw.circle(s, BLACK, (20, 6), 2)
    INVADER_SURFACES[t] = s

PLAYER_SURF = pygame.Surface((40, 24), pygame.SRCALPHA)
pygame.draw.polygon(PLAYER_SURF, TEAL, [(20, 0), (40, 24), (0, 24)])
pygame.draw.ellipse(PLAYER_SURF, (255, 100, 50), (16, 20, 8, 8))

# Classes
class Star:
    def __init__(self, layer):
        self.layer = layer
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2.0) * (layer + 1)
        self.speed = random.uniform(0.3, 1.5) * (layer + 1)
        self.brightness = random.randint(100, 220)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        c = (self.brightness, self.brightness, min(255, self.brightness + 20))
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 30
        self.max_life = 30
        self.color = color
        self.size = random.uniform(1, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.95

    def draw(self, surface):
        alpha = max(0, (self.life / self.max_life) * 200)
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        color_a = (*self.color, alpha)
        pygame.draw.circle(surf, color_a, surf.get_rect().center, self.size)
        surface.blit(surf, (self.x - self.size, self.y - self.size))

class Bullet:
    def __init__(self, x, y, speed, is_player):
        self.rect = pygame.Rect(x - 2, y, 4, 12)
        self.speed = speed
        self.is_player = is_player
        self.color = YELLOW if is_player else RED
        self.alpha = 200

    def update(self):
        self.rect.y += self.speed
        self.alpha = max(50, self.alpha - 3)

    def draw(self, surface):
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        color_a = (*self.color, self.alpha)
        pygame.draw.ellipse(surf, color_a, surf.get_rect())
        surface.blit(surf, self.rect)

class Invader:
    def __init__(self, x, y, col, row):
        self.base_rect = pygame.Rect(x, y, 30, 24)
        self.rect = self.base_rect.copy()
        self.col = col
        self.row = row
        self.type = row % 3
        self.color = [CYAN, ORANGE, PURPLE][self.type]
        self.alive = True
        self.anim_frame = 0

    def draw(self, surface, offset_x=0, offset_y=0):
        if not self.alive: return
        # Slight bobbing animation
        bob = 2 if self.anim_frame % 20 < 10 else 0
        surface.blit(INVADER_SURFACES[self.type],
                     (self.rect.x + offset_x, self.rect.y + offset_y + bob))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 20, HEIGHT - 60, 40, 24)
        self.speed = 5
        self.bullets = []
        self.cooldown = 0
        self.lives = 3
        self.score = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        if keys[pygame.K_SPACE] and self.cooldown <= 0:
            self.bullets.append(Bullet(self.rect.centerx, self.rect.top, -6, True))
            self.cooldown = 15

        if self.cooldown > 0:
            self.cooldown -= 1

        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.rect.bottom > 0]

    def draw(self, surface):
        surface.blit(PLAYER_SURF, self.rect)
        for b in self.bullets:
            b.draw(surface)

# Game Manager
class Game:
    def __init__(self):
        self.state = "MENU"
        self.stars = [Star(layer) for layer in range(3) for _ in range(30)]
        self.reset()

    def reset(self):
        self.player = Player()
        self.invaders = []
        self.enemy_bullets = []
        self.particles = []
        self.invader_dir = 1
        self.invader_speed = 1
        self.invader_step_down = False
        self.shoot_timer = 0
        self.anim_timer = 0

        # Create grid
        for row in range(5):
            for col in range(11):
                x = 100 + col * 45
                y = 60 + row * 40
                self.invaders.append(Invader(x, y, col, row))

    def spawn_explosion(self, x, y, color):
        for _ in range(12):
            self.particles.append(Particle(x, y, color))

    def update(self):
        for s in self.stars:
            s.update()

        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Invader movement
        self.anim_timer += 1
        for inv in self.invaders:
            inv.anim_frame = self.anim_timer

        # Check boundaries & step down
        hit_edge = False
        for inv in self.invaders:
            if not inv.alive: continue
            if (self.invader_dir == 1 and inv.rect.right >= WIDTH - 10) or \
               (self.invader_dir == -1 and inv.rect.left <= 10):
                hit_edge = True
                break

        if hit_edge:
            self.invader_dir *= -1
            for inv in self.invaders:
                inv.rect.y += 15
            # Speed up as they descend
            self.invader_speed += 0.2

        for inv in self.invaders:
            inv.rect.x += self.invader_dir * self.invader_speed

        # Enemy shooting
        self.shoot_timer += 1
        alive_count = sum(1 for i in self.invaders if i.alive)
        if alive_count > 0 and self.shoot_timer > max(10, 80 - alive_count):
            shooters = [i for i in self.invaders if i.alive]
            shooter = random.choice(shooters)
            self.enemy_bullets.append(Bullet(shooter.rect.centerx, shooter.rect.bottom, 3, False))
            self.shoot_timer = 0

        # Update enemy bullets
        for b in self.enemy_bullets:
            b.update()
        self.enemy_bullets = [b for b in self.enemy_bullets if b.rect.top < HEIGHT]

        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Collisions
        # Player bullets vs Invaders
        for b in self.player.bullets[:]:
            for inv in self.invaders:
                if inv.alive and inv.rect.colliderect(b.rect):
                    inv.alive = False
                    self.player.bullets.remove(b)
                    self.player.score += 10 * (inv.row + 1)
                    self.spawn_explosion(inv.rect.centerx, inv.rect.centery, inv.color)
                    break

        # Enemy bullets vs Player
        for b in self.enemy_bullets[:]:
            if self.player.rect.colliderect(b.rect):
                self.enemy_bullets.remove(b)
                self.player.lives -= 1
                self.spawn_explosion(self.player.rect.centerx, self.player.rect.centery, TEAL)
                if self.player.lives <= 0:
                    self.state = "GAME_OVER"

        # Check Win/Lose
        if not any(i.alive for i in self.invaders):
            self.state = "WIN"
        for inv in self.invaders:
            if inv.alive and inv.rect.bottom >= self.player.rect.top:
                self.state = "GAME_OVER"
                break

    def draw(self):
        screen.fill(BLACK)
        for s in self.stars:
            s.draw(screen)

        if self.state == "MENU":
            title = title_font.render("NEON INVADERS", True, WHITE)
            sub = font.render("Press SPACE to Start", True, TEAL)
            # FIXED: Use .get_width() for cross-version compatibility
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2))
            pygame.draw.polygon(screen, TEAL, [(WIDTH//2, HEIGHT//2 + 80), (WIDTH//2+40, HEIGHT//2+120), (WIDTH//2-40, HEIGHT//2+120)])
            return

        # Draw entities
        for inv in self.invaders:
            inv.draw(screen)

        self.player.draw(screen)
        for b in self.enemy_bullets:
            b.draw(screen)
        for p in self.particles:
            p.draw(screen)

        # UI
        score_txt = font.render(f"SCORE: {self.player.score}", True, WHITE)
        screen.blit(score_txt, (10, 10))

        for i in range(self.player.lives):
            screen.blit(PLAYER_SURF, (WIDTH - 60 - i*45, 5))

        # State screens
        if self.state in ["GAME_OVER", "WIN"]:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((BLACK, 150))
            screen.blit(overlay, (0, 0))

            txt = "YOU WIN!" if self.state == "WIN" else "GAME OVER"
            color = TEAL if self.state == "WIN" else RED
            title = title_font.render(txt, True, color)
            sub = font.render(f"Final Score: {self.player.score}  |  Press SPACE to Restart", True, WHITE)
            # FIXED: Use .get_width()
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2))

        pygame.display.flip()

# Main Loop
def main():
    game = Game()
    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.state != "PLAYING":
                        game.reset()
                        game.state = "PLAYING"

        game.update()
        game.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
