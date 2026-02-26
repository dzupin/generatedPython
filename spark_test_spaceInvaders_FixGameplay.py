# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).

# Analyze python game code bellow and then modify code to fix movement of ufo enemies that is currently restricted to left half of screen to utilize full width of screen.

# Analyze python game code bellow and then modify code to fix movement of invaders enemies that is currently restricted to left half of screen to utilize full width of screen. To be more specific about problem that needs to be fixed: Invader enemies are currently moving by very short distance back and forth in horizontal direction and not moving at vertical direction at all. As a result ufo enemies are staying at approximately same position where they have been spawned.

# Analyze python game code bellow and then modify code to fix movement of 28 invader enemies. the regular invaders (not the UFO) are stuck on the left side of the screen and never reach the right side.  the regular invaders looks like they only vibrate in left-right of horizontal direction and not moving to left (or to right) as expected. The barriers on the right remain intact because the invaders never migrate there.

# Analyze python game code bellow and then modify code to fix movement of 28 invader enemies. the regular invaders (not the UFO) are stuck on the left side of the screen and never reach the right side.  the regular invaders looks like they only vibrate in left-right of horizontal direction and not moving to left (or to right) as expected. The barriers on the right remain intact because the invaders never migrate there.  (Check screenshot for additional details, notice that barrier  on right side are never hit by regular invaders because invaders never move to left side of screen)

# Below is a Python pygame implementation of a Space Invaders clone. The game logic for enemy movement is broken: the 28 regular invaders are stuck vibrating horizontally near the left side of the screen and never migrate across to the right side. Consequently, the barriers on the right side of the screen remain completely untouched.
#
# Please analyze the Invader class and the Game.update_logic method to identify why the invaders are not moving horizontally across the screen. Then, provide the corrected code to fix this movement issue.
#
# The Symptoms:
#
#     Invaders move left and right slightly (vibrate) but stay in the same general horizontal area.
#     They never reach the right edge of the screen.
#     The "edge reached" logic in update_logic seems to trigger, but the invaders do not actually shift their base position.




import pygame
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_BULLET_SPEED = 4
MAX_ENEMY_BULLETS = 5
NUM_ENEMIES_ROWS = 4
NUM_ENEMIES_COLS = 8

# Game Balance
PLAYER_SHOOT_DELAY = 350
ENEMY_SHOOT_CHANCE = 0.05
PLAYER_LIVES = 3
MAX_BARRIERS = 4

# Colors
BG_COLOR = (10, 10, 20)
PLAYER_COLOR = (0, 255, 200)
ENEMY_1_COLOR = (255, 69, 0)
ENEMY_2_COLOR = (0, 255, 127)
ENEMY_3_COLOR = (138, 43, 226)
TEXT_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 255, 0)
ENEMY_BULLET_COLOR = (255, 100, 100)
UFO_COLOR = (255, 255, 255)
BARRIER_COLOR = (0, 255, 255)


# --- AUDIO SYSTEM ---
class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 512)
        self.channels = [pygame.mixer.Channel(i) for i in range(4)]
        self.sample_rate = 44100

    def create_tone(self, freq, duration, vol=0.3, wave_type='square'):
        samples = int(self.sample_rate * duration)
        buffer = [0] * (samples * 2)
        max_sample = 32767
        for s in range(samples):
            t = float(s) / self.sample_rate
            if wave_type == 'square':
                value = math.sin(2 * math.pi * freq * t)
                sample_val = int(max_sample * vol * (1 if value > 0 else -1))
                buffer[s * 2] = sample_val
                buffer[s * 2 + 1] = sample_val
            elif wave_type == 'sawtooth':
                value = ((2 * (t * freq - math.floor(t * freq + 0.5))))
                sample_val = int(max_sample * vol * value)
                buffer[s * 2] = sample_val
                buffer[s * 2 + 1] = sample_val
            else:
                sample_val = int(max_sample * vol * math.sin(2 * math.pi * freq * t))
                buffer[s * 2] = sample_val
                buffer[s * 2 + 1] = sample_val
        return pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        )

    def play_shoot(self):
        self.channels[0].play(self.create_tone(880, 0.15, 0.2, 'square'))

    def play_enemy_shoot(self):
        self.channels[1].play(self.create_tone(200, 0.2, 0.15, 'sawtooth'))

    def play_ufo_shoot(self):
        self.channels[0].play(self.create_tone(1200, 0.1, 0.25, 'square'))

    def play_explosion(self):
        duration = 0.3
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-16384, 16384) for _ in range(samples * 2)]
        self.channels[2].play(pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        ))

    def play_player_hit(self):
        self.channels[3].play(self.create_tone(150, 0.5, 0.4, 'sawtooth'))

    def play_barrier_hit(self):
        self.channels[2].play(self.create_tone(400, 0.1, 0.1, 'sawtooth'))


