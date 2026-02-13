# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Devstral-Small-2-24B-Instruct-2512-Q8_0.gguf  --mmproj /AI/models/Devstral-Small-2-24B-Instruct-2512-mmproj-BF16.gguf

import pygame
import random
import math

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
player_img = pygame.Surface((50, 40))
player_img.fill(GREEN)
player_x = SCREEN_WIDTH // 2 - 25
player_y = SCREEN_HEIGHT - 60
player_speed = 5

# Enemy
enemy_img = pygame.Surface((40, 40))
enemy_img.fill(RED)
enemies = []
num_enemies = 6

for i in range(num_enemies):
    enemies.append({
        'x': random.randint(0, SCREEN_WIDTH - 40),
        'y': random.randint(50, 200),
        'x_change': 2,
        'y_change': 20
    })

# Bullet
bullet_img = pygame.Surface((5, 15))
bullet_img.fill(WHITE)
bullet_x = 0
bullet_y = SCREEN_HEIGHT - 60
bullet_speed = 7
bullet_state = "ready"  # "ready" - not on screen, "fire" - moving

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game over
game_over_font = pygame.font.SysFont(None, 64)

def player(x, y):
    screen.blit(player_img, (x, y))

def enemy(x, y):
    screen.blit(enemy_img, (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_img, (x + 22, y - 15))

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt((enemy_x - bullet_x) ** 2 + (enemy_y - bullet_y) ** 2)
    return distance < 27

def show_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def game_over():
    game_over_text = game_over_font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 32))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # RGB background
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keystroke events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x -= player_speed
            if event.key == pygame.K_RIGHT:
                player_x += player_speed
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bullet_x = player_x
                bullet_y = player_y
                fire_bullet(bullet_x, bullet_y)

    # Keep player within bounds
    if player_x <= 0:
        player_x = 0
    elif player_x >= SCREEN_WIDTH - 50:
        player_x = SCREEN_WIDTH - 50

    # Enemy movement
    for enemy_data in enemies[:]:
        # Game over if enemy reaches bottom
        if enemy_data['y'] > SCREEN_HEIGHT - 80:
            for e in enemies:
                e['y'] = 2000  # Move all enemies off screen
            game_over()
            break

        enemy_data['x'] += enemy_data['x_change']

        if enemy_data['x'] <= 0:
            enemy_data['x_change'] = 2
            enemy_data['y'] += enemy_data['y_change']
        elif enemy_data['x'] >= SCREEN_WIDTH - 40:
            enemy_data['x_change'] = -2
            enemy_data['y'] += enemy_data['y_change']

        # Collision detection
        if bullet_state == "fire":
            if is_collision(enemy_data['x'], enemy_data['y'], bullet_x, bullet_y):
                bullet_state = "ready"
                score += 1
                enemies.remove(enemy_data)
                # Add new enemy if all are destroyed
                if not enemies:
                    for i in range(num_enemies):
                        enemies.append({
                            'x': random.randint(0, SCREEN_WIDTH - 40),
                            'y': random.randint(50, 200),
                            'x_change': 2 + score // 5,  # Increase speed as score increases
                            'y_change': 20
                        })
                break

    # Bullet movement
    if bullet_state == "fire":
        fire_bullet(bullet_x, bullet_y)
        bullet_y -= bullet_speed
        if bullet_y <= 0:
            bullet_state = "ready"

    # Draw player and enemies
    player(player_x, player_y)
    for enemy_data in enemies:
        enemy(enemy_data['x'], enemy_data['y'])

    show_score()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
