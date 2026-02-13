# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library. (Then run error fix for: TypeError: invalid color argument)
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# NOTE Prompt1: 0-shot,  Prompt2: 1-shot (fix for shot cooldown)
import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - ULTIMATE EDITION")

# Colors (RGB tuples — fixed for no TypeError)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Player
player_width = 50
player_height = 30
player_x = SCREEN_WIDTH // 2 - player_width // 2
player_y = SCREEN_HEIGHT - player_height - 20
player_speed = 6
player_lives = 3
invincible_timer = 0  # For flashing after being hit

# Bullets
bullets = []
bullet_speed = -7
bullet_width = 5
bullet_height = 15
bullet_cooldown = 0  # Fire delay (frames). 0 = ready to fire.

# Enemies
enemy_width = 40
enemy_height = 30
enemy_rows = 5
enemy_cols = 10
enemy_gap = 10
enemies = []
enemy_speed = 1.2
enemy_direction = 1
enemy_drop_speed = 20
enemy_spawn_rate = 1.0

# Particle system for explosions
particles = []

# Power-ups
powerups = []
powerup_drop_chance = 0.05
powerup_types = ["speed", "multi_shot", "shield"]

# Score & Level
score = 0
level = 1
font = pygame.font.SysFont('Arial', 28)
big_font = pygame.font.SysFont('Arial', 60)
clock = pygame.time.Clock()
game_over = False
level_cleared = False
level_timer = 0

# Create initial enemies
def create_enemies():
    enemies.clear()
    for row in range(enemy_rows):
        for col in range(enemy_cols):
            enemy_x = col * (enemy_width + enemy_gap) + 50
            enemy_y = row * (enemy_height + enemy_gap) + 50
            enemies.append([enemy_x, enemy_y])

create_enemies()

# Add particle explosion
def create_explosion(x, y):
    for _ in range(15):
        particles.append({
            'x': x + enemy_width // 2,
            'y': y + enemy_height // 2,
            'vx': random.uniform(-4, 4),
            'vy': random.uniform(-4, 4),
            'life': 20,
            'color': random.choice([YELLOW, RED, WHITE])
        })

# Draw particles
def update_particles():
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 1
        if particle['life'] <= 0:
            particles.remove(particle)

def draw_particles():
    for particle in particles:
        alpha = particle['life'] / 20
        color = particle['color']
        surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, int(255 * alpha)), (2, 2), 2)
        screen.blit(surf, (particle['x'] - 2, particle['y'] - 2))

# Spawn power-up
def spawn_powerup(x, y):
    if random.random() < powerup_drop_chance:
        p_type = random.choice(powerup_types)
        powerups.append({
            'x': x + enemy_width // 2,
            'y': y + enemy_height // 2,
            'type': p_type,
            'speed': 2,
            'collected': False
        })

# Draw power-ups
def draw_powerups():
    for p in powerups[:]:
        color = YELLOW if p['type'] == 'speed' else PURPLE if p['type'] == 'multi_shot' else (0, 255, 255)
        pygame.draw.rect(screen, color, (p['x'], p['y'], 15, 15))
        p['y'] += p['speed']
        if p['y'] > SCREEN_HEIGHT:
            powerups.remove(p)
        # Check if player collects power-up
        if (player_x < p['x'] + 15 and player_x + player_width > p['x'] and
            player_y < p['y'] + 15 and player_y + player_height > p['y']):
            if p['type'] == 'speed':
                global player_speed
                player_speed = 10
                pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
            elif p['type'] == 'multi_shot':
                global bullet_cooldown
                bullet_cooldown = -20  # Enable multi-shot mode for 20 frames
                pygame.time.set_timer(pygame.USEREVENT + 2, 8000)
            elif p['type'] == 'shield':
                global invincible_timer
                invincible_timer = 180  # 3 seconds
            powerups.remove(p)

# Check if player is invincible
def is_invincible():
    return invincible_timer > 0

