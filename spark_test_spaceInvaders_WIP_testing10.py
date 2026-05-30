# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0  --port 5000 -fa 1 --model /AI/models/gemma-4-26B-A4B-it-heretic.Q6_K.gguf.gguf  --mmproj /AI/models/gemma-4-31b-mmproj-F32.gguf

import pygame
import random
import math

# --- Configuration & Constants ---
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors (Neon/Vibrant Palette)
BLACK = (5, 5, 15)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)
RED = (255, 50, 50)
ORANGE = (255, 165, 0)


# --- Helper Classes for "Juice" ---

class Particle(pygame.sprite.Sprite):
    """Small particles for explosions."""

    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
        self.lifetime = 25  # Frames

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class Barrier(pygame.sprite.Sprite):
    """Destructible bunkers."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 3
        self.draw_barrier()

    def draw_barrier(self):
        self.image.fill((0, 0, 0, 0))  # Clear
        # Draw a blocky green barrier
        color = (0, 150, 0) if self.health > 1 else (0, 60, 0)
        for i in range(4):
            for j in range(4):
                if random.random() > 0.1:  # Slightly irregular
                    pygame.draw.rect(self.image, color, (i * 10, j * 10, 10, 10))

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            self.draw_barrier()


# --- Core Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        self._draw_ship()
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.speed = 7

    def _draw_ship(self):
        points = [(20, 0), (40, 30), (30, 25), (10, 25), (0, 30)]
        pygame.draw.polygon(self.image, CYAN, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, color, level_speed):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((35, 30), pygame.SRCALPHA)
        self._draw_alien()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.base_speed = level_speed

    def _draw_alien(self):
        offsets = [(10, 5), (25, 5), (5, 15), (30, 15), (10, 25), (25, 25)]
        for ox, oy in offsets:
            pygame.draw.rect(self.image, self.color, (ox, oy, 15, 10))
        pygame.draw.rect(self.image, WHITE, (5, 5, 30, 25), 1)

    def update(self, move_down=False):
        if move_down:
            self.rect.y += 30
        self.rect.x += self.base_speed * self.direction


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Star:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.5, 1.5)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT: self.y = 0; self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, (60, 60, 80), (int(self.x), int(self.y)), self.size)


# --- Main Game Engine ---

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NEON INVADERS: OVERDRIVE")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("Arial", 64, bold=True)
    font_small = pygame.font.SysFont("Arial", 24, bold=True)

    # Game State
    level = 1
    score = 0
    shake_timer = 0
    running = True
    game_over = False

    def spawn_level(lvl):
        aliens = pygame.sprite.Group()
        rows, cols = 5, 10
        # Speed increases with level
        speed = 1 + (lvl * 0.5)
        for r in range(rows):
            for c in range(cols):
                color = [GREEN, YELLOW, MAGENTA, RED, CYAN][(r + lvl) % 5]
                a = Alien(100 + c * 55, 50 + r * 45, color, speed)
                aliens.add(a)

        barriers = pygame.sprite.Group()
        for i in range(4):
            for j in range(3):
                b = Barrier(120 + i * 160, 450 + j * 40)
                barriers.add(b)
        return aliens, barriers

    # Initialize Objects
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    stars = [Star() for _ in range(100)]

    aliens, barriers = spawn_level(level)
    all_sprites.add(aliens)
    all_sprites.add(barriers)

    while running:
        # --- 1. Input & Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    b = Bullet(player.rect.centerx, player.rect.top, YELLOW, -10)
                    bullets.add(b)
                    all_sprites.add(b)
                if event.key == pygame.K_r and game_over:
                    run_game()
                    return

        if not game_over:
            # --- 2. Logic ---
            all_sprites.update()
            particles.update()
            for s in stars: s.update()

            # Alien Movement Logic
            move_down = False
            for a in aliens:
                if a.rect.right >= WIDTH or a.rect.left <= 0:
                    move_down = True
                    break
            if move_down:
                for a in aliens:
                    a.direction *= -1
                    if move_down: a.rect.y += 30

            # Collision: Player Bullets -> Aliens
            hits = pygame.sprite.groupcollide(aliens, bullets, True, True)
            for hit in hits:
                score += 100
                shake_timer = 5  # Trigger screen shake
                for _ in range(10):  # Explosion particles
                    p = Particle(hit.rect.centerx, hit.rect.centery, hit.color)
                    particles.add(p)
                    all_sprites.add(p)

            # Collision: Bullets -> Barriers
            pygame.sprite.groupcollide(barriers, bullets, False, True)
            pygame.sprite.groupcollide(barriers, enemy_bullets, False, True)

            # Collision: Bullets -> Barriers (Manual check for barrier health)
            for b in barriers:
                if pygame.sprite.spritecollideany(b, bullets):
                    b.hit()
                if pygame.sprite.spritecollideany(b, enemy_bullets):
                    b.hit()

            # Enemy Shooting
            if aliens and random.random() < (0.01 + (level * 0.005)):
                shooter = random.choice(aliens.sprites())
                eb = Bullet(shooter.rect.centerx, shooter.rect.bottom, RED, 5 + level)
                enemy_bullets.add(eb)
                all_sprites.add(eb)

            # Collision: Player Death
            if pygame.sprite.spritecollide(player, enemy_bullets, True) or \
                    pygame.sprite.spritecollide(player, aliens, False):
                game_over = True
                shake_timer = 20

            # Check if Level Cleared
            if not aliens:
                level += 1
                aliens, barriers = spawn_level(level)
                all_sprites.add(aliens)
                all_sprites.add(barriers)

            # Check if Aliens reached bottom
            for a in aliens:
                if a.rect.bottom >= player.rect.top:
                    game_over = True

        # --- 3. Rendering ---
        # Screen Shake logic
        render_offset = [0, 0]
        if shake_timer > 0:
            render_offset = [random.randint(-5, 5), random.randint(-5, 5)]
            shake_timer -= 1

        screen.fill(BLACK)

        # Draw stars with offset
        for s in stars:
            s.draw(screen)

        # Draw everything with shake offset
        # We create a temporary surface to apply the shake to everything but the UI
        game_surface = pygame.Surface((WIDTH, HEIGHT))
        game_surface.fill(BLACK)

        # Re-draw logic for game_surface
        for s in stars: s.draw(game_surface)
        for sprite in all_sprites:
            game_surface.blit(sprite.image, sprite.rect)
        for sprite in particles:
            game_surface.blit(sprite.image, sprite.rect)

        screen.blit(game_surface, render_offset)

        # UI (Drawn directly to screen, no shake)
        score_lbl = font_small.render(f"SCORE: {score}  |  LEVEL: {level}", True, WHITE)
        screen.blit(score_lbl, (15, 15))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            msg = font_large.render("GAME OVER", True, RED)
            retry = font_small.render("PRESS 'R' TO RESTART", True, WHITE)
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            screen.blit(retry, retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_game()
