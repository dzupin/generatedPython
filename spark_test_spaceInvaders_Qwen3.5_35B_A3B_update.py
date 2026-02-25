# PROMPT USED (create game baseline): Write Space Invaders game in python using pygame library, make it visually appealing but don't use any external files (e.g. for graphic).
# 0-shot  (best visuals for this game so far)
# PROMPT FOLLOW UP (game enhancement): Excellent. Python code is working correctly. Now update the code to make game more addictive for end user to play. Make sure that enhancement is visible to end user and therefore more addictive to play but also make sure to keep scope in reasonable level so that update will work correctly.
# /AI/llama.cpp/build/bin/llama-server --no-mmap -ngl 999 --jinja -c 262144  --host 0.0.0.0  --port 5000 -fa 1  --model /AI/models/Qwen3.5-35B-A3B-UD-Q8_K_XL.gguf  --mmproj /AI/models/Qwen3.5-35B-A3B_mmproj-BF16.gguf
# 1-shot to play followed by   more shots to cleanup later errors

import pygame
import random
import sys
import math

# --- Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG_TOP = (10, 10, 30)
COLOR_BG_BOTTOM = (20, 20, 60)
COLOR_PLAYER = (0, 255, 255)
COLOR_PLAYER_DARK = (0, 150, 150)
COLOR_PLAYER_SHIELD = (100, 100, 255)
COLOR_BULLET_PLAYER = (255, 255, 0)
COLOR_BULLET_ENEMY = (255, 100, 100)
COLOR_ALIEN_1 = (0, 255, 100)
COLOR_ALIEN_2 = (255, 255, 0)
COLOR_ALIEN_3 = (255, 100, 0)
COLOR_BOSS = (200, 50, 200)
COLOR_TEXT = (255, 255, 255)
COLOR_PARTICLE = (255, 255, 255)
COLOR_POWERUP = (255, 0, 255)
COLOR_POWERUP_SHIELD = (100, 100, 255)
COLOR_POWERUP_SLOW = (0, 200, 255)

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_BASE_SPEED = 1
ALIEN_DROP_HEIGHT = 30
FIRE_COOLDOWN = 25


# --- Helper Functions ---

def create_gradient_surface(width, height, top_color, bottom_color):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / height)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / height)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / height)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    return surf


