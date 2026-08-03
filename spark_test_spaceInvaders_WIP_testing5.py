# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --temp 0.6 --top_p 0.95 --top_k 20 --min_p 0.0 --repeat-penalty 1.0 --presence-penalty 0.0  --spec-type draft-mtp --spec-draft-n-max 4 --model /AI/models/Qwen3.6-27B-uncensored-heretic-v2-Native-MTP-Preserved-NVFP4-MLP-Only-Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import math
import random
import json
import os
import sys
import struct  # Added for robust sound buffer creation

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (40, 40, 40)
DARK_GRAY = (20, 20, 20)
YELLOW = (255, 215, 0)

# Game Settings
PLAYER_SPEED = 7
BULLET_SPEED = 10
ALIEN_BULLET_SPEED = 5
INITIAL_ALIEN_SPEED = 1
ALIEN_DROP_DISTANCE = 20
BARRIER_COUNT = 3


# --- Sound Generator (Synthesizer) ---
class SoundGenerator:
    """Generates simple sounds using Pygame's sound module."""

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}

    def generate_sound(self, frequency, duration, sound_type='square', sample_rate=44100):
        """Creates a raw sound data buffer using struct for reliability."""
        try:
            num_samples = int(duration * sample_rate)
            if num_samples < 1:
                return None

            samples = []
            if sound_type == 'sine':
                # Simple sine wave
                for i in range(num_samples):
                    val = math.sin(2 * math.pi * frequency * i / sample_rate)
                    samples.append(int(32767 * val))
            else:
                # Square wave (more retro arcade feel)
                for i in range(num_samples):
                    # Simple square wave: high for first half, low for second
                    if i < num_samples // 2:
                        samples.append(32767)
                    else:
                        samples.append(-32767)

            # Pack samples into little-endian signed short format ('<h')
            # This avoids issues with platform-endianness differences
            sound_data = struct.pack(f'<{num_samples}h', *samples)

            sound = pygame.mixer.Sound(buffer=sound_data)
            return sound
        except Exception as e:
            # Debug print if sound fails
            print(f"Sound generation error: {e}")
            return None

    def load_all_sounds(self):
        # Player Shoot
        self.sounds['player_shoot'] = self.generate_sound(800, 0.1, 'square')
        # Alien Shoot
        self.sounds['alien_shoot'] = self.generate_sound(200, 0.15, 'square')
        # Explosion
        self.sounds['explosion'] = self.generate_sound(150, 0.2, 'square')
        # Bonus Enemy
        self.sounds['bonus'] = self.generate_sound(1200, 0.05, 'sine')
        # Game Over / Level Complete
        self.sounds['level_up'] = self.generate_sound(400, 0.5, 'sine')
        self.sounds['game_over'] = self.generate_sound(100, 1.0, 'square')

    def play(self, name):
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()


# --- Classes ---

class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.blocks = []
        self.create_blocks()

    def create_blocks(self):
        # Create a pixelated barrier shape (U-shape)
        # We divide the barrier into small 4x4 blocks
        rows = 10
        cols = 15
        for r in range(rows):
            for c in range(cols):
                # Create U shape
                if ((r < 6 and c >= 3 and c <= 11) or
                        (r >= 4 and c < 3) or
                        (r >= 4 and c > 11)):
                    block_x = self.x + c * 4
                    block_y = self.y + r * 4
                    self.blocks.append([block_x, block_y, 4, 4])

    def draw(self, screen):
        for block in self.blocks:
            pygame.draw.rect(screen, GREEN, block)

    def hit(self, bullet_x, bullet_y, bullet_width, bullet_height):
        """Check if bullet hits any block in this barrier."""
        for i, block in enumerate(self.blocks):
            bx, by, bw, bh = block
            if (bullet_x < bx + bw and
                    bullet_x + bullet_width > bx and
                    bullet_y < by + bh and
                    bullet_y + bullet_height > by):
                return i
        return -1

    def remove_block(self, index):
        if 0 <= index < len(self.blocks):
            self.blocks.pop(index)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True
        self.cooldown = 0

    def update(self, keys, sound_gen):
        if not self.alive:
            return None

        if self.cooldown > 0:
            self.cooldown -= 1

        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

        self.rect.x = self.x
        self.rect.y = self.y

        # Shooting
        if keys[pygame.K_SPACE] and self.cooldown <= 0:
            bullet = Bullet(self.x + self.width // 2 - 2, self.y, -BULLET_SPEED, WHITE, is_player=True)
            self.cooldown = 15  # Frames cooldown
            return bullet
        return None

    def draw(self, screen):
        if self.alive:
            # Draw a retro spaceship shape
            pygame.draw.rect(screen, CYAN, (self.x + 5, self.y + 5, 30, 15))
            pygame.draw.rect(screen, CYAN, (self.x + 15, self.y - 10, 10, 15))
            pygame.draw.rect(screen, WHITE, (self.x + 18, self.y - 15, 4, 5))

    def hit(self):
        self.alive = False


class Alien:
    def __init__(self, x, y, type_id=0):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True
        self.type_id = type_id  # 0: standard, 1: bonus
        self.color = MAGENTA if type_id == 1 else WHITE

    def draw(self, screen):
        if not self.alive:
            return

        if self.type_id == 1:
            # Bonus Ufo
            pygame.draw.ellipse(screen, YELLOW, (self.x, self.y + 5, self.width, 10))
            pygame.draw.rect(screen, YELLOW, (self.x + 5, self.y, 20, 5))
        else:
            # Standard Invader (Pixel art style via rects)
            pygame.draw.rect(screen, self.color, (self.x + 5, self.y, 20, 15))
            pygame.draw.rect(screen, self.color, (self.x, self.y + 5, 5, 10))
            pygame.draw.rect(screen, self.color, (self.x + 25, self.y + 5, 5, 10))
            # Eyes
            pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 5, 5, 5))
            pygame.draw.rect(screen, BLACK, (self.x + 17, self.y + 5, 5, 5))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y

    def shoot(self, sound_gen):
        if random.random() < 0.005:  # Increased chance slightly
            bullet = Bullet(self.x + self.width // 2 - 2, self.y + self.height, ALIEN_BULLET_SPEED, RED,
                            is_player=False)
            sound_gen.play('alien_shoot')
            return bullet
        return None


