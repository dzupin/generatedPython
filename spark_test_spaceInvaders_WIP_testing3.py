# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.



# --------------------------------------------------------------
# Space Invaders – All assets generated in‑code (no external files)
# --------------------------------------------------------------
import pygame
import sys
import random
import math
import json
import os
import tempfile
import datetime
from pathlib import Path

# ----------------------------------------------------------------------
# Initialize Pygame and core settings
# ----------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders – Generated Edition")
FPS = 60
clock = pygame.time.Clock()

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# ----------------------------------------------------------------------
# Sound generation utilities (pure‑Python tones)
# ----------------------------------------------------------------------
def generate_tone(frequency, duration_ms=200, volume=0.5):
    """Return a pygame Sound object containing a simple sine wave beep."""
    sample_rate = 44100
    frames = int(sample_rate * duration_ms / 1000.0)
    # Generate sine wave samples
    samples = [int(math.sin(2 * math.pi * frequency * t / sample_rate) * 32767) for t in range(frames)]
    # Convert to bytes (16‑bit signed)
    audio_bytes = bytes([b & 0xFF for b in samples] + [(b >> 8) & 0xFF for b in samples])
    sound = pygame.mixer.Sound(buffer=audio_bytes)
    sound.set_volume(volume)
    return sound

# Predefined sound effects (original, non‑copyrighted beeps)
SHOOT_SOUND = generate_tone(880, 100)          # A5 note
EXPLOSION_SOUND = generate_tone(220, 300, 0.7) # Low rumble
HIT_SOUND = generate_tone(660, 150)            # E5 note
BONUS_SOUND = generate_tone(1320, 200)         # High chirp
BACKGROUND_MUSIC = generate_tone(110, 500, 0.3) # Very low hum (looped)

# ----------------------------------------------------------------------
# Helper drawing functions
# ----------------------------------------------------------------------
def draw_text(surface, font, text, color, center):
    """Render centered text."""
    txt_surface = font.render(text, True, color)
    rect = txt_surface.get_rect(center=center)
    surface.blit(txt_surface, rect)

def draw_rect_outline(surface, color, rect, width=1):
    """Draw a rectangle with an outline."""
    pygame.draw.rect(surface, color, rect, width)

# ----------------------------------------------------------------------
# Game objects
# ----------------------------------------------------------------------
class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.lives = 3
        self.shield = False
        self.shield_timer = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        # Simple triangle ship
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, CYAN, points)
        # Shield indicator
        if self.shield:
            pygame.draw.ellipse(surface, GREEN, (self.x - 10, self.y - 10, self.width + 20, self.height + 20), 2)

    def move(self, dx):
        self.x += dx * self.speed
        # Keep ship within screen bounds
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.rect.x = self.x

class Bullet:
    def __init__(self, x, y, owner='player'):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 12
        self.speed = 7 if owner == 'player' else 3
        self.owner = owner
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.owner == 'player':
            self.y -= self.speed
        else:
            self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        color = RED if self.owner == 'player' else YELLOW
        pygame.draw.rect(surface, color, self.rect)

class Enemy:
    def __init__(self, x, y, row, col, total_cols):
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.total_cols = total_cols
        self.width = 35
        self.height = 25
        self.base_speed = 1 + row * 0.2   # Faster in later rows
        self.direction = 1                 # 1 = right, -1 = left
        self.move_timer = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, barrier_hits):
        # Horizontal movement
        self.move_timer += 1
        if self.move_timer >= 30 - self.row * 5:   # Adjust speed per row
            self.x += self.direction * self.base_speed
            self.rect.x = self.x
            self.move_timer = 0

        # Check for barrier hits (simplified)
        for b in barrier_hits:
            if self.rect.colliderect(b.rect):
                self.direction *= -1
                self.y += 10
                self.rect.y = self.y
                break

        # Descend when hitting edge
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.direction *= -1
            self.y += self.height
            self.rect.y = self.y

    def draw(self, surface):
        # Enemy shape: a simple hexagon
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height // 2),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width, self.y + self.height // 2)
        ]
        pygame.draw.polygon(surface, RED, points)

