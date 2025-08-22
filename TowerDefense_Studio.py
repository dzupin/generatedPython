import pygame
import math
import random
import json
import os

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Game Constants and Settings ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
GAME_PANEL_WIDTH = 256
SAVE_FILE = "upgrades.json"

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
pygame.display.set_caption("Procedural Tower Defense (With Research)")

# --- Save File and Upgrade Management ---
player_upgrades = {}


def load_upgrades():
    global player_upgrades
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            player_upgrades = json.load(f)
    else:
        player_upgrades = {
            "research_points": 0,
            "upgrades": {
                "starting_money": 0,
                "starting_health": 0,
                "gatling_damage": 0,
                "cannon_cost": 0,
            }
        }
        save_upgrades()


def save_upgrades():
    with open(SAVE_FILE, 'w') as f:
        json.dump(player_upgrades, f, indent=4)


# --- Global Game Variables ---
game_state = "MAIN_MENU"
game = None
research_menu = None


# --- Helper Functions ---
def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# --- Particle and Effect Classes ---
class Effect:
    def __init__(self, pos, shape, color, size, duration, vel=None, size_decay=0, alpha_decay=0):
        self.pos, self.shape, self.color, self.size, self.duration = list(pos), shape, list(color), size, duration
        self.vel, self.size_decay, self.alpha_decay = vel if vel else [0, 0], size_decay, alpha_decay
        self.is_active, self.alpha = True, 255

    def update(self):
        self.duration -= 1
        if self.duration <= 0: self.is_active = False; return
        self.pos[0] += self.vel[0];
        self.pos[1] += self.vel[1]
        self.size -= self.size_decay;
        self.alpha = max(0, self.alpha - self.alpha_decay)

    def draw(self, surface):
        if self.size <= 0: return
        if self.shape == 'circle':
            temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.color, self.alpha), (self.size, self.size), self.size)
            surface.blit(temp_surf, (self.pos[0] - self.size, self.pos[1] - self.size))


# --- Game Entity Classes ---
class Enemy:
    def __init__(self, enemy_type, start_pos):
        self.pos, self.type, self.path_index = list(start_pos), enemy_type, 0
        self.target_pos, self.is_alive, self.effects = enemy_path[0], True, {}
        if self.type == "grunt":
            self.max_health, self.speed, self.reward, self.color, self.size = 100, 1.5, 10, (50, 150, 50), 20
        elif self.type == "runner":
            self.max_health, self.speed, self.reward, self.color, self.size = 60, 3.0, 15, (200, 50, 50), 16
        elif self.type == "tank":
            self.max_health, self.speed, self.reward, self.color, self.size = 500, 0.8, 50, (100, 50, 150), 30
        self.health = self.max_health

    def update(self):
        if not self.is_alive: return
        current_speed = self.speed
        if "slow" in self.effects:
            effect = self.effects["slow"]
            current_speed *= effect["factor"];
            effect["timer"] -= 1
            if effect["timer"] <= 0: del self.effects["slow"]
        if distance(self.pos, self.target_pos) < current_speed:
            self.path_index += 1
            if self.path_index >= len(enemy_path): self.reach_end(); return
            self.target_pos = enemy_path[self.path_index]
        dir_x, dir_y = self.target_pos[0] - self.pos[0], self.target_pos[1] - self.pos[1]
        norm = math.sqrt(dir_x ** 2 + dir_y ** 2)
        if norm > 0: self.pos[0] += dir_x / norm * current_speed; self.pos[1] += dir_y / norm * current_speed

    def draw(self, surface):
        if not self.is_alive: return
        rect = pygame.Rect(self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect);
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
        h_bar_w, h_bar_h, h_ratio = self.size, 5, self.health / self.max_health
        pygame.draw.rect(surface, COLOR_HEALTH_RED,
                         (self.pos[0] - h_bar_w / 2, self.pos[1] - self.size / 2 - 10, h_bar_w, h_bar_h))
        pygame.draw.rect(surface, COLOR_HEALTH_GREEN,
                         (self.pos[0] - h_bar_w / 2, self.pos[1] - self.size / 2 - 10, h_bar_w * h_ratio, h_bar_h))

    # --- DEBUGGED: Money is now awarded on death, not on hit ---
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False
            if game: game.player_money += self.reward

    def apply_effect(self, effect_type, duration, factor):
        self.effects[effect_type] = {"timer": duration, "factor": factor}

    def reach_end(self):
        if game: game.player_health -= 1
        self.is_alive = False


