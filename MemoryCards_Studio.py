import pygame
import random
import math
import time

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
BG_COLOR1 = (30, 30, 60)
BG_COLOR2 = (50, 50, 90)
CARD_FACE_COLOR = (230, 230, 255)
CARD_OUTLINE_COLOR = (255, 255, 255)
CARD_MATCHED_COLOR = (50, 200, 50)

# --- UNLOCKABLE COSMETICS ---

# Color Palettes
PALETTES = {
    'Default': [
        (255, 105, 180), (255, 215, 0), (138, 43, 226), (0, 255, 255), (255, 165, 0),
        (75, 0, 130), (240, 230, 140), (255, 0, 0), (0, 128, 0), (0, 0, 255)
    ],
    'Forest': [
        (44, 117, 44), (124, 181, 124), (16, 78, 48), (144, 238, 144), (85, 107, 47),
        (34, 139, 34), (0, 100, 0), (154, 205, 50), (107, 142, 35), (50, 205, 50)
    ],
    'Ocean': [
        (0, 119, 190), (0, 188, 212), (173, 232, 244), (64, 224, 208), (0, 206, 209),
        (30, 144, 255), (70, 130, 180), (135, 206, 250), (0, 255, 255), (224, 255, 255)
    ]
}


# Card Back Drawing Functions
def draw_card_back_default(surface, rect):
    start_color, end_color = (100, 150, 255), (60, 100, 200)
    for x in range(rect.width):
        ratio = x / rect.width
        color = (
            int(start_color[0] * (1 - ratio) + end_color[0] * ratio),
            int(start_color[1] * (1 - ratio) + end_color[1] * ratio),
            int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        )
        pygame.draw.line(surface, color, (x, 0), (x, rect.height))
    pygame.draw.line(surface, WHITE, (10, 10), (rect.width - 10, rect.height - 10), 3)
    pygame.draw.line(surface, WHITE, (10, rect.height - 10), (rect.width - 10, 10), 3)


