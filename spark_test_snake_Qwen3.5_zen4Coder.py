# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 4-shot  (but very good in fixing bugs)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 163000 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/zen4-coder.i1-Q6_K.gguf

import pygame
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BG_COLOR = (15, 15, 20)
GRID_LINE_COLOR = (25, 25, 30)
SNAKE_HEAD_COLOR = (0, 255, 170)  # Neon Teal
SNAKE_BODY_COLOR = (0, 200, 140)
FOOD_COLOR = (255, 80, 80)  # Neon Pink/Red
TEXT_COLOR = (255, 255, 255)
GLOW_COLOR = (0, 255, 170)

# Game Settings
FPS = 12
INITIAL_LENGTH = 3


# --- CLASSES ---

class Particle:
    """Explosion effect for when snake eats food"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        # Random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        self.life = 1.0  # Opacity/Life (1.0 to 0.0)
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= self.decay
        self.size *= 0.96  # Shrink over time

    def draw(self, surface):
        # Ensure color is always a valid tuple (R, G, B)
        if isinstance(self.color, tuple):
            r, g, b = self.color[:3]
        else:
            r, g, b = self.color, self.color, self.color

        alpha = int(255 * max(0, self.life))
        final_color = (r, g, b, alpha)

        pygame.draw.circle(surface, final_color, (int(self.x), int(self.y)), max(1, self.size))


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.pulse = 0
        self.locked = False

    def spawn(self, snake_body):
        should_move = not self.locked

        if self.locked:
            if self.position in snake_body:
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

    def draw(self, surface):
        x, y = self.position
        self.pulse += 0.15

        radius = GRID_SIZE // 2 - 2 + math.sin(self.pulse) * 4

        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        base_alpha = 40
        pulse_alpha = int(math.sin(self.pulse) * 20)
        pygame.draw.circle(glow_surf, (*FOOD_COLOR, base_alpha + pulse_alpha), (center_x, center_y), radius * 2.5)
        surface.blit(glow_surf, (0, 0))

        pygame.draw.circle(surface, FOOD_COLOR, (center_x, center_y), radius)
        highlight_color = (255, 200, 200)
        pygame.draw.circle(surface, highlight_color, (center_x - 3, center_y - 3), radius // 3)


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

    def change_direction(self, direction):
        current_dir = self.direction
        if direction[0] + current_dir[0] != 0 or direction[1] + current_dir[1] != 0:
            self.direction = direction

    def update(self, food):
        if self.dead:
            return True

        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction

        new_head = (head_x + dir_x, head_y + dir_y)

        # 1. Check Wall Collisions
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.dead = True
            return False

        # 2. Check Self Collisions
        if new_head in self.body[:-1]:
            self.dead = True
            return False

        self.body.insert(0, new_head)

        # 3. Check if ate food
        if new_head == food.position:
            self.score += 10
            self.grow_pending += 1

            # Unlock food so it can move to a new spot
            food.locked = False
            food.spawn(self.body)
            return True

        # 4. Handle Growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return True

    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            if i == 0:
                color = SNAKE_HEAD_COLOR
                size = GRID_SIZE + 2
                offset = -1
            else:
                factor = i * 0.05
                color = (
                    int(SNAKE_BODY_COLOR[0] * (1 - factor)),
                    int(SNAKE_BODY_COLOR[1] * (1 - factor)),
                    int(SNAKE_BODY_COLOR[2] * (1 - factor))
                )
                size = GRID_SIZE
                offset = 0

            rect = pygame.Rect(x * GRID_SIZE + offset, y * GRID_SIZE + offset, size, size)

            if i == 0:
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 40),
                                   (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE * 1.5)
                surface.blit(glow_surf, (0, 0))

            pygame.draw.rect(surface, color, rect, border_radius=7)

            # Eyes for the head
            if i == 0:
                eye_size = 4
                hx, hy = x * GRID_SIZE, y * GRID_SIZE
                dx, dy = self.direction

                if dx == 1:  # Moving Right
                    left_eye_pos = (hx + 12, hy + 5)
                    right_eye_pos = (hx + 12, hy + 15)
                elif dx == -1:  # Moving Left
                    left_eye_pos = (hx + 8, hy + 5)
                    right_eye_pos = (hx + 8, hy + 15)
                elif dy == -1:  # Moving Up
                    left_eye_pos = (hx + 5, hy + 8)
                    right_eye_pos = (hx + 15, hy + 8)
                else:  # Moving Down
                    left_eye_pos = (hx + 5, hy + 12)
                    right_eye_pos = (hx + 15, hy + 12)

                pygame.draw.circle(surface, (20, 20, 20), left_eye_pos, eye_size)
                pygame.draw.circle(surface, (20, 20, 20), right_eye_pos, eye_size)

    def get_head_position(self):
        return self.body[0]


# --- MAIN GAME LOGIC ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Snake")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Segoe UI', 24)
    big_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
    small_font = pygame.font.SysFont('Segoe UI', 18)

    snake = Snake()
    food = Food()
    particles = []

    food.spawn(snake.body)

    game_running = True
    game_over = False
    paused = False

    while True:
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_RETURN:
                            game_over = False
                            snake.reset()
                            food.spawn(snake.body)
                            particles.clear()
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
                            paused = True
                            game_running = False

            if not paused and not game_over:
                ate_food = snake.update(food)

                if ate_food:
                    hx, hy = snake.get_head_position()
                    center_x = hx * GRID_SIZE + GRID_SIZE // 2
                    center_y = hy * GRID_SIZE + GRID_SIZE // 2

                    for _ in range(10):
                        particles.append(Particle(center_x, center_y, FOOD_COLOR))

                particles = [p for p in particles if p.life > 0.05]
                for p in particles:
                    p.update()

                if snake.dead:
                    game_over = True

            # --- DRAWING ---
            screen.fill(BG_COLOR)

            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(screen, GRID_LINE_COLOR, (x, 0), (x, HEIGHT), 1)
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (WIDTH, y), 1)

            food.draw(screen)
            snake.draw(screen)

            for p in particles:
                p.draw(screen)

            score_text = font.render(f"Score: {snake.score}", True, TEXT_COLOR)
            screen.blit(score_text, (15, 15))

            if paused and not game_over:
                pause_label = small_font.render("PAUSED (Press ESC or SPACE)", True, (150, 150, 150))
                screen.blit(pause_label, (WIDTH - 200, 20))

            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BG_COLOR)
                screen.blit(overlay, (0, 0))

                go_text = big_font.render("GAME OVER", True, (255, 60, 60))
                go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
                screen.blit(go_text, go_rect)

                final_score_text = font.render(f"Final Score: {snake.score}", True, TEXT_COLOR)
                final_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
                screen.blit(final_score_text, final_rect)

                restart_text = small_font.render("Press ENTER to Restart", True, GLOW_COLOR)
                restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
                screen.blit(restart_text, restart_rect)

            pygame.display.flip()
            clock.tick(FPS)

        while not game_running and not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                        game_running = True

            pause_text = big_font.render("PAUSED", True, TEXT_COLOR)
            rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, rect)

            dim = pygame.Surface((WIDTH, HEIGHT))
            dim.set_alpha(100)
            dim.fill(BG_COLOR)
            screen.blit(dim, (0, 0))

            pygame.display.flip()
            clock.tick(10)


if __name__ == "__main__":
    main()
