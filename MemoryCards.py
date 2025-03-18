import pygame
import random
import time
import sys
import os
import json
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Constants
CARD_WIDTH = 120
CARD_HEIGHT = 160
CARD_MARGIN = 20
GRID_COLS = 5
GRID_ROWS = 4
TOTAL_CARDS = GRID_COLS * GRID_ROWS

# Calculate window dimensions to fit all cards with margins
WINDOW_WIDTH = GRID_COLS * (CARD_WIDTH + CARD_MARGIN) + CARD_MARGIN
WINDOW_HEIGHT = GRID_ROWS * (CARD_HEIGHT + CARD_MARGIN) + CARD_MARGIN + 100  # Extra 100px for UI elements

# Colors
CARD_BACK_COLOR = (41, 128, 185)  # Blue
BG_COLOR = (236, 240, 241)  # Light gray
TEXT_COLOR = (44, 62, 80)  # Dark blue
HIGHLIGHT_COLOR = (46, 204, 113)  # Green
MATCHED_COLOR = (39, 174, 96)  # Darker green
STATS_BG_COLOR = (245, 245, 245)  # Very light gray

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Card Game")

# Set up fonts
font_large = pygame.font.SysFont("Arial", 36)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)
font_tiny = pygame.font.SysFont("Arial", 16)

