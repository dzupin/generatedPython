# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-35B-A3B-UD-Q8_K_XL.gguf  --mmproj /AI/models/Qwen3.5-35B-A3B_mmproj-BF16.gguf

import pygame
import random
import sys

# --- Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG_TOP = (10, 10, 30)
COLOR_BG_BOTTOM = (20, 20, 60)
COLOR_PLAYER = (0, 255, 255)  # Cyan
COLOR_PLAYER_DARK = (0, 150, 150)
COLOR_BULLET_PLAYER = (255, 255, 0)  # Yellow
COLOR_BULLET_ENEMY = (255, 100, 100)  # Red/Pink
COLOR_ALIEN_1 = (0, 255, 100)  # Green
COLOR_ALIEN_2 = (255, 255, 0)  # Yellow
COLOR_ALIEN_3 = (255, 100, 0)  # Orange
COLOR_TEXT = (255, 255, 255)
COLOR_PARTICLE = (255, 255, 255)

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_BASE_SPEED = 1
ALIEN_DROP_HEIGHT = 30
FIRE_COOLDOWN = 25  # Frames


# --- Helper Functions ---

def create_gradient_surface(width, height, top_color, bottom_color):
    """Creates a surface with a vertical linear gradient."""
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / height)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / height)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / height)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    return surf


def create_alien_surface(pixel_map, color):
    """
    Creates a sprite surface from a binary pixel map.
    1 = color, 0 = transparent.
    """
    pixel_size = 4
    rows = len(pixel_map)
    cols = len(pixel_map[0]) if rows > 0 else 0

    w = cols * pixel_size
    h = rows * pixel_size

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for r in range(rows):
        for c in range(cols):
            if pixel_map[r][c] == 1:
                rect = pygame.Rect(c * pixel_size, r * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(surf, color, rect)
    return surf


# Alien Pixel Maps (1 = draw, 0 = empty)
ALIEN_MAP_1 = [
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0]
]

ALIEN_MAP_2 = [
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1]
]

ALIEN_MAP_3 = [
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0]
]

# Pre-generate Aliens Surfaces
ALien_1_Surf = create_alien_surface(ALIEN_MAP_1, COLOR_ALIEN_1)
ALIEN_2_Surf = create_alien_surface(ALIEN_MAP_2, COLOR_ALIEN_2)
ALIEN_3_Surf = create_alien_surface(ALIEN_MAP_3, COLOR_ALIEN_3)


# --- Classes ---

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((random.randint(3, 6), random.randint(3, 6)))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = (random.uniform(-2, 2), random.uniform(-2, 2))
        self.life = random.randint(10, 20)
        self.color = color

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        self.life -= 1
        self.image.set_alpha(self.life * 12)
        if self.life <= 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        # Draw Player Shape
        pygame.draw.polygon(self.image, COLOR_PLAYER, [(20, 0), (0, 30), (40, 30)])
        pygame.draw.polygon(self.image, COLOR_PLAYER_DARK, [(20, 5), (5, 25), (35, 25)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown == 0:
            self.cooldown = FIRE_COOLDOWN
            bullet = Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED, COLOR_BULLET_PLAYER)
            return bullet
        return None


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, alien_type):
        super().__init__()
        self.alien_type = alien_type
        if alien_type == 1:
            self.image = ALien_1_Surf
        elif alien_type == 2:
            self.image = ALIEN_2_Surf
        else:
            self.image = ALIEN_3_Surf

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.points = 0
        if alien_type == 1:
            self.points = 30
        elif alien_type == 2:
            self.points = 20
        else:
            self.points = 10

    def update(self):
        pass  # Movement handled in Game Loop for group sync


class Star:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, SCREEN_HEIGHT)

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -10
        self.speed = random.uniform(0.5, 2.0)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(50, 200)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.reset()