def draw_card_back_circles(surface, rect):
    start_color, end_color = (255, 100, 100), (200, 60, 60)
    pygame.draw.rect(surface, end_color, (0, 0, rect.width, rect.height))
    center = rect.center
    for r in range(10, rect.width // 2, 15):
        pygame.draw.circle(surface, WHITE, center, r, 2)


CARD_BACK_STYLES = {
    'Default': draw_card_back_default,
    'Crimson Circles': draw_card_back_circles
}

# --- RANKS and UNLOCKS ---
RANKS = {
    0: {'name': "Novice", 'medal_color': (205, 127, 50)},  # Bronze
    3: {'name': "Beginner", 'unlock': ('palette', 'Forest'), 'medal_color': (192, 192, 192)},  # Silver
    6: {'name': "Apprentice", 'unlock': ('card_back', 'Crimson Circles'), 'medal_color': (255, 215, 0)},  # Gold
}

# Animation speeds
FLIP_SPEED = 0.05
MATCH_ANIMATION_SPEED = 0.1


# --- Helper Functions ---
def draw_gradient_background(surface):
    rect = pygame.Rect(0, 0, surface.get_width(), surface.get_height())
    start_color, end_color = BG_COLOR1, BG_COLOR2
    for y in range(rect.height):
        ratio = y / rect.height
        color = tuple(int(start_color[i] * (1 - ratio) + end_color[i] * ratio) for i in range(3))
        pygame.draw.line(surface, color, (rect.left, y), (rect.right, y))


def draw_text(surface, text, size, x, y, color=WHITE, align="center"):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def draw_medal(surface, x, y, size, color):
    # Draw a simple medal shape
    outer_circle_rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
    pygame.draw.circle(surface, color, (x, y), size)
    pygame.draw.circle(surface, tuple(min(255, c + 30) for c in color), (x, y), size * 0.8)
    # Ribbon
    pygame.draw.rect(surface, (200, 0, 0), (x - size * 0.4, y - size, size * 0.8, size * 0.5))


# --- Shape Drawing Functions ---
# (Re-using the shape functions from the original code)
def draw_shape_1(surface, color): pygame.draw.polygon(surface, color, [(surface.get_width() // 2, 10),
                                                                       (surface.get_width() - 10,
                                                                        surface.get_height() // 2),
                                                                       (surface.get_width() // 2,
                                                                        surface.get_height() - 10),
                                                                       (10, surface.get_height() // 2)])


def draw_shape_2(surface, color): pygame.draw.rect(surface, color, (30, 10, surface.get_width() - 60,
                                                                    surface.get_height() - 20)); pygame.draw.rect(
    surface, color, (10, 30, surface.get_width() - 20, surface.get_height() - 60))


def draw_shape_3(surface, color): center = (surface.get_width() // 2, surface.get_height() // 2); pygame.draw.circle(
    surface, color, center, surface.get_width() // 2 - 10, 10); pygame.draw.circle(surface, color, center,
                                                                                   surface.get_width() // 2 - 30, 10)


def draw_shape_4(surface, color): pygame.draw.polygon(surface, color, [(surface.get_width() // 2, 10),
                                                                       (surface.get_width() - 10,
                                                                        surface.get_height() - 10),
                                                                       (10, surface.get_height() - 10)])


def draw_shape_5(surface, color): pygame.draw.polygon(surface, color, [(10, 10), (surface.get_width() - 10, 10),
                                                                       (10, surface.get_height() - 10),
                                                                       (surface.get_width() - 10,
                                                                        surface.get_height() - 10)])


def draw_shape_6(surface, color):
    center_x, center_y = surface.get_width() // 2, surface.get_height() // 2;
    outer_radius, inner_radius = surface.get_width() // 2 - 10, surface.get_width() // 5;
    points = []
    for i in range(10): angle = math.radians(
        i * 36); radius = outer_radius if i % 2 == 0 else inner_radius; points.append(
        (center_x + radius * math.sin(angle), center_y - radius * math.cos(angle)))
    pygame.draw.polygon(surface, color, points)


def draw_shape_7(surface, color): pygame.draw.rect(surface, color,
                                                   (10, 10, surface.get_width() - 20, surface.get_height() - 20),
                                                   10); pygame.draw.circle(surface, color, (surface.get_width() // 2,
                                                                                            surface.get_height() // 2),
                                                                           20)


def draw_shape_8(surface, color): pygame.draw.line(surface, color, (10, 10),
                                                   (surface.get_width() - 10, surface.get_height() - 10),
                                                   15); pygame.draw.line(surface, color,
                                                                         (10, surface.get_height() - 10),
                                                                         (surface.get_width() - 10, 10), 15)


def draw_shape_9(surface, color): pygame.draw.rect(surface, color,
                                                   (10, 20, surface.get_width() - 20, 20)); pygame.draw.rect(surface,
                                                                                                             color, (10,
                                                                                                                     surface.get_height() // 2 - 10,
                                                                                                                     surface.get_width() - 20,
                                                                                                                     20)); pygame.draw.rect(
    surface, color, (10, surface.get_height() - 40, surface.get_width() - 20, 20))


def draw_shape_10(surface, color): center, radius = (surface.get_width() // 2,
                                                     surface.get_height() // 2), surface.get_width() // 2 - 10; rect = (
    center[0] - radius, center[1] - radius, radius * 2, radius * 2); pygame.draw.arc(surface, color, rect,
                                                                                     math.radians(45),
                                                                                     math.radians(315), radius)


SHAPE_FUNCTIONS = [draw_shape_1, draw_shape_2, draw_shape_3, draw_shape_4, draw_shape_5, draw_shape_6, draw_shape_7,
                   draw_shape_8, draw_shape_9, draw_shape_10]


# --- UI Class ---
class Button:
    def __init__(self, x, y, width, height, text, color=(150, 250, 150), hover_color=(200, 255, 200), text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=15)
        draw_text(screen, self.text, 30, self.rect.centerx, self.rect.centery, self.text_color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False


# --- Card Class ---
class Card:
    def __init__(self, shape_id, color, x, y, card_back_style):
        self.shape_id = shape_id
        self.color = color
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.is_flipped = False
        self.is_matched = False
        self.flip_animation = 0
        self.match_animation = 0
        self.create_surfaces(card_back_style)

    def create_surfaces(self, card_back_style):
        # Create face surface
        self.face_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.face_surface, CARD_FACE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        SHAPE_FUNCTIONS[self.shape_id](self.face_surface, self.color)
        pygame.draw.rect(self.face_surface, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)

        # Create back surface using the selected style
        self.back_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        card_back_func = CARD_BACK_STYLES[card_back_style]
        card_back_func(self.back_surface, self.back_surface.get_rect())
        pygame.draw.rect(self.back_surface, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)

    def draw(self, screen):
        if self.is_matched:
            if self.match_animation < 1: self.match_animation += MATCH_ANIMATION_SPEED
            tint = pygame.Surface((CARD_WIDTH, CARD_HEIGHT));
            tint.fill(CARD_MATCHED_COLOR)
            tint.set_alpha(int(150 * self.match_animation))
            screen.blit(self.face_surface, self.rect.topleft);
            screen.blit(tint, self.rect.topleft)
            return

        if self.is_flipped and self.flip_animation < 1:
            self.flip_animation += FLIP_SPEED
        elif not self.is_flipped and self.flip_animation > 0:
            self.flip_animation -= FLIP_SPEED
        self.flip_animation = max(0, min(1, self.flip_animation))

        current_scale = abs(1 - 2 * self.flip_animation)
        surface_to_draw = self.face_surface if self.flip_animation >= 0.5 else self.back_surface
        scaled_surface = pygame.transform.scale(surface_to_draw, (int(CARD_WIDTH * current_scale), CARD_HEIGHT))
        screen.blit(scaled_surface, scaled_surface.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(
                event.pos) and not self.is_flipped and not self.is_matched:
            self.flip()
            return self
        return None

    def flip(self):
        self.is_flipped = not self.is_flipped


# --- Game Logic Functions ---
def create_board(game_state):
    num_pairs = (GRID_ROWS * GRID_COLS) // 2
    shape_ids = list(range(num_pairs))
    card_pairs = []

    palette = PALETTES[game_state['current_palette']]

    for i in range(num_pairs):
        shape_id = shape_ids[i]
        color = palette[i % len(palette)]
        card_pairs.extend([(shape_id, color), (shape_id, color)])

    random.shuffle(card_pairs)

    cards = []
    board_width = GRID_COLS * (CARD_WIDTH + CARD_GAP) - CARD_GAP
    board_height = GRID_ROWS * (CARD_HEIGHT + CARD_GAP) - CARD_GAP
    start_x, start_y = (SCREEN_WIDTH - board_width) // 2, (SCREEN_HEIGHT - board_height) // 2

    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            shape_id, color = card_pairs.pop()
            x, y = start_x + j * (CARD_WIDTH + CARD_GAP), start_y + i * (CARD_HEIGHT + CARD_GAP)
            cards.append(Card(shape_id, color, x, y, game_state['current_card_back']))
    return cards


def run_game_session(screen, clock, game_state):
    cards = create_board(game_state)
    flipped_cards = []
    moves = 0
    start_time = pygame.time.get_ticks()
    game_over = False

    running = True
    while running:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {'status': 'quit'}

            if not game_over and len(flipped_cards) < 2:
                for card in cards:
                    flipped_card = card.handle_event(event)
                    if flipped_card:
                        flipped_cards.append(flipped_card)

        if len(flipped_cards) == 2:
            pygame.time.wait(400)
            moves += 1
            card1, card2 = flipped_cards
            if card1.shape_id == card2.shape_id:
                card1.is_matched = True
                card2.is_matched = True
            else:
                card1.flip();
                card2.flip()
            flipped_cards = []

        if not game_over and all(card.is_matched for card in cards):
            game_over = True
            total_time = elapsed_time
            pygame.time.wait(1000)  # Pause to celebrate
            return {'status': 'won', 'moves': moves, 'time': total_time}

        draw_gradient_background(screen)
        for card in cards: card.draw(screen)
        draw_text(screen, f"Moves: {moves}", 36, 100, 30)
        draw_text(screen, f"Time: {elapsed_time}", 36, SCREEN_WIDTH - 100, 30)

        pygame.display.flip()
        clock.tick(60)


def run_summary_screen(screen, clock, game_state, last_game_stats):
    # Update game state
    game_state['games_played'] += 1
    game_state['total_play_time'] += last_game_stats['time']

    # Check for level up
    new_rank_unlocked = False
    old_rank = game_state['rank_name']
    for games_req, rank_info in RANKS.items():
        if game_state['games_played'] >= games_req:
            game_state['rank_name'] = rank_info['name']
            game_state['medal_color'] = rank_info['medal_color']

    if old_rank != game_state['rank_name']:
        new_rank_unlocked = True
        unlock_info = RANKS[game_state['games_played']]['unlock']
        if unlock_info[0] == 'palette':
            game_state['unlocked_palettes'].append(unlock_info[1])
        elif unlock_info[0] == 'card_back':
            game_state['unlocked_card_backs'].append(unlock_info[1])

    # UI Elements
    next_game_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Next Game")

    # Cycle buttons for cosmetics
    palette_button = Button(450, 400, 250, 40, f"Palette: {game_state['current_palette']}", (80, 80, 150),
                            (100, 100, 180))
    card_back_button = Button(450, 450, 250, 40, f"Card Back: {game_state['current_card_back']}", (80, 80, 150),
                              (100, 100, 180))

    # Animation variables
    animation_start_time = time.time()
    animation_duration = 1.5  # seconds

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if next_game_button.handle_event(event):
                return 'continue'

            if palette_button.handle_event(event):
                current_idx = game_state['unlocked_palettes'].index(game_state['current_palette'])
                next_idx = (current_idx + 1) % len(game_state['unlocked_palettes'])
                game_state['current_palette'] = game_state['unlocked_palettes'][next_idx]
                palette_button.text = f"Palette: {game_state['current_palette']}"

            if card_back_button.handle_event(event):
                current_idx = game_state['unlocked_card_backs'].index(game_state['current_card_back'])
                next_idx = (current_idx + 1) % len(game_state['unlocked_card_backs'])
                game_state['current_card_back'] = game_state['unlocked_card_backs'][next_idx]
                card_back_button.text = f"Card Back: {game_state['current_card_back']}"

        draw_gradient_background(screen)

        # --- Draw Titles ---
        draw_text(screen, "Round Complete!", 70, SCREEN_WIDTH // 2, 60)

        # --- Draw Stats Box ---
        stats_box = pygame.Rect(50, 120, 350, 400)
        pygame.draw.rect(screen, (0, 0, 0, 150), stats_box, border_radius=15)
        draw_text(screen, "Last Round", 40, stats_box.centerx, 150)
        draw_text(screen, f"Moves: {last_game_stats['moves']}", 30, stats_box.centerx, 200)
        draw_text(screen, f"Time: {last_game_stats['time']}s", 30, stats_box.centerx, 240)

        draw_text(screen, "Overall Stats", 40, stats_box.centerx, 320)
        draw_text(screen, f"Games Played: {game_state['games_played']}", 30, stats_box.centerx, 370)
        total_m, total_s = divmod(game_state['total_play_time'], 60)
        draw_text(screen, f"Total Play Time: {total_m}m {total_s}s", 30, stats_box.centerx, 410)

        # --- Draw Rank and Unlocks Box ---
        rank_box = pygame.Rect(420, 120, 330, 400)
        pygame.draw.rect(screen, (0, 0, 0, 150), rank_box, border_radius=15)
        draw_text(screen, "Your Rank", 40, rank_box.centerx, 150)

        # --- Level Up Animation ---
        if new_rank_unlocked:
            elapsed = time.time() - animation_start_time
            if elapsed < animation_duration:
                # Ease-out cubic interpolation for a smooth "pop"
                t = elapsed / animation_duration
                eased_t = 1 - pow(1 - t, 3)
                current_size = int(80 * eased_t)
                draw_text(screen, "Rank Up!", 50, rank_box.centerx, 200)
                draw_medal(screen, rank_box.centerx, 280, current_size, game_state['medal_color'])
                draw_text(screen, game_state['rank_name'], int(40 * eased_t), rank_box.centerx, 360)
            else:  # Animation finished
                draw_medal(screen, rank_box.centerx, 250, 80, game_state['medal_color'])
                draw_text(screen, game_state['rank_name'], 40, rank_box.centerx, 340)
                unlock_info = RANKS[game_state['games_played']]['unlock']
                draw_text(screen, f"Unlocked: {unlock_info[1]}", 24, rank_box.centerx, 370, (200, 255, 200))
        else:  # No animation
            draw_medal(screen, rank_box.centerx, 250, 80, game_state['medal_color'])
            draw_text(screen, game_state['rank_name'], 40, rank_box.centerx, 340)

        # Draw Customization Options
        draw_text(screen, "Customize Next Game", 30, rank_box.centerx, 390)
        palette_button.draw(screen)
        card_back_button.draw(screen)

        # Draw Next Game button
        next_game_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# --- Main Application ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Card Game")
    clock = pygame.time.Clock()

    # Persistent state across games
    game_state = {
        'games_played': 0,
        'total_play_time': 0,
        'rank_name': 'Novice',
        'medal_color': RANKS[0]['medal_color'],
        'unlocked_palettes': ['Default'],
        'unlocked_card_backs': ['Default'],
        'current_palette': 'Default',
        'current_card_back': 'Default'
    }

    app_running = True
    while app_running:
        game_result = run_game_session(screen, clock, game_state)

        if game_result['status'] == 'quit':
            app_running = False
        elif game_result['status'] == 'won':
            summary_result = run_summary_screen(screen, clock, game_state, game_result)
            if summary_result == 'quit':
                app_running = False

    pygame.quit()


if __name__ == "__main__":
    main()