class BonusAlien:
    def __init__(self):
        self.x = 0
        self.y = 50
        self.width = 40
        self.height = 20
        self.speed_x = 3
        self.active = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.points = random.choice([50, 100, 150])
        self.color = YELLOW

    def update(self, sound_gen):
        if not self.active:
            # Spawn chance
            if random.random() < 0.001:  # Rare appearance
                self.active = True
                self.x = 0
                self.y = 50
                self.points = random.choice([50, 100, 150])
                return None

        if self.active:
            self.x += self.speed_x
            self.rect.x = self.x

            if self.x > SCREEN_WIDTH:
                self.active = False
                return None

            # Shoot randomly
            if random.random() < 0.02:
                bullet = Bullet(self.x + self.width // 2 - 2, self.y + self.height, ALIEN_BULLET_SPEED, YELLOW,
                                is_player=False)
                sound_gen.play('alien_shoot')  # Reuse alien sound
                return bullet
            return None

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Simple Ufo details
            pygame.draw.ellipse(screen, WHITE, (self.x + 10, self.y + 5, 20, 10))

    def hit(self, bullet):
        if self.active and bullet.rect.colliderect(self.rect):
            self.active = False
            return True, self.points
        return False, 0


class Bullet:
    def __init__(self, x, y, speed, color, is_player=True):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = speed
        self.color = color
        self.is_player = is_player
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.alive = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


