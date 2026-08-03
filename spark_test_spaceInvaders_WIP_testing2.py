# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/GRM-Qwen2.6-27B-Opus-Heretic-Abliterated-MTP.Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf

import pygame
import random
import math
import json
import os
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ----------------------
# Constants & Settings
# ----------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# All colors defined (no missing constants)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_CYAN = (0, 150, 150)
LIGHT_BLUE = (100, 100, 255)
DARK_BLUE = (0, 0, 150)
BLUE = (0, 0, 255)

# Game Settings (balanced for playability)
PLAYER_SPEED = 6
BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 5
ENEMY_SPEED_BASE = 1.0
PLAYER_SHOOT_COOLDOWN = 300  # ms
BARRIER_BLOCK_SIZE = 5
# Large barriers (2.5x wider, 2x taller than original)
BARRIER_WIDTH = 100
BARRIER_HEIGHT = 60
POWERUP_CHANCE = 0.07  # Slightly higher drop rate for fun
SAVE_FILE = "space_invaders_save.json"


# ----------------------
# Sound Generation (No External Files!)
# ----------------------
def generate_sound(frequency, duration, volume=0.5, wave_type='sine', sweep_end_freq=None):
    """Generate sound buffer programmatically"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()

    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'sine':
            if sweep_end_freq:
                freq = frequency + (sweep_end_freq - frequency) * (t / duration)
                sample = math.sin(2 * math.pi * freq * t)
            else:
                sample = math.sin(2 * math.pi * frequency * t)
        elif wave_type == 'square':
            sample = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        elif wave_type == 'noise':
            sample = random.uniform(-1, 1)
        elif wave_type == 'triangle':
            sample = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
        else:
            sample = 0

        sample = int(sample * volume * 32767)
        buf.extend(sample.to_bytes(2, byteorder='little', signed=True))

    # Convert to stereo
    stereo_buf = bytearray()
    for i in range(0, len(buf), 2):
        stereo_buf.extend(buf[i:i + 2])
        stereo_buf.extend(buf[i:i + 2])

    return pygame.mixer.Sound(buffer=stereo_buf)


# Generate sound effects
try:
    SHOOT_SOUND = generate_sound(1000, 0.1, 0.3, 'sine', 400)
    ENEMY_EXPLOSION_SOUND = generate_sound(200, 0.3, 0.4, 'noise')
    PLAYER_HIT_SOUND = generate_sound(150, 0.5, 0.5, 'square')
    LEVEL_UP_SOUND = generate_sound(523, 0.1, 0.4, 'sine')
    pygame.mixer.Sound.play(LEVEL_UP_SOUND)
    time.sleep(0.1)
    LEVEL_UP_SOUND = generate_sound(659, 0.1, 0.4, 'sine')
    pygame.mixer.Sound.play(LEVEL_UP_SOUND)
    time.sleep(0.1)
    LEVEL_UP_SOUND = generate_sound(783, 0.1, 0.4, 'sine')
    POWERUP_SOUND = generate_sound(880, 0.2, 0.4, 'sine')
    UFO_SOUND = generate_sound(200, 0.5, 0.3, 'sawtooth')
    BACKGROUND_HUM = generate_sound(60, 2.0, 0.05, 'sine')
    BACKGROUND_HUM.set_volume(0.1)
    SOUND_AVAILABLE = True
except Exception as e:
    SOUND_AVAILABLE = False
    print(f"Sound not available, running without audio (error: {e})")

# ----------------------
# Game Setup
# ----------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)


# ----------------------
# Sprite Classes
# ----------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        # Sleek spaceship design
        pygame.draw.polygon(self.image, CYAN, [(25, 0), (50, 30), (25, 20), (0, 30)])
        pygame.draw.polygon(self.image, DARK_CYAN, [(25, 5), (45, 28), (25, 18), (5, 28)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.lives = 3
        self.shield_active = False
        self.shield_end_time = 0
        self.fast_shoot_active = False
        self.fast_shoot_end_time = 0
        self.wide_bullets_active = False
        self.wide_bullets_end_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

        current_time = pygame.time.get_ticks()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= clock.get_time()

        # Update power-up timers
        if self.shield_active and current_time > self.shield_end_time:
            self.shield_active = False
        if self.fast_shoot_active and current_time > self.fast_shoot_end_time:
            self.fast_shoot_active = False
        if self.wide_bullets_active and current_time > self.wide_bullets_end_time:
            self.wide_bullets_active = False

        # Shooting
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            cooldown = PLAYER_SHOOT_COOLDOWN // 2 if self.fast_shoot_active else PLAYER_SHOOT_COOLDOWN
            self.shoot_cooldown = cooldown
            bullet_width = 15 if self.wide_bullets_active else 3
            bullet = PlayerBullet(self.rect.centerx, self.rect.top, bullet_width)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            if SOUND_AVAILABLE:
                SHOOT_SOUND.play()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield_active:
            pygame.draw.circle(surface, (0, 255, 255, 100), self.rect.center, 35, 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type  # 1 = basic, 2 = fast, 3 = tank
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)

        # Different enemy designs
        if self.enemy_type == 1:
            color = GREEN
            pygame.draw.ellipse(self.image, color, (5, 5, 30, 20))
            pygame.draw.line(self.image, color, (10, 25), (5, 30), 2)
            pygame.draw.line(self.image, color, (30, 25), (35, 30), 2)
        elif self.enemy_type == 2:
            color = YELLOW
            pygame.draw.rect(self.image, color, (10, 5, 20, 20))
            pygame.draw.line(self.image, color, (10, 10), (0, 0), 2)
            pygame.draw.line(self.image, color, (30, 10), (40, 0), 2)
            pygame.draw.line(self.image, color, (10, 20), (0, 30), 2)
            pygame.draw.line(self.image, color, (30, 20), (40, 30), 2)
        else:
            color = RED
            pygame.draw.ellipse(self.image, color, (5, 0, 30, 25))
            for i in range(4):
                pygame.draw.line(self.image, color, (10 + i * 7, 25), (5 + i * 7, 30), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Capped enemy speed to prevent impossible difficulty
        self.speed = min(ENEMY_SPEED_BASE * (1 + (current_level - 1) * 0.1) * (1.5 if self.enemy_type == 2 else 1), 3.0)
        self.shoot_cooldown = random.randint(2000, 4000) - (current_level * 50)
        self.health = 1 if self.enemy_type == 1 else (2 if self.enemy_type == 2 else 3)

    def update(self):
        # FIX: Declare all global variables BEFORE using them (fixes SyntaxError)
        global last_enemy_shot_time, global_enemy_cooldown, fire_rate_multiplier
        current_time = pygame.time.get_ticks()
        # Global fire rate limiter prevents "rain of shots"
        if current_time > self.shoot_cooldown and current_time > last_enemy_shot_time + (
                global_enemy_cooldown * fire_rate_multiplier):
            self.shoot_cooldown = current_time + random.randint(2000, 4000) - (current_level * 50)
            last_enemy_shot_time = current_time
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, width=3, color=YELLOW):
        super().__init__()
        self.direction = direction  # -1 = UP (player), 1 = DOWN (enemy)
        self.image = pygame.Surface((width, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, width, 12))
        # Glow effect
        glow = pygame.Surface((width + 6, 12 + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 50), (0, 0, width + 6, 12 + 6))
        self.image.blit(glow, (-3, -3))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = BULLET_SPEED if direction == -1 else ENEMY_BULLET_SPEED

    def update(self):
        self.rect.y += self.speed * self.direction
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Fixed directions: player shoots UP, enemy shoots DOWN
class PlayerBullet(Bullet):
    def __init__(self, x, y, width=3):
        super().__init__(x, y, -1, width, YELLOW)  # Direction = -1 (UP)


class EnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 3, RED)  # Direction = 1 (DOWN)


class BarrierBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BARRIER_BLOCK_SIZE, BARRIER_BLOCK_SIZE))
        self.image.fill(LIGHT_BLUE)
        # 3D effect highlight/shadow
        pygame.draw.rect(self.image, WHITE, (0, 0, BARRIER_BLOCK_SIZE, 2))
        pygame.draw.rect(self.image, DARK_CYAN, (0, BARRIER_BLOCK_SIZE - 2, BARRIER_BLOCK_SIZE, 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Barrier:
    def __init__(self, x, y):
        self.blocks = pygame.sprite.Group()
        block_cols = BARRIER_WIDTH // BARRIER_BLOCK_SIZE
        block_rows = BARRIER_HEIGHT // BARRIER_BLOCK_SIZE
        for row in range(block_rows):
            for col in range(block_cols):
                # Classic arch shape at the BOTTOM so player can shoot over, enemy fire is blocked
                if (row > block_rows - 2 and col < 2) or (row > block_rows - 2 and col > block_cols - 3):
                    continue
                block = BarrierBlock(x + col * BARRIER_BLOCK_SIZE, y + row * BARRIER_BLOCK_SIZE)
                self.blocks.add(block)
                all_sprites.add(block)

    def draw(self, surface):
        self.blocks.draw(surface)

    def check_hit(self, bullet):
        hit_blocks = pygame.sprite.spritecollide(bullet, self.blocks, True)
        return len(hit_blocks) > 0


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['extra_life', 'fast_shoot', 'shield', 'wide_bullets'])
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

        # Glowing orb with icon
        color = RED if self.type == 'extra_life' else (
            BLUE if self.type == 'fast_shoot' else (CYAN if self.type == 'shield' else YELLOW))
        pygame.draw.circle(self.image, (*color, 150), (15, 15), 12)
        pygame.draw.circle(self.image, color, (15, 15), 8)

        if self.type == 'extra_life':
            pygame.draw.polygon(self.image, WHITE, [(15, 8), (20, 15), (15, 22), (10, 15)])
        elif self.type == 'fast_shoot':
            pygame.draw.line(self.image, WHITE, (8, 15), (22, 15), 2)
            pygame.draw.polygon(self.image, WHITE, [(22, 10), (28, 15), (22, 20)])
        elif self.type == 'shield':
            pygame.draw.circle(self.image, WHITE, (15, 15), 6, 2)
        elif self.type == 'wide_bullets':
            pygame.draw.rect(self.image, WHITE, (8, 12, 14, 6))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 20), pygame.SRCALPHA)
        # Saucer shape
        pygame.draw.ellipse(self.image, PURPLE, (0, 5, 60, 10))
        pygame.draw.ellipse(self.image, WHITE, (20, 0, 20, 5))
        # Glow effect
        glow = pygame.Surface((70, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*PURPLE, 50), (0, 5, 70, 20))
        self.image.blit(glow, (-5, -5))
        self.rect = self.image.get_rect()
        # Spawn from random side
        self.rect.x = 0 if random.random() < 0.5 else SCREEN_WIDTH
        self.rect.y = 50
        self.speed = 3 if self.rect.x == 0 else -3
        self.direction = 1 if self.rect.x == 0 else -1

    def update(self):
        self.rect.x += self.speed * self.direction
        # Despawn if off screen
        if (self.direction == 1 and self.rect.left > SCREEN_WIDTH) or (self.direction == -1 and self.rect.right < 0):
            self.kill()
            global ufo
            ufo = None


class ExplosionParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = [random.uniform(-3, 3), random.uniform(-3, 3)]
        self.lifetime = random.randint(20, 40)
        self.max_lifetime = self.lifetime
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.velocity[0] *= 0.95
        self.velocity[1] *= 0.95
        return self.lifetime > 0

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))


# ----------------------
# Game State Management
# ----------------------
def load_save():
    default_save = {"high_score": 0, "max_level": 1, "total_kills": 0}
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                loaded_data = json.load(f)
            # Merge with defaults to fix missing keys from old saves
            default_save.update(loaded_data)
            return default_save
        except:
            return default_save
    return default_save


def save_game(score, level, kills):
    save_data = load_save()
    save_data["high_score"] = max(save_data["high_score"], score)
    save_data["max_level"] = max(save_data["max_level"], level)
    save_data["total_kills"] = save_data["total_kills"] + kills
    with open(SAVE_FILE, 'w') as f:
        json.dump(save_data, f)


def reset_level():
    global enemies, enemy_direction, level_start_time, enemy_bullets, current_level
    # Clear existing objects to prevent leftovers
    for enemy in enemies:
        enemy.kill()
    for bullet in enemy_bullets:
        bullet.kill()
    for bullet in player_bullets:
        bullet.kill()

    enemies = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    # Balanced enemy spawn (fewer enemies at start, caps at reasonable numbers)
    rows = min(4 + (current_level - 1), 8)  # Max 8 rows
    cols = min(6 + (current_level - 1) // 2, 8)  # Max 8 columns
    for row in range(rows):
        for col in range(cols):
            enemy_type = 1 if row < 2 else (2 if row < 4 else 3)
            enemy = Enemy(50 + col * 70, 50 + row * 40, enemy_type)
            enemies.add(enemy)
            all_sprites.add(enemy)

    enemy_direction = 1
    level_start_time = time.time()

    # Reset barriers every level
    for barrier in barriers:
        for block in barrier.blocks:
            block.kill()
    barriers.clear()
    # 4 large barriers covering full screen width
    barrier_positions = [50, 250, 450, 650]
    for x in barrier_positions:
        barriers.append(Barrier(x, 450))


def spawn_powerup(x, y):
    powerup = PowerUp(x, y)
    all_sprites.add(powerup)
    powerups.add(powerup)


# ----------------------
# Main Game Variables
# ----------------------
save_data = load_save()
high_score = save_data["high_score"]
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
barriers = []
powerups = pygame.sprite.Group()
particles = []
player = Player()
all_sprites.add(player)
current_level = 1
score = 0
level_kills = 0
enemy_direction = 1
level_start_time = time.time()
notification_text = ""
notification_timer = 0
game_state = "start"  # start, playing, paused, game_over

# Global fire rate control (fixes "rain of shots")
global_enemy_cooldown = 1000  # Base 1 shot per second at level 1
last_enemy_shot_time = 0
fire_rate_multiplier = 1.0
fire_rate_timer = 0

# UFO variables
ufo = None
ufo_spawn_timer = 0  # Fixed: no longer uses undefined current_time at init
ufo_spawn_delay = 15000  # Spawn every 15 seconds

# Starfield background
stars = []
for _ in range(100):
    stars.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(0, SCREEN_HEIGHT),
        'size': random.randint(1, 3),
        'brightness': random.randint(100, 255),
        'twinkle_speed': random.uniform(0.01, 0.05)
    })

# Initialize first level
reset_level()

# ----------------------
# Main Game Loop
# ----------------------
running = True
while running:
    current_time = pygame.time.get_ticks()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "start" or game_state == "game_over":
                if event.key == pygame.K_RETURN:
                    # Full game reset
                    all_sprites = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    player_bullets = pygame.sprite.Group()
                    enemy_bullets = pygame.sprite.Group()
                    powerups = pygame.sprite.Group()
                    particles = []
                    player = Player()
                    all_sprites.add(player)
                    current_level = 1
                    score = 0
                    level_kills = 0
                    global_enemy_cooldown = 1000
                    fire_rate_multiplier = 1.0
                    ufo = None
                    ufo_spawn_timer = current_time + 15000  # Set proper spawn time on game start
                    reset_level()
                    game_state = "playing"
                    if SOUND_AVAILABLE:
                        BACKGROUND_HUM.play(loops=-1)
                elif event.key == pygame.K_q:
                    running = False
            elif game_state == "playing":
                if event.key == pygame.K_p:
                    game_state = "paused"
                elif event.key == pygame.K_q:
                    save_game(score, current_level, level_kills)
                    running = False
            elif game_state == "paused":
                if event.key == pygame.K_p:
                    game_state = "playing"

    # Update game state
    if game_state == "playing":
        all_sprites.update()

        # Update particles
        particles = [p for p in particles if p.update()]

        # Update notification timer
        if notification_timer > 0:
            notification_timer -= clock.get_time()
            if notification_timer <= 0:
                notification_text = ""

        # Update star twinkle
        for star in stars:
            star['brightness'] += star['twinkle_speed'] * random.randint(-1, 1)
            star['brightness'] = max(100, min(255, star['brightness']))

        # Spawn UFO every 15-20 seconds
        if ufo is None and current_time > ufo_spawn_timer:
            ufo = UFO()
            all_sprites.add(ufo)
            ufo_spawn_timer = current_time + random.randint(15000, 20000)
            if SOUND_AVAILABLE:
                UFO_SOUND.play(loops=-1)
        # Update UFO if active
        if ufo:
            ufo.update()
            # UFO collision with player bullets
            hits = pygame.sprite.spritecollide(ufo, player_bullets, True)
            if hits:
                score += 1000
                if SOUND_AVAILABLE:
                    UFO_SOUND.stop()
                    LEVEL_UP_SOUND.play()
                # 10x fire rate reduction for 5 seconds (as requested)
                fire_rate_multiplier = 0.1
                fire_rate_timer = current_time + 5000
                notification_text = "FIRE RATE REDUCED 10x FOR 5s!"
                notification_timer = 3000
                # Spawn explosion
                for _ in range(20):
                    particles.append(ExplosionParticle(ufo.rect.centerx, ufo.rect.centery, PURPLE))
                ufo.kill()
                ufo = None

        # Reset fire rate after duration
        if fire_rate_multiplier != 1.0 and current_time > fire_rate_timer:
            fire_rate_multiplier = 1.0
            notification_text = "FIRE RATE NORMAL"
            notification_timer = 2000

        # Scale global enemy cooldown with level (slower scaling for playability)
        global_enemy_cooldown = max(300, 1000 - (current_level * 50))

        # Enemy formation movement
        if enemies:
            rightmost = max(enemies, key=lambda e: e.rect.right).rect.right
            leftmost = min(enemies, key=lambda e: e.rect.left).rect.left
            if rightmost >= SCREEN_WIDTH - 10 and enemy_direction == 1:
                enemy_direction = -1
                for enemy in enemies:
                    enemy.rect.y += 20
            elif leftmost <= 10 and enemy_direction == -1:
                enemy_direction = 1
                for enemy in enemies:
                    enemy.rect.y += 20

            for enemy in enemies:
                enemy.rect.x += enemy.speed * enemy_direction

        # Collision detection
        # Player bullets vs enemies
        hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy, bullets in hits.items():
            for _ in bullets:
                enemy.health -= 1
                if enemy.health <= 0:
                    enemy.kill()
                    score += 100 * enemy.enemy_type
                    level_kills += 1
                    # Explosion particles
                    for _ in range(15):
                        particles.append(ExplosionParticle(enemy.rect.centerx, enemy.rect.centery,
                                                           ORANGE if enemy.enemy_type == 1 else (
                                                               YELLOW if enemy.enemy_type == 2 else RED)))
                    if SOUND_AVAILABLE:
                        ENEMY_EXPLOSION_SOUND.play()
                    # Powerup drop
                    if random.random() < POWERUP_CHANCE:
                        spawn_powerup(enemy.rect.centerx, enemy.rect.centery)

        # Player bullets vs barriers
        for bullet in player_bullets:
            for barrier in barriers:
                if barrier.check_hit(bullet):
                    bullet.kill()
                    break

        # Enemy bullets vs barriers
        for bullet in enemy_bullets:
            for barrier in barriers:
                if barrier.check_hit(bullet):
                    bullet.kill()
                    break

        # Enemy bullets vs player
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits and not player.shield_active:
            player.lives -= 1
            if SOUND_AVAILABLE:
                PLAYER_HIT_SOUND.play()
            # Player explosion
            for _ in range(20):
                particles.append(ExplosionParticle(player.rect.centerx, player.rect.centery, CYAN))
            if player.lives <= 0:
                game_state = "game_over"
                if SOUND_AVAILABLE:
                    BACKGROUND_HUM.stop()
                    if ufo and UFO_SOUND.get_num_channels() > 0:
                        UFO_SOUND.stop()
                save_game(score, current_level, level_kills)
            else:
                player.rect.centerx = SCREEN_WIDTH // 2
                player.rect.bottom = SCREEN_HEIGHT - 20
                enemy_bullets.empty()

        # Powerup collection
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in hits:
            if SOUND_AVAILABLE:
                POWERUP_SOUND.play()
            current_time = pygame.time.get_ticks()
            if powerup.type == 'extra_life':
                player.lives += 1
                notification_text = "EXTRA LIFE!"
            elif powerup.type == 'fast_shoot':
                player.fast_shoot_active = True
                player.fast_shoot_end_time = current_time + 10000
                notification_text = "FAST SHOOT ACTIVE"
            elif powerup.type == 'shield':
                player.shield_active = True
                player.shield_end_time = current_time + 10000
                notification_text = "SHIELD ACTIVE"
            elif powerup.type == 'wide_bullets':
                player.wide_bullets_active = True
                player.wide_bullets_end_time = current_time + 10000
                notification_text = "WIDE BULLETS ACTIVE"
            notification_timer = 2000

        # Enemies reaching bottom = game over
        for enemy in enemies:
            if enemy.rect.bottom >= player.rect.top:
                player.lives = 0
                game_state = "game_over"
                if SOUND_AVAILABLE:
                    BACKGROUND_HUM.stop()
                    if ufo and UFO_SOUND.get_num_channels() > 0:
                        UFO_SOUND.stop()
                save_game(score, current_level, level_kills)
                break

        # Level complete
        if not enemies:
            current_level += 1
            # Bonus points for fast completion and remaining lives
            time_taken = time.time() - level_start_time
            level_bonus = int(max(0, 30000 - time_taken * 1000) * 0.1) + (500 * player.lives)
            score += 1000 * (current_level - 1) + level_bonus
            if SOUND_AVAILABLE:
                LEVEL_UP_SOUND.play()
            notification_text = f"LEVEL {current_level} COMPLETE! +{1000 * (current_level - 1) + level_bonus} BONUS"
            notification_timer = 3000
            reset_level()

    # Drawing
    screen.fill(BLACK)

    # Draw starfield
    for star in stars:
        pygame.draw.circle(screen, (star['brightness'], star['brightness'], star['brightness']),
                           (star['x'], star['y']), star['size'])

    # Draw all sprites
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    # Draw barriers
    for barrier in barriers:
        barrier.draw(screen)

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    # Draw UI
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    high_score_text = font_medium.render(f"High Score: {high_score}", True, WHITE)
    level_text = font_medium.render(f"Level: {current_level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

    # Draw lives
    for i in range(player.lives):
        pygame.draw.polygon(screen, CYAN, [(30 + i * 30, SCREEN_HEIGHT - 10),
                                           (45 + i * 30, SCREEN_HEIGHT - 30),
                                           (30 + i * 30, SCREEN_HEIGHT - 20),
                                           (15 + i * 30, SCREEN_HEIGHT - 30)])

    # Draw powerup timers
    current_time = pygame.time.get_ticks()
    y_offset = 40
    if player.shield_active:
        remaining = max(0, (player.shield_end_time - current_time) / 1000)
        pygame.draw.rect(screen, DARK_CYAN, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100, 10))
        pygame.draw.rect(screen, CYAN, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100 * (remaining / 10), 10))
        y_offset += 20
    if player.fast_shoot_active:
        remaining = max(0, (player.fast_shoot_end_time - current_time) / 1000)
        pygame.draw.rect(screen, DARK_BLUE, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100, 10))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100 * (remaining / 10), 10))
        y_offset += 20
    if player.wide_bullets_active:
        remaining = max(0, (player.wide_bullets_end_time - current_time) / 1000)
        pygame.draw.rect(screen, (100, 100, 0), (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100, 10))
        pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100 * (remaining / 10), 10))
        y_offset += 20

    # Draw fire rate reduction timer
    if fire_rate_multiplier != 1.0:
        remaining = max(0, (fire_rate_timer - current_time) / 1000)
        pygame.draw.rect(screen, (100, 0, 0), (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100, 10))
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - y_offset, 100 * (remaining / 5), 10))

    # Draw notifications
    if notification_text and notification_timer > 0:
        notif_surface = font_medium.render(notification_text, True, YELLOW)
        screen.blit(notif_surface, (SCREEN_WIDTH // 2 - notif_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

    # Game state overlays
    if game_state == "start":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = font_large.render("SPACE INVADERS", True, CYAN)
        subtitle = font_medium.render("Press ENTER to Start", True, WHITE)
        controls = font_small.render("Arrow Keys = Move | SPACE = Shoot | P = Pause | Q = Quit", True, WHITE)
        high_score_text = font_medium.render(f"High Score: {high_score}", True, YELLOW)

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))

    elif game_state == "paused":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        paused_text = font_large.render("PAUSED", True, WHITE)
        resume_text = font_medium.render("Press P to Resume", True, WHITE)
        screen.blit(paused_text, (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    elif game_state == "game_over":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("GAME OVER", True, RED)
        final_score = font_medium.render(f"Final Score: {score}", True, WHITE)
        new_high_score = font_medium.render("NEW HIGH SCORE!", True, YELLOW) if score > high_score else None
        restart_text = font_medium.render("Press ENTER to Play Again | Q to Quit", True, WHITE)

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        if new_high_score:
            screen.blit(new_high_score, (SCREEN_WIDTH // 2 - new_high_score.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
