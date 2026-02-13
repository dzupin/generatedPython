# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library.
# first prompt 1-shot
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# enhanced game 0-shot
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
pygame.display.set_caption("Space Invaders - Enhanced Edition")
# Create a more detailed icon
icon = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.polygon(icon, (0, 255, 0), [(16, 0), (0, 16), (32, 16)])
pygame.draw.circle(icon, (255, 255, 0), (16, 16), 10)
pygame.draw.polygon(icon, (255, 0, 0), [(16, 10), (10, 16), (22, 16)])
pygame.display.set_icon(icon)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Game variables
score_value = 0
lives = 3
level = 1
high_score = 0
game_active = True
enemy_speed = 1.5
enemy_acceleration = 1.02
bullet_cooldown = 0
cooldown_time = 20  # Frames

# Load high score if exists
try:
    with open('highscore.txt', 'r') as f:
        high_score = int(f.read())
except:
    pass

# Background
def draw_background():
    screen.fill(BLACK)
    # Draw stars (reduced number for less distraction)
    for _ in range(80):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        alpha = random.randint(50, 150)
        star = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(star, (*WHITE, alpha), (size, size), size)
        screen.blit(star, (x, y))
    # Add some moving stars for depth
    for _ in range(20):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        alpha = random.randint(50, 150)
        star = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(star, (*WHITE, alpha), (size, size), size)
        screen.blit(star, (x, y - 2))  # Subtle movement

# Simple sound effects
def play_beep(frequency, duration):
    try:
        mixer.init(frequency=frequency)
        sound = mixer.Sound(buffer=mixer.Sound.array([math.sin(math.pi * frequency * i / 44100) * 32767 for i in range(int(44100 * duration))]).get_raw())
        sound.play()
    except:
        pass

# Player
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 60
player_width = 50
player_height = 40
player_speed = 6
player_x_change = 0
player_invulnerable = False
invulnerable_timer = 0
invulnerable_duration = 120  # Frames