class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.health = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        color = (255, 100, 100) if self.health == 1 else (255, 200, 200) if self.health == 2 else GREEN
        pygame.draw.rect(surface, color, self.rect)
        # Simple health bar
        bar_width = self.width * (self.health / 3.0)
        pygame.draw.rect(surface, RED, (self.x, self.y - 4, bar_width, 2))

    def hit(self):
        if self.health > 0:
            self.health -= 1
            return True
        return False

class Bonus:
    def __init__(self, x, y, bonus_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.bonus_type = bonus_type   # 'extra_life', 'shield', 'speed'
        self.speed = 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        color = YELLOW if self.bonus_type == 'speed' else GREEN if self.bonus_type == 'extra_life' else BLUE
        pygame.draw.rect(surface, color, self.rect)
        # Small icon inside
        pygame.draw.circle(surface, BLACK, (self.x + self.width//2, self.y + self.height//2), 10)

# ----------------------------------------------------------------------
# Game state management
# ----------------------------------------------------------------------
class Game:
    def __init__(self):
        self.screen = SCREEN
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Player ship
        self.ship = Ship(WIDTH // 2 - 20, HEIGHT - 80)

        # Bullets
        self.player_bullets = []
        self.enemy_bullets = []

        # Enemies
        self.enemies = []
        self.spawn_enemies()

        # Barriers (two side walls)
        self.barriers = []
        barrier_y = HEIGHT - 100
        for i in range(5):
            self.barriers.append(Barrier(50 + i * 80, barrier_y))

        # Bonuses
        self.bonuses = []

        # Game stats
        self.score = 0
        self.level = 1
        self.max_level = 5
        self.lives = self.ship.lives
        self.game_over = False
        self.victory = False

        # Timing
        self.enemy_shoot_timer = 0
        self.bonus_spawn_timer = 0
        self.start_time = datetime.datetime.now()
        self.elapsed_time = 0

        # Sound
        self.background_music_playing = False

        # Load persistent stats
        self.stats_file = self.get_stats_path()
        self.stats = self.load_stats()

        # Play background music once
        BACKGROUND_MUSIC.play(-1)

    def get_stats_path(self):
        # Use a temporary directory for stats (no user‑visible files)
        tmpdir = tempfile.gettempdir()
        return Path(tmpdir) / "space_invaders_stats.json"

    def load_stats(self):
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_stats(self):
        # Update stats with current session
        self.stats["high_score"] = max(self.stats.get("high_score", 0), self.score)
        self.stats["levels_completed"] = max(self.stats.get("levels_completed", 0), self.level)
        self.stats["total_play_time_seconds"] = self.stats.get("total_play_time_seconds", 0) + self.elapsed_time
        self.stats["last_played"] = datetime.datetime.now().isoformat()
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            pass

    def spawn_enemies(self):
        self.enemies.clear()
        cols = 10
        rows = 3
        spacing_x = WIDTH // cols
        spacing_y = 50
        for row in range(rows):
            for col in range(cols):
                x = col * spacing_x + spacing_x // 2 - 17
                y = row * spacing_y + 50
                self.enemies.append(Enemy(x, y, row, col, cols))

    def spawn_enemy_bullet(self):
        if self.enemies:
            target = random.choice(self.enemies)
            bullet = Bullet(target.x + target.width // 2 - 2, target.y + target.height, owner='enemy')
            self.enemy_bullets.append(bullet)

    def spawn_bonus(self):
        if random.random() < 0.02:   # 2% chance per frame
            # Decide bonus type based on level
            bonus_types = ['extra_life', 'shield', 'speed']
            # Weight higher levels towards speed bonus
            if self.level >= 4:
                bonus_type = 'speed'
            else:
                bonus_type = random.choice(bonus_types)
            x = random.randint(100, WIDTH - 100)
            y = -30
            self.bonuses.append(Bonus(x, y, bonus_type))

    def apply_bonus(self, bonus):
        if bonus.bonus_type == 'extra_life' and self.lives < 5:
            self.lives += 1
            self.ship.lives = self.lives
        elif bonus.bonus_type == 'shield':
            self.ship.shield = True
            self.ship.shield_timer = 200   # frames
        elif bonus.bonus_type == 'speed':
            self.ship.speed *= 1.5
            # Reduce enemy speed for a short while
            for e in self.enemies:
                e.base_speed *= 0.8
            # Reset after 200 frames (handled in update)
            self.speed_boost_timer = 200

    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.score += 10 * (enemy.row + 1)
                    HIT_SOUND.play()
                    self.enemies.remove(enemy)
                    self.player_bullets.remove(bullet)
                    break

        # Enemy bullets vs ship
        for bullet in self.enemy_bullets[:]:
            if self.ship.rect.colliderect(bullet.rect):
                if self.ship.shield:
                    self.ship.shield = False
                    self.ship.shield_timer = 0
                else:
                    self.lives -= 1
                    EXPLOSION_SOUND.play()
                    self.enemy_bullets.remove(bullet)
                    if self.lives <= 0:
                        self.game_over = True
                break

        # Player bullets vs barriers
        for bullet in self.player_bullets[:]:
            for bar in self.barriers:
                if bullet.rect.colliderect(bar.rect):
                    if bar.hit():
                        HIT_SOUND.play()
                    self.player_bullets.remove(bullet)
                    break

        # Enemy bullets vs barriers
        for bullet in self.enemy_bullets[:]:
            for bar in self.barriers:
                if bullet.rect.colliderect(bar.rect):
                    if bar.hit():
                        HIT_SOUND.play()
                    self.enemy_bullets.remove(bullet)
                    break

        # Ship vs bonuses
        for bonus in self.bonuses[:]:
            if self.ship.rect.colliderect(bonus.rect):
                self.apply_bonus(bonus)
                BONUS_SOUND.play()
                self.bonuses.remove(bonus)

    def update(self):
        if self.game_over or self.victory:
            return

        # Update elapsed time
        self.elapsed_time = (datetime.datetime.now() - self.start_time).total_seconds()

        # Player input
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        self.ship.move(dx)

        # Shooting
        if keys[pygame.K_SPACE]:
            if len(self.player_bullets) < 3:   # Limit simultaneous bullets
                bullet = Bullet(self.ship.x + self.ship.width // 2 - 2, self.ship.y, owner='player')
                self.player_bullets.append(bullet)
                SHOOT_SOUND.play()

        # Enemy behavior
        self.enemy_shoot_timer += 1
        if self.enemy_shoot_timer >= 60 - self.level * 5:
            self.spawn_enemy_bullet()
            self.enemy_shoot_timer = 0

        for enemy in self.enemies:
            enemy.update(self.barriers)

        # Update bullets
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.y < -10:
                self.player_bullets.remove(bullet)
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.y > HEIGHT + 10:
                self.enemy_bullets.remove(bullet)

        # Spawn bonuses
        self.bonus_spawn_timer += 1
        if self.bonus_spawn_timer >= 600:   # Every ~10 seconds
            self.spawn_bonus()
            self.bonus_spawn_timer = 0

        for bonus in self.bonuses[:]:
            bonus.update()
            if bonus.y > HEIGHT + 10:
                self.bonuses.remove(bonus)

        # Check collisions
        self.check_collisions()

        # Barrier health depletion
        self.barriers = [b for b in self.barriers if b.health > 0]

        # Level progression: if all enemies are gone
        if not self.enemies:
            self.level += 1
            if self.level <= self.max_level:
                self.spawn_enemies()
                # Increase difficulty
                for e in self.enemies:
                    e.base_speed += 0.2
                # Reset ship speed if boosted
                if hasattr(self, 'speed_boost_timer') and self.speed_boost_timer > 0:
                    self.speed_boost_timer -= 1
                    if self.speed_boost_timer <= 0:
                        self.ship.speed = 5
                        for e in self.enemies:
                            e.base_speed = e.base_speed / 0.8  # revert
                # Give a small bonus at level start
                self.lives += 1
                self.ship.lives = self.lives
            else:
                self.victory = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw sky gradient (simple)
        for y in range(0, HEIGHT, 4):
            color = (0, 0, max(50, 150 - y // 10))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        # Draw ship
        self.ship.draw(self.screen)

        # Draw bullets
        for b in self.player_bullets:
            b.draw(self.screen)
        for b in self.enemy_bullets:
            b.draw(self.screen)

        # Draw enemies
        for e in self.enemies:
            e.draw(self.screen)

        # Draw barriers
        for b in self.barriers:
            b.draw(self.screen)

        # Draw bonuses
        for bonus in self.bonuses:
            bonus.draw(self.screen)

        # UI: score, lives, level
        draw_text(self.screen, self.font_small, f"Score: {self.score}", WHITE, (100, 30))
        draw_text(self.screen, self.font_small, f"Lives: {self.lives}", WHITE, (100, 70))
        draw_text(self.screen, self.font_small, f"Level: {self.level}", WHITE, (WIDTH - 100, 30))
        draw_text(self.screen, self.font_small, f"Time: {int(self.elapsed_time)}s", WHITE, (WIDTH - 100, 70))

        # Game over / victory screens
        if self.game_over:
            draw_text(self.screen, self.font_large, "GAME OVER", RED, (WIDTH // 2, HEIGHT // 2 - 50))
            draw_text(self.screen, self.font_medium, f"Final Score: {self.score}", WHITE, (WIDTH // 2, HEIGHT // 2 + 20))
            draw_text(self.screen, self.font_small, "Press R to Restart or Q to Quit", WHITE, (WIDTH // 2, HEIGHT // 2 + 80))
            self.save_stats()
        elif self.victory:
            draw_text(self.screen, self.font_large, "VICTORY!", GREEN, (WIDTH // 2, HEIGHT // 2 - 50))
            draw_text(self.screen, self.font_medium, f"Score: {self.score}", WHITE, (WIDTH // 2, HEIGHT // 2 + 20))
            draw_text(self.screen, self.font_small, "Press R to Restart or Q to Quit", WHITE, (WIDTH // 2, HEIGHT // 2 + 80))
            self.save_stats()
        else:
            # Press SPACE to pause? (optional)
            pass

        pygame.display.flip()

    def reset(self):
        self.ship = Ship(WIDTH // 2 - 20, HEIGHT - 80)
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.spawn_enemies()
        self.barriers = []
        barrier_y = HEIGHT - 100
        for i in range(5):
            self.barriers.append(Barrier(50 + i * 80, barrier_y))
        self.bonuses.clear()
        self.score = 0
        self.level = 1
        self.lives = self.ship.lives
        self.game_over = False
        self.victory = False
        self.start_time = datetime.datetime.now()
        self.elapsed_time = 0
        if hasattr(self, 'speed_boost_timer'):
            del self.speed_boost_timer

# ----------------------------------------------------------------------
# Main game loop
# ----------------------------------------------------------------------
def main():
    game = Game()
    menu = True
    running = True

    while running:
        clock.tick(FPS)

        # --- Menu ---
        if menu:
            SCREEN.fill(BLACK)
            draw_text(SCREEN, game.font_large, "SPACE INVADERS", CYAN, (WIDTH // 2, HEIGHT // 2 - 100))
            draw_text(SCREEN, game.font_medium, "Press SPACE to Start", WHITE, (WIDTH // 2, HEIGHT // 2))
            draw_text(SCREEN, game.font_small, "Use ARROW KEYS to move, SPACE to shoot", WHITE, (WIDTH // 2, HEIGHT // 2 + 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        menu = False
                    if event.key == pygame.K_q:
                        running = False

        # --- Gameplay ---
        else:
            game.update()
            game.draw()

            # Event handling for restart/quit during play
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                        menu = True   # show menu briefly before restart
                    if event.key == pygame.K_q:
                        running = False

            # Auto‑hide menu after restart
            if not menu and pygame.key.get_pressed()[pygame.K_r]:
                menu = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
