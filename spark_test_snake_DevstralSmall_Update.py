# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# baseline needed 1-shot to fix the types attribute is being referenced before it's defined in the Food class.
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# follow up enhancement 0-shot
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Devstral-Small-2-24B-Instruct-2512-Q8_0.gguf  --mmproj /AI/models/Devstral-Small-2-24B-Instruct-2512-mmproj-BF16.gguf

import pygame
import random
import sys
import time
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 100, 0)
BACKGROUND = (50, 50, 50)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0
        self.high_score = 0
        self.color = GREEN
        self.head_color = YELLOW
        self.speed = FPS
        self.streak = 0
        self.max_streak = 0
        self.invulnerable = False
        self.invulnerable_time = 0
        self.segments = []  # For visual effect

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        # Check for self-collision (unless invulnerable)
        if not self.invulnerable and new_head in self.positions[1:]:
            return False  # Game over

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

        # Update invulnerability timer
        if self.invulnerable:
            current_time = time.time()
            if current_time - self.invulnerable_time > 3:  # 3 seconds of invulnerability
                self.invulnerable = False

        return True  # Game continues

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.streak = 0
        self.invulnerable = False
        self.segments = []

    def render(self, surface):
        # Create segments for smooth movement effect
        if len(self.positions) > 1:
            self.segments = []
            for i in range(1, len(self.positions)):
                # Create a segment between current and next position
                prev_x, prev_y = self.positions[i-1]
                curr_x, curr_y = self.positions[i]

                # Calculate the angle of the segment
                dx = curr_x - prev_x
                dy = curr_y - prev_y
                angle = math.degrees(math.atan2(dy, dx))

                # Create a rotated rectangle for the segment
                segment_rect = pygame.Rect(prev_x * GRID_SIZE, prev_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                rotated_segment = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(rotated_segment, (0, 200, 0), (0, 0, GRID_SIZE, GRID_SIZE), 0)
                rotated_segment = pygame.transform.rotate(rotated_segment, angle)
                rotated_segment_rect = rotated_segment.get_rect(center=segment_rect.center)

                self.segments.append((rotated_segment, rotated_segment_rect))

        # Draw segments
        for segment in self.segments:
            surface.blit(segment[0], segment[1])

        # Draw head
        head = self.get_head_position()
        head_rect = pygame.Rect((head[0] * GRID_SIZE, head[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))

        # Pulsing effect when invulnerable
        if self.invulnerable:
            pulse_size = GRID_SIZE + int(5 * math.sin(time.time() * 5))
            pulse_rect = pygame.Rect((head[0] * GRID_SIZE - (pulse_size - GRID_SIZE) // 2,
                                    head[1] * GRID_SIZE - (pulse_size - GRID_SIZE) // 2),
                                   (pulse_size, pulse_size))
            pygame.draw.circle(surface, (255, 255, 255, 100), pulse_rect.center, pulse_size // 2)
            pygame.draw.rect(surface, YELLOW, head_rect)
            pygame.draw.rect(surface, DARK_GREEN, head_rect, 2)
        else:
            pygame.draw.rect(surface, self.head_color, head_rect)
            pygame.draw.rect(surface, DARK_GREEN, head_rect, 2)

        # Draw body
        for i, p in enumerate(self.positions):
            if i == 0:  # Skip head
                continue
            # Gradient effect for body
            color_intensity = 150 + (i * 5) % 100
            body_color = (0, color_intensity, 0)
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, body_color, rect)
            pygame.draw.rect(surface, DARK_GREEN, rect, 1)  # Border

class Food:
    def __init__(self):
        self.types = ["regular", "special", "power", "invulnerable", "golden"]
        self.current_type = "regular"
        self.position = (0, 0)
        self.color = RED
        self.spawn_time = 0
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        self.current_type = random.choice(self.types)

        # Adjust probabilities for different food types
        if self.current_type == "special":
            if random.random() > 0.3:  # 70% chance to change back to regular
                self.current_type = "regular"
        elif self.current_type == "power":
            if random.random() > 0.5:  # 50% chance to change back to regular
                self.current_type = "regular"
        elif self.current_type == "invulnerable":
            if random.random() > 0.7:  # 30% chance to keep invulnerable
                self.current_type = "regular"
        elif self.current_type == "golden":
            if random.random() > 0.8:  # 20% chance to keep golden
                self.current_type = "regular"

        self.spawn_time = time.time()

    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))

        if self.current_type == "regular":
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.circle(surface, WHITE, (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                               self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)
        elif self.current_type == "special":
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, PURPLE, rect, 3)  # Border
            pygame.draw.circle(surface, YELLOW, (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                               self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 4)
        elif self.current_type == "power":
            pygame.draw.rect(surface, ORANGE, rect)
            pygame.draw.rect(surface, RED, rect, 2)  # Border
            pygame.draw.rect(surface, WHITE, (self.position[0] * GRID_SIZE + 5, self.position[1] * GRID_SIZE + 5,
                                            GRID_SIZE - 10, GRID_SIZE - 10))
        elif self.current_type == "invulnerable":
            pygame.draw.rect(surface, PINK, rect)
            pygame.draw.circle(surface, CYAN, (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                              self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)
            pygame.draw.circle(surface, WHITE, (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                              self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 4)
        elif self.current_type == "golden":
            pygame.draw.rect(surface, GOLD, rect)
            pygame.draw.rect(surface, (218, 165, 32), rect, 3)  # Border
            pygame.draw.circle(surface, (255, 215, 0), (self.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                                       self.position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)

def show_game_over(surface, score, high_score, streak, max_streak):
    surface.fill(BACKGROUND)
    draw_grid(surface)

    font = pygame.font.SysFont('arial', 50)
    text = font.render(f"Game Over!", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))

    font_medium = pygame.font.SysFont('arial', 30)
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))

    high_score_text = font_medium.render(f"High Score: {high_score}", True, GOLD)
    high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))

    streak_text = font_medium.render(f"Current Streak: {streak}", True, YELLOW)
    streak_rect = streak_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))

    max_streak_text = font_medium.render(f"Max Streak: {max_streak}", True, YELLOW)
    max_streak_rect = max_streak_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))

    font_small = pygame.font.SysFont('arial', 20)
    restart_text = font_small.render("Press R to restart or Q to quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))

    surface.blit(text, text_rect)
    surface.blit(score_text, score_rect)
    surface.blit(high_score_text, high_score_rect)
    surface.blit(streak_text, streak_rect)
    surface.blit(max_streak_text, max_streak_rect)
    surface.blit(restart_text, restart_rect)

def show_score(surface, score, high_score, streak):
    font = pygame.font.SysFont('arial', 20)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, GOLD)
    streak_text = font.render(f"Streak: {streak}", True, YELLOW)

    surface.blit(score_text, (10, 10))
    surface.blit(high_score_text, (10, 40))
    surface.blit(streak_text, (10, 70))