# Update invincibility
def update_invincibility():
    global invincible_timer
    if invincible_timer > 0:
        invincible_timer -= 1

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                if bullet_cooldown <= 0:  # Only fire if ready
                    bullet_x = player_x + player_width // 2 - bullet_width // 2
                    bullet_y = player_y
                    bullets.append([bullet_x, bullet_y])

                    # If multi-shot power-up is active, fire 3 bullets
                    if bullet_cooldown < 0:
                        bullets.append([bullet_x - 10, bullet_y])
                        bullets.append([bullet_x + 10, bullet_y])

                    bullet_cooldown = 15  # Reset cooldown to 15 frames (~0.25s)

            if event.key == pygame.K_r and game_over:
                # Reset game
                score = 0
                level = 1
                player_lives = 3
                player_x = SCREEN_WIDTH // 2 - player_width // 2
                create_enemies()
                bullets.clear()
                powerups.clear()
                particles.clear()
                bullet_cooldown = 0
                player_speed = 6
                invincible_timer = 0
                game_over = False
                level_cleared = False

        # Power-up timers
        if event.type == pygame.USEREVENT + 1:  # Speed expires
            player_speed = 6
        if event.type == pygame.USEREVENT + 2:  # Multi-shot expires
            bullet_cooldown = 0  # Return to normal cooldown

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
            player_x += player_speed

        # Bullet movement
        for bullet in bullets[:]:
            bullet[1] += bullet_speed
            if bullet[1] < -10:
                bullets.remove(bullet)

        # Enemy movement
        move_down = False
        for enemy in enemies:
            if enemy[0] + enemy_width >= SCREEN_WIDTH or enemy[0] <= 0:
                move_down = True
                break

        if move_down:
            enemy_direction *= -1
            for enemy in enemies:
                enemy[1] += enemy_drop_speed

        for enemy in enemies:
            enemy[0] += enemy_speed * enemy_direction

        # Bullet-enemy collision + explosion
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet[0] < enemy[0] + enemy_width and
                    bullet[0] + bullet_width > enemy[0] and
                    bullet[1] < enemy[1] + enemy_height and
                    bullet[1] + bullet_height > enemy[1]):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    create_explosion(enemy[0], enemy[1])
                    score += 10
                    spawn_powerup(enemy[0], enemy[1])
                    break

        # Level cleared
        if len(enemies) == 0 and not level_cleared:
            level += 1
            level_cleared = True
            level_timer = 120
            enemy_speed += 0.3
            enemy_drop_speed += 5
            create_enemies()
            if level % 3 == 0:
                enemy_rows += 1

        if level_cleared:
            level_timer -= 1
            if level_timer <= 0:
                level_cleared = False

        # Enemy reaches bottom
        for enemy in enemies:
            if enemy[1] + enemy_height >= player_y:
                game_over = True
                break

        # Update invincibility
        update_invincibility()

        # **CRITICAL: Decrement bullet cooldown every frame**
        if bullet_cooldown > 0:
            bullet_cooldown -= 1

    # Draw player (flashing if invincible)
    if not is_invincible() or (invincible_timer // 6) % 2 == 0:
        pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))

    # Draw enemies
    for enemy in enemies:
        if level_cleared:
            pygame.draw.rect(screen, (255, 255, 200), (enemy[0], enemy[1], enemy_width, enemy_height))
        else:
            pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_width, enemy_height))

    # Draw particles
    update_particles()
    draw_particles()

    # Draw power-ups
    draw_powerups()

    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, YELLOW)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
    screen.blit(lives_text, (10, 50))

    # Level cleared text
    if level_cleared:
        level_clear_text = big_font.render(f"LEVEL {level} CLEARED!", True, PURPLE)
        screen.blit(level_clear_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))

    # Game over screen
    if game_over:
        game_over_text = big_font.render("GAME OVER", True, RED)
        retry_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))

    # High score
    if score > 0:
        high_score_text = font.render(f"High Score: {score}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH - 180, 50))

    pygame.display.flip()

    # Quit on 'Q'
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        running = False

pygame.quit()
sys.exit()

