# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# 1 Shot (fix spacebar not shooting bug)
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
pygame.display.set_caption("Neon Space Invaders")
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
BLUE = (0, 200, 255)
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)  # DEFINED HERE TO FIX ERROR


# --- Helper Functions ---

def draw_text(surface, text, size, color, x, y, align="center"):
    font = pygame.font.SysFont("Arial", size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.centerx = x
        text_rect.top = y
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def draw_health_bar(surface, x, y, width, height, current, max):
    fill = (current / max) * width
    outline_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


# --- Classes ---

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 3)
        self.brightness = random.randint(50, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        color_val = int(self.brightness)
        pygame.draw.circle(surface, (color_val, color_val, color_val), (self.x, self.y), self.size)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        # Draw Ship
        pygame.draw.polygon(self.image, GREEN, [(20, 0), (40, 30), (0, 30)])
        # Engine flame
        pygame.draw.polygon(self.image, ORANGE, [(10, 30), (20, 40), (30, 30)])

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 7
        self.lives = 3
        self.shield = 0
        self.shield_time = 0
        self.power_level = 1
        self.power_time = 0
        self.last_shot = 0
        self.shoot_delay = 250  # ms

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

        # Shooting Logic (FIXED)
        if keys[pygame.K_SPACE]:
            bullets = self.shoot()
            for b in bullets:
                all_sprites.add(b)
                bullets_group.add(b)

        # Power-up Timers
        if self.power_level > 1:
            if pygame.time.get_ticks() - self.power_time > 10000:  # 10 seconds
                self.power_level = 1

        if self.shield > 0:
            if pygame.time.get_ticks() - self.shield_time > 8000:  # 8 seconds
                self.shield = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        current_delay = 150 if self.power_level == 3 else 250  # Rapid fire

        if now - self.last_shot > current_delay:
            self.last_shot = now

            if self.power_level == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, 0, -10, BLUE)
                return [bullet]
            elif self.power_level == 2:  # Spread Shot
                b1 = Bullet(self.rect.centerx - 10, self.rect.top, -2, -10, PURPLE)
                b2 = Bullet(self.rect.centerx, self.rect.top, 0, -10, PURPLE)
                b3 = Bullet(self.rect.centerx + 10, self.rect.top, 2, -10, PURPLE)
                return [b1, b2, b3]
            else:  # Rapid Fire (Single stream)
                bullet = Bullet(self.rect.centerx, self.rect.top, 0, -15, YELLOW)
                return [bullet]
        return []

    def get_powerup(self, type):
        if type == 'shield':
            self.shield = 1
            self.shield_time = pygame.time.get_ticks()
        elif type == 'spread':
            self.power_level = 2
            self.power_time = pygame.time.get_ticks()
        elif type == 'rapid':
            self.power_level = 3
            self.power_time = pygame.time.get_ticks()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type_score):
        super().__init__()
        self.type_score = type_score  # Determines color/shape
        self.image = pygame.Surface((35, 30), pygame.SRCALPHA)

        if type_score == 1:  # Top Row (Fast, Red)
            self.image.fill(RED)
            pygame.draw.circle(self.image, BLACK, (10, 10), 4)
            pygame.draw.circle(self.image, BLACK, (25, 10), 4)
            pygame.draw.rect(self.image, BLACK, (10, 20, 15, 5))
        elif type_score == 2:  # Middle (Green)
            self.image.fill(GREEN)
            pygame.draw.rect(self.image, BLACK, (5, 5, 10, 10))
            pygame.draw.rect(self.image, BLACK, (20, 5, 10, 10))
            pygame.draw.rect(self.image, BLACK, (10, 20, 15, 3))
        else:  # Bottom (Blue)
            self.image.fill(BLUE)
            pygame.draw.polygon(self.image, BLACK, [(5, 25), (15, 15), (25, 25)])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_right = True
        self.base_speed = 1

    def update(self):
        self.rect.x += self.move_speed_x
        self.rect.y += self.move_speed_y


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, color):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vx = vx
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.size = random.randint(2, 5)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(20, 50)
        self.color = color

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()
        else:
            # Fade out effect
            alpha = int(255 * (self.life / 50))
            self.image.set_alpha(alpha)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['shield', 'spread', 'rapid'])
        self.image = pygame.Surface((25, 25))

        if self.type == 'shield':
            self.image.fill(BLUE)
            pygame.draw.circle(self.image, WHITE, (12, 12), 5)
        elif self.type == 'spread':
            self.image.fill(PURPLE)
            pygame.draw.polygon(self.image, WHITE, [(12, 2), (2, 23), (22, 23)])
        else:  # rapid
            self.image.fill(YELLOW)
            pygame.draw.rect(self.image, WHITE, (8, 5, 9, 15))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# --- Main Game Logic ---

def spawn_powerup(x, y):
    if random.random() < 0.15:  # 15% chance
        return PowerUp(x, y)
    return None


