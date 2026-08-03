# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files for resources (e.g. for graphic or for sound), but feel free to use external temp files or files to store game progress and stats. Make sure game will have barriers for user spaceship to hide, several levels bonus system to keep player engaged. Also include sound in game as well.
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1 --spec-type draft-mtp --spec-draft-n-max 2 --model /AI/models/Huihui-Qwen3.6-27B-abliterated-ggml-model-Q8_0.gguf  --mmproj /AI/models/Qwen3.6-27B-mmproj-F32.gguf


import pygame
import math
import json
import os
import io
import random

# ================= CONFIGURATION =================
WIDTH, HEIGHT = 900, 700
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 8
ENEMY_BASE_SPEED = 1.5
ENEMY_DROP = 15
STATS_FILE = "space_invaders_stats.json"

# Colors
C_BG = (10, 12, 20)
C_PLAYER = (0, 200, 255)
C_ENEMY_1 = (255, 100, 100)
C_ENEMY_2 = (100, 255, 150)
C_ENEMY_3 = (255, 200, 50)
C_BULLET = (200, 200, 255)
C_BARRIER = (0, 180, 180)
C_POWERUP = (255, 200, 255)
C_TEXT = (255, 255, 255)
C_SCANLINE = (0, 0, 0, 30)

ENEMY_COLORS = {1: C_ENEMY_1, 2: C_ENEMY_2, 3: C_ENEMY_3}


# ================= SOUND GENERATION =================
def generate_wav(freq, duration, volume=0.5, wave_type='sine'):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    header = b'RIFF'
    size = 36 + n_samples * 2
    header += size.to_bytes(4, 'little')
    header += b'WAVEfmt '
    header += (16).to_bytes(4, 'little')
    header += (1).to_bytes(2, 'little')
    header += (1).to_bytes(2, 'little')
    header += sample_rate.to_bytes(4, 'little')
    header += (sample_rate * 2).to_bytes(4, 'little')
    header += (2).to_bytes(2, 'little')
    header += (16).to_bytes(2, 'little')
    header += b'data'
    header += (n_samples * 2).to_bytes(4, 'little')

    data = []
    for i in range(n_samples):
        t = i / sample_rate
        env = 1.0 - (i / n_samples)
        if wave_type == 'noise':
            val = int((random.random() * 2 - 1) * 32767 * env * volume)
        else:
            val = int(math.sin(2 * math.pi * freq * t) * 32767 * env * volume)
        data.extend(val.to_bytes(2, 'little', signed=True))
    return pygame.mixer.Sound(header + bytes(data))


# ================= ASSET GENERATION =================
def create_surface(w, h, color):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect())
    return surf


def draw_sprite(surface, pattern, pixel_size, color):
    for y, row in enumerate(pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x * pixel_size, y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(surface, color, rect)


PLAYER_PATTERN = [
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 1]
]

ENEMY_PATTERNS = {
    1: [[1, 0, 1, 1, 1, 0, 1], [0, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 0, 1],
        [0, 1, 0, 0, 0, 1, 0]],
    2: [[0, 1, 1, 1, 1, 1, 0], [1, 1, 0, 1, 0, 1, 1], [1, 1, 1, 1, 1, 1, 1], [0, 0, 1, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 1, 0]],
    3: [[1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 1, 1]]
}


def load_sprites():
    sprites = {}
    sprites['player'] = create_surface(35, 25, C_PLAYER)
    draw_sprite(sprites['player'], PLAYER_PATTERN, 5, (255, 255, 255))

    for i in range(1, 4):
        sprites[f'enemy_{i}'] = create_surface(35, 25, ENEMY_COLORS[i])
        draw_sprite(sprites[f'enemy_{i}'], ENEMY_PATTERNS[i], 5, (255, 255, 255))

    sprites['bullet'] = create_surface(4, 12, C_BULLET)
    pygame.draw.rect(sprites['bullet'], (255, 255, 255), sprites['bullet'].get_rect())

    sprites['powerup'] = create_surface(20, 20, C_POWERUP)
    pygame.draw.circle(sprites['powerup'], (255, 255, 255), (10, 10), 8)
    return sprites


