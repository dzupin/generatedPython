import pygame
import random
import math

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Grid dimensions
GRID_ROWS = 4
GRID_COLS = 5

# Card dimensions and spacing
CARD_WIDTH = 120
CARD_HEIGHT = 120
CARD_GAP = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
BG_COLOR1 = (30, 30, 60)
BG_COLOR2 = (50, 50, 90)

# Card Colors
CARD_BACK_COLOR1 = (100, 150, 255)
CARD_BACK_COLOR2 = (60, 100, 200)
CARD_FACE_COLOR = (230, 230, 255)
CARD_OUTLINE_COLOR = (255, 255, 255)
CARD_MATCHED_COLOR = (50, 200, 50)

# Shape Colors (a palette of visually distinct colors)
SHAPE_COLORS = [
    (255, 105, 180),  # Hot Pink
    (255, 215, 0),  # Gold
    (138, 43, 226),  # Blue Violet
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (75, 0, 130),  # Indigo
    (240, 230, 140),  # Khaki
    (255, 0, 0),  # Red
    (0, 128, 0),  # Green
    (0, 0, 255),  # Blue
]

# Animation speeds
FLIP_SPEED = 0.05
MATCH_ANIMATION_SPEED = 0.1


# --- Helper Functions for Graphics ---

def draw_gradient_background(surface):
    """Draws a vertical gradient on a surface."""
    rect = pygame.Rect(0, 0, surface.get_width(), surface.get_height())
    start_color = BG_COLOR1
    end_color = BG_COLOR2
    for y in range(rect.height):
        ratio = y / rect.height
        color = (
            int(start_color[0] * (1 - ratio) + end_color[0] * ratio),
            int(start_color[1] * (1 - ratio) + end_color[1] * ratio),
            int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        )
        pygame.draw.line(surface, color, (rect.left, y), (rect.right, y))


def draw_card_back(surface, rect):
    """Draws the back of a card with a gradient and a simple shape."""
    # Gradient
    start_color = CARD_BACK_COLOR1
    end_color = CARD_BACK_COLOR2
    for x in range(rect.width):
        ratio = x / rect.width
        color = (
            int(start_color[0] * (1 - ratio) + end_color[0] * ratio),
            int(start_color[1] * (1 - ratio) + end_color[1] * ratio),
            int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        )
        pygame.draw.line(surface, color, (x, 0), (x, rect.height))
    # Simple intersecting lines as a pattern
    pygame.draw.line(surface, WHITE, (10, 10), (rect.width - 10, rect.height - 10), 3)
    pygame.draw.line(surface, WHITE, (10, rect.height - 10), (rect.width - 10, 10), 3)


# --- Shape Drawing Functions ---
# Each function draws a unique shape on a given surface.

