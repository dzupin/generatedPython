# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for graphic.
# 0-shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-397B-A17B-UD-TQ1_0.gguf  --mmproj /AI/models/Qwen3.5-397B-A17B-mmproj-BF16.gguf


import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 0, 255)
ORANGE = (255, 165, 0)

# Game variables
clock = pygame.time.Clock()
FPS = 60


# Player class
class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.speed = 5
        self.color = CYAN
        self.bullets = []
        self.lives = 3

    def draw(self):
        # Draw spaceship body
        pygame.draw.polygon(screen, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ])

        # Draw cockpit
        pygame.draw.circle(screen, WHITE, (self.x + self.width // 2, self.y + 15), 8)

        # Draw engine glow
        pygame.draw.circle(screen, ORANGE, (self.x + self.width // 2, self.y + self.height + 5), 5)

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width

    def shoot(self):
        self.bullets.append([self.x + self.width // 2, self.y])

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] -= 7
            if bullet[1] < 0:
                self.bullets.remove(bullet)

    def draw_bullets(self):
        for bullet in self.bullets:
            # Draw bullet with glow effect
            pygame.draw.circle(screen, YELLOW, (bullet[0], bullet[1]), 4)
            pygame.draw.circle(screen, ORANGE, (bullet[0], bullet[1]), 2)


# Invader class
class Invader:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.color = color
        self.alive = True

    def draw(self):
        if self.alive:
            # Draw invader body
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

            # Draw eyes
            pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 12), 5)
            pygame.draw.circle(screen, BLACK, (self.x + 30, self.y + 12), 5)

            # Draw mouth
            pygame.draw.line(screen, BLACK, (self.x + 10, self.y + 22), (self.x + 30, self.y + 22), 3)

            # Draw antennas
            pygame.draw.line(screen, self.color, (self.x + 10, self.y), (self.x + 10, self.y - 8), 2)
            pygame.draw.line(screen, self.color, (self.x + 30, self.y), (self.x + 30, self.y - 8), 2)
            pygame.draw.circle(screen, RED, (self.x + 10, self.y - 8), 3)
            pygame.draw.circle(screen, RED, (self.x + 30, self.y - 8), 3)


# Enemy bullet class
class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4

    def update(self):
        self.y += self.speed

    def draw(self):
        # Draw enemy bullet
        pygame.draw.rect(screen, RED, (self.x - 3, self.y, 6, 12))
        pygame.draw.circle(screen, ORANGE, (self.x, self.y), 4)


# Explosion effect
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.alpha = 255

    def update(self):
        self.radius += 2
        self.alpha -= 15
        if self.alpha < 0:
            self.alpha = 0

    def draw(self):
        if self.alpha > 0:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, ORANGE, (self.x, self.y), self.radius - 5)


# Star background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)


# Create stars for background
stars = [Star() for _ in range(100)]


# Game functions
def create_invaders():
    invaders = []
    colors = [PURPLE, BLUE, GREEN, YELLOW, ORANGE]
    for row in range(5):
        for col in range(11):
            x = 100 + col * 50
            y = 50 + row * 40
            color = colors[row % len(colors)]
            invaders.append(Invader(x, y, color))
    return invaders


def draw_score(score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))


def draw_lives(lives):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(text, (WIDTH - 120, 10))


def draw_game_over():
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))

    font = pygame.font.Font(None, 36)
    text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))


def draw_win():
    font = pygame.font.Font(None, 72)
    text = font.render("YOU WIN!", True, GREEN)
    screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))

    font = pygame.font.Font(None, 36)
    text = font.render("Press R to Play Again", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 110, HEIGHT // 2 + 20))


def draw_bunker(player_x, player_y):
    """Draw protective bunkers"""
    bunker_color = GREEN
    bunker_positions = [(150, 480), (300, 480), (450, 480), (600, 480)]

    for bx, by in bunker_positions:
        # Draw bunker blocks
        for i in range(3):
            for j in range(4):
                x = bx + j * 15
                y = by + i * 10
                pygame.draw.rect(screen, bunker_color, (x, y, 14, 9))


# Main game function
def main():
    player = Player()
    invaders = create_invaders()
    enemy_bullets = []
    explosions = []
    score = 0
    game_over = False
    game_win = False
    invader_direction = 1
    invader_speed = 1
    move_down = False

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not game_win:
                    player.shoot()
                if event.key == pygame.K_r and (game_over or game_win):
                    # Reset game
                    player = Player()
                    invaders = create_invaders()
                    enemy_bullets = []
                    explosions = []
                    score = 0
                    game_over = False
                    game_win = False
                    invader_direction = 1
                    invader_speed = 1

        # Update stars
        for star in stars:
            star.update()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_left()
        if keys[pygame.K_RIGHT]:
            player.move_right()

        # Update player bullets
        player.update_bullets()

        # Move invaders
        if not game_over and not game_win:
            move_down = False
            for invader in invaders:
                invader.x += invader_speed * invader_direction
                if invader.x <= 0 or invader.x + invader.width >= WIDTH:
                    move_down = True

            if move_down:
                invader_direction *= -1
                for invader in invaders:
                    invader.y += 20

            # Enemy shooting
            if random.random() < 0.02 and invaders:
                invader = random.choice([i for i in invaders if i.alive])
                enemy_bullets.append(EnemyBullet(invader.x + invader.width // 2, invader.y + invader.height))

            # Update enemy bullets
            for bullet in enemy_bullets[:]:
                bullet.update()
                if bullet.y > HEIGHT:
                    enemy_bullets.remove(bullet)

            # Check bullet collisions
            # Player bullets hitting invaders
            for bullet in player.bullets[:]:
                for invader in invaders:
                    if invader.alive:
                        if (bullet[0] > invader.x and bullet[0] < invader.x + invader.width and
                                bullet[1] > invader.y and bullet[1] < invader.y + invader.height):
                            player.bullets.remove(bullet)
                            invader.alive = False
                            score += 10
                            explosions.append(
                                Explosion(invader.x + invader.width // 2, invader.y + invader.height // 2))
                            break

            # Enemy bullets hitting player
            for bullet in enemy_bullets[:]:
                if (bullet.x > player.x and bullet.x < player.x + player.width and
                        bullet.y > player.y and bullet.y < player.y + player.height):
                    enemy_bullets.remove(bullet)
                    player.lives -= 1
                    explosions.append(Explosion(player.x + player.width // 2, player.y + player.height // 2))
                    if player.lives <= 0:
                        game_over = True

            # Check if all invaders are dead
            if all(not invader.alive for invader in invaders):
                game_win = True

            # Increase difficulty over time
            invader_speed += 0.001

        # Update explosions
        for explosion in explosions[:]:
            explosion.update()
            if explosion.alpha <= 0:
                explosions.remove(explosion)

        # Draw everything
        screen.fill(BLACK)

        # Draw stars
        for star in stars:
            star.draw()

        # Draw bunkers
        draw_bunker(player.x, player.y)

        # Draw player
        player.draw()
        player.draw_bullets()

        # Draw invaders
        for invader in invaders:
            invader.draw()

        # Draw enemy bullets
        for bullet in enemy_bullets:
            bullet.draw()

        # Draw explosions
        for explosion in explosions:
            explosion.draw()

        # Draw score and lives
        draw_score(score)
        draw_lives(player.lives)

        # Draw game over or win screen
        if game_over:
            draw_game_over()
        elif game_win:
            draw_win()

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
