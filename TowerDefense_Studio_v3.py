import pygame
import random
import math
import json
import os

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 100) // GRID_SIZE
INFO_PANEL_HEIGHT = 100
FPS = 60
TOTAL_WAVES = 20  # Increased for a longer game
BOSS_WAVE_INTERVAL = 5
STATS_FILE = 'dungeon_stats.json'
ACHIEVEMENTS_FILE = 'achievements.json'

# --- Colors ---
COLOR_WALL = (50, 50, 50)
COLOR_PATH = (100, 100, 100)
COLOR_GRID = (70, 70, 70)
COLOR_PATH_INDICATOR = (40, 40, 40)
COLOR_UI_BG = (30, 30, 30)
COLOR_UI_BORDER = (150, 150, 150)
COLOR_TEXT = (255, 255, 255)
COLOR_DAMAGE_TEXT = (255, 100, 100)
COLOR_ENEMY_GRUNT = (200, 50, 50)
COLOR_ENEMY_BRUTE = (150, 50, 200)
COLOR_ENEMY_TANK = (50, 120, 50)
COLOR_ENEMY_SCOUT = (220, 120, 0)
COLOR_ENEMY_BOSS = (255, 255, 0)
COLOR_SPIKE_TRAP = (120, 120, 120)
COLOR_SPIKE_TRAP_ARMED = (180, 180, 180)
COLOR_SLOW_TRAP = (100, 100, 200)
COLOR_SLOW_TRAP_ACTIVE = (150, 150, 255)
COLOR_TURRET_BASE = (80, 80, 90)
COLOR_TURRET_CANNON = (140, 140, 150)
COLOR_GOLD_MINE = (255, 223, 0)
COLOR_PROJECTILE = (255, 200, 0)
COLOR_RANGE_INDICATOR = (255, 255, 255, 50)
COLOR_HEALTH_BAR_BG = (180, 0, 0)
COLOR_HEALTH_BAR_FG = (0, 180, 0)
COLOR_GAME_OVER_BG = (100, 0, 0)
COLOR_WIN_BG = (0, 100, 0)
COLOR_PAUSE_BG = (0, 0, 0, 150)
COLOR_BUTTON = (0, 80, 150)
COLOR_BUTTON_HOVER = (50, 130, 200)
COLOR_DISABLED_BUTTON = (80, 80, 80)
COLOR_COMBO = (255, 165, 0)
COLOR_ULTIMATE = (255, 215, 0)
COLOR_ACHIEVEMENT_BG = (0, 128, 128)  # Teal


# --- Achievement System ---
class AchievementNotification(pygame.sprite.Sprite):
    def __init__(self, name, font):
        super().__init__()
        self.text = f"Achievement Unlocked: {name}!"
        self.font = font
        self.image = self.font.render(self.text, True, COLOR_TEXT)
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH / 2, bottom=0)
        self.lifespan = 5.0  # Total time on screen
        self.fade_time = 0.5  # Time to fade in/out
        self.alpha = 255
        self.state = "fading_in"  # "fading_in", "visible", "fading_out"

    def update(self, dt):
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.kill()
            return

        if self.state == "fading_in":
            self.rect.y += 80 * dt
            if self.rect.top >= 10:
                self.rect.top = 10
                self.state = "visible"
        elif self.lifespan <= self.fade_time:
            self.state = "fading_out"

        if self.state == "fading_out":
            self.alpha = max(0, 255 * (self.lifespan / self.fade_time))
            self.image.set_alpha(self.alpha)


class AchievementManager:
    def __init__(self, game):
        self.game = game
        self.achievements = {}
        self.load_achievements()

    def load_achievements(self):
        if not os.path.exists(ACHIEVEMENTS_FILE):
            # Handle error or create a default file. Here we just print a warning.
            print(f"Warning: {ACHIEVEMENTS_FILE} not found!")
            return
        try:
            with open(ACHIEVEMENTS_FILE, 'r') as f:
                self.achievements = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding {ACHIEVEMENTS_FILE}. It might be corrupted.")

    def save_achievements(self):
        with open(ACHIEVEMENTS_FILE, 'w') as f:
            json.dump(self.achievements, f, indent=4)

    def show_notification(self, name):
        notification = AchievementNotification(name, self.game.font)
        self.game.achievement_notifications.add(notification)

    def unlock(self, key):
        if key in self.achievements and not self.achievements[key]['unlocked']:
            self.achievements[key]['unlocked'] = True
            reward = self.achievements[key].get('reward_points', 0)
            if reward > 0:
                self.game.research.data['research_points'] += reward
            self.show_notification(self.achievements[key]['name'])
            self.save_achievements()
            return True
        return False

    def add_progress(self, key, value):
        if key in self.achievements and not self.achievements[key]['unlocked']:
            ach = self.achievements[key]
            ach['progress'] = ach.get('progress', 0) + value
            if ach['progress'] >= ach['target']:
                self.unlock(key)  # This will handle unlocking, rewards, and saving
            else:
                self.save_achievements()  # Save progress even if not unlocked


