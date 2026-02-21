# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for graphic.
# 0-shot
# PROMPT FOLLOW UP (game enhancement):  Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure to keep update scope in reasonable level so that update will work correctly and will not break a game.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-397B-A17B-UD-TQ1_0.gguf  --mmproj /AI/models/Qwen3.5-397B-A17B-mmproj-BF16.gguf

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Enhanced Edition")

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
PINK = (255, 105, 180)
GOLD = (255, 215, 0)

# Game variables
clock = pygame.time.Clock()
FPS = 60

# Power-up types
POWER_UP_TYPES = ['TRIPLE_SHOT', 'SHIELD', 'SPEED_BOOST', 'BOMB']


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
        self.power_up = None
        self.power_up_timer = 0
        self.shield_active = False
        self.invincible = False
        self.invincible_timer = 0

    def draw(self):
        # Draw spaceship body with gradient effect
        pygame.draw.polygon(screen, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ])

        # Draw cockpit
        pygame.draw.circle(screen, WHITE, (self.x + self.width // 2, self.y + 15), 8)

        # Draw engine glow
        pygame.draw.circle(screen, ORANGE, (self.x + self.width // 2, self.y + self.height + 5), 5)

        # Draw shield if active
        if self.shield_active:
            pygame.draw.circle(screen, BLUE, (self.x + self.width // 2, self.y + self.height // 2), 30, 2)

        # Draw invincibility effect
        if self.invincible:
            pygame.draw.circle(screen, GOLD, (self.x + self.width // 2, self.y + self.height // 2), 35, 2)

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width

    def shoot(self):
        if self.power_up == 'TRIPLE_SHOT':
            self.bullets.append([self.x + self.width // 2, self.y, 0])  # straight
            self.bullets.append([self.x + self.width // 2, self.y, -1])  # left angle
            self.bullets.append([self.x + self.width // 2, self.y, 1])  # right angle
        else:
            self.bullets.append([self.x + self.width // 2, self.y, 0])

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] -= 7
            if bullet[1] < 0:
                self.bullets.remove(bullet)

    def draw_bullets(self):
        for bullet in self.bullets:
            # Draw bullet with glow effect
            if bullet[2] == 0:
                pygame.draw.circle(screen, YELLOW, (bullet[0], bullet[1]), 4)
            elif bullet[2] == -1:
                pygame.draw.circle(screen, BLUE, (bullet[0] - 5, bullet[1]), 4)
            else:
                pygame.draw.circle(screen, RED, (bullet[0] + 5, bullet[1]), 4)
            pygame.draw.circle(screen, ORANGE, (bullet[0], bullet[1]), 2)

    def activate_power_up(self, power_type, duration=500):
        self.power_up = power_type
        self.power_up_timer = pygame.time.get_ticks() + duration
        if power_type == 'SHIELD':
            self.shield_active = True
        elif power_type == 'SPEED_BOOST':
            self.speed = 8

    def deactivate_power_up(self):
        self.power_up = None
        self.shield_active = False
        self.speed = 5

    def check_power_up_expiry(self):
        if self.power_up_timer > 0 and pygame.time.get_ticks() > self.power_up_timer:
            self.deactivate_power_up()

    def become_invincible(self, duration=3000):
        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks() + duration

    def check_invincibility_expiry(self):
        if self.invincible and pygame.time.get_ticks() > self.invincible_timer:
            self.invincible = False


# Invader class
class Invader:
    def __init__(self, x, y, color, invader_type='normal'):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.color = color
        self.alive = True
        self.invader_type = invader_type
        self.move_pattern = 0
        self.special_ability = False

    def draw(self):
        if self.alive:
            if self.invader_type == 'normal':
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

            elif self.invader_type == 'fast':
                # Fast invader - smaller and different color
                pygame.draw.polygon(screen, self.color, [
                    (self.x + self.width // 2, self.y),
                    (self.x + self.width, self.y + self.height),
                    (self.x, self.y + self.height)
                ])
                pygame.draw.circle(screen, WHITE, (self.x + self.width // 2, self.y + 10), 5)

            elif self.invader_type == 'tank':
                # Tank invader - larger and tougher
                pygame.draw.rect(screen, self.color, (self.x, self.y, self.width + 10, self.height + 10))
                pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 15), 8)
                pygame.draw.circle(screen, BLACK, (self.x + 35, self.y + 15), 8)


# Enemy bullet class
class EnemyBullet:
    def __init__(self, x, y, speed=4, color=RED):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color

    def update(self):
        self.y += self.speed

    def draw(self):
        # Draw enemy bullet with trail
        pygame.draw.rect(screen, self.color, (self.x - 3, self.y, 6, 12))
        pygame.draw.circle(screen, ORANGE, (self.x, self.y), 4)


# Power-up class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.power_type = power_type
        self.active = True
        self.color = GOLD if power_type == 'BOMB' else GREEN

    def draw(self):
        if self.active:
            # Draw power-up box
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

            # Draw symbol based on type
            if self.power_type == 'TRIPLE_SHOT':
                pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 15), 8)
            elif self.power_type == 'SHIELD':
                pygame.draw.circle(screen, BLUE, (self.x + 15, self.y + 15), 10, 2)
            elif self.power_type == 'SPEED_BOOST':
                pygame.draw.polygon(screen, WHITE, [
                    (self.x + 15, self.y + 5),
                    (self.x + 25, self.y + 15),
                    (self.x + 15, self.y + 25)
                ])
            elif self.power_type == 'BOMB':
                pygame.draw.circle(screen, RED, (self.x + 15, self.y + 15), 10)


# Explosion effect
class Explosion:
    def __init__(self, x, y, size='small'):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30 if size == 'small' else 50
        self.alpha = 255
        self.size = size

    def update(self):
        self.radius += 2
        self.alpha -= 15
        if self.alpha < 0:
            self.alpha = 0

    def draw(self):
        if self.alpha > 0:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, ORANGE, (self.x, self.y), self.radius - 5)


# Particle effect
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)


# Star background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.randint(1, 3)
        self.twinkle = random.random() > 0.5

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        if self.twinkle:
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        else:
            color = WHITE
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)


# Create stars for background
stars = [Star() for _ in range(100)]


# Game functions
def create_invaders(wave=1):
    invaders = []
    colors = [PURPLE, BLUE, GREEN, YELLOW, ORANGE]

    # Different wave patterns
    if wave == 1:
        for row in range(5):
            for col in range(11):
                x = 100 + col * 50
                y = 50 + row * 40
                color = colors[row % len(colors)]
                invaders.append(Invader(x, y, color, 'normal'))
    elif wave == 2:
        # Include fast invaders
        for row in range(5):
            for col in range(11):
                x = 100 + col * 50
                y = 50 + row * 40
                color = colors[row % len(colors)]
                inv_type = 'fast' if random.random() < 0.3 else 'normal'
                invaders.append(Invader(x, y, color, inv_type))
    else:
        # Include tank invaders
        for row in range(5):
            for col in range(11):
                x = 100 + col * 50
                y = 50 + row * 40
                color = colors[row % len(colors)]
                inv_type = 'tank' if random.random() < 0.2 else 'normal'
                invaders.append(Invader(x, y, color, inv_type))

    return invaders


def create_power_up():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(100, HEIGHT // 2)
    power_type = random.choice(POWER_UP_TYPES)
    return PowerUp(x, y, power_type)


def draw_score(score, combo, high_score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

    if combo > 1:
        combo_text = font.render(f"Combo: x{combo}", True, GOLD)
        screen.blit(combo_text, (10, 45))

    hs_text = font.render(f"High: {high_score}", True, YELLOW)
    screen.blit(hs_text, (WIDTH - 120, 10))


def draw_lives(lives, wave):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(text, (WIDTH - 120, 50))

    wave_text = font.render(f"Wave: {wave}", True, GREEN)
    screen.blit(wave_text, (WIDTH // 2 - 50, 10))


def draw_game_over(score, high_score):
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2))

    if score >= high_score:
        hs_text = font.render("NEW HIGH SCORE!", True, GOLD)
        screen.blit(hs_text, (WIDTH // 2 - 120, HEIGHT // 2 + 40))

    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 80))


def draw_win(wave):
    font = pygame.font.Font(None, 72)
    text = font.render("WAVE COMPLETE!", True, GREEN)
    screen.blit(text, (WIDTH // 2 - 180, HEIGHT // 2 - 50))

    font = pygame.font.Font(None, 36)
    wave_text = font.render(f"Wave {wave} Cleared!", True, WHITE)
    screen.blit(wave_text, (WIDTH // 2 - 100, HEIGHT // 2))

    next_text = font.render("Press SPACE for Next Wave", True, YELLOW)
    screen.blit(next_text, (WIDTH // 2 - 130, HEIGHT // 2 + 40))


def draw_bunker(player_x, player_y):
    """Draw protective bunkers"""
    bunker_color = GREEN
    bunker_positions = [(150, 480), (300, 480), (450, 480), (600, 480)]

    for bx, by in bunker_positions:
        for i in range(3):
            for j in range(4):
                x = bx + j * 15
                y = by + i * 10
                pygame.draw.rect(screen, bunker_color, (x, y, 14, 9))


def draw_bomb_effect():
    """Draw bomb explosion covering bottom of screen"""
    for i in range(20):
        x = random.randint(0, WIDTH)
        y = random.randint(400, HEIGHT)
        pygame.draw.circle(screen, ORANGE, (x, y), random.randint(5, 15))


# Screen shake effect
def screen_shake():
    offset_x = random.randint(-5, 5)
    offset_y = random.randint(-5, 5)
    return offset_x, offset_y


# Main game function
def main():
    player = Player()
    invaders = create_invaders()
    enemy_bullets = []
    explosions = []
    particles = []
    power_ups = []
    score = 0
    high_score = 0
    combo = 0
    combo_timer = 0
    game_over = False
    game_win = False
    wave = 1
    invader_direction = 1
    invader_speed = 1
    move_down = False
    wave_complete = False
    bomb_available = True
    bomb_timer = 0
    shake_offset = (0, 0)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over and not game_win and not wave_complete:
                        player.shoot()
                    elif wave_complete and not game_over:
                        # Start next wave
                        wave += 1
                        invaders = create_invaders(wave)
                        enemy_bullets = []
                        wave_complete = False
                        invader_speed = 1 + wave * 0.5
                    elif game_over or game_win:
                        # Reset game
                        player = Player()
                        invaders = create_invaders()
                        enemy_bullets = []
                        explosions = []
                        particles = []
                        power_ups = []
                        score = 0
                        combo = 0
                        wave = 1
                        game_over = False
                        game_win = False
                        wave_complete = False
                        invader_speed = 1
                        bomb_available = True

                if event.key == pygame.K_b and bomb_available and not game_over:
                    # Activate bomb
                    bomb_available = False
                    bomb_timer = pygame.time.get_ticks() + 30000  # 30 seconds cooldown
                    # Destroy all enemies
                    for invader in invaders:
                        if invader.alive:
                            invader.alive = False
                            score += 10
                            explosions.append(
                                Explosion(invader.x + invader.width // 2, invader.y + invader.height // 2, 'large'))
                            for _ in range(10):
                                particles.append(
                                    Particle(invader.x + random.randint(0, 40), invader.y + random.randint(0, 30),
                                             invader.color))
                    draw_bomb_effect()
                    shake_offset = screen_shake()

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

        # Check power-up expiry
        player.check_power_up_expiry()
        player.check_invincibility_expiry()

        # Check bomb cooldown
        if not bomb_available and pygame.time.get_ticks() > bomb_timer:
            bomb_available = True

        # Update combo timer
        if combo_timer > 0 and pygame.time.get_ticks() > combo_timer:
            combo = 0
            combo_timer = 0

        # Spawn power-ups randomly
        if random.random() < 0.005 and len(power_ups) < 3:
            power_ups.append(create_power_up())

        # Move invaders
        if not game_over and not game_win and not wave_complete:
            move_down = False
            for invader in invaders:
                if invader.alive:
                    invader.x += invader_speed * invader_direction
                    if invader.x <= 0 or invader.x + invader.width >= WIDTH:
                        move_down = True

            if move_down:
                invader_direction *= -1
                for invader in invaders:
                    if invader.alive:
                        invader.y += 20

            # Enemy shooting
            if random.random() < 0.02 and invaders:
                alive_invaders = [i for i in invaders if i.alive]
                if alive_invaders:
                    invader = random.choice(alive_invaders)
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
                        bullet_x = bullet[0] + (bullet[2] * 5 if len(bullet) > 2 else 0)
                        if (bullet_x > invader.x and bullet_x < invader.x + invader.width and
                                bullet[1] > invader.y and bullet[1] < invader.y + invader.height):
                            player.bullets.remove(bullet)
                            invader.alive = False

                            # Combo system
                            combo += 1
                            combo_timer = pygame.time.get_ticks() + 2000
                            combo_score = 10 * combo
                            score += combo_score

                            explosions.append(
                                Explosion(invader.x + invader.width // 2, invader.y + invader.height // 2))

                            # Spawn particles
                            for _ in range(5):
                                particles.append(
                                    Particle(invader.x + random.randint(0, 40), invader.y + random.randint(0, 30),
                                             invader.color))

                            # Chance to spawn power-up
                            if random.random() < 0.1:
                                power_ups.append(PowerUp(invader.x, invader.y, random.choice(POWER_UP_TYPES)))

                            break

            # Enemy bullets hitting player
            for bullet in enemy_bullets[:]:
                if not player.invincible:
                    if player.shield_active:
                        # Shield absorbs damage
                        enemy_bullets.remove(bullet)
                        explosions.append(Explosion(bullet.x, bullet.y, 'small'))
                    elif (bullet.x > player.x and bullet.x < player.x + player.width and
                          bullet.y > player.y and bullet.y < player.y + player.height):
                        enemy_bullets.remove(bullet)
                        player.lives -= 1
                        explosions.append(
                            Explosion(player.x + player.width // 2, player.y + player.height // 2, 'large'))
                        shake_offset = screen_shake()
                        player.become_invincible(2000)  # 2 seconds invincibility
                        if player.lives <= 0:
                            game_over = True
                            if score > high_score:
                                high_score = score

            # Check if all invaders are dead
            if all(not invader.alive for invader in invaders):
                wave_complete = True

            # Increase difficulty over time
            invader_speed += 0.001

        # Check power-up collection
        for power_up in power_ups[:]:
            if power_up.active:
                if (player.x < power_up.x + power_up.width and
                        player.x + player.width > power_up.x and
                        player.y < power_up.y + power_up.height and
                        player.y + player.height > power_up.y):
                    power_up.active = False
                    power_ups.remove(power_up)
                    player.activate_power_up(power_up.power_type)
                    score += 50

        # Update explosions
        for explosion in explosions[:]:
            explosion.update()
            if explosion.alpha <= 0:
                explosions.remove(explosion)

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)

        # Update high score
        if score > high_score:
            high_score = score

        # Draw everything
        screen.fill(BLACK)

        # Apply screen shake
        if shake_offset:
            screen.blit(screen, shake_offset)
            shake_offset = (0, 0)

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

        # Draw power-ups
        for power_up in power_ups:
            power_up.draw()

        # Draw explosions
        for explosion in explosions:
            explosion.draw()

        # Draw particles
        for particle in particles:
            particle.draw()

        # Draw score and lives
        draw_score(score, combo, high_score)
        draw_lives(player.lives, wave)

        # Draw bomb availability
        font = pygame.font.Font(None, 24)
        if bomb_available:
            bomb_text = font.render("Press B for Bomb", True, RED)
            screen.blit(bomb_text, (WIDTH - 150, 80))
        else:
            cooldown = max(0, (bomb_timer - pygame.time.get_ticks()) // 1000)
            bomb_text = font.render(f"Bomb: {cooldown}s", True, ORANGE)
            screen.blit(bomb_text, (WIDTH - 150, 80))

        # Draw game over or win screen
        if game_over:
            draw_game_over(score, high_score)
        elif wave_complete:
            draw_win(wave)

        # Draw combo notification
        if combo >= 5:
            font = pygame.font.Font(None, 48)
            combo_text = font.render(f"COMBO x{combo}!", True, GOLD)
            screen.blit(combo_text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
