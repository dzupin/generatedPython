# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 4-shot  (but very good in fixing bugs)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 163000 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/zen4-coder.i1-Q6_K.gguf

import pygame
import random
import math
import json
import os

# --- CONFIGURATION & CONSTANTS ---
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Base Color Palette
BASE_COLORS = {
    'bg': (15, 15, 20),
    'grid': (25, 25, 30),
    'snake_head': (0, 255, 170),
    'snake_body': (0, 200, 140),
    'food': (255, 80, 80),
    'text': (255, 255, 255),
    'accent': (0, 255, 170)
}

# Map Dictionary Colors to Standalone Variables for Class Access
BG_COLOR = BASE_COLORS['bg']
GRID_COLOR = BASE_COLORS['grid']
SNAKE_HEAD_COLOR = BASE_COLORS['snake_head']
SNAKE_BODY_COLOR = BASE_COLORS['snake_body']
FOOD_COLOR = BASE_COLORS['food']
TEXT_COLOR = BASE_COLORS['text']
GLOW_COLOR = BASE_COLORS['accent']

# Game Settings
INITIAL_FPS = 12
MAX_FPS = 25


# --- UTILITIES ---

def get_high_score():
    score_file = "snake_highscore.json"
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                data = json.load(f)
                return data.get('highscore', 0)
        except:
            return 0
    return 0


def save_high_score(score):
    score_file = "snake_highscore.json"
    try:
        with open(score_file, 'w') as f:
            json.dump({'highscore': score}, f)
    except:
        pass


def calculate_hue_shift(score):
    """Returns an HSL hue value that shifts every 50 points"""
    hue = (score * 2) % 360
    return hue


# --- CLASSES ---

class Particle:
    def __init__(self, x, y, color, speed_multiplier=1.0, size_var=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6) * size_var
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4) * speed_multiplier
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.gravity = random.uniform(0.05, 0.15)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity  # Add gravity effect
        self.life -= self.decay
        self.size *= 0.96

    def draw(self, surface):
        if isinstance(self.color, tuple):
            r, g, b = self.color[:3]
        else:
            r, g, b = self.color, self.color, self.color

        alpha = int(255 * max(0, self.life))
        final_color = (r, g, b, alpha)
        pygame.draw.circle(surface, final_color, (int(self.x), int(self.y)), max(1, self.size))


