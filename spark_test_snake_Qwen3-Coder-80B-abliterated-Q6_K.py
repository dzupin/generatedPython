# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Qwen3-Coder-80B-abliterated-Q6_K.gguf


import pygame
import random
import math

# --- INITIALIZATION ---
pygame.init()
pygame.font.init()
pygame.display.set_caption("Neon Snake")

# --- CONFIGURATION ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
TILE_SIZE = 20
TILE_COUNT_X = SCREEN_WIDTH // TILE_SIZE
TILE_COUNT_Y = SCREEN_HEIGHT // TILE_SIZE
FPS = 15

# Colors (Dark Background for Neon effect)
BG_COLOR = pygame.Color(15, 15, 20)
GRID_COLOR = pygame.Color(25, 25, 35)
SNAKE_HEAD_COLOR = pygame.Color(0, 255, 128)
SNAKE_BODY_COLOR = pygame.Color(0, 200, 100)
FOOD_COLOR = pygame.Color(255, 50, 100)
TEXT_COLOR = pygame.Color(255, 255, 255)

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

# --- GAME STATE VARIABLES ---
score = 0
high_score = 0
particles = []  # For explosion effects


# --- CLASSES & FUNCTIONS ---

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(10, 10), (10, 11), (10, 12)]
        self.direction = (0, -1)  # Moving Up
        self.next_direction = (0, -1)
        self.grow_pending = False

    def update(self):
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % TILE_COUNT_X, (head_y + dir_y) % TILE_COUNT_Y)

        # Check Collision (Self or Wall - though wall is wrapped here)
        if new_head in self.body[1:]:
            return False  # Game Over

        self.body.insert(0, new_head)

        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

        return True

    def grow(self):
        self.grow_pending = True

    def draw(self):
        # Draw Body
        for i, segment in enumerate(self.body):
            x = segment[0] * TILE_SIZE
            y = segment[1] * TILE_SIZE

            # Head is different color
            if i == 0:
                color = SNAKE_HEAD_COLOR
                # Draw Eyes on Head
                pygame.draw.circle(screen, (0, 0, 0), (x + 6, y + 6), 3)
                pygame.draw.circle(screen, (0, 0, 0), (x + 14, y + 6), 3)
            else:
                color = SNAKE_BODY_COLOR

            # Draw rounded rectangle for style
            rect = pygame.Rect(x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2)
            pygame.draw.rect(screen, color, rect, border_radius=6)

    def change_direction(self, direction):
        # Prevent reversing
        opposite = (-self.direction[0], -self.direction[1])
        if direction != opposite:
            self.next_direction = direction


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        if snake_body is None:
            snake_body = []

        while True:
            x = random.randint(0, TILE_COUNT_X - 1)
            y = random.randint(0, TILE_COUNT_Y - 1)
            if (x, y) not in snake_body:
                self.position = (x, y)
                break

    def draw(self):
        x = self.position[0] * TILE_SIZE
        y = self.position[1] * TILE_SIZE

        # Pulsing effect for food
        pulse = math.sin(pygame.time.get_ticks() / 200) * 3

        radius = (TILE_SIZE // 2) - 4 + pulse

        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2

        # Glow effect
        pygame.draw.circle(screen, (FOOD_COLOR.r, FOOD_COLOR.g, FOOD_COLOR.b, 60),
                           (center_x, center_y), radius + 5)

        # Main Fruit
        pygame.draw.circle(screen, FOOD_COLOR, (center_x, center_y), max(4, radius))

        # Shine
        pygame.draw.circle(screen, (255, 255, 255, 150), (center_x - 3, center_y - 3), 3)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        # Ensure color is a tuple of integers (R, G, B)
        # This handles both (r, g, b) tuples and pygame.Color objects
        if isinstance(color, pygame.Color):
            self.color = (color.r, color.g, color.b)
        else:
            self.color = color

        self.size = random.randint(3, 6)
        speed = random.uniform(2, 6)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0  # Opacity/Life
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.95

    def draw(self, surface):
        alpha = int(self.life * 255)

        # Create a surface with per-pixel alpha
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # --- HERE IS THE FIX FOR THE ERROR ---
        # We create a color tuple: (R, G, B, Alpha)
        current_color = (*self.color, alpha)

        # Draw the circle.
        # Note: We pass 'current_color' as a single argument (unpacking it with *)
        pygame.draw.circle(s, current_color, (self.size // 2, self.size // 2), self.size // 2)

        surface.blit(s, (self.x, self.y))

def create_explosion(x, y, color):
    for _ in range(15):
        particles.append(Particle(x, y, color))


def draw_grid():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_ui(score, high_score):
    # Score Board
    score_text = font_small.render(f"Score: {score}", True, TEXT_COLOR)
    high_score_text = font_small.render(f"Best: {high_score}", True, TEXT_COLOR)

    screen.blit(score_text, (20, 20))
    screen.blit(high_score_text, (SCREEN_WIDTH - 130, 20))


def draw_center_message(title, subtitle, color=TEXT_COLOR):
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BG_COLOR)
    screen.blit(overlay, (0, 0))

    # Title
    title_surf = font_large.render(title, True, color)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title_surf, title_rect)

    # Subtitle
    sub_surf = font_small.render(subtitle, True, (200, 200, 200))
    sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(sub_surf, sub_rect)

    # Instructions
    inst_surf = font_small.render("Press SPACE to Start", True, (150, 150, 150))
    inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
    screen.blit(inst_surf, inst_rect)


# --- MAIN GAME LOOP ---
def main():
    global score, high_score, particles

    snake = Snake()
    food = Food()

    game_state = "START"  # START, PLAYING, GAMEOVER
    game_speed = FPS

    running = True
    while running:
        # Input Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == "START":
                    if event.key == pygame.K_SPACE:
                        snake.reset()
                        score = 0
                        game_state = "PLAYING"

                elif game_state == "PLAYING":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        snake.change_direction((1, 0))
                    elif event.key == pygame.K_p:
                        game_state = "PAUSED"

                elif game_state == "PAUSED":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_p:
                        game_state = "PLAYING"

                elif game_state == "GAMEOVER":
                    if event.key == pygame.K_SPACE:
                        game_state = "START"

        # Update Logic
        if game_state == "PLAYING":
            if not snake.update():
                game_state = "GAMEOVER"
                if score > high_score:
                    high_score = score

            # Check Food Collision
            if snake.body[0] == food.position:
                score += 10
                snake.grow()
                food.spawn(snake.body)

                # Create Explosion
                fx_x = snake.body[0][0] * TILE_SIZE + TILE_SIZE // 2
                fx_y = snake.body[0][1] * TILE_SIZE + TILE_SIZE // 2
                create_explosion(fx_x, fx_y, FOOD_COLOR)

            # Update Particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

        # Drawing
        screen.fill(BG_COLOR)
        draw_grid()

        food.draw()

        # Draw Particles behind snake
        for p in particles:
            p.draw(screen)

        snake.draw()
        draw_ui(score, high_score)

        # State Specific Overlays
        if game_state == "START":
            draw_center_message("Neon Snake", "Use Arrow Keys or WASD to move", SNAKE_HEAD_COLOR)

        elif game_state == "PAUSED":
            draw_center_message("Paused", "Press P or SPACE to Resume", (255, 200, 50))

        elif game_state == "GAMEOVER":
            draw_center_message("Game Over", f"Final Score: {score}", (255, 75, 75))

        pygame.display.flip()
        clock.tick(game_speed)

    pygame.quit()


if __name__ == "__main__":
    main()
