# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# NOTE: First prompt 0-shot, Second prompt multiple error reporting prompt needed to create functional code
# functional  context 256K perfect summary  partial censor Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf    (https://huggingface.co/unsloth/Qwen3-Next-80B-A3B-Instruct-GGUF)  (text only)
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3-Next-80B-A3B-Instruct-Q8_0-00001-of-00002.gguf


import pygame
import random
import math

# Initialize pygame
pygame.init()

# Colors (modern, pleasing palette)
BACKGROUND_COLOR = (10, 15, 30)  # Deep space blue
SNAKE_COLORS = [
    (70, 200, 150),  # Emerald
    (100, 180, 255),  # Cyan-blue
    (255, 150, 100),  # Coral
    (255, 100, 180),  # Magenta
    (200, 70, 255),  # Purple
    (255, 200, 70),  # Gold
]
FOOD_COLOR = (255, 100, 100)  # Soft pink
TEXT_COLOR = (220, 220, 255)  # Light white-blue
BORDER_COLOR = (40, 60, 100)  # Darker border
GRID_COLOR = (25, 30, 60)  # Subtle grid

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
BASE_FPS = 10  # Starting speed
FPS = BASE_FPS  # Global speed variable (modified during play)

# Initialize screen and fonts
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Addictive Snake — Eat. Grow. Conquer.")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont('Arial', 48, bold=True)
font_medium = pygame.font.SysFont('Arial', 32)
font_small = pygame.font.SysFont('Arial', 20)
font_toast = pygame.font.SysFont('Arial', 28, bold=True)

# Sound Effects (optional)
try:
    pygame.mixer.init()
    can_play_sounds = True
    eat_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=bytearray([0] * 1024)))  # Dummy placeholder
    game_over_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=bytearray([0] * 1024)))
    level_up_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=bytearray([0] * 1024)))
except:
    can_play_sounds = False


def play_sound(sound):
    if can_play_sounds:
        sound.play()


# Create dummy sound functions if mixer fails
def dummy_sound():
    pass


if not can_play_sounds:
    eat_sound = dummy_sound
    game_over_sound = dummy_sound
    level_up_sound = dummy_sound


def draw_gradient_background():
    """Draw a vertical gradient background"""
    for y in range(WINDOW_HEIGHT):
        intensity = int(10 + (y / WINDOW_HEIGHT) * 25)
        color = (intensity, intensity + 5, intensity + 25)
        pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))


def draw_grid():
    """Draw subtle grid lines"""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)