# --- CLASSES ---

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.0)
        self.brightness = random.randint(50, 255)
        self.alpha = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        alpha = int(self.alpha * (self.y / HEIGHT * 0.3 + 0.7))
        color = (self.brightness, self.brightness, self.brightness)
        surface.set_alpha(alpha)
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        surface.fill(color, rect, special_flags=pygame.BLEND_RGBA_MULT)


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-3, 3)
        self.life, self.decay = 1.0, random.uniform(0.02, 0.05)
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        surface.set_alpha(alpha)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size * self.life))


class Bullet:
    def __init__(self, x, y, is_player=False, size=4):
        self.x, self.y = x, y
        self.width, self.height = size, size * 2
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -BULLET_SPEED if is_player else ENEMY_BULLET_SPEED
        self.active = True

    def update(self):
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        surface.fill(self.color, self.rect)


class Invader:
    def __init__(self, x, y, row, col):
        self.x, self.y = x, y
        self.start_x, self.start_y = x, y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        self.color = ENEMY_3_COLOR if row == 0 else (ENEMY_2_COLOR if row < 3 else ENEMY_1_COLOR)
        self.score_value = 30 if row == 0 else (20 if row < 3 else 10)
        self.animation_offset = random.randint(0, 10)
        self.active = True
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(3000, 6000)
        self.is_on_cooldown = False

    def update(self, time, move_step_x, move_step_y):
        sine_offset = math.sin(time * 0.02 + self.animation_offset) * 10
        self.x = self.start_x + sine_offset
        self.y = self.start_y + move_step_y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        color = self.color
        surface.fill(color, (self.x + 4, self.y + 4, self.width - 8, self.height - 6))
        surface.fill((0, 0, 0), (self.x + 7, self.y + 7, 4, 4))
        surface.fill((0, 0, 0), (self.x + self.width - 11, self.y + 7, 4, 4))
        if (self.row % 2 == 0):
            surface.fill(color, (self.x, self.y + 8, 4, 8))
            surface.fill(color, (self.x + self.width - 4, self.y + 8, 4, 8))
            surface.fill(color, (self.x + 4, self.y + self.height - 4, 6, 4))
            surface.fill(color, (self.x + self.width - 10, self.y + self.height - 4, 6, 4))
        else:
            surface.fill(color, (self.x - 2, self.y + 6, 6, 4))
            surface.fill(color, (self.x + self.width - 4, self.y + 6, 6, 4))


