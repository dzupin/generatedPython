# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library. (Then run error fix for: TypeError: invalid color argument)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors (defined as RGB tuples — this avoids TypeError: invalid color argument)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Player
player_width = 50
player_height = 30
player_x = SCREEN_WIDTH // 2 - player_width // 2
player_y = SCREEN_HEIGHT - player_height - 20
player_speed = 5

# Bullets
bullets = []
bullet_speed = -7
bullet_width = 5
bullet_height = 15

# Enemies
enemy_width = 40
enemy_height = 30
enemy_rows = 5
enemy_cols = 10
enemy_gap = 10
enemies = []
enemy_speed = 1
enemy_direction = 1  # 1 for right, -1 for left

# Create enemies grid
for row in range(enemy_rows):
    for col in range(enemy_cols):
        enemy_x = col * (enemy_width + enemy_gap) + 50
        enemy_y = row * (enemy_height + enemy_gap) + 50
        enemies.append([enemy_x, enemy_y])

# Game variables
score = 0
font = pygame.font.SysFont('Arial', 30)
clock = pygame.time.Clock()
game_over = False

# Main game loop
running = True
while running:
    screen.fill(BLACK)  # Clear screen with black background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullet_x = player_x + player_width // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

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
            if bullet[1] < 0:
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
                enemy[1] += 20  # Move down

        for enemy in enemies:
            enemy[0] += enemy_speed * enemy_direction

        # Bullet-enemy collision
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet[0] < enemy[0] + enemy_width and
                    bullet[0] + bullet_width > enemy[0] and
                    bullet[1] < enemy[1] + enemy_height and
                    bullet[1] + bullet_height > enemy[1]):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10
                    break

        # Check if enemies reached bottom
        for enemy in enemies:
            if enemy[1] + enemy_height >= player_y:
                game_over = True
                break

    # Draw player
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_width, enemy_height))

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Game over text
    if game_over:
        game_over_text = font.render("GAME OVER! Press Q to quit", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

    # Quit on 'Q' key press when game over
    keys = pygame.key.get_pressed()
    if game_over and keys[pygame.K_q]:
        running = False

pygame.quit()
sys.exit()
