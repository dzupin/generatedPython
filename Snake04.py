import pygame
import sys
import random
import time
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)
BACKGROUND = (20, 20, 20)
PANEL_COLOR = (40, 40, 40)
BUTTON_COLOR = (60, 60, 60)
BUTTON_HOVER_COLOR = (80, 80, 80)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# File paths
STATS_FILE = "snake_stats.json"

# Initialize game variables
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = (1, 0)
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
score = 0
game_over = False
viewing_stats = False
previous_stats = []

# Game statistics
start_time = time.time()
game_duration = 0
max_snake_length = 1
food_eaten = 0
moves_made = 0
avg_speed = 0
game_date = ""

# Initialize fonts
font = pygame.font.SysFont('Arial', 25)
stats_font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 30, bold=True)
small_font = pygame.font.SysFont('Arial', 16)


# Button class for UI elements
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

        text_surf = small_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()
                return True
        return False


def load_stats():
    """Load statistics from JSON file"""
    global previous_stats
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                previous_stats = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            previous_stats = []
    else:
        previous_stats = []


def save_stats():
    """Save current game statistics to JSON file"""
    global previous_stats

    # Create stats dictionary
    current_stats = {
        "date": game_date,
        "score": score,
        "duration": game_duration,
        "snake_length": len(snake),
        "food_eaten": food_eaten,
        "moves_made": moves_made,
        "avg_speed": avg_speed
    }

    # Load existing stats
    load_stats()

    # Add current stats to the list
    previous_stats.append(current_stats)

    # Keep only the last 10 games
    if len(previous_stats) > 10:
        previous_stats = previous_stats[-10:]

    # Save to file
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(previous_stats, f, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")


def view_stats():
    """Toggle viewing previous statistics"""
    global viewing_stats
    viewing_stats = not viewing_stats


def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))


def draw_snake():
    # Draw snake head
    head = snake[0]
    head_rect = pygame.Rect(head[0] * GRID_SIZE, head[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, GREEN, head_rect)

    # Draw snake eyes
    eye_radius = GRID_SIZE // 8
    eye_offset = GRID_SIZE // 4

    # Left eye
    left_eye_pos = (head[0] * GRID_SIZE + eye_offset, head[1] * GRID_SIZE + eye_offset)
    pygame.draw.circle(screen, BLACK, left_eye_pos, eye_radius)

    # Right eye
    right_eye_pos = (head[0] * GRID_SIZE + GRID_SIZE - eye_offset, head[1] * GRID_SIZE + eye_offset)
    pygame.draw.circle(screen, BLACK, right_eye_pos, eye_radius)

    # Draw snake body with gradient color
    for i, segment in enumerate(snake[1:], 1):
        # Create a gradient from green to dark green
        color_factor = 1 - (i / len(snake))
        segment_color = (
            int(GREEN[0] * color_factor + DARK_GREEN[0] * (1 - color_factor)),
            int(GREEN[1] * color_factor + DARK_GREEN[1] * (1 - color_factor)),
            int(GREEN[2] * color_factor + DARK_GREEN[2] * (1 - color_factor))
        )

        segment_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, segment_color, segment_rect)

        # Add a small inner rectangle for texture
        inner_margin = GRID_SIZE // 5
        inner_rect = pygame.Rect(
            segment[0] * GRID_SIZE + inner_margin,
            segment[1] * GRID_SIZE + inner_margin,
            GRID_SIZE - 2 * inner_margin,
            GRID_SIZE - 2 * inner_margin
        )
        pygame.draw.rect(screen, (
            min(segment_color[0] + 30, 255),
            min(segment_color[1] + 30, 255),
            min(segment_color[2] + 30, 255)
        ), inner_rect)