# ================= PARTICLE SYSTEM =================
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.uniform(15, 40)
        self.color = color
        self.size = random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.96
        return self.life > 0

    def draw(self, screen):
        alpha = int(self.life / 40 * 255)
        pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))


# ================= GAME ENTITIES =================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_sprites()['player']
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 200
        self.last_shot = 0
        self.powerups = {'shield': 0, 'rapid': 0, 'multi': 0}
        self.max_lives = 3
        self.lives = self.max_lives

    def update(self, keys, bullets_group):
        now = pygame.time.get_ticks()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, HEIGHT - 60, WIDTH, 60))

        if keys[pygame.K_SPACE] and now - self.last_shot > (100 if self.powerups['rapid'] > 0 else self.shoot_cooldown):
            self.shoot(bullets_group)
            self.last_shot = now

        for key in self.powerups:
            if self.powerups[key] > 0: self.powerups[key] -= 1

    def shoot(self, bullets_group):
        if self.powerups['multi'] > 0:
            for ang in [-0.2, 0, 0.2]:
                bullets_group.add(Bullet(self.rect.centerx, self.rect.top, 0, -BULLET_SPEED, ang))
        else:
            bullets_group.add(Bullet(self.rect.centerx, self.rect.top, 0, -BULLET_SPEED))

    # ADDED: Missing hit method
    def hit(self):
        if self.powerups['shield'] > 0:
            self.powerups['shield'] = 0
            return
        self.lives -= 1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.image = load_sprites()[f'enemy_{enemy_type}']
        self.rect = self.image.get_rect(center=(x, y))
        self.type = enemy_type
        self.shoot_chance = 0.005 + (enemy_type * 0.002)
        self.points = enemy_type * 10


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, angle=0):
        super().__init__()
        self.image = load_sprites()['bullet']
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = vx + math.sin(angle) * BULLET_SPEED
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if not (0 < self.rect.y < HEIGHT): self.kill()


class BarrierBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_surface(8, 8, C_BARRIER)
        self.rect = self.image.get_rect(topleft=(x, y))


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype):
        super().__init__()
        self.image = load_sprites()['powerup']
        self.rect = self.image.get_rect(center=(x, y))
        self.ptype = ptype
        self.vy = 2

    def update(self):
        self.rect.y += self.vy
        if self.rect.y > HEIGHT: self.kill()


