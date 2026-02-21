# PROMPT USED (create game baseline): Write Snake game in python using pygame library. Make it visually appealing
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 1048576 --host 0.0.0.0 --port 5000 -fa 1 --model /AI/models/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated.Q8_0.gguf

"""
Snake – fixed food & HUD
------------------------------------------------
Run:  python snake.py
"""

import pygame, sys, random

# ------------------------------- constants ------------------------------------
CELL = 30
COLS, ROWS = 20, 15
W, H = COLS * CELL, ROWS * CELL
FPS = 12

BG        = (28, 28, 38)
GRID      = (48, 48, 68)
SNAKE_HEAD= (255, 107, 107)
SNAKE_BODY= (253, 203, 110)
FOOD      = (116, 217, 191)
TEXT      = (245, 245, 245)

pygame.init()
FONT   = pygame.font.SysFont('consolas', 22)
FONT_SMALL = pygame.font.SysFont('consolas', 18)

screen  = pygame.display.set_mode((W + 200, H))
pygame.display.set_caption("Snake")
clock   = pygame.time.Clock()

# ------------------------------- helpers --------------------------------------
def random_food():
    return (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))

def draw_grid():
    for x in range(0, W + 1, CELL):
        pygame.draw.line(screen, GRID, (x, 0), (x, H))
    for y in range(0, H + 1, CELL):
        pygame.draw.line(screen, GRID, (0, y), (W, y))

def draw_cell(r, c, colour):
    rect = pygame.Rect(c * CELL, r * CELL, CELL - 2, CELL - 2)
    pygame.draw.rect(screen, colour, rect)

# ------------------------------- entities -------------------------------------
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(COLS // 2, ROWS // 2),
                     (COLS // 2 - 1, ROWS // 2),
                     (COLS // 2 - 2, ROWS // 2)]
        self.dir  = (1, 0)
        self.grow = 0

    def move(self):
        head = self.body[0]
        new_head = ((head[0] + self.dir[0]) % COLS,
                    (head[1] + self.dir[1]) % ROWS)
        self.body = [new_head] + self.body
        if self.grow:
            self.grow -= 1
        else:
            self.body.pop()

    def change_dir(self, dir):
        if (dir[0], dir[1]) != (-self.dir[0], -self.dir[1]):
            self.dir = dir

class Food:
    def __init__(self, snake):
        self.snake = snake
        self.randomize()

    def randomize(self):
        while True:
            pos = random_food()
            if pos not in self.snake.body:
                self.pos = pos
                return

    def draw(self):
        draw_cell(*self.pos, FOOD)

# ------------------------------- main loop ------------------------------------
def game_over(score):
    msg1 = FONT.render("GAME OVER", True, (255, 107, 107))
    msg2 = FONT_SMALL.render(f"Score: {score}", True, TEXT)
    rect1 = msg1.get_rect(center=(W//2, H//2 - 30))
    rect2 = msg2.get_rect(center=(W//2, H//2 + 20))
    screen.blit(msg1, rect1); screen.blit(msg2, rect2)

def paused(score):
    txt = FONT_SMALL.render("PAUSED – press SPACE or R to resume", True, TEXT)
    rect = txt.get_rect(center=(W//2, H//2))
    screen.blit(txt, rect)

def main():
    snake  = Snake()
    food   = Food(snake)
    score  = 0
    paused_flag = False

    # fixed-timestep clock
    current_time = 0.0
    move_interval = 1.0 / FPS

    while True:
        dt = clock.tick(FPS) / 1000.0
        current_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused_flag = not paused_flag
                elif paused_flag and (event.key in (pygame.K_r, pygame.K_R)):
                    snake.reset(); food.randomize(); score = 0; paused_flag = False

        # direction from KEYDOWN only
        new_dir = None
        keys = pygame.key.get_pressed()
        if   keys[pygame.K_UP]    : new_dir = (0, -1)
        elif keys[pygame.K_DOWN]  : new_dir = (0, 1)
        elif keys[pygame.K_LEFT]  : new_dir = (-1, 0)
        elif keys[pygame.K_RIGHT] : new_dir = (1, 0)

        if new_dir is not None and not paused_flag:
            snake.change_dir(new_dir)

        # fixed-timestep physics
        if not paused_flag and current_time >= move_interval:
            snake.move()
            if snake.body[0] == food.pos:
                score += 10
                food.randomize()
                snake.grow += 1
            current_time = 0.0

        # drawing
        screen.fill(BG)
        draw_grid()

        for r, c in snake.body:
            colour = SNAKE_HEAD if (r, c) == snake.body[0] else SNAKE_BODY
            draw_cell(r, c, colour)

        food.draw()

        # HUD on the right
        txt_score   = FONT.render(f"Score: {score}", True, TEXT)
        rect_score  = txt_score.get_rect(right=W+120, top=20)
        screen.blit(txt_score, rect_score)

        if paused_flag:
            paused(score)

        pygame.display.flip()

if __name__ == "__main__":
    main()
