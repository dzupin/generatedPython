import pygame
import math
import random

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Game Constants and Settings ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
GAME_PANEL_WIDTH = 256

# Colors
COLOR_GRASS_TOP = (58, 142, 58)
COLOR_GRASS_BOTTOM = (40, 98, 40)
COLOR_PATH = (188, 158, 114)
COLOR_PANEL = (50, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_HEALTH_GREEN = (0, 255, 0)
COLOR_HEALTH_RED = (255, 0, 0)
COLOR_RANGE_CIRCLE = (255, 255, 255, 50)
COLOR_BUTTON_DISABLED = (40, 40, 40)

# Game Fonts
FONT_UI = pygame.font.SysFont("Arial", 24)
FONT_TITLE = pygame.font.SysFont("Arial", 32, bold=True)
FONT_GAME_OVER = pygame.font.SysFont("Arial", 64, bold=True)

# Game Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Procedural Tower Defense (Polished)")

# Game Variables
game_running = True
game_over = False
player_health = 20
player_money = 650
current_wave = 0
selected_tower = None
placing_tower_type = None

# Enemy Path (Waypoints)
enemy_path = [
    (-50, 150), (150, 150), (150, 400), (400, 400), (400, 250),
    (650, 250), (650, 550), (900, 550), (900, 100), (SCREEN_WIDTH - GAME_PANEL_WIDTH + 50, 100)
]

# Wave definitions: (enemy_type, count, spawn_delay)
wave_definitions = [
    [("grunt", 10, 60)],
    [("grunt", 15, 50)],
    [("runner", 5, 80), ("grunt", 10, 40)],
    [("grunt", 20, 30), ("runner", 8, 70)],
    [("tank", 3, 200)],
    [("tank", 5, 180), ("runner", 15, 40)],
    [("grunt", 30, 20)],
    [("tank", 8, 150), ("grunt", 25, 25)],
    [("runner", 40, 15)],
    [("tank", 12, 120), ("runner", 20, 30), ("grunt", 20, 30)],
]


# --- Helper Functions ---
def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# --- Particle and Effect Classes ---
class Effect:
    """A generic class for visual effects like explosions and muzzle flashes."""

    def __init__(self, pos, shape, color, size, duration, vel=None, size_decay=0, alpha_decay=0):
        self.pos = list(pos)
        self.shape = shape
        self.color = list(color)
        self.size = size
        self.duration = duration
        self.vel = vel if vel else [0, 0]
        self.size_decay = size_decay
        self.alpha_decay = alpha_decay
        self.is_active = True
        self.alpha = 255

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.is_active = False
            return

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.size -= self.size_decay
        self.alpha -= self.alpha_decay
        self.alpha = max(0, self.alpha)

    def draw(self, surface):
        if self.size <= 0: return

        if self.shape == 'circle':
            # Create a temporary surface to handle alpha transparency
            temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.color, self.alpha), (self.size, self.size), self.size)
            surface.blit(temp_surf, (self.pos[0] - self.size, self.pos[1] - self.size))


# --- Game Entity Classes ---

class Enemy:
    def __init__(self, enemy_type, start_pos):
        self.pos = list(start_pos)
        self.type = enemy_type
        self.path_index = 0
        self.target_pos = enemy_path[0]
        self.is_alive = True
        self.effects = {}

        if self.type == "grunt":
            self.max_health = 100
            self.speed = 1.5
            self.reward = 10
            self.color = (50, 150, 50)
            self.size = 20
        elif self.type == "runner":
            self.max_health = 60
            self.speed = 3.0
            self.reward = 15
            self.color = (200, 50, 50)
            self.size = 16
        elif self.type == "tank":
            self.max_health = 500
            self.speed = 0.8
            self.reward = 50
            self.color = (100, 50, 150)
            self.size = 30

        self.health = self.max_health

    def update(self):
        if not self.is_alive: return
        current_speed = self.speed
        if "slow" in self.effects:
            effect = self.effects["slow"]
            current_speed *= effect["factor"]
            effect["timer"] -= 1
            if effect["timer"] <= 0: del self.effects["slow"]

        dist = distance(self.pos, self.target_pos)
        if dist < current_speed:
            self.path_index += 1
            if self.path_index >= len(enemy_path):
                self.reach_end()
                return
            self.target_pos = enemy_path[self.path_index]

        direction_x, direction_y = self.target_pos[0] - self.pos[0], self.target_pos[1] - self.pos[1]
        norm = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if norm > 0:
            self.pos[0] += direction_x / norm * current_speed
            self.pos[1] += direction_y / norm * current_speed

    def draw(self, surface):
        if not self.is_alive: return
        rect = pygame.Rect(self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
        health_bar_width, health_bar_height = self.size, 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, COLOR_HEALTH_RED,
                         (self.pos[0] - health_bar_width / 2, self.pos[1] - self.size / 2 - 10, health_bar_width,
                          health_bar_height))
        pygame.draw.rect(surface, COLOR_HEALTH_GREEN,
                         (self.pos[0] - health_bar_width / 2, self.pos[1] - self.size / 2 - 10,
                          health_bar_width * health_ratio, health_bar_height))

    def take_damage(self, amount):
        global player_money
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False
            player_money += self.reward

    def apply_effect(self, effect_type, duration, factor):
        self.effects[effect_type] = {"timer": duration, "factor": factor}

    def reach_end(self):
        global player_health
        self.is_alive = False
        player_health -= 1


