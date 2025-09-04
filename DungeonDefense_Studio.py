import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 100) // GRID_SIZE
INFO_PANEL_HEIGHT = 100
FPS = 60
TOTAL_WAVES = 10

# Colors
COLOR_WALL = (50, 50, 50)
COLOR_PATH = (100, 100, 100)
COLOR_GRID = (70, 70, 70)
COLOR_PATH_INDICATOR = (40, 40, 40)
COLOR_UI_BG = (30, 30, 30)
COLOR_UI_BORDER = (150, 150, 150)
COLOR_TEXT = (255, 255, 255)
COLOR_ENEMY = (200, 50, 50)
COLOR_SPIKE_TRAP = (120, 120, 120)
COLOR_SPIKE_TRAP_ARMED = (180, 180, 180)
COLOR_SLOW_TRAP = (100, 100, 200)
COLOR_SLOW_TRAP_ACTIVE = (150, 150, 255)
COLOR_TURRET_BASE = (80, 80, 90)
COLOR_TURRET_CANNON = (140, 140, 150)
COLOR_PROJECTILE = (255, 200, 0)
COLOR_RANGE_INDICATOR = (255, 255, 255, 50)  # Transparent white
COLOR_GAME_OVER_BG = (100, 0, 0)
COLOR_WIN_BG = (0, 100, 0)
COLOR_BUTTON = (0, 80, 150)
COLOR_BUTTON_HOVER = (50, 130, 200)


# --- Game Object Classes ---

class Projectile(pygame.sprite.Sprite):
    """ A class for projectiles fired by turrets """

    def __init__(self, x, y, target, damage):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_PROJECTILE, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target
        self.damage = damage
        self.speed = 300  # Pixels per second

    def update(self, dt):
        """ Move the projectile towards its target """
        if not self.target.alive():
            self.kill()
            return

        target_pos = self.target.rect.center
        current_pos = self.rect.center

        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        dist = math.hypot(dx, dy)

        if dist < 5:
            # Hit target
            self.target.take_damage(self.damage)
            self.kill()
            return

        # Move towards target
        self.rect.x += (dx / dist) * self.speed * dt
        self.rect.y += (dy / dist) * self.speed * dt


