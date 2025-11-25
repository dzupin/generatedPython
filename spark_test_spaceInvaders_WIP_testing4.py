# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-122B-A10B-heretic.Q6_K.gguf  --mmproj /AI/models/Qwen3.5-122B-A10B-heretic.mmproj-f16.gguf

import pygame
import random

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Neon Palette)
COLOR_BG = (10, 10, 20)
COLOR_PLAYER = (0, 255, 255)
COLOR_ENEMY_1 = (255, 50, 50)
COLOR_ENEMY_2 = (255, 100, 50)
COLOR_ENEMY_3 = (255, 200, 50)
COLOR_PLAYER_BULLET = (0, 255, 255)
COLOR_ENEMY_BULLET = (255, 100, 100)
COLOR_TEXT = (255, 255, 255)

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED_X = 1
ENEMY_DROP_Y = 20
BULLET_COOLDOWN = 15

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neon Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 20, bold=True)
title_font = pygame.font.SysFont("Courier New", 48, bold=True)


# --- Helper Functions ---

def draw_glow(surface, color, rect, size_offset=10, alpha=50):
    glow_surf = pygame.Surface((rect.width + size_offset, rect.height + size_offset), pygame.SRCALPHA)
    glow_color = (*color, alpha)
    pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=4)
    surface.blit(glow_surf, (rect.x - size_offset // 2, rect.y - size_offset // 2))


def create_stars(count):
    stars = []
    for _ in range(count):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        speed = random.uniform(0.5, 2)
        brightness = random.randint(50, 255)
        stars.append([x, y, speed, brightness])
    return stars


def update_stars(stars):
    for star in stars:
        star[1] += star[2]
        if star[1] > SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, SCREEN_WIDTH)


def draw_text(text, font, color, surface, x, y, center=False):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


# --- Classes ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = 40

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.05)

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / 40) * 255)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))


class Player:
    def __init__(self):
        self.width = 40
        self.height = 30
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = PLAYER_SPEED
        self.color = COLOR_PLAYER
        self.bullets = []
        self.cooldown = 0
        self.lives = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        if self.cooldown == 0:
            # Player shoots UP (direction=-1 means y decreases)
            self.bullets.append(Bullet(self.x + self.width // 2 - 2, self.y, direction=-1))
            self.cooldown = BULLET_COOLDOWN

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        draw_glow(surface, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height - 5),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.rect(surface, (100, 255, 255), (self.x + 15, self.y + 10, 10, 10))


class Enemy:
    def __init__(self, x, y, type_id):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type_id = type_id
        if type_id == 1:
            self.color = COLOR_ENEMY_1
        elif type_id == 2:
            self.color = COLOR_ENEMY_2
        else:
            self.color = COLOR_ENEMY_3
        self.alive = True

    def draw(self, surface):
        if not self.alive: return
        draw_glow(surface, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
        color = self.color
        pygame.draw.rect(surface, color, (self.x + 5, self.y + 5, 20, 20))
        pygame.draw.rect(surface, (0, 0, 0), (self.x + 8, self.y + 8, 5, 5))
        pygame.draw.rect(surface, (0, 0, 0), (self.x + 17, self.y + 8, 5, 5))
        pygame.draw.rect(surface, color, (self.x + 10, self.y + 18, 10, 5))


class Bullet:
    def __init__(self, x, y, direction=-1):  # FIXED: Default direction=-1 (player shoots up)
        self.x = x
        self.y = y
        self.width = 4
        self.height = 12
        self.speed = BULLET_SPEED * direction  # direction=-1 for player (up), direction=1 for enemy (down)
        self.active = True
        self.is_player = direction < 0  # direction < 0 means player bullet

    def update(self):
        self.y += self.speed
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface):
        color = COLOR_PLAYER_BULLET if self.is_player else COLOR_ENEMY_BULLET
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))


# --- Game Logic ---

