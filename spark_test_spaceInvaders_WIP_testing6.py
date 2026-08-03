# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/Qwen3.6-27B-MTP-UD-Q8_K_XL.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import sys
import random
import math
import os
import struct
import array

# --- CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game Constants
PLAYER_SPEED = 7
BULLET_SPEED = 10
ENEMY_SPEED_BASE = 1  # Speed increases per level
ENEMY_DROP_DISTANCE = 20
BARRIER_SIZE = 40  # Size of a block in a barrier


# --- SOUND GENERATION (PROCEDURAL & ROBUST) ---
class SoundManager:
    def __init__(self):
        # Initialize mixer with specific settings to ensure compatibility
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sfx = {}
        self.generate_sfx()

    def generate_sine_wave(self, freq, duration_seconds):
        """
        Generates a sine wave buffer as a bytearray.
        Args:
            freq: Frequency in Hz
            duration_seconds: Duration of the sound
        Returns:
            bytearray of PCM data
        """
        sample_rate = 44100
        num_samples = int(sample_rate * duration_seconds)
        # Create an array of floats for precision
        samples = array.array('f', [0.0] * num_samples)

        for i in range(num_samples):
            # Apply a simple envelope: attack and decay to avoid clicking
            # Attack: first 10%
            if i < num_samples * 0.1:
                envelope = i / (num_samples * 0.1)
            # Decay: last 10%
            elif i > num_samples * 0.9:
                envelope = (num_samples - i) / (num_samples * 0.1)
            else:
                envelope = 1.0

            # Sine wave formula
            t = i / sample_rate
            sample_val = math.sin(2 * math.pi * freq * t) * envelope

            # Clamp to [-1.0, 1.0]
            if sample_val > 1.0: sample_val = 1.0
            if sample_val < -1.0: sample_val = -1.0

            samples[i] = sample_val

        # Convert float array to 16-bit integer PCM data
        # Pygame mixer expects signed 16-bit integers
        pcm_data = array.array('h', [int(x * 32767) for x in samples])

        # Convert to bytes (little-endian)
        # struct.pack('<h', val) packs a short integer
        byte_data = b''.join([struct.pack('<h', s) for s in pcm_data])

        return byte_data

    def generate_sfx(self):
        try:
            # Player Shoot: High pitch short blip (800Hz, 0.1s)
            self.sfx['shoot'] = pygame.mixer.Sound(buffer=self.generate_sine_wave(800, 0.1))

            # Enemy Hit: Lower pitch, slightly longer (150Hz, 0.15s)
            self.sfx['enemy_explosion'] = pygame.mixer.Sound(buffer=self.generate_sine_wave(150, 0.15))

            # Player Hit: Low buzz (100Hz, 0.3s)
            self.sfx['player_hit'] = pygame.mixer.Sound(buffer=self.generate_sine_wave(100, 0.3))

            # Mystery Ship: Higher, distinct hum (400Hz, 0.2s)
            self.sfx['mystery'] = pygame.mixer.Sound(buffer=self.generate_sine_wave(400, 0.2))

            # Level Up: Ascending tones (played manually in game logic usually, but we can just use a generic one)
            self.sfx['level_up'] = pygame.mixer.Sound(buffer=self.generate_sine_wave(600, 0.2))

        except Exception as e:
            print(f"Warning: Could not initialize sound effects. {e}")
            self.sfx = {}

    def play(self, key):
        if self.sfx and key in self.sfx:
            try:
                self.sfx[key].play()
            except:
                pass


# --- GRAPHICS (PROCEDURAL DRAWING) ---
class GraphicsManager:
    """Handles drawing pixel-art style shapes using primitives"""

    @staticmethod
    def draw_invader(screen, x, y, type_idx, size=30):
        color = WHITE
        if type_idx == 0:
            color = YELLOW  # Top
        elif type_idx == 1:
            color = WHITE  # Middle
        elif type_idx == 2:
            color = RED  # Bottom

        # Simple pixel art representation using rectangles
        s = size // 5
        pygame.draw.rect(screen, color, (x, y, size, s * 3))  # Top bar
        pygame.draw.rect(screen, color, (x, y + s * 3, s, s * 2))  # Left leg
        pygame.draw.rect(screen, color, (x + size - s, y + s * 3, s, s * 2))  # Right leg
        pygame.draw.rect(screen, BLACK, (x + s, y + s, s * 2, s))  # Eye

    @staticmethod
    def draw_ufo(screen, x, y):
        pygame.draw.ellipse(screen, GREEN, (x, y + 10, 40, 10))
        pygame.draw.ellipse(screen, YELLOW, (x + 10, y, 20, 20))

    @staticmethod
    def draw_player(screen, x, y):
        pygame.draw.rect(screen, GREEN, (x + 10, y, 20, 20))  # Body
        pygame.draw.rect(screen, GREEN, (x + 20, y - 10, 10, 10))  # Turret


