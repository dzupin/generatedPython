import pygame
import random
import sys
import math
import time

# --- Initialization ---
pygame.init()

# PROMPT for Gemini 2.5 Pro Experimental 03-25 : Write Memory Cards game in python using pygame library. Make it visually appealing

# --- Constants ---
# Grid settings (adjust for difficulty)
GRID_COLS = 4
GRID_ROWS = 4
TOTAL_CARDS = GRID_COLS * GRID_ROWS
if TOTAL_CARDS % 2 != 0:
    raise ValueError("GRID_COLS * GRID_ROWS must be an even number for pairs.")
NUM_UNIQUE_SYMBOLS = TOTAL_CARDS // 2

# Screen dimensions (calculated based on grid and card size)
CARD_WIDTH = 100
CARD_HEIGHT = 120
GAP = 15 # Gap between cards
BORDER_RADIUS = 10 # How rounded the card corners are
TOP_MARGIN = 50 # Space for score/tries display
SIDE_MARGIN = 50

SCREEN_WIDTH = GRID_COLS * (CARD_WIDTH + GAP) - GAP + 2 * SIDE_MARGIN
SCREEN_HEIGHT = GRID_ROWS * (CARD_HEIGHT + GAP) - GAP + TOP_MARGIN + SIDE_MARGIN

# Colors (RGB)
BACKGROUND_COLOR = (30, 30, 40)     # Dark Slate Blue/Gray
CARD_BACK_COLOR = (70, 130, 180)   # Steel Blue
CARD_FACE_COLOR = (210, 210, 220)   # Light Gray
CARD_MATCHED_COLOR = (60, 60, 70)   # Darker Gray for matched cards
BORDER_COLOR = (255, 255, 255)    # White border for highlighting revealed cards (optional)
SCORE_COLOR = (230, 230, 230)   # Light Gray/Off-white
WIN_TEXT_COLOR = (144, 238, 144)  # Light Green

# Symbol colors (add more if you increase grid size)
SYMBOL_COLORS = [
    (255, 0, 0),     # Red
    (0, 0, 255),     # Blue
    (0, 255, 0),     # Lime Green
    (255, 255, 0),   # Yellow
    (255, 165, 0),   # Orange
    (128, 0, 128),   # Purple
    (0, 255, 255),   # Cyan
    (255, 0, 255),   # Magenta
    (255, 192, 203), # Pink
    (0, 128, 0),     # Green
    (165, 42, 42),   # Brown
    (0, 0, 0)        # Black
]
if NUM_UNIQUE_SYMBOLS > len(SYMBOL_COLORS):
     raise ValueError("Not enough SYMBOL_COLORS defined for the grid size.")

# Timing
REVEAL_SPEED = 8 # Not really speed, but frames to show mismatch. Lower is faster flip back.
MISMATCH_DELAY_MS = 750 # Milliseconds to show non-matching cards before flipping back

# Card States
STATE_HIDDEN = 0
STATE_REVEALED = 1
STATE_MATCHED = 2

# --- Screen and Clock Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Cards")
clock = pygame.time.Clock()

# --- Fonts ---
try:
    info_font = pygame.font.SysFont("bahnschrift", 30)
    win_font_big = pygame.font.SysFont("consolas", 60)
    win_font_small = pygame.font.SysFont("consolas", 25)
except pygame.error:
    print("Warning: Using default font. Consider installing 'bahnschrift' or 'consolas'.")
    info_font = pygame.font.SysFont(None, 40)
    win_font_big = pygame.font.SysFont(None, 80)
    win_font_small = pygame.font.SysFont(None, 35)