# --- Main Game Class ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PyInvaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 40)

        self.reset_game()
        self.background = create_gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)
        self.stars = [Star() for _ in range(50)]

    def reset_game(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        self.score = 0
        self.level = 1
        self.alien_move_speed = ALIEN_BASE_SPEED
        self.alien_dx = self.alien_move_speed
        self.alien_dy = ALIEN_DROP_HEIGHT
        self.alien_direction = 1  # 1 = right, -1 = left
        self.game_over = False
        self.level_active = True
        self.spawn_aliens()

    def spawn_aliens(self):
        self.enemies.empty()
        self.bullets.empty()
        self.all_sprites.add(self.player)

        rows = 5
        cols = 10
        spacing_x = 50
        spacing_y = 50
        start_x = (SCREEN_WIDTH - (cols * spacing_x)) // 2
        start_y = 50

        for r in range(rows):
            for c in range(cols):
                alien_type = (r % 3) + 1
                x = start_x + c * spacing_x
                y = start_y + r * spacing_y
                alien = Alien(x, y, alien_type)
                self.enemies.add(alien)

    def create_explosion(self, x, y):
        for _ in range(10):
            self.particles.add(Particle(x, y, random.choice([COLOR_BULLET_PLAYER, COLOR_ALIEN_1, COLOR_ALIEN_2])))

    def check_collisions(self):
        # Bullets vs Aliens
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += hit.points
            self.create_explosion(hit.rect.centerx, hit.rect.centery)

        # Bullets vs Player
        if pygame.sprite.spritecollide(self.player, self.bullets, True):
            self.create_explosion(self.player.rect.centerx, self.player.rect.centery)
            return False  # Player died

        # Aliens vs Player (or reaching bottom)
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                return False

        # Alien Bullets (Simulated)
        # In this version, aliens shoot randomly
        if random.random() < 0.02 + (self.level * 0.005) and len(self.enemies) > 0:
            if self.enemies:
                shooter = random.choice(list(self.enemies))
                bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, BULLET_SPEED, COLOR_BULLET_ENEMY)
                self.bullets.add(bullet)

        return True

    def update_aliens(self):
        if not self.level_active: return

        # Check edges
        move_down = False
        for enemy in self.enemies:
            if enemy.rect.right >= SCREEN_WIDTH - 10 and self.alien_direction > 0:
                move_down = True
                break
            if enemy.rect.left <= 10 and self.alien_direction < 0:
                move_down = True
                break

        if move_down:
            self.alien_direction *= -1
            for enemy in self.enemies:
                enemy.rect.y += self.alien_dy
        else:
            for enemy in self.enemies:
                enemy.rect.x += (self.alien_move_speed * self.alien_direction)

        # Increase speed as enemies die
        self.alien_move_speed = ALIEN_BASE_SPEED + (50 - len(self.enemies)) / 10

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))

        # Draw Stars
        for star in self.stars:
            s = pygame.Surface((star.size, star.size))
            s.set_alpha(star.alpha)
            s.fill(COLOR_TEXT)
            self.screen.blit(s, (star.x, star.y))
            star.update()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset_game()
                        else:
                            bullet = self.player.shoot()
                            if bullet:
                                self.bullets.add(bullet)
                    elif event.key == pygame.K_r:
                        if self.game_over:
                            self.reset_game()

            if not self.game_over:
                # Update
                self.player.update()
                self.bullets.update()
                self.particles.update()
                self.update_aliens()

                collision_active = self.check_collisions()

                if not collision_active:
                    self.game_over = True

                if len(self.enemies) == 0 and self.game_over == False:
                    self.level += 1
                    self.spawn_aliens()
                    self.alien_move_speed = min(self.alien_move_speed + 0.5, 5)  # Cap speed

            # Drawing
            self.draw_background()

            self.all_sprites.draw(self.screen)
            self.bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            self.particles.draw(self.screen)

            # UI
            score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
            level_text = self.font.render(f"Level: {self.level}", True, COLOR_TEXT)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (SCREEN_WIDTH - 120, 10))

            if self.game_over:
                # Draw semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                msg = "GAME OVER"
                sub_msg = "Press SPACE or R to Restart"
                text = self.big_font.render(msg, True, COLOR_TEXT)
                sub = self.font.render(sub_msg, True, (200, 200, 200))

                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

                self.screen.blit(text, text_rect)
                self.screen.blit(sub, sub_rect)

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