class Tower:
    def __init__(self, pos, tower_type):
        self.pos, self.type, self.level = pos, tower_type, 1
        self.cooldown_timer, self.target = 0, None
        self.set_stats()

    def set_stats(self):
        if self.type == "gatling":
            base_damage, damage_bonus = [8, 15, 25][self.level - 1], 1 + (
                        player_upgrades["upgrades"]["gatling_damage"] * 0.05)
            self.damage = int(base_damage * damage_bonus)
            self.range, self.cooldown, self.cost = [120, 140, 160][self.level - 1], [20, 15, 10][self.level - 1], 100
            self.upgrade_cost, self.base_color, self.barrel_color = [150, 250, 0][self.level - 1], (128, 128, 128), (80,
                                                                                                                     80,
                                                                                                                     80)
        elif self.type == "cannon":
            base_cost, cost_reduction = 250, 1 - (player_upgrades["upgrades"]["cannon_cost"] * 0.03)
            self.cost = int(base_cost * cost_reduction)
            self.damage, self.range, self.cooldown = [40, 80, 150][self.level - 1], [180, 200, 220][self.level - 1], \
            [120, 110, 100][self.level - 1]
            self.splash_radius, self.upgrade_cost = [25, 30, 35][self.level - 1], [300, 500, 0][self.level - 1]
            self.base_color, self.barrel_color = (40, 40, 40), (20, 20, 20)
        elif self.type == "slowing":
            self.damage, self.range, self.cooldown, self.cost = 0, [150, 170, 190][self.level - 1], [60, 60, 60][
                self.level - 1], 150
            self.slow_factor, self.slow_duration, self.upgrade_cost = [0.6, 0.5, 0.4][self.level - 1], 60, \
            [100, 150, 0][self.level - 1]
            self.base_color, self.barrel_color = (50, 100, 200), (100, 150, 255)

    def upgrade(self):
        if game and self.level < 3 and game.player_money >= self.upgrade_cost:
            game.player_money -= self.upgrade_cost;
            self.level += 1;
            self.set_stats()

    def find_target(self, enemies):
        if self.target and (
                not self.target.is_alive or distance(self.pos, self.target.pos) > self.range): self.target = None
        if not self.target:
            for enemy in enemies:
                if enemy.is_alive and distance(self.pos, enemy.pos) <= self.range: self.target = enemy; break

    def update(self, enemies, projectiles, effects):
        self.cooldown_timer = max(0, self.cooldown_timer - 1);
        self.find_target(enemies)
        if self.target and self.cooldown_timer == 0: self.cooldown_timer = self.cooldown; self.fire(projectiles,
                                                                                                    effects)

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
                if enemy.is_alive and distance(self.pos, enemy.pos) <= self.range: enemy.apply_effect("slow",
                                                                                                      self.slow_duration,
                                                                                                      self.slow_factor)

    def draw(self, surface):
        if game and game.selected_tower is self:
            rs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
            pygame.draw.circle(rs, COLOR_RANGE_CIRCLE, self.pos, self.range);
            surface.blit(rs, (0, 0))
        if self.type == "slowing":
            pts = [(self.pos[0] + 20 * math.cos(math.pi / 180 * (60 * i - 30)),
                    self.pos[1] + 20 * math.sin(math.pi / 180 * (60 * i - 30))) for i in range(6)]
            pygame.draw.polygon(surface, self.base_color, pts);
            pygame.draw.polygon(surface, (0, 0, 0), pts, 3)
        else:
            pygame.draw.rect(surface, self.base_color, (self.pos[0] - 20, self.pos[1] - 20, 40, 40));
            pygame.draw.rect(surface, (0, 0, 0), (self.pos[0] - 20, self.pos[1] - 20, 40, 40), 3)
        angle = math.atan2(self.target.pos[1] - self.pos[1],
                           self.target.pos[0] - self.pos[0]) if self.target else -math.pi / 2
        end_x, end_y = self.pos[0] + 25 * math.cos(angle), self.pos[1] + 25 * math.sin(angle)
        if self.type in ["gatling", "cannon"]:
            pygame.draw.line(surface, self.barrel_color, self.pos, (end_x, end_y), 6 if self.type == "gatling" else 12)
        elif self.type == "slowing":
            pygame.draw.circle(surface, self.barrel_color, self.pos,
                               int(8 + (math.sin(pygame.time.get_ticks() / 200) + 1) * 3))
        for i in range(self.level - 1):
            pts = [(self.pos[0] - 15 + i * 10, self.pos[1] + 18), (self.pos[0] - 10 + i * 10, self.pos[1] + 12),
                   (self.pos[0] - 5 + i * 10, self.pos[1] + 18)]
            pygame.draw.lines(surface, (255, 215, 0), False, pts, 3)


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
        self.is_active = False;
        self.target.take_damage(self.damage)
        if self.splash_radius > 0:
            for _ in range(15):
                angle, speed = random.uniform(0, 2 * math.pi), random.uniform(1, 4)
                vel, color = [speed * math.cos(angle), speed * math.sin(angle)], random.choice(
                    [(255, 100, 0), (255, 200, 50), (200, 50, 0)])
                effects.append(
                    Effect(self.target.pos, 'circle', color, random.randint(3, 8), 20, vel=vel, size_decay=0.3))
            for enemy in enemies:
                if enemy is not self.target and enemy.is_alive and distance(self.target.pos,
                                                                            enemy.pos) <= self.splash_radius: enemy.take_damage(
                    self.damage * 0.5)

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
        pygame.draw.rect(surface, final_color, self.rect);
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = FONT_UI.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center);
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered and self.is_enabled: self.callback(); return True
        return False


