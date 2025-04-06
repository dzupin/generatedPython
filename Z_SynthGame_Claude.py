import pygame
import random
import math
import sys
# PROMPT 1 Claude 2.7 Sonnet:   write a retro synthwave style game in python using pygame library.
# PROMPT 2 Copy and paste error message to get code bellow

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Synthwave Racer")

# Colors (neon palette)
BLACK = (0, 0, 0)
PURPLE = (180, 0, 255)
PINK = (255, 0, 255)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
GRID_COLOR = (60, 20, 120)
SUN_COLOR = (255, 60, 60)

# Player settings
player_width = 60
player_height = 80
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 7

# Road settings
road_width = 500
horizon_y = HEIGHT // 3
road_color = (30, 30, 50)
stripe_width = 10
stripe_height = 30
stripe_gap = 30
stripes = []
for y in range(horizon_y, HEIGHT, stripe_height + stripe_gap):
    stripes.append(pygame.Rect(WIDTH // 2 - stripe_width // 2, y, stripe_width, stripe_height))

# Obstacle settings
obstacle_width = 60
obstacle_height = 80
obstacles = []
obstacle_speed = 5
obstacle_spawn_rate = 60  # Frames between obstacle spawns
obstacle_counter = 0

# Game settings
clock = pygame.time.Clock()
FPS = 60
score = 0
game_over = False
game_started = False
game_font = pygame.font.Font(None, 36)

# Music
try:
    pygame.mixer.music.load("synthwave.mp3")  # You'll need to provide your own music file
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely
except:
    print("Music file not found. Game will run without music.")

# Grid settings
grid_spacing = 50
grid_lines_horizon = 15  # Number of horizontal lines
vanishing_point_y = horizon_y
grid_depth = 5000


def draw_grid():
    # Draw horizontal grid lines with perspective
    for i in range(grid_lines_horizon):
        y_pos = horizon_y + i * ((HEIGHT - horizon_y) / grid_lines_horizon)
        intensity = 255 - int(i * (200 / grid_lines_horizon))
        line_color = (30, 0, min(intensity, 100))
        pygame.draw.line(screen, line_color, (0, y_pos), (WIDTH, y_pos), 2)

    # Draw vertical grid lines with perspective effect
    for x in range(0, WIDTH, grid_spacing):
        # Left side lines
        start_x = x
        start_y = HEIGHT
        end_x = ((x - WIDTH // 2) * horizon_y / HEIGHT) + WIDTH // 2
        end_y = horizon_y

        intensity = 100 - abs(x - WIDTH // 2) * (80 / WIDTH)
        if intensity > 0:
            pygame.draw.line(screen, GRID_COLOR, (start_x, start_y), (end_x, end_y), 2)


def draw_sun():
    # Draw retro sun
    pygame.draw.circle(screen, SUN_COLOR, (WIDTH // 2, horizon_y - 40), 60)
    for i in range(1, 6):
        # Make sure colors don't go below 0
        r = max(0, SUN_COLOR[0] - i * 20)
        g = max(0, SUN_COLOR[1] - i * 20)
        b = max(0, SUN_COLOR[2] - i * 20)
        pygame.draw.circle(screen, (r, g, b), (WIDTH // 2, horizon_y - 40), 60 - i * 8)


def draw_mountains():
    # Draw background mountains
    points = []
    for x in range(0, WIDTH + 50, 50):
        points.append((x, horizon_y - random.randint(20, 70) - 20))

    for i in range(len(points) - 1):
        polygon_points = [points[i], points[i + 1], (points[i + 1][0], horizon_y), (points[i][0], horizon_y)]
        pygame.draw.polygon(screen, (80, 0, 120), polygon_points)


def draw_stars():
    # Draw random stars in the sky
    for _ in range(50):
        x = random.randint(0, WIDTH)
        y = random.randint(0, horizon_y - 60)

        # Make stars twinkle
        if random.random() > 0.8:
            size = random.randint(1, 3)
            color_value = random.randint(200, 255)
            pygame.draw.circle(screen, (color_value, color_value, color_value), (x, y), size)


def draw_road():
    # Draw the main road
    road_left = WIDTH // 2 - road_width // 2
    pygame.draw.polygon(screen, road_color,
                        [(road_left, HEIGHT),
                         (WIDTH // 2 - 50, horizon_y),
                         (WIDTH // 2 + 50, horizon_y),
                         (road_left + road_width, HEIGHT)])

    # Draw road stripes with perspective
    for i, stripe in enumerate(stripes):
        # Scale stripes to create perspective
        scale_factor = 1 - ((stripe.y - horizon_y) / (HEIGHT - horizon_y)) * 0.7
        stripe_w = stripe_width * scale_factor

        stripe_x = WIDTH // 2 - stripe_w // 2
        pygame.draw.rect(screen, YELLOW, (stripe_x, stripe.y, stripe_w, stripe.height * scale_factor))


def draw_player(x, y):
    # Draw player car (retro neon style)
    pygame.draw.rect(screen, BLUE, (x, y, player_width, player_height))
    pygame.draw.rect(screen, PURPLE, (x + 5, y + 10, player_width - 10, player_height - 20))

    # Car windows
    pygame.draw.rect(screen, (0, 0, 30), (x + 10, y + 5, player_width - 20, 20))

    # Wheels
    pygame.draw.rect(screen, BLACK, (x - 5, y + 15, 8, 20))
    pygame.draw.rect(screen, BLACK, (x + player_width - 3, y + 15, 8, 20))
    pygame.draw.rect(screen, BLACK, (x - 5, y + player_height - 20, 8, 20))
    pygame.draw.rect(screen, BLACK, (x + player_width - 3, y + player_height - 20, 8, 20))

    # Neon glow effect
    pygame.draw.rect(screen, PINK, (x, y, player_width, player_height), 2)


def move_obstacles():
    global obstacles, score, game_over

    # Move existing obstacles
    for obs in obstacles[:]:
        # Calculate scale based on y position to create perspective
        scale_factor = (obs[1] - horizon_y) / (HEIGHT - horizon_y)
        if scale_factor < 0.1:
            scale_factor = 0.1

        speed_adjusted = obstacle_speed * (0.5 + scale_factor)
        width_adjusted = obstacle_width * scale_factor

        # Move obstacle
        obs[1] += speed_adjusted

        # Check if obstacle is off screen
        if obs[1] > HEIGHT:
            obstacles.remove(obs)
            score += 10

        # Check collision with player
        if obs[1] + obstacle_height * scale_factor > player_y and obs[1] < player_y + player_height:
            if obs[0] + width_adjusted > player_x and obs[0] < player_x + player_width:
                game_over = True


def spawn_obstacle():
    global obstacle_counter, obstacles

    obstacle_counter += 1
    if obstacle_counter >= obstacle_spawn_rate:
        # Spawn a new obstacle at a random position on the road
        road_left = WIDTH // 2 - road_width // 2
        road_right = road_left + road_width

        # Adjust for perspective
        perspective_road_left = WIDTH // 2 - 50
        perspective_road_right = WIDTH // 2 + 50

        # Random x position on the road at horizon
        obstacle_x = random.randint(int(perspective_road_left), int(perspective_road_right - obstacle_width * 0.2))
        obstacles.append([obstacle_x, horizon_y])

        obstacle_counter = 0


def draw_obstacles():
    for obs in obstacles:
        # Calculate scale based on y position to create perspective
        scale_factor = (obs[1] - horizon_y) / (HEIGHT - horizon_y)
        if scale_factor < 0.1:
            scale_factor = 0.1

        width_adjusted = obstacle_width * scale_factor
        height_adjusted = obstacle_height * scale_factor

        # Adjust x position for perspective
        x_center_offset = (obs[0] - WIDTH // 2)
        x_adjusted = WIDTH // 2 + x_center_offset * scale_factor

        # Draw obstacle
        pygame.draw.rect(screen, PINK, (x_adjusted, obs[1], width_adjusted, height_adjusted))
        pygame.draw.rect(screen, PURPLE, (x_adjusted, obs[1], width_adjusted, height_adjusted), 2)


def draw_game_over():
    # Draw game over screen
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, PINK)
    score_text = game_font.render(f"Final Score: {score}", True, BLUE)
    restart_text = game_font.render("Press R to Restart", True, YELLOW)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))


def draw_start_screen():
    # Draw start screen
    screen.fill(BLACK)

    # Draw retro grid for background
    draw_grid()
    draw_sun()
    draw_stars()

    # Title
    font = pygame.font.Font(None, 72)
    title_text = font.render("SYNTHWAVE RACER", True, PINK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))

    # Instructions
    instructions = [
        "Arrow keys to move",
        "Avoid obstacles",
        "Press SPACE to start"
    ]

    y_offset = HEIGHT // 2
    for instruction in instructions:
        text = game_font.render(instruction, True, BLUE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 40

    # Draw player car for decoration
    draw_player(WIDTH // 2 - player_width // 2, HEIGHT // 2 + 100)


def reset_game():
    global score, game_over, obstacles, obstacle_counter, player_x, player_y
    score = 0
    game_over = False
    obstacles = []
    obstacle_counter = 0
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_started:
                game_started = True
            if event.key == pygame.K_r and game_over:
                reset_game()

    # Clear screen
    screen.fill(BLACK)

    if not game_started:
        draw_start_screen()
    else:
        # Draw background
        draw_stars()
        draw_sun()
        draw_mountains()
        draw_grid()

        # Draw road
        draw_road()

        if not game_over:
            # Get keyboard input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > WIDTH // 2 - road_width // 2 + 10:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < WIDTH // 2 + road_width // 2 - player_width - 10:
                player_x += player_speed

            # Update obstacles
            spawn_obstacle()
            move_obstacles()

        # Draw obstacles
        draw_obstacles()

        # Draw player
        draw_player(player_x, player_y)

        # Draw score
        score_text = game_font.render(f"Score: {score}", True, YELLOW)
        screen.blit(score_text, (10, 10))

        # Draw game over if necessary
        if game_over:
            draw_game_over()

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()