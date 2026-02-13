# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Huihui-Qwen3-Coder-80B-abliterated-Q6_K.gguf

import pygame
import random
import math

# --- INITIALIZATION ---
pygame.init()
pygame.font.init()
pygame.display.set_caption("Neon Snake Pro")

# --- CONFIGURATION ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
TILE_SIZE = 20
TILE_COUNT_X = SCREEN_WIDTH // TILE_SIZE
TILE_COUNT_Y = SCREEN_HEIGHT // TILE_SIZE
BASE_FPS = 15

# Themes Configuration
THEMES = {
    "Classic": {
        "bg": (15, 15, 20),
        "grid": (25, 25, 35),
        "head": (0, 255, 128),
        "body": (0, 200, 100),
        "food": (255, 50, 100),
        "text": (255, 255, 255)
    },
    "Cyber": {
        "bg": (10, 10, 25),
        "grid": (20, 20, 40),
        "head": (255, 0, 255),
        "body": (150, 0, 255),
        "food": (0, 255, 255),
        "text": (255, 255, 200)
    },
    "Sunset": {
        "bg": (30, 10, 10),
        "grid": (50, 20, 20),
        "head": (255, 200, 50),
        "body": (255, 100, 0),
        "food": (200, 50, 255),
        "text": (255, 230, 200)
    }
}

# --- GLOBAL STATE VARIABLES ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Initialize Global Variables
score = 0
high_score = 0
level = 1
combo = 0
combo_timer = 0
shake_intensity = 0
particles = []
current_theme_name = "Classic"
theme_colors = THEMES["Classic"]