class Tower:
    def __init__(self, pos, tower_type):
        self.pos = pos
        self.type = tower_type
        self.level = 1
        self.cooldown_timer = 0
        self.target = None
        self.set_stats()

    def set_stats(self):
        if self.type == "gatling":
            self.base_color, self.barrel_color = (128, 128, 128), (80, 80, 80)
            self.damage, self.range, self.cooldown = [8, 15, 25][self.level - 1], [120, 140, 160][self.level - 1], \
            [20, 15, 10][self.level - 1]
            self.cost, self.upgrade_cost = 100, [150, 250, 0][self.level - 1]
        elif self.type == "cannon":
            self.base_color, self.barrel_color = (40, 40, 40), (20, 20, 20)
            self.damage, self.range, self.cooldown = [40, 80, 150][self.level - 1], [180, 200, 220][self.level - 1], \
            [120, 110, 100][self.level - 1]
            self.splash_radius = [25, 30, 35][self.level - 1]
            self.cost, self.upgrade_cost = 250, [300, 500, 0][self.level - 1]
        elif self.type == "slowing":
            self.base_color, self.barrel_color = (50, 100, 200), (100, 150, 255)
            self.damage, self.range, self.cooldown = 0, [150, 170, 190][self.level - 1], [60, 60, 60][self.level - 1]
            self.slow_factor, self.slow_duration = [0.6, 0.5, 0.4][self.level - 1], 60
            self.cost, self.upgrade_cost = 150, [100, 150, 0][self.level - 1]

    def upgrade(self):
        global player_money
        if self.level < 3 and player_money >= self.upgrade_cost:
            player_money -= self.upgrade_cost
            self.level += 1
            self.set_stats()

    def find_target(self, enemies):
        if self.target and (
                not self.target.is_alive or distance(self.pos, self.target.pos) > self.range): self.target = None
        if not self.target:
            for enemy in enemies:
                if enemy.is_alive and distance(self.pos, enemy.pos) <= self.range:
                    self.target = enemy
                    break

    def update(self, enemies, projectiles, effects):
        self.cooldown_timer = max(0, self.cooldown_timer - 1)
        self.find_target(enemies)
        if self.target and self.cooldown_timer == 0:
            self.cooldown_timer = self.cooldown
            self.fire(projectiles, effects)

    def fire(self, projectiles, effects):
        if self.type == "gatling":
            projectiles.append(Projectile(self.pos, self.target, self.damage, 5, (255, 255, 0)))
            angle = math.atan2(self.target.pos[1] - self.pos[1], self.target.pos[0] - self.pos[0])
            flash_pos = (self.pos[0] + 25 * math.cos(angle), self.pos[1] + 25 * math.sin(angle))
            effects.append(Effect(flash_pos, 'circle', (255, 255, 150), 8, 5, size_decay=1.5))
        elif self.type == "cannon":
            projectiles.append(
                Projectile(self.pos, self.target, self.damage, 3, (0, 0, 0), splash_radius=self.splash_radius))
        elif self.type == "slowing":
            effects.append(Effect(self.pos, 'circle', (150, 180, 255), self.range, 30, alpha_decay=8.5))
            for enemy in game.enemies:
                if enemy.is_alive and distance(self.pos, enemy.pos) <= self.range:
                    enemy.apply_effect("slow", self.slow_duration, self.slow_factor)

    def draw(self, surface):
        if selected_tower is self:
            range_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, COLOR_RANGE_CIRCLE, self.pos, self.range)
            surface.blit(range_surface, (0, 0))

        if self.type == "slowing":
            points = [(self.pos[0] + 20 * math.cos(math.pi / 180 * (60 * i - 30)),
                       self.pos[1] + 20 * math.sin(math.pi / 180 * (60 * i - 30))) for i in range(6)]
            pygame.draw.polygon(surface, self.base_color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 3)
        else:
            pygame.draw.rect(surface, self.base_color, (self.pos[0] - 20, self.pos[1] - 20, 40, 40))
            pygame.draw.rect(surface, (0, 0, 0), (self.pos[0] - 20, self.pos[1] - 20, 40, 40), 3)

        angle = math.atan2(self.target.pos[1] - self.pos[1],
                           self.target.pos[0] - self.pos[0]) if self.target else -math.pi / 2
        end_x, end_y = self.pos[0] + 25 * math.cos(angle), self.pos[1] + 25 * math.sin(angle)

        if self.type in ["gatling", "cannon"]:
            pygame.draw.line(surface, self.barrel_color, self.pos, (end_x, end_y), 6 if self.type == "gatling" else 12)
        elif self.type == "slowing":
            pulse_size = 8 + (math.sin(pygame.time.get_ticks() / 200) + 1) * 3
            pygame.draw.circle(surface, self.barrel_color, self.pos, int(pulse_size))

        for i in range(self.level - 1):
            points = [(self.pos[0] - 15 + i * 10, self.pos[1] + 18), (self.pos[0] - 10 + i * 10, self.pos[1] + 12),
                      (self.pos[0] - 5 + i * 10, self.pos[1] + 18)]
            pygame.draw.lines(surface, (255, 215, 0), False, points, 3)


