# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library. (Then run error fix for: TypeError: invalid color argument)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Huihui-Qwen3-Next-80B-A3B-Instruct-abliterated.Q8_0.gguf



import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 30
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
BULLET_WIDTH = 5
BULLET_HEIGHT = 15
PLAYER_SPEED = 5
ENEMY_SPEED = 1
BULLET_SPEED = 7
ENEMY_DROP_SPEED = 10
ENEMY_ROWS = 5
ENEMY_COLS = 10
ENEMY_GAP = 15
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()


class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = PLAYER_SPEED
        self.color = GREEN
        self.lives = 3
        self.score = 0

    def draw(self):
        # Draw player as a triangle
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        return Bullet(self.x + self.width // 2 - BULLET_WIDTH // 2, self.y, direction=1)

    def reset(self):
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20


class Bullet:
    def __init__(self, x, y, direction=1):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = BULLET_SPEED
        self.color = WHITE
        self.direction = direction  # 1 for upward (player), -1 for downward (enemy)

    def update(self):
        self.y -= self.speed * self.direction  # Move in direction

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return self.y < -self.height or self.y > SCREEN_HEIGHT + self.height


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.speed = ENEMY_SPEED
        self.color = RED
        self.alive = True

    def draw(self):
        # Draw enemy as a simple rectangle
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add enemy details
        pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 8, self.width - 16, self.height - 16))

    def move(self, direction):
        self.x += self.speed * direction

    def drop(self):
        self.y += ENEMY_DROP_SPEED

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.enemy_direction = 1  # 1 for right, -1 for left
        self.enemy_drop = False
        self.game_over = False
        self.wave_number = 1
        self.create_enemies()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)

    def create_enemies(self):
        self.enemies = []
        start_x = (SCREEN_WIDTH - (ENEMY_COLS * (ENEMY_WIDTH + ENEMY_GAP))) // 2
        start_y = 50

        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * (ENEMY_WIDTH + ENEMY_GAP)
                y = start_y + row * (ENEMY_HEIGHT + ENEMY_GAP)
                self.enemies.append(Enemy(x, y))

    def update(self):
        if self.game_over:
            return

        # Move all bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # Check for bullet-enemy collisions (player bullets hitting enemies)
        for bullet in self.bullets[:]:
            # Only player bullets (direction=1) should damage enemies
            if bullet.direction == 1:  # Player bullet
                for enemy in self.enemies:
                    if enemy.alive and bullet.x < enemy.x + enemy.width and bullet.x + bullet.width > enemy.x and \
                            bullet.y < enemy.y + enemy.height and bullet.y + bullet.height > enemy.y:
                        enemy.alive = False
                        self.bullets.remove(bullet)
                        self.player.score += 10
                        break

        # Check if all enemies are dead
        if all(not enemy.alive for enemy in self.enemies):
            self.wave_number += 1
            self.create_enemies()
            # Increase enemy speed with each wave
            for enemy in self.enemies:
                enemy.speed = ENEMY_SPEED + (self.wave_number - 1) * 0.2

        # Move enemies
        move_down = False
        max_x = max(enemy.x for enemy in self.enemies if enemy.alive)
        min_x = min(enemy.x for enemy in self.enemies if enemy.alive)

        if max_x + ENEMY_WIDTH >= SCREEN_WIDTH or min_x <= 0:
            self.enemy_direction *= -1
            move_down = True

        for enemy in self.enemies:
            if enemy.alive:
                enemy.move(self.enemy_direction)
                if move_down:
                    enemy.drop()

        # Check if enemies reached the bottom
        for enemy in self.enemies:
            if enemy.alive and enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                break

        # Random enemy shooting (enemy bullets are fired downward)
        alive_enemies = [enemy for enemy in self.enemies if enemy.alive]
        if alive_enemies and random.random() < 0.01:  # 1% chance per frame
            shooter = random.choice(alive_enemies)
            # Create bullet from enemy position (going downward)
            enemy_bullet = Bullet(shooter.x + shooter.width // 2 - BULLET_WIDTH // 2,
                                  shooter.y + shooter.height, direction=-1)
            self.bullets.append(enemy_bullet)

        # Check for enemy bullets hitting player
        for bullet in self.bullets[:]:
            # Only enemy bullets (direction=-1) should damage player
            if bullet.direction == -1:  # Enemy bullet
                if (bullet.x < self.player.x + self.player.width and
                        bullet.x + bullet.width > self.player.x and
                        bullet.y < self.player.y + self.player.height and
                        bullet.y + bullet.height > self.player.y):
                    self.player.lives -= 1
                    self.bullets.remove(bullet)
                    if self.player.lives <= 0:
                        self.game_over = True
                    else:
                        self.player.reset()

    def draw(self):
        screen.fill(BLACK)

        # Draw player
        self.player.draw()

        # Draw enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw()

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()

        # Draw UI
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        wave_text = self.font.render(f"Wave: {self.wave_number}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(wave_text, (10, 70))

        # Game over screen
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press SPACE to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                       SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()

    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemy_direction = 1
        self.enemy_drop = False
        self.game_over = False
        self.wave_number = 1
        self.create_enemies()


def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_over:
                    game.reset()
                elif event.key == pygame.K_SPACE and not game.game_over:
                    # Player shoots
                    bullet = game.player.shoot()
                    game.bullets.append(bullet)

        # Get key presses for player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.player.move_left()
        if keys[pygame.K_RIGHT]:
            game.player.move_right()

        # Update game state
        game.update()

        # Draw everything
        game.draw()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
