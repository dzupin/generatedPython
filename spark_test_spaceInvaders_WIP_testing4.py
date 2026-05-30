# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic or for sound). Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that new enhancements are visually appealing and  noticeable to end user. Introduce more rewards and bonuses and significantly improve game mechanics for end user to enjoy a game.   Like before, don't use any external game assets files  in your enhancements. Use original game as a guide and feel free to complete change original code if your deem it necessary.  Provide complete updated code.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0  --port 5000 -fa 1 --model /AI/models/gemma-4-31b-it-heretic-ara.i1-Q6_K.gguf  --mmproj /AI/models/gemma-4-31b-mmproj-F32.gguf#


import pygame
import random
import numpy as np

# --- Configuration & Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = -7
ENEMY_BULLET_SPEED = 4
BARRIER_COLOR = (0, 200, 0)


# --- Sound Generator ---
def generate_sound(freq, duration, volume=0.1, type='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)

    if type == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif type == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif type == 'noise':
        wave = np.random.uniform(-1, 1, n_samples)

    # Convert to 16-bit signed integers (Mono)
    audio = (wave * 32767 * volume).astype(np.int16)

    # FIX: Convert Mono to Stereo by duplicating the channel
    # This creates a 2D array where col 0 is Left and col 1 is Right
    stereo_audio = np.column_stack((audio, audio))

    return pygame.sndarray.make_sound(stereo_audio)


# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(0, 30), (25, 0), (50, 30)])
        pygame.draw.rect(self.image, GREEN, (20, 5, 10, 10))
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        color = YELLOW if y < 100 else PURPLE if y < 200 else RED
        pygame.draw.rect(self.image, color, (5, 5, 30, 20), border_radius=5)
        pygame.draw.rect(self.image, color, (10, 0, 10, 10))
        pygame.draw.rect(self.image, color, (20, 0, 10, 10))
        pygame.draw.circle(self.image, BLACK, (12, 15), 3)
        pygame.draw.circle(self.image, BLACK, (28, 15), 3)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.speed = 1 + (level * 0.2)

    def update(self, shift_down=False):
        if shift_down:
            self.rect.y += 10
        else:
            self.rect.x += self.direction * self.speed


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill(BARRIER_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))


class BonusShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, WHITE, (0, 0, 60, 20))
        pygame.draw.rect(self.image, WHITE, (20, -5, 20, 10))
        self.rect = self.image.get_rect(topleft=(-60, 50))
        self.speed = 3

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()


# --- Main Game Class ---

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Explicitly initialize mixer
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders - Procedural Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # Generate Sounds
        self.snd_shoot = generate_sound(440, 0.1, type='square')
        self.snd_exp = generate_sound(100, 0.2, type='noise')
        self.snd_bonus = generate_sound(880, 0.3, type='sine')

        self.reset_game()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.game_over = False
        self.setup_level()

    def setup_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        for row in range(5):
            for col in range(10):
                enemy = Enemy(100 + col * 60, 50 + row * 40, self.level)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

        for b_idx in range(4):
            bx = 100 + b_idx * 180
            by = 450
            for row in range(3):
                for col in range(5):
                    block = Barrier(bx + col * 15, by + row * 15)
                    self.barriers.add(block)
                    self.all_sprites.add(block)

        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

    def spawn_bonus(self):
        if random.random() < 0.005:
            bonus = BonusShip()
            self.bonuses.add(bonus)
            self.all_sprites.add(bonus)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_SPACE:
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top, BULLET_SPEED, GREEN)
                        self.player_bullets.add(bullet)
                        self.all_sprites.add(bullet)
                        self.snd_shoot.play()

            if not self.game_over:
                self.player.update(keys)
                self.spawn_bonus()
                self.bonuses.update()

                enemy_shift = False
                for enemy in self.enemies:
                    if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                        enemy_shift = True
                        break

                if enemy_shift:
                    for enemy in self.enemies:
                        enemy.direction *= -1
                        enemy.update(shift_down=True)

                self.enemies.update()
                self.player_bullets.update()
                self.enemy_bullets.update()

                if random.random() < 0.02 * (1 + self.level * 0.1):
                    if self.enemies:
                        shooter = random.choice(self.enemies.sprites())
                        eb = Bullet(shooter.rect.centerx, shooter.rect.bottom, ENEMY_BULLET_SPEED, RED)
                        self.enemy_bullets.add(eb)
                        self.all_sprites.add(eb)

                hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
                for hit in hits:
                    self.score += 10 * self.level
                    self.snd_exp.play()

                pygame.sprite.groupcollide(self.barriers, self.player_bullets, True, True)
                pygame.sprite.groupcollide(self.barriers, self.enemy_bullets, True, True)

                if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
                    self.game_over = True
                    self.snd_exp.play()

                bonus_hits = pygame.sprite.groupcollide(self.bonuses, self.player_bullets, True, True)
                for hit in bonus_hits:
                    self.score += 100 * self.level
                    self.snd_bonus.play()

                if not self.enemies:
                    self.level += 1
                    self.setup_level()

                for enemy in self.enemies:
                    if enemy.rect.bottom >= self.player.rect.top:
                        self.game_over = True

            self.screen.fill(BLACK)
            for star in self.stars:
                pygame.draw.circle(self.screen, WHITE, star, 1)
            self.all_sprites.draw(self.screen)

            score_text = self.font.render(f"Score: {self.score}  Level: {self.level}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            if self.game_over:
                go_text = self.font.render("GAME OVER! Press R to Restart", True, RED)
                self.screen.blit(go_text, (WIDTH // 2 - 150, HEIGHT // 2))
                if keys[pygame.K_r]:
                    self.reset_game()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
