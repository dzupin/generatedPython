import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning,
                       message="Your system is avx2 capable but pygame was not built with support for it.")

import pygame
import random
import sys
from pygame import mixer



# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


# Player
class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.lives = 3
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Enemy
class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 1

    def update(self):
        self.rect.x += self.speed * self.direction

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Bullet
class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Enemy Bullet
class EnemyBullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 255, 0))  # Yellow
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 5

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.enemy_shoot_chance = 0.01
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.spawn_enemies()

        # Initialize sounds without loading actual files
        # This creates dummy sound objects that won't produce errors
        self.sound_enabled = False
        try:
            # Create empty sounds
            self.shoot_sound = pygame.mixer.Sound(buffer=bytearray(44))
            self.explosion_sound = pygame.mixer.Sound(buffer=bytearray(44))
            # Set volume to 0 to avoid any potential noise
            self.shoot_sound.set_volume(0)
            self.explosion_sound.set_volume(0)
            self.sound_enabled = True
        except:
            # If sound creation fails, we'll skip playing sounds
            print("Sound initialization failed. Sound effects disabled.")

    def spawn_enemies(self):
        for row in range(5):
            for col in range(10):
                enemy = Enemy(col * 70 + 50, row * 50 + 50)
                self.enemies.append(enemy)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.top))
                    if self.sound_enabled:
                        self.shoot_sound.play()
                if event.key == pygame.K_RETURN and self.game_over:
                    self.__init__()
        return True

    def run_logic(self):
        if not self.game_over:
            self.player.update()

            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.rect.bottom < 0:
                    self.bullets.remove(bullet)
                else:
                    for enemy in self.enemies[:]:
                        if bullet.rect.colliderect(enemy.rect):
                            self.bullets.remove(bullet)
                            self.enemies.remove(enemy)
                            self.player.score += 10
                            if self.sound_enabled:
                                self.explosion_sound.play()
                            break

            # Enemies movement
            move_down = False
            for enemy in self.enemies:
                enemy.update()
                if enemy.rect.right > SCREEN_WIDTH or enemy.rect.left < 0:
                    move_down = True

                # Enemy shooting
                if random.random() < self.enemy_shoot_chance:
                    self.enemy_bullets.append(EnemyBullet(enemy.rect.centerx, enemy.rect.bottom))

            if move_down:
                for enemy in self.enemies:
                    enemy.direction *= -1
                    enemy.rect.y += 20

            # Enemy bullets
            for bullet in self.enemy_bullets[:]:
                bullet.update()
                if bullet.rect.top > SCREEN_HEIGHT:
                    self.enemy_bullets.remove(bullet)
                elif bullet.rect.colliderect(self.player.rect):
                    self.enemy_bullets.remove(bullet)
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True

            # Check if any enemy reached the bottom
            for enemy in self.enemies:
                if enemy.rect.bottom > SCREEN_HEIGHT - 50:
                    self.game_over = True

            # Check if all enemies are destroyed
            if len(self.enemies) == 0:
                self.spawn_enemies()
                self.enemy_shoot_chance += 0.005

    def display_frame(self):
        screen.fill(BLACK)

        # Draw player, enemies, bullets
        self.player.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for bullet in self.enemy_bullets:
            bullet.draw(screen)

        # Draw score and lives
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press Enter to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))

        pygame.display.flip()


def main():
    pygame.init()
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        running = game.process_events()
        game.run_logic()
        game.display_frame()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()