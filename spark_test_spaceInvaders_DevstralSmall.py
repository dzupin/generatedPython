# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Devstral-Small-2-24B-Instruct-2512-Q8_0.gguf  --mmproj /AI/models/Devstral-Small-2-24B-Instruct-2512-mmproj-BF16.gguf

import pygame
import random
import math
import sys
from pygame import mixer

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Title and Icon
pygame.display.set_caption("Space Invaders")
# Create a simple icon using pygame.draw
icon = pygame.Surface((32, 32))
pygame.draw.polygon(icon, (0, 255, 0), [(16, 0), (0, 16), (32, 16)])
pygame.draw.circle(icon, (255, 255, 0), (16, 16), 10)
pygame.display.set_icon(icon)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Background
def draw_background():
    screen.fill(BLACK)
    # Draw stars
    for _ in range(20):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        pygame.draw.circle(screen, WHITE, (x, y), size)

# Simple sound effects (we'll use beep sounds since we can't load external files)
def play_beep(frequency, duration):
    try:
        mixer.init(frequency=frequency)
        mixer.Sound(buffer=mixer.Sound.array([math.sin(math.pi * frequency * i / 44100) * 32767 for i in range(int(44100 * duration))]).get_raw()).play()
    except:
        pass  # Silently fail if sound can't be played

# Player
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 60
player_width = 50
player_height = 40
player_speed = 5
player_x_change = 0

def draw_player(x, y):
    # Draw player spaceship
    pygame.draw.polygon(screen, GREEN, [(x, y), (x + player_width, y), (x + player_width // 2, y - 20)])
    # Draw player base
    pygame.draw.rect(screen, GREEN, (x + player_width // 2 - 10, y, 20, player_height))
    # Draw thruster
    pygame.draw.polygon(screen, RED, [(x + player_width // 2 - 5, y + player_height), (x + player_width // 2 + 5, y + player_height), (x + player_width // 2, y + player_height + 10)])

# Enemy
# Enemy dimensions
enemy_width = 50
enemy_height = 40
num_enemies = 6
enemies = []
for _ in range(num_enemies):
    enemies.append({
        'x': random.randint(0, SCREEN_WIDTH - 64),
        'y': random.randint(50, 150),
        'x_change': 2,
        'y_change': 40,
        'width': enemy_width,
        'height': enemy_height
    })

def draw_enemy(enemy):
    # Draw enemy UFO
    pygame.draw.ellipse(screen, RED, (enemy['x'], enemy['y'], enemy['width'], enemy['height'] // 2))
    # Draw enemy body
    pygame.draw.rect(screen, BLUE,
                     (enemy['x'] + 5, enemy['y'] + enemy['height'] // 2, enemy['width'] - 10, enemy['height'] // 2))
    # Draw eyes (centered properly)
    pygame.draw.circle(screen, WHITE, (enemy['x'] + 15, enemy['y'] + 15), 5)
    pygame.draw.circle(screen, WHITE, (enemy['x'] + enemy['width'] - 25, enemy['y'] + 15), 5)  # Adjusted position
    # Draw antenna (centered)
    pygame.draw.line(screen, WHITE, (enemy['x'] + enemy['width'] // 2, enemy['y']),
                     (enemy['x'] + enemy['width'] // 2, enemy['y'] - 10), 2)


# Bullet
bullet_x = 0
bullet_y = SCREEN_HEIGHT - 60
bullet_width = 5
bullet_height = 15
bullet_speed = 7
bullet_state = "ready"  # ready - not fired, fire - moving

def draw_bullet(x, y):
    pygame.draw.rect(screen, YELLOW, (x + player_width // 2 - bullet_width // 2, y - 20, bullet_width, bullet_height))

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    # Simple collision detection using rectangles
    if (bullet_x + bullet_width >= enemy_x and bullet_x <= enemy_x + enemy['width'] and
        bullet_y + bullet_height >= enemy_y and bullet_y <= enemy_y + enemy['height']):
        return True
    return False

# Score
score_value = 0
font = pygame.font.SysFont('Arial', 32)  # Use system font instead of external file

def show_score(x, y):
    score = font.render(f"Score: {score_value}", True, WHITE)
    screen.blit(score, (x, y))

# Game Over
over_font = pygame.font.SysFont('Arial', 64)

def game_over_text():
    over_text = over_font.render("GAME OVER", True, RED)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 32))

# Game loop
running = True
clock = pygame.time.Clock()
FPS = 60

while running:
    # Draw background
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -player_speed
            if event.key == pygame.K_RIGHT:
                player_x_change = player_speed
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    play_beep(1000, 0.1)  # Laser sound
                    bullet_x = player_x + player_width // 2 - bullet_width // 2
                    bullet_y = player_y - 20  # Set bullet position just above player
                    bullet_state = "fire"

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    # Player movement
    player_x += player_x_change

    # Boundary check for player
    if player_x <= 0:
        player_x = 0
    elif player_x >= SCREEN_WIDTH - player_width:
        player_x = SCREEN_WIDTH - player_width

    # Enemy movement
    for i, enemy in enumerate(enemies):
        # Game over condition
        if enemy['y'] > SCREEN_HEIGHT - 100:
            game_over_text()
            # Reset game after a few seconds
            pygame.display.update()
            pygame.time.wait(2000)
            # Reset enemies
            for e in enemies:
                e['x'] = random.randint(0, SCREEN_WIDTH - 64)
                e['y'] = random.randint(50, 150)
            score_value = 0
            break

        enemy['x'] += enemy['x_change']
        if enemy['x'] <= 0:
            enemy['x_change'] = 2
            enemy['y'] += enemy['y_change']
        elif enemy['x'] >= SCREEN_WIDTH - enemy['width']:
            enemy['x_change'] = -2
            enemy['y'] += enemy['y_change']

        # Collision
        if bullet_state == "fire" and is_collision(enemy['x'], enemy['y'], bullet_x + player_width // 2 - bullet_width // 2, bullet_y - 20):
            play_beep(500, 0.2)  # Explosion sound
            bullet_state = "ready"
            score_value += 1
            enemy['x'] = random.randint(0, SCREEN_WIDTH - enemy['width'])
            enemy['y'] = random.randint(50, 150)

        draw_enemy(enemy)

    # Bullet movement
    if bullet_state == "fire":
        draw_bullet(bullet_x, bullet_y)
        bullet_y -= bullet_speed
        if bullet_y <= 0:
            bullet_state = "ready"
            bullet_y = player_y  # Reset bullet position

    draw_player(player_x, player_y)
    show_score(10, 10)
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
