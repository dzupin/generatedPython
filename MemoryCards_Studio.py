import pygame
import random
import math
import time

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_ROWS, GRID_COLS = 4, 5
CARD_WIDTH, CARD_HEIGHT, CARD_GAP = 120, 120, 20

# --- Colors ---
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (100, 100, 100)
BG_COLOR1, BG_COLOR2 = (25, 25, 50), (45, 45, 80)
CARD_FACE_COLOR, CARD_OUTLINE_COLOR = (230, 230, 255), (255, 255, 255)
CARD_MATCHED_COLOR, SHADOW_COLOR = (50, 200, 50), (20, 20, 20)

# --- UNLOCKABLE COSMETICS ---
PALETTES = {
    'Default': [(255, 105, 180), (255, 215, 0), (138, 43, 226), (0, 255, 255), (255, 165, 0), (75, 0, 130),
                (240, 230, 140), (255, 0, 0), (0, 128, 0), (0, 0, 255)],
    'Forest': [(44, 117, 44), (124, 181, 124), (16, 78, 48), (144, 238, 144), (85, 107, 47), (34, 139, 34), (0, 100, 0),
               (154, 205, 50), (107, 142, 35), (50, 205, 50)],
    'Ocean': [(0, 119, 190), (0, 188, 212), (173, 232, 244), (64, 224, 208), (0, 206, 209), (30, 144, 255),
              (70, 130, 180), (135, 206, 250), (0, 255, 255), (224, 255, 255)]
}


def draw_card_back_default(s, r):
    sc, ec = (100, 150, 255), (60, 100, 200)
    for x in range(r.width): pygame.draw.line(s, tuple(
        int(sc[i] * (1 - x / r.width) + ec[i] * x / r.width) for i in range(3)), (x, 0), (x, r.height))
    pygame.draw.line(s, WHITE, (10, 10), (r.width - 10, r.height - 10), 3);
    pygame.draw.line(s, WHITE, (10, r.height - 10), (r.width - 10, 10), 3)


def draw_card_back_circles(s, r):
    pygame.draw.rect(s, (200, 60, 60), (0, 0, r.width, r.height))
    for rad in range(10, r.width // 2, 15): pygame.draw.circle(s, WHITE, r.center, rad, 2)


CARD_BACK_STYLES = {'Default': draw_card_back_default, 'Crimson Circles': draw_card_back_circles}

# --- RANKS and SCORING ---
RANKS = {
    0: {'name': "Novice", 'medal_color': (205, 127, 50)},
    3: {'name': "Beginner", 'unlock': ('palette', 'Forest'), 'medal_color': (192, 192, 192)},
    6: {'name': "Apprentice", 'unlock': ('card_back', 'Crimson Circles'), 'medal_color': (255, 215, 0)},
}
BASE_ROUND_SCORE = 500
TIME_BONUS_SECONDS = 30

# --- Animation speeds ---
FLIP_SPEED, MATCH_ANIMATION_SPEED, PULSE_SPEED = 0.05, 0.1, 0.03


# --- Helper Functions ---
def create_background_particles():
    particles = []
    for _ in range(40):
        particles.append({
            'rect': pygame.Rect(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),
                                random.randint(10, 40), random.randint(10, 40)),
            'color': (255, 255, 255, random.randint(10, 40)),
            'speed': (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        })
    return particles


def draw_animated_background(surface, particles):
    surface.fill(BG_COLOR1)
    for p in particles:
        p['rect'].x += p['speed'][0];
        p['rect'].y += p['speed'][1]
        if p['rect'].left > SCREEN_WIDTH: p['rect'].right = 0
        if p['rect'].right < 0: p['rect'].left = SCREEN_WIDTH
        if p['rect'].top > SCREEN_HEIGHT: p['rect'].bottom = 0
        if p['rect'].bottom < 0: p['rect'].top = SCREEN_HEIGHT
        shape_surf = pygame.Surface(p['rect'].size, pygame.SRCALPHA)
        pygame.draw.ellipse(shape_surf, p['color'], (0, 0, *p['rect'].size))
        surface.blit(shape_surf, p['rect'])


def draw_text_shadow(surface, text, size, x, y, color=WHITE, align="center"):
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, color)
    shadow_surf = font.render(text, True, SHADOW_COLOR)
    text_rect = text_surf.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    surface.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
    surface.blit(text_surf, text_rect)