def create_alien_surface(pixel_map, color):
    pixel_size = 4
    rows = len(pixel_map)
    cols = len(pixel_map[0]) if rows > 0 else 0
    w = cols * pixel_size
    h = rows * pixel_size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for r in range(rows):
        for c in range(cols):
            if pixel_map[r][c] == 1:
                rect = pygame.Rect(c * pixel_size, r * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(surf, color, rect)
    return surf


# Pixel Maps
ALIEN_MAP_1 = [[0, 0, 1, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
               [0, 1, 1, 0, 1, 1, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
               [1, 0, 1, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 1, 1, 1, 0, 0, 0]]
ALIEN_MAP_2 = [[0, 0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
               [1, 1, 0, 1, 1, 1, 1, 0, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
               [0, 1, 0, 0, 0, 0, 0, 0, 1, 0], [1, 0, 1, 0, 0, 0, 0, 1, 0, 1]]
ALIEN_MAP_3 = [[0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
               [0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 1, 0]]

# Pre-generate Aliens
ALIEN_1_Surf = create_alien_surface(ALIEN_MAP_1, COLOR_ALIEN_1)
ALIEN_2_Surf = create_alien_surface(ALIEN_MAP_2, COLOR_ALIEN_2)
ALIEN_3_Surf = create_alien_surface(ALIEN_MAP_3, COLOR_ALIEN_3)


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed=1.5):
        super().__init__()
        size = random.randint(2, 5)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        angle = random.uniform(0, 2 * math.pi)
        vel = random.uniform(1, speed)
        self.dx = math.cos(angle) * vel
        self.dy = math.sin(angle) * vel
        self.life = random.randint(15, 30)
        self.alpha = 255

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.life -= 1
        self.alpha = max(0, self.life * 10)
        self.image.set_alpha(self.alpha)
        if self.life <= 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_PLAYER, [(20, 0), (0, 30), (40, 30)])
        pygame.draw.polygon(self.image, COLOR_PLAYER_DARK, [(20, 5), (5, 25), (35, 25)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.cooldown = 0
        self.lives = 3
        self.shield = False
        self.power_level = 1
        self.slow_time = False
        self.invulnerable_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invulnerable_time > 0:
            self.invulnerable_time -= 1

    def shoot(self):
        if self.cooldown == 0:
            self.cooldown = FIRE_COOLDOWN
            bullets = []
            if self.power_level >= 1:
                b = Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED, COLOR_BULLET_PLAYER)
                bullets.append(b)
            if self.power_level >= 2:
                b = Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED, COLOR_BULLET_PLAYER)
                b.dx = -2
                b.dy = -6
                bullets.append(b)
            if self.power_level >= 3:
                b = Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED, COLOR_BULLET_PLAYER)
                b.dx = 2
                b.dy = -6
                bullets.append(b)
            return bullets
        return []


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y, color, dx=0):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_y = speed_y
        self.dx = dx

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.dx
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, alien_type, is_boss=False):
        super().__init__()
        self.alien_type = alien_type
        self.is_boss = is_boss
        if is_boss:
            self.image = pygame.Surface((80, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, COLOR_BOSS, (0, 0, 80, 60))
            pygame.draw.rect(self.image, (255, 255, 255), (10, 10, 20, 20))
            pygame.draw.rect(self.image, (255, 255, 255), (50, 10, 20, 20))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.hp = 20
            self.points = 500
        else:
            if alien_type == 1:
                self.image = ALIEN_1_Surf
            elif alien_type == 2:
                self.image = ALIEN_2_Surf
            else:
                self.image = ALIEN_3_Surf
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.hp = 1
            self.points = 30 if alien_type == 1 else 20 if alien_type == 2 else 10

    def update(self):
        pass


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        color = COLOR_POWERUP
        symbol = "S"
        if power_type == "SHIELD":
            color = COLOR_POWERUP_SHIELD
            symbol = "H"
        elif power_type == "SLOW":
            color = COLOR_POWERUP_SLOW
            symbol = "T"
        pygame.draw.circle(self.image, color, (10, 10), 10)
        font = pygame.font.SysFont("consolas", 12, bold=True)
        text = font.render(symbol, True, (0, 0, 0))
        self.image.blit(text, (5, 6))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Star:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, SCREEN_HEIGHT)

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -10
        self.speed = random.uniform(0.5, 2.0)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.reset()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super PyInvaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 40)
        self.reset_game()
        self.background = create_gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)
        self.stars = [Star() for _ in range(50)]
        self.shake_timer = 0
        self.flash_timer = 0
        self.combo = 0
        self.max_combo = 0
        self.last_kill_time = 0
        self.boss_active = False
        self.level_transition = False
        self.level_transition_timer = 0

    def reset_game(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        self.score = 0
        self.high_score = 0
        self.level = 1
        self.alien_move_speed = ALIEN_BASE_SPEED
        self.alien_dx = self.alien_move_speed
        self.alien_dy = ALIEN_DROP_HEIGHT
        self.alien_direction = 1
        self.game_over = False
        self.level_active = True
        self.boss_active = False
        self.level_transition = False
        self.spawn_aliens()

    def spawn_aliens(self):
        self.enemies.empty()
        self.bullets.empty()
        self.powerups.empty()
        self.particles.empty()
        self.all_sprites.add(self.player)

        if self.level % 5 == 0 and not self.boss_active:
            self.boss_active = True
            boss = Alien(SCREEN_WIDTH // 2, 50, 1, is_boss=True)
            self.enemies.add(boss)
            self.flash_screen()
            return

        rows = 5
        cols = 10
        spacing_x = 50
        spacing_y = 50
        start_x = (SCREEN_WIDTH - (cols * spacing_x)) // 2
        start_y = 50

        for r in range(rows):
            for c in range(cols):
                alien_type = (r % 3) + 1
                x = start_x + c * spacing_x
                y = start_y + r * spacing_y
                alien = Alien(x, y, alien_type)
                self.enemies.add(alien)

    def level_up(self):
        self.level += 1
        self.alien_move_speed = min(self.alien_move_speed + 0.3, 4)
        self.level_transition = True
        self.level_transition_timer = 120
        self.create_explosion(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 30, COLOR_TEXT)
        self.flash_screen()

        if self.level % 5 == 0:
            self.boss_active = True
            boss = Alien(SCREEN_WIDTH // 2, 50, 1, is_boss=True)
            self.enemies.add(boss)
        else:
            self.boss_active = False
            self.spawn_aliens()

    def create_explosion(self, x, y, count=15, color=None):
        c = color if color else random.choice([COLOR_BULLET_PLAYER, COLOR_ALIEN_1, COLOR_ALIEN_2])
        for _ in range(count):
            self.particles.add(Particle(x, y, c))
        self.shake_screen(5)

    def shake_screen(self, intensity):
        self.shake_timer = intensity

    def flash_screen(self):
        self.flash_timer = 5

    def check_collisions(self):
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += hit.points * (1 + self.combo // 10)
            self.create_explosion(hit.rect.centerx, hit.rect.centery, 20, hit.image.get_at((10, 10)))
            self.last_kill_time = pygame.time.get_ticks()
            self.combo += 1
            if self.combo > self.max_combo: self.max_combo = self.combo

            drop_chance = 0.05 + (self.level * 0.01)
            if hit.is_boss: drop_chance = 0.4

            if random.random() < drop_chance:
                types = ["POWER", "SHIELD", "SLOW"]
                pu_type = random.choice(types)
                self.powerups.add(PowerUp(hit.rect.centerx, hit.rect.bottom, pu_type))

        for pu in self.powerups:
            if self.player.rect.colliderect(pu.rect):
                self.apply_powerup(pu.power_type)
                pu.kill()
                self.create_explosion(self.player.rect.centerx, self.player.rect.centery, 5, COLOR_POWERUP)

        if not self.player.shield:
            if pygame.sprite.spritecollide(self.player, self.bullets, True):
                self.take_damage()

        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.take_damage()
            if enemy.rect.bottom >= self.player.rect.top:
                return False

        # Check if all enemies are dead (regular level)
        if not self.boss_active and len(self.enemies) == 0:
            self.level_up()

        return True

    def apply_powerup(self, type):
        if type == "SHIELD":
            self.player.shield = True
        elif type == "POWER":
            self.player.power_level = min(self.player.power_level + 1, 3)
        elif type == "SLOW":
            self.player.slow_time = True

    def take_damage(self):
        if self.player.invulnerable_time > 0: return

        self.player.shield = False
        self.player.power_level = 1
        self.player.slow_time = False
        self.create_explosion(self.player.rect.centerx, self.player.rect.centery, 50, COLOR_PLAYER)
        self.flash_screen()
        self.shake_screen(15)
        self.combo = 0

        self.player.lives -= 1
        if self.player.lives <= 0:
            self.game_over = True
        else:
            self.player.invulnerable_time = 120

    def update_aliens(self):
        if not self.level_active or self.level_transition: return

        move_down = False
        for enemy in self.enemies:
            if enemy.rect.right >= SCREEN_WIDTH - 10 and self.alien_direction > 0:
                move_down = True
                break
            if enemy.rect.left <= 10 and self.alien_direction < 0:
                move_down = True
                break

        if move_down:
            self.alien_direction *= -1
            for enemy in self.enemies:
                enemy.rect.y += self.alien_dy
        else:
            for enemy in self.enemies:
                enemy.rect.x += (self.alien_move_speed * self.alien_direction)

        if self.boss_active:
            # FIX: Changed from sprite_at(0) to list conversion
            boss_list = list(self.enemies)
            if boss_list:
                boss = boss_list[0]
                boss.rect.x += self.alien_move_speed * self.alien_direction
                if boss.rect.right > SCREEN_WIDTH or boss.rect.left < 0:
                    self.alien_direction *= -1
                    boss.rect.x += self.alien_move_speed * self.alien_direction
                if random.random() < 0.05:
                    bullet = Bullet(boss.rect.centerx, boss.rect.bottom, BULLET_SPEED * 1.5, COLOR_BULLET_ENEMY)
                    self.bullets.add(bullet)

        if self.boss_active and len(self.enemies) == 0:
            self.boss_active = False
            self.level_up()

    def update_powerups(self):
        for pu in self.powerups:
            pu.update()

    def update_level_transition(self):
        if self.level_transition:
            self.level_transition_timer -= 1
            if self.level_transition_timer <= 0:
                self.level_transition = False

    def update_combo(self):
        now = pygame.time.get_ticks()
        if now - self.last_kill_time > 3000:
            self.combo = 0

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))
        for star in self.stars:
            s = pygame.Surface((star.size, star.size))
            s.fill(COLOR_TEXT)
            self.screen.blit(s, (star.x, star.y))
            star.update()

        if self.shake_timer > 0:
            sx = random.randint(-self.shake_timer, self.shake_timer)
            sy = random.randint(-self.shake_timer, self.shake_timer)
            self.shake_timer = max(0, self.shake_timer - 1)
        else:
            sx, sy = 0, 0

        if self.flash_timer > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((255, 255, 255))
            self.screen.blit(overlay, (0, 0))
            self.flash_timer -= 1

        return sx, sy

    def draw_ui(self, sx, sy):
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, COLOR_TEXT)
        level_text = self.font.render(f"Level: {self.level}", True, COLOR_TEXT)
        combo_text = self.font.render(f"Combo: x{1 + self.combo // 10}", True,
                                      (255, 200, 0) if self.combo > 0 else COLOR_TEXT)
        power_text = self.font.render(f"Power: {'★' * self.player.power_level}", True, COLOR_PLAYER)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))
        self.screen.blit(level_text, (SCREEN_WIDTH - 120, 10))
        self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - 40, 10))
        self.screen.blit(power_text, (SCREEN_WIDTH // 2 - 50, 40))

        if self.level_transition:
            transition_text = self.big_font.render(f"LEVEL {self.level}!", True, COLOR_TEXT)
            text_rect = transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(transition_text, text_rect)

        if self.player.invulnerable_time > 0 and (pygame.time.get_ticks() // 100) % 2 == 0:
            self.player.image.set_alpha(128)
        else:
            self.player.image.set_alpha(255)

        if self.player.shield:
            shield_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*COLOR_PLAYER_SHIELD, 100), (25, 25), 25)
            shield_surf.set_colorkey(COLOR_PLAYER_SHIELD)
            self.screen.blit(shield_surf, (self.player.rect.x - 5, self.player.rect.y - 5))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset_game()
                        else:
                            bullets = self.player.shoot()
                            self.bullets.add(bullets)
                    elif event.key == pygame.K_r:
                        if self.game_over:
                            self.reset_game()

            if not self.game_over:
                self.player.update()
                self.bullets.update()
                self.particles.update()
                self.update_powerups()
                self.update_level_transition()
                self.update_aliens()
                collision_active = self.check_collisions()

                if not collision_active:
                    self.game_over = True

                self.update_combo()

            self.draw_background()
            sx, sy = 0, 0

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))

            for sprite in self.bullets:
                self.screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))

            for sprite in self.enemies:
                self.screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))

            for sprite in self.powerups:
                self.screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))

            for sprite in self.particles:
                self.screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))

            self.draw_ui(sx, sy)

            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                msg = "GAME OVER"
                sub_msg = f"Score: {self.score} | High: {self.high_score}"
                restart_msg = "Press SPACE or R to Restart"

                text = self.big_font.render(msg, True, COLOR_TEXT)
                sub = self.font.render(sub_msg, True, (200, 200, 200))
                res = self.font.render(restart_msg, True, COLOR_TEXT)

                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
                sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
                res_rect = res.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

                self.screen.blit(text, text_rect)
                self.screen.blit(sub, sub_rect)
                self.screen.blit(res, res_rect)

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
