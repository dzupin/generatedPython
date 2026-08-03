# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --image-min-tokens 1024 --reasoning-preserve --parallel 1  --temp 1.0 --top_p 1.0 --chat-template-kwargs '{"reasoning_effort":"max"}' --model /AI/models/DeepSeek-V4-Flash-0731-UD-IQ2_M-00001-of-00003.gguf
import pygame
import sys
import random
import math
import struct

# ---------- Constants ----------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_SPEED = 300          # pixels per second
PLAYER_BULLET_SPEED = -600  # up
ALIEN_BOMB_SPEED = 300      # down
BONUS_SPEED = 120

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)

# ---------- Sound synthesis ----------
def create_sound(freq_start, freq_end, duration, volume=0.4, wave='square'):
    sample_rate = 44100
    n = int(sample_rate * duration)
    data = []
    for i in range(n):
        t = i / sample_rate
        progress = i / n
        freq = freq_start + (freq_end - freq_start) * progress
        if wave == 'square':
            val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            val = math.sin(2 * math.pi * freq * t)
        val *= volume * (1 - progress)
        sample = int(max(-1.0, min(1.0, val)) * 32767)
        data.append(struct.pack('<h', sample))
        data.append(struct.pack('<h', sample))  # stereo
    return b''.join(data)

def create_noise(duration, volume=0.4):
    sample_rate = 44100
    n = int(sample_rate * duration)
    data = []
    for i in range(n):
        val = random.uniform(-1, 1)
        progress = i / n
        val *= volume * (1 - progress)
        sample = int(max(-1.0, min(1.0, val)) * 32767)
        data.append(struct.pack('<h', sample))
        data.append(struct.pack('<h', sample))
    return b''.join(data)

def create_tone_sequence(freqs, duration_per_note, volume=0.4, wave='square'):
    sample_rate = 44100
    data = []
    for freq in freqs:
        n = int(sample_rate * duration_per_note)
        for i in range(n):
            t = i / sample_rate
            progress = i / n
            if wave == 'square':
                val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            else:
                val = math.sin(2 * math.pi * freq * t)
            val *= volume * (1 - progress)
            sample = int(max(-1.0, min(1.0, val)) * 32767)
            data.append(struct.pack('<h', sample))
            data.append(struct.pack('<h', sample))
    return b''.join(data)

class SoundManager:
    def __init__(self):
        self.enabled = False
        try:
            self.shoot_sound = pygame.mixer.Sound(buffer=create_sound(880, 220, 0.12, 0.3))
            self.explosion_sound = pygame.mixer.Sound(buffer=create_noise(0.3, 0.5))
            self.player_hit_sound = pygame.mixer.Sound(buffer=create_noise(0.5, 0.7))
            self.bonus_sound = pygame.mixer.Sound(buffer=create_tone_sequence([660, 880, 1320], 0.1, 0.4, 'sine'))
            self.levelup_sound = pygame.mixer.Sound(buffer=create_tone_sequence([440, 554, 659, 880], 0.15, 0.4))
            self.gameover_sound = pygame.mixer.Sound(buffer=create_tone_sequence([440, 349, 262, 196], 0.4, 0.5))
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def play_shoot(self):
        if self.enabled:
            self.shoot_sound.play()

    def play_explosion(self):
        if self.enabled:
            self.explosion_sound.play()

    def play_player_hit(self):
        if self.enabled:
            self.player_hit_sound.play()

    def play_bonus(self):
        if self.enabled:
            self.bonus_sound.play()

    def play_levelup(self):
        if self.enabled:
            self.levelup_sound.play()

    def play_gameover(self):
        if self.enabled:
            self.gameover_sound.play()

# ---------- Background ----------
class Starfield:
    def __init__(self):
        self.stars = []
        for _ in range(150):
            self.stars.append([
                random.randrange(SCREEN_WIDTH),
                random.randrange(SCREEN_HEIGHT),
                random.uniform(10, 30),  # pixels per second
                random.choice([1, 2])
            ])

    def update(self, dt):
        for star in self.stars:
            star[1] += star[2] * dt
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randrange(SCREEN_WIDTH)

    def draw(self, surface):
        for x, y, speed, size in self.stars:
            pygame.draw.circle(surface, WHITE, (int(x), int(y)), size)

# ---------- Bullets ----------
class Bullet:
    def __init__(self, x, y, vx, vy, color, is_player):
        self.rect = pygame.Rect(0, 0, 6, 16)
        self.rect.centerx = x
        self.rect.centery = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.is_player = is_player

    def update(self, dt):
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

    def draw(self, surface):
        if self.is_player:
            pygame.draw.line(surface, self.color,
                             (self.rect.centerx, self.rect.bottom),
                             (self.rect.centerx, self.rect.top), 4)
        else:
            pygame.draw.circle(surface, self.color, self.rect.center, 6)

