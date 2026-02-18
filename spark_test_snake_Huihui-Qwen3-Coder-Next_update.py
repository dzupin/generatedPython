# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play.

# functional  context 256K perfect summary  partial censor Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf    (https://huggingface.co/unsloth/Qwen3-Next-80B-A3B-Instruct-GGUF)  (text only)
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf

import pygame
import random
import math
import os
import json
import numpy

# --- Initialization ---
pygame.init()
pygame.font.init()
pygame.display.set_caption("Neon Snake: Addictive Edition")

# Screen Dimensions
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# --- Color Palettes ---
THEMES = {
    "neon": {
        "bg": (20, 20, 40),
        "snake": (0, 255, 128),
        "snake_head": (0, 230, 100),
        "food": (255, 50, 100),
        "text": (255, 255, 255),
        "accent": (50, 200, 255)
    },
    "sunset": {
        "bg": (50, 30, 20),
        "snake": (255, 200, 50),
        "snake_head": (255, 150, 50),
        "food": (255, 50, 100),
        "text": (255, 240, 220),
        "accent": (200, 50, 255)
    },
    "matrix": {
        "bg": (0, 20, 0),
        "snake": (0, 255, 0),
        "snake_head": (0, 200, 0),
        "food": (255, 255, 0),
        "text": (200, 255, 200),
        "accent": (50, 255, 50)
    }
}

# --- Audio System (Synthesizer) ---
class SoundManager:
    def __init__(self):
        self.freq = 44100
        self.size = -16
        self.channels = 2
        self.buffer = 4096
        try:
            pygame.mixer.init(self.freq, self.size, self.channels, self.buffer)
            pygame.mixer.set_num_channels(8)
        except Exception as e:
            print(f"Mixer init skipped: {e}")

    def play_tone(self, freq, duration, volume=0.3, wave_type='sine'):
        try:
            sample_rate = pygame.mixer.get_init()[0]
            n_samples = int(sample_rate * duration)
            buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
            max_sample = 2 ** (abs(self.size) - 1)

            for s in range(n_samples):
                t = float(s) / sample_rate

                if wave_type == 'sine':
                    value = math.sin(2 * math.pi * freq * t)
                elif wave_type == 'square':
                    value = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
                elif wave_type == 'triangle':
                    value = 2 * abs(2 * (t * freq - int(t * freq))) - 1
                elif wave_type == 'sawtooth':
                    value = (t * freq - int(t * freq)) * 2 - 1

                # Envelope for smooth start/end
                envelope = 1.0
                if t < duration * 0.1:
                    envelope = t / (duration * 0.1)
                elif t > duration * 0.9:
                    envelope = 1.0 - (t - duration * 0.9) / (duration * 0.1)

                sample = int(value * max_sample * volume * envelope)
                buf[s][0] = numpy.int16(sample)
                buf[s][1] = numpy.int16(sample)

            sound = pygame.sndarray.make_sound(buf)
            sound.play()
        except Exception as e:
            print(f"Sound play skipped: {e}")

    def play_eat(self):
        self.play_tone(600, 0.1, 0.3, 'sine')
        pygame.time.delay(50)
        self.play_tone(900, 0.15, 0.2, 'sine')

    def play_move(self):
        self.play_tone(150, 0.05, 0.1, 'triangle')

    def play_death(self):
        self.play_tone(150, 0.4, 0.5, 'sawtooth')
        pygame.time.delay(100)
        self.play_tone(100, 0.4, 0.5, 'sawtooth')
        pygame.time.delay(100)
        self.play_tone(60, 0.6, 0.5, 'sawtooth')

    def play_start(self):
        self.play_tone(400, 0.1, 0.3, 'sine')
        pygame.time.delay(100)
        self.play_tone(600, 0.1, 0.3, 'sine')
        pygame.time.delay(100)
        self.play_tone(800, 0.3, 0.3, 'sine')

