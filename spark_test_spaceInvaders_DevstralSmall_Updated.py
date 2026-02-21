# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library without using external files for graphic.
# 0-shot result
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
pygame.display.set_caption("Space Invaders Extreme")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Game difficulty levels
DIFFICULTY_LEVELS = [
    {"enemy_speed": 1, "enemy_count": 4, "bullet_speed": 5, "player_speed": 5},
    {"enemy_speed": 1.5, "enemy_count": 6, "bullet_speed": 6, "player_speed": 5},
    {"enemy_speed": 2, "enemy_count": 8, "bullet_speed": 7, "player_speed": 6},
    {"enemy_speed": 2.5, "enemy_count": 10, "bullet_speed": 8, "player_speed": 6}
]

# Player
player_width = 50
player_height = 20
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = DIFFICULTY_LEVELS[0]["player_speed"]
player_lives = 3
player_invincible = False
invincibility_timer = 0

# Bullet
bullet_width = 5
bullet_height = 15
bullet_speed = DIFFICULTY_LEVELS[0]["bullet_speed"]
bullets = []  # List to track all bullets
bullet_count = 1
bullet_cooldown = 0

# Enemy
enemy_width = 40
enemy_height = 40
enemy_speed = DIFFICULTY_LEVELS[0]["enemy_speed"]
enemy_direction = 1
enemies = []
enemy_types = ["basic", "fast", "tank", "boss"]
enemy_scores = {"basic": 10, "fast": 20, "tank": 30, "boss": 100}

# Power-ups
powerups = []
powerup_types = ["extra_life", "double_shot", "speed_boost", "shield"]
powerup_active = {}
powerup_timer = {}
powerup_duration = 10000  # 10 seconds in milliseconds

# Score and high score
score = 0
high_score = 0
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

# Game state
current_level = 0
game_over = False
paused = False
start_screen = True
wave_count = 0

# Clock for controlling frame rate
clock = pygame.time.Clock()