def draw_medal(s, x, y, size, c):
    pygame.draw.circle(s, c, (x, y), size);
    pygame.draw.circle(s, tuple(min(255, v + 30) for v in c), (x, y), size * 0.8)
    pygame.draw.rect(s, (200, 0, 0), (x - size * 0.4, y - size, size * 0.8, size * 0.5))


def fade_transition(screen, direction='out'):
    fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surf.fill(BLACK)
    for alpha in range(0, 256, 5):
        current_alpha = alpha if direction == 'out' else 255 - alpha
        fade_surf.set_alpha(current_alpha)
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)


# --- Shape Drawing Functions (minified) ---
def d_s_1(s, c): pygame.draw.polygon(s, c, [(s.get_width() // 2, 10), (s.get_width() - 10, s.get_height() // 2),
                                            (s.get_width() // 2, s.get_height() - 10), (10, s.get_height() // 2)])


def d_s_2(s, c): pygame.draw.rect(s, c, (30, 10, s.get_width() - 60, s.get_height() - 20)); pygame.draw.rect(s, c,
                                                                                                             (10, 30,
                                                                                                              s.get_width() - 20,
                                                                                                              s.get_height() - 60))


def d_s_3(s, c): c_xy = s.get_width() // 2, s.get_height() // 2; pygame.draw.circle(s, c, c_xy, s.get_width() // 2 - 10,
                                                                                    10); pygame.draw.circle(s, c, c_xy,
                                                                                                            s.get_width() // 2 - 30,
                                                                                                            10)


def d_s_4(s, c): pygame.draw.polygon(s, c, [(s.get_width() // 2, 10), (s.get_width() - 10, s.get_height() - 10),
                                            (10, s.get_height() - 10)])


def d_s_5(s, c): pygame.draw.polygon(s, c, [(10, 10), (s.get_width() - 10, 10), (10, s.get_height() - 10),
                                            (s.get_width() - 10, s.get_height() - 10)])


def d_s_6(s,
          c): cx, cy = s.get_width() // 2, s.get_height() // 2;r1, r2 = s.get_width() // 2 - 10, s.get_width() // 5;p = [];[
    p.append((cx + (r1 if i % 2 == 0 else r2) * math.sin(math.radians(i * 36)),
              cy - (r1 if i % 2 == 0 else r2) * math.cos(math.radians(i * 36)))) for i in
    range(10)];pygame.draw.polygon(s, c, p)


def d_s_7(s, c): pygame.draw.rect(s, c, (10, 10, s.get_width() - 20, s.get_height() - 20), 10);pygame.draw.circle(s, c,
                                                                                                                  (s.get_width() // 2,
                                                                                                                   s.get_height() // 2),
                                                                                                                  20)


def d_s_8(s, c): pygame.draw.line(s, c, (10, 10), (s.get_width() - 10, s.get_height() - 10), 15);pygame.draw.line(s, c,
                                                                                                                  (10,
                                                                                                                   s.get_height() - 10),
                                                                                                                  (s.get_width() - 10,
                                                                                                                   10),
                                                                                                                  15)


def d_s_9(s, c): pygame.draw.rect(s, c, (10, 20, s.get_width() - 20, 20));pygame.draw.rect(s, c, (10,
                                                                                                  s.get_height() // 2 - 10,
                                                                                                  s.get_width() - 20,
                                                                                                  20));pygame.draw.rect(
    s, c, (10, s.get_height() - 40, s.get_width() - 20, 20))


def d_s_10(s, c): c_xy, r = (s.get_width() // 2, s.get_height() // 2), s.get_width() // 2 - 10;rect = (c_xy[0] - r,
                                                                                                       c_xy[1] - r,
                                                                                                       r * 2,
                                                                                                       r * 2);pygame.draw.arc(
    s, c, rect, math.radians(45), math.radians(315), r)


SHAPE_FUNCTIONS = [d_s_1, d_s_2, d_s_3, d_s_4, d_s_5, d_s_6, d_s_7, d_s_8, d_s_9, d_s_10]


# --- UI & Game Classes ---
class Button:
    def __init__(self, x, y, w, h, text, color=(150, 250, 150), hover_color=(200, 255, 200), text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h);
        self.text, self.color, self.hover_color, self.text_color = text, color, hover_color, text_color;
        self.is_hovered = False

    def draw(self, s):
        c = self.hover_color if self.is_hovered else self.color;
        pygame.draw.rect(s, c, self.rect, border_radius=15)
        draw_text_shadow(s, self.text, 30, self.rect.centerx, self.rect.centery, self.text_color)

    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(e.pos)
        if e.type == pygame.MOUSEBUTTONDOWN and self.is_hovered: return True
        return False


class Card:
    def __init__(self, shape_id, color, x, y, card_back_style):
        self.shape_id, self.color = shape_id, color;
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.is_flipped, self.is_matched = False, False
        self.flip_anim, self.match_anim, self.pulse_anim = 0, 0, 0
        self.create_surfaces(card_back_style)

    def create_surfaces(self, style):
        self.face_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.face_surf, CARD_FACE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        SHAPE_FUNCTIONS[self.shape_id](self.face_surf, self.color)
        pygame.draw.rect(self.face_surf, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)
        self.back_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        CARD_BACK_STYLES[style](self.back_surf, self.back_surf.get_rect())
        pygame.draw.rect(self.back_surf, CARD_OUTLINE_COLOR, (0, 0, CARD_WIDTH, CARD_HEIGHT), 4, border_radius=10)

    def draw(self, screen):
        if self.is_matched:
            if self.match_anim < 1: self.match_anim += MATCH_ANIMATION_SPEED
            self.pulse_anim += PULSE_SPEED
            pulse_alpha = (math.sin(self.pulse_anim * math.pi * 2) + 1) / 2 * 60 + 20
            highlight = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 200, pulse_alpha), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
            screen.blit(self.face_surf, self.rect.topleft);
            screen.blit(highlight, self.rect.topleft)
            return
        if self.is_flipped and self.flip_anim < 1:
            self.flip_anim += FLIP_SPEED
        elif not self.is_flipped and self.flip_anim > 0:
            self.flip_anim -= FLIP_SPEED
        self.flip_anim = max(0, min(1, self.flip_anim))
        scale = abs(1 - 2 * self.flip_anim)
        surf = self.face_surf if self.flip_anim >= 0.5 else self.back_surf
        scaled = pygame.transform.scale(surf, (int(CARD_WIDTH * scale), CARD_HEIGHT))
        screen.blit(scaled, scaled.get_rect(center=self.rect.center))

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(
                e.pos) and not self.is_flipped and not self.is_matched:
            self.flip();
            return self
        return None

    def flip(self):
        self.is_flipped = not self.is_flipped


def create_board(game_state):
    num_pairs, palette = (GRID_ROWS * GRID_COLS) // 2, PALETTES[game_state['current_palette']]
    card_pairs = [];
    [card_pairs.extend([((i), palette[i % len(palette)]), ((i), palette[i % len(palette)])]) for i in range(num_pairs)]
    random.shuffle(card_pairs);
    cards = []
    board_w = GRID_COLS * (CARD_WIDTH + CARD_GAP) - CARD_GAP;
    sx, sy = (SCREEN_WIDTH - board_w) // 2, (SCREEN_HEIGHT - (GRID_ROWS * (CARD_HEIGHT + CARD_GAP) - CARD_GAP)) // 2
    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            shape_id, color = card_pairs.pop()
            cards.append(Card(shape_id, color, sx + j * (CARD_WIDTH + CARD_GAP), sy + i * (CARD_HEIGHT + CARD_GAP),
                              game_state['current_card_back']))
    return cards


def run_game_session(screen, clock, game_state, particles):
    cards = create_board(game_state)
    active_cards = []
    moves, start_time, game_over = 0, pygame.time.get_ticks(), False
    rank = game_state['rank_name']
    flip_count_for_move = 0

    running = True
    while running:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        newly_flipped = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return {'status': 'quit'}
            if rank == 'Apprentice' and len(active_cards) == 2: continue
            if not game_over:
                for card in cards:
                    if (flipped := card.handle_event(event)):
                        newly_flipped = flipped
                        flip_count_for_move += 1
                        # --- BUG FIX ---
                        # A "move" is completed every time a second card is flipped.
                        if flip_count_for_move > 0 and flip_count_for_move % 2 == 0:
                            moves += 1
                        # --- END FIX ---
                        break

        if rank == 'Apprentice':
            if newly_flipped: active_cards.append(newly_flipped)
            if len(active_cards) == 2:
                pygame.time.wait(400)
                c1, c2 = active_cards
                if c1.shape_id == c2.shape_id:
                    c1.is_matched, c2.is_matched = True, True
                else:
                    c1.flip();
                    c2.flip()
                active_cards.clear()
        else:  # Novice & Beginner
            max_visible = 3 if rank == 'Novice' else 2
            if newly_flipped:
                match_found = False
                for card in active_cards:
                    if card.shape_id == newly_flipped.shape_id:
                        card.is_matched, newly_flipped.is_matched = True, True
                        active_cards.remove(card);
                        match_found = True;
                        break
                if not match_found: active_cards.append(newly_flipped)
                if len(active_cards) > max_visible:
                    if not (card_to_hide := active_cards.pop(0)).is_matched: card_to_hide.flip()

        if not game_over and all(c.is_matched for c in cards):
            game_over = True;
            pygame.time.wait(1000)
            return {'status': 'won', 'moves': moves, 'time': elapsed_time}

        draw_animated_background(screen, particles)
        for card in cards: card.draw(screen)
        draw_text_shadow(screen, f"Moves: {moves}", 36, 100, 30)
        draw_text_shadow(screen, f"Time: {elapsed_time}", 36, SCREEN_WIDTH - 100, 30)
        pygame.display.flip();
        clock.tick(60)


def run_summary_screen(screen, clock, game_state, last_game_stats, particles):
    game_state['games_played'] += 1;
    game_state['total_play_time'] += last_game_stats['time']
    moves, time_taken = last_game_stats['moves'], last_game_stats['time']

    time_bonus = max(0, (TIME_BONUS_SECONDS - time_taken)) * 10

    perfect_moves = (GRID_ROWS * GRID_COLS) // 2
    if moves <= perfect_moves:
        efficiency_bonus = 2000
    elif moves <= perfect_moves + 2:
        efficiency_bonus = 1000
    elif moves <= perfect_moves + 5:
        efficiency_bonus = 500
    else:
        efficiency_bonus = 100

    total_earned = BASE_ROUND_SCORE + time_bonus + efficiency_bonus
    target_score = game_state['total_score'] + total_earned
    game_state['total_score'] = target_score
    if target_score > game_state['high_score']: game_state['high_score'] = target_score

    new_rank_unlocked = False;
    rank_games = 0
    for g in sorted(RANKS.keys(), reverse=True):
        if game_state['games_played'] >= g: rank_games = g; break
    if game_state['rank_name'] != RANKS[rank_games]['name']:
        new_rank_unlocked = True;
        game_state['rank_name'] = RANKS[rank_games]['name']
        game_state['medal_color'] = RANKS[rank_games]['medal_color']
        if 'unlock' in RANKS[rank_games]:
            ut, un = RANKS[rank_games]['unlock']
            if ut == 'palette':
                game_state['unlocked_palettes'].append(un)
            elif ut == 'card_back':
                game_state['unlocked_card_backs'].append(un)

    next_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Next Round")
    palette_btn = Button(450, 430, 250, 40, f"Palette: {game_state['current_palette']}", (80, 80, 150), (100, 100, 180))
    card_back_btn = Button(450, 480, 250, 40, f"Card Back: {game_state['current_card_back']}", (80, 80, 150),
                           (100, 100, 180))
    anim_start_time, displayed_score = time.time(), game_state['total_score'] - total_earned

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return 'quit'
            if next_btn.handle_event(e): return 'continue'
            if palette_btn.handle_event(e):
                idx = (game_state['unlocked_palettes'].index(game_state['current_palette']) + 1) % len(
                    game_state['unlocked_palettes'])
                game_state['current_palette'] = game_state['unlocked_palettes'][idx];
                palette_btn.text = f"Palette: {game_state['current_palette']}"
            if card_back_btn.handle_event(e):
                idx = (game_state['unlocked_card_backs'].index(game_state['current_card_back']) + 1) % len(
                    game_state['unlocked_card_backs'])
                game_state['current_card_back'] = game_state['unlocked_card_backs'][idx];
                card_back_btn.text = f"Card Back: {game_state['current_card_back']}"

        draw_animated_background(screen, particles)
        draw_text_shadow(screen, "Round Complete!", 70, SCREEN_WIDTH // 2, 50)

        box1 = pygame.Rect(50, 110, 350, 450);
        pygame.draw.rect(screen, (0, 0, 0, 150), box1, border_radius=15)
        draw_text_shadow(screen, "Performance", 40, box1.centerx, 140)
        draw_text_shadow(screen, f"Moves: {moves}", 30, box1.centerx, 190)
        draw_text_shadow(screen, f"Time: {time_taken}s", 30, box1.centerx, 225)
        draw_text_shadow(screen, "Score Earned", 40, box1.centerx, 280)
        draw_text_shadow(screen, f"Round Bonus: +{BASE_ROUND_SCORE}", 28, box1.centerx, 320, (200, 200, 200))
        draw_text_shadow(screen, f"Time Bonus: +{time_bonus}", 28, box1.centerx, 350, (200, 200, 200))
        draw_text_shadow(screen, f"Efficiency Bonus: +{efficiency_bonus}", 28, box1.centerx, 380, (220, 220, 150))
        if displayed_score < target_score: displayed_score = min(target_score,
                                                                 displayed_score + int(total_earned / 60) + 1)
        draw_text_shadow(screen, "Total Score", 40, box1.centerx, 440)
        draw_text_shadow(screen, f"{displayed_score:,}", 50, box1.centerx, 480)
        draw_text_shadow(screen, f"High Score: {game_state['high_score']:,}", 24, box1.centerx, 520, (200, 200, 200))

        box2 = pygame.Rect(420, 110, 330, 450);
        pygame.draw.rect(screen, (0, 0, 0, 150), box2, border_radius=15)
        draw_text_shadow(screen, "Your Rank", 40, box2.centerx, 140)
        if new_rank_unlocked and time.time() - anim_start_time < 1.5:
            t = (time.time() - anim_start_time) / 1.5;
            et = 1 - pow(1 - t, 3)
            draw_text_shadow(screen, "Rank Up!", 50, box2.centerx, 190);
            draw_medal(screen, box2.centerx, 270, int(80 * et), game_state['medal_color']);
            draw_text_shadow(screen, game_state['rank_name'], int(40 * et), box2.centerx, 350)
        else:
            draw_medal(screen, box2.centerx, 240, 80, game_state['medal_color']);
            draw_text_shadow(screen, game_state['rank_name'], 40, box2.centerx, 330)
            if new_rank_unlocked: draw_text_shadow(screen, f"Unlocked: {RANKS[rank_games]['unlock'][1]}", 24,
                                                   box2.centerx, 360, (200, 255, 200))

        draw_text_shadow(screen, "Customize", 30, box2.centerx, 400)
        palette_btn.draw(screen);
        card_back_btn.draw(screen)

        next_btn.draw(screen);
        pygame.display.flip();
        clock.tick(60)


# --- Main Application ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Card Game - Final Edition")
    clock = pygame.time.Clock()
    game_state = {
        'games_played': 0, 'total_play_time': 0, 'rank_name': 'Novice', 'medal_color': RANKS[0]['medal_color'],
        'unlocked_palettes': ['Default'], 'unlocked_card_backs': ['Default'],
        'current_palette': 'Default', 'current_card_back': 'Default',
        'total_score': 0, 'high_score': 0
    }
    particles = create_background_particles()
    app_running = True
    while app_running:
        game_result = run_game_session(screen, clock, game_state, particles)
        if game_result['status'] == 'quit':
            app_running = False
        elif game_result['status'] == 'won':
            fade_transition(screen, 'out')
            if run_summary_screen(screen, clock, game_state, game_result, particles) == 'quit':
                app_running = False
            else:
                fade_transition(screen, 'in')
    pygame.quit()


if __name__ == "__main__":
    main()