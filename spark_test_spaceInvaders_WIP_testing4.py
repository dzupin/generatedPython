# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic or for sound). Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that new enhancements are visually appealing and  noticeable to end user. Introduce more rewards and bonuses and significantly improve game mechanics for end user to enjoy a game.   Like before, don't use any external game assets files  in your enhancements. Use original game as a guide and feel free to complete change original code if your deem it necessary.  Provide complete updated code.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0  --port 5000 -fa 1 --model /AI/models/gemma-4-31b-it-heretic-ara.i1-Q6_K.gguf  --mmproj /AI/models/gemma-4-31b-mmproj-F32.gguf#

import pygame
import random
import math
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
PURPLE = (160, 32, 240)

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = -7
ALIEN_BULLET_SPEED = 4
ALIEN_SPEED_START = 1
ALIEN_DROP = 10

# --- Sound Generator ---
# Since we can't use external files, we generate waveforms using numpy
pygame.mixer.init(frequency=22050, size=-16, channels=2)


def generate_sound(freq, duration=0.1, type='sine'):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)

    if type == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif type == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif type == 'noise':
        wave = np.random.uniform(-1, 1, n_samples)

    # Fade out to avoid clicking
    fade = np.linspace(1, 0, n_samples)
    wave = (wave * fade * 32767).astype(np.int16)

    # Create stereo sound
    stereo_wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo_wave)


# Pre-generate sounds
SOUND_SHOOT = generate_sound(440, 0.05, 'square')
SOUND_EXPLODE = generate_sound(100, 0.2, 'noise')
SOUND_BONUS = generate_sound(880, 0.1, 'sine')
SOUND_LEVEL_UP = generate_sound(660, 0.3, 'sine')


# --- Game Objects ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(0, 20), (20, 0), (40, 20)])
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, alien_type):
        super().__init__()
        self.type = alien_type
        self.image = pygame.Surface((30, 20), pygame.SRCALPHA)
        color = RED if alien_type == 1 else PURPLE if alien_type == 2 else BLUE
        # Draw a simple alien shape
        pygame.draw.rect(self.image, color, [5, 5, 20, 10])
        pygame.draw.rect(self.image, color, [0, 0, 5, 5])
        pygame.draw.rect(self.image, color, [25, 0, 5, 5])

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
        # Draw a "blocky" shield
        pygame.draw.rect(self.image, GREEN, [0, 0, 60, 40], border_radius=5)
        pygame.draw.rect(self.image, BLACK, [20, 10, 20, 20])  # cutout
        self.rect = self.image.get_rect(topleft=(x, y))


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += 3
        if self.rect.top > HEIGHT:
            self.kill()


# --- Main Game Class ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cyber Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.reset_game()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.setup_level()

    def setup_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        # Create Aliens
        rows = 5
        cols = 8
        for r in range(rows):
            for c in range(cols):
                a_type = 3 if r == 0 else (2 if r < 3 else 1)
                alien = Alien(100 + c * 60, 50 + r * 40, a_type)
                self.aliens.add(alien)
                self.all_sprites.add(alien)

        # Create Barriers
        for b in range(4):
            barrier = Barrier(100 + b * 160, 450)
            self.barriers.add(barrier)
            self.all_sprites.add(barrier)

        self.alien_direction = 1
        self.alien_speed = ALIEN_SPEED_START + (self.level * 0.5)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    bullet = Bullet(self.player.rect.centerx, self.player.rect.top, BULLET_SPEED, WHITE)
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    SOUND_SHOOT.play()
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.bullets.update()
        self.alien_bullets.update()
        self.bonuses.update()

        # Alien Movement
        move_down = False
        for alien in self.aliens:
            if alien.rect.right >= WIDTH or alien.rect.left <= 0:
                move_down = True
                break

        if move_down:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.rect.y += ALIEN_DROP

        for alien in self.aliens:
            alien.update(self.alien_speed * self.alien_direction, 0)

        # Alien Shooting
        if random.random() < 0.02 + (self.level * 0.005):
            shooter = random.choice(self.aliens.sprites())
            ab = Bullet(shooter.rect.centerx, shooter.rect.bottom, ALIEN_BULLET_SPEED, RED)
            self.alien_bullets.add(ab)
            self.all_sprites.add(ab)

        # Collisions: Player Bullets -> Aliens
        hits = pygame.sprite.groupcollide(self.aliens, self.bullets, True, True)
        for hit in hits:
            self.score += 10 * self.level
            SOUND_EXPLODE.play()
            if random.random() < 0.1:  # 10% chance for bonus
                bonus = Bonus(hit.rect.centerx, hit.rect.centery)
                self.bonuses.add(bonus)
                self.all_sprites.add(bonus)

        # Collisions: Alien Bullets -> Player
        if pygame.sprite.spritecollide(self.player, self.alien_bullets, True):
            self.lives -= 1
            SOUND_EXPLODE.play()
            if self.lives <= 0:
                self.game_over = True

        # Collisions: Any Bullet -> Barrier
        pygame.sprite.groupcollide(self.barriers, self.bullets, False, True)
        pygame.sprite.groupcollide(self.barriers, self.alien_bullets, False, True)

        # Collisions: Player -> Bonus
        bonus_hits = pygame.sprite.spritecollide(self.player, self.bonuses, True)
        for bh in bonus_hits:
            self.lives += 1
            SOUND_BONUS.play()

        # Check Level Clear
        if not self.aliens:
            self.level += 1
            SOUND_LEVEL_UP.play()
            self.setup_level()

        # Check Game Over (Aliens reach bottom)
        for alien in self.aliens:
            if alien.rect.bottom >= self.player.rect.top:
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw starfield (static for performance, but looks nice)
        for i in range(20):
            pygame.draw.circle(self.screen, WHITE, ((i * 137) % WIDTH, (i * 257) % HEIGHT), 1)

        self.all_sprites.draw(self.screen)

        # UI
        score_txt = self.font.render(f"Score: {self.score}  Level: {self.level}  Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_txt, (10, 10))

        if self.game_over:
            over_txt = self.font.render("GAME OVER! Press 'R' to Restart", True, RED)
            self.screen.blit(over_txt, (WIDTH // 2 - 150, HEIGHT // 2))

        pygame.display.flip()

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
