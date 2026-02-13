# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Huihui-Qwen3-Coder-Next-abliterated.Q8_0.gguf

import pygame
import random
import math

# --- Configuration ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# --- Colors (Evolved Palette) ---
COLORS = {
    "bg_start": (20, 20, 30),  # Dark Blue-Black
    "bg_end": (40, 20, 50),  # Deep Purple (at max level)
    "grid": (40, 40, 55),
    "snake_head": (0, 255, 200),
    "snake_body": (0, 200, 150),
    "food": (255, 0, 128),
    "food_glow": (255, 50, 180),
    "text": (255, 255, 255),
    "shadow": (15, 15, 20),
}

# --- Global Game State Variables ---
game_level = 1
score_multiplier = 1.0
combo_timer = 30
screen_shake = 0

# Initialize Pygame
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neon Snake: Level Up")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, 1)
big_font = pygame.font.SysFont("Arial", 50, 1)


# --- Particle System ---
class Particle:
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.size = random.uniform(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.95

    def draw(self, surface):
        alpha = int(self.life * 255)
        color_with_alpha = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))


# --- Enhanced Snake Class ---
class Snake:
    def __init__(self):
        self.reset()
        self.score = 0
        self.high_score = self.load_high_score()

    def reset(self):
        self.body = [(10, 10), (10, 11), (10, 12)]
        self.direction = (0, -1)
        self.next_direction = (0, -1)
        self.grow_pending = False
        self.color_shift = 0

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def update(self):
        global combo_timer, score_multiplier, screen_shake

        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Wall Collision Check
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False

        # Self Collision Check
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

        # Reset combo timer on move
        combo_timer = 30
        return True

    def grow(self):
        global combo_timer, score_multiplier
        self.grow_pending = True
        # Boost multiplier if eating within combo window
        if combo_timer > 15:
            score_multiplier = min(score_multiplier + 0.25, 5.0)
            combo_timer = 30  # Reset combo window

    def draw(self, surface):
        for i, pos in enumerate(self.body):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE

            # Dynamic color based on position in body and game level
            base_color = COLORS["snake_body"]
            r_shift = (game_level * 5) % 50
            g_shift = (game_level * 2) % 50
            color = (base_color[0], max(0, base_color[1] - r_shift), max(0, base_color[2] - g_shift))

            if i == 0:  # Head
                head_surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
                head_surf.set_alpha(255)
                pygame.draw.rect(head_surf, COLORS["snake_head"], head_surf.get_rect(), border_radius=6)

                # Eyes
                eye_color = (20, 20, 30)
                ox, oy = self.direction
                offset = 5 if (ox, oy) in [(0, -1), (0, 1)] else 15

                pygame.draw.circle(head_surf, eye_color, (5 if ox <= 0 else 15, 5 if oy <= 0 else 15), 3)
                pygame.draw.circle(head_surf, eye_color, (5 if ox <= 0 else 15, 15 if oy >= 0 else 5), 3)

                surface.blit(head_surf, (x, y))

                # Head Glow
                glow_surf = pygame.Surface((GRID_SIZE * 2.5, GRID_SIZE * 2.5))
                glow_surf.set_alpha(60)

                # Get base head color
                base_head_color = COLORS["snake_head"]
                pulse = int(math.sin(pygame.time.get_ticks() / 200) * 20)

                # Create a clean RGB tuple for the glow
                # We ensure it's always 3 elements: (R, G, B)
                glow_color = (
                    base_head_color[0],
                    base_head_color[1] + pulse,  # Pulse green channel
                    base_head_color[2]
                )

                # Draw the circle
                pygame.draw.circle(glow_surf, glow_color, (GRID_SIZE, GRID_SIZE), GRID_SIZE)
                surface.blit(glow_surf, (x - GRID_SIZE / 2, y - GRID_SIZE / 2))


            else:  # Body
                alpha_offset = 255 - (i * 2)
                body_surf = pygame.Surface((GRID_SIZE - 2, GRID_SIZE - 2))
                body_surf.fill(color)
                body_surf.set_alpha(alpha_offset)
                pygame.draw.rect(body_surf, color, body_surf.get_rect(), border_radius=4)
                surface.blit(body_surf, (x + 1, y + 1))


