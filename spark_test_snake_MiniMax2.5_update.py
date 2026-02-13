import pygame
import sys
import random
import os

# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.


# --- Configuration & Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
FPS_BASE = 12  # Starting speed (lower is slower)

# --- Colors (R, G, B) ---
COLOR_BG = (20, 20, 20)
COLOR_GRID = (35, 35, 35)
COLOR_SNAKE_HEAD = (0, 255, 127)
COLOR_SNAKE_BODY = (0, 200, 100)
COLOR_FOOD = (255, 105, 80)
COLOR_TEXT = (240, 240, 240)
COLOR_HIGH_SCORE = (100, 100, 100)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Pygame")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)
big_font = pygame.font.SysFont("arial", 40, bold=True)
small_font = pygame.font.SysFont("arial", 15)


# --- Helper Classes ---

class PopupText:
    """Creates text that floats up and fades out."""

    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 20  # How many frames it lasts

    def update(self):
        self.y -= 1.5  # Move up
        self.timer -= 1

    def draw(self, surface, off_x, off_y):
        if self.timer > 0:
            text_surf = font.render(self.text, True, self.color)
            surface.blit(text_surf, (self.x + off_x, self.y + off_y))


# --- High Score Logic ---
HS_FILE = "highscore.txt"


def get_high_score():
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0


def save_high_score(score):
    with open(HS_FILE, "w") as f:
        f.write(str(score))


# --- Helper Functions ---
def draw_text(surface, font_obj, text, color, x, y, centered=False):
    text_surface = font_obj.render(text, True, color)
    rect = text_surface.get_rect()
    if centered:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_surface, rect)


# --- Main Game Function ---

def main():
    # Game State
    snake = [[5, 5], [4, 5], [3, 5]]
    score = 0
    high_score = get_high_score()

    # Direction & Grid
    snake_dir = (1, 0)
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE

    # Generate Food
    food_pos = [random.randint(0, cols - 1), random.randint(0, rows - 1)]

    # Visual Effects State
    effects = []
    shake_timer = 0

    running = True
    game_over = False

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        main()
                    elif event.key == pygame.K_q:
                        running = False
                else:
                    if event.key == pygame.K_LEFT and snake_dir != (1, 0):
                        snake_dir = (-1, 0)
                    elif event.key == pygame.K_RIGHT and snake_dir != (-1, 0):
                        snake_dir = (1, 0)
                    elif event.key == pygame.K_UP and snake_dir != (0, 1):
                        snake_dir = (0, -1)
                    elif event.key == pygame.K_DOWN and snake_dir != (0, -1):
                        snake_dir = (0, 1)

        # 2. Game Logic
        if not game_over:
            # Calculate Dynamic Speed: Gets faster every 3 points
            # Cap max speed at 30 FPS (so it doesn't become impossible)
            current_speed = min(FPS_BASE + (score // 3), 30)

            head_x, head_y = snake[0]
            dx, dy = snake_dir
            new_head = [head_x + dx, head_y + dy]

            # Collisions (Walls)
            if (new_head[0] < 0 or new_head[0] >= cols or
                    new_head[1] < 0 or new_head[1] >= rows):
                game_over = True

            # Collisions (Self)
            if new_head in snake:
                game_over = True

            # Movement
            if not game_over:
                snake.insert(0, new_head)

                # Eat Food
                if new_head == food_pos:
                    score += 1
                    shake_timer = 5  # Trigger screen shake for 5 frames

                    # Add floating text effect
                    # FIX: Creating instance and appending correctly
                    pt_instance = PopupText(
                        new_head[0] * BLOCK_SIZE,
                        new_head[1] * BLOCK_SIZE,
                        "+1",
                        (255, 255, 255)
                    )
                    effects.append(pt_instance)

                    # Respawn Food
                    while True:
                        food_pos = [random.randint(0, cols - 1), random.randint(0, rows - 1)]
                        if food_pos not in snake:
                            break
                else:
                    snake.pop()

        # 3. Drawing
        screen.fill(COLOR_BG)

        # Calculate Camera Offset (Screen Shake)
        off_x, off_y = 0, 0
        if shake_timer > 0:
            off_x = random.randint(-3, 3)
            off_y = random.randint(-3, 3)
            shake_timer -= 1

        # Draw Grid
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

        # Draw Food
        fx, fy = food_pos
        pygame.draw.circle(screen, COLOR_FOOD,
                           (fx * BLOCK_SIZE + BLOCK_SIZE // 2 + off_x, fy * BLOCK_SIZE + BLOCK_SIZE // 2 + off_y),
                           BLOCK_SIZE // 2 - 2)

        # Draw Snake
        for i, block in enumerate(snake):
            x, y = block
            block_color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            rect = pygame.Rect(x * BLOCK_SIZE + off_x, y * BLOCK_SIZE + off_y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, block_color, rect)
            # Outline
            pygame.draw.rect(screen, COLOR_BG, rect, 1)

        # Draw Effects (Popups)
        for effect in effects[:]:
            effect.update()
            if effect.timer <= 0:
                effects.remove(effect)
            else:
                effect.draw(screen, off_x, off_y)

        # Draw UI
        score_surf = font.render(f"SCORE: {score}", True, COLOR_TEXT)
        screen.blit(score_surf, (10, 10))

        # High Score UI
        hs_color = (0, 255, 0) if score >= high_score and score > 0 else COLOR_HIGH_SCORE
        hs_surf = small_font.render(f"BEST: {high_score}", True, hs_color)
        screen.blit(hs_surf, (10, 35))

        # Speed UI
        sp_surf = small_font.render(f"SPEED: {current_speed}", True, COLOR_TEXT)
        screen.blit(sp_surf, (10, 60))

        # Game Over Overlay
        if game_over:
            if score > high_score:
                save_high_score(score)
                high_score = score

            # Darken
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            draw_text(screen, big_font, "GAME OVER", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                      centered=True)
            draw_text(screen, font, f"Final Score: {score}", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                      centered=True)
            draw_text(screen, font, "Press 'R' to Restart", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
                      centered=True)
            draw_text(screen, font, "Press 'Q' to Quit", COLOR_TEXT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70,
                      centered=True)

        pygame.display.flip()

        # Speed Control
        if game_over:
            clock.tick(FPS_BASE)
        else:
            clock.tick(current_speed)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