# --- Particle System ---
class Particle:
    def __init__(self, x, y, color, speed_mult=1):
        self.x = x
        self.y = y
        # Ensure color is a tuple of 3 integers (RGB)
        if isinstance(color, (list, tuple)):
            if len(color) >= 3:
                self.color = (
                    max(0, min(255, int(color[0]))),
                    max(0, min(255, int(color[1]))),
                    max(0, min(255, int(color[2])))
                )
            else:
                # Fallback color if not enough components
                self.color = (255, 255, 255)
        else:
            # Fallback color if color isn't iterable
            self.color = (255, 255, 255)
        self.size = random.randint(3, 6)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.04)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.95

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * self.life)))  # Ensure alpha is between 0-255
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        radius_int = max(1, int(self.size))  # Ensure radius is at least 1

        try:
            # Create color tuple with alpha
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), radius_int)
            surface.blit(s, (self.x - self.size, self.y - self.size))
        except ValueError as e:
            print(f"Color drawing error: {e}")
            # Final fallback - draw with white color
            color_with_alpha = (255, 255, 255, alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), radius_int)
            surface.blit(s, (self.x - self.size, self.y - self.size))

# --- Game Logic Classes ---
class GameConfig:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.theme_name = "neon"
        self.speed = 10
        self.current_theme = THEMES[self.theme_name]
        self.load_high_score()

    def load_high_score(self):
        if os.path.exists("snake_highscore.json"):
            with open("snake_highscore.json", "r") as f:
                data = json.load(f)
                self.high_score = data.get("highscore", 0)
        else:
            self.high_score = 0

    def save_high_score(self):
        with open("snake_highscore.json", "w") as f:
            json.dump({"highscore": self.high_score}, f)

class Snake:
    def __init__(self, config):
        self.config = config
        self.reset()

    def reset(self):
        self.x = (WIDTH // 2 // TILE_SIZE) * TILE_SIZE
        self.y = (HEIGHT // 2 // TILE_SIZE) * TILE_SIZE
        self.dx = TILE_SIZE
        self.dy = 0
        self.body = []
        self.length = 3
        self.dead = False
        self.grow_pending = 0
        for i in range(self.length):
            self.body.append((self.x - i * TILE_SIZE, self.y))

    def update(self, sound_mgr):
        if self.dead:
            return

        self.x += self.dx
        self.y += self.dy

        # Wall Collision
        if self.x < 0 or self.x >= WIDTH or self.y < 0 or self.y >= HEIGHT:
            self.dead = True
            sound_mgr.play_death()

        # Self Collision
        for segment in self.body[1:]:
            if self.x == segment[0] and self.y == segment[1]:
                self.dead = True
                sound_mgr.play_death()
                break

        self.body.insert(0, (self.x, self.y))

        if len(self.body) > self.length + self.grow_pending:
            self.body.pop()
            if random.random() < 0.3:
                sound_mgr.play_move()
        else:
            self.grow_pending -= 1

    def grow(self):
        self.length += 1
        self.config.score += 10
        if self.config.score > self.config.high_score:
            self.config.high_score = self.config.score
            self.config.save_high_score()

        if self.config.score > 0 and self.config.score % 50 == 0:
            self.config.level += 1
            self.config.speed = max(5, self.config.speed - 1)
            themes_list = list(THEMES.keys())
            self.config.theme_name = themes_list[self.config.level % len(themes_list)]
            self.config.current_theme = THEMES[self.config.theme_name]

    def draw(self, surface):
        for i, (bx, by) in enumerate(self.body):
            if i == 0:
                color = self.config.current_theme["snake_head"]
                glow_intensity = 60
            else:
                multiplier = 1 - (i / (len(self.body) + 5))
                color = (0, int(200 * multiplier), int(128 * multiplier))
                glow_intensity = 20

            if i % 2 == 0:
                glow_surf = pygame.Surface((TILE_SIZE + 10, TILE_SIZE + 10), pygame.SRCALPHA)
                alpha_val = int(glow_intensity * (1 - i / len(self.body)))
                pygame.draw.circle(glow_surf, (*color, alpha_val),
                                   (TILE_SIZE // 2 + 5, TILE_SIZE // 2 + 5), TILE_SIZE // 2 + 5)
                surface.blit(glow_surf, (bx - 5, by - 5), special_flags=pygame.BLEND_ADD)

            rect = pygame.Rect(bx + 1, by + 1, TILE_SIZE - 2, TILE_SIZE - 2)
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, (20, 20, 40), rect, width=1, border_radius=6)

            if i == 0:
                eye_color = (20, 20, 20)
                eye_size = 4
                offset_x, offset_y = TILE_SIZE // 3, TILE_SIZE // 3

                ex1, ey1 = bx + offset_x, by + offset_y
                if self.dx > 0:
                    ex1 += 5
                elif self.dx < 0:
                    ex1 -= 5
                elif self.dy > 0:
                    ey1 += 5
                elif self.dy < 0:
                    ey1 -= 5
                pygame.draw.circle(surface, eye_color, (ex1, ey1), eye_size)

                ex2, ey2 = bx + offset_x, by + offset_y
                if self.dx > 0:
                    ey2 += 5
                elif self.dx < 0:
                    ey2 -= 5
                elif self.dy > 0:
                    ex2 += 5
                elif self.dy < 0:
                    ex2 -= 5
                pygame.draw.circle(surface, eye_color, (ex2, ey2), eye_size)

class Food:
    def __init__(self, config):
        self.config = config
        self.x = 0
        self.y = 0
        self.pulse = 0

    def place(self, snake_body):
        valid_position = False
        while not valid_position:
            self.x = random.randint(1, TILE_COUNT - 2) * TILE_SIZE
            self.y = random.randint(1, TILE_COUNT - 2) * TILE_SIZE
            if (self.x, self.y) not in snake_body:
                valid_position = True

    def get_current_color(self):
        base = self.config.current_theme["food"]
        r = (base[0] + int(math.sin(self.pulse + self.config.level) * 30)) % 255
        g = (base[1] + int(math.cos(self.pulse) * 30)) % 255
        b = base[2] % 255
        return (int(r), int(g), int(b))

    def draw(self, surface):
        self.pulse += 0.1
        radius = (TILE_SIZE // 2) - 4
        pulse_size = math.sin(self.pulse) * 4

        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2

        food_color = self.get_current_color()

        # Draw glow effect
        glow_radius = radius + 10 + pulse_size
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*food_color, 70), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius), special_flags=pygame.BLEND_ADD)

        # Draw food
        pygame.draw.circle(surface, food_color, (center_x, center_y), radius)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 3, center_y - 3), radius // 3)