class Projectile:
    def __init__(self, start_pos, target, damage, speed, color, splash_radius=0):
        self.pos, self.target, self.damage, self.speed, self.color, self.splash_radius = list(
            start_pos), target, damage, speed, color, splash_radius
        self.is_active = True

    def update(self, enemies, effects):
        if not self.is_active or not self.target.is_alive: self.is_active = False; return
        target_pos = self.target.pos
        if distance(self.pos, target_pos) < self.speed: self.hit(enemies, effects); return
        dir_x, dir_y = target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]
        norm = math.sqrt(dir_x ** 2 + dir_y ** 2)
        if norm > 0: self.pos[0] += dir_x / norm * self.speed; self.pos[1] += dir_y / norm * self.speed

    def hit(self, enemies, effects):
        self.is_active = False
        self.target.take_damage(self.damage)
        if self.splash_radius > 0:
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 4)
                vel = [speed * math.cos(angle), speed * math.sin(angle)]
                color = random.choice([(255, 100, 0), (255, 200, 50), (200, 50, 0)])
                effects.append(
                    Effect(self.target.pos, 'circle', color, random.randint(3, 8), 20, vel=vel, size_decay=0.3))

            for enemy in enemies:
                if enemy is not self.target and enemy.is_alive and distance(self.target.pos,
                                                                            enemy.pos) <= self.splash_radius:
                    enemy.take_damage(self.damage * 0.5)

    def draw(self, surface):
        if self.is_active: pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), 4)


