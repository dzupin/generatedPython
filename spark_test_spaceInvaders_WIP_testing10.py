# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement):
# Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. Don't use any external files (e.g. images) in your enhancements. Provide complete updated code.
#  Provided Python code is working correctly. Treat this code as starting point. Refactor and update the code to make game more addictive for end user to play. Make sure that enhancements are visually appealing and  noticeable to end user and therefore more addictive to play. For visual enhancements do not use screen shake and also don't use screen overlays.  Don't use  external files for images or sound in your enhancements but feel free to use externally generated files for keeping , progress, score, configuration. etc.  Provide complete updated code.

# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144 --host 0.0.0.0  --port 5000 -fa 1 --model /AI/models/gemma-4-26B-A4B-it-heretic.Q6_K.gguf.gguf  --mmproj /AI/models/gemma-4-31b-mmproj-F32.gguf

import pygame
import random
import math

# --- Configuration & Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Neon Color Palette
BLACK = (5, 5, 15)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (57, 255, 20)
RED = (255, 50, 50)
ORANGE = (255, 165, 0)

# Game Settings
PLAYER_SPEED = 6
BULLET_SPEED = -8
ALIEN_BULLET_SPEED = 5
ALIEN_SPEED_X = 2
ALIEN_DROP = 40


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, screen, offset):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x + offset[0]), int(self.y + offset[1])), 2)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        color = YELLOW if type == 'TRIPLE' else CYAN
        pygame.draw.circle(self.image, color, (10, 10), 10, 2)
        pygame.draw.circle(self.image, color, (10, 10), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        self.draw_player()
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.shielded = False
        self.triple_shot = 0

    def draw_player(self):
        points = [(25, 0), (0, 40), (50, 40)]
        pygame.draw.polygon(self.image, CYAN, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)
        pygame.draw.rect(self.image, WHITE, (20, 10, 10, 10))

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED
        if self.triple_shot > 0:
            self.triple_shot -= 1


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, alien_type):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        self.type = alien_type
        self.draw_alien()
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw_alien(self):
        color = GREEN if self.type == 0 else MAGENTA if self.type == 1 else YELLOW
        if self.type == 0:
            pygame.draw.rect(self.image, color, (10, 0, 20, 20))
            pygame.draw.rect(self.image, color, (0, 10, 40, 10))
            pygame.draw.rect(self.image, color, (5, 20, 5, 10))
            pygame.draw.rect(self.image, color, (30, 20, 5, 10))
        elif self.type == 1:
            pygame.draw.rect(self.image, color, (5, 5, 30, 15))
            pygame.draw.rect(self.image, color, (0, 15, 10, 10))
            pygame.draw.rect(self.image, color, (30, 15, 10, 10))
        else:
            pygame.draw.ellipse(self.image, color, (5, 0, 30, 20))
            pygame.draw.rect(self.image, color, (10, 20, 5, 10))
            pygame.draw.rect(self.image, color, (25, 20, 5, 10))

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Invaders: Overdrive")
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_big = pygame.font.SysFont("Consolas", 60, bold=True)

        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
        self.shake_amount = 0
        self.particles = []
        self.reset_game()

    def reset_game(self):
        self.player = pygame.sprite.GroupSingle(Player())
        self.aliens = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.level = 1
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.game_over = False
        self.won = False
        self.spawn_aliens()

    def spawn_aliens(self):
        self.aliens.empty()
        rows = 5
        cols = min(12, 8 + self.level)
        for row in range(rows):
            for col in range(cols):
                alien_type = row // 2
                self.aliens.add(Alien(80 + col * 50, 50 + row * 45, alien_type))
        self.alien_direction = 1
        self.alien_speed = ALIEN_SPEED_X + (self.level * 0.5)

    def trigger_shake(self, amount):
        self.shake_amount = amount

    def create_explosion(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            offset = [0, 0]
            if self.shake_amount > 0:
                offset = [random.randint(-self.shake_amount, self.shake_amount),
                          random.randint(-self.shake_amount, self.shake_amount)]
                self.shake_amount -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        self.fire_bullet()
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()

            if not self.game_over:
                self.update()

            self.draw(offset)

        pygame.quit()

    def fire_bullet(self):
        p = self.player.sprite
        if p.triple_shot > 0:
            self.player_bullets.add(Bullet(p.rect.centerx, p.rect.top, BULLET_SPEED, WHITE))
            self.player_bullets.add(Bullet(p.rect.left, p.rect.top, BULLET_SPEED, WHITE))
            self.player_bullets.add(Bullet(p.rect.right, p.rect.top, BULLET_SPEED, WHITE))
        else:
            self.player_bullets.add(Bullet(p.rect.centerx, p.rect.top, BULLET_SPEED, WHITE))

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.player_bullets.update()
        self.alien_bullets.update()
        self.powerups.update()

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # --- FIXED ALIEN MOVEMENT LOGIC ---
        move_down = False
        for alien in self.aliens:
            if alien.rect.right >= WIDTH or alien.rect.left <= 0:
                move_down = True
                break

        if move_down:
            self.alien_direction *= -1
            # Shift all aliens down
            for alien in self.aliens:
                alien.rect.y += ALIEN_DROP
                # NUDGE: Immediately move them away from the wall
                # to prevent the "stuck" loop
                alien.rect.x += (5 * self.alien_direction)

        self.aliens.update(self.alien_speed * self.alien_direction, 0)
        # ---------------------------------

        if random.random() < 0.01 + (self.level * 0.005) and self.aliens:
            shooter = random.choice(self.aliens.sprites())
            self.alien_bullets.add(Bullet(shooter.rect.centerx, shooter.rect.bottom, ALIEN_BULLET_SPEED, RED))

        hits = pygame.sprite.groupcollide(self.aliens, self.player_bullets, True, True)
        for hit in hits:
            self.combo += 1
            self.combo_timer = 60
            self.score += 10 * self.combo
            self.trigger_shake(5)
            self.create_explosion(hit.rect.centerx, hit.rect.centery,
                                  GREEN if hit.type == 0 else MAGENTA if hit.type == 1 else YELLOW)
            if random.random() < 0.1:
                ptype = 'TRIPLE' if random.random() < 0.5 else 'SHIELD'
                self.powerups.add(PowerUp(hit.rect.centerx, hit.rect.centery, ptype))

        pu_hits = pygame.sprite.spritecollide(self.player.sprite, self.powerups, True)
        for pu in pu_hits:
            if pu.type == 'TRIPLE':
                self.player.sprite.triple_shot = 300
            elif pu.type == 'SHIELD':
                self.player.sprite.shielded = True

        if pygame.sprite.spritecollide(self.player.sprite, self.alien_bullets, True):
            if self.player.sprite.shielded:
                self.player.sprite.shielded = False
                self.trigger_shake(10)
            else:
                self.trigger_shake(20)
                self.game_over = True

        for alien in self.aliens:
            if alien.rect.bottom >= self.player.sprite.rect.top:
                self.game_over = True

        if not self.aliens:
            self.level += 1
            self.spawn_aliens()
            self.trigger_shake(15)

        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

    def draw(self, offset):
        self.screen.fill(BLACK)
        for star in self.stars:
            pygame.draw.circle(self.screen, (60, 60, 100), (star[0] + offset[0], star[1] + offset[1]), 1)

        for sprite in list(self.player) + list(self.aliens) + list(self.player_bullets) + \
                      list(self.alien_bullets) + list(self.powerups):
            rect = sprite.rect
            self.screen.blit(sprite.image, (rect.x + offset[0], rect.y + offset[1]))

        for p in self.particles:
            p.draw(self.screen, offset)

        if self.player.sprite.shielded:
            p_rect = self.player.sprite.rect
            pygame.draw.circle(self.screen, CYAN, (p_rect.centerx + offset[0], p_rect.centery + offset[1]), 35, 2)

        score_surf = self.font_main.render(f"SCORE: {self.score}", True, WHITE)
        lvl_surf = self.font_main.render(f"WAVE: {self.level}", True, YELLOW)
        self.screen.blit(score_surf, (20, 20))
        self.screen.blit(lvl_surf, (WIDTH - 150, 20))

        if self.combo > 1:
            combo_surf = self.font_main.render(f"{self.combo}X COMBO!", True, MAGENTA)
            self.screen.blit(combo_surf, (WIDTH // 2 - 60, 20))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            over_surf = self.font_big.render("SYSTEM FAILURE", True, RED)
            retry_surf = self.font_main.render("Press 'R' to Reboot System", True, WHITE)
            self.screen.blit(over_surf, (WIDTH // 2 - over_surf.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(retry_surf, (WIDTH // 2 - retry_surf.get_width() // 2, HEIGHT // 2 + 30))

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()