# --- Helper Functions ---
def draw_text(surface, text, size, x, y, color, center=True, bold=True):
    font = pygame.font.SysFont("Arial", size, bold=bold)
    shadow = font.render(text, True, (0, 0, 0))
    rect = shadow.get_rect(center=(x + 2, y + 2))
    surface.blit(shadow, rect)

    render = font.render(text, True, color)
    rect = render.get_rect(center=(x, y) if center else (x, y))
    surface.blit(render, rect)

def create_starfield(surface, num_stars=30):
    for _ in range(num_stars):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        alpha = random.randint(30, 100)
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (size // 2, size // 2), size)
        surface.blit(s, (x, y))

# --- Main Game Loop ---
TILE_SIZE = 25
TILE_COUNT = WIDTH // TILE_SIZE

def game_loop():
    # Initialize Config & Objects
    config = GameConfig()
    snake = Snake(config)
    food = Food(config)
    sound_mgr = SoundManager()
    particles = []

    state = "MENU"
    frame_count = 0
    screen_shake = 0

    food.place(snake.body)
    sound_mgr.play_start()

    while True:
        # Screen Shake Decay
        if screen_shake > 0:
            screen_shake *= 0.9
            if screen_shake < 0.5:
                screen_shake = 0

        # Update current theme reference
        config.current_theme = THEMES[config.theme_name]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if state == "MENU":
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    state = "PLAYING"
                    snake.reset()
                    particles = []
                    config.score = 0
                    config.level = 1
                    config.speed = 10
                    sound_mgr.play_start()

            elif state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and snake.dy == 0:
                        snake.dx, snake.dy = 0, -TILE_SIZE
                    elif event.key == pygame.K_DOWN and snake.dy == 0:
                        snake.dx, snake.dy = 0, TILE_SIZE
                    elif event.key == pygame.K_LEFT and snake.dx == 0:
                        snake.dx, snake.dy = -TILE_SIZE, 0
                    elif event.key == pygame.K_RIGHT and snake.dx == 0:
                        snake.dx, snake.dy = TILE_SIZE, 0
                    elif event.key == pygame.K_SPACE:
                        state = "PAUSED"
                        sound_mgr.play_move()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    state = "PAUSED"

            elif state == "PAUSED":
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    state = "PLAYING"
                    sound_mgr.play_move()

            elif state == "GAMEOVER":
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    state = "MENU"
                    sound_mgr.play_death()

        # Logic Update
        if state == "PLAYING":
            frame_count += 1

            if frame_count % config.speed == 0:
                snake.update(sound_mgr)

                if snake.x == food.x and snake.y == food.y:
                    snake.grow()
                    food.place(snake.body)

                    for _ in range(15):
                        particles.append(
                            Particle(food.x + TILE_SIZE // 2, food.y + TILE_SIZE // 2, food.get_current_color()))

                    sound_mgr.play_eat()

                particles = [p for p in particles if p.life > 0]
                for p in particles:
                    p.update()

                if snake.dead:
                    screen_shake = 20
                    state = "GAMEOVER"

        # --- Drawing ---
        shake_surface = pygame.Surface((WIDTH, HEIGHT))
        shake_x = random.randint(-int(screen_shake), int(screen_shake))
        shake_y = random.randint(-int(screen_shake), int(screen_shake))

        # Background
        shake_surface.fill(config.current_theme["bg"])
        create_starfield(shake_surface)

        # Grid
        grid_color = (30, 30, 50)
        for x in range(0, WIDTH, TILE_SIZE):
            pygame.draw.line(shake_surface, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, TILE_SIZE):
            pygame.draw.line(shake_surface, grid_color, (0, y), (WIDTH, y), 1)

        # Game Elements
        food.draw(shake_surface)
        snake.draw(shake_surface)

        for p in particles:
            p.draw(shake_surface)

        # UI Overlays
        if state == "MENU":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(config.current_theme["bg"])
            shake_surface.blit(overlay, (0, 0))

            draw_text(shake_surface, "NEON SNAKE", 60, WIDTH // 2, HEIGHT // 3, config.current_theme["snake"], bold=True)
            draw_text(shake_surface, "High Score: " + str(config.high_score), 30, WIDTH // 2, HEIGHT // 2 - 40,
                      config.current_theme["text"])
            draw_text(shake_surface, "Press SPACE or Click to Play", 24, WIDTH // 2, HEIGHT // 2 + 60,
                      config.current_theme["accent"], bold=False)
            draw_text(shake_surface, "Arrow Keys to Move", 18, WIDTH // 2, HEIGHT - 100, (150, 150, 150), bold=False)

        elif state == "PAUSED":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((20, 20, 40))
            shake_surface.blit(overlay, (0, 0))
            draw_text(shake_surface, "PAUSED", 60, WIDTH // 2, HEIGHT // 2, (255, 255, 255), bold=True)

        elif state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((50, 10, 10))
            shake_surface.blit(overlay, (0, 0))

            draw_text(shake_surface, "GAME OVER", 70, WIDTH // 2, HEIGHT // 3, (255, 80, 80), bold=True)
            draw_text(shake_surface, f"Score: {snake.config.score}", 40, WIDTH // 2, HEIGHT // 2 - 20, (255, 255, 255),
                      bold=True)
            draw_text(shake_surface, f"Level Reached: {snake.config.level}", 24, WIDTH // 2, HEIGHT // 2 + 30,
                      (200, 200, 200), bold=False)
            draw_text(shake_surface, "Press Any Key to Restart", 22, WIDTH // 2, HEIGHT // 2 + 100, (255, 200, 50),
                      bold=True)

        # HUD
        hud_color = config.current_theme["text"]
        draw_text(shake_surface, f"SCORE: {snake.config.score}", 20, WIDTH - 80, 20, hud_color, center=False)
        draw_text(shake_surface, f"LVL: {snake.config.level}", 20, 80, 20, hud_color, center=False)
        speed_label = "SLOW"
        if snake.config.speed < 8: speed_label = "FAST"
        if snake.config.speed < 6: speed_label = "INSANE"
        draw_text(shake_surface, speed_label, 16, WIDTH // 2, 20, config.current_theme["accent"], center=False)

        # Apply Shake and Blit to Main Window
        WIN.blit(shake_surface, (shake_x, shake_y))
        pygame.display.flip()
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    game_loop()