# --- Main Game Class ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Python Edition")
        self.clock = pygame.time.Clock()

        self.sound_gen = SoundGenerator()
        self.sound_gen.load_all_sounds()

        self.font = pygame.font.SysFont("comicsansms", 30)
        self.big_font = pygame.font.SysFont("comicsansms", 60)

        self.load_stats()

        self.reset_game()

        self.running = True
        self.game_over = False
        self.level_complete = False

    def reset_game(self):
        self.score = 0
        self.high_score = self.stats.get('high_score', 0)
        self.level = 1
        self.alien_speed = INITIAL_ALIEN_SPEED
        self.alien_dx = 1
        self.bullets = []
        self.aliens = []
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
        self.barriers = []
        self.bonus_alien = BonusAlien()
        self.create_barriers()
        self.create_aliens()
        self.level_complete = False
        self.game_over = False

    def create_barriers(self):
        self.barriers = []
        spacing = SCREEN_WIDTH // (BARRIER_COUNT + 1)
        for i in range(BARRIER_COUNT):
            x = spacing * (i + 1) - 30
            y = SCREEN_HEIGHT - 120
            self.barriers.append(Barrier(x, y))

    def create_aliens(self):
        self.aliens = []
        rows = 4 + min(self.level, 3)  # Increase rows with level
        cols = 8
        start_x = 50
        start_y = 50

        for r in range(rows):
            for c in range(cols):
                alien_type = 0
                # Bonus alien row at top
                if r == 0:
                    alien_type = 1

                alien = Alien(start_x + c * 50, start_y + r * 40, alien_type)
                self.aliens.append(alien)

    def load_stats(self):
        file_path = 'invaders_stats.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    self.stats = json.load(f)
                except json.JSONDecodeError:
                    self.stats = {'high_score': 0}
        else:
            self.stats = {'high_score': 0}

    def save_stats(self):
        file_path = 'invaders_stats.json'
        with open(file_path, 'w') as f:
            json.dump(self.stats, f)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_p and self.level_complete:
                    self.next_level()

    def update(self):
        if self.game_over or self.level_complete:
            return

        keys = pygame.key.get_pressed()

        # Player Logic
        bullet = self.player.update(keys, self.sound_gen)
        if bullet:
            self.bullets.append(bullet)

        if self.player.alive:
            # Collision: Player bullet vs Aliens
            for bullet in self.bullets[:]:
                if bullet.is_player and bullet.alive:
                    for alien in self.aliens[:]:
                        if alien.alive and bullet.rect.colliderect(alien.rect):
                            alien.alive = False
                            bullet.alive = False
                            self.sound_gen.play('explosion')
                            if alien.type_id == 1:
                                self.score += 100
                            else:
                                self.score += 10
                            break
                        elif bullet.rect.colliderect(alien.rect):
                            bullet.alive = False
                            break

                    # Collision: Player bullet vs Bonus Alien
                    hit, points = self.bonus_alien.hit(bullet)
                    if hit:
                        bullet.alive = False
                        self.sound_gen.play('bonus')
                        self.score += points

                    # Collision: Player bullet vs Barriers
                    for barrier in self.barriers:
                        idx = barrier.hit(bullet.x, bullet.y, bullet.width, bullet.height)
                        if idx != -1:
                            barrier.remove_block(idx)
                            bullet.alive = False
                            break

        # Aliens Logic
        move_down = False
        alive_aliens = [a for a in self.aliens if a.alive]

        if not alive_aliens:
            self.next_level()
            return

        # Determine direction and edge hit
        min_x = min(a.x for a in alive_aliens)
        max_x = max(a.x + a.width for a in alive_aliens)

        # FIX: Reset alien position when hitting edges
        if max_x >= SCREEN_WIDTH - 10:
            self.alien_dx = -1
            move_down = True
            # Reset all aliens to start from the right edge
            for alien in alive_aliens:
                alien.x = SCREEN_WIDTH - 10 - alien.width
                alien.move(0, 0)  # Update rect

        elif min_x <= 10:
            self.alien_dx = 1
            move_down = True
            # Reset all aliens to start from the left edge
            for alien in alive_aliens:
                alien.x = 10
                alien.move(0, 0)  # Update rect

        for alien in alive_aliens:
            if move_down:
                alien.move(0, ALIEN_DROP_DISTANCE)
            else:
                alien.move(self.alien_dx * self.alien_speed, 0)

            # Alien Bullet
            alien_bullet = alien.shoot(self.sound_gen)
            if alien_bullet:
                self.bullets.append(alien_bullet)

            # Game Over if aliens reach player
            if alien.y + alien.height >= self.player.y - 10:  # -10 buffer
                self.game_over = True
                self.sound_gen.play('game_over')

        # Update Bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.alive:
                self.bullets.remove(bullet)
                continue

            # Alien bullet vs Player
            if not bullet.is_player and self.player.alive:
                if bullet.rect.colliderect(self.player.rect):
                    self.player.hit()
                    self.sound_gen.play('explosion')
                    self.game_over = True

            # Alien bullet vs Barriers
            for barrier in self.barriers:
                idx = barrier.hit(bullet.x, bullet.y, bullet.width, bullet.height)
                if idx != -1:
                    barrier.remove_block(idx)
                    bullet.alive = False
                    break

            # Player bullet vs Barriers (handled in player logic above)

        # Bonus Alien Update
        bonus_bullet = self.bonus_alien.update(self.sound_gen)
        if bonus_bullet:
            self.bullets.append(bonus_bullet)

    def next_level(self):
        self.level += 1
        self.bullets.clear()
        self.aliens.clear()
        self.player.alive = True
        self.player.x = SCREEN_WIDTH // 2 - 20
        self.player.y = SCREEN_HEIGHT - 50
        self.alien_speed = INITIAL_ALIEN_SPEED + (self.level * 0.5)
        self.alien_dx = 1
        self.create_aliens()

        # Restore barriers partially
        spacing = SCREEN_WIDTH // (BARRIER_COUNT + 1)
        for i, barrier in enumerate(self.barriers):
            # Update x FIRST
            barrier.x = spacing * (i + 1) - 30
            barrier.y = SCREEN_HEIGHT - 120
            # THEN create blocks
            barrier.create_blocks()

        self.sound_gen.play('level_up')
        self.level_complete = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 40))

        high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        self.screen.blit(high_score_text, (SCREEN_WIDTH - 200, 10))

        # Draw Entities
        if self.player.alive:
            self.player.draw(self.screen)

        for alien in self.aliens:
            alien.draw(self.screen)

        self.bonus_alien.draw(self.screen)

        for barrier in self.barriers:
            barrier.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Overlays
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.big_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

            if self.score > self.high_score:
                self.high_score = self.score
                self.stats['high_score'] = self.high_score
                self.save_stats()
                msg_text = self.font.render("NEW HIGH SCORE!", True, YELLOW)
                self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        if self.level_complete:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            level_text = self.big_font.render(f"LEVEL {self.level} COMPLETE", True, GREEN)
            next_text = self.font.render("Press 'P' for Next Level", True, WHITE)
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
