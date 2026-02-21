# PROMPT USED (create game baseline): WWrite Space Invaders game in python using pygame library without using external files for graphic.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Devstral-Small-2-24B-Instruct-2512-Q8_0.gguf  --mmproj /AI/models/Devstral-Small-2-24B-Instruct-2512-mmproj-BF16.gguf

import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player
player_width = 50
player_height = 20
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 5

# Bullet
bullet_width = 5
bullet_height = 15
bullet_speed = 7
bullet_state = "ready"  # "ready" - not on screen, "fire" - moving
bullet_x = 0
bullet_y = player_y

# Enemy
enemy_width = 40
enemy_height = 40
enemy_speed = 1
enemy_direction = 1
enemies = []
num_enemies = 6

for i in range(num_enemies):
    enemies.append({
        'x': random.randint(0, WIDTH - enemy_width),
        'y': random.randint(50, 200),
        'direction': 1,
        'move_down': False
    })

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game over flag
game_over = False

# Clock for controlling frame rate
clock = pygame.time.Clock()

def draw_player(x, y):
    """Draw the player spaceship"""
    pygame.draw.rect(screen, GREEN, (x, y, player_width, player_height))
    # Add a simple triangle for the top
    pygame.draw.polygon(screen, GREEN, [
        (x + player_width//2, y - 10),
        (x + player_width, y),
        (x, y)
    ])

def fire_bullet(x, y):
    """Fire a bullet"""
    global bullet_state
    bullet_state = "fire"
    screen.blit(pygame.Surface((bullet_width, bullet_height)), (x + player_width//2 - bullet_width//2, y))

def draw_bullet(x, y):
    """Draw the bullet"""
    pygame.draw.rect(screen, WHITE, (x, y, bullet_width, bullet_height))

def draw_enemy(x, y):
    """Draw an alien enemy"""
    # Draw the main body
    pygame.draw.rect(screen, RED, (x, y, enemy_width, enemy_height))

    # Add some details to make it look like an alien
    # Eyes
    pygame.draw.circle(screen, BLACK, (x + enemy_width//4, y + enemy_height//4), 5)
    pygame.draw.circle(screen, BLACK, (x + 3*enemy_width//4, y + enemy_height//4), 5)
    pygame.draw.circle(screen, WHITE, (x + enemy_width//4, y + enemy_height//4), 3)
    pygame.draw.circle(screen, WHITE, (x + 3*enemy_width//4, y + enemy_height//4), 3)

    # Mouth
    pygame.draw.arc(screen, BLACK,
                   (x + enemy_width//4, y + 3*enemy_height//4, enemy_width//2, enemy_height//4),
                   0, math.pi, 2)

def show_score():
    """Display the current score"""
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def show_game_over():
    """Display game over message"""
    game_over_text = font.render("GAME OVER", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

def reset_game():
    """Reset the game state"""
    global player_x, player_y, bullet_state, bullet_x, bullet_y, enemies, score, game_over

    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    bullet_state = "ready"
    bullet_x = 0
    bullet_y = player_y
    enemies = []
    score = 0

    for i in range(num_enemies):
        enemies.append({
            'x': random.randint(0, WIDTH - enemy_width),
            'y': random.randint(50, 200),
            'direction': 1,
            'move_down': False
        })

    game_over = False

# Main game loop
running = True
while running:
    # Fill the screen with black
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x -= player_speed
            if event.key == pygame.K_RIGHT:
                player_x += player_speed
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bullet_x = player_x + player_width//2 - bullet_width//2
                bullet_y = player_y
                fire_bullet(bullet_x, bullet_y)

            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_q:
                    running = False

    # Keep player within screen bounds
    if player_x <= 0:
        player_x = 0
    elif player_x >= WIDTH - player_width:
        player_x = WIDTH - player_width

    # Enemy movement
    for enemy in enemies[:]:
        # Move enemies
        enemy['x'] += enemy_speed * enemy['direction']

        # Change direction if hit screen edge
        if enemy['x'] <= 0 or enemy['x'] >= WIDTH - enemy_width:
            enemy['direction'] *= -1
            enemy['y'] += 20  # Move down

            # Check if enemy reached bottom
            if enemy['y'] > HEIGHT - 50:
                game_over = True

        # Check for collision with bullet
        if (bullet_state == "fire" and
            bullet_x < enemy['x'] + enemy_width and
            bullet_x + bullet_width > enemy['x'] and
            bullet_y < enemy['y'] + enemy_height and
            bullet_y + bullet_height > enemy['y']):

            bullet_state = "ready"
            enemies.remove(enemy)
            score += 10
            # Add new enemy if we have less than original number
            if len(enemies) < num_enemies:
                enemies.append({
                    'x': random.randint(0, WIDTH - enemy_width),
                    'y': random.randint(50, 200),
                    'direction': enemy_speed,
                    'move_down': False
                })

        # Check for collision with player
        if (enemy['y'] < player_y + player_height and
            enemy['y'] + enemy_height > player_y and
            enemy['x'] < player_x + player_width and
            enemy['x'] + enemy_width > player_x):
            game_over = True

    # Bullet movement
    if bullet_state == "fire":
        draw_bullet(bullet_x, bullet_y)
        bullet_y -= bullet_speed
        if bullet_y <= 0:
            bullet_state = "ready"

    # Draw all game elements
    draw_player(player_x, player_y)

    for enemy in enemies:
        draw_enemy(enemy['x'], enemy['y'])

    show_score()

    if game_over:
        show_game_over()

    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
