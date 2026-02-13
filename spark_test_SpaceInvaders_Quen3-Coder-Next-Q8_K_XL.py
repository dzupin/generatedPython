# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1  --model  /AI/models/stepfun-ai_Step-3.5-Flash-IQ4_XS-00001-of-00003.gguf

import pygame
import math
import random

# --- Initialization ---
pygame.init()
pygame.font.init()

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python Space Invaders")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Game Clock
clock = pygame.time.Clock()
FPS = 60


# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple ship shape using a surface
        self.image = pygame.Surface((40, 30))
        self.image.fill(GREEN)
        # Draw a simple triangle shape for the ship
        pygame.draw.polygon(self.image, WHITE, [(20, 0), (40, 30), (0, 30)])

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 7
        self.lives = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 25))
        self.image.fill(RED)
        # Draw simple alien face
        pygame.draw.rect(self.image, BLACK, (5, 5, 5, 5))  # Eye
        pygame.draw.rect(self.image, BLACK, (20, 5, 5, 5))  # Eye
        pygame.draw.rect(self.image, BLACK, (10, 15, 10, 3))  # Mouth

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Movement variables
        self.move_right = True
        self.move_speed_x = 2
        self.move_speed_y = 0

    def update(self):
        self.rect.x += self.move_speed_x
        self.rect.y += self.move_speed_y


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        # Remove bullet if it goes off screen
        if self.rect.bottom < 0:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Random velocity for explosion effect
        self.vx = random.randint(-3, 3)
        self.vy = random.randint(-3, 3)
        self.life = 30  # Frames to live

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()


# --- Game Functions ---

def create_enemies():
    enemies = pygame.sprite.Group()
    rows = 4
    cols = 8
    start_x = 50
    start_y = 50

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * 60
            y = start_y + row * 50
            enemy = Enemy(x, y)
            enemies.add(enemy)
    return enemies


def main():
    running = True
    score = 0
    game_over = False
    winner = False

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    enemies = create_enemies()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)
    all_sprites.add(enemies)

    # Enemy movement timer (simple way to slow down enemies relative to player)
    enemy_move_timer = 0
    ENEMY_MOVE_INTERVAL = 30  # Lower is faster

    while running:
        clock.tick(FPS)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not winner:
                    bullet = player.shoot()
                    bullets.add(bullet)
                    all_sprites.add(bullet)
                if (game_over or winner) and event.key == pygame.K_r:
                    # Restart Game
                    return main()

        if game_over or winner:
            continue

        # --- Updates ---
        player.update()
        bullets.update()
        particles.update()

        # Enemy Logic
        enemy_move_timer += 1

        # Move enemies every X frames
        if enemy_move_timer > ENEMY_MOVE_INTERVAL:
            enemy_move_timer = 0
            hit_edge = False

            # Check edges
            for enemy in enemies:
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    hit_edge = True
                    break

            # Change direction and move down
            if hit_edge:
                for enemy in enemies:
                    enemy.move_right = not enemy.move_right
                    enemy.rect.y += 20  # Drop down
                    # Reset speed direction
                    enemy.move_speed_x = 2 if enemy.move_right else -2

            # Move forward
            for enemy in enemies:
                if not hit_edge:  # Only change X if not dropping
                    enemy.move_speed_x = 2 if enemy.move_right else -2
                enemy.update()

            # Check if enemies reached the player level
            for enemy in enemies:
                if enemy.rect.bottom >= player.rect.top - 10:
                    game_over = True

        # Collision Detection: Bullet hits Enemy
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 10
            # Create explosion particles
            for i in range(8):
                particle = Particle(hit.rect.centerx, hit.rect.centery)
                particles.add(particle)
                all_sprites.add(particle)

        # Check Win Condition
        if len(enemies) == 0:
            winner = True

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw Grid Lines (Optional, for retro feel)
        pygame.draw.line(screen, (50, 50, 50), (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50))

        all_sprites.draw(screen)
        particles.draw(screen)

        # UI Text
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            font_large = pygame.font.SysFont("Arial", 60)
            text = font_large.render("GAME OVER", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        elif winner:
            font_large = pygame.font.SysFont("Arial", 60)
            text = font_large.render("YOU WIN!", True, GREEN)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
