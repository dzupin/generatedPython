
#/AI/llama.cpp/build/bin/llama-server --no-mmap --jinja --host 0.0.0.0 --port 5000 --ctx-size 65536  -fa 1  --model  /AI/models/stepfun-ai_Step-3.5-Flash-IQ4_XS-00001-of-00003.gguf

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (20, 20, 20)  # Dark grey background
PLAYER_COLOR = (0, 255, 0)  # Green
ENEMY_COLOR = (255, 0, 0)  # Red
TEXT_COLOR = (255, 255, 255)  # White

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_SPEED = 5

# Bullet settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 7

# Enemy settings
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_PRED_H_SPEED = 1  # Horizontal speed
ENEMY_VERT_SPEED = 30  # How far they drop down

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - Python Pygame")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


# --- Classes ---

class Player(pygame.sprite.Sprite):  # Fixed typo here
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
        self.rect.y = SCREEN_HEIGHT - 50
        self.speed_x = 0

    def update(self):
        self.rect.x += self.speed_x
        # Keep player within screen bounds
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - PLAYER_WIDTH:
            self.rect.x = SCREEN_WIDTH - PLAYER_WIDTH

    def shoot(self):
        return Bullet(self.rect.x + PLAYER_WIDTH // 2, self.rect.y, "up")


class Enemy(pygame.sprite.Sprite):  # Fixed typo here
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Bullet(pygame.sprite.Sprite):  # Fixed typo here
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(TEXT_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction  # "up" or "down"

    def update(self):
        if self.direction == "up":
            self.rect.y -= BULLET_SPEED
        else:
            self.rect.y += BULLET_SPEED


# --- Helper Functions ---

def draw_text(text, font, color, surface, x, y):
    # Fixed: Removed 'surface' from render() arguments.
    # render() returns a surface, it does not take the destination as an argument.
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

    # Create Player
    player = Player()
    all_sprites.add(player)

    # Create Grid of Enemies
    rows = 4
    cols = 8
    for row in range(rows):
        for col in range(cols):
            enemy = Enemy(100 + col * (ENEMY_WIDTH + 50), 50 + row * (ENEMY_HEIGHT + 50))
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Game Variables
    running = True
    game_over = False
    score = 0

    # Movement logic variables
    enemy_move_direction = 1  # 1 for right, -1 for left
    enemy_move_timer = 0
    enemy_move_delay = 10  # Frames to wait before moving enemies again (lower = faster)

    while running:
        clock.tick(60)  # 60 FPS

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
                    main()  # Restart game
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
            # Remove bullets that go off screen
            for bullet in bullets:
                if bullet.rect.y < 0 or bullet.rect.y > SCREEN_HEIGHT:
                    bullet.kill()

            # 3. Enemy Movement Logic
            enemy_move_timer += 1
            if enemy_move_timer > enemy_move_delay:
                enemy_move_timer = 0
                move_down = False

                # Check if any enemy hits the wall
                for enemy in enemies:
                    if (enemy.rect.x + ENEMY_WIDTH >= SCREEN_WIDTH and enemy_move_direction == 1) or \
                            (enemy.rect.x <= 0 and enemy_move_direction == -1):
                        move_down = True
                        break

                if move_down:
                    enemy_move_direction *= -1
                    for enemy in enemies:
                        enemy.rect.y += ENEMY_VERT_SPEED
                        # If enemy touches bottom, game over
                        if enemy.rect.y >= player.rect.y:
                            game_over = True
                else:
                    for enemy in enemies:
                        enemy.rect.x += (ENEMY_PRED_H_SPEED * enemy_move_direction)

            # 4. Enemy Shooting Logic (Random)
            if random.randint(0, 100) == 0:
                # Pick a random enemy to shoot
                # Ensure there are enemies left before picking one
                if len(enemies) > 0:
                    target = random.choice(enemies.sprites())
                    b = Bullet(target.rect.x + ENEMY_WIDTH // 2, target.rect.y + ENEMY_HEIGHT, "down")
                    all_sprites.add(b)
                    bullets.add(b)

            # 5. Collision Detection

            # Player Bullet hits Enemy
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                score += 10

            # Enemy Bullet hits Player
            # Filter bullets that are moving down
            enemy_bullets = [b for b in bullets if b.direction == "down"]
            hits_player = pygame.sprite.spritecollide(player, enemy_bullets, False)
            if hits_player:
                game_over = True

            # Check if all enemies are dead
            if len(enemies) == 0:
                game_over = True
                score = "YOU WIN!"

        # --- Drawing ---
        screen.fill(BG_COLOR)

        all_sprites.draw(screen)

        # Draw UI
        draw_text(f"Score: {score}", font, TEXT_COLOR, screen, 80, 20)

        if game_over:
            if score == "YOU WIN!":
                msg = "YOU WIN! Press R to Restart"
            else:
                msg = "GAME OVER! Press R to Restart"
            draw_text(msg, font, (255, 255, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