# --- CLASSES ---

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(10, 10), (10, 11), (10, 12)]
        self.direction = (0, -1)
        self.next_direction = (0, -1)
        self.grow_pending = False

    def update(self, current_speed):
        self.direction = self.next_direction

        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % TILE_COUNT_X, (head_y + dir_y) % TILE_COUNT_Y)

        # Self Collision
        if new_head in self.body[1:]:
            return False

        self.body.insert(0, new_head)

        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

        return True

    def grow(self):
        self.grow_pending = True

    def change_direction(self, direction):
        opposite = (-self.direction[0], -self.direction[1])
        if direction != opposite:
            self.next_direction = direction

    def draw(self):
        for i, segment in enumerate(self.body):
            x = segment[0] * TILE_SIZE
            y = segment[1] * TILE_SIZE

            color = theme_colors["head"] if i == 0 else theme_colors["body"]

            # Draw Glow Effect
            glow_size = TILE_SIZE + (4 if i == 0 else 2)
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, 50), (glow_size // 2, glow_size // 2), glow_size // 2)
            screen.blit(glow_surface, (x - 2, y - 2))

            # Draw Body Segment
            rect = pygame.Rect(x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2)
            pygame.draw.rect(screen, color, rect, border_radius=6)

            # Eyes for Head
            if i == 0:
                pygame.draw.circle(screen, (0, 0, 0), (x + 6, y + 6), 3)
                pygame.draw.circle(screen, (0, 0, 0), (x + 14, y + 6), 3)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = "normal"
        self.spawn()

    def spawn(self, snake_body=None):
        if snake_body is None:
            snake_body = []
        while True:
            x = random.randint(0, TILE_COUNT_X - 1)
            y = random.randint(0, TILE_COUNT_Y - 1)
            if (x, y) not in snake_body:
                self.position = (x, y)

                # Determine Food Type based on Random Chance and Score
                chance = random.random()
                if score > 50 and chance > 0.80:
                    self.type = "gold"
                elif score > 100 and chance < 0.15:
                    self.type = "bitter"
                else:
                    self.type = "normal"
                break

    def draw(self):
        x = self.position[0] * TILE_SIZE
        y = self.position[1] * TILE_SIZE

        if self.type == "gold":
            color = (255, 215, 0)  # Gold
            radius_mult = 1.5
            label = "!"
        elif self.type == "bitter":
            color = (100, 100, 110)  # Dark Grey
            radius_mult = 0.8
            label = "X"
        else:
            color = theme_colors["food"]
            radius_mult = 1.0
            label = ""

        pulse = math.sin(pygame.time.get_ticks() / 150) * 4
        radius = (TILE_SIZE // 2) - 4 + pulse

        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2

        # Draw Glow
        pygame.draw.circle(screen, (*color, 40), (center_x, center_y), radius * radius_mult + 6)

        # Main Fruit
        pygame.draw.circle(screen, color, (center_x, center_y), max(4, radius * radius_mult))

        # Type Icon
        if self.type != "normal":
            icon_surf = font_small.render(label, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(center=(center_x, center_y))
            screen.blit(icon_surf, icon_rect)


class Particle:
    def __init__(self, x, y, color, p_type="normal"):
        self.x = x
        self.y = y
        if isinstance(color, pygame.Color):
            self.color = (color.r, color.g, color.b)
        else:
            self.color = color
        self.size = random.randint(3, 6) if p_type != "gold" else 8
        speed = random.uniform(2, 6)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.type = p_type

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.95

    def draw(self, surface):
        alpha = int(self.life * 255)
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        if self.type == "spark":
            pygame.draw.circle(s, (*self.color, alpha), (self.size // 2, self.size // 2), self.size // 2)
        else:
            pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.size, self.size))

        surface.blit(s, (self.x, self.y))


# --- UTILITY FUNCTIONS ---

def get_theme():
    if score >= 150:
        return "Sunset"
    elif score >= 50:
        return "Cyber"
    return "Classic"


def create_explosion(x, y, color, count=15, p_type="normal"):
    for _ in range(count):
        particles.append(Particle(x, y, color, p_type))


def draw_grid():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, theme_colors["grid"], (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, theme_colors["grid"], (0, y), (SCREEN_WIDTH, y), 1)


def draw_ui():
    combo_bonus = f"x{combo}" if combo > 1 else ""
    score_text = font_small.render(f"Score: {score}", True, theme_colors["text"])
    high_score_text = font_small.render(f"Best: {high_score}", True, theme_colors["text"])
    level_text = font_small.render(f"Level: {level}", True, theme_colors["text"])
    combo_text = font_large.render(combo_bonus, True, (255, 215, 0))

    screen.blit(score_text, (20, 20))
    screen.blit(level_text, (20, 50))
    screen.blit(high_score_text, (SCREEN_WIDTH - 140, 20))

    if combo > 1:
        screen.blit(combo_text, (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20))


def draw_center_message(title, subtitle, color=None):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    color = color if color else theme_colors["head"]
    title_surf = font_large.render(title, True, color)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title_surf, title_rect)

    sub_surf = font_small.render(subtitle, True, (200, 200, 200))
    sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(sub_surf, sub_rect)

    inst_surf = font_small.render("Press SPACE to Start", True, (150, 150, 150))
    inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
    screen.blit(inst_surf, inst_rect)


# --- MAIN GAME LOOP ---
def main():
    global score, high_score, level, combo, combo_timer, shake_intensity, current_theme_name, theme_colors

    snake = Snake()
    food = Food()
    game_state = "START"

    current_theme_name = "Classic"
    theme_colors = THEMES[current_theme_name]
    base_speed = BASE_FPS

    running = True
    while running:
        # --- 1. Initialize Variables (Fixes UnboundLocalError) ---
        current_speed = base_speed + (score // 50)

        # --- 2. Input Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == "START":
                    if event.key == pygame.K_SPACE:
                        snake.reset()
                        score = 0
                        combo = 0
                        level = 1
                        shake_intensity = 0
                        game_state = "PLAYING"

                elif game_state == "PLAYING":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if snake.direction != (0, 1): snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if snake.direction != (0, -1): snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if snake.direction != (1, 0): snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if snake.direction != (-1, 0): snake.change_direction((1, 0))
                    elif event.key == pygame.K_p:
                        game_state = "PAUSED"

                elif game_state == "PAUSED":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_p:
                        game_state = "PLAYING"

                elif game_state == "GAMEOVER":
                    if event.key == pygame.K_SPACE:
                        game_state = "START"

        # --- 3. Update Logic ---
        if game_state == "PLAYING":
            if not snake.update(current_speed):
                game_state = "GAMEOVER"
                shake_intensity = 15
                if score > high_score:
                    high_score = score

            # Combo Logic
            if combo > 0:
                combo_timer -= 1
                if combo_timer <= 0:
                    combo = max(0, combo - 1)
                    combo_timer = 60

            # Check Food Collision
            if snake.body[0] == food.position:
                points = 10
                growth = 1
                food_color = theme_colors["food"]

                if food.type == "gold":
                    points = 30
                    growth = 3
                    combo += 2
                    combo_timer = 90
                    food_color = (255, 215, 0)
                    create_explosion(snake.body[0][0] * TILE_SIZE, snake.body[0][1] * TILE_SIZE, food_color, 25, "gold")
                    shake_intensity = 10
                elif food.type == "bitter":
                    points = -5
                    growth = 5
                    combo = max(0, combo - 1)
                    food_color = (100, 100, 100)
                    create_explosion(snake.body[0][0] * TILE_SIZE, snake.body[0][1] * TILE_SIZE, food_color, 15,
                                     "bitter")
                    shake_intensity = 5
                else:
                    if combo > 0:
                        points += (combo * 5)
                    create_explosion(snake.body[0][0] * TILE_SIZE, snake.body[0][1] * TILE_SIZE, food_color)

                score += points
                if score < 0: score = 0

                # Level Up Logic
                new_level = (score // 50) + 1
                if new_level > level:
                    level = new_level
                    shake_intensity += 5
                    # Level Up Flash
                    flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    flash_surf.fill((255, 255, 255))
                    flash_surf.set_alpha(100)
                    screen.blit(flash_surf, (0, 0))

                current_theme_name = get_theme()
                theme_colors = THEMES[current_theme_name]

                for _ in range(growth):
                    snake.grow()

                food.spawn(snake.body)

        # Update Particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # --- 4. Drawing ---

        # Screen Shake Calculation
        shake_x = random.randint(-int(shake_intensity), int(shake_intensity)) if shake_intensity > 0 else 0
        shake_y = random.randint(-int(shake_intensity), int(shake_intensity)) if shake_intensity > 0 else 0

        screen.fill(theme_colors["bg"])
        screen.blit(screen, (shake_x, shake_y))

        # Redraw content on top of shake
        screen.fill(theme_colors["bg"])
        draw_grid()

        food.draw()

        for p in particles:
            p.draw(screen)

        snake.draw()
        draw_ui()

        if game_state == "START":
            draw_center_message("Neon Snake Pro", "Eat food. Build combos. Survive.", theme_colors["head"])

        elif game_state == "PAUSED":
            draw_center_message("Paused", "Press P or SPACE to Resume", theme_colors["head"])

        elif game_state == "GAMEOVER":
            draw_center_message("Game Over", f"Final Score: {score}", (255, 75, 75))

        # Decay Shake
        if shake_intensity > 0:
            shake_intensity = int(shake_intensity * 0.9)

        pygame.display.flip()
        clock.tick(current_speed)

    pygame.quit()


# Initialize Fonts
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

if __name__ == "__main__":
    main()
