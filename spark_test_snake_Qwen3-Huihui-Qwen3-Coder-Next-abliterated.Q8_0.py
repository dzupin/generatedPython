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
GRID_SIZE = 20  # Size of one square
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors (Neon Palette)
COLORS = {
    "bg": (20, 20, 30),  # Dark Blue-Black Background
    "grid": (40, 40, 55),  # Subtle Grid Lines
    "snake_head": (0, 255, 200),  # Cyan
    "snake_body": (0, 200, 150),  # Teal
    "food": (255, 0, 128),  # Neon Pink
    "food_glow": (255, 50, 180),
    "text": (255, 255, 255),
    "shadow": (15, 15, 20)
}

# Initialize Pygame
pygame.init()
# Use '1' for bold in Pygame 2.x
BOLD = 1
font = pygame.font.SysFont("Arial", 24, BOLD)
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neon Snake")
clock = pygame.time.Clock()



# --- Particle System for Visual Flair ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0  # Opacity/Life
        self.decay = random.uniform(0.02, 0.05)
        self.size = random.uniform(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.95  # Shrink over time

    def draw(self, surface):
        alpha = int(self.life * 255)
        color_with_alpha = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))


# --- Game Logic ---

class Snake:
    def __init__(self):
        self.reset()
        self.score = 0
        self.high_score = self.load_high_score()

    def reset(self):
        self.body = [(10, 10), (10, 11), (10, 12)]
        self.direction = (0, -1)  # Moving Up
        self.next_direction = (0, -1)
        self.grow_pending = False

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
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Check Wall Collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False

        # Check Self Collision
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

        return True

    def grow(self):
        self.grow_pending = True

    def draw(self, surface):
        for i, pos in enumerate(self.body):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE

            # Determine color
            if i == 0:
                color = COLORS["snake_head"]
                # Add a "face" to the head
                head_surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
                head_surf.set_alpha(255)
                pygame.draw.rect(head_surf, color, head_surf.get_rect(), border_radius=5)

                # Draw Eyes
                eye_color = (20, 20, 30)
                ox, oy = self.direction
                # Offset eyes based on direction
                if (ox, oy) == (0, -1):  # Up
                    pygame.draw.circle(head_surf, eye_color, (5, 5), 3)
                    pygame.draw.circle(head_surf, eye_color, (15, 5), 3)
                elif (ox, oy) == (0, 1):  # Down
                    pygame.draw.circle(head_surf, eye_color, (5, 15), 3)
                    pygame.draw.circle(head_surf, eye_color, (15, 15), 3)
                elif (ox, oy) == (1, 0):  # Right
                    pygame.draw.circle(head_surf, eye_color, (15, 5), 3)
                    pygame.draw.circle(head_surf, eye_color, (15, 15), 3)
                else:  # Left
                    pygame.draw.circle(head_surf, eye_color, (5, 5), 3)
                    pygame.draw.circle(head_surf, eye_color, (5, 15), 3)

                surface.blit(head_surf, (x, y))
                # Glow for head
                glow_surf = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2))
                glow_surf.set_alpha(50)
                pygame.draw.circle(glow_surf, COLORS["snake_head"], (GRID_SIZE, GRID_SIZE), GRID_SIZE)
                surface.blit(glow_surf, (x - GRID_SIZE / 2, y - GRID_SIZE / 2))

            else:
                # Gradient effect for body
                alpha_offset = 255 - (i * 3)
                if alpha_offset < 100: alpha_offset = 100

                body_surf = pygame.Surface((GRID_SIZE - 2, GRID_SIZE - 2))
                body_surf.fill(COLORS["snake_body"])
                body_surf.set_alpha(alpha_offset)

                # Rounded corners for body segments
                pygame.draw.rect(body_surf, COLORS["snake_body"], body_surf.get_rect(), border_radius=4)
                surface.blit(body_surf, (x + 1, y + 1))


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
        pulse_size = int(math.sin(self.pulse) * 3)

        # Glow Ring
        glow_color = COLORS["food_glow"]
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, 30), (x, y), radius + 10 + pulse_size)
        surface.blit(glow_surf, (0, 0))

        # Main Food Circle
        pygame.draw.circle(surface, COLORS["food"], (x, y), radius + pulse_size // 2)

        # Inner White Dot
        pygame.draw.circle(surface, (255, 255, 255), (x, y), radius // 3)

        self.pulse += 0.1


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, COLORS["grid"], (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, COLORS["grid"], (0, y), (SCREEN_WIDTH, y))


def draw_ui(surface, snake):
    # Score Board
    score_text = font.render(f"Score: {snake.score}", True, COLORS["text"])
    high_score_text = font.render(f"High Score: {snake.high_score}", True, COLORS["text"])

    surface.blit(score_text, (10, 10))
    surface.blit(high_score_text, (10, 45))

    # Instructions
    inst_text = font.render("Press SPACE to Pause", True, (200, 200, 200))
    # Calculate the x position so the text ends exactly at the right edge
    inst_x = SCREEN_WIDTH - inst_text.get_width() - 10
    surface.blit(inst_text, (inst_x, 10))


def draw_game_over(surface):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    title = pygame.font.SysFont("Arial", 60, 1).render("GAME OVER", True, (255, 0, 50))
    subtitle = pygame.font.SysFont("Arial", 30).render("Press ENTER to Restart", True, COLORS["text"])

    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 + 20))


def draw_pause(surface):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(100)
    overlay.fill((20, 20, 30))
    surface.blit(overlay, (0, 0))

    pause_text = pygame.font.SysFont("Arial", 50, 1).render("PAUSED", True, COLORS["text"])
    surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))


# --- Main Game Loop ---

def main():
    snake = Snake()
    food = Food()
    particles = []
    food.spawn(snake.body)

    running = True
    game_active = True
    paused = False
    game_speed = 10

    # Start music (optional, using simple beeps if no file)
    # pygame.mixer.init()
    # pygame.mixer.music.load("bg_music.mp3") ...

    while running:
        clock.tick(game_speed)

        # Input Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_active and event.key == pygame.K_RETURN:
                    # Restart Game
                    snake.reset()
                    food.spawn(snake.body)
                    particles = []
                    snake.score = 0
                    game_active = True
                    paused = False
                    game_speed = 10

                elif event.key == pygame.K_SPACE and game_active:
                    # Toggle Pause
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
            # Update Snake
            if snake.update():
                # Check Food Collision
                head = snake.body[0]
                if head == food.position:
                    snake.score += 10
                    if snake.score > snake.high_score:
                        snake.high_score = snake.score
                    snake.grow()

                    # Spawn Particles
                    px = head[0] * GRID_SIZE + GRID_SIZE // 2
                    py = head[1] * GRID_SIZE + GRID_SIZE // 2
                    for _ in range(15):
                        particles.append(Particle(px, py, COLORS["food"]))

                    food.spawn(snake.body)

                    # Speed up slightly every 50 points
                    if snake.score % 50 == 0:
                        game_speed += 1
            else:
                game_active = False

        # Update Particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # --- Drawing ---
        screen.fill(COLORS["bg"])

        draw_grid(screen)

        food.draw(screen)
        snake.draw(screen)

        # Draw Particles
        for p in particles:
            p.draw(screen)

        draw_ui(screen, snake)

        if paused:
            draw_pause(screen)

        if not game_active:
            draw_game_over(screen)

        pygame.display.flip()

    snake.save_high_score()
    pygame.quit()


if __name__ == "__main__":
    main()

