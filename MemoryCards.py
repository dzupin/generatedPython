import pygame
import random
import time
import sys


# Initialize pygame
pygame.init()

# Constants
CARD_WIDTH = 120
CARD_HEIGHT = 160
CARD_MARGIN = 20
GRID_COLS = 5
GRID_ROWS = 4
CARD_WIDTH = 120
CARD_HEIGHT = 160
CARD_MARGIN = 20
GRID_COLS = 5
GRID_ROWS = 4
# Calculate window dimensions to fit all cards with margins
WINDOW_WIDTH = GRID_COLS * (CARD_WIDTH + CARD_MARGIN) + CARD_MARGIN
WINDOW_HEIGHT = GRID_ROWS * (CARD_HEIGHT + CARD_MARGIN) + CARD_MARGIN + 100  # Extra 100px for UI elements
TOTAL_CARDS = GRID_COLS * GRID_ROWS
CARD_BACK_COLOR = (41, 128, 185)  # Blue
BG_COLOR = (236, 240, 241)  # Light gray
TEXT_COLOR = (44, 62, 80)  # Dark blue
HIGHLIGHT_COLOR = (46, 204, 113)  # Green
MATCHED_COLOR = (39, 174, 96)  # Darker green

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Card Game")

# Set up fonts
font_large = pygame.font.SysFont("Arial", 36)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)

# Game variables
card_values = list(range(1, TOTAL_CARDS // 2 + 1)) * 2
matches_found = 0
moves = 0
start_time = 0
game_over = False


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
    global cards, card_values, matches_found, moves, start_time, game_over

    # Shuffle the card values
    random.shuffle(card_values)

    # Create cards
    cards = []
    for i in range(TOTAL_CARDS):
        row = i // GRID_COLS
        col = i % GRID_COLS
        x = col * (CARD_WIDTH + CARD_MARGIN) + CARD_MARGIN
        y = row * (CARD_HEIGHT + CARD_MARGIN) + CARD_MARGIN + 100  # Add offset for UI
        cards.append(Card(x, y, card_values[i]))

    # Reset game state
    matches_found = 0
    moves = 0
    start_time = time.time()
    game_over = False


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
    screen.blit(moves_text, (20, 60))

    # Draw progress
    progress_text = font_medium.render(f"Matches: {matches_found}/{TOTAL_CARDS // 2}", True, TEXT_COLOR)
    screen.blit(progress_text, (WINDOW_WIDTH - 200, 20))

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
            if game_over:
                # Check if play again button is clicked
                button_width, button_height = 200, 50
                panel_width, panel_height = 400, 250
                button_x = (WINDOW_WIDTH - panel_width) // 2 + (panel_width - button_width) // 2
                button_y = (WINDOW_HEIGHT - panel_height) // 2 + panel_height - button_height - 30
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                if button_rect.collidepoint(event.pos):
                    setup_game()
            elif not animating and wait_time <= 0:
                # Check if a card is clicked
                for card in cards:
                    if card.contains_point(event.pos) and not card.revealed and not card.matched:
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

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)

# Quit pygame
pygame.quit()
sys.exit()