# ================= MAIN GAME CLASS =================
class SpaceInvadersGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 24)
        self.big_font = pygame.font.SysFont('consolas', 48, bold=True)

        self.snd_shoot = generate_wav(880, 0.1, 0.3)
        self.snd_enemy_shoot = generate_wav(440, 0.15, 0.2)
        self.snd_explosion = generate_wav(100, 0.25, 0.4, 'noise')
        self.snd_powerup = generate_wav(1200, 0.2, 0.3)
        self.snd_levelup = generate_wav(600, 0.4, 0.4)

        self.sprites = load_sprites()
        self.state = 'MENU'
        self.stats = self.load_stats()
        self.reset_game()

        self.scan_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.scan_surf, C_SCANLINE, (0, y), (WIDTH, y))

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f: return json.load(f)
        return {"high_score": 0, "levels_cleared": 0, "games_played": 0}

    def save_stats(self):
        with open(STATS_FILE, 'w') as f: json.dump(self.stats, f, indent=2)

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.combo = 1
        self.player = Player(WIDTH // 2, HEIGHT - 40)
        self.player_group = pygame.sprite.Group(self.player)
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.barrier_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.particles = []
        self.enemy_move_timer = 0
        self.enemy_drop = False
        self.level_timer = 0
        self.create_level()

    def create_level(self):
        self.enemy_group.empty()
        self.bullet_group.empty()
        self.enemy_bullet_group.empty()
        self.barrier_group.empty()
        self.powerup_group.empty()
        self.particles.clear()
        self.player.rect.center = (WIDTH // 2, HEIGHT - 40)
        self.player.powerups = {'shield': 0, 'rapid': 0, 'multi': 0}

        for bx in range(4):
            base_x = 150 + bx * 180
            for by in range(12):
                for bl in range(8):
                    if by < 4 or bl < 2 or bl > 5:
                        self.barrier_group.add(BarrierBlock(base_x + bl * 8, HEIGHT - 120 + by * 8))

        rows = min(5, 3 + self.level // 2)
        cols = min(10, 8 + self.level // 3)
        spacing_x, spacing_y = 55, 45
        start_x = (WIDTH - (cols * spacing_x)) // 2 + spacing_x // 2
        start_y = 80

        for r in range(rows):
            for c in range(cols):
                etype = random.randint(1, 3)
                if self.level > 3 and random.random() < 0.3: etype = 3
                if self.level > 6 and random.random() < 0.4: etype = 3
                self.enemy_group.add(Enemy(start_x + c * spacing_x, start_y + r * spacing_y, etype))

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count): self.particles.append(Particle(x, y, color))

    def update(self):
        if self.state == 'MENU':
            if pygame.key.get_pressed()[pygame.K_RETURN] or pygame.key.get_pressed()[pygame.K_SPACE]:
                self.state = 'PLAYING'
                self.reset_game()
            return

        if self.state == 'GAMEOVER':
            if pygame.key.get_pressed()[pygame.K_r]:
                self.state = 'MENU'
                self.reset_game()
            return

        if self.state == 'LEVELUP':
            self.level_timer += 1
            if self.level_timer > 90:
                self.state = 'PLAYING'
                self.level += 1
                self.create_level()
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.bullet_group)

        self.enemy_move_timer += 1
        speed_mod = 1 + (self.level * 0.15)
        if self.enemy_move_timer >= max(5, 30 - self.level):
            self.enemy_move_timer = 0
            move_dir = 1 if not self.enemy_drop else -1
            for e in self.enemy_group:
                e.rect.x += move_dir * 10 * speed_mod
                if e.type == 3 and not self.enemy_drop:
                    if random.random() < e.shoot_chance * speed_mod:
                        self.enemy_bullet_group.add(Bullet(e.rect.centerx, e.rect.bottom, 0, 4, 0))
                        self.snd_enemy_shoot.play()

            if self.enemy_group:
                left_min = min(e.rect.left for e in self.enemy_group)
                right_max = max(e.rect.right for e in self.enemy_group)
                if (right_max > WIDTH - 20 and not self.enemy_drop) or (left_min < 20 and self.enemy_drop):
                    self.enemy_drop = not self.enemy_drop
                    for e in self.enemy_group:
                        e.rect.y += ENEMY_DROP

        self.bullet_group.update()
        self.enemy_bullet_group.update()
        self.powerup_group.update()

        hits = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, True)
        for e_list in hits.values():
            for e in e_list:
                self.score += e.points * self.combo
                self.spawn_particles(e.rect.centerx, e.rect.centery, ENEMY_COLORS[e.type], 15)
                self.snd_explosion.play()
                if random.random() < 0.05:
                    self.powerup_group.add(PowerUp(e.rect.centerx, e.rect.centery,
                                                   random.choice(['shield', 'rapid', 'multi', 'life', 'score'])))
                self.combo = min(self.combo + 0.1, 5)

        barrier_hits = pygame.sprite.groupcollide(self.bullet_group, self.barrier_group, True, True)
        for b in barrier_hits:
            self.spawn_particles(b.rect.centerx, b.rect.centery, C_BARRIER, 5)

        p_hits = pygame.sprite.groupcollide(self.enemy_bullet_group, self.player_group, True, False)
        if p_hits:
            self.player.hit()
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, C_PLAYER, 20)
            self.snd_explosion.play()
            self.combo = 1
            if self.player.lives <= 0:
                self.stats['games_played'] += 1
                if self.score > self.stats['high_score']: self.stats['high_score'] = self.score
                if self.level > self.stats['levels_cleared']: self.stats['levels_cleared'] = self.level
                self.save_stats()
                self.state = 'GAMEOVER'

        barrier_hits_e = pygame.sprite.groupcollide(self.enemy_bullet_group, self.barrier_group, True, True)
        for b in barrier_hits_e:
            self.spawn_particles(b.rect.centerx, b.rect.centery, C_BARRIER, 5)

        pickups = pygame.sprite.spritecollide(self.player, self.powerup_group, True)
        for pu in pickups:
            self.snd_powerup.play()
            if pu.ptype == 'shield':
                self.player.powerups['shield'] = 600
            elif pu.ptype == 'rapid':
                self.player.powerups['rapid'] = 600
            elif pu.ptype == 'multi':
                self.player.powerups['multi'] = 400
            elif pu.ptype == 'life':
                self.player.lives = min(self.player.lives + 1, self.player.max_lives + 2)
            elif pu.ptype == 'score':
                self.score += 500

        self.particles = [p for p in self.particles if p.update()]
        if not p_hits and self.combo > 1: self.combo = max(1, self.combo - 0.02)

        if not self.enemy_group:
            self.state = 'LEVELUP'
            self.level_timer = 0
            self.score += 1000 * self.level
            self.snd_levelup.play()
            self.save_stats()

    def draw(self):
        self.screen.fill(C_BG)
        self.screen.blit(self.scan_surf, (0, 0))

        for e in self.enemy_group: self.screen.blit(e.image, e.rect)
        for b in self.bullet_group: self.screen.blit(b.image, b.rect)
        for eb in self.enemy_bullet_group: self.screen.blit(eb.image, eb.rect)
        for br in self.barrier_group: self.screen.blit(br.image, br.rect)
        for p in self.powerup_group: self.screen.blit(p.image, p.rect)

        self.screen.blit(self.player.image, self.player.rect)
        if self.player.powerups['shield'] > 0:
            pygame.draw.circle(self.screen, (255, 255, 255, 100), self.player.rect.center, 25, 2)
        if self.player.powerups['rapid'] > 0:
            pygame.draw.circle(self.screen, (255, 100, 0, 100), self.player.rect.center, 28, 2)

        for p in self.particles: p.draw(self.screen)

        self.screen.blit(self.font.render(f"SCORE: {int(self.score)}", True, C_TEXT), (20, 20))
        self.screen.blit(self.font.render(f"LEVEL: {self.level}", True, C_TEXT), (20, 50))
        self.screen.blit(self.font.render(f"LIVES: {self.player.lives}", True, C_TEXT), (WIDTH - 120, 20))
        self.screen.blit(self.font.render(f"COMBO: {self.combo:.1f}x", True, (255, 200, 50)), (WIDTH - 120, 50))

        if self.state == 'MENU':
            self.draw_center_text("NEON SPACE INVADERS", self.big_font, 100)
            self.draw_center_text("Press SPACE or ENTER to Start", self.font, 180)
            self.draw_center_text(f"High Score: {self.stats['high_score']}", self.font, 230)
            self.draw_center_text("A/D or Arrows to Move | SPACE to Shoot", self.font, 300)
        elif self.state == 'GAMEOVER':
            self.draw_center_text("GAME OVER", self.big_font, -50)
            self.draw_center_text(f"Final Score: {int(self.score)}", self.font, 0)
            self.draw_center_text("Press R to Return to Menu", self.font, 50)
        elif self.state == 'LEVELUP':
            self.draw_center_text(f"LEVEL {self.level} COMPLETE!", self.big_font, -50)
            self.draw_center_text(f"Level {self.level + 1} Starting...", self.font, 0)

    def draw_center_text(self, text, font, offset_y=0):
        surf = font.render(text, True, C_TEXT)
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - surf.get_height() // 2 + offset_y))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.stats['games_played'] += 1
            if self.score > self.stats['high_score']: self.stats['high_score'] = self.score
            if self.level > self.stats['levels_cleared']: self.stats['levels_cleared'] = self.level
            self.save_stats()
            pygame.quit()
            import sys;
            sys.exit()


def main():
    game = SpaceInvadersGame()
    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        game.update()
        game.draw()
        pygame.display.flip()
        game.clock.tick(FPS)


if __name__ == "__main__":
    main()