class Button:
    def __init__(self, rect, text, callback, check_afford=None):
        self.rect, self.text, self.callback, self.check_afford = pygame.Rect(rect), text, callback, check_afford
        self.color, self.hover_color = (100, 100, 100), (150, 150, 150)
        self.is_hovered, self.is_enabled = False, True

    def draw(self, surface):
        self.is_enabled = self.check_afford() if self.check_afford else True
        current_color = self.color if self.is_enabled else COLOR_BUTTON_DISABLED
        final_color = self.hover_color if self.is_hovered and self.is_enabled else current_color

        pygame.draw.rect(surface, final_color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = FONT_UI.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered and self.is_enabled:
            self.callback()
            return True
        return False


class Game:
    def __init__(self):
        self.towers, self.enemies, self.projectiles, self.effects = [], [], [], []
        self.wave_spawn_list, self.wave_spawn_timer = [], 0

        # --- DEBUGGED LINE ---
        self.time_between_waves = 900
        self.wave_cooldown = self.time_between_waves

        self.setup_ui()

    def setup_ui(self):
        self.buttons = []
        panel_x = SCREEN_WIDTH - GAME_PANEL_WIDTH + 20
        self.buttons.append(
            Button((panel_x, 180, 216, 50), "Gatling ($100)", lambda: self.select_tower_to_place("gatling"),
                   lambda: player_money >= 100))
        self.buttons.append(
            Button((panel_x, 240, 216, 50), "Cannon ($250)", lambda: self.select_tower_to_place("cannon"),
                   lambda: player_money >= 250))
        self.buttons.append(
            Button((panel_x, 300, 216, 50), "Slowing ($150)", lambda: self.select_tower_to_place("slowing"),
                   lambda: player_money >= 150))
        self.upgrade_button = Button((panel_x, 500, 216, 50), "Upgrade", self.upgrade_selected_tower,
                                     lambda: selected_tower and selected_tower.level < 3 and player_money >= selected_tower.upgrade_cost)
        self.buttons.append(self.upgrade_button)
        self.start_wave_button = Button((panel_x, SCREEN_HEIGHT - 70, 216, 50), "Start Wave", self.start_next_wave)
        self.buttons.append(self.start_wave_button)

    def select_tower_to_place(self, tower_type):
        global placing_tower_type, selected_tower
        placing_tower_type, selected_tower = tower_type, None

    def upgrade_selected_tower(self):
        if selected_tower: selected_tower.upgrade()

    def start_next_wave(self):
        global current_wave, player_money
        if not self.wave_spawn_list and current_wave < len(wave_definitions):
            if self.wave_cooldown < self.time_between_waves:
                bonus = int(((self.time_between_waves - self.wave_cooldown) / self.time_between_waves) * (
                            50 + current_wave * 5))
                player_money += bonus

            current_wave += 1
            wave_data = wave_definitions[current_wave - 1]
            self.wave_spawn_list = []
            for enemy_type, count, delay in wave_data:
                for i in range(count): self.wave_spawn_list.append((enemy_type, i * delay))
            self.wave_spawn_list.sort(key=lambda x: x[1])
            self.wave_spawn_timer, self.wave_cooldown = 0, 0
            self.start_wave_button.text = "Wave in Progress"

    def handle_events(self, events):
        global placing_tower_type, selected_tower, game_running
        for event in events:
            if event.type == pygame.QUIT: game_running = False
            for button in self.buttons: button.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < SCREEN_WIDTH - GAME_PANEL_WIDTH:
                    if placing_tower_type:
                        self.place_tower(mouse_pos)
                    else:
                        selected_tower = next((t for t in self.towers if distance(mouse_pos, t.pos) < 20), None)

    def place_tower(self, pos):
        global player_money, placing_tower_type
        path_rects = [pygame.Rect(min(p1[0], p2[0]) - 25, min(p1[1], p2[1]) - 25, abs(p1[0] - p2[0]) + 50,
                                  abs(p1[1] - p2[1]) + 50) for i in range(len(enemy_path) - 1) for p1, p2 in
                      [(enemy_path[i], enemy_path[i + 1])]]
        if any(rect.collidepoint(pos) for rect in path_rects) or any(
            distance(pos, t.pos) < 40 for t in self.towers): return
        new_tower = Tower(pos, placing_tower_type)
        if player_money >= new_tower.cost:
            player_money -= new_tower.cost
            self.towers.append(new_tower)
            placing_tower_type = None

    def update(self):
        if game_over: return
        for tower in self.towers: tower.update(self.enemies, self.projectiles, self.effects)
        for projectile in self.projectiles: projectile.update(self.enemies, self.effects)
        for effect in self.effects: effect.update()
        for enemy in self.enemies: enemy.update()
        self.enemies = [e for e in self.enemies if e.is_alive]
        self.projectiles = [p for p in self.projectiles if p.is_active]
        self.effects = [e for e in self.effects if e.is_active]
        if self.wave_spawn_list:
            self.wave_spawn_timer += 1
            if self.wave_spawn_list and self.wave_spawn_list[0][1] < self.wave_spawn_timer:
                enemy_type, _ = self.wave_spawn_list.pop(0)
                self.enemies.append(Enemy(enemy_type, enemy_path[0]))
        elif not self.enemies:
            if self.wave_cooldown < self.time_between_waves: self.wave_cooldown += 1
            if self.wave_cooldown >= self.time_between_waves and current_wave < len(wave_definitions):
                self.start_wave_button.text = f"Start Wave {current_wave + 1}"
            elif current_wave >= len(wave_definitions):
                self.start_wave_button.text = "YOU WIN!"

    def draw(self, surface):
        self.draw_map(surface)
        for enemy in self.enemies: enemy.draw(surface)
        for tower in self.towers: tower.draw(surface)
        for projectile in self.projectiles: projectile.draw(surface)
        for effect in self.effects: effect.draw(surface)
        if placing_tower_type: self.draw_placement_preview(surface)
        self.draw_ui(surface)
        if game_over: self.draw_game_over(surface)

    def draw_map(self, surface):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (
                int(COLOR_GRASS_TOP[0] * (1 - ratio) + COLOR_GRASS_BOTTOM[0] * ratio),
                int(COLOR_GRASS_TOP[1] * (1 - ratio) + COLOR_GRASS_BOTTOM[1] * ratio),
                int(COLOR_GRASS_TOP[2] * (1 - ratio) + COLOR_GRASS_BOTTOM[2] * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH - GAME_PANEL_WIDTH, y))
        for i in range(len(enemy_path) - 1): pygame.draw.line(surface, COLOR_PATH, enemy_path[i], enemy_path[i + 1], 50)
        for point in enemy_path: pygame.draw.circle(surface, COLOR_PATH, point, 25)

    def draw_placement_preview(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > SCREEN_WIDTH - GAME_PANEL_WIDTH: return
        temp_tower = Tower(mouse_pos, placing_tower_type)
        range_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*COLOR_RANGE_CIRCLE[:3], 100), mouse_pos, temp_tower.range)
        surface.blit(range_surface, (0, 0))
        base_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        base_surf.fill((*temp_tower.base_color, 128))
        surface.blit(base_surf, (mouse_pos[0] - 20, mouse_pos[1] - 20))

    def draw_ui(self, surface):
        panel_rect = (SCREEN_WIDTH - GAME_PANEL_WIDTH, 0, GAME_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect)
        surface.blit(FONT_UI.render(f"Health: {player_health}", True, COLOR_TEXT), (panel_rect[0] + 20, 20))
        surface.blit(FONT_UI.render(f"Money: ${player_money}", True, COLOR_TEXT), (panel_rect[0] + 20, 50))
        surface.blit(FONT_UI.render(f"Wave: {current_wave}/{len(wave_definitions)}", True, COLOR_TEXT),
                     (panel_rect[0] + 20, 80))
        surface.blit(FONT_TITLE.render("Build Towers", True, COLOR_TEXT), (panel_rect[0] + 20, 130))
        for button in self.buttons: button.draw(surface)

        if selected_tower:
            info_title = FONT_TITLE.render(f"Lvl {selected_tower.level} {selected_tower.type.capitalize()}", True,
                                           COLOR_TEXT)
            surface.blit(info_title, (panel_rect[0] + 20, 380))
            surface.blit(FONT_UI.render(f"Damage: {selected_tower.damage}", True, COLOR_TEXT),
                         (panel_rect[0] + 20, 420))
            surface.blit(FONT_UI.render(f"Range: {selected_tower.range}", True, COLOR_TEXT), (panel_rect[0] + 20, 445))
            if selected_tower.type != "slowing":
                speed = round(60 / selected_tower.cooldown, 1)
                surface.blit(FONT_UI.render(f"Speed: {speed}/s", True, COLOR_TEXT), (panel_rect[0] + 20, 470))
            self.upgrade_button.text = f"Upgrade (${selected_tower.upgrade_cost})" if selected_tower.level < 3 else "Max Level"
        else:
            self.upgrade_button.text = "Upgrade"

        if not self.wave_spawn_list and not self.enemies and current_wave < len(wave_definitions):
            bonus = int(
                ((self.time_between_waves - self.wave_cooldown) / self.time_between_waves) * (50 + current_wave * 5))
            if bonus > 0:
                bonus_text = FONT_UI.render(f"Wave Rush Bonus: ${bonus}", True, (255, 215, 0))
                surface.blit(bonus_text, (panel_rect[0] + 20, SCREEN_HEIGHT - 110))

    def draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        game_over_text = FONT_GAME_OVER.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        surface.blit(game_over_text, text_rect)
        wave_reached_text = FONT_TITLE.render(f"You reached wave {current_wave}", True, COLOR_TEXT)
        wave_rect = wave_reached_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20))
        surface.blit(wave_reached_text, wave_rect)


# --- Main Game Loop ---
if __name__ == "__main__":
    clock = pygame.time.Clock()
    game = Game()
    while game_running:
        events = pygame.event.get()
        game.handle_events(events)
        game.update()
        if player_health <= 0: game_over = True
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()