# --- Card Class ---
class Card:
    def __init__(self, symbol_id, symbol_color, symbol_shape):
        self.symbol_id = symbol_id # Identifier for matching
        self.symbol_color = symbol_color
        self.symbol_shape = symbol_shape # 'circle', 'square', 'diamond', 'triangle'
        self.state = STATE_HIDDEN # hidden, revealed, matched
        self.rect = None # Pygame Rect for position and collision, set later

    def draw_symbol(self, surface, rect):
        """Draws the specific symbol inside the given rect."""
        center_x = rect.centerx
        center_y = rect.centery
        size = min(rect.width, rect.height) * 0.6 # Scale symbol size

        if self.symbol_shape == 'circle':
            pygame.draw.circle(surface, self.symbol_color, (center_x, center_y), int(size / 2))
        elif self.symbol_shape == 'square':
            half_size = int(size / 2)
            pygame.draw.rect(surface, self.symbol_color, (center_x - half_size, center_y - half_size, size, size))
        elif self.symbol_shape == 'diamond':
            half_size = int(size / 2)
            points = [
                (center_x, center_y - half_size),
                (center_x + half_size, center_y),
                (center_x, center_y + half_size),
                (center_x - half_size, center_y)
            ]
            pygame.draw.polygon(surface, self.symbol_color, points)
        elif self.symbol_shape == 'triangle':
            height = size * math.sqrt(3) / 2
            half_base = size / 2
            points = [
                (center_x, center_y - height / 2), # Top point
                (center_x - half_base, center_y + height / 2), # Bottom left
                (center_x + half_base, center_y + height / 2)  # Bottom right
            ]
            pygame.draw.polygon(surface, self.symbol_color, points)
        # Add more shapes here if needed

    def draw(self, surface):
        """Draws the card based on its state."""
        if not self.rect: return # Don't draw if position not set

        if self.state == STATE_HIDDEN:
            pygame.draw.rect(surface, CARD_BACK_COLOR, self.rect, border_radius=BORDER_RADIUS)
        elif self.state == STATE_REVEALED:
            pygame.draw.rect(surface, CARD_FACE_COLOR, self.rect, border_radius=BORDER_RADIUS)
            self.draw_symbol(surface, self.rect)
            # Optional: Highlight revealed card
            # pygame.draw.rect(surface, BORDER_COLOR, self.rect, width=3, border_radius=BORDER_RADIUS)
        elif self.state == STATE_MATCHED:
            # Draw slightly differently to show it's matched (e.g., dimmer)
            pygame.draw.rect(surface, CARD_MATCHED_COLOR, self.rect, border_radius=BORDER_RADIUS)
            # Optionally draw the symbol faded on matched cards too
            # temp_color = tuple(c // 1.5 for c in self.symbol_color) # Fade color
            # self.draw_symbol(surface, self.rect, color=temp_color)


# --- Helper Functions ---