# --- CLASSES ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(BLACK)
        # Draw ship
        pygame.draw.polygon(self.image, GREEN,
                            [(10, 30), (30, 30), (40, 30), (40, 10), (30, 0), (10, 0), (0, 10), (0, 30)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = PLAYER_SPEED
        self.lives = 3

    def update(self, input_keys):
        if input_keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if input_keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.direction = direction  # 1 = down (enemy), -1 = up (player)

    def update(self):
        self.rect.y += BULLET_SPEED * self.direction
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type_idx):
        super().__init__()
        self.image = pygame.Surface((30, 20))
        self.image.fill(BLACK)
        self.type_idx = type_idx
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        GraphicsManager.draw_invader(screen, self.rect.x, self.rect.y, self.type_idx)

    def update(self, direction, speed):
        self.rect.x += direction * speed


class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Barriers are made of small blocks
        self.image = pygame.Surface((120, 40))  # 3 blocks wide, 1 high
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # We simulate damage by keeping a list of "pixels" or sub-rects that still exist
        # For optimization, we treat it as 3x3 grid of 13x13 blocks roughly
        self.blocks = []
        for row in range(3):
            for col in range(9):
                if row == 0 and (col == 4): continue  # Create the arch gap
                self.blocks.append(pygame.Rect(x + col * 13, y + row * 13, 13, 13))

    def draw(self, screen):
        for b in self.blocks:
            pygame.draw.rect(screen, GREEN, b)

    def update(self, bullets, enemy_bullets):
        # Check collision with Player Bullets
        for bullet in bullets:
            for b in self.blocks[:]:
                if b.colliderect(bullet.rect):
                    self.blocks.remove(b)
                    bullet.kill()
                    break

        # Check collision with Enemy Bullets
        for bullet in enemy_bullets:
            for b in self.blocks[:]:
                if b.colliderect(bullet.rect):
                    self.blocks.remove(b)
                    bullet.kill()
                    break

        # If no blocks left, kill sprite
        if not self.blocks:
            self.kill()


class MysteryShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 20))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = -50
        self.rect.y = 50
        self.speed = 3
        self.direction = 1
        self.active = False

    def start(self):
        if random.randint(0, 100) > 90:  # 10% chance every check
            if not self.active:
                self.active = True
                self.rect.x = -50 if random.randint(0, 1) else SCREEN_WIDTH + 50
                self.direction = 1 if self.rect.x < 0 else -1
                SoundManager().play('mystery')

    def draw(self, screen):
        if self.active:
            GraphicsManager.draw_ufo(screen, self.rect.x, self.rect.y)

    def update(self):
        if self.active:
            self.rect.x += self.speed * self.direction
            if (self.rect.x > SCREEN_WIDTH + 50) or (self.rect.x < -50):
                self.active = False


