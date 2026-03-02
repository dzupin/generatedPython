# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.

import pygame
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 9
ENEMY_BULLET_SPEED = 5
MAX_ENEMY_BULLETS = 6
NUM_ENEMIES_ROWS = 4
NUM_ENEMIES_COLS = 8

# Game Balance
PLAYER_SHOOT_DELAY = 250
ENEMY_SHOOT_CHANCE = 0.02
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
EXPLOSION_COLORS = [(255, 69, 0), (255, 165, 0), (255, 255, 0), (255, 255, 255)]


# --- AUDIO SYSTEM ---
class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(44100, -16, 2, 512)
        except:
            pass  # Fallback if audio init fails
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
        try:
            self.channels[0].play(self.create_tone(880, 0.1, 0.2, 'square'))
        except:
            pass

    def play_enemy_shoot(self):
        try:
            self.channels[1].play(self.create_tone(150, 0.2, 0.15, 'sawtooth'))
        except:
            pass

    def play_ufo_shoot(self):
        try:
            self.channels[0].play(self.create_tone(1200, 0.1, 0.25, 'square'))
        except:
            pass

    def play_explosion(self, pitch=1.0):
        try:
            duration = 0.3
            samples = int(self.sample_rate * duration)
            buffer = [random.randint(-16384, 16384) for _ in range(samples * 2)]
            sound = pygame.sndarray.make_sound(
                pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
            )
            # Pitch shift simulation by changing speed (not implemented here for simplicity, just volume)
            self.channels[2].play(sound)
        except:
            pass

    def play_player_hit(self):
        try:
            self.channels[3].play(self.create_tone(100, 0.6, 0.4, 'sawtooth'))
        except:
            pass

    def play_barrier_hit(self):
        try:
            self.channels[2].play(self.create_tone(400, 0.05, 0.1, 'sawtooth'))
        except:
            pass


