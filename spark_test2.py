import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 10

# Colors
BACKGROUND = (10, 20, 30)
SNAKE_HEAD = (0, 255, 100)
SNAKE_BODY = (0, 200, 80)
FOOD_COLOR = (255, 100, 100)
TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (50, 50, 70)

# Fonts
font = pygame.font.SysFont("Arial", 30, bold=True)

# Game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game 🐍")
clock = pygame.time.Clock()


# Snake class
class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Start in center
        self.direction = (1, 0)  # Move right initially
        self.grow = False  # This must be reset on every game start

    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Collision with self
        if new_head in self.positions:
            return False

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False  # Reset after growing

        return True

    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def grow_snake(self):
        self.grow = True

    def draw(self, surface):
        for i, (x, y) in enumerate(self.positions):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


# Food class
class Food:
    def __init__(self, snake_positions):
        self.position = self.random_position(snake_positions)

    def random_position(self, snake_positions):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_positions:
                return pos

    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)
        for _ in range(3):
            x = self.position[0] * GRID_SIZE + random.randint(0, GRID_SIZE)
            y = self.position[1] * GRID_SIZE + random.randint(0, GRID_SIZE)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 1)


# Game Over screen
def game_over(screen, score):
    screen.fill(BACKGROUND)
    game_over_text = font.render("GAME OVER", True, TEXT_COLOR)
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
    quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# Main game function
def main():
    snake = Snake()
    food = Food(snake.positions)
    score = 0
    running = True
    game_active = True
    particles = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_active:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                if event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                if event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                if event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))

        if game_active:
            if not snake.move():
                game_active = False
                game_over(screen, score)
                continue

            if snake.positions[0] == food.position:
                snake.grow_snake()
                food = Food(snake.positions)
                score += 1

        # Draw everything
        screen.fill(BACKGROUND)

        # Grid lines
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (20, 30, 40), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (20, 30, 40), (0, y), (SCREEN_WIDTH, y), 1)

        # Particles
        for i, (x, y, size) in enumerate(particles):
            pygame.draw.circle(screen, (100, 100, 255), (x, y), size)
            particles[i] = (x + random.randint(-1, 1), y + random.randint(-1, 1), size)
            if size <= 1:
                particles.pop(i)

        if random.randint(0, 20) == 0:
            particles.append((random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(2, 5)))

        snake.draw(screen)
        food.draw(screen)

        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


# Start
if __name__ == "__main__":
    main()