def draw_snake(snake_body, snake_color, trail_list):
    """Draw snake with trail effect and color"""
    # Draw trail (fading pixels behind head)
    for i, trail_pos in enumerate(trail_list):
        alpha = 1 - (i / len(trail_list)) * 0.7
        trail_size = GRID_SIZE - 4
        rect = pygame.Rect(
            trail_pos[0] * GRID_SIZE + 2,
            trail_pos[1] * GRID_SIZE + 2,
            trail_size, trail_size
        )
        trail_color = (
            int(snake_color[0] * alpha),
            int(snake_color[1] * alpha),
            int(snake_color[2] * alpha)
        )
        pygame.draw.rect(screen, trail_color, rect, border_radius=6)

    # Draw snake body
    for i, segment in enumerate(snake_body):
        if i == 0:  # Head
            color = (120, 255, 200)  # Brighter head
            size = GRID_SIZE - 2
        else:
            color = snake_color
            size = GRID_SIZE - 4

        rect = pygame.Rect(
            segment[0] * GRID_SIZE + (GRID_SIZE - size) // 2,
            segment[1] * GRID_SIZE + (GRID_SIZE - size) // 2,
            size, size
        )
        pygame.draw.rect(screen, color, rect, border_radius=8)

        # Eyes on head — only if snake has at least 2 segments
        if i == 0 and len(snake_body) > 1:
            eye_size = 2
            # Determine direction from head to next segment
            head_x, head_y = snake_body[0]
            next_x, next_y = snake_body[1]

            eye_offset_x = 0
            eye_offset_y = 0

            if head_x > next_x:  # Moving left → eyes on right
                eye_offset_x = 3
            elif head_x < next_x:  # Moving right → eyes on left
                eye_offset_x = -3
            elif head_y > next_y:  # Moving up → eyes on bottom
                eye_offset_y = 3
            elif head_y < next_y:  # Moving down → eyes on top
                eye_offset_y = -3

            # Left eye
            pygame.draw.circle(screen, (10, 10, 10),
                               (segment[0] * GRID_SIZE + GRID_SIZE // 2 + eye_offset_x,
                                segment[1] * GRID_SIZE + GRID_SIZE // 2 + eye_offset_y), eye_size)
            # Right eye
            pygame.draw.circle(screen, (10, 10, 10),
                               (segment[0] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x,
                                segment[1] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_y), eye_size)


def draw_food(food_position, multiplier=1):
    """Draw food with glow and pulsing scale"""
    # Glow effect
    for i in range(4):
        alpha = 0.25 - (i * 0.05)
        size = GRID_SIZE + i * 3
        glow_rect = pygame.Rect(
            food_position[0] * GRID_SIZE + (GRID_SIZE - size) // 2,
            food_position[1] * GRID_SIZE + (GRID_SIZE - size) // 2,
            size, size
        )
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface,
                           (FOOD_COLOR[0], FOOD_COLOR[1], FOOD_COLOR[2], int(255 * alpha)),
                           (size // 2, size // 2), size // 2)
        screen.blit(glow_surface, glow_rect.topleft)

    # Pulsing effect
    pulse = (1 + 0.1 * abs(math.sin(pygame.time.get_ticks() * 0.003)))  # Slow pulse
    radius = int((GRID_SIZE // 2 - 2) * pulse)

    pygame.draw.circle(screen, FOOD_COLOR,
                       (food_position[0] * GRID_SIZE + GRID_SIZE // 2,
                        food_position[1] * GRID_SIZE + GRID_SIZE // 2),
                       radius)

    # Shine highlight
    pygame.draw.circle(screen, (255, 255, 255, 150),
                       (food_position[0] * GRID_SIZE + GRID_SIZE // 3,
                        food_position[1] * GRID_SIZE + GRID_SIZE // 3),
                       2)


def show_score(score, multiplier, level):
    """Display score, multiplier, and level"""
    score_text = font_medium.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))

    if multiplier > 1:
        multi_text = font_small.render(f"X{multiplier} COMBO!", True, (255, 255, 100))
        screen.blit(multi_text, (10, 50))

    level_text = font_small.render(f"Level: {level}", True, TEXT_COLOR)
    screen.blit(level_text, (10, 80))


def show_toast(message, duration=2000):
    """Display a floating toast notification"""
    now = pygame.time.get_ticks()
    if not hasattr(show_toast, 'toasts'):
        show_toast.toasts = []
    show_toast.toasts.append((message, now))

    # Clean old toasts
    show_toast.toasts = [(msg, t) for msg, t in show_toast.toasts if now - t < duration]

    # Draw active toasts
    for i, (msg, t) in enumerate(show_toast.toasts):
        toast_color = (50, 200, 100) if "LEVEL" in msg else (255, 255, 100)
        toast_text = font_toast.render(msg, True, toast_color)
        x = WINDOW_WIDTH // 2 - toast_text.get_width() // 2
        y = 100 + i * 40 - (now - t) * 0.05  # Fade up
        screen.blit(toast_text, (x, y))


def show_game_over(score, level):
    """Game over with screen shake and animation"""
    # Screen shake effect
    shake_offset = random.randint(-5, 5), random.randint(-5, 5)

    # Overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Game Over text (with shake)
    game_over_text = font_large.render("GAME OVER", True, (255, 80, 80))
    text_rect = game_over_text.get_rect(
        center=(WINDOW_WIDTH // 2 + shake_offset[0], WINDOW_HEIGHT // 2 - 60 + shake_offset[1]))
    screen.blit(game_over_text, text_rect)

    # Final score
    score_text = font_medium.render(f"Final Score: {score}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(score_text, score_rect)

    # Level reached
    level_text = font_small.render(f"Reached Level {level}", True, TEXT_COLOR)
    level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
    screen.blit(level_text, level_rect)

    # Restart instruction
    restart_text = font_small.render("Press SPACE to Restart or ESC to Quit", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
    screen.blit(restart_text, restart_rect)

    # Add floating particles
    for _ in range(20):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(1, 4)
        color = (random.randint(200, 255), random.randint(100, 150), random.randint(100, 150))
        pygame.draw.circle(screen, color, (x, y), size)


def game_loop():
    """Main game loop with addictive mechanics"""
    global FPS  # 👈 Declare global at the top — CRITICAL FIX!

    # Initial snake position
    snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (1, 0)  # Start moving right
    snake_length = 1
    snake_color_index = 0
    snake_color = SNAKE_COLORS[snake_color_index]

    # Initial food position
    food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    # Game state
    game_over = False
    paused = False
    score = 0
    combo = 0
    combo_multiplier = 1
    level = 1
    last_food_eaten = 0
    trail_list = []  # For snake trail
    last_trail_time = 0
    trail_delay = 100  # ms between trail dots

    # Main game loop
    while True:
        current_time = pygame.time.get_ticks()

        # Trail generation
        if len(snake_body) > 0 and current_time - last_trail_time > trail_delay:
            trail_list.append(snake_body[0])
            if len(trail_list) > 8:
                trail_list.pop(0)
            last_trail_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_direction != (0, 1):
                    snake_direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake_direction != (0, -1):
                    snake_direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake_direction != (1, 0):
                    snake_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                    snake_direction = (1, 0)
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_SPACE and game_over:
                    # Restart game
                    snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                    snake_direction = (1, 0)
                    snake_length = 1
                    snake_color_index = 0
                    snake_color = SNAKE_COLORS[snake_color_index]
                    food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                    game_over = False
                    paused = False
                    score = 0
                    combo = 0
                    combo_multiplier = 1
                    level = 1
                    trail_list = []
                    FPS = BASE_FPS  # Reset speed
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        if game_over:
            screen.fill(BACKGROUND_COLOR)
            draw_gradient_background()
            draw_grid()
            show_score(score, combo_multiplier, level)
            show_game_over(score, level)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if paused:
            screen.fill(BACKGROUND_COLOR)
            draw_gradient_background()
            draw_grid()
            draw_snake(snake_body, snake_color, trail_list)
            draw_food(food_position, combo_multiplier)
            show_score(score, combo_multiplier, level)

            # Pause overlay
            pause_text = font_large.render("PAUSED", True, TEXT_COLOR)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_text, text_rect)

            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Move snake
        head_x, head_y = snake_body[0]
        dx, dy = snake_direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Check for self-collision
        if new_head in snake_body[1:]:
            game_over = True
            game_over_sound()
            continue

        # Add new head
        snake_body.insert(0, new_head)

        # Check if food eaten
        if new_head == food_position:
            snake_length += 1
            combo += 1
            last_food_eaten = current_time

            if combo >= 3:
                combo_multiplier = min(4, combo // 3 + 1)  # Max 4x
                score += 10 * combo_multiplier
                play_sound(eat_sound)
                show_toast(f"LEVEL UP! {combo_multiplier}x", 2000)
                # Level up every 100 points
                if score // 100 > level - 1:
                    level = score // 100 + 1
                    snake_color_index = (snake_color_index + 1) % len(SNAKE_COLORS)
                    snake_color = SNAKE_COLORS[snake_color_index]
                    play_sound(level_up_sound)
                    show_toast(f"LEVEL {level}!", 2000)
                    FPS = min(BASE_FPS + level * 2, 25)  # Speed up gradually — NO global needed here anymore!
            else:
                score += 10
                play_sound(eat_sound)

            # Generate new food (avoiding snake body)
            while True:
                food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                if food_position not in snake_body:
                    break
        else:
            # Remove tail if no food eaten
            if len(snake_body) > snake_length:
                snake_body.pop()
            combo = 0  # Reset combo if no food
            combo_multiplier = 1

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        draw_gradient_background()
        draw_grid()
        draw_snake(snake_body, snake_color, trail_list)
        draw_food(food_position, combo_multiplier)
        show_score(score, combo_multiplier, level)
        show_toast("")  # Refresh toasts

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    game_loop()