class Enemy(pygame.sprite.Sprite):
    """ A class to represent the enemies """

    def __init__(self, path, health):
        super().__init__()
        self.path = path
        self.path_index = 0
        self.x, self.y = self.path[0]
        self.image = pygame.Surface([GRID_SIZE // 2, GRID_SIZE // 2])
        self.draw_enemy()
        self.rect = self.image.get_rect(
            center=(self.x * GRID_SIZE + GRID_SIZE // 2, self.y * GRID_SIZE + GRID_SIZE // 2))
        self.speed = 2
        self.max_health = health
        self.health = health
        self.is_slowed = False
        self.slow_timer = 0

    def draw_enemy(self):
        """ Procedurally draws the enemy """
        self.image.fill(COLOR_ENEMY)
        pygame.draw.rect(self.image, (255, 100, 100), self.image.get_rect(), 2)
        eye_surface = pygame.Surface((4, 4))
        eye_surface.fill((255, 255, 255))
        self.image.blit(eye_surface, (5, 5))
        self.image.blit(eye_surface, (self.image.get_width() - 9, 5))

    def update(self, dt):
        """ Updates the enemy's position along the path """
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            target_pixel_x = target_x * GRID_SIZE + GRID_SIZE // 2
            target_pixel_y = target_y * GRID_SIZE + GRID_SIZE // 2

            dx = target_pixel_x - self.rect.centerx
            dy = target_pixel_y - self.rect.centery
            dist = math.hypot(dx, dy)

            current_speed = self.speed
            if self.is_slowed:
                current_speed *= 0.5
                self.slow_timer -= dt
                if self.slow_timer <= 0:
                    self.is_slowed = False

            if dist > current_speed:
                self.rect.centerx += (dx / dist) * current_speed * GRID_SIZE * dt
                self.rect.centery += (dy / dist) * current_speed * GRID_SIZE * dt
            else:
                self.rect.centerx = target_pixel_x
                self.rect.centery = target_pixel_y
                self.path_index += 1

    def take_damage(self, amount):
        """ Reduces enemy health """
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        return False

    def slow(self, duration):
        """ Applies a slow effect to the enemy """
        self.is_slowed = True
        self.slow_timer = duration


class Trap(pygame.sprite.Sprite):
    """ A base class for traps """

    def __init__(self, x, y, cost, upgrade_cost):
        super().__init__()
        self.x = x
        self.y = y
        self.cost = cost
        self.upgrade_cost = upgrade_cost
        self.level = 1
        self.image = pygame.Surface([GRID_SIZE, GRID_SIZE], pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x * GRID_SIZE, y * GRID_SIZE))

    def upgrade(self):
        """ Upgrades the trap """
        self.level += 1


class SpikeTrap(Trap):
    """ A trap that periodically damages enemies """

    def __init__(self, x, y):
        super().__init__(x, y, 50, 30)
        self.damage = 5
        self.cooldown = 2
        self.timer = 0
        self.armed = True
        self.draw()

    def draw(self):
        """ Procedurally draws the spike trap """
        color = COLOR_SPIKE_TRAP_ARMED if self.armed else COLOR_SPIKE_TRAP
        self.image.fill(COLOR_PATH)
        pygame.draw.rect(self.image, color, (5, 5, GRID_SIZE - 10, GRID_SIZE - 10))
        for i in range(3):
            for j in range(3):
                spike_center = (8 + i * 8, 8 + j * 8)
                pygame.draw.polygon(self.image, (150, 150, 150), [
                    (spike_center[0] - 3, spike_center[1] + 3),
                    (spike_center[0] + 3, spike_center[1] + 3),
                    spike_center
                ])

    def update(self, dt, enemies, projectiles):
        """ Updates the trap's state and damages enemies """
        killed_enemy = False
        self.timer -= dt
        if not self.armed and self.timer <= 0:
            self.armed = True
            self.draw()
        if self.armed and self.timer <= 0:
            enemies_on_trap = [e for e in enemies if self.rect.colliderect(e.rect)]
            if enemies_on_trap:
                for enemy in enemies_on_trap:
                    if enemy.take_damage(self.damage):
                        killed_enemy = True
                self.armed = False
                self.timer = self.cooldown
                self.draw()
        return killed_enemy

    def upgrade(self):
        super().upgrade()
        self.damage += 3
        self.upgrade_cost += 10


class SlowTrap(Trap):
    """ A trap that slows enemies """

    def __init__(self, x, y):
        super().__init__(x, y, 75, 40)
        self.slow_duration = 3
        self.draw()

    def draw(self):
        """ Procedurally draws the slow trap """
        self.image.fill(COLOR_PATH)
        pygame.draw.circle(self.image, COLOR_SLOW_TRAP, (GRID_SIZE // 2, GRID_SIZE // 2), GRID_SIZE // 2 - 5)
        pygame.draw.circle(self.image, COLOR_SLOW_TRAP_ACTIVE, (GRID_SIZE // 2, GRID_SIZE // 2), GRID_SIZE // 4)

    def update(self, dt, enemies, projectiles):
        """ Applies slow effect to enemies on the trap """
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.slow(self.slow_duration)
        return False

    def upgrade(self):
        super().upgrade()
        self.slow_duration += 1.5
        self.upgrade_cost += 20


class TurretTrap(Trap):
    """ A trap that shoots projectiles at enemies """

    def __init__(self, x, y):
        super().__init__(x, y, 100, 50)
        self.range = 100  # pixels
        self.damage = 3
        self.cooldown = 1.0  # seconds
        self.timer = 0
        self.angle = 0
        self.target = None
        self.draw()

    def draw(self):
        """ Procedurally draws the turret """
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        # Base
        pygame.draw.circle(self.image, COLOR_TURRET_BASE, (GRID_SIZE // 2, GRID_SIZE // 2), GRID_SIZE // 2 - 4)
        pygame.draw.circle(self.image, COLOR_GRID, (GRID_SIZE // 2, GRID_SIZE // 2), GRID_SIZE // 2 - 4, 2)
        # Cannon
        cannon_length = GRID_SIZE // 2
        end_x = GRID_SIZE // 2 + cannon_length * math.cos(self.angle)
        end_y = GRID_SIZE // 2 + cannon_length * math.sin(self.angle)
        pygame.draw.line(self.image, COLOR_TURRET_CANNON, (GRID_SIZE // 2, GRID_SIZE // 2), (end_x, end_y), 6)

    def find_target(self, enemies):
        """ Finds the best enemy to shoot at """
        self.target = None
        in_range_enemies = []
        for enemy in enemies:
            dist = math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery)
            if dist <= self.range:
                in_range_enemies.append(enemy)

        # Target enemy closest to the end of the path
        if in_range_enemies:
            self.target = max(in_range_enemies, key=lambda e: e.path_index)

    def update(self, dt, enemies, projectiles):
        """ Aims, and shoots at enemies """
        self.timer -= dt
        self.find_target(enemies)

        if self.target:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            self.angle = math.atan2(dy, dx)
            self.draw()

            if self.timer <= 0:
                proj = Projectile(self.rect.centerx, self.rect.centery, self.target, self.damage)
                projectiles.add(proj)
                self.timer = self.cooldown
        return False  # Turret killing is handled by the projectile

    def upgrade(self):
        super().upgrade()
        self.range += 15
        self.damage += 2
        self.cooldown *= 0.9  # Fire faster
        self.upgrade_cost += 25


# --- Button Class ---
class Button:
    """ A simple button class """

    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, screen):
        """ Draws the button on the screen """
        color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """ Checks if the mouse is hovering over the button """
        self.is_hovered = self.rect.collidepoint(mouse_pos)


# --- Game Class ---

class Game:
    """ The main game class """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Warfare")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.large_font = pygame.font.SysFont(None, 72)
        self.running = True
        self.game_state = "playing"
        self.new_game_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50, "New Game", self.font)
        self.reset_game()

    def reset_game(self):
        """ Resets the game to its initial state """
        self.path_list = []
        while not self.path_list:
            self.grid = self.create_grid()
            self.path_list = self.find_path()
        self.path_set = set(self.path_list)

        self.enemies = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        self.money = 2000
        self.lives = 20
        self.wave = 0
        self.wave_timer = 10
        self.wave_in_progress = False

        self.enemies_killed = 0
        self.money_earned = 2000

        self.selected_trap_type = None
        self.selected_trap_instance = None
        self.game_state = "playing"

    def create_grid(self):
        """ Creates the dungeon grid """
        grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if 1 < x < GRID_WIDTH - 2 and random.random() < 0.3:
                    grid[y][x] = 0
        grid[GRID_HEIGHT // 2][0] = 1
        grid[GRID_HEIGHT // 2][GRID_WIDTH - 1] = 1
        return grid

    def find_path(self):
        """ Finds a path for enemies using A* """
        start = (0, GRID_HEIGHT // 2)
        end = (GRID_WIDTH - 1, GRID_HEIGHT // 2)
        open_set = {start}
        came_from = {}
        g_score = {(x, y): float('inf') for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH)}
        g_score[start] = 0
        f_score = {(x, y): float('inf') for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH)}
        f_score[start] = self.heuristic(start, end)

        while open_set:
            current = min(open_set, key=lambda o: f_score.get(o, float('inf')))
            if current == end:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and self.grid[neighbor[1]][
                    neighbor[0]] == 1:
                    tentative_g_score = g_score.get(current, float('inf')) + 1
                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, end)
                        if neighbor not in open_set:
                            open_set.add(neighbor)
        return []

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_mouse_click(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.selected_trap_type = "spike"
                        self.selected_trap_instance = None
                    elif event.key == pygame.K_2:
                        self.selected_trap_type = "slow"
                        self.selected_trap_instance = None
                    elif event.key == pygame.K_3:
                        self.selected_trap_type = "turret"
                        self.selected_trap_instance = None
                    elif event.key == pygame.K_u and self.selected_trap_instance:
                        if self.money >= self.selected_trap_instance.upgrade_cost:
                            self.money -= self.selected_trap_instance.upgrade_cost
                            self.selected_trap_instance.upgrade()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.new_game_button.rect.collidepoint(event.pos):
                        self.reset_game()

    def handle_mouse_click(self, pos):
        grid_x, grid_y = pos[0] // GRID_SIZE, pos[1] // GRID_SIZE
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            trap_at_pos = self.get_trap_at(grid_x, grid_y)
            if self.selected_trap_type and not trap_at_pos:
                self.place_trap(grid_x, grid_y)
            elif trap_at_pos:
                self.selected_trap_instance = trap_at_pos
                self.selected_trap_type = None

    def get_trap_at(self, x, y):
        for trap in self.traps:
            if trap.x == x and trap.y == y:
                return trap
        return None

    def place_trap(self, x, y):
        # Can place turrets on walls, others on path
        can_place = (self.selected_trap_type == 'turret' and self.grid[y][x] == 0) or \
                    (self.selected_trap_type != 'turret' and self.grid[y][x] == 1)

        if not can_place: return

        if self.selected_trap_type == "spike" and self.money >= 50:
            self.traps.add(SpikeTrap(x, y))
            self.money -= 50
        elif self.selected_trap_type == "slow" and self.money >= 75:
            self.traps.add(SlowTrap(x, y))
            self.money -= 75
        elif self.selected_trap_type == "turret" and self.money >= 100:
            self.traps.add(TurretTrap(x, y))
            self.money -= 100

    def update(self, dt):
        if self.game_state == "playing":
            self.enemies.update(dt)
            self.projectiles.update(dt)

            # Update traps and check for kills
            for trap in self.traps:
                if trap.update(dt, self.enemies, self.projectiles):
                    self.enemies_killed += 1
                    self.money += 5
                    self.money_earned += 5

            # Check for kills from projectiles
            for proj in list(self.projectiles):
                if not proj.target.alive():
                    self.enemies_killed += 1
                    self.money += 5
                    self.money_earned += 5

            for enemy in list(self.enemies):
                if enemy.path_index >= len(self.path_list) - 1:
                    self.lives -= 1
                    enemy.kill()
                    if self.lives <= 0:
                        self.lives = 0
                        self.game_state = "game_over"

            if not self.wave_in_progress:
                self.wave_timer -= dt
                if self.wave_timer <= 0:
                    self.start_wave()

            if self.wave_in_progress and not self.enemies:
                self.wave_in_progress = False
                if self.wave >= TOTAL_WAVES:
                    self.game_state = "victory"
                else:
                    self.wave_timer = 10
        else:
            self.new_game_button.check_hover(pygame.mouse.get_pos())

    def start_wave(self):
        self.wave += 1
        self.wave_in_progress = True
        enemy_health = 10 + (self.wave - 1) * 7
        for i in range(self.wave * 5):
            enemy = Enemy(self.path_list, enemy_health)
            enemy.rect.centerx -= i * 40
            self.enemies.add(enemy)

    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.game_state == "playing":
            self.draw_grid()
            if isinstance(self.selected_trap_instance, TurretTrap):
                self.draw_range_indicator(self.selected_trap_instance)
            self.traps.draw(self.screen)
            self.projectiles.draw(self.screen)
            self.enemies.draw(self.screen)
            self.draw_ui()
        elif self.game_state == "game_over":
            self.draw_end_screen("Game Over", COLOR_GAME_OVER_BG)
        elif self.game_state == "victory":
            self.draw_end_screen("Victory!", COLOR_WIN_BG)
        pygame.display.flip()

    def draw_range_indicator(self, turret):
        """ Draws a transparent circle showing the turret's range """
        s = pygame.Surface((turret.range * 2, turret.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, COLOR_RANGE_INDICATOR, (turret.range, turret.range), turret.range)
        self.screen.blit(s, (turret.rect.centerx - turret.range, turret.rect.centery - turret.range))

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if self.grid[y][x] == 0:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
                    if (x, y) in self.path_set:
                        pygame.draw.circle(self.screen, COLOR_PATH_INDICATOR, rect.center, GRID_SIZE // 4)
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_ui(self):
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - INFO_PANEL_HEIGHT, SCREEN_WIDTH, INFO_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, ui_rect)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, ui_rect, 2)

        money_text = self.font.render(f"Money: {self.money}", True, COLOR_TEXT)
        self.screen.blit(money_text, (10, SCREEN_HEIGHT - 90))
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (10, SCREEN_HEIGHT - 50))
        wave_text = self.font.render(f"Wave: {self.wave}/{TOTAL_WAVES}", True, COLOR_TEXT)
        self.screen.blit(wave_text, (200, SCREEN_HEIGHT - 90))

        if not self.wave_in_progress and self.wave < TOTAL_WAVES:
            next_wave_text = self.font.render(f"Next Wave: {int(self.wave_timer) + 1}s", True, COLOR_TEXT)
            self.screen.blit(next_wave_text, (200, SCREEN_HEIGHT - 50))

        trap_info_text = self.small_font.render("1: Spike (50)  2: Slow (75)  3: Turret (100)", True, COLOR_TEXT)
        self.screen.blit(trap_info_text, (380, SCREEN_HEIGHT - 90))
        trap_info_text_2 = self.small_font.render("Click trap, then 'U' to upgrade. Turrets go on walls.", True,
                                                  COLOR_TEXT)
        self.screen.blit(trap_info_text_2, (380, SCREEN_HEIGHT - 50))

        if self.selected_trap_instance:
            trap = self.selected_trap_instance
            cost_text = f"Upgrade: {trap.upgrade_cost}"
            if isinstance(trap, SpikeTrap):
                info = f"Spike | Lvl {trap.level} | Dmg: {trap.damage}"
            elif isinstance(trap, SlowTrap):
                info = f"Slow | Lvl {trap.level} | Dur: {trap.slow_duration:.1f}s"
            elif isinstance(trap, TurretTrap):
                info = f"Turret | Lvl {trap.level} | Dmg: {trap.damage}"

            sel_text_1 = self.font.render(info, True, COLOR_TEXT)
            self.screen.blit(sel_text_1, (740, SCREEN_HEIGHT - 90))
            sel_text_2 = self.font.render(cost_text, True, COLOR_TEXT)
            self.screen.blit(sel_text_2, (740, SCREEN_HEIGHT - 50))

    def draw_end_screen(self, title_text, bg_color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*bg_color, 230))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.large_font.render(title_text, True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)

        stats_box_rect = pygame.Rect(0, 0, 400, 200)
        stats_box_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        pygame.draw.rect(self.screen, COLOR_UI_BG, stats_box_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, stats_box_rect, 3, border_radius=15)

        stats_y_start = stats_box_rect.centery - 45
        waves_survived = self.wave - 1 if self.game_state == "game_over" and self.wave_in_progress else self.wave
        if self.game_state == "victory": waves_survived = TOTAL_WAVES
        waves_text = self.font.render(f"Waves Survived: {waves_survived} / {TOTAL_WAVES}", True, COLOR_TEXT)
        self.screen.blit(waves_text, waves_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y_start)))
        killed_text = self.font.render(f"Enemies Killed: {self.enemies_killed}", True, COLOR_TEXT)
        self.screen.blit(killed_text, killed_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y_start + 45)))
        money_text = self.font.render(f"Total Money Earned: {self.money_earned}", True, COLOR_TEXT)
        self.screen.blit(money_text, money_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y_start + 90)))

        self.new_game_button.rect.center = (SCREEN_WIDTH // 2, stats_box_rect.bottom + 60)
        self.new_game_button.draw(self.screen)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()