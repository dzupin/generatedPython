# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-27B-heretic-v2-Q8_0.gguf  --mmproj /AI/models/Qwen3.5-27B-mmproj-F32.gguf


import pygame
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 5
MAX_ENEMY_BULLETS = 6
NUM_ENEMIES_ROWS = 5
NUM_ENEMIES_COLS = 8

# Game Balance
PLAYER_SHOOT_DELAY = 250  # Faster shooting
ENEMY_SHOOT_CHANCE = 0.08  # Slightly more aggressive
PLAYER_LIVES = 3
MAX_BARRIERS = 4

# Colors
BG_COLOR = (15, 15, 30)
PLAYER_COLOR = (0, 255, 200)
ENEMY_1_COLOR = (255, 80, 80)
ENEMY_2_COLOR = (0, 255, 100)
ENEMY_3_COLOR = (150, 0, 255)
TEXT_COLOR = (255, 255, 255)
BULLET_COLOR = (0, 255, 255)
ENEMY_BULLET_COLOR = (255, 200, 0)
UFO_COLOR = (255, 100, 255)
BARRIER_COLOR = (0, 200, 200)
SCORE_POPUP_COLOR = (255, 255, 0)


# --- AUDIO SYSTEM ---
class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 512)
        self.channels = [pygame.mixer.Channel(i) for i in range(5)]
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
            elif wave_type == 'sawtooth':
                value = ((2 * (t * freq - math.floor(t * freq + 0.5))))
                sample_val = int(max_sample * vol * value)
            else:
                sample_val = int(max_sample * vol * math.sin(2 * math.pi * freq * t))
            buffer[s * 2] = sample_val
            buffer[s * 2 + 1] = sample_val
        return pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        )

    def play_shoot(self):
        self.channels[0].play(self.create_tone(880, 0.1, 0.2, 'square'))

    def play_enemy_shoot(self):
        self.channels[1].play(self.create_tone(200, 0.15, 0.15, 'sawtooth'))

    def play_ufo_shoot(self):
        self.channels[0].play(self.create_tone(1200, 0.08, 0.25, 'square'))

    def play_explosion(self):
        duration = 0.3
        samples = int(self.sample_rate * duration)
        buffer = [random.randint(-16384, 16384) for _ in range(samples * 2)]
        self.channels[2].play(pygame.sndarray.make_sound(
            pygame.sndarray.array(buffer).astype('int16').reshape((-1, 2))
        ))

    def play_player_hit(self):
        self.channels[3].play(self.create_tone(150, 0.6, 0.4, 'sawtooth'))

    def play_barrier_hit(self):
        self.channels[2].play(self.create_tone(300, 0.05, 0.05, 'sawtooth'))

    def play_level_up(self):
        # A simple arpeggio for level up
        for i, f in enumerate([440, 554, 659, 880]):
            self.channels[4].play(self.create_tone(f, 0.1, 0.2, 'square'))
            pygame.time.delay(50)


# --- CLASSES ---

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 3.0)  # Faster for depth
        self.brightness = random.randint(100, 255)
        self.alpha = random.randint(150, 255)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            self.size = random.randint(1, 3)

    def draw(self, surface):
        alpha = int(self.alpha * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.04 + self.x)))
        color = (self.brightness, self.brightness, self.brightness)
        surface.set_alpha(alpha)
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        surface.fill(color, rect, special_flags=pygame.BLEND_RGBA_MULT)


