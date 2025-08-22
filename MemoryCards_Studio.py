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


def draw_card_back_default(surface, rect):
    start_color, end_color = (100, 150, 255), (60, 100, 200)
    for x in range(rect.width):
        ratio = x / rect.width
        color = tuple(int(start_color[i] * (1 - ratio) + end_color[i] * ratio) for i in range(3))
        pygame.draw.line(surface, color, (x, 0), (x, rect.height))
    pygame.draw.line(surface, WHITE, (10, 10), (rect.width - 10, rect.height - 10), 3)
    pygame.draw.line(surface, WHITE, (10, rect.height - 10), (rect.width - 10, 10), 3)


def draw_card_back_circles(surface, rect):
    pygame.draw.rect(surface, (200, 60, 60), (0, 0, rect.width, rect.height))
    for r in range(10, rect.width // 2, 15): pygame.draw.circle(surface, WHITE, rect.center, r, 2)


CARD_BACK_STYLES = {'Default': draw_card_back_default, 'Crimson Circles': draw_card_back_circles}

# --- RANKS and UNLOCKS ---
RANKS = {
    0: {'name': "Novice", 'medal_color': (205, 127, 50)},
    3: {'name': "Beginner", 'unlock': ('palette', 'Forest'), 'medal_color': (192, 192, 192)},
    6: {'name': "Apprentice", 'unlock': ('card_back', 'Crimson Circles'), 'medal_color': (255, 215, 0)},
}

# --- Animation speeds ---
FLIP_SPEED = 0.05
MATCH_ANIMATION_SPEED = 0.1


# --- Helper Functions ---
def draw_gradient_background(surface):
    start_color, end_color = BG_COLOR1, BG_COLOR2
    for y in range(surface.get_height()):
        ratio = y / surface.get_height()
        color = tuple(int(start_color[i] * (1 - ratio) + end_color[i] * ratio) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


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
    pygame.draw.circle(surface, color, (x, y), size)
    pygame.draw.circle(surface, tuple(min(255, c + 30) for c in color), (x, y), size * 0.8)
    pygame.draw.rect(surface, (200, 0, 0), (x - size * 0.4, y - size, size * 0.8, size * 0.5))


# --- Shape Drawing Functions (minified for brevity) ---
def draw_shape_1(s, c): pygame.draw.polygon(s, c, [(s.get_width() // 2, 10), (s.get_width() - 10, s.get_height() // 2),
                                                   (s.get_width() // 2, s.get_height() - 10),
                                                   (10, s.get_height() // 2)])


def draw_shape_2(s, c): pygame.draw.rect(s, c, (30, 10, s.get_width() - 60, s.get_height() - 20)); pygame.draw.rect(s,
                                                                                                                    c,
                                                                                                                    (10,
                                                                                                                     30,
                                                                                                                     s.get_width() - 20,
                                                                                                                     s.get_height() - 60))


def draw_shape_3(s, c): center = s.get_width() // 2, s.get_height() // 2; pygame.draw.circle(s, c, center,
                                                                                             s.get_width() // 2 - 10,
                                                                                             10); pygame.draw.circle(s,
                                                                                                                     c,
                                                                                                                     center,
                                                                                                                     s.get_width() // 2 - 30,
                                                                                                                     10)


def draw_shape_4(s, c): pygame.draw.polygon(s, c, [(s.get_width() // 2, 10), (s.get_width() - 10, s.get_height() - 10),
                                                   (10, s.get_height() - 10)])


def draw_shape_5(s, c): pygame.draw.polygon(s, c, [(10, 10), (s.get_width() - 10, 10), (10, s.get_height() - 10),
                                                   (s.get_width() - 10, s.get_height() - 10)])


def draw_shape_6(s,
                 c): cx, cy = s.get_width() // 2, s.get_height() // 2;r1, r2 = s.get_width() // 2 - 10, s.get_width() // 5;p = [];[
    p.append((cx + (r1 if i % 2 == 0 else r2) * math.sin(math.radians(i * 36)),
              cy - (r1 if i % 2 == 0 else r2) * math.cos(math.radians(i * 36)))) for i in
    range(10)];pygame.draw.polygon(s, c, p)


def draw_shape_7(s, c): pygame.draw.rect(s, c, (10, 10, s.get_width() - 20, s.get_height() - 20),
                                         10);pygame.draw.circle(s, c, (s.get_width() // 2, s.get_height() // 2), 20)


def draw_shape_8(s, c): pygame.draw.line(s, c, (10, 10), (s.get_width() - 10, s.get_height() - 10),
                                         15);pygame.draw.line(s, c, (10, s.get_height() - 10), (s.get_width() - 10, 10),
                                                              15)


def draw_shape_9(s, c): pygame.draw.rect(s, c, (10, 20, s.get_width() - 20, 20));pygame.draw.rect(s, c, (10,
                                                                                                         s.get_height() // 2 - 10,
                                                                                                         s.get_width() - 20,
                                                                                                         20));pygame.draw.rect(
    s, c, (10, s.get_height() - 40, s.get_width() - 20, 20))


def draw_shape_10(s, c): center, r = (s.get_width() // 2, s.get_height() // 2), s.get_width() // 2 - 10;rect = (
    center[0] - r, center[1] - r, r * 2, r * 2);pygame.draw.arc(s, c, rect, math.radians(45), math.radians(315), r)


SHAPE_FUNCTIONS = [draw_shape_1, draw_shape_2, draw_shape_3, draw_shape_4, draw_shape_5, draw_shape_6, draw_shape_7,
                   draw_shape_8, draw_shape_9, draw_shape_10]


# --- UI Class ---
class Button:
    def __init__(self, x, y, width, height, text, color=(150, 250, 150), hover_color=(200, 255, 200), text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.color, self.hover_color, self.text_color = text, color, hover_color, text_color
        self.is_hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=15)
        draw_text(screen, self.text, 30, self.rect.centerx, self.rect.centery, self.text_color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered: return True
        return False


# --- Card Class ---
class Card:
    def __init__(self, shape_id, color, x, y, card_back_style):
        self.shape_id, self.color = shape_id, color
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.is_flipped, self.is_matched = False, False
        self.flip_animation, self.match_animation = 0, 0
        self.create_surfaces(card_back_style)

    def create_surfaces(self, card_back_style):
        self.face_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.face_surface, CARD_FACE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        SHAPE_FUNCTIONS[self.shape_id](self.face_surface, self.color)
        pygame.draw.rect(self.face_surface, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)
        self.back_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        CARD_BACK_STYLES[card_back_style](self.back_surface, self.back_surface.get_rect())
        pygame.draw.rect(self.back_surface, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)

    def draw(self, screen):
        if self.is_matched:
            if self.match_animation < 1: self.match_animation += MATCH_ANIMATION_SPEED
            tint = pygame.Surface((CARD_WIDTH, CARD_HEIGHT));
            tint.fill(CARD_MATCHED_COLOR);
            tint.set_alpha(int(150 * self.match_animation))
            screen.blit(self.face_surface, self.rect.topleft);
            screen.blit(tint, self.rect.topleft)
            return
        if self.is_flipped and self.flip_animation < 1:
            self.flip_animation += FLIP_SPEED
        elif not self.is_flipped and self.flip_animation > 0:
            self.flip_animation -= FLIP_SPEED
        self.flip_animation = max(0, min(1, self.flip_animation))
        scale = abs(1 - 2 * self.flip_animation)
        surf = self.face_surface if self.flip_animation >= 0.5 else self.back_surface
        scaled_surf = pygame.transform.scale(surf, (int(CARD_WIDTH * scale), CARD_HEIGHT))
        screen.blit(scaled_surf, scaled_surf.get_rect(center=self.rect.center))

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
    palette = PALETTES[game_state['current_palette']]
    card_pairs = []
    for i in range(num_pairs): card_pairs.extend([((i), palette[i % len(palette)]), ((i), palette[i % len(palette)])])
    random.shuffle(card_pairs)
    cards = []
    board_w = GRID_COLS * (CARD_WIDTH + CARD_GAP) - CARD_GAP
    start_x, start_y = (SCREEN_WIDTH - board_w) // 2, (
                SCREEN_HEIGHT - (GRID_ROWS * (CARD_HEIGHT + CARD_GAP) - CARD_GAP)) // 2
    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            shape_id, color = card_pairs.pop()
            cards.append(
                Card(shape_id, color, start_x + j * (CARD_WIDTH + CARD_GAP), start_y + i * (CARD_HEIGHT + CARD_GAP),
                     game_state['current_card_back']))
    return cards


def run_game_session(screen, clock, game_state):
    cards = create_board(game_state)
    active_cards = []
    moves, start_time, game_over = 0, pygame.time.get_ticks(), False
    rank = game_state['rank_name']

    running = True
    while running:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

        # --- Event Handling ---
        newly_flipped_card = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return {'status': 'quit'}

            # Prevent interaction while Apprentice pair is being checked
            if rank == 'Apprentice' and len(active_cards) == 2: continue

            if not game_over:
                for card in cards:
                    if (flipped := card.handle_event(event)):
                        newly_flipped_card = flipped
                        break

        # --- Game Logic based on Rank ---
        if rank == 'Apprentice':
            if newly_flipped_card: active_cards.append(newly_flipped_card)

            if len(active_cards) == 2:
                pygame.time.wait(400)
                moves += 1
                card1, card2 = active_cards
                if card1.shape_id == card2.shape_id:
                    card1.is_matched, card2.is_matched = True, True
                else:
                    card1.flip();
                    card2.flip()
                active_cards.clear()

        else:  # Logic for Novice and Beginner
            max_visible = 3 if rank == 'Novice' else 2

            if newly_flipped_card:
                match_found = False
                # Check for a match with any existing active card
                for card in active_cards:
                    if card.shape_id == newly_flipped_card.shape_id:
                        moves += 1
                        card.is_matched, newly_flipped_card.is_matched = True, True
                        active_cards.remove(card)
                        match_found = True
                        break

                if not match_found:
                    active_cards.append(newly_flipped_card)

                # Enforce visibility limit
                if len(active_cards) > max_visible:
                    card_to_hide = active_cards.pop(0)
                    if not card_to_hide.is_matched:
                        card_to_hide.flip()

        # --- Win Condition & Drawing ---
        if not game_over and all(card.is_matched for card in cards):
            game_over = True
            pygame.time.wait(1000)
            return {'status': 'won', 'moves': moves, 'time': elapsed_time}

        draw_gradient_background(screen)
        for card in cards: card.draw(screen)
        draw_text(screen, f"Moves: {moves}", 36, 100, 30)
        draw_text(screen, f"Time: {elapsed_time}", 36, SCREEN_WIDTH - 100, 30)

        pygame.display.flip()
        clock.tick(60)


def run_summary_screen(screen, clock, game_state, last_game_stats):
    game_state['games_played'] += 1
    game_state['total_play_time'] += last_game_stats['time']
    new_rank_unlocked, old_rank = False, game_state['rank_name']

    current_rank_games = 0
    for games_req in sorted(RANKS.keys(), reverse=True):
        if game_state['games_played'] >= games_req:
            current_rank_games = games_req
            break

    if game_state['rank_name'] != RANKS[current_rank_games]['name']:
        new_rank_unlocked = True
        game_state['rank_name'] = RANKS[current_rank_games]['name']
        game_state['medal_color'] = RANKS[current_rank_games]['medal_color']
        if 'unlock' in RANKS[current_rank_games]:
            unlock_type, unlock_name = RANKS[current_rank_games]['unlock']
            if unlock_type == 'palette':
                game_state['unlocked_palettes'].append(unlock_name)
            elif unlock_type == 'card_back':
                game_state['unlocked_card_backs'].append(unlock_name)

    next_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Next Game")
    palette_btn = Button(450, 400, 250, 40, f"Palette: {game_state['current_palette']}", (80, 80, 150), (100, 100, 180))
    card_back_btn = Button(450, 450, 250, 40, f"Card Back: {game_state['current_card_back']}", (80, 80, 150),
                           (100, 100, 180))
    anim_start_time = time.time()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'quit'
            if next_btn.handle_event(event): return 'continue'
            if palette_btn.handle_event(event):
                idx = (game_state['unlocked_palettes'].index(game_state['current_palette']) + 1) % len(
                    game_state['unlocked_palettes'])
                game_state['current_palette'] = game_state['unlocked_palettes'][idx]
                palette_btn.text = f"Palette: {game_state['current_palette']}"
            if card_back_btn.handle_event(event):
                idx = (game_state['unlocked_card_backs'].index(game_state['current_card_back']) + 1) % len(
                    game_state['unlocked_card_backs'])
                game_state['current_card_back'] = game_state['unlocked_card_backs'][idx]
                card_back_btn.text = f"Card Back: {game_state['current_card_back']}"

        draw_gradient_background(screen)
        draw_text(screen, "Round Complete!", 70, SCREEN_WIDTH // 2, 60)

        stats_box = pygame.Rect(50, 120, 350, 400);
        pygame.draw.rect(screen, (0, 0, 0, 150), stats_box, border_radius=15)
        draw_text(screen, "Last Round", 40, stats_box.centerx, 150)
        draw_text(screen, f"Moves: {last_game_stats['moves']}", 30, stats_box.centerx, 200)
        draw_text(screen, f"Time: {last_game_stats['time']}s", 30, stats_box.centerx, 240)
        draw_text(screen, "Overall Stats", 40, stats_box.centerx, 320)
        draw_text(screen, f"Games Played: {game_state['games_played']}", 30, stats_box.centerx, 370)
        m, s = divmod(game_state['total_play_time'], 60)
        draw_text(screen, f"Total Play Time: {m}m {s}s", 30, stats_box.centerx, 410)

        rank_box = pygame.Rect(420, 120, 330, 400);
        pygame.draw.rect(screen, (0, 0, 0, 150), rank_box, border_radius=15)
        draw_text(screen, "Your Rank", 40, rank_box.centerx, 150)

        if new_rank_unlocked and time.time() - anim_start_time < 1.5:
            t = (time.time() - anim_start_time) / 1.5;
            eased_t = 1 - pow(1 - t, 3)
            draw_text(screen, "Rank Up!", 50, rank_box.centerx, 200);
            draw_medal(screen, rank_box.centerx, 280, int(80 * eased_t), game_state['medal_color']);
            draw_text(screen, game_state['rank_name'], int(40 * eased_t), rank_box.centerx, 360)
        else:
            draw_medal(screen, rank_box.centerx, 250, 80, game_state['medal_color']);
            draw_text(screen, game_state['rank_name'], 40, rank_box.centerx, 340)
            if new_rank_unlocked: draw_text(screen, f"Unlocked: {RANKS[current_rank_games]['unlock'][1]}", 24,
                                            rank_box.centerx, 370, (200, 255, 200))

        draw_text(screen, "Customize Next Game", 30, rank_box.centerx, 390)
        palette_btn.draw(screen);
        card_back_btn.draw(screen);
        next_btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)


# --- Main Application ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Card Game")
    clock = pygame.time.Clock()
    game_state = {
        'games_played': 0, 'total_play_time': 0, 'rank_name': 'Novice', 'medal_color': RANKS[0]['medal_color'],
        'unlocked_palettes': ['Default'], 'unlocked_card_backs': ['Default'],
        'current_palette': 'Default', 'current_card_back': 'Default'
    }
    app_running = True
    while app_running:
        game_result = run_game_session(screen, clock, game_state)
        if game_result['status'] == 'quit':
            app_running = False
        elif game_result['status'] == 'won':
            if run_summary_screen(screen, clock, game_state, game_result) == 'quit': app_running = False
    pygame.quit()


if __name__ == "__main__":
    main()