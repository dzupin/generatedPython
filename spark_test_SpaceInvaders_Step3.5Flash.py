# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1  --model  /AI/models/stepfun-ai_Step-3.5-Flash-IQ4_XS-00001-of-00003.gguf

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 70, 200)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Load fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)


class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = 5
        self.color = GREEN
        self.lives = 3
        self.score = 0
        self.bullets = []
        self.cooldown = 0
        self.cooldown_time = 15  # frames between shots

    def draw(self):
        # Draw player ship (triangle shape)
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW,
                             (bullet[0], bullet[1], 4, 10))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown == 0:
            self.bullets.append([self.x + self.width // 2 - 2, self.y])
            self.cooldown = self.cooldown_time

    def update_bullets(self):
        # Move bullets up
        for bullet in self.bullets[:]:
            bullet[1] -= 7
            if bullet[1] < 0:
                self.bullets.remove(bullet)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Alien:
    def __init__(self, x, y, alien_type):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.alien_type = alien_type  # 0, 1, or 2 for different alien types
        self.color = self.get_color()
        self.bullets = []
        self.shoot_chance = 0.001  # Chance to shoot each frame

    def get_color(self):
        colors = [PURPLE, BLUE, RED]
        return colors[self.alien_type]

    def draw(self):
        # Draw alien based on type
        if self.alien_type == 0:
            # Crab-like alien
            pygame.draw.rect(screen, self.color,
                             (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK,
                             (self.x + 10, self.y + 5, 5, 5))
            pygame.draw.rect(screen, BLACK,
                             (self.x + self.width - 15, self.y + 5, 5, 5))
        elif self.alien_type == 1:
            # Squid-like alien
            points = [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height),
                (self.x + self.width, self.y + self.height // 2)
            ]
            pygame.draw.polygon(screen, self.color, points)
        else:  # type 2
            # Octopus-like alien
            pygame.draw.rect(screen, self.color,
                             (self.x + 5, self.y, self.width - 10, self.height))
            pygame.draw.rect(screen, BLACK,
                             (self.x + 10, self.y + 10, 5, 5))
            pygame.draw.rect(screen, BLACK,
                             (self.x + self.width - 15, self.y + 10, 5, 5))

    def update(self, dx, dy):
        self.x += dx
        self.y += dy

        # Random shooting
        if random.random() < self.shoot_chance:
            self.bullets.append([self.x + self.width // 2 - 2, self.y + self.height])

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] += 4
            if bullet[1] > SCREEN_HEIGHT:
                self.bullets.remove(bullet)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class AlienGrid:
    def __init__(self):
        self.aliens = []
        self.direction = 1  # 1 for right, -1 for left
        self.move_speed = 1
        self.move_down_distance = 20
        self.shoot_cooldown = 0
        self.create_grid()

    def create_grid(self):
        rows = 4
        cols = 8
        spacing_x = 60
        spacing_y = 50
        start_x = 50
        start_y = 50

        for row in range(rows):
            for col in range(cols):
                alien_type = row // 2  # Different types in different rows
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.aliens.append(Alien(x, y, alien_type))

    def draw(self):
        for alien in self.aliens:
            alien.draw()
            for bullet in alien.bullets:
                pygame.draw.rect(screen, RED,
                                 (bullet[0], bullet[1], 4, 10))

    def update(self):
        # Check if any alien hits the edge
        hit_edge = False
        for alien in self.aliens:
            if (alien.x <= 0 and self.direction == -1) or \
                    (alien.x + alien.width >= SCREEN_WIDTH and self.direction == 1):
                hit_edge = True
                break

        # Move aliens
        dx = self.move_speed * self.direction
        dy = 0

        if hit_edge:
            self.direction *= -1
            dy = self.move_down_distance

        for alien in self.aliens:
            alien.update(dx, dy)
            alien.update_bullets()

        # Increase speed as aliens are destroyed
        if len(self.aliens) < 10:
            self.move_speed = 3
        elif len(self.aliens) < 20:
            self.move_speed = 2

    def get_aliens_rects(self):
        return [alien.get_rect() for alien in self.aliens]

    def remove_alien(self, alien):
        if alien in self.aliens:
            self.aliens.remove(alien)


class Barrier:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 40)
        self.health = 10
        self.blocks = []
        self.create_blocks()

    def create_blocks(self):
        block_size = 8
        for y in range(0, 40, block_size):
            for x in range(0, 80, block_size):
                # Create a barrier with gaps (like original Space Invaders)
                if (x < 20 or x > 60) or (y < 10):
                    continue
                self.blocks.append(pygame.Rect(
                    self.rect.x + x,
                    self.rect.y + y,
                    block_size, block_size
                ))

    def draw(self):
        for block in self.blocks[:]:
            pygame.draw.rect(screen, GREEN, block)

    def hit(self, x, y):
        for block in self.blocks[:]:
            if block.collidepoint(x, y):
                self.blocks.remove(block)
                self.health -= 1
                return True
        return False

    def is_destroyed(self):
        return len(self.blocks) == 0


def create_barriers():
    barriers = []
    for i in range(4):
        x = 100 + i * 150
        barriers.append(Barrier(x, SCREEN_HEIGHT - 150))
    return barriers


def check_collisions(player, alien_grid, barriers):
    # Player bullets vs aliens
    for bullet in player.bullets[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
        for alien in alien_grid.aliens[:]:
            if bullet_rect.colliderect(alien.get_rect()):
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
                alien_grid.remove_alien(alien)
                player.score += 10 * (3 - alien.alien_type)  # Different points for different aliens
                break

    # Alien bullets vs player
    for alien in alien_grid.aliens:
        for bullet in alien.bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
            if bullet_rect.colliderect(player.get_rect()):
                alien.bullets.remove(bullet)
                player.lives -= 1
                return True

    # Aliens vs player
    for alien in alien_grid.aliens:
        if alien.get_rect().colliderect(player.get_rect()):
            player.lives -= 1
            return True

    # Aliens vs barriers
    for barrier in barriers:
        for alien in alien_grid.aliens:
            if alien.get_rect().colliderect(barrier.rect):
                # Damage barrier where alien touches
                for x in range(alien.x, alien.x + alien.width):
                    for y in range(alien.y, alien.y + alien.height):
                        barrier.hit(x, y)

    # Player bullets vs barriers
    for bullet in player.bullets[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
        for barrier in barriers:
            for block in barrier.blocks[:]:
                if bullet_rect.colliderect(block):
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    barrier.hit(block.centerx, block.centery)
                    break

    # Alien bullets vs barriers
    for alien in alien_grid.aliens:
        for bullet in alien.bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 4, 10)
            for barrier in barriers:
                for block in barrier.blocks[:]:
                    if bullet_rect.colliderect(block):
                        if bullet in alien.bullets:
                            alien.bullets.remove(bullet)
                        barrier.hit(block.centerx, block.centery)
                        break

    return False


def draw_game_over(screen, player, game_won):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    if game_won:
        text = font_large.render("YOU WIN!", True, GREEN)
    else:
        text = font_large.render("GAME OVER", True, RED)

    score_text = font_medium.render(f"Final Score: {player.score}", True, WHITE)
    restart_text = font_small.render("Press R to restart or Q to quit", True, WHITE)

    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))


def main():
    player = Player()
    alien_grid = AlienGrid()
    barriers = create_barriers()

    game_over = False
    game_won = False

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.shoot()
                if game_over:
                    if event.key == pygame.K_r:
                        # Reset game
                        player = Player()
                        alien_grid = AlienGrid()
                        barriers = create_barriers()
                        game_over = False
                        game_won = False
                    elif event.key == pygame.K_q:
                        running = False

        if not game_over:
            # Player movement
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update_bullets()

            # Alien movement
            alien_grid.update()

            # Check collisions
            hit = check_collisions(player, alien_grid, barriers)

            # Check win/lose conditions
            if player.lives <= 0:
                game_over = True
            if len(alien_grid.aliens) == 0:
                game_over = True
                game_won = True
            for alien in alien_grid.aliens:
                if alien.y + alien.height >= player.y:
                    game_over = True

        # Drawing
        screen.fill(BLACK)

        # Draw stars in background
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)

        # Draw game objects
        player.draw()
        alien_grid.draw()
        for barrier in barriers:
            barrier.draw()

        # Draw UI
        score_text = font_small.render(f"Score: {player.score}", True, WHITE)
        lives_text = font_small.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))

        # Draw game over screen
        if game_over:
            draw_game_over(screen, player, game_won)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