# --- Enhanced Food Class ---
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.pulse = 0

    def spawn(self, snake_body):
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            if self.position not in snake_body:
                break

    def draw(self, surface):
        x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        y = self.position[1] * GRID_SIZE + GRID_SIZE // 2

        # Pulsing effect
        radius = (GRID_SIZE // 2) - 2
        pulse_size = int(math.sin(self.pulse) * 4)

        # Dynamic Glow
        glow_color = COLORS["food_glow"]
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Glow size increases with game level
        glow_radius = radius + 10 + pulse_size + (game_level * 2)
        pygame.draw.circle(glow_surf, (*glow_color, 40), (x, y), glow_radius)
        surface.blit(glow_surf, (0, 0))

        # Main Food Circle
        current_food_color = (
            COLORS["food"][0],
            COLORS["food"][1] + pulse_size * 5,
            COLORS["food"][2]
        )
        pygame.draw.circle(surface, current_food_color, (x, y), radius + pulse_size // 2)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), radius // 3)

        # "Star" sparkle if level is high
        if game_level > 3:
            pygame.draw.circle(surface, (255, 255, 0), (x - 3, y - 3), 2)

        self.pulse += 0.15


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, COLORS["grid"], (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, COLORS["grid"], (0, y), (SCREEN_WIDTH, y))


def get_background_color(level):
    # Interpolate color from Dark Blue to Deep Purple based on level
    t = min(level / 20, 1.0)  # 0 to 1 based on level
    r = int(COLORS["bg_start"][0] * (1 - t) + COLORS["bg_end"][0] * t)
    g = int(COLORS["bg_start"][1] * (1 - t) + COLORS["bg_end"][1] * t)
    b = int(COLORS["bg_start"][2] * (1 - t) + COLORS["bg_end"][2] * t)
    return (r, g, b)


def draw_ui(surface, snake):
    # --- Score Board (Top Left) ---
    score_text = font.render(f"Score: {snake.score}", True, COLORS["text"])
    high_score_text = font.render(f"Best: {snake.high_score}", True, COLORS["text"])

    surface.blit(score_text, (10, 10))
    surface.blit(high_score_text, (10, 45))

    # --- Level & Multiplier (Below Score) ---
    level_text = font.render(f"Level: {game_level}", True, (200, 200, 255))
    mult_text = font.render(f"Combo x{score_multiplier:.1f}", True, (255, 215, 0))

    surface.blit(level_text, (10, 80))
    surface.blit(mult_text, (10, 110))

    # --- Combo Bar (Visual "Engine" for points) ---
    bar_x = 10
    bar_y = 145
    bar_width = 200  # Made wider so it's easier to see
    bar_height = 12

    # Draw Background Track
    pygame.draw.rect(surface, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=6)

    # Calculate Fill
    # Timer resets to 30 every move, decays over time if not eating
    fill_width = int((combo_timer / 30) * bar_width)

    # Color Logic: Green (Great), Yellow (Good), Orange (Decaying)
    if combo_timer > 22:
        combo_color = (0, 255, 100)  # Bright Green
    elif combo_timer > 15:
        combo_color = (255, 215, 0)  # Gold
    else:
        combo_color = (255, 140, 0)  # Orange

    # Draw Active Combo Bar
    pygame.draw.rect(surface, combo_color, (bar_x, bar_y, fill_width, bar_height), border_radius=6)

    # Draw Text Label for Combo Bar
    combo_label = font.render("COMBO ENGINE", True, (180, 180, 200))
    surface.blit(combo_label, (bar_x, bar_y - 15))

    # --- Instructions (Top Right) ---
    inst_text = font.render("Press SPACE to Pause", True, (200, 200, 200))
    inst_x = SCREEN_WIDTH - inst_text.get_width() - 10
    surface.blit(inst_text, (inst_x, 10))


def draw_game_over(surface, snake):
    global game_level, score_multiplier

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    # Dynamic Game Over Text
    title_color = COLORS["food"]
    title = big_font.render("GAME OVER", True, title_color)

    # Level reached text
    level_reached_text = font.render(f"You reached Level {game_level}!", True, COLORS["text"])
    score_text = font.render(f"Final Score: {snake.score}", True, COLORS["text"])
    subtitle = font.render("Press ENTER to Restart", True, COLORS["text"])

    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
    surface.blit(level_reached_text, (SCREEN_WIDTH // 2 - level_reached_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 + 60))


def draw_pause(surface):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(120)
    overlay.fill((20, 20, 30))
    surface.blit(overlay, (0, 0))

    pause_text = big_font.render("PAUSED", True, COLORS["text"])
    surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))


# --- Main Game Loop ---
def main():
    global game_level, score_multiplier, combo_timer, screen_shake

    snake = Snake()
    food = Food()
    particles = []
    food.spawn(snake.body)

    running = True
    game_active = True
    paused = False
    game_speed = 10

    while running:
        # Screen Shake Logic
        shake_offset_x = 0
        shake_offset_y = 0
        if screen_shake > 0:
            shake_intensity = screen_shake * 2
            shake_offset_x = random.randint(-shake_intensity, shake_intensity)
            shake_offset_y = random.randint(-shake_intensity, shake_intensity)
            screen_shake *= 0.9  # Decay shake
            if screen_shake < 0.5:
                screen_shake = 0

        clock.tick(game_speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_active and event.key == pygame.K_RETURN:
                    # Reset Global Variables
                    game_level = 1
                    score_multiplier = 1.0
                    combo_timer = 30
                    screen_shake = 0
                    snake.reset()
                    food.spawn(snake.body)
                    particles = []
                    snake.score = 0
                    game_active = True
                    paused = False
                    game_speed = 10

                elif event.key == pygame.K_SPACE and game_active:
                    paused = not paused

                if game_active and not paused:
                    if event.key == pygame.K_UP and snake.direction != (0, 1):
                        snake.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                        snake.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                        snake.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                        snake.next_direction = (1, 0)

        if game_active and not paused:
            if snake.update():
                head = snake.body[0]
                if head == food.position:
                    base_points = 10
                    bonus_points = int(base_points * score_multiplier)
                    snake.score += bonus_points

                    if snake.score > snake.high_score:
                        snake.high_score = snake.score

                    snake.grow()

                    # Spawn Particles with more energy at higher levels
                    px = head[0] * GRID_SIZE + GRID_SIZE // 2
                    py = head[1] * GRID_SIZE + GRID_SIZE // 2
                    particle_count = 15 + (game_level * 2)
                    for _ in range(particle_count):
                        particles.append(Particle(px, py, COLORS["food"], speed_mult=1 + (game_level / 10)))

                    # Screen Shake on Eat
                    screen_shake = 5 + game_level

                    # Level Up Logic
                    if snake.score > game_level * 100:
                        game_level += 1
                        game_speed += 0.5  # Speed up slightly
                        screen_shake += 3  # Big shake on level up

                    food.spawn(snake.body)
            else:
                screen_shake = 15  # Big shake on Death
                game_active = False

        # Update Particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # --- Drawing ---
        # Apply Screen Shake to the whole screen context
        screen.fill(get_background_color(game_level))

        # Create a temporary surface to draw everything on, then shake it
        temp_surface = screen.copy()

        draw_grid(temp_surface)
        food.draw(temp_surface)
        snake.draw(temp_surface)

        # Draw Particles
        for p in particles:
            p.draw(temp_surface)

        draw_ui(temp_surface, snake)

        if paused:
            draw_pause(temp_surface)

        if not game_active:
            draw_game_over(temp_surface, snake)

        # Apply Shake by copying temp surface to main screen with offset
        screen.blit(temp_surface, (shake_offset_x, shake_offset_y))

        pygame.display.flip()

    snake.save_high_score()
    pygame.quit()


if __name__ == "__main__":
    main()