# --- CLASSES ---

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 3.0)
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
        # Use a temporary surface for alpha blending
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, alpha), (self.size // 2, self.size // 2), self.size // 2)
        surface.blit(surf, (self.x, self.y), special_flags=pygame.BLEND_RGBA_ADD)


class Particle:
    def __init__(self, x, y, color, speed_mag=3.0):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, speed_mag)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life, self.max_life = 1.0, random.uniform(0.4, 0.8)
        self.decay = 1.0 / self.max_life
        self.size = random.randint(2, 5)
        self.gravity = 0.05

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Add gravity
        self.life -= self.decay
        self.size *= 0.95  # Shrink

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        color = (*self.color[:3], alpha)
        surf = pygame.Surface((int(self.size) * 2, int(self.size) * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (int(self.size), int(self.size)), int(self.size))
        surface.blit(surf, (int(self.x), int(self.y)), special_flags=pygame.BLEND_RGBA_ADD)


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = 1.0
        self.vy = -1.0

    def update(self):
        self.y += self.vy
        self.life -= 0.02

    def draw(self, surface, font):
        if self.life <= 0: return
        alpha = int(self.life * 255)
        surf = font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        surface.blit(surf, (int(self.x), int(self.y)))


class Bullet:
    def __init__(self, x, y, is_player=False, size=4):
        self.x, self.y = x, y
        self.width, self.height = size, size * 2
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -BULLET_SPEED if is_player else ENEMY_BULLET_SPEED
        self.active = True
        self.trail = []

    def update(self):
        # Create trail effect
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)
        if self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            s = pygame.Surface((self.width, self.height))
            s.fill(self.color)
            s.set_alpha(alpha)
            surface.blit(s, (tx - self.width // 2, ty))

        surface.fill(self.color, self.rect)


class Invader:
    def __init__(self, x, y, row, col):
        self.x, self.y = x, y
        self.logical_x, self.logical_y = x, y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        self.color = ENEMY_3_COLOR if row == 0 else (ENEMY_2_COLOR if row < 3 else ENEMY_1_COLOR)
        self.score_value = 30 if row == 0 else (20 if row < 3 else 10)
        self.animation_offset = random.randint(0, 10)
        self.active = True
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(3000, 6000)
        self.is_on_cooldown = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.wobble_phase = random.uniform(0, 10)

    def update(self, time, move_step_x, move_step_y):
        self.logical_x += move_step_x
        self.logical_y += move_step_y

        # Enhanced wobble: combine sine with a slight vertical bob
        sine_offset = math.sin(time * 0.05 + self.animation_offset) * 4
        bob_offset = math.sin(time * 0.1 + self.wobble_phase) * 2
        self.x = self.logical_x + sine_offset
        self.y = self.logical_y + bob_offset

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        # Draw body
        surface.fill(self.color, (self.x + 4, self.y + 4, self.width - 8, self.height - 6))
        # Draw eyes (glowing)
        surface.fill((255, 255, 255), (self.x + 7, self.y + 7, 4, 4))
        surface.fill((255, 255, 255), (self.x + self.width - 11, self.y + 7, 4, 4))
        surface.fill((0, 0, 0), (self.x + 8, self.y + 8, 2, 2))
        surface.fill((0, 0, 0), (self.x + self.width - 10, self.y + 8, 2, 2))

        # Decorative legs based on row
        if (self.row % 2 == 0):
            surface.fill(self.color, (self.x, self.y + 8, 4, 8))
            surface.fill(self.color, (self.x + self.width - 4, self.y + 8, 4, 8))
        else:
            surface.fill(self.color, (self.x - 2, self.y + 6, 6, 4))
            surface.fill(self.color, (self.x + self.width - 4, self.y + 6, 6, 4))


class UFO:
    def __init__(self):
        self.width = 50
        self.height = 25
        self.y = 50
        self.speed = 5
        self.move_down_step = 20
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(8000, 15000)
        self.active = True
        self.score_value = 50
        self.rect = pygame.Rect(0, self.y, self.width, self.height)
        self.x = -self.width
        self.direction = 1
        self.timer = 0

    def update(self):
        self.x += self.speed * self.direction
        self.timer += 1

        # Erratic movement
        if self.timer % 60 == 0:
            self.y += random.randint(-5, 5)

        if self.x < 10:
            self.x = 10
            self.y += self.move_down_step
            self.direction = 1
        elif self.x > WIDTH - self.width - 10:
            self.x = WIDTH - self.width - 10
            self.y += self.move_down_step
            self.direction = -1

        if self.y > HEIGHT - 150:
            self.active = False

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def shoot(self, game):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown:
            bullet_x = self.x + self.width // 2
            bullet_y = self.y + self.height
            bullet = Bullet(bullet_x, bullet_y, is_player=False, size=8)
            game.enemy_bullets.append(bullet)
            self.last_shot_time = current_time
            game.sound_manager.play_ufo_shoot()

    def draw(self, surface):
        # Glowing UFO
        glow = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*UFO_COLOR, 50), (0, 0, self.width + 10, self.height + 10))
        surface.blit(glow, (self.x - 5, self.y - 5), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.ellipse(surface, UFO_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(surface, (200, 200, 255), (self.x + self.width // 2, self.y + 8), 6)

        # Rotating lights
        angle = pygame.time.get_ticks() * 0.005
        for i in range(3):
            lx = self.x + 10 + i * 12
            ly = self.y + self.height - 4 + math.sin(angle + i) * 2
            pygame.draw.circle(surface, (255, 0, 0), (int(lx), int(ly)), 3)


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
                # Gradient effect based on position
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
        self.thrust_frame = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)
        self.thrust_frame += 1

    def draw(self, surface):
        # Pulsing glow
        glow_size = 5 + abs(math.sin(pygame.time.get_ticks() * 0.01) * 5)
        glow_surf = pygame.Surface((self.width + glow_size * 2, self.height + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surf, (*self.color, 50), [
            (self.width // 2 + glow_size, 0),
            (self.width + glow_size, self.height + glow_size),
            (0, self.height + glow_size)
        ])
        surface.blit(glow_surf, (self.x - glow_size, self.y - glow_size), special_flags=pygame.BLEND_RGBA_ADD)

        # Ship body
        pygame.draw.polygon(surface, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width, self.y + self.height - 8),
            (self.x + self.width - 10, self.y + self.height - 8),
            (self.x + 10, self.y + self.height - 8),
            (self.x, self.y + self.height - 8),
            (self.x, self.y + self.height)
        ])

        # Engine thrust particles
        if self.thrust_frame % 5 == 0:
            pass  # Handled in game logic if needed, keeping draw clean


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders - Ultimate Edition")
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
        self.floating_texts = []
        self.stars = [Star() for _ in range(150)]
        self.barrriers = []

        # Dynamic Difficulty
        self.base_enemy_speed = 10
        self.enemy_direction = 1
        self.enemy_drop_distance = 20
        self.last_enemy_move_time = 0
        self.enemy_move_interval = 500

        # Visual Effects
        self.shake_offset = [0, 0]
        self.shake_duration = 0

        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(15000, 30000)

        # Combo System
        self.combo = 0
        self.combo_timer = 0

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
        # Reset speed based on level
        self.current_enemy_speed = self.base_enemy_speed + (self.level * 1.5)

    def init_barriers(self):
        self.barrriers = []
        barrier_spacing = WIDTH // (MAX_BARRIERS + 1)
        for i in range(MAX_BARRIERS):
            barrier_x = barrier_spacing * (i + 1) - 30
            barrier_y = HEIGHT - 150
            self.barrriers.append(Barrier(barrier_x, barrier_y))

    def add_shake(self, intensity):
        self.shake_duration = intensity
        self.shake_offset = [random.randint(-intensity, intensity), random.randint(-intensity, intensity)]

    def spawn_explosion(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def reset_game(self):
        self.player = Player()
        self.score = 0
        self.level = 1
        self.combo = 0
        self.init_enemies()
        self.init_barriers()
        self.current_enemy_speed = self.base_enemy_speed
        self.enemy_direction = 1
        self.enemy_bullets = []
        self.particles = []
        self.floating_texts = []
        self.ufo = None
        self.state = "PLAYING"
        self.shake_offset = [0, 0]

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

            # Update Bullets
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

        # Update Stars
        for star in self.stars:
            star.update()

        # Update Shake
        if self.shake_duration > 0:
            self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
            self.shake_duration -= 1
        else:
            self.shake_offset = [0, 0]

        if self.state == "PLAYING":
            # Combo Timer
            if self.combo > 0:
                self.combo_timer += 1
                if self.combo_timer > 180:  # 3 seconds
                    self.combo = 0

            # UFO Spawning
            if self.ufo_spawn_time == 0:
                self.ufo_spawn_time = current_time
            elif current_time - self.ufo_spawn_time > self.ufo_spawn_interval:
                self.ufo = UFO()
                self.ufo_spawn_time = current_time
                self.ufo_spawn_interval = random.randint(15000, 30000)

            # UFO Logic
            if self.ufo and self.ufo.active:
                self.ufo.update()
                if random.random() < 0.01:
                    self.ufo.shoot(self)
                if not self.ufo.active:
                    self.ufo = None

            # Enemy Movement Logic
            if current_time - self.last_enemy_move_time > self.enemy_move_interval:
                self.last_enemy_move_time = current_time

                # Speed increases as enemies die (fewer enemies = faster ticks)
                alive_count = sum(1 for e in self.enemies if e.active)
                if alive_count == 0:
                    self.level += 1
                    self.init_enemies()
                    self.score += 1000
                    self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), 50)
                    self.add_shake(10)
                    self.enemy_move_interval = max(50, 500 - self.level * 40)
                    self.current_enemy_speed = self.base_enemy_speed + (self.level * 1.5)
                else:
                    # Adjust interval based on alive count (classic mechanic)
                    # Fewer enemies = faster movement
                    factor = (NUM_ENEMIES_ROWS * NUM_ENEMIES_COLS) / alive_count
                    actual_interval = self.enemy_move_interval / factor

                move_step = self.current_enemy_speed * self.enemy_direction
                edge_reached = False

                # Check edges
                for enemy in self.enemies:
                    if enemy.active:
                        test_x = enemy.logical_x + move_step
                        if (test_x + enemy.width > WIDTH - 30 and self.enemy_direction == 1) or \
                                (test_x < 30 and self.enemy_direction == -1):
                            edge_reached = True
                            break

                if edge_reached:
                    self.enemy_direction *= -1
                    for enemy in self.enemies:
                        if enemy.active:
                            enemy.logical_y += self.enemy_drop_distance
                            enemy.logical_x += (self.current_enemy_speed * self.enemy_direction)  # Bounce back
                else:
                    for enemy in self.enemies:
                        if enemy.active:
                            enemy.logical_x += move_step

            # Enemy Shooting
            bullets_to_add = 0
            for enemy in self.enemies:
                if enemy.active and not enemy.is_on_cooldown:
                    if current_time - enemy.last_shot_time > enemy.shot_cooldown:
                        if random.random() < ENEMY_SHOOT_CHANCE * (1 + self.level * 0.1):
                            bullets_to_add += 1

            bullets_to_add = min(bullets_to_add, MAX_ENEMY_BULLETS - len(self.enemy_bullets))
            if bullets_to_add > 0 and len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                active_enemies = [e for e in self.enemies if e.active and not e.is_on_cooldown]
                if active_enemies:
                    selected_enemies = random.sample(active_enemies, min(len(active_enemies), bullets_to_add))
                    for enemy in selected_enemies:
                        if len(self.enemy_bullets) < MAX_ENEMY_BULLETS:
                            bullet = Bullet(enemy.x + enemy.width // 2, enemy.y + enemy.height, is_player=False, size=6)
                            self.enemy_bullets.append(bullet)
                            enemy.last_shot_time = current_time
                            enemy.is_on_cooldown = True
                            self.sound_manager.play_enemy_shoot()

            # Reset cooldowns
            for enemy in self.enemies:
                if enemy.is_on_cooldown and (current_time - enemy.last_shot_time > enemy.shot_cooldown * 1.2):
                    enemy.is_on_cooldown = False

            # Update Barriers
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

                        # Combo Logic
                        self.combo += 1
                        self.combo_timer = 0
                        combo_bonus = int(enemy.score_value * (1 + self.combo * 0.1))
                        self.score += int(enemy.score_value * 0.1 * self.combo)  # Bonus points

                        self.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color, 20)
                        self.sound_manager.play_explosion()

                        # Floating Text
                        text = f"+{enemy.score_value}"
                        if self.combo > 1:
                            text = f"COMBO x{self.combo}!"
                        self.floating_texts.append(FloatingText(enemy.x, enemy.y, text, (255, 255, 0)))

                        hit = True
                        break

                if hit:
                    continue

                # Bullet vs Barrier
                for barrier in self.barrriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, 5)
                        self.sound_manager.play_barrier_hit()
                        break

                if b.active:
                    for eb in self.enemy_bullets[:]:
                        if b.rect.colliderect(eb.rect):
                            b.active = False
                            eb.active = False
                            self.spawn_explosion(b.x, b.y, (255, 255, 255), 10)
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
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, 5)
                        self.sound_manager.play_barrier_hit()
                        break

            # 4. Enemies vs Player
            for enemy in self.enemies:
                if enemy.active and enemy.y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.x, enemy.y, enemy.color, 30)
                    enemy.active = False
                    self.add_shake(20)
                    break

            # 5. UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player.bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2,
                                             UFO_COLOR, 30)
                        self.sound_manager.play_explosion()
                        self.floating_texts.append(FloatingText(self.ufo.x, self.ufo.y, "UFO HIT! +50", (255, 0, 0)))
                        self.add_shake(15)
                        self.ufo.active = False
                        self.ufo = None
                        break

            # Cleanup
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            for ft in self.floating_texts:
                ft.update()
            self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

    def player_hit(self):
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color,
            40
        )
        self.sound_manager.play_player_hit()
        self.add_shake(25)
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Apply Shake
        shake_x, shake_y = self.shake_offset
        camera = pygame.Surface((WIDTH, HEIGHT))
        camera.fill(BG_COLOR)

        # Draw Stars
        for star in self.stars:
            star.draw(camera)

        if self.state == "START":
            self.draw_center_text("SPACE INVADERS", self.large_font, (0, 255, 200), -80)
            self.draw_center_text("Press SPACE to Start", self.font, TEXT_COLOR, 20)
            self.draw_center_text("Arrows to Move | SPACE to Shoot", self.font, (150, 150, 150), 70)

            # Draw decorative enemies in background
            for i in range(3):
                pygame.draw.rect(camera, ENEMY_3_COLOR, (WIDTH // 2 - 50 + i * 60, HEIGHT // 2 + 50, 30, 20))

        elif self.state == "PLAYING":
            self.player.draw(camera)
            for barrier in self.barrriers:
                if barrier.active:
                    barrier.draw(camera)
            for enemy in self.enemies:
                if enemy.active:
                    enemy.update(pygame.time.get_ticks(), 0, 0)
                    enemy.draw(camera)
            if self.ufo and self.ufo.active:
                self.ufo.draw(camera)
            for b in self.player.bullets:
                b.draw(camera)
            for b in self.enemy_bullets:
                b.draw(camera)
            for p in self.particles:
                p.draw(camera)
            for ft in self.floating_texts:
                ft.draw(camera, self.font)

            # UI
            score_surf = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, TEXT_COLOR)
            level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)

            # Combo Display
            if self.combo > 1:
                combo_surf = self.font.render(f"COMBO x{self.combo}!", True, (255, 255, 0))
                combo_rect = combo_surf.get_rect(center=(WIDTH // 2, 50))
                camera.blit(combo_surf, combo_rect)

            camera.blit(score_surf, (10, 10))
            camera.blit(lives_surf, (WIDTH - 120, 10))
            camera.blit(level_surf, (WIDTH // 2 - 50, 10))

            # UFO Alert
            if self.ufo:
                ufo_surf = self.font.render("UFO APPROACHING!", True, UFO_COLOR)
                camera.blit(ufo_surf, (WIDTH // 2 - 80, 40))

        elif self.state in ["GAMEOVER", "VICTORY"]:
            title = "GAME OVER" if self.state == "GAMEOVER" else "VICTORY!"
            color = (255, 50, 50) if self.state == "GAMEOVER" else (50, 255, 50)
            self.draw_center_text(title, self.large_font, color, -80)
            self.draw_center_text(f"Final Score: {self.score}", self.font, TEXT_COLOR, -30)
            self.draw_center_text(f"High Score: {self.high_score}", self.font, (255, 215, 0), 20)
            self.draw_center_text("Press SPACE to Play Again", self.font, (150, 150, 150), 80)

        # Blit camera to screen with shake
        self.screen.blit(camera, (shake_x, shake_y))

        # --- FIX START: Manual Vignette and Scanlines ---

        # 1. Scanlines (Retro CRT effect)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(0, HEIGHT, 4):
            pygame.draw.line(overlay, (0, 0, 0, 20), (0, i), (WIDTH, i))
        self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 2. Vignette (Darkening edges) - Replaces radial_gradient
        vignette_size = int(WIDTH * 0.8)
        vignette_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Draw a large black circle with alpha in the center, leaving edges dark
        # We actually want the opposite: transparent center, dark edges.
        # Easier approach: Draw a huge black circle with a hole? No, let's just draw semi-transparent black rects at corners
        # Or use a radial gradient simulation via multiple circles
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        max_radius = int(math.hypot(WIDTH, HEIGHT))

        # Simple vignette using concentric circles with increasing alpha
        for i in range(20, 100, 5):
            radius = int((i / 100) * max_radius)
            alpha = int((i / 100) * 100)  # Darker further out
            if alpha > 0:
                # We want dark edges, so we draw a large circle that covers everything but is transparent in the middle?
                # Actually, let's just draw a black surface with a transparent hole in the middle.
                pass

        # Efficient Vignette: Draw a black surface, then cut a hole in the middle using BLIND_SUBTRACT logic isn't easy in pygame.
        # Alternative: Draw radial gradient manually using circles from center outwards with increasing opacity
        for r in range(0, int(math.hypot(WIDTH, HEIGHT)) // 2, 40):
            dist_factor = r / (math.hypot(WIDTH, HEIGHT) // 2)
            alpha = int(dist_factor * 150)  # 0 at center, 150 at edge
            if alpha > 20:  # Skip very faint ones for performance
                pygame.draw.circle(vignette_surface, (0, 0, 0, alpha), (center_x, center_y), r + 50)

        # Better Vignette: Just draw a large semi-transparent black circle over the whole screen,
        # but we want the center clear.
        # Let's use the "Corner Darkening" method which is cheaper and looks retro.
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Draw 4 corner gradients (simulated by rects)
        pygame.draw.rect(vignette, (0, 0, 0, 60), (0, 0, WIDTH, 100))  # Top
        pygame.draw.rect(vignette, (0, 0, 0, 60), (0, HEIGHT - 100, WIDTH, 100))  # Bottom
        pygame.draw.rect(vignette, (0, 0, 0, 60), (0, 0, 100, HEIGHT))  # Left
        pygame.draw.rect(vignette, (0, 0, 0, 60), (WIDTH - 100, 0, 100, HEIGHT))  # Right

        # Apply vignette
        self.screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # --- FIX END ---

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