def main():
    running = True
    game_state = "MENU"

    # Entities
    player = Player()
    stars = create_stars(100)
    particles = []
    enemies = []
    enemy_bullets = []
    enemy_direction = 1
    enemy_move_interval = 40

    def spawn_enemies():
        nonlocal enemies, enemy_move_interval
        enemies = []
        enemy_move_interval = 40
        rows = 5
        cols = 10
        padding = 15
        start_x = 50
        start_y = 50
        for r in range(rows):
            for c in range(cols):
                type_id = (r % 3) + 1
                ex = start_x + c * (30 + padding)
                ey = start_y + r * (30 + padding)
                enemies.append(Enemy(ex, ey, type_id))

    score = 0

    spawn_enemies()

    while running:
        clock.tick(FPS)
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    if event.key == pygame.K_SPACE:
                        game_state = "PLAYING"
                        spawn_enemies()
                        player = Player()
                        player.bullets = []
                        enemy_bullets = []
                        score = 0
                elif game_state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        player.shoot()
                elif game_state == "GAMEOVER":
                    if event.key == pygame.K_SPACE:
                        game_state = "MENU"

        for star in stars:
            pygame.draw.circle(screen, (star[3], star[3], star[3]), (int(star[0]), int(star[1])), 1)
        update_stars(stars)

        if game_state == "MENU":
            draw_text("NEON SPACE INVADERS", title_font, COLOR_PLAYER, screen, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 2 - 50, center=True)
            draw_text("Press SPACE to Start", font, COLOR_TEXT, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                      center=True)
            draw_text("Controls: Arrow Keys to Move, SPACE to Shoot", font, (150, 150, 150), screen, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 2 + 60, center=True)

        elif game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update()
            player.draw(screen)

            # Update & Draw Player Bullets
            for b in player.bullets[:]:
                b.update()
                b.draw(screen)
                if not b.active:
                    player.bullets.remove(b)

            # Enemy Movement Logic
            move_down = False
            for e in enemies:
                if e.alive:
                    if (e.x + e.width >= SCREEN_WIDTH and enemy_direction == 1) or (e.x <= 0 and enemy_direction == -1):
                        move_down = True
                        break

            if move_down:
                enemy_direction *= -1
                for e in enemies:
                    e.y += ENEMY_DROP_Y
            else:
                for e in enemies:
                    e.x += ENEMY_SPEED_X * enemy_direction * (enemy_move_interval / 40)

            # Enemy Shooting (Shoot DOWN at player)
            if random.randint(0, 200) < 1 and any(e.alive for e in enemies):
                shooter = random.choice([e for e in enemies if e.alive])
                # Enemy shoots DOWN (direction=1 means y increases)
                enemy_bullets.append(
                    Bullet(shooter.x + shooter.width // 2 - 2, shooter.y + shooter.height, direction=1))

            # Collision: Player Bullets hitting Enemies
            for b in player.bullets[:]:
                for e in enemies[:]:
                    if e.alive and b.active:
                        if (b.x < e.x + e.width and b.x + b.width > e.x and
                                b.y < e.y + e.height and b.y + b.height > e.y):
                            e.alive = False
                            b.active = False
                            if b in player.bullets:
                                player.bullets.remove(b)
                            score += 100
                            for _ in range(10):
                                particles.append(Particle(e.x + e.width // 2, e.y + e.height // 2, e.color))
                            break

            # Update & Draw Enemy Bullets
            for b in enemy_bullets[:]:
                b.update()
                b.draw(screen)
                if not b.active:
                    enemy_bullets.remove(b)
                    continue

                # Collision: Enemy Bullets hitting Player
                if (b.x < player.x + player.width and b.x + b.width > player.x and
                        b.y < player.y + player.height and b.y + b.height > player.y):
                    player.lives -= 1
                    b.active = False
                    for _ in range(10):
                        particles.append(
                            Particle(player.x + player.width // 2, player.y + player.height // 2, COLOR_PLAYER))
                    if player.lives <= 0:
                        game_state = "GAMEOVER"

            # Update & Draw Particles
            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)

            # Draw Enemies
            for e in enemies:
                e.draw(screen)

            # Check Win Condition (All enemies dead)
            if all(not e.alive for e in enemies):
                spawn_enemies()
                if enemy_move_interval > 15:
                    enemy_move_interval -= 5

            # UI
            draw_text(f"Lives: {player.lives}", font, COLOR_PLAYER, screen, 10, 10)
            draw_text(f"Score: {score}", font, COLOR_TEXT, screen, 10, 40)
            draw_text(f"Level: {60 - enemy_move_interval}", font, COLOR_TEXT, screen, SCREEN_WIDTH - 150, 10)

        elif game_state == "GAMEOVER":
            draw_text("GAME OVER", title_font, (255, 50, 50), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                      center=True)
            draw_text(f"Final Score: {score}", font, COLOR_TEXT, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10,
                      center=True)
            draw_text("Press SPACE to Menu", font, COLOR_TEXT, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                      center=True)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