# Game variables
card_values = list(range(1, TOTAL_CARDS // 2 + 1)) * 2
matches_found = 0
moves = 0
start_time = 0
game_over = False
show_stats = False

# Stats file
STATS_FILE = "memory_game_stats.json"


# Load previous stats
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []


# Save stats
def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


# History of games
game_history = load_stats()


# Card class
class Card:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.revealed = False
        self.matched = False
        self.animation = 0  # 0: normal, 1-10: flip animation
        self.flip_direction = 1  # 1: flipping to front, -1: flipping to back

    def draw(self):
        # Calculate animation width for flipping effect
        if self.animation > 0:
            width_factor = abs(5 - self.animation) / 5
            width = int(CARD_WIDTH * width_factor)
            if width < 2:
                width = 2
        else:
            width = CARD_WIDTH

        # Draw card background
        rect = pygame.Rect(
            self.x + (CARD_WIDTH - width) // 2,
            self.y,
            width,
            CARD_HEIGHT
        )

        if self.animation > 0:
            # During animation
            if self.animation <= 5:  # First half of animation
                pygame.draw.rect(screen, CARD_BACK_COLOR, rect, 0, 10)
            else:  # Second half of animation
                color = MATCHED_COLOR if self.matched else (230, 126, 34)  # Orange for unmatched
                pygame.draw.rect(screen, color, rect, 0, 10)

                # Only draw value in second half of animation when revealing
                if self.flip_direction == 1 and width > CARD_WIDTH // 2:
                    self.draw_value(rect)
        else:
            # Not animating
            if self.revealed:
                color = MATCHED_COLOR if self.matched else (230, 126, 34)
                pygame.draw.rect(screen, color, rect, 0, 10)
                self.draw_value(rect)
            else:
                pygame.draw.rect(screen, CARD_BACK_COLOR, rect, 0, 10)

                # Draw decorative pattern on back
                pattern_color = (25, 79, 115)  # Darker blue
                margin = 15
                pattern_rect = pygame.Rect(
                    rect.x + margin,
                    rect.y + margin,
                    rect.width - 2 * margin,
                    rect.height - 2 * margin
                )
                pygame.draw.rect(screen, pattern_color, pattern_rect, 2, 5)

                # Draw lines on back
                for i in range(margin * 2, rect.width - margin * 2, 10):
                    pygame.draw.line(
                        screen,
                        pattern_color,
                        (rect.x + i, rect.y + margin),
                        (rect.x + i, rect.y + rect.height - margin),
                        1
                    )

    def draw_value(self, rect):
        # Draw card value - use shapes instead of just numbers
        value_colors = [
            (231, 76, 60),  # Red
            (241, 196, 15),  # Yellow
            (46, 204, 113),  # Green
            (52, 152, 219),  # Blue
            (155, 89, 182),  # Purple
            (230, 126, 34),  # Orange
            (26, 188, 156),  # Turquoise
            (22, 160, 133),  # Dark Turquoise
            (192, 57, 43),  # Dark Red
            (142, 68, 173)  # Dark Purple
        ]

        color = value_colors[(self.value - 1) % len(value_colors)]

        # Different shapes based on value
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2

        if self.value % 5 == 1:  # Circle
            radius = min(rect.width, rect.height) // 3
            pygame.draw.circle(screen, color, (center_x, center_y), radius)
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius, 2)
        elif self.value % 5 == 2:  # Square
            size = min(rect.width, rect.height) // 2
            square_rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
            pygame.draw.rect(screen, color, square_rect, 0, 5)
            pygame.draw.rect(screen, (255, 255, 255), square_rect, 2, 5)
        elif self.value % 5 == 3:  # Triangle
            size = min(rect.width, rect.height) // 2
            points = [
                (center_x, center_y - size),
                (center_x - size, center_y + size // 2),
                (center_x + size, center_y + size // 2)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        elif self.value % 5 == 4:  # Diamond
            size = min(rect.width, rect.height) // 2
            points = [
                (center_x, center_y - size),
                (center_x + size, center_y),
                (center_x, center_y + size),
                (center_x - size, center_y)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        else:  # Star
            size = min(rect.width, rect.height) // 3
            points = []
            for i in range(5):
                # Outer points
                angle = i * 2 * 3.14159 / 5 - 3.14159 / 2
                points.append((
                    center_x + int(size * 1.0 * pygame.math.Vector2.from_polar((1, angle * 180 / 3.14159)).x),
                    center_y + int(size * 1.0 * pygame.math.Vector2.from_polar((1, angle * 180 / 3.14159)).y)
                ))
                # Inner points
                angle += 3.14159 / 5
                points.append((
                    center_x + int(size * 0.4 * pygame.math.Vector2.from_polar((1, angle * 180 / 3.14159)).x),
                    center_y + int(size * 0.4 * pygame.math.Vector2.from_polar((1, angle * 180 / 3.14159)).y)
                ))
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)

        # Draw number in corner
        value_text = font_small.render(str(self.value), True, (255, 255, 255))
        screen.blit(value_text, (rect.x + 5, rect.y + 5))

    def update_animation(self):
        if self.animation > 0:
            self.animation += self.flip_direction
            if self.animation > 10 or self.animation < 1:
                self.animation = 0
                return True  # Animation complete
        return False

    def start_flip(self, to_front=True):
        self.animation = 1 if to_front else 10
        self.flip_direction = 1 if to_front else -1

    def contains_point(self, point):
        return (self.x <= point[0] <= self.x + CARD_WIDTH and
                self.y <= point[1] <= self.y + CARD_HEIGHT)


# Function to set up the game
def setup_game():
    global cards, card_values, matches_found, moves, start_time, game_over, show_stats

    # Shuffle the card values
    random.shuffle(card_values)

    # Create cards
    cards = []
    for i in range(TOTAL_CARDS):
        row = i // GRID_COLS
        col = i % GRID_COLS
        x = col * (CARD_WIDTH + CARD_MARGIN) + CARD_MARGIN
        y = row * (CARD_HEIGHT + CARD_MARGIN) + CARD_MARGIN + 80  # Add offset for UI
        cards.append(Card(x, y, card_values[i]))

    # Reset game state
    matches_found = 0
    moves = 0
    start_time = time.time()
    game_over = False
    show_stats = False


# Function to draw a rounded rectangle with a gradient
def draw_rounded_rect(surface, rect, color, radius=0.4):
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return surface.blit(rectangle, pos)


# Function to draw UI elements
def draw_ui():
    # Draw timer
    elapsed_time = int(time.time() - start_time) if not game_over else game_over_time
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = font_medium.render(f"Time: {minutes:02d}:{seconds:02d}", True, TEXT_COLOR)
    screen.blit(timer_text, (20, 20))

    # Draw moves counter
    moves_text = font_medium.render(f"Moves: {moves}", True, TEXT_COLOR)
    screen.blit(moves_text, (20, 50))

    # Draw progress
    progress_text = font_medium.render(f"Matches: {matches_found}/{TOTAL_CARDS // 2}", True, TEXT_COLOR)
    screen.blit(progress_text, (WINDOW_WIDTH - 200, 20))

    # Draw stats button
    stats_button_width, stats_button_height = 140, 40
    stats_button_x = WINDOW_WIDTH - 150
    stats_button_y = 50

    # Check if mouse is over stats button
    mouse_pos = pygame.mouse.get_pos()
    stats_button_rect = pygame.Rect(stats_button_x, stats_button_y, stats_button_width, stats_button_height)
    stats_button_hover = stats_button_rect.collidepoint(mouse_pos)

    # Draw stats button
    stats_button_color = HIGHLIGHT_COLOR if stats_button_hover else (52, 152, 219)
    draw_rounded_rect(screen, stats_button_rect, stats_button_color, 0.4)

    # Draw stats button text
    stats_text = font_small.render("Game History", True, (255, 255, 255))
    screen.blit(stats_text, (stats_button_x + (stats_button_width - stats_text.get_width()) // 2,
                             stats_button_y + (stats_button_height - stats_text.get_height()) // 2))

    # Draw game over message if applicable
    if game_over:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Draw game over panel
        panel_width, panel_height = 400, 250
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        draw_rounded_rect(screen, (panel_x, panel_y, panel_width, panel_height), (255, 255, 255), 0.2)

        # Draw game over text
        game_over_text = font_large.render("Game Over!", True, TEXT_COLOR)
        screen.blit(game_over_text, (panel_x + (panel_width - game_over_text.get_width()) // 2, panel_y + 30))

        # Draw stats
        stats_text = font_medium.render(f"Time: {minutes:02d}:{seconds:02d}", True, TEXT_COLOR)
        screen.blit(stats_text, (panel_x + (panel_width - stats_text.get_width()) // 2, panel_y + 80))

        moves_text = font_medium.render(f"Moves: {moves}", True, TEXT_COLOR)
        screen.blit(moves_text, (panel_x + (panel_width - moves_text.get_width()) // 2, panel_y + 120))

        # Draw play again button
        button_width, button_height = 200, 50
        button_x = panel_x + (panel_width - button_width) // 2
        button_y = panel_y + panel_height - button_height - 30

        # Check if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_hover = button_rect.collidepoint(mouse_pos)

        # Draw button
        button_color = HIGHLIGHT_COLOR if button_hover else (52, 152, 219)
        draw_rounded_rect(screen, button_rect, button_color, 0.4)

        # Draw button text
        play_again_text = font_medium.render("Play Again", True, (255, 255, 255))
        screen.blit(play_again_text, (button_x + (button_width - play_again_text.get_width()) // 2,
                                      button_y + (button_height - play_again_text.get_height()) // 2))


# Function to draw stats screen
def draw_stats_screen():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    # Draw stats panel
    panel_width = min(WINDOW_WIDTH - 40, 700)
    panel_height = min(WINDOW_HEIGHT - 40, 500)
    panel_x = (WINDOW_WIDTH - panel_width) // 2
    panel_y = (WINDOW_HEIGHT - panel_height) // 2
    draw_rounded_rect(screen, (panel_x, panel_y, panel_width, panel_height), STATS_BG_COLOR, 0.2)

    # Draw stats title
    stats_title = font_large.render("Game History", True, TEXT_COLOR)
    screen.blit(stats_title, (panel_x + (panel_width - stats_title.get_width()) // 2, panel_y + 20))

    # Draw headers
    headers = ["#", "Date", "Time", "Moves", "Duration"]
    header_width = panel_width // len(headers)
    for i, header in enumerate(headers):
        header_text = font_medium.render(header, True, TEXT_COLOR)
        screen.blit(header_text,
                    (panel_x + i * header_width + (header_width - header_text.get_width()) // 2, panel_y + 70))

    # Draw separator line
    pygame.draw.line(screen, TEXT_COLOR, (panel_x + 20, panel_y + 100), (panel_x + panel_width - 20, panel_y + 100), 2)

    # Draw stats entries
    max_entries = 10
    start_index = max(0, len(game_history) - max_entries)
    displayed_history = game_history[start_index:]

    for i, entry in enumerate(displayed_history):
        y_pos = panel_y + 120 + i * 30

        # Game number
        game_num = font_small.render(str(start_index + i + 1), True, TEXT_COLOR)
        screen.blit(game_num, (panel_x + (header_width - game_num.get_width()) // 2, y_pos))

        # Date
        date_text = font_small.render(entry["date"], True, TEXT_COLOR)
        screen.blit(date_text, (panel_x + header_width + (header_width - date_text.get_width()) // 2, y_pos))

        # Time
        time_text = font_small.render(entry["time"], True, TEXT_COLOR)
        screen.blit(time_text, (panel_x + 2 * header_width + (header_width - time_text.get_width()) // 2, y_pos))

        # Moves
        moves_text = font_small.render(str(entry["moves"]), True, TEXT_COLOR)
        screen.blit(moves_text, (panel_x + 3 * header_width + (header_width - moves_text.get_width()) // 2, y_pos))

        # Duration
        duration_text = font_small.render(entry["duration"], True, TEXT_COLOR)
        screen.blit(duration_text,
                    (panel_x + 4 * header_width + (header_width - duration_text.get_width()) // 2, y_pos))

    # Draw "More Stats" section
    if game_history:
        # Calculate average stats
        total_moves = sum(entry["moves"] for entry in game_history)
        total_seconds = sum(entry["seconds"] for entry in game_history)
        avg_moves = total_moves / len(game_history)
        avg_seconds = total_seconds / len(game_history)
        avg_minutes = avg_seconds // 60
        avg_seconds_remainder = avg_seconds % 60

        # Find best stats
        best_moves = min(game_history, key=lambda x: x["moves"])
        best_time = min(game_history, key=lambda x: x["seconds"])

        # Draw stats lines
        stats_lines = [
            f"Total Games Played: {len(game_history)}",
            f"Average Moves: {avg_moves:.1f}",
            f"Average Time: {int(avg_minutes):02d}:{int(avg_seconds_remainder):02d}",
            f"Best Moves: {best_moves['moves']} (Game #{game_history.index(best_moves) + 1})",
            f"Best Time: {best_time['duration']} (Game #{game_history.index(best_time) + 1})"
        ]

        for i, line in enumerate(stats_lines):
            y_pos = panel_y + panel_height - 150 + i * 25
            line_text = font_medium.render(line, True, TEXT_COLOR)
            screen.blit(line_text, (panel_x + 30, y_pos))

    # Draw close button
    button_width, button_height = 150, 40
    button_x = panel_x + (panel_width - button_width) // 2
    button_y = panel_y + panel_height - button_height - 20

    # Check if mouse is over button
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_hover = button_rect.collidepoint(mouse_pos)

    # Draw button
    button_color = HIGHLIGHT_COLOR if button_hover else (52, 152, 219)
    draw_rounded_rect(screen, button_rect, button_color, 0.4)

    # Draw button text
    close_text = font_medium.render("Close", True, (255, 255, 255))
    screen.blit(close_text, (button_x + (button_width - close_text.get_width()) // 2,
                             button_y + (button_height - close_text.get_height()) // 2))


# Set up the game
setup_game()

# Game loop
running = True
first_card = None
second_card = None
wait_time = 0
animating = False
game_over_time = 0

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if stats button is clicked
            stats_button_rect = pygame.Rect(WINDOW_WIDTH - 150, 50, 140, 40)
            if stats_button_rect.collidepoint(mouse_pos) and not game_over:
                show_stats = not show_stats

            # If stats screen is open, check for close button click
            if show_stats:
                panel_width = min(WINDOW_WIDTH - 40, 700)
                panel_height = min(WINDOW_HEIGHT - 40, 500)
                panel_x = (WINDOW_WIDTH - panel_width) // 2
                panel_y = (WINDOW_HEIGHT - panel_height) // 2

                button_width, button_height = 150, 40
                button_x = panel_x + (panel_width - button_width) // 2
                button_y = panel_y + panel_height - button_height - 20
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                if button_rect.collidepoint(mouse_pos):
                    show_stats = False

            # Game over screen handling
            elif game_over:
                # Check if play again button is clicked
                button_width, button_height = 200, 50
                panel_width, panel_height = 400, 250
                button_x = (WINDOW_WIDTH - panel_width) // 2 + (panel_width - button_width) // 2
                button_y = (WINDOW_HEIGHT - panel_height) // 2 + panel_height - button_height - 30
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                if button_rect.collidepoint(mouse_pos):
                    setup_game()

            # Regular game play
            elif not animating and wait_time <= 0 and not show_stats:
                # Check if a card is clicked
                for card in cards:
                    if card.contains_point(mouse_pos) and not card.revealed and not card.matched:
                        if first_card is None:
                            first_card = card
                            first_card.revealed = True
                            first_card.start_flip(to_front=True)
                            animating = True
                        elif second_card is None and card != first_card:
                            second_card = card
                            second_card.revealed = True
                            second_card.start_flip(to_front=True)
                            animating = True
                            moves += 1
                        break

    # Clear the screen
    screen.fill(BG_COLOR)

    # Update card animations
    if animating:
        animating = False
        for card in cards:
            if card.animation > 0:
                animation_complete = card.update_animation()
                if not animation_complete:
                    animating = True

        # Check for matches if both cards are revealed and not animating
        if first_card and second_card and not animating:
            if first_card.value == second_card.value:
                first_card.matched = True
                second_card.matched = True
                matches_found += 1
                first_card = None
                second_card = None

                # Check if game is over
                if matches_found == TOTAL_CARDS // 2:
                    game_over = True
                    game_over_time = int(time.time() - start_time)

                    # Create a new stats entry
                    from datetime import datetime

                    now = datetime.now()
                    date_str = now.strftime("%Y-%m-%d")
                    time_str = now.strftime("%H:%M:%S")
                    duration_str = f"{game_over_time // 60:02d}:{game_over_time % 60:02d}"

                    game_history.append({
                        "date": date_str,
                        "time": time_str,
                        "moves": moves,
                        "seconds": game_over_time,
                        "duration": duration_str
                    })

                    # Save stats to file
                    save_stats(game_history)
            else:
                wait_time = 60  # Wait for 1 second (60 frames at 60 FPS)

    # Handle wait time
    if wait_time > 0:
        wait_time -= 1
        if wait_time == 0:
            # Flip cards back
            if first_card and not first_card.matched:
                first_card.start_flip(to_front=False)
                first_card.revealed = False
                animating = True
            if second_card and not second_card.matched:
                second_card.start_flip(to_front=False)
                second_card.revealed = False
                animating = True
            first_card = None
            second_card = None

    # Draw cards
    for card in cards:
        card.draw()

    # Draw UI
    draw_ui()

    # Draw stats screen if toggled
    if show_stats:
        draw_stats_screen()

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)

# Quit pygame
pygame.quit()
sys.exit()