# --- Game Controller Class ---
enemy_path = [(-50, 150), (150, 150), (150, 400), (400, 400), (400, 250), (650, 250), (650, 550), (900, 550),
              (900, 100), (SCREEN_WIDTH - GAME_PANEL_WIDTH + 50, 100)]
wave_definitions = [[("grunt", 10, 60)], [("grunt", 15, 50)], [("runner", 5, 80), ("grunt", 10, 40)],
                    [("grunt", 20, 30), ("runner", 8, 70)], [("tank", 3, 200)], [("tank", 5, 180), ("runner", 15, 40)],
                    [("grunt", 30, 20)], [("tank", 8, 150), ("grunt", 25, 25)], [("runner", 40, 15)],
                    [("tank", 12, 120), ("runner", 20, 30), ("grunt", 20, 30)]]


class Game:
    def __init__(self):
        self.towers, self.enemies, self.projectiles, self.effects = [], [], [], []
        self.wave_spawn_list, self.wave_spawn_timer = [], 0
        self.time_between_waves, self.wave_cooldown = 900, 900
        self.player_health = 20 + player_upgrades["upgrades"]["starting_health"]
        self.player_money = 650 + (player_upgrades["upgrades"]["starting_money"] * 50)
        self.current_wave, self.selected_tower, self.placing_tower_type = 0, None, None
        self.setup_ui()

    def setup_ui(self):
        self.buttons = []
        panel_x = SCREEN_WIDTH - GAME_PANEL_WIDTH + 20
        self.buttons.append(Button((panel_x, 180, 216, 50), f"Gatling (${Tower(None, 'gatling').cost})",
                                   lambda: self.select_tower_to_place("gatling"),
                                   lambda: self.player_money >= Tower(None, "gatling").cost))
        self.buttons.append(Button((panel_x, 240, 216, 50), f"Cannon (${Tower(None, 'cannon').cost})",
                                   lambda: self.select_tower_to_place("cannon"),
                                   lambda: self.player_money >= Tower(None, "cannon").cost))
        self.buttons.append(Button((panel_x, 300, 216, 50), f"Slowing (${Tower(None, 'slowing').cost})",
                                   lambda: self.select_tower_to_place("slowing"),
                                   lambda: self.player_money >= Tower(None, "slowing").cost))
        self.upgrade_button = Button((panel_x, 500, 216, 50), "Upgrade", self.upgrade_selected_tower,
                                     lambda: self.selected_tower and self.selected_tower.level < 3 and self.player_money >= self.selected_tower.upgrade_cost)
        self.buttons.append(self.upgrade_button)
        self.start_wave_button = Button((panel_x, SCREEN_HEIGHT - 70, 216, 50), "Start Wave", self.start_next_wave)
        self.buttons.append(self.start_wave_button)

    def select_tower_to_place(self, tower_type):
        self.placing_tower_type, self.selected_tower = tower_type, None

    def upgrade_selected_tower(self):
        if self.selected_tower: self.selected_tower.upgrade()

    def start_next_wave(self):
        if not self.wave_spawn_list and self.current_wave < len(wave_definitions):
            if self.wave_cooldown < self.time_between_waves: self.player_money += int(
                ((self.time_between_waves - self.wave_cooldown) / self.time_between_waves) * (
                            50 + self.current_wave * 5))
            self.current_wave += 1
            wave_data = wave_definitions[self.current_wave - 1]
            self.wave_spawn_list = [(e_type, i * delay) for e_type, count, delay in wave_data for i in range(count)]
            self.wave_spawn_list.sort(key=lambda x: x[1]);
            self.wave_spawn_timer, self.wave_cooldown = 0, 0
            self.start_wave_button.text = "Wave in Progress"

    def handle_events(self, events):
        global game_running
        for event in events:
            if event.type == pygame.QUIT: game_running = False
            for button in self.buttons: button.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < SCREEN_WIDTH - GAME_PANEL_WIDTH:
                    if self.placing_tower_type:
                        self.place_tower(mouse_pos)
                    else:
                        self.selected_tower = next((t for t in self.towers if distance(mouse_pos, t.pos) < 20), None)

    def place_tower(self, pos):
        path_rects = [pygame.Rect(min(p1[0], p2[0]) - 25, min(p1[1], p2[1]) - 25, abs(p1[0] - p2[0]) + 50,
                                  abs(p1[1] - p2[1]) + 50) for i in range(len(enemy_path) - 1) for p1, p2 in
                      [(enemy_path[i], enemy_path[i + 1])]]
        if any(r.collidepoint(pos) for r in path_rects) or any(distance(pos, t.pos) < 40 for t in self.towers): return
        new_tower = Tower(pos, self.placing_tower_type)
        if self.player_money >= new_tower.cost: self.player_money -= new_tower.cost; self.towers.append(
            new_tower); self.placing_tower_type = None

    # --- DEBUGGED: Added logic to transition to GAME_OVER on a win ---
    def update(self):
        global game_state
        if self.player_health <= 0:
            game_state = "GAME_OVER"; return
        elif not self.wave_spawn_list and not self.enemies and self.current_wave >= len(wave_definitions):
            game_state = "GAME_OVER"; return

        for t in self.towers: t.update(self.enemies, self.projectiles, self.effects)
        for p in self.projectiles: p.update(self.enemies, self.effects)
        for e in self.effects: e.update()
        for e in self.enemies: e.update()
        self.enemies[:] = [e for e in self.enemies if e.is_alive]
        self.projectiles[:] = [p for p in self.projectiles if p.is_active]
        self.effects[:] = [e for e in self.effects if e.is_active]
        if self.wave_spawn_list:
            self.wave_spawn_timer += 1
            if self.wave_spawn_list and self.wave_spawn_list[0][1] < self.wave_spawn_timer:
                e_type, _ = self.wave_spawn_list.pop(0);
                self.enemies.append(Enemy(e_type, enemy_path[0]))
        elif not self.enemies:
            if self.wave_cooldown < self.time_between_waves: self.wave_cooldown += 1
            if self.wave_cooldown >= self.time_between_waves and self.current_wave < len(wave_definitions):
                self.start_wave_button.text = f"Start Wave {self.current_wave + 1}"
            elif self.current_wave >= len(wave_definitions):
                self.start_wave_button.text = "YOU WIN!"

    def draw(self, surface):
        self.draw_map(surface)
        for e in self.enemies: e.draw(surface)
        for t in self.towers: t.draw(surface)
        for p in self.projectiles: p.draw(surface)
        for e in self.effects: e.draw(surface)
        if self.placing_tower_type: self.draw_placement_preview(surface)
        self.draw_ui(surface)

    def draw_map(self, surface):
        for y in range(SCREEN_HEIGHT):
            r = y / SCREEN_HEIGHT;
            color = (int(COLOR_GRASS_TOP[0] * (1 - r) + COLOR_GRASS_BOTTOM[0] * r),
                     int(COLOR_GRASS_TOP[1] * (1 - r) + COLOR_GRASS_BOTTOM[1] * r),
                     int(COLOR_GRASS_TOP[2] * (1 - r) + COLOR_GRASS_BOTTOM[2] * r))
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH - GAME_PANEL_WIDTH, y))
        for i in range(len(enemy_path) - 1): pygame.draw.line(surface, COLOR_PATH, enemy_path[i], enemy_path[i + 1], 50)
        for p in enemy_path: pygame.draw.circle(surface, COLOR_PATH, p, 25)

    def draw_placement_preview(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > SCREEN_WIDTH - GAME_PANEL_WIDTH: return
        temp_tower = Tower(mouse_pos, self.placing_tower_type)
        rs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
        pygame.draw.circle(rs, (*COLOR_RANGE_CIRCLE[:3], 100), mouse_pos, temp_tower.range);
        surface.blit(rs, (0, 0))
        bs = pygame.Surface((40, 40), pygame.SRCALPHA);
        bs.fill((*temp_tower.base_color, 128));
        surface.blit(bs, (mouse_pos[0] - 20, mouse_pos[1] - 20))

    def draw_ui(self, surface):
        pr = (SCREEN_WIDTH - GAME_PANEL_WIDTH, 0, GAME_PANEL_WIDTH, SCREEN_HEIGHT);
        pygame.draw.rect(surface, COLOR_PANEL, pr)
        surface.blit(FONT_UI.render(f"Health: {self.player_health}", True, COLOR_TEXT), (pr[0] + 20, 20))
        surface.blit(FONT_UI.render(f"Money: ${self.player_money}", True, COLOR_TEXT), (pr[0] + 20, 50))
        surface.blit(FONT_UI.render(f"Wave: {self.current_wave}/{len(wave_definitions)}", True, COLOR_TEXT),
                     (pr[0] + 20, 80))
        surface.blit(FONT_TITLE.render("Build Towers", True, COLOR_TEXT), (pr[0] + 20, 130))
        for b in self.buttons: b.draw(surface)
        if self.selected_tower:
            st = self.selected_tower
            surface.blit(FONT_TITLE.render(f"Lvl {st.level} {st.type.capitalize()}", True, COLOR_TEXT),
                         (pr[0] + 20, 380))
            surface.blit(FONT_UI.render(f"Damage: {st.damage}", True, COLOR_TEXT), (pr[0] + 20, 420))
            surface.blit(FONT_UI.render(f"Range: {st.range}", True, COLOR_TEXT), (pr[0] + 20, 445))
            if st.type != "slowing": surface.blit(
                FONT_UI.render(f"Speed: {round(60 / st.cooldown, 1)}/s", True, COLOR_TEXT), (pr[0] + 20, 470))
            self.upgrade_button.text = f"Upgrade (${st.upgrade_cost})" if st.level < 3 else "Max Level"
        else:
            self.upgrade_button.text = "Upgrade"
        if not self.wave_spawn_list and not self.enemies and self.current_wave < len(wave_definitions):
            bonus = int(((self.time_between_waves - self.wave_cooldown) / self.time_between_waves) * (
                        50 + self.current_wave * 5))
            if bonus > 0: surface.blit(FONT_UI.render(f"Rush Bonus: ${bonus}", True, (255, 215, 0)),
                                       (pr[0] + 20, SCREEN_HEIGHT - 110))


# --- Research Menu Class ---
class ResearchMenu:
    def __init__(self):
        self.buttons = []
        self.setup_menu()

    def get_upgrade_cost(self, name):
        base_costs = {"starting_money": 20, "starting_health": 30, "gatling_damage": 50, "cannon_cost": 40}
        level = player_upgrades["upgrades"][name]
        return int(base_costs[name] * (1.6 ** level))

    def upgrade_stat(self, name):
        cost = self.get_upgrade_cost(name)
        if player_upgrades["research_points"] >= cost:
            player_upgrades["research_points"] -= cost;
            player_upgrades["upgrades"][name] += 1;
            save_upgrades()

    def setup_menu(self):
        self.buttons = [
            Button((SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT - 100, 300, 60), "Start New Game", self.start_game)]
        self.buttons.append(Button((300, 250, 150, 50), "Upgrade", lambda: self.upgrade_stat("starting_money"),
                                   lambda: player_upgrades["research_points"] >= self.get_upgrade_cost(
                                       "starting_money")))
        self.buttons.append(Button((300, 350, 150, 50), "Upgrade", lambda: self.upgrade_stat("starting_health"),
                                   lambda: player_upgrades["research_points"] >= self.get_upgrade_cost(
                                       "starting_health")))
        self.buttons.append(Button((800, 250, 150, 50), "Upgrade", lambda: self.upgrade_stat("gatling_damage"),
                                   lambda: player_upgrades["research_points"] >= self.get_upgrade_cost(
                                       "gatling_damage")))
        self.buttons.append(Button((800, 350, 150, 50), "Upgrade", lambda: self.upgrade_stat("cannon_cost"),
                                   lambda: player_upgrades["research_points"] >= self.get_upgrade_cost("cannon_cost")))

    def start_game(self):
        global game, game_state
        game, game_state = Game(), "IN_GAME"

    def handle_events(self, events):
        global game_running
        for event in events:
            if event.type == pygame.QUIT: game_running = False
            for button in self.buttons: button.handle_event(event)

    def draw(self, surface):
        surface.fill((20, 30, 40))
        title_surf = FONT_TITLE.render("Research & Development", True, COLOR_TEXT);
        surface.blit(title_surf, (SCREEN_WIDTH / 2 - title_surf.get_width() / 2, 50))
        rp_surf = FONT_UI.render(f"Research Points: {player_upgrades['research_points']} RP", True, (255, 215, 0));
        surface.blit(rp_surf, (SCREEN_WIDTH / 2 - rp_surf.get_width() / 2, 120))
        self.draw_upgrade_info(surface, "starting_money", "Bonus Starting Money",
                               f"+${player_upgrades['upgrades']['starting_money'] * 50}", 100, 250)
        self.draw_upgrade_info(surface, "starting_health", "Bonus Starting Health",
                               f"+{player_upgrades['upgrades']['starting_health']} HP", 100, 350)
        self.draw_upgrade_info(surface, "gatling_damage", "Gatling Damage",
                               f"+{player_upgrades['upgrades']['gatling_damage'] * 5}%", 600, 250)
        self.draw_upgrade_info(surface, "cannon_cost", "Cannon Cost Reduction",
                               f"-{player_upgrades['upgrades']['cannon_cost'] * 3}%", 600, 350)
        for button in self.buttons: button.draw(surface)

    def draw_upgrade_info(self, surface, name, title, effect_text, x, y):
        level, cost = player_upgrades['upgrades'][name], self.get_upgrade_cost(name)
        surface.blit(FONT_UI.render(f"{title} (Lvl {level})", True, COLOR_TEXT), (x, y - 40))
        surface.blit(FONT_UI.render(f"Current: {effect_text}", True, (150, 255, 150)), (x, y))
        surface.blit(FONT_UI.render(f"Cost: {cost} RP", True, (255, 215, 0)), (x, y + 25))


# --- Main Game Loop ---
if __name__ == "__main__":
    clock = pygame.time.Clock()
    load_upgrades()
    research_menu = ResearchMenu()
    game_running = True
    game_over_button = Button((SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 + 80, 300, 50), "Return to Menu", lambda: None)
    final_wave, earned_rp = 0, 0

    while game_running:
        events = pygame.event.get()

        if game_state == "MAIN_MENU":
            research_menu.handle_events(events)
            research_menu.draw(screen)

        elif game_state == "IN_GAME":
            if game: game.handle_events(events); game.update(); game.draw(screen)

        elif game_state == "GAME_OVER":
            if game:
                final_wave = game.current_wave
                earned_rp = final_wave * 10 if final_wave >= len(wave_definitions) else (final_wave - 1) * 10
                earned_rp = max(0, earned_rp)  # Ensure RP is not negative
                player_upgrades["research_points"] += earned_rp
                save_upgrades()
                game = None

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 180));
            screen.blit(overlay, (0, 0))
            go_text = FONT_GAME_OVER.render("GAME OVER", True, (255, 0, 0));
            screen.blit(go_text, go_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80)))
            wave_text = FONT_TITLE.render(f"You reached wave {final_wave}", True, COLOR_TEXT);
            screen.blit(wave_text, wave_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
            rp_text = FONT_UI.render(f"You earned {earned_rp} Research Points!", True, (255, 215, 0));
            screen.blit(rp_text, rp_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)))

            for event in events:
                if event.type == pygame.QUIT: game_running = False
                if game_over_button.handle_event(event): game_state = "MAIN_MENU"
            game_over_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()