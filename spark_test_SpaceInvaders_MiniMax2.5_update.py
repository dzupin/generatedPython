import pygame
import sys
import random

# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library. (Then run error fix for: TypeError: invalid color argument)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
import pygame
import random

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (15, 15, 20)  # Deep space blue/black
TEXT_COLOR = (255, 220, 150)  # Creamy white

# Game Settings
START_SPEED = 4
PLAYER_SPEED = 6
BULLET_SPEED = 7
ENEMY_DROP_SPEED = 30
ENEMY_BASE_SPEED = 1
SCREEN_SHAKE_INTENSITY = 0


# --- Helper: Sprite Generator ---
def create_sprite_surface(bitmap, color, pixel_size, scale=1):
    """
    Generates a pygame Surface from a text-based bitmap.
    bitmap: List of strings representing rows. '1' is a pixel.
    color: RGB tuple.
    pixel_size: Size of one 'pixel'.
    """
    rows = len(bitmap)
    cols = len(bitmap[0])
    surface = pygame.Surface((cols * pixel_size, rows * pixel_size))
    surface.set_colorkey((0, 0, 0))  # Background color for transparency
    surface.fill((0, 0, 0))

    for r, row in enumerate(bitmap):
        for c, char in enumerate(row):
            if char == '1':
                pygame.draw.rect(surface, color, (c * pixel_size, r * pixel_size, pixel_size, pixel_size))

    # Scale up if needed
    if scale > 1:
        return pygame.transform.scale(surface, (surface.get_width() * scale, surface.get_height() * scale))
    return surface


# --- Bitmaps for Sprites ---
PLAYER_IMG = [
    "      11  11      ",
    "      11  11      ",
    "    1111  1111    ",
    "    1111  1111    ",
    "  111111  111111  ",
    "  111111  111111  ",
    "  1111111 1111111 ",
    "  1111111 1111111 ",
    "  111111111111111 ",
    "  1  111111111  1 ",
    "  1  1        1 1 ",
]

ENEMY_IMG = [
    "    11    11    ",
    "    11    11    ",
    "  11111  11111  ",
    "  11111  11111  ",
    "1111111111111111",
    "11 1111  1111 11",
    "111  111111  111",
    "11           11 ",
    "  1   1111   1  ",
]


# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Generate pixel art sprite
        self.image = create_sprite_surface(PLAYER_IMG, (50, 255, 50), 4, scale=2)
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - self.rect.width) // 2
        self.rect.y = SCREEN_HEIGHT - 60
        self.speed_x = 0
        self.mask_rect = self.rect.copy()  # For collision logic optimization

    def update(self):
        self.rect.x += self.speed_x
        # Keep player within screen bounds
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
        self.mask_rect = self.rect

    def shoot(self):
        # Spawn bullet at the "nose" of the ship
        return Bullet(self.rect.x + self.rect.width // 2, self.rect.y + 10, "up")


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = create_sprite_surface(ENEMY_IMG, color, 4, scale=2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask_rect = self.rect


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x - 2  # Center alignment
        self.rect.y = y
        self.direction = direction

    def update(self):
        if self.direction == "up":
            self.rect.y -= BULLET_SPEED
        else:
            self.rect.y += BULLET_SPEED


class Particle(pygame.sprite.Sprite):
    """Debris from explosions"""

    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(4, 10)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Random velocity
        self.vel_x = random.randint(-5, 5)
        self.vel_y = random.randint(-5, 5)
        self.timer = random.randint(10, 20)  # Lifespan in frames

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.timer -= 1
        if self.timer <= 0:
            self.kill()


class Star(pygame.sprite.Sprite):
    """Background stars"""

    def __init__(self):
        super().__init__()
        size = random.randint(1, 3)
        self.image = pygame.Surface((size, size))
        color_val = random.randint(50, 255)
        self.image.fill((color_val, color_val, color_val))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, SCREEN_WIDTH)


# --- Helper Functions ---

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


# --- Main Game Loop ---

def main():
    # Groups
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    # Create Background Stars
    for _ in range(50):
        star = Star()
        stars.add(star)
        all_sprites.add(star, layer=0)  # Layer 0 for background

    # Create Player
    player = Player()
    all_sprites.add(player)

    # Game Variables
    running = True
    game_over = False
    level = 1
    score = 0
    base_enemy_speed = ENEMY_BASE_SPEED

    # Movement logic variables
    enemy_move_direction = 1
    enemy_move_timer = 0
    enemy_move_delay = 10

    def spawn_enemies():
        nonlocal level, base_enemy_speed
        rows = 4
        cols = 8

        # Colors for rows (Classic Invaders colors)
        colors = [(255, 100, 100), (200, 200, 50), (200, 50, 200), (100, 255, 100)]

        for row in range(rows):
            for col in range(cols):
                # Scale speed with level
                current_color = colors[row % len(colors)]
                enemy = Enemy(100 + col * 70, 50 + row * 70, current_color)
                all_sprites.add(enemy)
                enemies.add(enemy)

        # Speed increases slightly every level
        base_enemy_speed = ENEMY_BASE_SPEED + (level * 0.2)

    spawn_enemies()

    while running:
        clock.tick(60)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -PLAYER_SPEED
                elif event.key == pygame.K_RIGHT:
                    player.speed_x = PLAYER_SPEED
                elif event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                elif event.key == pygame.K_r and game_over:
                    main()  # Restart game completely
                    return

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.speed_x = 0

        if not game_over:
            # --- Game Logic ---

            # 1. Update Player
            player.update()

            # 2. Update Bullets
            bullets.update()
            for bullet in bullets:
                if bullet.rect.y < 0 or bullet.rect.y > SCREEN_HEIGHT:
                    bullet.kill()

            # 3. Update Particles
            particles.update()

            # 4. Enemy Movement Logic
            enemy_move_timer += 1
            if enemy_move_timer > enemy_move_delay:
                enemy_move_timer = 0
                move_down = False

                # Check wall collision
                for enemy in enemies:
                    if (enemy.rect.x + enemy.rect.width >= SCREEN_WIDTH and enemy_move_direction == 1) or \
                            (enemy.rect.x <= 0 and enemy_move_direction == -1):
                        move_down = True
                        break

                if move_down:
                    enemy_move_direction *= -1
                    for enemy in enemies:
                        enemy.rect.y += ENEMY_DROP_SPEED
                        if enemy.rect.y >= player.rect.y:
                            game_over = True
                else:
                    for enemy in enemies:
                        enemy.rect.x += (base_enemy_speed * enemy_move_direction)

            # 5. Enemy Shooting Logic
            # Chance increases slightly based on level
            shoot_chance = 100 - (level * 5)
            if shoot_chance < 20: shoot_change = 20  # Cap max speed

            if len(enemies) > 0 and random.randint(0, shoot_chance) == 0:
                target = random.choice(enemies.sprites())
                b = Bullet(target.rect.x + target.rect.width // 2, target.rect.y + target.rect.height, "down")
                all_sprites.add(b)
                bullets.add(b)

            # 6. Collision Detection

            # Player hits Enemy
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit_enemy, hit_bullets in hits.items():
                # Spawn explosion
                for _ in range(8):  # 8 particles per hit
                    p = Particle(hit_enemy.rect.center[0], hit_enemy.rect.center[1], (255, 50, 50))
                    particles.add(p)
                    all_sprites.add(p)
                score += 20

            # Enemy hits Player
            enemy_bullets = [b for b in bullets if b.direction == "down"]
            hits_player = pygame.sprite.spritecollide(player, enemy_bullets, False)
            if hits_player:
                # Spawn explosion for player death
                for _ in range(20):
                    p = Particle(player.rect.center[0], player.rect.center[1], (50, 255, 50))
                    particles.add(p)
                    all_sprites.add(p)
                game_over = True

            # Check Level Clear
            if len(enemies) == 0:
                level += 1
                # Heal player or reset? Just spawn new wave
                spawn_enemies()
                # Clear bullets to prevent cheap shots
                for b in bullets: b.kill()

        # --- Drawing ---
        # Apply screen shake if game over (explosion shake)
        shake_x = 0
        shake_y = 0
        if game_over and score != "YOU WIN!":
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-3, 3)

        # Draw Background
        screen.fill(BG_COLOR)

        # Draw Sprites (Stars, Enemies, Player, Bullets, Particles)
        # We need to draw in specific order. Pygame group draw handles this by group order if we used OrderedUpdates,
        # but here we just use one group.
        # To ensure stars are behind, let's redraw stars or just rely on them being added first (layer=0 logic is internal to custom classes usually).
        # Simplest way: clear screen, draw stars, draw others.

        # Actually, since we add stars to all_sprites, they are drawn with it.
        # But we want stars in background.
        # Hack: Draw stars manually first
        for s in stars:
            screen.blit(s.image, s.rect)

        for sprite in all_sprites:
            if not isinstance(sprite, Star):  # Don't draw stars twice
                # Apply shake offset
                rect = sprite.rect
                screen.blit(sprite.image, (rect.x + shake_x, rect.y + shake_y))

        # Draw UI
        ui_font = pygame.font.Font(None, 40)
        draw_text(f"LEVEL: {level}", ui_font, (255, 200, 100), screen, 700, 30)
        draw_text(f"SCORE: {score}", ui_font, TEXT_COLOR, screen, 100, 30)

        if game_over:
            if score == "YOU WIN!":
                msg = "YOU WIN! Press R to Restart"
            else:
                msg = "GAME OVER! Press R to Restart"

            # Draw box behind text
            s = pygame.Surface((400, 100))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            screen.blit(s, (200, 250))

            draw_text(msg, font, (255, 255, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