def show_tutorial(surface):
    font = pygame.font.SysFont('arial', 16)
    tutorial_text = [
        "Controls: Arrow keys",
        "Regular food: +10 points",
        "Special food: +30 points, grows by 2",
        "Power food: +20 points, increases speed",
        "Invulnerable food: 3 seconds of invulnerability",
        "Golden food: +50 points, extra long streak bonus"
    ]

    for i, line in enumerate(tutorial_text):
        text = font.render(line, True, WHITE)
        surface.blit(text, (WIDTH - 200, 20 + i * 25))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Addictive Snake Game")
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()
    game_over = False
    show_tutorial_screen = True

    # Game timer for streak calculation
    last_food_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if show_tutorial_screen:
                    if event.key == pygame.K_RETURN:
                        show_tutorial_screen = False
                elif game_over:
                    if event.key == pygame.K_r:
                        snake.reset()
                        food.randomize_position()
                        game_over = False
                        last_food_time = time.time()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT

        if show_tutorial_screen:
            # Show tutorial screen
            screen.fill(BACKGROUND)
            draw_grid(screen)

            font = pygame.font.SysFont('arial', 30)
            title = font.render("Addictive Snake Game", True, YELLOW)
            title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))

            font_small = pygame.font.SysFont('arial', 20)
            start_text = font_small.render("Press Enter to Start", True, WHITE)
            start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))

            screen.blit(title, title_rect)
            screen.blit(start_text, start_rect)
            show_tutorial(screen)

            pygame.display.update()
            continue

        if not game_over:
            # Update game state
            if not snake.update():
                game_over = True

            # Check if snake eats food
            if snake.get_head_position() == food.position:
                # Different effects for different food types
                if food.current_type == "regular":
                    snake.length += 1
                    snake.score += 10
                    snake.streak += 1
                elif food.current_type == "special":
                    snake.length += 2
                    snake.score += 30
                    snake.streak += 2
                elif food.current_type == "power":
                    snake.speed = min(snake.speed + 2, 20)  # Increase speed
                    snake.score += 20
                    snake.streak += 1
                elif food.current_type == "invulnerable":
                    snake.invulnerable = True
                    snake.invulnerable_time = time.time()
                    snake.score += 50
                    snake.streak += 3
                elif food.current_type == "golden":
                    snake.length += 3
                    snake.score += 50
                    snake.streak += 5

                # Update high score and max streak
                if snake.score > snake.high_score:
                    snake.high_score = snake.score
                if snake.streak > snake.max_streak:
                    snake.max_streak = snake.streak

                food.randomize_position()
                # Make sure food doesn't spawn on snake
                while food.position in snake.positions:
                    food.randomize_position()

                # Streak bonus (every 5 foods)
                if snake.streak % 5 == 0 and snake.streak > 0:
                    snake.score += 20 * (snake.streak // 5)

            # Reset streak if too much time passes without eating
            current_time = time.time()
            if current_time - last_food_time > 10:  # 10 seconds without eating
                snake.streak = 0
            else:
                last_food_time = current_time

        # Drawing
        screen.fill(BACKGROUND)
        draw_grid(screen)

        snake.render(screen)
        food.render(screen)

        # Show current food type
        if food.current_type == "regular":
            food_type_text = "Regular"
            food_color = RED
        elif food.current_type == "special":
            food_type_text = "Special"
            food_color = BLUE
        elif food.current_type == "power":
            food_type_text = "Power"
            food_color = ORANGE
        elif food.current_type == "invulnerable":
            food_type_text = "Invulnerable"
            food_color = PINK
        elif food.current_type == "golden":
            food_type_text = "Golden"
            food_color = GOLD

        font_small = pygame.font.SysFont('arial', 16)
        food_text = font_small.render(f"Next: {food_type_text}", True, food_color)
        food_rect = food_text.get_rect(center=(WIDTH//2, HEIGHT - 30))
        screen.blit(food_text, food_rect)

        show_score(screen, snake.score, snake.high_score, snake.streak)

        if game_over:
            show_game_over(screen, snake.score, snake.high_score, snake.streak, snake.max_streak)

        pygame.display.update()
        clock.tick(snake.speed)

if __name__ == "__main__":
    main()