def draw_food():
    food_rect = pygame.Rect(food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, RED, food_rect)

    # Add a shiny effect
    shine_radius = GRID_SIZE // 4
    shine_pos = (food[0] * GRID_SIZE + shine_radius, food[1] * GRID_SIZE + shine_radius)
    pygame.draw.circle(screen, WHITE, shine_pos, shine_radius // 2)


def draw_score():
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display time
    current_time = time.time() - start_time if not game_over else game_duration
    minutes = int(current_time // 60)
    seconds = int(current_time % 60)
    time_text = font.render(f'Time: {minutes:02d}:{seconds:02d}', True, WHITE)
    screen.blit(time_text, (WIDTH - time_text.get_width() - 10, 10))


def format_time(seconds):
    """Format seconds into MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def draw_previous_stats():
    """Draw a panel showing previous game statistics"""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

    # Create a panel for statistics
    panel_width, panel_height = 500, 450
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2

    # Draw panel background
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

    # Title
    title_text = title_font.render('GAME HISTORY', True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, panel_y + 30))
    screen.blit(title_text, title_rect)

    # Headers
    headers = ["Date", "Score", "Time", "Length", "Speed"]
    header_widths = [0.30, 0.15, 0.20, 0.15, 0.20]  # Proportional widths

    # Draw headers
    header_y = panel_y + 70
    current_x = panel_x + 20

    for i, header in enumerate(headers):
        header_text = stats_font.render(header, True, WHITE)
        screen.blit(header_text, (current_x, header_y))
        current_x += int(panel_width * header_widths[i])

    # Draw horizontal line
    pygame.draw.line(screen, WHITE, (panel_x + 10, header_y + 25),
                     (panel_x + panel_width - 10, header_y + 25))

    # Display stats (most recent first)
    if not previous_stats:
        no_stats_text = stats_font.render("No previous games found", True, WHITE)
        no_stats_rect = no_stats_text.get_rect(center=(WIDTH // 2, header_y + 60))
        screen.blit(no_stats_text, no_stats_rect)
    else:
        # Sort by date (most recent first)
        sorted_stats = sorted(previous_stats, key=lambda x: x.get("date", ""), reverse=True)

        for i, stat in enumerate(sorted_stats[:8]):  # Show up to 8 previous games
            row_y = header_y + 40 + i * 35
            current_x = panel_x + 20

            # Date
            date_text = small_font.render(stat.get("date", "Unknown"), True, WHITE)
            screen.blit(date_text, (current_x, row_y))
            current_x += int(panel_width * header_widths[0])

            # Score
            score_text = small_font.render(str(stat.get("score", 0)), True, WHITE)
            screen.blit(score_text, (current_x, row_y))
            current_x += int(panel_width * header_widths[1])

            # Time
            time_text = small_font.render(format_time(stat.get("duration", 0)), True, WHITE)
            screen.blit(time_text, (current_x, row_y))
            current_x += int(panel_width * header_widths[2])

            # Length
            length_text = small_font.render(str(stat.get("snake_length", 1)), True, WHITE)
            screen.blit(length_text, (current_x, row_y))
            current_x += int(panel_width * header_widths[3])

            # Speed
            speed = stat.get("avg_speed", 0)
            speed_text = small_font.render(f"{speed:.2f}/s", True, WHITE)
            screen.blit(speed_text, (current_x, row_y))

    # Close button
    close_button = Button(panel_x + panel_width - 100, panel_y + panel_height - 40,
                          80, 30, "Close", view_stats)
    close_button.check_hover(pygame.mouse.get_pos())
    close_button.draw(screen)


def draw_game_over():
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

    # Create a panel for statistics
    panel_width, panel_height = 400, 400
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2

    # Draw panel background
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

    # Game over title
    title_text = title_font.render('GAME OVER', True, RED)
    title_rect = title_text.get_rect(center=(WIDTH // 2, panel_y + 30))
    screen.blit(title_text, title_rect)

    # Statistics
    stats = [
        f"Score: {score}",
        f"Time Played: {format_time(game_duration)}",
        f"Snake Length: {len(snake)}",
        f"Food Eaten: {food_eaten}",
        f"Moves Made: {moves_made}",
        f"Avg. Speed: {avg_speed:.2f} moves/sec",
        f"Max Possible Score: {GRID_WIDTH * GRID_HEIGHT - 1}",
        f"Game Date: {game_date}"
    ]

    # Display statistics
    for i, stat in enumerate(stats):
        stat_text = stats_font.render(stat, True, WHITE)
        screen.blit(stat_text, (panel_x + 30, panel_y + 70 + i * 30))

    # Buttons
    button_width = 150
    button_height = 40
    button_y = panel_y + panel_height - 60

    # Restart button
    restart_button = Button(panel_x + 30, button_y, button_width, button_height, "Restart Game", None)
    restart_button.check_hover(pygame.mouse.get_pos())
    restart_button.draw(screen)

    # View Stats button
    view_stats_button = Button(panel_x + panel_width - button_width - 30, button_y,
                               button_width, button_height, "View History", view_stats)
    view_stats_button.check_hover(pygame.mouse.get_pos())
    view_stats_button.draw(screen)

    # Instructions
    instructions = small_font.render("Press R to restart or H to view game history", True, WHITE)
    instructions_rect = instructions.get_rect(center=(WIDTH // 2, panel_y + panel_height - 20))
    screen.blit(instructions, instructions_rect)

    return [restart_button, view_stats_button]


def update_game():
    global snake, food, score, game_over, snake_direction, food_eaten, moves_made
    global max_snake_length, game_duration, avg_speed, game_date

    # Get user input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and snake_direction != (0, 1):
        snake_direction = (0, -1)
    elif keys[pygame.K_DOWN] and snake_direction != (0, -1):
        snake_direction = (0, 1)
    elif keys[pygame.K_LEFT] and snake_direction != (1, 0):
        snake_direction = (-1, 0)
    elif keys[pygame.K_RIGHT] and snake_direction != (-1, 0):
        snake_direction = (1, 0)

    # Move the snake
    head_x, head_y = snake[0]
    new_head = (head_x + snake_direction[0], head_y + snake_direction[1])
    moves_made += 1

    # Check for collisions with walls
    if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
        handle_game_over()
        return

    # Check for collisions with self
    if new_head in snake[1:]:
        handle_game_over()
        return

    # Add new head
    snake.insert(0, new_head)

    # Update max snake length
    max_snake_length = max(max_snake_length, len(snake))

    # Check if snake ate food
    if new_head == food:
        # Generate new food
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in snake:
                break
        score += 1
        food_eaten += 1
    else:
        # Remove tail if no food was eaten
        snake.pop()


def handle_game_over():
    global game_over, game_duration, avg_speed, game_date

    game_over = True
    game_duration = time.time() - start_time
    avg_speed = moves_made / game_duration if game_duration > 0 else 0
    game_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Save statistics to JSON file
    save_stats()


def reset_game():
    global snake, snake_direction, food, score, game_over, start_time, game_duration
    global max_snake_length, food_eaten, moves_made, avg_speed, viewing_stats

    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (1, 0)
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    score = 0
    game_over = False
    start_time = time.time()
    viewing_stats = False

    # Reset statistics
    game_duration = 0
    max_snake_length = 1
    food_eaten = 0
    moves_made = 0
    avg_speed = 0


# Main game loop
close_button = None
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_h and game_over:
                view_stats()

        # Handle close button click in game history
        if viewing_stats and close_button:
            close_button.check_hover(pygame.mouse.get_pos())
            if close_button.handle_event(event):
                viewing_stats = False

    # Fill the screen
    screen.fill(BACKGROUND)

    if not game_over and not viewing_stats:
        # Draw grid
        draw_grid()

        # Update game state
        update_game()

        # Draw game elements
        draw_snake()
        draw_food()
        draw_score()

    elif game_over and not viewing_stats:
        # Draw game over screen
        buttons = draw_game_over()

        # Handle button events
        for button in buttons:
            if button.handle_event(event):
                if button.text == "Restart Game":
                    reset_game()
                elif button.text == "View History":
                    view_stats()

    elif viewing_stats:
        # Draw previous game statistics
        panel_width, panel_height = 500, 450
        panel_x = (WIDTH - panel_width) // 2
        panel_y = (HEIGHT - panel_height) // 2

        # Create close button if not already created
        if not close_button:
            close_button = Button(panel_x + panel_width - 100, panel_y + panel_height - 40,
                                  80, 30, "Close", view_stats)

        # Draw previous game statistics
        draw_previous_stats()
        close_button.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)