class Particle:
    def __init__(self, x, y, color, size=2):
        self.x, self.y, self.color = x, y, color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life, self.decay = 1.0, random.uniform(0.03, 0.08)
        self.size = size

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
    def __init__(self, x, y, is_player=False, size=3):
        self.x, self.y = x, y
        self.width, self.height = size, size * 3
        self.is_player = is_player
        self.color = BULLET_COLOR if is_player else ENEMY_BULLET_COLOR
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.velocity_y = -BULLET_SPEED if is_player else ENEMY_BULLET_SPEED
        self.active = True
        # Trail effect
        self.trail = []

    def update(self):
        self.y += self.velocity_y
        self.rect.topleft = (self.x - self.width // 2, self.y)

        # Add trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        if self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 - (len(self.trail) - i) * 20)
            color = self.color
            if self.is_player:
                color = (0, 200, 255)
            else:
                color = (255, 150, 50)
            surface.set_alpha(alpha)
            pygame.draw.circle(surface, color, (int(tx), int(ty)), int(self.width))

        surface.set_alpha(255)
        surface.fill(self.color, self.rect)


class Invader:
    def __init__(self, x, y, row, col):
        self.base_x = x
        self.base_y = y
        self.row, self.col = row, col
        self.width, self.height = 30, 20
        # Gradient colors based on row
        self.color = ENEMY_3_COLOR if row == 0 else (ENEMY_2_COLOR if row < 3 else ENEMY_1_COLOR)
        self.score_value = 30 if row == 0 else (20 if row < 3 else 10)
        self.animation_offset = random.randint(0, 10)
        self.active = True
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(3000, 6000)
        self.is_on_cooldown = False
        self.rect = pygame.Rect(self.base_x, self.base_y, self.width, self.height)

    def update(self, current_time):
        # Visual wobble
        sine_offset = math.sin(current_time * 0.02 + self.animation_offset) * 8

        visual_x = self.base_x + sine_offset
        visual_y = self.base_y

        self.rect.topleft = (int(visual_x), int(visual_y))
        self.x = visual_x
        self.y = visual_y

    def draw(self, surface):
        color = self.color
        px, py = int(self.rect.x), int(self.rect.y)

        # Animation: Squash and stretch
        time = pygame.time.get_ticks()
        scale_x = 1 + 0.1 * math.sin(time * 0.04 + self.col * 0.5)
        scale_y = 1 - 0.1 * math.sin(time * 0.04 + self.col * 0.5)

        # Draw body
        body_rect = pygame.Rect(px, py, int(self.width * scale_x), int(self.height * scale_y))
        surface.fill(color, body_rect)

        # Draw eyes (black)
        eye_size = 4
        eye_x = px + 8
        eye_y = py + 8
        surface.fill((0, 0, 0), (eye_x, eye_y, eye_size, eye_size))
        surface.fill((0, 0, 0), (px + self.width - 8 - eye_size, eye_y, eye_size, eye_size))

        # Draw legs (animation)
        leg_w = 2
        leg_h = 4
        if self.row % 2 == 0:
            # Row 0, 2, 4 style
            surface.fill(color, (px + 4, py + self.height - 4, leg_w, leg_h))
            surface.fill(color, (px + self.width - 4 - leg_w, py + self.height - 4, leg_w, leg_h))
        else:
            # Row 1, 3 style
            surface.fill(color, (px + 2, py + self.height - 6, leg_w, leg_h))
            surface.fill(color, (px + self.width - 2 - leg_w, py + self.height - 6, leg_w, leg_h))


class UFO:
    def __init__(self):
        self.width = 60
        self.height = 30
        self.y = 40
        self.speed = 5
        self.move_down_step = 25
        self.last_shot_time = 0
        self.shot_cooldown = random.randint(10000, 20000)
        self.active = True
        self.score_value = 150
        self.rect = pygame.Rect(0, self.y, self.width, self.height)
        self.x = 20
        self.direction = 1
        self.particles = []

    def update(self):
        self.x += self.speed * self.direction

        # Trail particles
        if random.random() < 0.3:
            self.particles.append(Particle(self.x + (self.direction * -20), self.y + self.height, UFO_COLOR, 2))

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

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def shoot(self, game):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown:
            bullet_x = self.x + self.width // 2
            bullet_y = self.y + self.height
            bullet = Bullet(bullet_x, bullet_y, is_player=False, size=5)
            game.enemy_bullets.append(bullet)
            self.last_shot_time = current_time
            game.sound_manager.play_ufo_shoot()

    def draw(self, surface):
        # Draw particles
        for p in self.particles:
            p.draw(surface)

        # UFO Body
        surface.set_alpha(255)
        pygame.draw.ellipse(surface, UFO_COLOR, (self.x, self.y, self.width, self.height))
        # Dome
        pygame.draw.circle(surface, (200, 200, 255), (int(self.x + self.width // 2), int(self.y + 8)), 8)
        # Lights
        for i in range(4):
            color = (255, 0, 0) if i % 2 == 0 else (0, 255, 0)
            pygame.draw.circle(surface, color, (int(self.x + 10 + i * 14), int(self.y + self.height - 5)), 2)
        # Legs
        pygame.draw.line(surface, UFO_COLOR, (int(self.x + 15), int(self.y + self.height)),
                         (int(self.x + 15), int(self.y + self.height + 6)), 2)
        pygame.draw.line(surface, UFO_COLOR, (int(self.x + 25), int(self.y + self.height)),
                         (int(self.x + 25), int(self.y + self.height + 6)), 2)
        pygame.draw.line(surface, UFO_COLOR, (int(self.x + 35), int(self.y + self.height)),
                         (int(self.x + 35), int(self.y + self.height + 6)), 2)
        pygame.draw.line(surface, UFO_COLOR, (int(self.x + 45), int(self.y + self.height)),
                         (int(self.x + 45), int(self.y + self.height + 6)), 2)


class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 50
        self.active = True
        self.segments = []
        self.create_segments()
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def create_segments(self):
        segment_width = 6
        segment_height = 6
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
                # Add some gradient effect
                if segment['y'] < self.y + 10:
                    color = (0, 255, 255)
                elif segment['y'] > self.y + 30:
                    color = (0, 150, 150)

                # Draw the main segment
                surface.fill(color, (segment['x'], segment['y'], segment['width'], segment['height']))

                # Draw the border
                # Ensure rect is a tuple of 4 integers (x, y, w, h) and width is a keyword arg
                rect_tuple = (int(segment['x']), int(segment['y']), int(segment['width']), int(segment['height']))
                pygame.draw.rect(surface, (50, 200, 200), rect_tuple, width=1)


class ScorePopup:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.life = 1.0
        self.decay = 0.02
        self.velocity_y = -2

    def update(self):
        self.y += self.velocity_y
        self.life -= self.decay
        self.velocity_y *= 0.95

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        color = (255, 255, 0)
        font = pygame.font.SysFont("Courier New", 16, bold=True)
        text = font.render(f"+{self.value}", True, color)
        text_surf = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
        text_surf.set_alpha(alpha)
        text_surf.blit(text, (0, 0))
        surface.blit(text_surf, (int(self.x), int(self.y)))


class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2 - 20, HEIGHT - 60
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

        # Pulsing glow
        glow_size = 10 + int(math.sin(current_time * 0.05) * 5)
        glow_color = (200, 200, 255)
        surface.set_alpha(150)
        pygame.draw.circle(surface, glow_color, (int(self.x + self.width // 2), int(self.y + self.height)), glow_size)
        surface.set_alpha(255)

        # Ship Body
        pygame.draw.polygon(surface, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width, self.y + self.height - 8),
            (self.x + self.width - 10, self.y + self.height - 8),
            (self.x + 10, self.y + self.height - 8),
            (self.x, self.y + self.height - 8),
            (self.x, self.y + self.height)
        ])

        # Engine flame
        flame_h = 10 + int(math.sin(current_time * 0.1) * 5)
        pygame.draw.polygon(surface, (255, 100, 0), [
            (self.x + self.width // 2, self.y + self.height),
            (self.x + self.width // 2 - 3, self.y + self.height + flame_h),
            (self.x + self.width // 2 + 3, self.y + self.height + flame_h)
        ])


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders - Enhanced")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 24, bold=True)
        self.large_font = pygame.font.SysFont("Courier New", 48, bold=True)
        self.score_font = pygame.font.SysFont("Courier New", 16, bold=True)
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
        self.enemy_move_interval = 400
        self.ufo_spawn_time = 0
        self.ufo_spawn_interval = random.randint(15000, 30000)
        self.score_popups = []

        # Screen shake
        self.shake_duration = 0
        self.shake_magnitude = 0

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
        self.enemy_move_speed = 8 + (self.level * 2)

    def init_barriers(self):
        self.barrriers = []
        barrier_spacing = WIDTH // (MAX_BARRIERS + 1)
        for i in range(MAX_BARRIERS):
            barrier_x = barrier_spacing * (i + 1) - 30
            barrier_y = HEIGHT - 150
            self.barrriers.append(Barrier(barrier_x, barrier_y))

    def spawn_explosion(self, x, y, color, size=15):
        for _ in range(size):
            self.particles.append(Particle(x, y, color))

        # Screen shake
        if size > 10:
            self.shake_duration = 15
            self.shake_magnitude = 8

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
        self.score_popups = []

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
                self.ufo.update()
                if random.random() < 0.01:
                    self.ufo.shoot(self)
                if not self.ufo.active:
                    self.ufo = None

            # Enemy movement logic
            if current_time - self.last_enemy_move_time > self.enemy_move_interval:
                self.last_enemy_move_time = current_time
                self.enemy_move_interval = max(100, 500 - self.level * 80)  # Faster progression

                move_step = self.enemy_move_speed * self.enemy_direction
                edge_reached = False

                for enemy in self.enemies:
                    if enemy.active:
                        if (enemy.base_x + enemy.width > WIDTH - 30 and self.enemy_direction == 1) or \
                                (enemy.base_x < 30 and self.enemy_direction == -1):
                            edge_reached = True
                            break

                if edge_reached:
                    self.enemy_direction *= -1
                    move_step = self.enemy_move_speed * self.enemy_direction

                    for enemy in self.enemies:
                        if enemy.active:
                            enemy.base_y += self.enemy_drop_distance
                            enemy.base_x += move_step
                else:
                    for enemy in self.enemies:
                        if enemy.active:
                            enemy.base_x += move_step

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
                            bullet_x = enemy.base_x + enemy.width // 2
                            bullet_y = enemy.base_y + enemy.height
                            bullet = Bullet(bullet_x, bullet_y, is_player=False)
                            self.enemy_bullets.append(bullet)
                            enemy.last_shot_time = current_time
                            enemy.is_on_cooldown = True
                            self.sound_manager.play_enemy_shoot()

            for enemy in self.enemies:
                if enemy.is_on_cooldown and (current_time - enemy.last_shot_time > enemy.shot_cooldown * 1.2):
                    enemy.is_on_cooldown = False

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
                        self.score_popups.append(ScorePopup(enemy.base_x, enemy.base_y, enemy.score_value))
                        self.spawn_explosion(enemy.base_x + enemy.width // 2, enemy.base_y + enemy.height // 2,
                                             enemy.color)
                        self.sound_manager.play_explosion()
                        hit = True
                        break

                if hit:
                    continue
                # Bullet vs Barrier
                for barrier in self.barrriers:
                    if barrier.active and barrier.take_damage(b.rect):
                        b.active = False
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, size=8)
                        self.sound_manager.play_barrier_hit()
                        break

                if b.active:
                    for eb in self.enemy_bullets[:]:
                        if b.rect.colliderect(eb.rect):
                            b.active = False
                            eb.active = False
                            self.spawn_explosion(b.x, b.y, (255, 255, 255), size=10)
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
                        self.spawn_explosion(b.x, b.y, BARRIER_COLOR, size=8)
                        self.sound_manager.play_barrier_hit()
                        break

            # 4. Enemies vs Player
            for enemy in self.enemies:
                if enemy.active and enemy.base_y + enemy.height >= self.player.y:
                    self.player_hit()
                    self.spawn_explosion(enemy.base_x, enemy.base_y, enemy.color)
                    enemy.active = False
                    break

            # 5. UFO Collision
            if self.ufo and self.ufo.active:
                for b in self.player.bullets[:]:
                    if b.active and b.rect.colliderect(self.ufo.rect):
                        b.active = False
                        self.score += self.ufo.score_value
                        self.spawn_explosion(self.ufo.x + self.ufo.width // 2, self.ufo.y + self.ufo.height // 2,
                                             UFO_COLOR, size=30)
                        self.sound_manager.play_explosion()
                        self.ufo.active = False
                        self.ufo = None
                        break

            if not any(e.active for e in self.enemies):
                self.level += 1
                self.enemy_move_speed += 2
                self.init_enemies()
                self.score += 1000
                self.spawn_explosion(WIDTH // 2, HEIGHT // 2, (255, 255, 255), size=50)
                self.sound_manager.play_level_up()

            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            for sp in self.score_popups:
                sp.update()
            self.score_popups = [sp for sp in self.score_popups if sp.life > 0]

        # Screen shake decay
        if self.shake_duration > 0:
            self.shake_duration -= 1

    def player_hit(self):
        self.spawn_explosion(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            self.player.color,
            size=20
        )
        self.sound_manager.play_player_hit()
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score

    def draw(self):
        # Screen shake effect
        offset_x = 0
        offset_y = 0
        if self.shake_duration > 0:
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)

            # Create a temporary surface for the shake
            temp_screen = pygame.Surface((WIDTH, HEIGHT))
            temp_screen.fill(BG_COLOR)

            for star in self.stars:
                star.draw(temp_screen)
            if self.state == "PLAYING":
                self.player.draw(temp_screen)
                for barrier in self.barrriers:
                    if barrier.active:
                        barrier.draw(temp_screen)
                for enemy in self.enemies:
                    if enemy.active:
                        enemy.update(pygame.time.get_ticks())
                        enemy.draw(temp_screen)
                if self.ufo and self.ufo.active:
                    self.ufo.draw(temp_screen)
                for b in self.player.bullets:
                    b.draw(temp_screen)
                for b in self.enemy_bullets:
                    b.draw(temp_screen)
                for p in self.particles:
                    p.draw(temp_screen)
                for sp in self.score_popups:
                    sp.draw(temp_screen)

                self.screen.blit(temp_screen, (offset_x, offset_y))
            else:
                self.screen.blit(temp_screen, (offset_x, offset_y))
        else:
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
                        enemy.update(pygame.time.get_ticks())
                        enemy.draw(self.screen)
                if self.ufo and self.ufo.active:
                    self.ufo.draw(self.screen)
                for b in self.player.bullets:
                    b.draw(self.screen)
                for b in self.enemy_bullets:
                    b.draw(self.screen)
                for p in self.particles:
                    p.draw(self.screen)
                for sp in self.score_popups:
                    sp.draw(self.screen)

                score_surf = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
                lives_surf = self.font.render(f"LIVES: {self.player.lives}", True, TEXT_COLOR)
                level_surf = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
                ufo_surf = self.score_font.render("UFO: 150pts", True, UFO_COLOR)

                self.screen.blit(score_surf, (10, 10))
                self.screen.blit(lives_surf, (WIDTH - 150, 10))
                self.screen.blit(level_surf, (WIDTH // 2 - 50, 10))
                self.screen.blit(ufo_surf, (WIDTH // 2 - 80, 40))
            elif self.state in ["GAMEOVER", "VICTORY"]:
                title = "GAME OVER" if self.state == "GAMEOVER" else "VICTORY!"
                color = (255, 50, 50) if self.state == "GAMEOVER" else (50, 255, 50)
                self.draw_center_text(title, self.large_font, color, -80)
                self.draw_center_text(f"Final Score: {self.score}", self.font, TEXT_COLOR, -30)
                self.draw_center_text(f"High Score: {self.high_score}", self.font, (255, 215, 0), 20)
                self.draw_center_text("Press SPACE to Play Again", self.font, (150, 150, 150), 80)

        # CRT Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # 1. Slight white haze (optional)
        haze_color = (255, 255, 255, 20)
        overlay.fill(haze_color)

        # 2. Scanlines
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(overlay, (0, 0, 0, 100), (0, y), (WIDTH, y), 1)

        # 3. Vignette Effect (Darkens the corners)
        # We create a separate surface for the vignette to control alpha blending precisely
        vignette_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Draw a large black circle at the center of the vignette surface
        # The radius should be large enough to cover the screen diagonally
        vignette_radius = min(WIDTH, HEIGHT) // 2 + 100  # Make it larger than screen
        vignette_center = (WIDTH // 2, HEIGHT // 2)

        # We want the edges dark and center light.
        # So we draw a black circle, but we will invert the logic or use a gradient.
        # A simpler way: Draw a large black rectangle, then cut out a lighter circle in the middle.
        vignette_surf.fill((0, 0, 0, 100))  # Dark base for the whole screen

        # Now draw a lighter circle in the middle to "cut out" the view area
        # We use a radial gradient for the cut-out.
        # Instead of a complex gradient, let's just draw a large, semi-transparent circle in the middle.
        # This effectively makes the center less dark than the edges.
        center_circle_radius = min(WIDTH, HEIGHT) // 2 - 50  # Slightly smaller than screen
        pygame.draw.circle(vignette_surf, (0, 0, 0, 50), vignette_center, center_circle_radius)

        # Blit the vignette onto the main overlay
        overlay.blit(vignette_surf, (0, 0))

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