class FloatingText:
    def __init__(self, text, x, y, color, size=24, life=30):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.velocity_y = -1.5  # Floats up
        self.font = pygame.font.SysFont('Segoe UI', size, bold=True)

    def update(self):
        self.y += self.velocity_y
        self.life -= 1
        self.velocity_y *= 0.95  # Slow down float

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.score = 0
        self.grow_pending = 0
        self.dead = False
        self.speed = INITIAL_FPS

    def change_direction(self, direction):
        current_dir = self.direction
        # Prevent reversing
        if direction[0] + current_dir[0] != 0 or direction[1] + current_dir[1] != 0:
            self.direction = direction

    def update(self, food, combo_manager):
        if self.dead:
            return True

        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Wall Collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.dead = True
            return False

        # Self Collision
        if new_head in self.body[:-1]:
            self.dead = True
            return False

        self.body.insert(0, new_head)

        # Check Food
        if new_head == food.position:
            self.score += combo_manager.calculate_score_increment()
            self.grow_pending += 1

            # Increase game speed slightly every 50 points
            if self.score > 0 and self.score % 50 == 0:
                self.speed = min(self.speed + 1, MAX_FPS)

            food.locked = False
            food.spawn(self.body)
            combo_manager.activate_combo()  # Start or continue combo

            return True

        # Handle Growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return True

    def draw(self, surface, time_offset):
        for i, (x, y) in enumerate(self.body):
            # Dynamic Head Color
            if i == 0:
                # Shift head hue slightly based on score
                hue = calculate_hue_shift(self.score)
                base_h, base_s, base_l = self.rgb_to_hsl(*SNAKE_HEAD_COLOR)
                # Apply hue shift
                new_h = (base_h + (hue // 4)) % 360
                r, g, b = self.hsl_to_rgb(new_h, base_s, base_l)
                color = (r, g, b)
                size = GRID_SIZE + 2
                offset = -1
            else:
                # --- FIXED SECTION STARTS HERE ---
                factor = i * 0.05
                # Clamp values between 0 and 255 to prevent ValueError
                r = max(0, min(255, int(SNAKE_BODY_COLOR[0] * (1 - factor))))
                g = max(0, min(255, int(SNAKE_BODY_COLOR[1] * (1 - factor))))
                b = max(0, min(255, int(SNAKE_BODY_COLOR[2] * (1 - factor))))
                color = (r, g, b)
                # --- FIXED SECTION ENDS HERE ---

                size = GRID_SIZE
                offset = 0

            rect = pygame.Rect(x * GRID_SIZE + offset, y * GRID_SIZE + offset, size, size)

            # Glow effect for head
            if i == 0:
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                # Pulsating glow size
                pulse = math.sin(time_offset * 0.1) * 5
                glow_radius = GRID_SIZE * 1.5 + pulse
                pygame.draw.circle(glow_surf, (*color, 50),
                                   (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2), glow_radius)
                surface.blit(glow_surf, (0, 0))

            # This line was crashing because color was sometimes out of bounds
            pygame.draw.rect(surface, color, rect, border_radius=7)

            # Eyes
            if i == 0:
                eye_size = 4
                hx, hy = x * GRID_SIZE, y * GRID_SIZE
                dx, dy = self.direction
                eye_color = (255, 255, 255) if i == 0 else (20, 20, 20)

                if dx == 1:
                    left_eye_pos = (hx + 12, hy + 5);
                    right_eye_pos = (hx + 12, hy + 15)
                elif dx == -1:
                    left_eye_pos = (hx + 8, hy + 5);
                    right_eye_pos = (hx + 8, hy + 15)
                elif dy == -1:
                    left_eye_pos = (hx + 5, hy + 8);
                    right_eye_pos = (hx + 15, hy + 8)
                else:
                    left_eye_pos = (hx + 5, hy + 12);
                    right_eye_pos = (hx + 15, hy + 12)

                pygame.draw.circle(surface, eye_color, left_eye_pos, eye_size)
                pygame.draw.circle(surface, eye_color, right_eye_pos, eye_size)

    def get_head_position(self):
        return self.body[0]

    # Helper for color shifting
    def rgb_to_hsl(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        cmax = max(r, g, b);
        cmin = min(r, g, b);
        diff = cmax - cmin
        if cmax == cmin:
            h = 0
        elif cmax == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif cmax == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        l = (cmax + cmin) / 2
        s = diff / (1 - abs(2 * l - 1)) if l != 0 and l != 1 else 0
        return h, s * 100, l * 100

    def hsl_to_rgb(self, h, s, l):
        h, s, l = h / 360, s / 100, l / 100
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1 / 6: return p + (q - p) * 6 * t
                if t < 1 / 2: return q
                if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
                return p

            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1 / 3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1 / 3)
        return int(r * 255), int(g * 255), int(b * 255)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.pulse = 0
        self.locked = False

    def spawn(self, snake_body):
        should_move = not self.locked
        if self.locked and self.position in snake_body:
            should_move = True

        if should_move:
            max_attempts = 100
            attempts = 0
            while attempts < max_attempts:
                new_pos = (random.randint(0, GRID_WIDTH - 1),
                           random.randint(0, GRID_HEIGHT - 1))
                if new_pos not in snake_body:
                    self.position = new_pos
                    self.locked = True
                    self.pulse = 0
                    break
                attempts += 1
            if attempts >= max_attempts:
                self.locked = False

    def draw(self, surface, time_offset):
        x, y = self.position
        self.pulse += 0.2

        radius = GRID_SIZE // 2 - 2 + math.sin(self.pulse) * 5

        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # Dynamic Food Color based on time
        hue_shift = (time_offset * 0.5) % 360
        base_h, base_s, base_l = self.rgb_to_hsl(*FOOD_COLOR)
        new_h = (hue_shift + base_h) % 360
        r, g, b = self.hsl_to_rgb(new_h, base_s, base_l)

        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = 40 + int(math.sin(self.pulse) * 30)
        pygame.draw.circle(glow_surf, (r, g, b, alpha), (center_x, center_y), radius * 2.5)
        surface.blit(glow_surf, (0, 0))

        pygame.draw.circle(surface, (r, g, b), (center_x, center_y), radius)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 3, center_y - 3), radius // 3)

    def rgb_to_hsl(self, r, g, b):
        return self.__class__.rgb_to_hsl_static(r, g, b)

    def hsl_to_rgb(self, h, s, l):
        return self.__class__.hsl_to_rgb_static(h, s, l)

    @staticmethod
    def rgb_to_hsl_static(r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        cmax, cmin, diff = max(r, g, b), min(r, g, b), max(r, g, b) - min(r, g, b)
        h = 0
        if diff != 0:
            if cmax == r:
                h = (60 * ((g - b) / diff) + 360) % 360
            elif cmax == g:
                h = (60 * ((b - r) / diff) + 120) % 360
            else:
                h = (60 * ((r - g) / diff) + 240) % 360
        l = (cmax + cmin) / 2
        s = diff / (1 - abs(2 * l - 1)) if l != 0 and l != 1 else 0
        return h, s * 100, l * 100

    @staticmethod
    def hsl_to_rgb_static(h, s, l):
        h, s, l = h / 360, s / 100, l / 100
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1 / 6: return p + (q - p) * 6 * t
                if t < 1 / 2: return q
                if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
                return p

            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1 / 3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1 / 3)
        return int(r * 255), int(g * 255), int(b * 255)


class ComboManager:
    def __init__(self):
        self.combo = 0
        self.combo_timer = 0
        self.max_combo_time = 60  # Frames (approx 5 seconds)
        self.combo_multiplier = 1

    def activate_combo(self):
        self.combo_timer = self.max_combo_time
        if self.combo > 0:
            self.combo += 1
        else:
            self.combo = 1

        # Multiplier logic: 1x, 1.5x, 2x, 2.5x...
        self.combo_multiplier = 1 + (self.combo // 2) * 0.5

    def calculate_score_increment(self):
        base_score = 10
        return int(base_score * self.combo_multiplier)

    def update(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
        elif self.combo > 0:
            # Combo expired
            self.combo = 0
            self.combo_multiplier = 1

    def get_formatted_combo(self):
        if self.combo > 1:
            return f"{self.combo}x COMBO!"
        return ""


# --- MAIN GAME LOGIC ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Snake - Addictive Edition")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Segoe UI', 24)
    big_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
    small_font = pygame.font.SysFont('Segoe UI', 18)

    # Game State
    snake = Snake()
    food = Food()
    combo_manager = ComboManager()
    particles = []
    floating_texts = []

    high_score = get_high_score()
    food.spawn(snake.body)

    game_running = True
    game_over = False
    paused = False
    time_offset = 0
    screen_shake = 0

    while True:
        while game_running:
            time_offset += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_RETURN:
                            snake.reset()
                            combo_manager = ComboManager()  # Reset combo on restart
                            food.spawn(snake.body)
                            particles.clear()
                            floating_texts.clear()
                            game_over = False
                            game_running = True
                    elif paused:
                        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                            paused = False
                            game_running = True
                    else:
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            snake.change_direction((0, -1))
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            snake.change_direction((0, 1))
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            snake.change_direction((-1, 0))
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            snake.change_direction((1, 0))
                        elif event.key == pygame.K_ESCAPE:
                            paused = True; game_running = False

            if not paused and not game_over:
                # Update Logic
                ate_food = snake.update(food, combo_manager)
                combo_manager.update()

                # Screen Shake Logic
                if screen_shake > 0:
                    screen_shake *= 0.9
                    if screen_shake < 0.5: screen_shake = 0

                if ate_food:
                    hx, hy = snake.get_head_position()
                    cx = hx * GRID_SIZE + GRID_SIZE // 2
                    cy = hy * GRID_SIZE + GRID_SIZE // 2

                    # Spawn Particles
                    for _ in range(10):
                        particles.append(Particle(cx, cy, FOOD_COLOR))

                    # Spawn Floating Text
                    score_gained = int(10 * combo_manager.combo_multiplier)
                    text_color = (255, 255, 0) if combo_manager.combo > 1 else TEXT_COLOR
                    floating_texts.append(FloatingText(f"+{score_gained}", cx, cy, text_color))

                # Handle Game Over
                if snake.dead:
                    game_over = True
                    if snake.score > high_score:
                        high_score = snake.score
                        save_high_score(high_score)
                    screen_shake = 20  # Big shake on death

                # Update Visual Lists
                particles = [p for p in particles if p.life > 0.05]
                for p in particles: p.update()

                floating_texts = [ft for ft in floating_texts if ft.life > 0]
                for ft in floating_texts: ft.update()

            # --- DRAWING ---

            # Dynamic Background
            hue = calculate_hue_shift(snake.score)
            bg_hsl = list(BASE_COLORS['bg'])
            # Convert BG to HSL roughly for shift, then back
            # Simple approach: Shift BG color slightly
            bg_hue_mod = (time_offset * 0.1) % 360
            screen.fill(BG_COLOR)

            # Draw Grid
            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

            # Apply Screen Shake
            shake_offset_x = random.uniform(-screen_shake, screen_shake)
            shake_offset_y = random.uniform(-screen_shake, screen_shake)
            screen.fill(BG_COLOR)  # Clear again with shake logic if we wanted complex bg, but simple fill works

            # Draw Entities
            food.draw(screen, time_offset)
            snake.draw(screen, time_offset)
            for p in particles: p.draw(screen)
            for ft in floating_texts: ft.draw(screen)

            # --- HUD ---
            score_text = font.render(f"Score: {snake.score}", True, TEXT_COLOR)
            screen.blit(score_text, (15, 15))

            high_score_text = small_font.render(f"Best: {high_score}", True, (150, 150, 150))
            screen.blit(high_score_text, (WIDTH - 120, 15))

            combo_text = combo_manager.get_formatted_combo()
            if combo_text:
                combo_surf = big_font.render(combo_text, True, (255, 215, 0))
                # Fade combo out if timer is low
                alpha = int(255 * (combo_manager.combo_timer / combo_manager.max_combo_time))
                combo_surf.set_alpha(alpha)
                screen.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, HEIGHT - 100))

            if paused and not game_over:
                pause_text = big_font.render("PAUSED", True, TEXT_COLOR)
                rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(pause_text, rect)

            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BG_COLOR)
                screen.blit(overlay, (0, 0))

                go_text = big_font.render("GAME OVER", True, (255, 60, 60))
                go_rect = go_text.get_rect(center=(WIDTH // 2 + shake_offset_x, HEIGHT // 2 - 50 + shake_offset_y))
                screen.blit(go_text, go_rect)

                final_score_text = font.render(f"Final Score: {snake.score}", True, TEXT_COLOR)
                final_rect = final_score_text.get_rect(
                    center=(WIDTH // 2 + shake_offset_x, HEIGHT // 2 + 10 + shake_offset_y))
                screen.blit(final_score_text, final_rect)

                restart_text = small_font.render("Press ENTER to Restart", True, GLOW_COLOR)
                restart_rect = restart_text.get_rect(
                    center=(WIDTH // 2 + shake_offset_x, HEIGHT // 2 + 60 + shake_offset_y))
                screen.blit(restart_text, restart_rect)

            pygame.display.flip()
            clock.tick(snake.speed)

        # --- PAUSE LOOP ---
        while not game_running and not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                        game_running = True

            # Dim background
            dim = pygame.Surface((WIDTH, HEIGHT))
            dim.set_alpha(150)
            dim.fill(BG_COLOR)
            screen.blit(dim, (0, 0))

            pause_text = big_font.render("PAUSED", True, TEXT_COLOR)
            rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, rect)

            pygame.display.flip()
            clock.tick(10)


if __name__ == "__main__":
    main()
