# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# 0 Shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1 --temp 1.0  --model  /AI/models/Step-3.5-Flash-MXFP4_MOE-00001-of-00007.gguf

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Load fonts
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 36)
font_large = pygame.font.SysFont('Arial', 72)


class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 5
        self.color = GREEN
        self.lives = 3
        self.score = 0
        self.shoot_cooldown = 0
        self.shoot_delay = 250  # milliseconds between shots

    def draw(self):
        # Draw player ship (triangle shape)
        points = [
            (self.x + self.width // 2, self.y),  # Top
            (self.x, self.y + self.height),  # Bottom left
            (self.x + self.width, self.y + self.height)  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)
        # Draw cockpit
        pygame.draw.rect(screen, BLUE,
                         (self.x + self.width // 2 - 5, self.y + 10, 10, 10))

    def move(self, dx):
        self.x += dx * self.speed
        # Keep player on screen
        self.x = max(0, min(self.x, WIDTH - self.width))

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_delay
            return Bullet(self.x + self.width // 2, self.y, -10, YELLOW)
        return None

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= clock.get_time()

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Alien:
    def __init__(self, x, y, alien_type=0):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.type = alien_type
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        self.move_down = False
        self.color = [PURPLE, RED, BLUE][alien_type % 3]

    def draw(self):
        # Draw different alien types
        if self.type == 0:
            # Crab-like alien
            points = [
                (self.x + 10, self.y + 5),
                (self.x + 30, self.y + 5),
                (self.x + 5, self.y + 15),
                (self.x + 35, self.y + 15),
                (self.x + 10, self.y + 25),
                (self.x + 30, self.y + 25)
            ]
            pygame.draw.polygon(screen, self.color, points)
            # Eyes
            pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 15), 4)
            pygame.draw.circle(screen, WHITE, (self.x + 25, self.y + 15), 4)
            pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 15), 2)
            pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 15), 2)

        elif self.type == 1:
            # Squid-like alien
            pygame.draw.ellipse(screen, self.color,
                                (self.x, self.y, self.width, self.height))
            # Eyes
            pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 15), 3)
            pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 15), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 15), 1)
            pygame.draw.circle(screen, BLACK, (self.x + 30, self.y + 15), 1)

        else:
            # Classic UFO shape
            pygame.draw.ellipse(screen, self.color,
                                (self.x + 5, self.y, self.width - 10, self.height // 2))
            pygame.draw.rect(screen, self.color,
                             (self.x, self.y + self.height // 2, self.width, self.height // 2))
            # Dome
            pygame.draw.ellipse(screen, self.color,
                                (self.x + 10, self.y - 5, 20, 15))
            # Eyes
            pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 15), 3)
            pygame.draw.circle(screen, WHITE, (self.x + 25, self.y + 15), 3)

    def move(self, aliens, move_down=False):
        if move_down:
            self.y += 20
            self.direction *= -1
        else:
            self.x += self.speed * self.direction

        # Check if any alien hits the edge
        for alien in aliens:
            if alien.x <= 0 or alien.x >= WIDTH - alien.width:
                return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 15
        self.speed = speed
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color,
                         (self.x - self.width // 2, self.y, self.width, self.height))

    def move(self):
        self.y += self.speed

    def is_off_screen(self):
        return self.y < 0 or self.y > HEIGHT

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)


class AlienBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, 5, RED)


class Game:
    def __init__(self):
        self.player = Player()
        self.aliens = []
        self.player_bullets = []
        self.alien_bullets = []
        self.alien_move_direction = 1
        self.alien_move_down = False
        self.alien_move_timer = 0
        self.alien_move_delay = 500  # milliseconds between moves
        self.alien_shoot_timer = 0
        self.alien_shoot_delay = 2000
        self.wave = 1
        self.aliens_per_wave = 8
        self.game_state = "playing"  # "playing", "game_over", "win"
        self.create_wave()

    def create_wave(self):
        self.aliens = []
        rows = min(3 + self.wave // 2, 5)  # Increase rows every 2 waves, max 5
        cols = min(8 + self.wave // 3, 12)  # Increase columns every 3 waves, max 12

        start_x = 50
        start_y = 50

        for row in range(rows):
            for col in range(cols):
                alien_type = row % 3  # Different alien types per row
                x = start_x + col * 50
                y = start_y + row * 40
                self.aliens.append(Alien(x, y, alien_type))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        bullet = self.player.shoot()
                        if bullet:
                            self.player_bullets.append(bullet)
                elif self.game_state in ["game_over", "win"]:
                    if event.key == pygame.K_r:
                        self.__init__()  # Reset game

    def update(self):
        if self.game_state != "playing":
            return

        # Update player
        self.player.update()

        # Handle player movement (continuous)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1)

        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.player_bullets.remove(bullet)
                continue

            # Check collision with aliens
            bullet_rect = bullet.get_rect()
            for alien in self.aliens[:]:
                if bullet_rect.colliderect(alien.get_rect()):
                    self.aliens.remove(alien)
                    self.player_bullets.remove(bullet)
                    self.player.score += [10, 20, 30][alien.type]
                    break

        # Update alien movement
        current_time = pygame.time.get_ticks()
        if current_time - self.alien_move_timer > self.alien_move_delay:
            self.alien_move_timer = current_time

            # Check if any alien needs to move down
            move_down = False
            for alien in self.aliens:
                if (alien.x <= 0 and alien.direction == -1) or \
                        (alien.x >= WIDTH - alien.width and alien.direction == 1):
                    move_down = True
                    break

            # Move all aliens
            for alien in self.aliens:
                alien.move(self.aliens, move_down)

            # Increase speed as aliens decrease
            if len(self.aliens) > 0:
                self.alien_move_delay = max(100, 500 - (self.wave * 50))

        # Alien shooting
        if current_time - self.alien_shoot_timer > self.alien_shoot_delay and self.aliens:
            self.alien_shoot_timer = current_time
            # Random alien shoots
            shooting_alien = random.choice(self.aliens)
            self.alien_bullets.append(AlienBullet(
                shooting_alien.x + shooting_alien.width // 2,
                shooting_alien.y + shooting_alien.height
            ))
            self.alien_shoot_delay = max(500, 2000 - (self.wave * 200))

        # Update alien bullets
        for bullet in self.alien_bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.alien_bullets.remove(bullet)
                continue

            # Check collision with player
            if bullet.get_rect().colliderect(self.player.get_rect()):
                self.alien_bullets.remove(bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_state = "game_over"

        # Check if aliens reached bottom
        for alien in self.aliens:
            if alien.y + alien.height >= self.player.y:
                self.game_state = "game_over"
                break

        # Check if all aliens are destroyed
        if not self.aliens:
            self.wave += 1
            self.create_wave()
            # Increase player speed slightly each wave
            self.player.speed += 0.5

    def draw(self):
        screen.fill(BLACK)

        # Draw stars in background
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)

        # Draw game objects
        self.player.draw()

        for alien in self.aliens:
            alien.draw()

        for bullet in self.player_bullets:
            bullet.draw()

        for bullet in self.alien_bullets:
            bullet.draw()

        # Draw UI
        score_text = font_small.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = font_small.render(f"Lives: {self.player.lives}", True, WHITE)
        wave_text = font_small.render(f"Wave: {self.wave}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(wave_text, (10, 70))

        # Draw game state messages
        if self.game_state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            game_over_text = font_large.render("GAME OVER", True, RED)
            restart_text = font_medium.render("Press R to restart", True, WHITE)

            screen.blit(game_over_text,
                        (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text,
                        (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

        elif self.game_state == "win":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = font_large.render("YOU WIN!", True, GREEN)
            score_text = font_medium.render(f"Final Score: {self.player.score}", True, YELLOW)
            restart_text = font_medium.render("Press R to restart", True, WHITE)

            screen.blit(win_text,
                        (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(score_text,
                        (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(restart_text,
                        (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))


def main():
    game = Game()

    while True:
        game.handle_events()
        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