def main():
    running = True
    game_over = False
    winner = False
    score = 0
    high_score = 0
    screen_shake = 0

    # Background Stars
    stars = [Star() for _ in range(50)]

    # Sprite Groups
    global all_sprites, bullets_group  # Make global for player access
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    def init_level():
        enemies.empty()
        bullets_group.empty()
        enemy_bullets.empty()
        powerups.empty()
        # Keep player in all_sprites, clear others
        for enemy in enemies:
            enemies.remove(enemy)

        rows = 4
        cols = 8
        start_x = 50
        start_y = 50

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * 60
                y = start_y + row * 50
                # Determine enemy type based on row
                type = 1 if row == 0 else (2 if row < 3 else 3)
                enemy = Enemy(x, y, type)
                enemies.add(enemy)
                all_sprites.add(enemy)

    init_level()

    while running:
        clock.tick(FPS)

        # Screen Shake Logic
        if screen_shake > 0:
            screen_shake -= 1
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
            screen.fill(BLACK)
            pygame.draw.rect(screen, (20, 20, 20), (shake_x, shake_y, SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            screen.fill(BLACK)
            # Draw Stars
            for star in stars:
                star.update()
                star.draw(screen)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if (game_over or winner) and event.key == pygame.K_r:
                    return main()

        if game_over or winner:
            # UI Overlay
            draw_text(screen, "GAME OVER" if game_over else "YOU WIN!", 60, RED if game_over else GREEN,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, f"Final Score: {score}", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            draw_text(screen, "Press 'R' to Restart", 20, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

            # Draw static background elements behind game over
            all_sprites.draw(screen)
            bullets_group.draw(screen)
            powerups.draw(screen)
            pygame.display.flip()
            continue

        # --- Updates ---
        player.update()
        bullets_group.update()
        enemy_bullets.update()
        particles.update()
        powerups.update()

        # Enemy Logic
        # Increase difficulty based on score
        enemy_speed_multiplier = 1 + (score / 500)
        hit_edge = False

        for enemy in enemies:
            enemy.move_speed_x = (2 * enemy_speed_multiplier) if enemy.move_right else (-2 * enemy_speed_multiplier)
            enemy.move_speed_y = 0

            if enemy.rect.right >= SCREEN_WIDTH - 10 or enemy.rect.left <= 10:
                hit_edge = True

        if hit_edge:
            for enemy in enemies:
                enemy.move_right = not enemy.move_right
                enemy.rect.y += 20
                enemy.move_speed_x = (2 * enemy_speed_multiplier) if enemy.move_right else (-2 * enemy_speed_multiplier)

        # Enemy Shooting
        if len(enemies) > 0 and random.randint(1, 60) < (2 + score // 100):  # Shoots get more frequent
            shooter = random.choice(enemies.sprites())
            b = Bullet(shooter.rect.centerx, shooter.rect.bottom, 0, 5, RED)
            enemy_bullets.add(b)
            all_sprites.add(b)

        # Collision: Player Bullet hits Enemy
        hits = pygame.sprite.groupcollide(bullets_group, enemies, True, True)
        for hit in hits:
            score += 10 * (hits[hit][0].type_score)  # Higher score for harder enemies
            # Explosion
            for _ in range(10):
                p = Particle(hit.rect.centerx, hit.rect.centery, hits[hit][0].image.get_at((10, 10)))
                particles.add(p)

            # Chance for Powerup
            pu = spawn_powerup(hit.rect.centerx, hit.rect.centery)
            if pu:
                powerups.add(pu)
                all_sprites.add(pu)

        # Collision: Enemy Bullet hits Player
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            screen_shake = 15
            if player.shield > 0:
                player.shield = 0
                # Shield break effect
                for _ in range(15):
                    p = Particle(player.rect.centerx, player.rect.centery, BLUE)
                    particles.add(p)
            else:
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True
                # Player hit effect
                for _ in range(15):
                    p = Particle(player.rect.centerx, player.rect.centery, GREEN)
                    particles.add(p)

        # Collision: Player hits Powerup
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            player.get_powerup(hit.type)
            score += 50  # Bonus for collecting
            # Collect effect
            for _ in range(8):
                p = Particle(hit.rect.centerx, hit.rect.centery, YELLOW)
                particles.add(p)

        # Collision: Enemy hits Player (Body collision)
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            screen_shake = 20
            player.lives = 0
            game_over = True

        # Check Win Condition
        if len(enemies) == 0:
            winner = True

        # --- Drawing ---
        all_sprites.draw(screen)
        bullets_group.draw(screen)  # Draw bullets specifically
        powerups.draw(screen)
        particles.draw(screen)

        # Draw Player UI
        draw_text(screen, f"SCORE: {score}", 22, WHITE, SCREEN_WIDTH // 2, 10)
        draw_text(screen, f"HIGH: {max(score, high_score)}", 18, GRAY, SCREEN_WIDTH - 100, 15)

        # Lives & Shield
        draw_text(screen, "LIVES:", 20, WHITE, 10, SCREEN_HEIGHT - 35, "left")
        for i in range(player.lives):
            pygame.draw.rect(screen, GREEN, (100 + (i * 35), SCREEN_HEIGHT - 30, 25, 15))

        if player.shield > 0:
            shield_pct = 1 - ((pygame.time.get_ticks() - player.shield_time) / 8000)
            draw_text(screen, "SHIELD", 15, BLUE, 10, SCREEN_HEIGHT - 55, "left")
            pygame.draw.rect(screen, BLUE, (70, SCREEN_HEIGHT - 55, 20 * shield_pct, 5))

        if player.power_level > 1:
            power_pct = 1 - ((pygame.time.get_ticks() - player.power_time) / 10000)
            p_name = "SPREAD" if player.power_level == 2 else "RAPID"
            draw_text(screen, p_name, 15, PURPLE if player.power_level == 2 else YELLOW, 70, 40)
            pygame.draw.rect(screen, PURPLE if player.power_level == 2 else YELLOW, (70, 60, 100 * power_pct, 5))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