# ---------- Player ----------
class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 40, 30)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.lives = 3
        self.cooldown = 0
        self.rapid_fire_timer = 0
        self.speed = PLAYER_SPEED

    def update(self, keys, dt):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.cooldown = max(0, self.cooldown - dt)
        self.rapid_fire_timer = max(0, self.rapid_fire_timer - dt)

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = 0.3 if self.rapid_fire_timer <= 0 else 0.1
            return Bullet(self.rect.centerx, self.rect.top, 0,
                          PLAYER_BULLET_SPEED, YELLOW, True)
        return None

    def draw(self, surface):
        x, y = self.rect.left, self.rect.top
        w, h = self.rect.width, self.rect.height
        pygame.draw.polygon(surface, CYAN,
                            [(x + w // 2, y), (x, y + h), (x + w, y + h)])
        pygame.draw.polygon(surface, BLUE,
                            [(x + w // 2, y + 6),
                             (x + w // 2 - 6, y + h),
                             (x + w // 2 + 6, y + h)])
        pygame.draw.circle(surface, RED, (x + w // 2 - 8, y + h - 2), 4)
        pygame.draw.circle(surface, RED, (x + w // 2 + 8, y + h - 2), 4)

# ---------- Aliens ----------
class Alien:
    def __init__(self, x, y, type, color):
        self.rect = pygame.Rect(0, 0, 30, 24)
        self.rect.center = (x, y)
        self.type = type
        self.color = color
        self.points = [10, 20, 30][type]
        self.anim_timer = random.uniform(0, math.pi * 2)

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height

        if self.type == 0:
            pygame.draw.ellipse(surface, self.color, (x + 2, y + 4, w - 4, h - 8))
            pygame.draw.circle(surface, BLACK, (x + 8, y + 8), 3)
            pygame.draw.circle(surface, BLACK, (x + w - 8, y + 8), 3)
            leg_offset = int(math.sin(self.anim_timer * 5) * 3)
            pygame.draw.line(surface, self.color,
                             (x + w // 2, y + h - 6),
                             (x + w // 2 - 6, y + h + leg_offset), 2)
            pygame.draw.line(surface, self.color,
                             (x + w // 2, y + h - 6),
                             (x + w // 2 + 6, y + h - leg_offset), 2)

        elif self.type == 1:
            points = [(x + w // 2, y), (x, y + h // 2),
                      (x + w // 2, y + h), (x + w, y + h // 2)]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.circle(surface, BLACK, (x + w // 2 - 5, y + h // 2), 3)
            pygame.draw.circle(surface, BLACK, (x + w // 2 + 5, y + h // 2), 3)

        else:
            pygame.draw.rect(surface, self.color, (x + 2, y + 4, w - 4, h - 6),
                             border_radius=4)
            pygame.draw.line(surface, self.color, (x, y + 6), (x - 6, y + 2), 3)
            pygame.draw.line(surface, self.color, (x + w, y + 6), (x + w + 6, y + 2), 3)
            pygame.draw.circle(surface, BLACK, (x + 10, y + 10), 4)
            pygame.draw.circle(surface, BLACK, (x + w - 10, y + 10), 4)

# ---------- Fleet ----------
class Fleet:
    def __init__(self, level):
        self.level = level
        rows = min(2 + level // 2, 6)
        cols = min(8 + level // 2, 12)

        self.aliens = []
        self.direction = 1
        self.horizontal_speed = 30 + level * 8
        self.move_down_distance = 15
        self.bomb_rate = 0.2 + level * 0.03

        formation_width = cols * 50
        start_x = (SCREEN_WIDTH - formation_width) // 2
        start_y = 60

        for row in range(rows):
            for col in range(cols):
                if row == rows - 1:
                    type = 0
                elif row == rows - 2:
                    type = 1
                else:
                    type = 2

                x = start_x + col * 50 + 25
                y = start_y + row * 40 + 12
                color = (random.randint(100, 255),
                         random.randint(100, 255),
                         random.randint(100, 255))
                self.aliens.append(Alien(x, y, type, color))

    def update(self, dt):
        edge = False
        for alien in self.aliens:
            if self.direction > 0 and alien.rect.right >= SCREEN_WIDTH - 5:
                edge = True
                break
            elif self.direction < 0 and alien.rect.left <= 5:
                edge = True
                break

        if edge:
            self.direction *= -1
            for alien in self.aliens:
                alien.rect.y += self.move_down_distance

        for alien in self.aliens:
            alien.rect.x += self.direction * self.horizontal_speed * dt

        for alien in self.aliens:
            alien.anim_timer += dt

    def draw(self, surface):
        for alien in self.aliens:
            alien.draw(surface)

# ---------- Barrier ----------
class Barrier:
    def __init__(self, x, y, width=70, height=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.draw_initial()

    def draw_initial(self):
        self.surface.fill((0, 0, 0, 0))
        for bx in range(0, self.rect.width, 20):
            for by in range(0, self.rect.height, 15):
                pygame.draw.rect(self.surface, GREEN,
                                 (bx, by, 18, 13), border_radius=2)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def hit(self, bullet):
        if not self.rect.colliderect(bullet.rect):
            return False

        local_x = bullet.rect.centerx - self.rect.x
        local_y = bullet.rect.centery - self.rect.y

        if 0 <= local_x < self.rect.width and 0 <= local_y < self.rect.height:
            if self.surface.get_at((local_x, local_y)).a > 0:
                pygame.draw.circle(self.surface, (0, 0, 0, 0),
                                   (local_x, local_y), 8)
                return True
        return False

# ---------- Particles ----------
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-100, 100)
        self.lifetime = random.uniform(0.2, 0.6)
        self.color = color
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color,
                               (int(self.x), int(self.y)), self.size)

# ---------- Bonus ----------
class Bonus:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = (x, y)
        self.type = type          # 'S', 'P', 'L'
        self.vy = BONUS_SPEED
        self.timer = 10.0         # seconds

    def update(self, dt):
        self.rect.y += self.vy * dt
        self.timer -= dt

    def draw(self, surface):
        colors = {'S': ORANGE, 'P': CYAN, 'L': RED}
        pygame.draw.circle(surface, colors[self.type], self.rect.center, 15)
        pygame.draw.circle(surface, WHITE, self.rect.center, 15, 2)
        font = pygame.font.Font(None, 24)
        text = font.render(self.type, True, BLACK)
        surface.blit(text, text.get_rect(center=self.rect.center))

# ---------- Main Game ----------
class Game:
    HIGHSCORE_FILE = "space_invaders_highscore.txt"

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.sound = SoundManager()
        self.starfield = Starfield()
        self.highscore = self.load_highscore()
        self.reset()

    def load_highscore(self):
        try:
            with open(self.HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def save_highscore(self):
        try:
            with open(self.HIGHSCORE_FILE, "w") as f:
                f.write(str(self.highscore))
        except Exception:
            pass

    def reset(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.player = Player()
        self.player.lives = self.lives
        self.player_bullets = []
        self.alien_bullets = []
        self.bonuses = []
        self.particles = []
        self.state = "playing"
        self.level_clear_timer = 0
        self.start_level(self.level)

    def start_level(self, level):
        self.level = level
        self.fleet = Fleet(level)

        self.barriers = []
        barrier_width = 70
        barrier_height = 50
        positions = [100, 300, 500, 700]
        for x in positions:
            self.barriers.append(Barrier(x, SCREEN_HEIGHT - 120,
                                         barrier_width, barrier_height))

        self.player_bullets.clear()
        self.alien_bullets.clear()
        self.bonuses.clear()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    if self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                elif event.key == pygame.K_r and self.state == "gameover":
                    self.reset()

    def spawn_explosion(self, x, y, color):
        for _ in range(10):
            self.particles.append(Particle(x, y, color))

    def update_particles(self, dt):
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def update(self, dt):
        if self.state == "paused":
            return

        self.update_particles(dt)

        if self.state == "gameover":
            return

        if self.state == "level_clear":
            self.level_clear_timer -= dt
            if self.level_clear_timer <= 0:
                self.level += 1
                self.start_level(self.level)
                self.state = "playing"
            return

        # Playing state
        self.starfield.update(dt)
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)

        # Player shooting
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                self.player_bullets.append(bullet)
                self.sound.play_shoot()

        # Update bullets
        for bullet in self.player_bullets[:]:
            bullet.update(dt)
            if bullet.rect.bottom < 0:
                self.player_bullets.remove(bullet)

        for bomb in self.alien_bullets[:]:
            bomb.update(dt)
            if bomb.rect.top > SCREEN_HEIGHT:
                self.alien_bullets.remove(bomb)

        # Barrier collisions
        for bullet in self.player_bullets[:]:
            for barrier in self.barriers:
                if barrier.hit(bullet):
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)
                    break

        for bomb in self.alien_bullets[:]:
            for barrier in self.barriers:
                if barrier.hit(bomb):
                    if bomb in self.alien_bullets:
                        self.alien_bullets.remove(bomb)
                    break

        # Player bullets vs aliens
        self.update_alien_hits()

        # Alien bombs vs player
        for bomb in self.alien_bullets[:]:
            if bomb.rect.colliderect(self.player.rect):
                self.alien_bullets.remove(bomb)
                self.player_hit()
                if self.state == "gameover":
                    return
                break

        # Aliens reach the player / bottom
        for alien in self.fleet.aliens:
            if (alien.rect.colliderect(self.player.rect) or
                    alien.rect.bottom >= self.player.rect.top):
                self.game_over()
                return

        # Fleet update and shooting
        self.fleet.update(dt)
        if random.random() < self.fleet.bomb_rate * dt:
            if self.fleet.aliens:
                shooter = random.choice(self.fleet.aliens)
                self.alien_bullets.append(
                    Bullet(shooter.rect.centerx, shooter.rect.bottom, 0,
                           ALIEN_BOMB_SPEED, RED, False))

        # Bonus updates
        for bonus in self.bonuses[:]:
            bonus.update(dt)
            if bonus.rect.colliderect(self.player.rect):
                self.apply_bonus(bonus)
                self.bonuses.remove(bonus)
            elif bonus.timer <= 0 or bonus.rect.top > SCREEN_HEIGHT:
                self.bonuses.remove(bonus)

        # Level clear check
        if not self.fleet.aliens:
            self.state = "level_clear"
            self.level_clear_timer = 2.0
            self.score += 100 * self.level
            self.sound.play_levelup()

    def update_alien_hits(self):
        for bullet in self.player_bullets[:]:
            for alien in self.fleet.aliens[:]:
                if alien.rect.colliderect(bullet.rect):
                    self.player_bullets.remove(bullet)
                    self.fleet.aliens.remove(alien)
                    self.score += alien.points
                    self.sound.play_explosion()
                    self.spawn_explosion(alien.rect.centerx,
                                         alien.rect.centery,
                                         alien.color)
                    if random.random() < 0.15:
                        self.bonuses.append(
                            Bonus(alien.rect.centerx, alien.rect.centery,
                                  random.choice(['S', 'P', 'L'])))
                    break

    def player_hit(self):
        self.lives -= 1
        self.player.lives = self.lives
        self.sound.play_player_hit()
        self.spawn_explosion(self.player.rect.centerx,
                             self.player.rect.centery, RED)

        if self.lives <= 0:
            self.game_over()
        else:
            self.player.rect.centerx = SCREEN_WIDTH // 2
            self.player.rect.bottom = SCREEN_HEIGHT - 20
            self.player.cooldown = 0
            self.player.rapid_fire_timer = 0
            self.alien_bullets.clear()

    def apply_bonus(self, bonus):
        self.sound.play_bonus()
        if bonus.type == 'S':
            self.score += 500
        elif bonus.type == 'P':
            self.player.rapid_fire_timer = 5.0
        elif bonus.type == 'L':
            self.lives += 1
            self.player.lives = self.lives

    def game_over(self):
        self.state = "gameover"
        self.sound.play_gameover()
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(None, size)
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(x, y))
        self.screen.blit(surf, rect)

    def draw(self):
        self.screen.fill(BLACK)
        self.starfield.draw(self.screen)

        for barrier in self.barriers:
            barrier.draw(self.screen)

        self.fleet.draw(self.screen)

        if self.state != "gameover":
            self.player.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)
        for bomb in self.alien_bullets:
            bomb.draw(self.screen)
        for bonus in self.bonuses:
            bonus.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)

        # UI
        self.draw_text(f"Score: {self.score}", 36, WHITE, 100, 20)
        self.draw_text(f"High: {self.highscore}", 36, YELLOW,
                       SCREEN_WIDTH // 2, 20)
        self.draw_text(f"Level: {self.level}", 36, CYAN,
                       SCREEN_WIDTH - 80, 20)

        # Lives
        for i in range(self.lives):
            pygame.draw.rect(self.screen, GREEN, (10 + i * 25, 45, 20, 12))
            pygame.draw.circle(self.screen, CYAN, (15 + i * 25, 40), 8)

        # State overlays
        if self.state == "paused":
            self.draw_text("PAUSED", 60, YELLOW,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.draw_text("Press P to resume", 30, WHITE,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        elif self.state == "gameover":
            self.draw_text("GAME OVER", 80, RED,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
            self.draw_text(f"Score: {self.score}", 40, WHITE,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            self.draw_text("Press R to restart", 30, WHITE,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        elif self.state == "level_clear":
            self.draw_text(f"Level {self.level} Clear!", 60, GREEN,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

# ---------- Entry point ----------
def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders")

    game = Game(screen)
    game.run()
    sys.exit(0)

if __name__ == "__main__":
    main()