def draw_player(x, y):
    if player_invulnerable and invulnerable_timer % 10 < 5:
        return  # Make player blink when invulnerable

    # Draw player spaceship with more detail
    pygame.draw.polygon(screen, GREEN, [(x, y), (x + player_width, y), (x + player_width // 2, y - 20)])
    pygame.draw.rect(screen, GREEN, (x + player_width // 2 - 10, y, 20, player_height))
    pygame.draw.polygon(screen, RED, [(x + player_width // 2 - 5, y + player_height), (x + player_width // 2 + 5, y + player_height), (x + player_width // 2, y + player_height + 10)])

    # Draw lives indicator
    for i in range(lives):
        pygame.draw.polygon(screen, GREEN, [(10 + i * 25, 10), (35 + i * 25, 10), (25 + i * 25, -10)])

# Enemy
num_enemies = 6
enemies = []
enemy_colors = [RED, BLUE, PURPLE, CYAN]
enemy_types = ['standard', 'fast', 'tank', 'shooter']
enemy_speed_multipliers = {'standard': 1, 'fast': 1.5, 'tank': 0.7, 'shooter': 1.2}

for _ in range(num_enemies):
    enemy_type = random.choice(enemy_types)
    enemies.append({
        'x': random.randint(0, SCREEN_WIDTH - 64),
        'y': random.randint(50, 150),
        'x_change': enemy_speed * enemy_speed_multipliers[enemy_type],
        'y_change': 40,
        'width': 50,
        'height': 40,
        'type': enemy_type,
        'color': random.choice(enemy_colors),
        'points': {'standard': 10, 'fast': 20, 'tank': 5, 'shooter': 15}[enemy_type],
        'shoot_timer': random.randint(0, 180),
        'bullet_y': 0,
        'bullet_state': 'ready'
    })

def draw_enemy(enemy):
    # Draw enemy UFO
    pygame.draw.ellipse(screen, enemy['color'], (enemy['x'], enemy['y'], enemy['width'], enemy['height'] // 2))

    # Draw different enemy types
    if enemy['type'] == 'standard':
        # Standard enemy
        pygame.draw.rect(screen, BLUE, (enemy['x'] + 5, enemy['y'] + enemy['height'] // 2, enemy['width'] - 10, enemy['height'] // 2))
    elif enemy['type'] == 'fast':
        # Fast enemy (green)
        pygame.draw.rect(screen, (0, 255, 0), (enemy['x'] + 5, enemy['y'] + enemy['height'] // 2, enemy['width'] - 10, enemy['height'] // 2))
    elif enemy['type'] == 'tank':
        # Tank enemy (thicker)
        pygame.draw.rect(screen, (139, 69, 19), (enemy['x'] + 5, enemy['y'] + enemy['height'] // 2, enemy['width'] - 10, enemy['height'] // 2))
        # Add armor plates
        pygame.draw.rect(screen, (255, 255, 255), (enemy['x'] + 10, enemy['y'] + 20, 10, 10))
        pygame.draw.rect(screen, (255, 255, 255), (enemy['x'] + 30, enemy['y'] + 20, 10, 10))
    elif enemy['type'] == 'shooter':
        # Shooter enemy (with guns)
        pygame.draw.rect(screen, (255, 165, 0), (enemy['x'] + 5, enemy['y'] + enemy['height'] // 2, enemy['width'] - 10, enemy['height'] // 2))
        # Draw guns
        pygame.draw.polygon(screen, RED, [(enemy['x'] + 15, enemy['y'] + 30), (enemy['x'] + 25, enemy['y'] + 35), (enemy['x'] + 25, enemy['y'] + 30)])
        pygame.draw.polygon(screen, RED, [(enemy['x'] + 25, enemy['y'] + 30), (enemy['x'] + 35, enemy['y'] + 35), (enemy['x'] + 35, enemy['y'] + 30)])

    # Draw eyes (centered properly)
    pygame.draw.circle(screen, WHITE, (enemy['x'] + 15, enemy['y'] + 15), 5)
    pygame.draw.circle(screen, WHITE, (enemy['x'] + enemy['width'] - 25, enemy['y'] + 15), 5)

    # Draw antenna (centered)
    pygame.draw.line(screen, WHITE, (enemy['x'] + enemy['width'] // 2, enemy['y']), (enemy['x'] + enemy['width'] // 2, enemy['y'] - 10), 2)

    # Draw enemy bullets if they exist
    if enemy['bullet_state'] == 'fire':
        pygame.draw.rect(screen, enemy['color'], (enemy['x'] + enemy['width'] // 2 - 2, enemy['bullet_y'], 4, 10))

# Bullets
player_bullets = []
enemy_bullets = []

def add_player_bullet(x, y):
    player_bullets.append({
        'x': x,
        'y': y,
        'state': 'fire',
        'speed': 7
    })

def add_enemy_bullet(enemy_x, enemy_y, color):
    enemy_bullets.append({
        'x': enemy_x + 23,  # Center of enemy
        'y': enemy_y + 40,  # Bottom of enemy
        'state': 'fire',
        'speed': 3,
        'color': color
    })

def draw_bullet(x, y, width=5, height=15, color=YELLOW):
    pygame.draw.rect(screen, color, (x, y, width, height))

def is_collision(obj1_x, obj1_y, obj1_width, obj1_height, obj2_x, obj2_y, obj2_width, obj2_height):
    return (obj1_x < obj2_x + obj2_width and
            obj1_x + obj1_width > obj2_x and
            obj1_y < obj2_y + obj2_height and
            obj1_y + obj1_height > obj2_y)

# UI Elements
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 20)
over_font = pygame.font.SysFont('Arial', 64)

def show_score(x, y):
    score_text = font.render(f"Score: {score_value}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (x, y))
    screen.blit(level_text, (x, y + 35))

def show_high_score(x, y):
    high_score_text = small_font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (x, SCREEN_HEIGHT - 30))

def show_pause():
    pause_text = over_font.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 32))
    resume_text = font.render("Press P to Resume", True, WHITE)
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Final Score: {score_value}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)

    screen.blit(over_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 100))

    # Update high score
    if score_value > high_score:
        with open('highscore.txt', 'w') as f:
            f.write(str(score_value))

def show_level_up():
    level_up_text = over_font.render(f"LEVEL {level} UNLOCKED!", True, GREEN)
    screen.blit(level_up_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 50))
    pygame.display.update()
    pygame.time.wait(1500)

# Game loop
running = True
clock = pygame.time.Clock()
FPS = 60
pause = False
level_up_triggered = False

while running:
    # Draw background
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -player_speed
            if event.key == pygame.K_RIGHT:
                player_x_change = player_speed
            if event.key == pygame.K_SPACE and game_active and not pause:
                if bullet_cooldown == 0 and not player_invulnerable:
                    play_beep(1000, 0.1)  # Laser sound
                    bullet_x = player_x + player_width // 2 - 2
                    bullet_y = player_y - 20
                    add_player_bullet(bullet_x, bullet_y)
                    bullet_cooldown = cooldown_time
            if event.key == pygame.K_p:
                pause = not pause
            if event.key == pygame.K_r and not game_active:
                # Reset game
                score_value = 0
                lives = 3
                level = 1
                game_active = True
                player_x = SCREEN_WIDTH // 2
                player_invulnerable = False
                enemy_speed = 1.5
                for enemy in enemies:
                    enemy['x'] = random.randint(0, SCREEN_WIDTH - enemy['width'])
                    enemy['y'] = random.randint(50, 150)
                    enemy['x_change'] = enemy_speed * enemy_speed_multipliers[enemy['type']]
                    enemy['points'] = {'standard': 10, 'fast': 20, 'tank': 5, 'shooter': 15}[enemy['type']]
                    enemy['bullet_state'] = 'ready'
                    enemy['bullet_y'] = 0

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    if not game_active:
        game_over_text()
        pygame.display.update()
        continue

    if pause:
        show_pause()
        pygame.display.update()
        continue

    # Player movement
    player_x += player_x_change

    # Boundary check for player
    if player_x <= 0:
        player_x = 0
    elif player_x >= SCREEN_WIDTH - player_width:
        player_x = SCREEN_WIDTH - player_width

    # Player invulnerability timer
    if player_invulnerable:
        invulnerable_timer -= 1
        if invulnerable_timer <= 0:
            player_invulnerable = False

    # Bullet cooldown
    if bullet_cooldown > 0:
        bullet_cooldown -= 1

    # Player bullet movement
    for bullet in player_bullets[:]:
        if bullet['state'] == 'fire':
            draw_bullet(bullet['x'], bullet['y'])
            bullet['y'] -= bullet['speed']

            # Check if bullet went off screen
            if bullet['y'] <= 0:
                player_bullets.remove(bullet)

    # Enemy bullet movement
    for bullet in enemy_bullets[:]:
        if bullet['state'] == 'fire':
            draw_bullet(bullet['x'], bullet['y'], 4, 10, bullet['color'])
            bullet['y'] += bullet['speed']

            # Check if bullet went off screen
            if bullet['y'] >= SCREEN_HEIGHT:
                enemy_bullets.remove(bullet)
            # Check collision with player
            elif is_collision(bullet['x'], bullet['y'], 4, 10, player_x, player_y, player_width, player_height) and not player_invulnerable:
                # Player hit
                lives -= 1
                enemy_bullets.remove(bullet)
                player_invulnerable = True
                invulnerable_timer = invulnerable_duration
                if lives <= 0:
                    game_active = False

    # Enemy movement and behavior
    for i, enemy in enumerate(enemies[:]):
        # Game over condition
        if enemy['y'] > SCREEN_HEIGHT - 100:
            game_active = False
            break

        enemy['x'] += enemy['x_change']
        if enemy['x'] <= 0:
            enemy['x_change'] = enemy_speed * enemy_speed_multipliers[enemy['type']]
            enemy['y'] += enemy['y_change']
        elif enemy['x'] >= SCREEN_WIDTH - enemy['width']:
            enemy['x_change'] = -enemy_speed * enemy_speed_multipliers[enemy['type']]
            enemy['y'] += enemy['y_change']

        # Enemy shooting behavior (for shooter types)
        if enemy['type'] == 'shooter':
            enemy['shoot_timer'] += 1
            if enemy['shoot_timer'] >= 120:  # Shoot every 2 seconds
                enemy['shoot_timer'] = 0
                if enemy['bullet_state'] == 'ready':
                    add_enemy_bullet(enemy['x'], enemy['y'], enemy['color'])
                    enemy['bullet_state'] = 'fire'

        # Move enemy bullets
        if enemy['bullet_state'] == 'fire':
            enemy['bullet_y'] += 3
            if enemy['bullet_y'] >= SCREEN_HEIGHT:
                enemy['bullet_state'] = 'ready'
                enemy['bullet_y'] = 0

        # Collision with player bullets
        for bullet in player_bullets[:]:
            if bullet['state'] == 'fire' and is_collision(
                bullet['x'], bullet['y'], 5, 15,
                enemy['x'], enemy['y'], enemy['width'], enemy['height']):

                play_beep(500, 0.2)  # Explosion sound
                player_bullets.remove(bullet)
                enemies.remove(enemy)
                score_value += enemy['points']

                # Add new enemy if we're below the maximum
                if len(enemies) < num_enemies:
                    new_enemy_type = random.choice(enemy_types)
                    enemies.append({
                        'x': random.randint(0, SCREEN_WIDTH - 64),
                        'y': random.randint(50, 150),
                        'x_change': enemy_speed * enemy_speed_multipliers[new_enemy_type],
                        'y_change': 40,
                        'width': 50,
                        'height': 40,
                        'type': new_enemy_type,
                        'color': random.choice(enemy_colors),
                        'points': {'standard': 10, 'fast': 20, 'tank': 5, 'shooter': 15}[new_enemy_type],
                        'shoot_timer': random.randint(0, 180),
                        'bullet_y': 0,
                        'bullet_state': 'ready'
                    })
                break

        draw_enemy(enemy)

    # Level progression
    if len(enemies) == 0 and not level_up_triggered:
        level_up_triggered = True
        show_level_up()
        pygame.time.wait(1500)
        level += 1
        enemy_speed *= enemy_acceleration
        for enemy in enemies:
            enemy['x_change'] = enemy_speed * enemy_speed_multipliers[enemy['type']]

        # Spawn new enemies for next level
        while len(enemies) < num_enemies:
            new_enemy_type = random.choice(enemy_types)
            enemies.append({
                'x': random.randint(0, SCREEN_WIDTH - 64),
                'y': random.randint(50, 150),
                'x_change': enemy_speed * enemy_speed_multipliers[new_enemy_type],
                'y_change': 40,
                'width': 50,
                'height': 40,
                'type': new_enemy_type,
                'color': random.choice(enemy_colors),
                'points': {'standard': 10, 'fast': 20, 'tank': 5, 'shooter': 15}[new_enemy_type],
                'shoot_timer': random.randint(0, 180),
                'bullet_y': 0,
                'bullet_state': 'ready'
            })

        level_up_triggered = False

    draw_player(player_x, player_y)
    show_score(10, 10)
    show_high_score(10, 50)
    pygame.display.update()
    clock.tick(FPS)

# Save high score before quitting
try:
    with open('highscore.txt', 'w') as f:
        f.write(str(high_score))
except:
    pass

pygame.quit()
sys.exit()
