# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# 1-shot  (missed self.screen used screen instead)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-35B-A3B-UD-Q8_K_XL.gguf  --mmproj /AI/models/Qwen3.5-35B-A3B_mmproj-BF16.gguf

import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 40)
GREEN = (76, 201, 157)
DARK_GREEN = (46, 151, 107)
RED = (255, 87, 87)
YELLOW = (255, 215, 0)
GRAY = (100, 100, 105)
LIGHT_GRAY = (180, 180, 185)

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.length = 3
        self.grow = False

    def set_direction(self, direction):
        if not (direction[0] == -self.direction[0] and direction[1] == -self.direction[1]):
            self.next_direction = direction

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False

    def check_collision(self):
        head = self.body[0]
        if (head[0] < 0 or head[0] >= GRID_WIDTH or
                head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
        if head in self.body[1:]:
            return True
        return False

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x, y, GRID_SIZE - 1, GRID_SIZE - 1))
            if i == 0:
                pygame.draw.rect(screen, LIGHT_GRAY, (x + 4, y + 4, GRID_SIZE - 9, GRID_SIZE - 9))


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.position = (x, y)
            if snake_body is None or (x, y) not in snake_body:
                break

    def draw(self, screen):
        x, y = self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE
        center_x, center_y = x + GRID_SIZE // 2, y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2
        pygame.draw.circle(screen, RED, (center_x, center_y), radius)
        pygame.draw.circle(screen, YELLOW, (center_x - 2, center_y - 2), 3)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 Snake Game")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

    def load_high_score(self):
        try:
            if os.path.exists("high_score.txt"):
                with open("high_score.txt", "r") as f:
                    return int(f.read())
        except:
            pass
        return 0

    def save_high_score(self):
        with open("high_score.txt", "w") as f:
            f.write(str(self.high_score))

    def reset_game(self):
        self.snake.reset()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.game_over = False
        self.paused = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.reset_game()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif not self.paused:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.snake.set_direction((0, -1))
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.snake.set_direction((0, 1))
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.snake.set_direction((-1, 0))
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.snake.set_direction((1, 0))
        return True

    def update(self):
        if self.game_over or self.paused:
            return
        self.snake.move()
        if self.snake.body[0] == self.food.position:
            self.snake.grow = True
            self.snake.length += 1
            self.score += 10
            self.food.spawn(self.snake.body)
        if self.snake.check_collision():
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def draw(self):
        self.screen.fill(BLACK)
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        self.draw_ui()
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
        pygame.display.flip()

    def draw_ui(self):
        text = font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))
        text = font_small.render(f"High Score: {self.high_score}", True, LIGHT_GRAY)
        self.screen.blit(text, (10, 45))

    def draw_pause(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        text = font_medium.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        text = font_large.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, text_rect)
        text = font_medium.render(f"Final Score: {self.score}", True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(text, text_rect)
        text = font_small.render("Press SPACE to Restart", True, LIGHT_GRAY)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(text, text_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