# --- MAIN GAME ENGINE ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 25)
        self.sfx_mgr = SoundManager()

        self.reset_game()

        # Load High Score
        self.high_score = self.load_highscore()

    def load_highscore(self):
        if os.path.exists("highscores.txt"):
            with open("highscores.txt", "r") as f:
                try:
                    return int(f.read().strip())
                except:
                    return 0
        return 0

    def save_highscore(self):
        with open("highscores.txt", "w") as f:
            f.write(str(self.high_score))

    def reset_game(self):
        self.player = Player()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.mystery = MysteryShip()

        self.level = 1
        self.score = 0
        self.state = "START"  # START, PLAY, GAMEOVER, LEVEL_TRANSITION

        self.enemy_dir = 1
        self.enemy_move_timer = 0

        self.spawn_level()

    def spawn_level(self):
        self.enemies.empty()
        self.enemy_bullets.empty()

        # Difficulty scaling
        self.enemy_speed = ENEMY_SPEED_BASE + (self.level * 0.2)

        rows = 5
        cols = 11

        for r in range(rows):
            for c in range(cols):
                enemy = Enemy(50 + c * 45, 50 + r * 30, r // 2)
                self.enemies.add(enemy)

        # Spawn Barriers only on Level 1 or if destroyed
        if self.level == 1 or not self.barriers:
            self.barriers.empty()
            for i in range(4):
                self.barriers.add(Barrier(100 + i * 180, SCREEN_HEIGHT - 100))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.state == "PLAY":
            self.player.update(keys)
            if keys[pygame.K_SPACE] and not self.last_shoot or (pygame.time.get_ticks() - self.last_shoot > 250):
                self.bullets.add(Bullet(self.player.rect.centerx, self.player.rect.top, -1))
                self.sfx_mgr.play('shoot')
                self.last_shoot = pygame.time.get_ticks()
        elif self.state == "START":
            if keys[pygame.K_RETURN]:
                self.state = "PLAY"
                # Don't reset game entirely, just start playing from current state if needed,
                # but here we reset to ensure clean start if coming from Game Over
                if self.score > 0 or self.level > 1:
                    # If restarting from game over, we want fresh start
                    self.score = 0
                    self.level = 1
                    self.player.lives = 3
                    self.spawn_level()
                else:
                    # If starting fresh
                    pass
        elif self.state == "GAMEOVER":
            if keys[pygame.K_RETURN]:
                self.high_score = max(self.high_score, self.score)
                self.save_highscore()
                pygame.quit()
                sys.exit()

    def update_logic(self):
        if self.state != "PLAY":
            return

        # Mystery Ship
        self.mystery.update()
        if self.mystery.active:
            # Create a temporary group for collision check with mystery ship
            mystery_group = pygame.sprite.Group()
            mystery_group.add(self.mystery)
            if self.bullets:
                hits = pygame.sprite.groupcollide(self.bullets, mystery_group, True, False)
                if hits:
                    self.score += 300
                    self.mystery.active = False
                    self.sfx_mgr.play('enemy_explosion')

        # Barriers
        self.barriers.update(self.bullets, self.enemy_bullets)

        # Bullets
        self.bullets.update()
        self.enemy_bullets.update()

        # Player Bullets hitting Enemies
        for bullet in self.bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, True)
            if hit_enemies:
                bullet.kill()
                self.sfx_mgr.play('enemy_explosion')
                # Points based on row
                for enemy in hit_enemies:
                    if enemy.type_idx == 0:
                        self.score += 30
                    elif enemy.type_idx == 1:
                        self.score += 20
                    else:
                        self.score += 10

        # Enemy Shooting
        if self.enemies and random.randint(0, 100) < 5:  # 5% chance per frame (approx)
            shooter = random.choice(self.enemies)
            self.enemy_bullets.add(Bullet(shooter.rect.centerx, shooter.rect.bottom, 1, RED))

        # Enemy Bullets hitting Player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits:
            self.player.lives -= 1
            self.sfx_mgr.play('player_hit')
            if self.player.lives <= 0:
                self.state = "GAMEOVER"

        # Invasion check (Enemies touch player level)
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.state = "GAMEOVER"

        # Level Complete
        if len(self.enemies) == 0:
            self.level += 1
            self.spawn_level()
            self.sfx_mgr.play('level_up')

        # Enemy Movement (The "Invader" Shuffle)
        # We move them continuously but check bounds
        hit_edge = False
        for enemy in self.enemies:
            enemy.update(self.enemy_dir, self.enemy_speed)
            if enemy.rect.right >= SCREEN_WIDTH - 10 or enemy.rect.left <= 10:
                hit_edge = True

        if hit_edge:
            self.enemy_dir *= -1
            for enemy in self.enemies:
                enemy.rect.y += ENEMY_DROP_DISTANCE

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "PLAY":
            # Draw Barriers
            self.barriers.draw(self.screen)  # Custom draw loop in group or manual

            # Draw Player
            self.screen.blit(self.player.image, self.player.rect)

            # Draw Enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)

            # Draw Mystery
            self.mystery.draw(self.screen)

            # Draw Bullets
            for b in self.bullets:
                self.screen.blit(b.image, b.rect)
            for b in self.enemy_bullets:
                self.screen.blit(b.image, b.rect)

            # HUD
            text_score = self.font.render(f"Score: {self.score}", True, WHITE)
            text_level = self.font.render(f"Level: {self.level}", True, WHITE)
            text_lives = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
            self.screen.blit(text_score, (10, 10))
            self.screen.blit(text_level, (SCREEN_WIDTH // 2, 10))
            self.screen.blit(text_lives, (SCREEN_WIDTH - 100, 10))

        elif self.state == "START":
            title = pygame.font.SysFont("arial", 50).render("SPACE INVADERS", True, GREEN)
            sub = self.font.render("Press ENTER to Start", True, WHITE)
            hs = self.font.render(f"High Score: {self.high_score}", True, YELLOW)

            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 300))
            self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 350))

        elif self.state == "GAMEOVER":
            title = pygame.font.SysFont("arial", 50).render("GAME OVER", True, RED)
            score = self.font.render(f"Final Score: {self.score}", True, WHITE)
            msg = self.font.render("Press ENTER to Quit", True, WHITE)

            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
            self.screen.blit(score, (SCREEN_WIDTH // 2 - score.get_width() // 2, 300))
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 350))

        pygame.display.flip()

    def run(self):
        self.last_shoot = 0
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.high_score = max(self.high_score, self.score)
                    self.save_highscore()
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.update_logic()
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