def generate_board():
    """Creates and shuffles the deck of cards."""
    symbols = list(range(NUM_UNIQUE_SYMBOLS)) * 2 # Create pairs of symbol IDs
    random.shuffle(symbols)

    shapes = ['circle', 'square', 'diamond', 'triangle'] # Available shapes
    if NUM_UNIQUE_SYMBOLS > len(shapes):
        # If more unique symbols than shapes, repeat shapes
        shapes = (shapes * (NUM_UNIQUE_SYMBOLS // len(shapes) + 1))[:NUM_UNIQUE_SYMBOLS]

    board = []
    symbol_index = 0
    for r in range(GRID_ROWS):
        row_cards = []
        for c in range(GRID_COLS):
            if symbol_index < len(symbols):
                symbol_id = symbols[symbol_index]
                color = SYMBOL_COLORS[symbol_id % len(SYMBOL_COLORS)] # Cycle through colors
                shape = shapes[symbol_id % len(shapes)] # Cycle through shapes
                card = Card(symbol_id, color, shape)

                # Calculate position
                x = SIDE_MARGIN + c * (CARD_WIDTH + GAP)
                y = TOP_MARGIN + r * (CARD_HEIGHT + GAP)
                card.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

                row_cards.append(card)
                symbol_index += 1
        board.append(row_cards)
    return board

def get_card_at_pos(board, pos):
    """Finds which card (row, col) is at the mouse coordinates."""
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if board[r][c].rect and board[r][c].rect.collidepoint(pos):
                return (r, c)
    return None, None

def draw_board(surface, board):
    """Draws all cards on the board."""
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            board[r][c].draw(surface)

def draw_info(surface, tries, matches):
    """Displays the number of tries and matches."""
    tries_text = f"Tries: {tries}"
    matches_text = f"Matches: {matches} / {NUM_UNIQUE_SYMBOLS}"
    tries_surf = info_font.render(tries_text, True, SCORE_COLOR)
    matches_surf = info_font.render(matches_text, True, SCORE_COLOR)

    surface.blit(tries_surf, (SIDE_MARGIN, 10))
    surface.blit(matches_surf, (SCREEN_WIDTH - matches_surf.get_width() - SIDE_MARGIN, 10))


def display_win_message(surface):
    """Displays the win message and instructions."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Semi-transparent black overlay
    surface.blit(overlay, (0, 0))

    win_text = "You Win!"
    prompt_text = "Press 'R' to Play Again or 'Q' to Quit"

    win_surf = win_font_big.render(win_text, True, WIN_TEXT_COLOR)
    prompt_surf = win_font_small.render(prompt_text, True, SCORE_COLOR)

    win_rect = win_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30))
    prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))

    surface.blit(win_surf, win_rect)
    surface.blit(prompt_surf, prompt_rect)

# --- Game Reset Function ---
def reset_game():
    global game_board, revealed_cards, matched_pairs, tries, game_won, allow_click, last_mismatch_time
    game_board = generate_board()
    revealed_cards = [] # Stores (row, col) of revealed cards
    matched_pairs = 0
    tries = 0
    game_won = False
    allow_click = True # Control clicking during mismatch delay
    last_mismatch_time = 0 # Timestamp of the last mismatch reveal

# --- Game Loop ---
def game_loop():
    global game_board, revealed_cards, matched_pairs, tries, game_won, allow_click, last_mismatch_time

    reset_game() # Initialize the first game
    running = True

    while running:
        # --- Event Handling ---
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if allow_click and not game_won: # Only process click if allowed and game not won
                    mouse_clicked = True
                    mouse_pos = event.pos
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r and game_won: # Only allow restart if won
                    reset_game()


        # --- Game Logic ---

        # Handle Mismatch Timer
        current_time = pygame.time.get_ticks()
        if not allow_click and current_time - last_mismatch_time > MISMATCH_DELAY_MS:
            # Time's up, hide the mismatched cards
            r1, c1 = revealed_cards[0]
            r2, c2 = revealed_cards[1]
            game_board[r1][c1].state = STATE_HIDDEN
            game_board[r2][c2].state = STATE_HIDDEN
            revealed_cards = []
            allow_click = True # Allow clicking again


        # Handle Card Click
        if mouse_clicked:
            r, c = get_card_at_pos(game_board, mouse_pos)

            if r is not None and game_board[r][c].state == STATE_HIDDEN:
                # Clicked on a valid hidden card
                game_board[r][c].state = STATE_REVEALED

                if (r, c) not in revealed_cards: # Avoid adding same card twice if clicked fast
                    revealed_cards.append((r, c))

                if len(revealed_cards) == 2:
                    # Two cards are revealed, check for match
                    r1, c1 = revealed_cards[0]
                    r2, c2 = revealed_cards[1]
                    card1 = game_board[r1][c1]
                    card2 = game_board[r2][c2]

                    tries += 1 # Increment tries when second card is revealed

                    if card1.symbol_id == card2.symbol_id:
                        # It's a match!
                        card1.state = STATE_MATCHED
                        card2.state = STATE_MATCHED
                        matched_pairs += 1
                        revealed_cards = [] # Clear revealed list
                        if matched_pairs == NUM_UNIQUE_SYMBOLS:
                            game_won = True # All pairs found
                    else:
                        # It's a mismatch
                        allow_click = False # Disable clicking until timer finishes
                        last_mismatch_time = pygame.time.get_ticks() # Start timer


        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)
        draw_board(screen, game_board)
        draw_info(screen, tries, matched_pairs)

        # Display win message if game is won
        if game_won:
            display_win_message(screen)

        # Update the display
        pygame.display.flip() # Use flip for smoother updates

        # --- Frame Rate ---
        clock.tick(60) # Limit to 60 FPS


    # --- Cleanup ---
    pygame.quit()
    sys.exit()

# --- Start the Game ---
if __name__ == "__main__":
    game_loop()