# --- Research and Stats Management ---
class Research:
    def __init__(self):
        self.data = {
            'research_points': 0,
            'stats': {'games_played': 0, 'victories': 0, 'total_kills': 0, 'rank_victories': 0},
            'upgrades': {'spike_damage': 0, 'spike_health': 0, 'slow_duration': 0, 'slow_health': 0, 'turret_damage': 0,
                         'turret_range': 0, 'gold_income': 0},
            'rank': 'Captain'
        }
        self.load()

    def load(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r') as f:
                    self.data = json.load(f)
                if 'rank' not in self.data: self.data['rank'] = 'Captain'
                if 'stats' not in self.data: self.data['stats'] = {'games_played': 0, 'victories': 0, 'total_kills': 0,
                                                                   'rank_victories': 0}
                if 'rank_victories' not in self.data['stats']: self.data['stats']['rank_victories'] = 0
                if 'upgrades' not in self.data: self.data['upgrades'] = {}
                if 'gold_income' not in self.data['upgrades']: self.data['upgrades']['gold_income'] = 0
            except json.JSONDecodeError:
                self.save()
        else:
            self.save()

    def save(self):
        with open(STATS_FILE, 'w') as f: json.dump(self.data, f, indent=4)

    def update_rank(self):
        victories = self.data['stats']['rank_victories']
        if victories >= 20:
            self.data['rank'] = 'Admiral'
        elif victories >= 10:
            self.data['rank'] = 'General'
        else:
            self.data['rank'] = 'Captain'

    def get_rank_bonus(self):
        rank = self.data.get('rank', 'Captain')
        if rank == 'Admiral': return 1.10
        if rank == 'General': return 1.05
        return 1.0

    def get_upgrade_cost(self, key):
        base_cost = 10 if key == 'gold_income' else 5
        return base_cost + (self.data['upgrades'][key] * 5)

    def purchase_upgrade(self, key):
        cost = self.get_upgrade_cost(key)
        if self.data['research_points'] >= cost:
            self.data['research_points'] -= cost
            self.data['upgrades'][key] += 1
            self.save()
            return True
        return False


# --- Game Object Classes ---
class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color, font):
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.y_vel = -30
        self.lifespan = 1.0

    def update(self, dt):
        self.rect.y += self.y_vel * dt
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.kill()
        else:
            self.alpha = max(0, 255 * (self.lifespan / 1.0))
            self.image.set_alpha(self.alpha)


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, is_shockwave=False):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.is_shockwave = is_shockwave
        if self.is_shockwave:
            self.max_lifespan, self.size, self.radius, self.max_radius = 0.4, 5, 5, 80
        else:
            self.max_lifespan, self.size = random.uniform(0.4, 0.9), random.randint(3, 8)
            angle, speed = random.uniform(0, 2 * math.pi), random.uniform(50, 150)
            self.vx, self.vy, self.gravity = math.cos(angle) * speed, math.sin(angle) * speed, 180
        self.lifespan = self.max_lifespan
        self.image = pygame.Surface([self.size * 2, self.size * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt):
        self.lifespan -= dt
        if self.lifespan <= 0: self.kill(); return
        if self.is_shockwave:
            self.radius += 200 * dt
            self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), int(self.radius), 4)
            self.rect = self.image.get_rect(center=(self.x, self.y))
        else:
            self.x += self.vx * dt;
            self.vy += self.gravity * dt;
            self.y += self.vy * dt
            self.rect.center = (self.x, self.y)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
        self.image.set_alpha(max(0, int(255 * (self.lifespan / self.max_lifespan))))


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, damage, game):
        super().__init__()
        self.game, self.image, self.rect, self.target, self.damage, self.speed = game, pygame.Surface((8, 8),
                                                                                                      pygame.SRCALPHA), None, target, damage, 300
        pygame.draw.circle(self.image, COLOR_PROJECTILE, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        if not self.target.alive(): self.kill(); return
        dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist < 5:
            self.target.take_damage(self.damage)
            self.game.create_explosion(self.rect.centerx, self.rect.centery, COLOR_PROJECTILE)
            self.kill();
            return
        self.rect.x += dx / dist * self.speed * dt
        self.rect.y += dy / dist * self.speed * dt


class Enemy(pygame.sprite.Sprite):
    enemy_type = "Base"

    def __init__(self, path, health, speed, trap_damage, color, game, value):
        super().__init__()
        self.game, self.path, self.path_index = game, path, 0
        self.x, self.y = self.path[0]
        self.speed, self.max_health, self.health, self.trap_damage = speed, health, health, trap_damage
        self.is_slowed, self.slow_timer, self.color, self.value = False, 0, color, value
        self.image = pygame.Surface([GRID_SIZE - 4, GRID_SIZE - 4], pygame.SRCALPHA)
        self.rect = self.image.get_rect(
            center=(self.x * GRID_SIZE + GRID_SIZE // 2, self.y * GRID_SIZE + GRID_SIZE // 2))

    def update(self, dt):
        if self.path_index < len(self.path) - 1:
            tx, ty = self.path[self.path_index + 1]
            tpx, tpy = tx * GRID_SIZE + GRID_SIZE // 2, ty * GRID_SIZE + GRID_SIZE // 2
            dx, dy = tpx - self.rect.centerx, tpy - self.rect.centery
            dist = math.hypot(dx, dy)
            curr_speed = self.speed * (0.5 if self.is_slowed else 1)
            if self.is_slowed: self.slow_timer -= dt; self.is_slowed = self.slow_timer > 0
            move_dist = curr_speed * GRID_SIZE * dt
            if dist > move_dist:
                self.rect.centerx += dx / dist * move_dist
                self.rect.centery += dy / dist * move_dist
            else:
                self.rect.center = (tpx, tpy);
                self.path_index += 1
                trap = self.game.get_trap_at(tx, ty)
                if trap: trap.take_damage(self.trap_damage)

    def take_damage(self, amount):
        damage = int(amount);
        self.health -= damage;
        self.health = max(0, self.health)
        self.game.floating_texts.add(
            FloatingText(self.rect.centerx, self.rect.top, str(damage), COLOR_DAMAGE_TEXT, self.game.damage_font))
        self.check_death()

    def check_death(self):
        if self.health <= 0:
            self.game.create_explosion(self.rect.centerx, self.rect.centery, self.color)
            self.game.register_kill(self.value, self.enemy_type)
            self.kill()

    def slow(self, duration):
        self.is_slowed = True;
        self.slow_timer = max(self.slow_timer, duration)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.is_slowed: pygame.draw.circle(surface, COLOR_SLOW_TRAP_ACTIVE, self.rect.center, self.rect.width // 2,
                                              2)

    def draw_health_bar(self, surface):
        if self.health < self.max_health:
            bar = pygame.Rect(self.rect.left, self.rect.top - 7, self.rect.width, 5)
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, bar)
            bar.width = self.rect.width * (self.health / self.max_health)
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FG, bar)


class Grunt(Enemy):
    enemy_type = "grunt"

    def __init__(self, path, health, game):
        super().__init__(path, health, 2.5, 5, COLOR_ENEMY_GRUNT, game, 5);
        self.draw_enemy()

    def draw_enemy(self):
        pygame.draw.rect(self.image, self.color, self.image.get_rect())
        pygame.draw.rect(self.image, (255, 100, 100), self.image.get_rect(), 2)


class Brute(Enemy):
    enemy_type = "brute"

    def __init__(self, path, health, game):
        super().__init__(path, int(health * 1.8), 2.0, 10, COLOR_ENEMY_BRUTE, game, 8);
        self.draw_enemy()

    def draw_enemy(self):
        w, h = self.image.get_size();
        points = [(w // 2, 0), (w, h // 4), (w, 3 * h // 4), (w // 2, h), (0, 3 * h // 4), (0, h // 4)]
        pygame.draw.polygon(self.image, self.color, points);
        pygame.draw.polygon(self.image, (255, 100, 255), points, 2)


class Tank(Enemy):
    enemy_type = "tank"

    def __init__(self, path, health, game):
        super().__init__(path, int(health * 3.5), 1.5, 20, COLOR_ENEMY_TANK, game, 12);
        self.draw_enemy()

    def draw_enemy(self):
        w, h = self.image.get_size();
        points = [(w // 4, 0), (3 * w // 4, 0), (w, h // 4), (w, 3 * h // 4), (3 * w // 4, h), (w // 4, h),
                  (0, 3 * h // 4), (0, h // 4)]
        pygame.draw.polygon(self.image, self.color, points);
        pygame.draw.polygon(self.image, (100, 255, 100), points, 2)


class Scout(Enemy):
    enemy_type = "scout"

    def __init__(self, path, health, game):
        super().__init__(path, int(health * 0.7), 4.5, 2, COLOR_ENEMY_SCOUT, game, 4);
        self.draw_enemy()

    def draw_enemy(self):
        w, h = self.image.get_size();
        points = [(w // 2, 0), (w, h), (0, h)]
        pygame.draw.polygon(self.image, self.color, points);
        pygame.draw.polygon(self.image, (255, 180, 50), points, 2)


class Boss(Enemy):
    enemy_type = "boss"

    def __init__(self, path, health, game):
        super().__init__(path, health, 1.0, 100, COLOR_ENEMY_BOSS, game, 150)
        self.image = pygame.Surface([GRID_SIZE, GRID_SIZE], pygame.SRCALPHA)
        self.rect = self.image.get_rect(
            center=(self.x * GRID_SIZE + GRID_SIZE // 2, self.y * GRID_SIZE + GRID_SIZE // 2));
        self.draw_enemy()

    def draw_enemy(self):
        pygame.draw.rect(self.image, self.color, self.image.get_rect(), 0, 8)
        pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 3, 8)


class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y, cost, upg_cost, max_hp, game):
        super().__init__()
        self.x, self.y, self.cost, self.upgrade_cost, self.level = x, y, cost, upg_cost, 1
        self.game = game;
        self.research = game.research;
        self.is_ultimate = False
        self.image = pygame.Surface([GRID_SIZE, GRID_SIZE], pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x * GRID_SIZE, y * GRID_SIZE))
        self.base_max_health, self.max_health, self.health = max_hp, max_hp, max_hp
        self.total_investment = cost

    def take_damage(self, amount):
        self.health -= amount; self.health = max(0, self.health); self.check_death()

    def check_death(self):
        if self.health <= 0: self.kill()

    def upgrade(self):
        self.total_investment += self.upgrade_cost;
        self.level += 1
        self.max_health += 25 * self.level;
        self.health = self.max_health
        if self.level >= 5 and not self.is_ultimate:
            self.is_ultimate = True;
            self.on_ultimate()
            self.game.achievement_manager.unlock('ultimate_power')

    def on_ultimate(self):
        pass

    def draw_health_bar(self, surface):
        if self.health < self.max_health:
            bar = pygame.Rect(self.rect.left + 2, self.rect.top - 7, GRID_SIZE - 4, 5)
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, bar)
            bar.width = (GRID_SIZE - 4) * (self.health / self.max_health)
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FG, bar)


class SpikeTrap(Trap):
    def __init__(self, x, y, game):
        super().__init__(x, y, 50, 30, 75, game);
        rank_bonus = self.research.get_rank_bonus()
        self.damage_bonus, self.health_bonus = self.research.data['upgrades']['spike_damage'], 1 + (
                    self.research.data['upgrades']['spike_health'] * 0.1)
        self.max_health = int(self.base_max_health * self.health_bonus * rank_bonus);
        self.health = self.max_health
        self.damage, self.cooldown, self.timer, self.armed = (5 + self.damage_bonus) * rank_bonus, 2.0, 0, True;
        self.draw()

    def draw(self):
        c = COLOR_SPIKE_TRAP_ARMED if self.armed else COLOR_SPIKE_TRAP;
        self.image.fill(COLOR_PATH)
        pygame.draw.rect(self.image, c, (5, 5, 22, 22))
        if self.is_ultimate: pygame.draw.rect(self.image, COLOR_ULTIMATE, (5, 5, 22, 22), 2)
        for i in range(3):
            for j in range(3): pygame.draw.polygon(self.image, (150, 150, 150),
                                                   [(8 + i * 8 - 3, 8 + j * 8 + 3), (8 + i * 8 + 3, 8 + j * 8 + 3),
                                                    (8 + i * 8, 8 + j * 8)])

    def update(self, dt, game):
        self.timer -= dt
        if not self.armed and self.timer <= 0: self.armed = True; self.draw()
        if self.armed and self.timer <= 0:
            enemies_on_trap = [e for e in game.enemies if self.rect.colliderect(e.rect)]
            if enemies_on_trap:
                for e in enemies_on_trap: e.take_damage(self.damage)
                if self.is_ultimate:
                    game.create_explosion(self.rect.centerx, self.rect.centery, COLOR_SPIKE_TRAP_ARMED,
                                          is_shockwave=True)
                    for e in game.enemies:
                        if math.hypot(e.rect.centerx - self.rect.centerx,
                                      e.rect.centery - self.rect.centery) <= 80: e.take_damage(self.damage * 2)
                self.armed = False;
                self.timer = self.cooldown;
                self.draw()

    def upgrade(self):
        super().upgrade(); self.damage += 3; self.upgrade_cost += 10

    def on_ultimate(self):
        self.damage += 10; self.draw()


class SlowTrap(Trap):
    def __init__(self, x, y, game):
        super().__init__(x, y, 75, 40, 100, game);
        rank_bonus = self.research.get_rank_bonus()
        self.duration_bonus, self.health_bonus = self.research.data['upgrades']['slow_duration'] * 0.25, 1 + (
                    self.research.data['upgrades']['slow_health'] * 0.1)
        self.max_health = int(self.base_max_health * self.health_bonus * rank_bonus);
        self.health = self.max_health
        self.slow_duration = (3 + self.duration_bonus) * rank_bonus;
        self.draw()

    def draw(self):
        self.image.fill(COLOR_PATH);
        pygame.draw.circle(self.image, COLOR_SLOW_TRAP, (16, 16), 11)
        pygame.draw.circle(self.image, COLOR_SLOW_TRAP_ACTIVE, (16, 16), 8)
        if self.is_ultimate: pygame.draw.circle(self.image, COLOR_ULTIMATE, (16, 16), 14, 2)

    def update(self, dt, game):
        for e in game.enemies:
            if self.rect.colliderect(e.rect): e.slow(self.slow_duration)

    def upgrade(self):
        super().upgrade(); self.slow_duration += 1.5; self.upgrade_cost += 20

    def on_ultimate(self):
        self.slow_duration += 3; self.draw()


class TurretTrap(Trap):
    def __init__(self, x, y, game):
        super().__init__(x, y, 100, 50, 50, game);
        rank_bonus = self.research.get_rank_bonus()
        self.damage_bonus, self.range_bonus = self.research.data['upgrades']['turret_damage'], \
        self.research.data['upgrades']['turret_range'] * 10
        self.damage, self.range = (3 + self.damage_bonus) * rank_bonus, (100 + self.range_bonus) * rank_bonus
        self.cooldown, self.timer, self.angle, self.target = 1.0, 0, 0, None;
        self.draw()

    def draw(self):
        self.image.fill((0, 0, 0, 0));
        pygame.draw.circle(self.image, COLOR_TURRET_BASE, (16, 16), 12)
        if self.is_ultimate:
            pygame.draw.circle(self.image, COLOR_ULTIMATE, (16, 16), 14, 2)
        else:
            pygame.draw.circle(self.image, COLOR_GRID, (16, 16), 12, 2)
        end_x, end_y = 16 + 16 * math.cos(self.angle), 16 + 16 * math.sin(self.angle)
        pygame.draw.line(self.image, COLOR_TURRET_CANNON, (16, 16), (end_x, end_y), 6)

    def find_target(self, enemies):
        in_range = [e for e in enemies if
                    math.hypot(self.rect.centerx - e.rect.centerx, self.rect.centery - e.rect.centery) <= self.range]
        self.target = max(in_range, key=lambda e: e.path_index) if in_range else None

    def update(self, dt, game):
        self.timer -= dt
        if not self.target or not self.target.alive(): self.find_target(game.enemies)
        if self.target:
            dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
            self.angle = math.atan2(dy, dx);
            self.draw()
            if self.timer <= 0:
                game.projectiles.add(Projectile(self.rect.centerx, self.rect.centery, self.target, self.damage, game))
                if self.is_ultimate:
                    offset_angle = self.angle + math.radians(15)
                    off_x, off_y = 16 + 16 * math.cos(offset_angle), 16 + 16 * math.sin(offset_angle)
                    game.projectiles.add(
                        Projectile(self.rect.left + off_x, self.rect.top + off_y, self.target, self.damage, game))
                self.timer = self.cooldown

    def upgrade(self):
        super().upgrade(); self.range += 15; self.damage += 2; self.cooldown *= 0.9; self.upgrade_cost += 25

    def on_ultimate(self):
        self.cooldown *= 0.7; self.draw()


class GoldMine(Trap):
    def __init__(self, x, y, game):
        super().__init__(x, y, 60, 40, 50, game);
        rank_bonus = self.research.get_rank_bonus()
        self.income_bonus = self.research.data['upgrades']['gold_income']
        self.income = int((5 + self.income_bonus) * rank_bonus)
        self.cooldown = 5.0;
        self.timer = self.cooldown;
        self.draw()

    def draw(self):
        self.image.fill(COLOR_PATH);
        pygame.draw.rect(self.image, COLOR_GOLD_MINE, (4, 4, 24, 24), border_radius=4)
        pygame.draw.rect(self.image, (255, 255, 255), (4, 4, 24, 24), 2, border_radius=4)
        if self.is_ultimate: pygame.draw.rect(self.image, COLOR_ULTIMATE, (2, 2, 28, 28), 2, border_radius=6)

    def update(self, dt, game):
        self.timer -= dt
        if self.timer <= 0:
            game.money += self.income
            game.floating_texts.add(
                FloatingText(self.rect.centerx, self.rect.top, f"+{self.income}", COLOR_GOLD_MINE, game.small_font))
            self.timer = self.cooldown

    def upgrade(self):
        super().upgrade(); self.income += 3; self.upgrade_cost += 20

    def on_ultimate(self):
        self.income += 10; self.draw()


class Button:
    def __init__(self, x, y, w, h, text, font, action=None):
        self.rect, self.text, self.font, self.action = pygame.Rect(x, y, w, h), text, font, action
        self.is_hovered, self.is_enabled = False, True

    def draw(self, screen):
        c = COLOR_BUTTON_HOVER if self.is_hovered and self.is_enabled else (
            COLOR_BUTTON if self.is_enabled else COLOR_DISABLED_BUTTON)
        pygame.draw.rect(screen, c, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_hover(self, pos): self.is_hovered = self.rect.collidepoint(pos)

    def click(self):
        if self.action and self.is_enabled: self.action()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Warfare: Enhanced")
        self.clock, self.running = pygame.time.Clock(), True
        self.font, self.small_font = pygame.font.SysFont("Arial", 24), pygame.font.SysFont("Arial", 18)
        self.damage_font, self.large_font = pygame.font.SysFont("Arial", 14, bold=True), pygame.font.SysFont("Arial",
                                                                                                             36,
                                                                                                             bold=True)
        self.research = Research()
        self.achievement_manager = AchievementManager(self)
        self.game_state = "main_menu"
        self.load_assets();
        self.setup_ui()

    def load_assets(self):
        self.background_images, self.current_background, self.rank_images = [], None, {}
        resource_dir = 'resources_TowerDefenseStudio'
        for i in range(1, 11):
            try:
                path = os.path.join(resource_dir, f"background{i:02d}.png")
                self.background_images.append(pygame.image.load(path).convert())
            except pygame.error as e:
                print(f"Warning: Could not load {path}. {e}")
        for rank in ["Captain", "General", "Admiral"]:
            try:
                path = os.path.join(resource_dir, f"{rank.lower()}.png")
                self.rank_images[rank] = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"Warning: Could not load {path}. {e}"); self.rank_images[rank] = None

    def setup_ui(self):
        self.new_game_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "New Game", self.font,
                                      action=self.start_new_game)
        self.research_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50, "Research Lab",
                                      self.font, action=lambda: self.set_state("research_lab"))
        self.main_menu_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, "Main Menu", self.font,
                                       action=lambda: self.set_state("main_menu"))
        self.setup_research_buttons()

    def setup_research_buttons(self):
        self.research_buttons = {}
        y_start, x_start = 150, SCREEN_WIDTH // 2 - 20
        upgrades = {'spike_damage': 'Spike Dmg', 'spike_health': 'Spike HP', 'slow_duration': 'Slow Time',
                    'slow_health': 'Slow HP', 'turret_damage': 'Turret Dmg', 'turret_range': 'Turret Rng',
                    'gold_income': 'Gold Income'}
        for i, (key, name) in enumerate(upgrades.items()): self.research_buttons[key] = Button(x_start,
                                                                                               y_start + i * 50, 50, 40,
                                                                                               "+", self.font,
                                                                                               action=lambda
                                                                                                   k=key: self.research.purchase_upgrade(
                                                                                                   k))

    def reset_game(self):
        self.current_background = random.choice(self.background_images) if self.background_images else None
        self.path_list = []
        while not self.path_list: self.grid = self.create_grid(); self.path_list = self.find_path()
        self.path_set = set(self.path_list)
        self.enemies, self.traps, self.projectiles = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
        self.particles, self.floating_texts = pygame.sprite.Group(), pygame.sprite.Group()
        self.achievement_notifications = pygame.sprite.Group()
        self.money, self.lives, self.wave = 250, 20, 0
        self.wave_timer, self.wave_in_progress = 10, False
        self.enemies_killed, self.money_earned = 0, 250
        self.combo_count, self.combo_timer, self.max_combo_time = 0, 0, 2.0
        self.selected_trap_type, self.selected_trap_instance = None, None
        self.shockwave_cooldown, self.shockwave_timer = 30.0, 0.0
        # --- Achievement Tracking Vars ---
        self.enemies_spawned_this_wave, self.enemies_killed_this_wave = 0, 0
        self.total_enemies_escaped, self.highest_combo_this_game = 0, 0

    def start_new_game(self):
        self.reset_game(); self.set_state("playing")

    def end_game(self, victory):
        s = self.research.data['stats']
        s['games_played'] += 1;
        s['total_kills'] += self.enemies_killed
        if victory:
            s['victories'] += 1; s['rank_victories'] += 1
        else:
            s['rank_victories'] = max(0, s['rank_victories'] - 1)
        self.research.update_rank()
        waves = TOTAL_WAVES if victory else (self.wave - (1 if self.wave_in_progress else 0))
        points = (waves * 5) + (self.enemies_killed // 2)
        if victory: points += 100

        # --- Achievement Checks ---
        self.achievement_manager.add_progress('millionaire', self.money_earned)
        if self.highest_combo_this_game >= 50: self.achievement_manager.unlock('combo_master')
        clean_game_bonus = 0
        if victory:
            self.achievement_manager.unlock('first_win')
            if self.lives == 1: self.achievement_manager.unlock('close_call')
            if self.total_enemies_escaped == 0:
                clean_game_bonus = 250  # Repeatable reward for a perfect game
                points += clean_game_bonus

        self.research.data['research_points'] += points
        self.research.save()
        self.last_game_stats = {'waves': waves, 'kills': self.enemies_killed, 'points': points, 'victory': victory,
                                'clean_bonus': clean_game_bonus}
        self.set_state("game_over")

    def register_kill(self, value, enemy_type):
        self.combo_timer = self.max_combo_time;
        self.combo_count += 1
        self.highest_combo_this_game = max(self.highest_combo_this_game, self.combo_count)
        bonus = self.combo_count // 5
        self.money += value + bonus;
        self.money_earned += value + bonus
        self.enemies_killed += 1;
        self.enemies_killed_this_wave += 1

        # --- Achievement Progress ---
        if enemy_type == 'grunt':
            self.achievement_manager.add_progress('grunt_slayer', 1)
        elif enemy_type == 'boss':
            self.achievement_manager.add_progress('boss_hunter', 1)

    def create_explosion(self, x, y, color, is_shockwave=False):
        num = 1 if is_shockwave else 15
        for _ in range(num): self.particles.add(Particle(x, y, color, is_shockwave))

    def create_grid(self):
        grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if 1 < x < GRID_WIDTH - 2 and random.random() < 0.3: grid[y][x] = 0
        grid[GRID_HEIGHT // 2][0] = 1;
        grid[GRID_HEIGHT // 2][GRID_WIDTH - 1] = 1
        return grid

    def find_path(self):
        start, end = (0, GRID_HEIGHT // 2), (GRID_WIDTH - 1, GRID_HEIGHT // 2)
        open_set, came_from, g, f = {start}, {}, {}, {}
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH): g[(x, y)], f[(x, y)] = float('inf'), float('inf')
        g[start], f[start] = 0, abs(start[0] - end[0]) + abs(start[1] - end[1])
        while open_set:
            curr = min(open_set, key=lambda o: f.get(o, float('inf')))
            if curr == end:
                path = []
                while curr in came_from: path.append(curr); curr = came_from[curr]
                path.append(start);
                return path[::-1]
            open_set.remove(curr)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (curr[0] + dx, curr[1] + dy)
                if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and self.grid[neighbor[1]][
                    neighbor[0]] == 1:
                    tentative_g = g.get(curr, float('inf')) + 1
                    if tentative_g < g.get(neighbor, float('inf')):
                        came_from[neighbor], g[neighbor] = curr, tentative_g
                        f[neighbor] = g[neighbor] + abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1])
                        if neighbor not in open_set: open_set.add(neighbor)
        return []

    def set_state(self, state):
        self.game_state = state

    def run(self):
        while self.running: dt = self.clock.tick(FPS) / 1000.0; self.handle_events(); self.update(dt); self.draw()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if self.game_state == "playing":
                        self.set_state("paused")
                    elif self.game_state == "paused":
                        self.set_state("playing")
            if self.game_state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.handle_mouse_click(event.pos)
                if event.type == pygame.KEYDOWN:
                    key_map = {pygame.K_1: "spike", pygame.K_2: "slow", pygame.K_3: "turret", pygame.K_4: "gold_mine"}
                    if event.key in key_map:
                        self.selected_trap_type, self.selected_trap_instance = key_map[event.key], None
                    elif event.key == pygame.K_u and self.selected_trap_instance and self.money >= self.selected_trap_instance.upgrade_cost and not self.selected_trap_instance.is_ultimate:
                        self.money -= self.selected_trap_instance.upgrade_cost;
                        self.selected_trap_instance.upgrade()
                    elif event.key == pygame.K_s and self.selected_trap_instance:
                        self.sell_trap(self.selected_trap_instance)
                    elif event.key == pygame.K_SPACE and not self.wave_in_progress:
                        self.money += 25; self.start_wave()
                    elif event.key == pygame.K_f and self.shockwave_timer <= 0:
                        self.activate_shockwave()
            elif self.game_state == "main_menu":
                self.new_game_button.check_hover(mouse_pos);
                self.research_button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.new_game_button.is_hovered: self.new_game_button.click()
                    if self.research_button.is_hovered: self.research_button.click()
            elif self.game_state == "research_lab":
                self.main_menu_button.check_hover(mouse_pos)
                for btn in self.research_buttons.values(): btn.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.main_menu_button.is_hovered: self.main_menu_button.click()
                    for btn in self.research_buttons.values():
                        if btn.is_hovered: btn.click()
            elif self.game_state == "game_over":
                self.main_menu_button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.main_menu_button.is_hovered: self.main_menu_button.click()

    def handle_mouse_click(self, pos):
        gx, gy = pos[0] // GRID_SIZE, pos[1] // GRID_SIZE
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            trap = self.get_trap_at(gx, gy)
            if self.selected_trap_type and not trap:
                self.place_trap(gx, gy)
            elif trap:
                self.selected_trap_instance, self.selected_trap_type = trap, None
            else:
                self.selected_trap_instance, self.selected_trap_type = None, None

    def get_trap_at(self, x, y):
        for trap in self.traps:
            if trap.x == x and trap.y == y: return trap
        return None

    def sell_trap(self, trap):
        refund = int(trap.total_investment * 0.7)
        self.money += refund
        self.floating_texts.add(
            FloatingText(trap.rect.centerx, trap.rect.centery, f"+${refund}", COLOR_GOLD_MINE, self.font))
        trap.kill();
        self.selected_trap_instance = None

    def place_trap(self, x, y):
        is_wall = self.grid[y][x] == 0
        turret_placement = self.selected_trap_type == 'turret' and is_wall
        path_trap_placement = self.selected_trap_type in ['spike', 'slow', 'gold_mine'] and not is_wall
        if not (turret_placement or path_trap_placement): return
        costs = {'spike': 50, 'slow': 75, 'turret': 100, 'gold_mine': 60}
        cost = costs.get(self.selected_trap_type)
        if self.money >= cost:
            trap_classes = {'spike': SpikeTrap, 'slow': SlowTrap, 'turret': TurretTrap, 'gold_mine': GoldMine}
            self.traps.add(trap_classes[self.selected_trap_type](x, y, self))
            self.money -= cost;
            self.achievement_manager.add_progress('master_builder', 1)

    def activate_shockwave(self):
        self.shockwave_timer = self.shockwave_cooldown
        start_pos = (self.path_list[0][0] * GRID_SIZE, self.path_list[0][1] * GRID_SIZE)
        self.create_explosion(start_pos[0], start_pos[1], COLOR_ULTIMATE, is_shockwave=True)
        for enemy in self.enemies: enemy.take_damage(25); enemy.slow(2.0)

    def update(self, dt):
        self.achievement_notifications.update(dt)
        if self.game_state != "playing": return
        self.enemies.update(dt);
        self.traps.update(dt, self);
        self.projectiles.update(dt)
        self.particles.update(dt);
        self.floating_texts.update(dt)
        if self.shockwave_timer > 0: self.shockwave_timer -= dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo_count = 0

        for enemy in list(self.enemies):
            if enemy.path_index >= len(self.path_list) - 1:
                damage = 1 if not isinstance(enemy, Boss) else 10
                self.lives -= damage;
                self.total_enemies_escaped += 1
                enemy.kill()

        if self.lives <= 0: self.end_game(False)
        if not self.wave_in_progress:
            self.wave_timer -= dt
            if self.wave_timer <= 0: self.start_wave()
        if self.wave_in_progress and not self.enemies:
            if self.enemies_killed_this_wave == self.enemies_spawned_this_wave and self.enemies_spawned_this_wave > 0:
                self.achievement_manager.unlock('clean_wave')  # Check for flawless wave
            self.wave_in_progress = False
            if self.wave >= TOTAL_WAVES:
                self.end_game(True)
            else:
                self.wave_timer = 10

    def start_wave(self):
        if len(self.background_images) > 1:
            new_bg = random.choice(self.background_images)
            while new_bg == self.current_background: new_bg = random.choice(self.background_images)
            self.current_background = new_bg
        elif self.background_images:
            self.current_background = self.background_images[0]

        self.wave += 1;
        self.wave_in_progress = True;
        self.wave_timer = 0
        self.enemies_killed_this_wave, self.enemies_spawned_this_wave = 0, 0
        base_health = 20 + (self.wave - 1) * 8
        if self.wave % BOSS_WAVE_INTERVAL == 0:
            self.enemies.add(Boss(self.path_list, base_health * 15 * (1 + self.wave // BOSS_WAVE_INTERVAL), self))
            self.enemies_spawned_this_wave = 1
            return
        enemy_pool = [Grunt]
        if self.wave >= 2: enemy_pool.append(Scout)
        if self.wave >= 4: enemy_pool.append(Brute)
        if self.wave >= 7: enemy_pool.append(Tank)

        num_enemies = self.wave * 4 + 5;
        self.enemies_spawned_this_wave = num_enemies
        for i in range(num_enemies):
            enemy_class = random.choice(enemy_pool)
            enemy = enemy_class(self.path_list, base_health, self)
            enemy.rect.centerx -= i * (GRID_SIZE * 1.5)
            self.enemies.add(enemy)

    def draw(self):
        if self.game_state == "main_menu":
            self.draw_main_menu()
        elif self.game_state == "research_lab":
            self.draw_research_lab()
        elif self.game_state in ["playing", "paused"]:
            self.draw_game_screen()
            if self.game_state == "paused": self.draw_pause_screen()
        elif self.game_state == "game_over":
            self.draw_end_screen()
        self.achievement_notifications.draw(self.screen)  # Draw notifications on top of everything
        pygame.display.flip()

    def draw_game_screen(self):
        if self.current_background:
            self.screen.blit(self.current_background, (0, 0))
        else:
            self.screen.fill(COLOR_PATH)
        self.draw_grid()
        if isinstance(self.selected_trap_instance, TurretTrap): self.draw_range_indicator(self.selected_trap_instance)
        self.traps.draw(self.screen)
        for trap in self.traps: trap.draw_health_bar(self.screen)
        for enemy in self.enemies: enemy.draw(self.screen)
        for enemy in self.enemies: enemy.draw_health_bar(self.screen)
        self.particles.draw(self.screen);
        self.projectiles.draw(self.screen);
        self.floating_texts.draw(self.screen)
        self.draw_ui()

    def draw_main_menu(self):
        self.screen.fill(COLOR_UI_BG)
        title = self.large_font.render("Dungeon Warfare", True, COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))
        self.new_game_button.draw(self.screen);
        self.research_button.draw(self.screen)

    def draw_research_lab(self):
        self.screen.fill(COLOR_UI_BG)
        title = self.large_font.render("Research Lab", True, COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))
        rp_text = self.font.render(f"Research Points: {self.research.data['research_points']}", True, COLOR_TEXT)
        self.screen.blit(rp_text, rp_text.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        upgrades_x, buttons_x, stats_x, upgrades_y = SCREEN_WIDTH // 2 - 220, SCREEN_WIDTH // 2 - 220 + 230, 40, 150
        upgrades = {'spike_damage': 'Spike Dmg', 'spike_health': 'Spike HP', 'slow_duration': 'Slow Time',
                    'slow_health': 'Slow HP', 'turret_damage': 'Turret Dmg', 'turret_range': 'Turret Rng',
                    'gold_income': 'Gold Income'}
        for i, (key, name) in enumerate(upgrades.items()):
            level, cost = self.research.data['upgrades'][key], self.research.get_upgrade_cost(key)
            text = self.font.render(f"{name}: Lvl {level} (Cost: {cost})", True, COLOR_TEXT)
            self.screen.blit(text, (upgrades_x, upgrades_y + i * 50))
            btn = self.research_buttons[key];
            btn.rect.x = buttons_x
            btn.is_enabled = self.research.data['research_points'] >= cost;
            btn.draw(self.screen)
        stats_y_start = 150;
        self.screen.blit(self.font.render("Lifetime Stats:", True, COLOR_TEXT), (stats_x, stats_y_start))
        s = self.research.data['stats']
        stat_lines = [f"Rank: {self.research.data['rank']} ({s['rank_victories']} Wins)",
                      f"Total Wins: {s['victories']}", f"Total Kills: {s['total_kills']}",
                      f"Games Played: {s['games_played']}"]
        for i, line in enumerate(stat_lines): self.screen.blit(self.font.render(line, True, COLOR_TEXT),
                                                               (stats_x, stats_y_start + 50 + (i * 50)))
        rank_image = self.rank_images.get(self.research.data['rank'])
        if rank_image: self.screen.blit(rank_image, (SCREEN_WIDTH - rank_image.get_width() - 20, 150))
        self.main_menu_button.draw(self.screen)

    def draw_range_indicator(self, turret):
        s = pygame.Surface((turret.range * 2, turret.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, COLOR_RANGE_INDICATOR, (turret.range, turret.range), int(turret.range))
        self.screen.blit(s, (turret.rect.centerx - turret.range, turret.rect.centery - turret.range))

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if self.grid[y][x] == 0:
                    s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA); s.fill(
                        (*COLOR_WALL, 180)); self.screen.blit(s, rect.topleft)
                else:
                    if (x, y) in self.path_set: pygame.draw.circle(self.screen, (*COLOR_PATH_INDICATOR, 150),
                                                                   rect.center, GRID_SIZE // 4)
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_ui(self):
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - INFO_PANEL_HEIGHT, SCREEN_WIDTH, INFO_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, ui_rect);
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, ui_rect, 2)
        self.screen.blit(self.font.render(f"Money: ${self.money}", True, COLOR_TEXT), (10, SCREEN_HEIGHT - 90))
        self.screen.blit(self.font.render(f"Lives: {self.lives}", True, COLOR_TEXT), (10, SCREEN_HEIGHT - 50))
        self.screen.blit(self.font.render(f"Wave: {self.wave}/{TOTAL_WAVES}", True, COLOR_TEXT),
                         (200, SCREEN_HEIGHT - 90))
        if not self.wave_in_progress and self.wave < TOTAL_WAVES: self.screen.blit(
            self.small_font.render("SPACE for next wave (+$25)", True, COLOR_TEXT), (180, SCREEN_HEIGHT - 55))
        shock_color = COLOR_ULTIMATE if self.shockwave_timer <= 0 else COLOR_DISABLED_BUTTON
        shock_text = "READY" if self.shockwave_timer <= 0 else f"{self.shockwave_timer:.1f}s"
        self.screen.blit(self.small_font.render(f"[F] Shockwave: {shock_text}", True, shock_color),
                         (180, SCREEN_HEIGHT - 25))
        if self.combo_count > 2:
            combo_font = pygame.font.SysFont("Arial", 30 + self.combo_count, bold=True)
            combo_surf = combo_font.render(f"{self.combo_count}x COMBO!", True, COLOR_COMBO)
            self.screen.blit(combo_surf, combo_surf.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        controls_x, info_x = 420, 750
        self.screen.blit(self.small_font.render("--- Build ---", True, COLOR_UI_BORDER),
                         (controls_x, SCREEN_HEIGHT - 95))
        self.screen.blit(self.small_font.render("[1] Spike: $50", True, COLOR_TEXT), (controls_x, SCREEN_HEIGHT - 70))
        self.screen.blit(self.small_font.render("[2] Slow: $75", True, COLOR_TEXT), (controls_x, SCREEN_HEIGHT - 45))
        self.screen.blit(self.small_font.render("[3] Turret: $100", True, COLOR_TEXT),
                         (controls_x + 160, SCREEN_HEIGHT - 70))
        self.screen.blit(self.small_font.render("[4] Mine: $60", True, COLOR_TEXT),
                         (controls_x + 160, SCREEN_HEIGHT - 45))
        if self.selected_trap_instance:
            trap = self.selected_trap_instance
            pygame.draw.line(self.screen, COLOR_UI_BORDER, (info_x - 20, SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 5),
                             (info_x - 20, SCREEN_HEIGHT - 5), 2)
            cost_text = "Status: ULTIMATE!" if trap.is_ultimate else f"Upgrade [U]: ${trap.upgrade_cost}"
            sell_text, hp_text = f"Sell [S]: ${int(trap.total_investment * 0.7)}", f"Health: {int(trap.health)}/{int(trap.max_health)}"
            info = f"{type(trap).__name__} L{trap.level}"
            self.screen.blit(self.font.render(info, True, COLOR_TEXT), (info_x, SCREEN_HEIGHT - 95))
            self.screen.blit(self.small_font.render(hp_text, True, COLOR_TEXT), (info_x, SCREEN_HEIGHT - 65))
            self.screen.blit(self.small_font.render(cost_text, True, COLOR_TEXT), (info_x, SCREEN_HEIGHT - 45))
            self.screen.blit(self.small_font.render(sell_text, True, COLOR_TEXT), (info_x, SCREEN_HEIGHT - 25))
        else:
            self.screen.blit(self.small_font.render("Click a trap to see details.", True, COLOR_TEXT),
                             (info_x, SCREEN_HEIGHT - 55))

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
        overlay.fill(COLOR_PAUSE_BG)
        self.screen.blit(overlay, (0, 0))
        pause_text = self.large_font.render("PAUSED", True, COLOR_TEXT)
        self.screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))

    def draw_end_screen(self):
        bg = COLOR_WIN_BG if self.last_game_stats['victory'] else COLOR_GAME_OVER_BG
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
        overlay.fill((*bg, 230));
        self.screen.blit(overlay, (0, 0))
        title = self.large_font.render("Victory!" if self.last_game_stats['victory'] else "Game Over", True, COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))
        box = pygame.Rect(0, 0, 450, 250);
        box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, COLOR_UI_BG, box, border_radius=15);
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, box, 3, border_radius=15)
        y, stats = box.centery - 80, self.last_game_stats
        texts = [f"Waves Survived: {stats['waves']}/{TOTAL_WAVES}", f"Enemies Killed: {stats['kills']}",
                 f"Research Points Earned: +{stats['points']}"]
        if stats['clean_bonus'] > 0:
            texts.append(f"PERFECT GAME BONUS: +{stats['clean_bonus']} RP")
        for i, text in enumerate(texts):
            surf = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, y + i * 50)))
        self.main_menu_button.rect.center = (SCREEN_WIDTH // 2, box.bottom + 60)
        self.main_menu_button.draw(self.screen)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()