def draw_shape_1(surface, color):  # Diamond
    points = [
        (surface.get_width() // 2, 10),
        (surface.get_width() - 10, surface.get_height() // 2),
        (surface.get_width() // 2, surface.get_height() - 10),
        (10, surface.get_height() // 2)
    ]
    pygame.draw.polygon(surface, color, points)


def draw_shape_2(surface, color):  # Cross
    pygame.draw.rect(surface, color, (30, 10, surface.get_width() - 60, surface.get_height() - 20))
    pygame.draw.rect(surface, color, (10, 30, surface.get_width() - 20, surface.get_height() - 60))


def draw_shape_3(surface, color):  # Concentric Circles
    center = (surface.get_width() // 2, surface.get_height() // 2)
    pygame.draw.circle(surface, color, center, surface.get_width() // 2 - 10, 10)
    pygame.draw.circle(surface, color, center, surface.get_width() // 2 - 30, 10)


def draw_shape_4(surface, color):  # Triangle
    points = [
        (surface.get_width() // 2, 10),
        (surface.get_width() - 10, surface.get_height() - 10),
        (10, surface.get_height() - 10)
    ]
    pygame.draw.polygon(surface, color, points)


def draw_shape_5(surface, color):  # Hourglass
    points = [
        (10, 10),
        (surface.get_width() - 10, 10),
        (10, surface.get_height() - 10),
        (surface.get_width() - 10, surface.get_height() - 10),
    ]
    pygame.draw.polygon(surface, color, points)


def draw_shape_6(surface, color):  # Star
    center_x, center_y = surface.get_width() // 2, surface.get_height() // 2
    outer_radius = surface.get_width() // 2 - 10
    inner_radius = outer_radius // 2.5
    points = []
    for i in range(10):
        angle = math.radians(i * 36)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)


def draw_shape_7(surface, color):  # Square with inner circle
    pygame.draw.rect(surface, color, (10, 10, surface.get_width() - 20, surface.get_height() - 20), 10)
    pygame.draw.circle(surface, color, (surface.get_width() // 2, surface.get_height() // 2), 20)


def draw_shape_8(surface, color):  # 'X'
    pygame.draw.line(surface, color, (10, 10), (surface.get_width() - 10, surface.get_height() - 10), 15)
    pygame.draw.line(surface, color, (10, surface.get_height() - 10), (surface.get_width() - 10, 10), 15)


def draw_shape_9(surface, color):  # Horizontal bars
    pygame.draw.rect(surface, color, (10, 20, surface.get_width() - 20, 20))
    pygame.draw.rect(surface, color, (10, surface.get_height() // 2 - 10, surface.get_width() - 20, 20))
    pygame.draw.rect(surface, color, (10, surface.get_height() - 40, surface.get_width() - 20, 20))


def draw_shape_10(surface, color):  # Pac-Man like shape
    center = (surface.get_width() // 2, surface.get_height() // 2)
    radius = surface.get_width() // 2 - 10
    rect = (center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    pygame.draw.arc(surface, color, rect, math.radians(45), math.radians(315), radius)


# List of shape drawing functions
SHAPE_FUNCTIONS = [
    draw_shape_1, draw_shape_2, draw_shape_3, draw_shape_4, draw_shape_5,
    draw_shape_6, draw_shape_7, draw_shape_8, draw_shape_9, draw_shape_10
]


# --- Card Class ---

class Card:
    def __init__(self, shape_id, color, x, y):
        self.shape_id = shape_id
        self.color = color
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.is_flipped = False
        self.is_matched = False
        self.flip_animation = 0  # 0: face down, 1: face up
        self.match_animation = 0  # for matched animation
        self.create_surfaces()

    def create_surfaces(self):
        # Create the face surface with the shape
        self.face_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.face_surface, CARD_FACE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        shape_func = SHAPE_FUNCTIONS[self.shape_id]
        shape_func(self.face_surface, self.color)
        pygame.draw.rect(self.face_surface, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)

        # Create the back surface
        self.back_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        draw_card_back(self.back_surface, self.back_surface.get_rect())
        pygame.draw.rect(self.back_surface, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)

    def draw(self, screen):
        if self.is_matched and self.match_animation < 1:
            self.match_animation += MATCH_ANIMATION_SPEED

        if self.is_matched:
            # Draw a green tint over the card when matched
            tint = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            tint.fill(CARD_MATCHED_COLOR)
            tint.set_alpha(int(150 * self.match_animation))
            screen.blit(self.face_surface, self.rect.topleft)
            screen.blit(tint, self.rect.topleft)
            return

        # Handle flip animation
        if self.is_flipped and self.flip_animation < 1:
            self.flip_animation += FLIP_SPEED
        elif not self.is_flipped and self.flip_animation > 0:
            self.flip_animation -= FLIP_SPEED

        self.flip_animation = max(0, min(1, self.flip_animation))

        # Determine which surface to show based on animation progress
        current_scale = abs(1 - 2 * self.flip_animation)
        scaled_width = int(CARD_WIDTH * current_scale)

        if self.flip_animation < 0.5:
            surface_to_draw = self.back_surface
        else:
            surface_to_draw = self.face_surface

        scaled_surface = pygame.transform.scale(surface_to_draw, (scaled_width, CARD_HEIGHT))
        scaled_rect = scaled_surface.get_rect(center=self.rect.center)
        screen.blit(scaled_surface, scaled_rect)

    def flip(self):
        if not self.is_matched:
            self.is_flipped = not self.is_flipped

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if not self.is_flipped and not self.is_matched:
                self.flip()
                return self
        return None


# --- Game Functions ---

def create_board():
    """Creates and shuffles the deck of cards."""
    num_pairs = (GRID_ROWS * GRID_COLS) // 2
    shape_ids = list(range(num_pairs))
    card_pairs = []

    for i in range(num_pairs):
        shape_id = shape_ids[i]
        color = SHAPE_COLORS[i % len(SHAPE_COLORS)]
        card_pairs.append((shape_id, color))
        card_pairs.append((shape_id, color))

    random.shuffle(card_pairs)

    cards = []
    board_width = GRID_COLS * (CARD_WIDTH + CARD_GAP) - CARD_GAP
    board_height = GRID_ROWS * (CARD_HEIGHT + CARD_GAP) - CARD_GAP
    start_x = (SCREEN_WIDTH - board_width) // 2
    start_y = (SCREEN_HEIGHT - board_height) // 2

    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            shape_id, color = card_pairs.pop()
            x = start_x + j * (CARD_WIDTH + CARD_GAP)
            y = start_y + i * (CARD_HEIGHT + CARD_GAP)
            cards.append(Card(shape_id, color, x, y))

    return cards


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=15)
        draw_text(screen, self.text, 30, self.rect.centerx, self.rect.centery, BLACK)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False


# --- Main Game Loop ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Card Game")
    clock = pygame.time.Clock()

    # Game variables
    cards = create_board()
    flipped_cards = []
    moves = 0
    start_time = pygame.time.get_ticks()
    game_over = False

    restart_button = Button(
        SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 60, 150, 40, "Restart",
        (150, 250, 150), (200, 255, 200)
    )

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                for card in cards:
                    flipped_card = card.handle_event(event)
                    if flipped_card and len(flipped_cards) < 2:
                        flipped_cards.append(flipped_card)

            if game_over:
                if restart_button.handle_event(event):
                    # Reset game
                    cards = create_board()
                    flipped_cards = []
                    moves = 0
                    start_time = pygame.time.get_ticks()
                    game_over = False

        # Game Logic
        if len(flipped_cards) == 2:
            pygame.time.wait(500)  # Pause to let player see the cards
            moves += 1
            card1, card2 = flipped_cards
            if card1.shape_id == card2.shape_id:
                card1.is_matched = True
                card2.is_matched = True
            else:
                card1.flip()
                card2.flip()
            flipped_cards = []

        # Check for win condition
        if not game_over:
            if all(card.is_matched for card in cards):
                game_over = True
                end_time = pygame.time.get_ticks()
                total_time = (end_time - start_time) // 1000

        # Drawing
        draw_gradient_background(screen)

        for card in cards:
            card.draw(screen)

        # UI Text
        draw_text(screen, f"Moves: {moves}", 36, 100, 30)
        if not game_over:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            draw_text(screen, f"Time: {elapsed_time}", 36, SCREEN_WIDTH - 100, 30)

        if game_over:
            # Game over overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "You Win!", 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, f"Total Moves: {moves}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            draw_text(screen, f"Total Time: {total_time}s", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
            restart_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()