def draw_player(x, y):
    """Draw the player spaceship with improved graphics"""
    # Main body
    pygame.draw.rect(screen, GREEN, (x, y, player_width, player_height))

    # Thrusters (when moving)
    if player_invincible:
        # Invincibility glow
        glow_size = 5
        for i in range(1, glow_size + 1):
            alpha = 255 - int(255 * i / glow_size)
            s = pygame.Surface((player_width + i*2, player_height + i*2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*GREEN, alpha), (i, i, player_width, player_height))
            screen.blit(s, (x - i, y - i))

    # Add a simple triangle for the top
    pygame.draw.polygon(screen, GREEN, [
        (x + player_width//2, y - 10),
        (x + player_width, y),
        (x, y)
    ])

    # Draw lives indicator
    lives_x = 10
    for i in range(player_lives):
        pygame.draw.rect(screen, GREEN, (lives_x + i * 30, HEIGHT - 30, 20, 10))
        pygame.draw.polygon(screen, GREEN, [
            (lives_x + i * 30 + 10, HEIGHT - 40),
            (lives_x + i * 30 + 20, HEIGHT - 30),
            (lives_x + i * 30, HEIGHT - 30)
        ])

def fire_bullet(x, y):
    """Fire bullet(s) depending on power-up status"""
    global bullet_cooldown

    if bullet_cooldown > 0:
        return

   #  bullets_sound = pygame.mixer.Sound("sounds/bullet.wav") if hasattr(pygame.mixer, 'Sound') else None

    if bullet_count == 1:
        # Single bullet
        bullets.append({
            'x': x + player_width//2 - bullet_width//2,
            'y': y,
            'width': bullet_width,
            'height': bullet_height,
            'active': True
        })
        bullet_cooldown = 10  # Cooldown frames
    else:
        # Double shot
        for i in [-1, 1]:
            bullets.append({
                'x': x + player_width//2 - bullet_width//2 + i * 15,
                'y': y,
                'width': bullet_width,
                'height': bullet_height,
                'active': True
            })
        bullet_cooldown = 15  # Cooldown frames

def draw_bullet(bullet):
    """Draw the bullet with improved graphics"""
    x, y = bullet['x'], bullet['y']
    pygame.draw.rect(screen, CYAN, (x, y, bullet['width'], bullet['height']))
    # Add a simple trail effect
    for i in range(3):
        alpha = 100 - i * 30
        s = pygame.Surface((bullet['width'] + 2, bullet['height'] + 2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*CYAN, alpha), (1, 1, bullet['width'], bullet['height']))
        screen.blit(s, (x - 1, y + i))

def draw_enemy(enemy):
    """Draw different types of enemies with improved graphics"""
    x, y = enemy['x'], enemy['y']
    width, height = enemy['width'], enemy['height']

    if enemy['type'] == 'basic':
        # Draw the main body
        pygame.draw.rect(screen, RED, (x, y, width, height))

        # Add some details to make it look like an alien
        # Eyes
        pygame.draw.circle(screen, BLACK, (x + width//4, y + height//4), 5)
        pygame.draw.circle(screen, BLACK, (x + 3*width//4, y + height//4), 5)
        pygame.draw.circle(screen, WHITE, (x + width//4, y + height//4), 3)
        pygame.draw.circle(screen, WHITE, (x + 3*width//4, y + height//4), 3)

        # Mouth
        pygame.draw.arc(screen, BLACK,
                       (x + width//4, y + 3*height//4, width//2, height//4),
                       0, math.pi, 2)

    elif enemy['type'] == 'fast':
        # Fast enemy (blue)
        pygame.draw.rect(screen, BLUE, (x, y, width, height))
        # Add lightning effect
        for i in range(3):
            pygame.draw.line(screen, WHITE,
                            (x + i*10, y),
                            (x + i*10, y + height),
                            2)

    elif enemy['type'] == 'tank':
        # Tank enemy (purple)
        pygame.draw.rect(screen, PURPLE, (x, y, width, height))
        # Add tank treads
        for i in range(2):
            pygame.draw.circle(screen, BLACK,
                              (x + i*width//3, y + height),
                              height//4)

    elif enemy['type'] == 'boss':
        # Boss enemy (yellow, larger)
        boss_width = width
        boss_height = height
        pygame.draw.rect(screen, YELLOW, (x, y, boss_width, boss_height))

        # Add boss details
        # Eyes
        pygame.draw.circle(screen, BLACK, (x + boss_width//4, y + boss_height//4), 10)
        pygame.draw.circle(screen, BLACK, (x + 3*boss_width//4, y + boss_height//4), 10)
        pygame.draw.circle(screen, RED, (x + boss_width//4, y + boss_height//4), 5)
        pygame.draw.circle(screen, RED, (x + 3*boss_width//4, y + boss_height//4), 5)

        # Mouth
        pygame.draw.arc(screen, BLACK,
                       (x + boss_width//4, y + 3*boss_height//4, boss_width//2, boss_height//4),
                       0, math.pi, 2)

def draw_powerup(powerup):
    """Draw power-up items"""
    x, y = powerup['x'], powerup['y']
    size = 20

    if powerup['type'] == 'extra_life':
        # Heart shape
        pygame.draw.circle(screen, RED, (x + size//2, y + size//2), size//2)
        pygame.draw.circle(screen, RED, (x + size//2, y + size//2), size//4)
        pygame.draw.circle(screen, WHITE, (x + size//2, y + size//2), size//8)
        # Add a triangle for the bottom point
        pygame.draw.polygon(screen, RED, [
            (x + size//2, y + size),
            (x, y + size//2),
            (x + size, y + size//2)
        ])

    elif powerup['type'] == 'double_shot':
        # Double gun
        pygame.draw.rect(screen, GREEN, (x, y + size//4, size, size//2))
        pygame.draw.polygon(screen, GREEN, [
            (x + size//2, y),
            (x + size, y + size//4),
            (x + size//2, y + size//2)
        ])

    elif powerup['type'] == 'speed_boost':
        # Speed lines
        for i in range(3):
            pygame.draw.line(screen, BLUE, (x + i*size//3, y), (x + i*size//3, y + size), 3)

    elif powerup['type'] == 'shield':
        # Shield icon
        pygame.draw.circle(screen, CYAN, (x + size//2, y + size//2), size//2)
        # Add some waves
        for i in range(3):
            pygame.draw.arc(screen, CYAN,
                           (x + size//2 - size//4, y + size//2 - size//4 + i*2,
                            size//2, size//2),
                           0, math.pi * 2, 2)

def show_score():
    """Display the current score and high score"""
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    level_text = font.render(f"Level: {current_level + 1}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (WIDTH - 200, 10))
    screen.blit(level_text, (WIDTH//2 - 50, 10))

def show_game_over():
    """Display game over message with score"""
    game_over_text = large_font.render("GAME OVER", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)

    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 120))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 20))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))

def show_start_screen():
    """Display the start screen"""
    title_text = large_font.render("SPACE INVADERS EXTREME", True, WHITE)
    start_text = font.render("Press SPACE to Start", True, WHITE)
    controls_text = font.render("Controls: Arrow keys to move, SPACE to shoot", True, WHITE)

    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT//2 + 50))

def show_pause_screen():
    """Display the pause screen"""
    pause_text = large_font.render("PAUSED", True, WHITE)
    resume_text = font.render("Press P to Resume", True, WHITE)

    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 + 20))

def create_enemies(count, wave_count):
    """Create a wave of enemies with different types"""
    enemies = []
    enemy_types_this_wave = []

    # Determine enemy types based on wave count
    if wave_count < 3:
        enemy_types_this_wave = ['basic'] * count
    elif wave_count < 6:
        enemy_types_this_wave = ['basic'] * (count * 3 // 4) + ['fast'] * (count // 4)
    else:
        enemy_types_this_wave = ['basic'] * (count // 3) + ['fast'] * (count // 3) + ['tank'] * (count // 3)

    # Shuffle the enemy types
    random.shuffle(enemy_types_this_wave)

    # Create boss enemy every 5 waves
    if wave_count % 5 == 0:
        enemies.append({
            'type': 'boss',
            'x': WIDTH // 2 - enemy_width * 1.5,
            'y': 50,
            'direction': 1,
            'move_down': False,
            'width': enemy_width * 2,
            'height': enemy_height * 2
        })
    else:
        # Create regular enemies
        for i in range(count):
            enemy_type = enemy_types_this_wave[i % len(enemy_types_this_wave)]
            enemies.append({
                'type': enemy_type,
                'x': random.randint(0, WIDTH - enemy_width),
                'y': random.randint(50, 150),
                'direction': 1,
                'move_down': False,
                'width': enemy_width,
                'height': enemy_height
            })

    return enemies

def reset_game():
    """Reset the game state"""
    global player_x, player_y, player_lives, player_invincible, bullets, \
           enemies, score, current_level, game_over, \
           paused, powerups, powerup_active, powerup_timer, wave_count

    # Reset player
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    player_lives = 3
    player_invincible = True
    invincibility_timer = pygame.time.get_ticks() + 3000  # 3 seconds invincibility

    # Reset bullets
    bullets = []
    bullet_count = 1

    # Reset power-ups
    powerups = []
    powerup_active = {}
    powerup_timer = {}

    # Reset game state
    enemies = create_enemies(DIFFICULTY_LEVELS[current_level]["enemy_count"], wave_count)
    score = 0
    game_over = False
    paused = False

    # Reset difficulty level
    global enemy_speed, bullet_speed, player_speed
    enemy_speed = DIFFICULTY_LEVELS[current_level]["enemy_speed"]
    bullet_speed = DIFFICULTY_LEVELS[current_level]["bullet_speed"]
    player_speed = DIFFICULTY_LEVELS[current_level]["player_speed"]

# Main game loop
running = True
while running:
    # Fill the screen with black
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if start_screen:
                if event.key == pygame.K_SPACE:
                    start_screen = False
                    reset_game()
            elif game_over:
                if event.key == pygame.K_r:
                    reset_game()
                    start_screen = False
                if event.key == pygame.K_q:
                    running = False
            elif not paused:
                if event.key == pygame.K_LEFT:
                    player_x -= player_speed
                if event.key == pygame.K_RIGHT:
                    player_x += player_speed
                if event.key == pygame.K_SPACE:
                    fire_bullet(player_x, player_y)
                if event.key == pygame.K_p:
                    paused = True
            else:  # paused
                if event.key == pygame.K_p:
                    paused = False

    # Keep player within screen bounds
    if player_x <= 0:
        player_x = 0
    elif player_x >= WIDTH - player_width:
        player_x = WIDTH - player_width

    # Handle power-up timers
    current_time = pygame.time.get_ticks()
    for powerup_type in list(powerup_active.keys()):
        if current_time > powerup_timer[powerup_type]:
            # Power-up expired
            if powerup_type == "double_shot":
                bullet_count = 1
            elif powerup_type == "speed_boost":
                player_speed = DIFFICULTY_LEVELS[current_level]["player_speed"]
            elif powerup_type == "shield":
                player_invincible = False

            del powerup_active[powerup_type]
            del powerup_timer[powerup_type]

    # Handle invincibility timer
    if player_invincible and current_time > invincibility_timer:
        player_invincible = False

    if paused and not start_screen and not game_over:
        show_pause_screen()
        pygame.display.update()
        clock.tick(60)
        continue

    if start_screen:
        show_start_screen()
        pygame.display.update()
        clock.tick(60)
        continue

    # Bullet movement and collision detection
    for bullet in bullets[:]:
        bullet['y'] -= bullet_speed

        # Check if bullet went off screen
        if bullet['y'] <= 0:
            bullets.remove(bullet)
            continue

        # Check for collision with enemies
        for enemy in enemies[:]:
            if (bullet['x'] < enemy['x'] + enemy['width'] and
                bullet['x'] + bullet['width'] > enemy['x'] and
                bullet['y'] < enemy['y'] + enemy['height'] and
                bullet['y'] + bullet['height'] > enemy['y']):

                score += enemy_scores.get(enemy['type'], 10)
                bullets.remove(bullet)
                enemies.remove(enemy)

                # Random chance to drop power-up
                if random.random() < 0.2:
                    powerups.append({
                        'type': random.choice(powerup_types),
                        'x': enemy['x'] + enemy['width']//2 - 10,
                        'y': enemy['y'] + enemy['height'],
                        'width': 20,
                        'height': 20
                    })
                break

    # Enemy movement
    all_enemies_dead = len(enemies) == 0
    for enemy in enemies[:]:
        # Move enemies
        enemy['x'] += enemy_speed * enemy['direction']

        # Change direction if hit screen edge
        if enemy['x'] <= 0 or enemy['x'] >= WIDTH - enemy['width']:
            enemy['direction'] *= -1
            enemy['y'] += 20  # Move down

            # Check if enemy reached bottom
            if enemy['y'] > HEIGHT - 50:
                player_lives -= 1
                if player_lives <= 0:
                    if score > high_score:
                        high_score = score
                    game_over = True
                else:
                    # Reset enemies for this wave
                    enemies = create_enemies(DIFFICULTY_LEVELS[current_level]["enemy_count"], wave_count)

    # Check if all enemies are dead
    if all_enemies_dead:
        wave_count += 1
        if wave_count % 3 == 0 and current_level < len(DIFFICULTY_LEVELS) - 1:
            current_level += 1
            enemy_speed = DIFFICULTY_LEVELS[current_level]["enemy_speed"]
            bullet_speed = DIFFICULTY_LEVELS[current_level]["bullet_speed"]
            player_speed = DIFFICULTY_LEVELS[current_level]["player_speed"]

        enemies = create_enemies(DIFFICULTY_LEVELS[current_level]["enemy_count"], wave_count)

    # Power-up movement and collection
    for powerup in powerups[:]:
        powerup['y'] += 2
        if powerup['y'] > HEIGHT:
            powerups.remove(powerup)
            continue

        # Check if player collected power-up
        if (player_x < powerup['x'] + powerup['width'] and
            player_x + player_width > powerup['x'] and
            player_y < powerup['y'] + powerup['height'] and
            player_y + player_height > powerup['y']):

            if powerup['type'] == "extra_life":
                player_lives += 1
            elif powerup['type'] == "double_shot":
                bullet_count = 2
                powerup_active["double_shot"] = True
                powerup_timer["double_shot"] = current_time + powerup_duration
            elif powerup['type'] == "speed_boost":
                player_speed = DIFFICULTY_LEVELS[current_level]["player_speed"] * 1.5
                powerup_active["speed_boost"] = True
                powerup_timer["speed_boost"] = current_time + powerup_duration
            elif powerup['type'] == "shield":
                player_invincible = True
                invincibility_timer = current_time + powerup_duration
                powerup_active["shield"] = True
                powerup_timer["shield"] = current_time + powerup_duration

            powerups.remove(powerup)

    # Draw all game elements
    draw_player(player_x, player_y)

    for bullet in bullets:
        draw_bullet(bullet)

    for enemy in enemies:
        draw_enemy(enemy)

    for powerup in powerups:
        draw_powerup(powerup)

    show_score()

    if game_over:
        show_game_over()

    # Update bullet cooldown
    if bullet_cooldown > 0:
        bullet_cooldown -= 1

    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