class UFO:
    def __init__(self):
        self.width = 50
        self.height = 25
        self.y = 50
        self.speed = 4  # Increased speed for better visibility
        self.move_down_step = 20  # More noticeable downward movement
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(8000, 15000)
        self.active = True
        self.score_value = 50
        self.rect = pygame.Rect(0, self.y, self.width, self.height)

        # Spawn on the LEFT side, moving RIGHT (clearer movement pattern)
        self.x = 20
        self.direction = 1  # 1 = moving right, -1 = moving left

    def update(self):
        # Move horizontally
        self.x += self.speed * self.direction

        # Check left edge
        if self.x < 10:
            self.x = 10
            self.y += self.move_down_step
            self.direction = 1  # Change direction to move right

        # Check right edge
        elif self.x > WIDTH - self.width - 10:
            self.x = WIDTH - self.width - 10
            self.y += self.move_down_step
            self.direction = -1  # Change direction to move left

        # Check if moved too far down (out of play)
        if self.y > HEIGHT - 150:
            self.active = False

        # Update rect position
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def shoot(self, game):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown:
            bullet_x = self.x + self.width // 2
            bullet_y = self.y + self.height
            bullet = Bullet(bullet_x, bullet_y, is_player=False, size=6)
            game.enemy_bullets.append(bullet)
            self.last_shot_time = current_time
            game.sound_manager.play_ufo_shoot()

    def draw(self, surface):
        # UFO body (oval)
        pygame.draw.ellipse(surface, UFO_COLOR, (self.x, self.y, self.width, self.height))
        # Dome
        pygame.draw.circle(surface, (200, 200, 255), (self.x + self.width // 2, self.y + 8), 6)
        # Lights
        for i in range(3):
            pygame.draw.circle(surface, (255, 0, 0), (self.x + 10 + i * 12, self.y + self.height - 4), 2)
        # Legs
        pygame.draw.line(surface, UFO_COLOR, (self.x + 10, self.y + self.height),
                         (self.x + 10, self.y + self.height + 4), 2)
        pygame.draw.line(surface, UFO_COLOR, (self.x + 25, self.y + self.height),
                         (self.x + 25, self.y + self.height + 4), 2)
        pygame.draw.line(surface, UFO_COLOR, (self.x + 40, self.y + self.height),
                         (self.x + 40, self.y + self.height + 4), 2)


class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.active = True
        self.segments = []
        self.create_segments()
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def create_segments(self):
        segment_width = 5
        segment_height = 5
        for row in range(self.height // segment_height):
            for col in range(self.width // segment_width):
                self.segments.append({
                    'x': self.x + col * segment_width,
                    'y': self.y + row * segment_height,
                    'width': segment_width,
                    'height': segment_height,
                    'active': True
                })

    def update(self):
        active_segments = [s for s in self.segments if s['active']]
        if not active_segments:
            self.active = False
            return
        min_x = min(s['x'] for s in active_segments)
        min_y = min(s['y'] for s in active_segments)
        max_x = max(s['x'] + s['width'] for s in active_segments)
        max_y = max(s['y'] + s['height'] for s in active_segments)
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def take_damage(self, bullet_rect):
        for segment in self.segments:
            if segment['active']:
                seg_rect = pygame.Rect(segment['x'], segment['y'], segment['width'], segment['height'])
                if bullet_rect.colliderect(seg_rect):
                    segment['active'] = False
                    return True
        return False

    def draw(self, surface):
        for segment in self.segments:
            if segment['active']:
                color = BARRIER_COLOR
                if segment['x'] > self.x + self.width // 2 - 5 and segment['x'] < self.x + self.width // 2 + 5:
                    color = (100, 255, 255)
                surface.fill(color, (segment['x'], segment['y'], segment['width'], segment['height']))


class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2 - 20, HEIGHT - 50
        self.width, self.height = 40, 24
        self.color = PLAYER_COLOR
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.active = True
        self.lives = PLAYER_LIVES
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        current_time = pygame.time.get_ticks()
        pygame.draw.polygon(surface, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width, self.y + self.height - 8),
            (self.x + self.width - 10, self.y + self.height - 8),
            (self.x + 10, self.y + self.height - 8),
            (self.x, self.y + self.height - 8),
            (self.x, self.y + self.height)
        ])
        glow_size = 5 + int(math.sin(current_time * 0.03) * 3)
        pygame.draw.circle(surface, (255, 255, 100), (self.x + self.width // 2, self.y + self.height), glow_size)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders - Enhanced")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 24, bold=True)
        self.large_font = pygame.font.SysFont("Courier New", 48, bold=True)
        self.sound_manager = SoundManager()

        self.state = "START"
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.ufo = None
        self.particles = []
        self.stars = [Star() for _ in range(100)]
        self.barrriers = []
        self.enemy_direction = 1
        self.enemy_move_speed = 10
        self.enemy_drop_distance = 20
        self.last_enemy_move_time = 0
        self.enemy_move_interval = 500
        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(15000, 30000)

        self.init_enemies()
        self.init_barriers()

    def init_enemies(self):
        self.enemies = []
        padding_x, padding_y, start_x, start_y = 15, 25, 50, 60
        for row in range(NUM_ENEMIES_ROWS):
            for col in range(NUM_ENEMIES_COLS):
                x = start_x + col * (35 + padding_x)
                y = start_y + row * (35 + padding_y)
                self.enemies.append(Invader(x, y, row, col))
        self.enemy_move_speed = 8 + (self.level * 1.5)

    def init_barriers(self):
        self.barrriers = []
        barrier_spacing = WIDTH // (MAX_BARRIERS + 1)
        for i in range(MAX_BARRIERS):
            barrier_x = barrier_spacing * (i + 1) - 30
            barrier_y = HEIGHT - 150
            self.barrriers.append(Barrier(barrier_x, barrier_y))

    def spawn_explosion(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def reset_game(self):
        self.player = Player()
        self.score, self.level = 0, 1
        self.init_enemies()
        self.init_barriers()
        self.enemy_move_speed = 8
        self.enemy_direction = 1
        self.enemy_bullets = []
        self.particles = []
        self.ufo = None
        self.state = "PLAYING"

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.state == "START":
            if keys[pygame.K_SPACE]:
                self.reset_game()
        elif self.state == "PLAYING":
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and current_time - self.player.last_shot > self.player.shoot_delay:
                bullet_x = self.player.x + self.player.width // 2
                bullet_y = self.player.y
                bullet = Bullet(bullet_x, bullet_y, is_player=True)
                self.player.bullets.append(bullet)
                self.player.last_shot = current_time
                self.sound_manager.play_shoot()
            self.player.update(keys)
            for b in self.player.bullets:
                b.update()
            self.player.bullets = [b for b in self.player.bullets if b.active]
            for b in self.enemy_bullets:
                b.update()
            self.enemy_bullets = [b for b in self.enemy_bullets if b.active]
        elif self.state in ["GAMEOVER", "VICTORY"]:
            if keys[pygame.K_SPACE]:
                self.reset_game()

    def update_logic(self):
        current_time = pygame.time.get_ticks()
        for star in self.stars:
            star.update()

        if self.state == "PLAYING":
            # UFO Spawning
            if self.ufo_spawn_time == 0:
                self.ufo_spawn_time = current_time
            elif current_time - self.ufo_spawn_time > self.ufo_spawn_interval:
                self.ufo = UFO()
                self.ufo_spawn_time = current_time
                self.ufo_spawn_interval = random.randint(15000, 30000)

            # UFO Movement and Shooting
            if self.ufo and self.ufo.active:
                # UPDATE UFO POSITION EVERY FRAME
                self.ufo.update()
                # UFO shoots occasionally
                if random.random() < 0.01:
                    self.ufo.shoot(self)
                if not self.ufo.active:
                    self.ufo = None

            # Enemy movement with fixed interval
            if current_time - self.last_enemy_move_time > self.enemy_move_interval:
                self.last_enemy_move_time = current_time
                self.enemy_move_interval = max(100, 500 - self.level * 50)

                move_step = self.enemy_move_speed * self.enemy_direction
                edge_reached = False
                for enemy in self.enemies:
                    if enemy.active:
                        enemy.x += move_step
                        if (enemy.x + enemy.width > WIDTH - 30 and self.enemy_direction == 1) or \
                                (enemy.x < 30 and self.enemy_direction == -1):
                            edge_reached = True

                if edge_reached:
                    self.enemy_direction *= -1
                    for enemy in self.enemies:
                        enemy.y += self.enemy_drop_distance
                        enemy.x += move_step

            # Enemy shooting
            bullets_to_add = 0
            for enemy in self.enemies:
                if enemy.active and not enemy.is_on_cooldown:
                    if current_time - enemy.last_shot_time > enemy.shot_cooldown:
                        if random.random() < ENEMY_SHOOT_CHANCE:
                            bullets_to_add += 1

            bullets_to_add = min(bullets_to_add, MAX_ENEMY_BULLETS - len(self.enemy_bullets))
            if bullets_to_add > 0 and len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                active_enemies = [e for e in self.enemies if e.active and not e.is_on_cooldown]
                if active_enemies:
                    selected_enemies = random.sample(active_enemies, min(len(active_enemies), bullets_to_add))
                    for enemy in selected_enemies:
                        if len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                            bullet_x = enemy.x + enemy.width // 2
                            bullet_y = enemy.y + enemy.height
                            bullet = Bullet(bullet_x, bullet_y, is_player=False)
                            self.enemy_bullets.append(bullet)
                            enemy.last_shot_time = current_time
                            enemy.is_on_cooldown = True
                            self.sound_manager.play_enemy_shoot()

            # Reset cooldowns
            for enemy in self.enemies:
                if enemy.is_on_cooldown and (current_time - enemy.last_shot_time > enemy.shot_cooldown * 1.2):
                    enemy.is_on_cooldown = False

            # Update barriers
            for barrier in self.barrriers:
                barrier.update()

            # COLLISIONS
            # 1. Player Bullets vs Enemies
            for b in self.player.bullets[:]:
                hit = False
                for enemy in self.enemies:
                    if enemy.active and b.rect.colliderect(enemy.rect):
                        enemy.active = False
                        b.active = False
                        self.score += enemy.score_value
                        self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color)
                        self.sound_manager.play_explosion()
                        hit = True
                        break

                if hit:
                    continue
                # Bullet vs Barrier
                for barrier in self.barrriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                        self.sound_manager.play_barrier_hit()
                        break

                if b.active:
                    for eb in self.enemy_bullets[:]:
                        if b.rect.colliderect(eb.rect):
                            b.active = False
                            eb.active = False
                            self.spawn_explosion(b.x, b.y, (255, 255, 255))
                            break

            # 2. Enemy Bullets vs Player
            for b in self.enemy_bullets[:]:
                if b.rect.colliderect(self.player.rect):
                    b.active = False
                    self.player_hit()
                    break

            # 3. Enemy Bullets vs Barriers
            for b in self.enemy_bullets[:]:
                for barrier in self.barrriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR)
                        self.sound_manager.play_barrier_hit()
                        break

            # 4. Enemies vs Player
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color)
                    enemy.active = False
                    break

            # 5. UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player.bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2,
                                             UFO_COLOR)
                        self.sound_manager.play_explosion()
                        self.ufo.active = False
                        self.ufo = None
                        break

            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 2
                self.init_enemies()
                self.score += 1000
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255))

            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

    def player_hit(self):
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color
        )
        self.sound_manager.play_player_hit()
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score

    def draw(self):
        self.screen.fill(BG_COLOR)
        for star in self.stars:
            star.draw(self.screen)

        if self.state == "START":
            self.draw_center_text("SPACE INVADERS", self.large_font, (0, 255, 200), -80)
            self.draw_center_text("Press SPACE to Start", self.font, TEXT_COLOR, 20)
            self.draw_center_text("Arrows to Move | SPACE to Shoot", self.font, (150, 150, 150), 70)
            self.draw_center_text("Protect yourself behind barriers!", self.font, (150, 150, 150), 120)
        elif self.state == "PLAYING":
            self.player.draw(self.screen)
            for barrier in self.barrriers:
                if barrier.active:
                    barrier.draw(self.screen)
            for enemy in self.enemies:
                if enemy.active:
                    enemy.update(pygame.time.get_ticks(), 0, 0)
                    enemy.draw(self.screen)
            if self.ufo and self.ufo.active:
                self.ufo.draw(self.screen)
            for b in self.player.bullets:
                b.draw(self.screen)
            for b in self.enemy_bullets:
                b.draw(self.screen)
            for p in self.particles:
                p.draw(self.screen)

            score_surf = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, TEXT_COLOR)
            level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
            ufo_surf = self.font.render("UFO: 50pts", True, UFO_COLOR)
            self.screen.blit(score_surf, (10, 10))
            self.screen.blit(lives_surf, (WIDTH - 120, 10))
            self.screen.blit(level_surf, (WIDTH // 2 - 50, 10))
            self.screen.blit(ufo_surf, (WIDTH // 2 - 100, 40))
        elif self.state in ["GAMEOVER", "VICTORY"]:
            title = "GAME OVER" if self.state == "GAMEOVER" else "VICTORY!"
            color = (255, 50, 50) if self.state == "GAMEOVER" else (50, 255, 50)
            self.draw_center_text(title, self.large_font, color, -80)
            self.draw_center_text(f"Final Score: {self.score}", self.font, TEXT_COLOR, -30)
            self.draw_center_text(f"High Score: {self.high_score}", self.font, (255, 215, 0), 20)
            self.draw_center_text("Press SPACE to Play Again", self.font, (150, 150, 150), 80)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 20))
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()

    def draw_center_text(self, text, font, color, y_offset):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        text_shadow = font.render(text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        self.screen.blit(text_surf, text_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.handle_input()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
