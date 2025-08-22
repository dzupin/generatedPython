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
COLOR_GRASS = (48, 116, 48)
COLOR_PATH = (188, 158, 114)
COLOR_PANEL = (50, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_HEALTH_GREEN = (0, 255, 0)
COLOR_HEALTH_RED = (255, 0, 0)
COLOR_RANGE_CIRCLE = (255, 255, 255, 50)  # Transparent white

# Game Fonts
FONT_UI = pygame.font.SysFont("Arial", 24)
FONT_TITLE = pygame.font.SysFont("Arial", 32, bold=True)
FONT_GAME_OVER = pygame.font.SysFont("Arial", 64, bold=True)

# Game Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Procedural Tower Defense")

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


# --- Classes ---

class Enemy:
    """ Base class for all enemies """

    def __init__(self, enemy_type, start_pos):
        self.pos = list(start_pos)
        self.type = enemy_type
        self.path_index = 0
        self.target_pos = enemy_path[0]
        self.is_alive = True
        self.effects = {}  # e.g., {"slow": {"timer": 120, "factor": 0.5}}

        # Enemy stats based on type
        if self.type == "grunt":
            self.max_health = 100
            self.speed = 1.5
            self.reward = 10
            self.color = (50, 150, 50)  # Green
            self.size = 20
        elif self.type == "runner":
            self.max_health = 60
            self.speed = 3.0
            self.reward = 15
            self.color = (200, 50, 50)  # Red
            self.size = 16
        elif self.type == "tank":
            self.max_health = 500
            self.speed = 0.8
            self.reward = 50
            self.color = (100, 50, 150)  # Purple
            self.size = 30

        self.health = self.max_health

    def update(self):
        if not self.is_alive:
            return

        # Handle effects
        current_speed = self.speed
        if "slow" in self.effects:
            effect = self.effects["slow"]
            current_speed *= effect["factor"]
            effect["timer"] -= 1
            if effect["timer"] <= 0:
                del self.effects["slow"]

        # Move towards the next waypoint
        dist = distance(self.pos, self.target_pos)
        if dist < current_speed:
            self.path_index += 1
            if self.path_index >= len(enemy_path):
                self.reach_end()
                return
            self.target_pos = enemy_path[self.path_index]

        direction_x = self.target_pos[0] - self.pos[0]
        direction_y = self.target_pos[1] - self.pos[1]

        # Normalize direction
        norm = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if norm > 0:
            direction_x /= norm
            direction_y /= norm

        self.pos[0] += direction_x * current_speed
        self.pos[1] += direction_y * current_speed

    def draw(self, surface):
        if not self.is_alive:
            return

        # Draw the enemy shape
        rect = pygame.Rect(self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)  # Black outline

        # Draw health bar
        health_bar_width = self.size
        health_bar_height = 5
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
    """ Base class for all towers """

    def __init__(self, pos, tower_type):
        self.pos = pos
        self.type = tower_type
        self.level = 1
        self.cooldown_timer = 0
        self.target = None

        self.set_stats()

    def set_stats(self):
        # Stats are defined by type and level
        if self.type == "gatling":
            self.base_color = (128, 128, 128)  # Grey
            self.barrel_color = (80, 80, 80)
            self.damage = [8, 15, 25][self.level - 1]
            self.range = [120, 140, 160][self.level - 1]
            self.cooldown = [20, 15, 10][self.level - 1]  # Faster fire rate
            self.cost = 100
            self.upgrade_cost = [150, 250, 0][self.level - 1]
        elif self.type == "cannon":
            self.base_color = (40, 40, 40)  # Dark Grey
            self.barrel_color = (20, 20, 20)
            self.damage = [40, 80, 150][self.level - 1]
            self.range = [180, 200, 220][self.level - 1]
            self.cooldown = [120, 110, 100][self.level - 1]
            self.splash_radius = [25, 30, 35][self.level - 1]
            self.cost = 250
            self.upgrade_cost = [300, 500, 0][self.level - 1]
        elif self.type == "slowing":
            self.base_color = (50, 100, 200)  # Blue
            self.barrel_color = (100, 150, 255)
            self.damage = 0
            self.range = [150, 170, 190][self.level - 1]
            self.cooldown = [10, 10, 10][self.level - 1]  # Constant pulse
            self.slow_factor = [0.6, 0.5, 0.4][self.level - 1]
            self.slow_duration = 60  # 1 second at 60 FPS
            self.cost = 150
            self.upgrade_cost = [100, 150, 0][self.level - 1]

    def upgrade(self):
        global player_money
        if self.level < 3 and player_money >= self.upgrade_cost:
            player_money -= self.upgrade_cost
            self.level += 1
            self.set_stats()

    def find_target(self, enemies):
        # If current target is invalid, find a new one
        if self.target and (not self.target.is_alive or distance(self.pos, self.target.pos) > self.range):
            self.target = None

        if not self.target:
            for enemy in enemies:
                if enemy.is_alive and distance(self.pos, enemy.pos) <= self.range:
                    self.target = enemy
                    break

    def update(self, enemies, projectiles):
        self.cooldown_timer = max(0, self.cooldown_timer - 1)
        self.find_target(enemies)

        if self.target and self.cooldown_timer == 0:
            self.cooldown_timer = self.cooldown
            self.fire(projectiles)

    def fire(self, projectiles):
        if self.type == "gatling":
            projectiles.append(Projectile(self.pos, self.target, self.damage, 5, (255, 255, 0)))
        elif self.type == "cannon":
            projectiles.append(
                Projectile(self.pos, self.target, self.damage, 3, (0, 0, 0), splash_radius=self.splash_radius))
        elif self.type == "slowing":
            # Slowing tower applies effect directly in a pulse, no projectile
            for enemy in game.enemies:
                if enemy.is_alive and distance(self.pos, enemy.pos) <= self.range:
                    enemy.apply_effect("slow", self.slow_duration, self.slow_factor)

    def draw(self, surface):
        # Draw range circle if selected
        if selected_tower is self:
            range_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, COLOR_RANGE_CIRCLE, self.pos, self.range)
            surface.blit(range_surface, (0, 0))

        # Draw tower base
        if self.type == "slowing":
            # Draw hexagon for slowing tower
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = math.pi / 180 * angle_deg
                points.append((self.pos[0] + 20 * math.cos(angle_rad), self.pos[1] + 20 * math.sin(angle_rad)))
            pygame.draw.polygon(surface, self.base_color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 3)
        else:
            pygame.draw.rect(surface, self.base_color, (self.pos[0] - 20, self.pos[1] - 20, 40, 40))
            pygame.draw.rect(surface, (0, 0, 0), (self.pos[0] - 20, self.pos[1] - 20, 40, 40), 3)

        # Draw barrel / top element
        barrel_length = 25
        if self.target:
            # Point towards target
            angle = math.atan2(self.target.pos[1] - self.pos[1], self.target.pos[0] - self.pos[0])
        else:
            angle = -math.pi / 2  # Point up

        end_x = self.pos[0] + barrel_length * math.cos(angle)
        end_y = self.pos[1] + barrel_length * math.sin(angle)

        if self.type == "gatling":
            pygame.draw.line(surface, self.barrel_color, self.pos, (end_x, end_y), 6)
        elif self.type == "cannon":
            pygame.draw.line(surface, self.barrel_color, self.pos, (end_x, end_y), 12)
        elif self.type == "slowing":
            # Pulsating effect for slowing tower
            pulse_size = 8 + (math.sin(pygame.time.get_ticks() / 200) + 1) * 3
            pygame.draw.circle(surface, self.barrel_color, self.pos, int(pulse_size))

        # Draw upgrade indicators (chevrons)
        for i in range(self.level - 1):
            points = [
                (self.pos[0] - 15 + i * 10, self.pos[1] + 18),
                (self.pos[0] - 10 + i * 10, self.pos[1] + 12),
                (self.pos[0] - 5 + i * 10, self.pos[1] + 18)
            ]
            pygame.draw.lines(surface, (255, 215, 0), False, points, 3)


class Projectile:
    def __init__(self, start_pos, target, damage, speed, color, splash_radius=0):
        self.pos = list(start_pos)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.splash_radius = splash_radius
        self.is_active = True

    def update(self, enemies):
        if not self.is_active or not self.target.is_alive:
            self.is_active = False
            return

        target_pos = self.target.pos
        dist = distance(self.pos, target_pos)

        if dist < self.speed:
            self.hit(enemies)
            return

        # Move towards target
        dir_x = target_pos[0] - self.pos[0]
        dir_y = target_pos[1] - self.pos[1]
        norm = math.sqrt(dir_x ** 2 + dir_y ** 2)
        if norm > 0:
            dir_x /= norm
            dir_y /= norm

        self.pos[0] += dir_x * self.speed
        self.pos[1] += dir_y * self.speed

    def hit(self, enemies):
        self.is_active = False
        self.target.take_damage(self.damage)

        if self.splash_radius > 0:
            for enemy in enemies:
                if enemy is not self.target and enemy.is_alive:
                    if distance(self.target.pos, enemy.pos) <= self.splash_radius:
                        enemy.take_damage(self.damage * 0.5)  # Splash deals 50% damage

    def draw(self, surface):
        if self.is_active:
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), 4)


class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

        text_surf = FONT_UI.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.callback()
                return True
        return False


class Game:
    """ Main game controller class """

    def __init__(self):
        self.towers = []
        self.enemies = []
        self.projectiles = []

        self.wave_spawn_list = []
        self.wave_spawn_timer = 0
        self.time_between_waves = 900  # 15 seconds
        self.wave_cooldown = self.time_between_waves

        self.setup_ui()

    def setup_ui(self):
        self.buttons = []
        panel_x = SCREEN_WIDTH - GAME_PANEL_WIDTH + 20

        # Tower placement buttons
        self.buttons.append(
            Button((panel_x, 180, 216, 50), "Gatling ($100)", lambda: self.select_tower_to_place("gatling")))
        self.buttons.append(
            Button((panel_x, 240, 216, 50), "Cannon ($250)", lambda: self.select_tower_to_place("cannon")))
        self.buttons.append(
            Button((panel_x, 300, 216, 50), "Slowing ($150)", lambda: self.select_tower_to_place("slowing")))

        # Upgrade button
        self.upgrade_button = Button((panel_x, 500, 216, 50), "Upgrade", self.upgrade_selected_tower)
        self.buttons.append(self.upgrade_button)

        # Start Wave button
        self.start_wave_button = Button((panel_x, SCREEN_HEIGHT - 70, 216, 50), "Start Wave", self.start_next_wave)
        self.buttons.append(self.start_wave_button)

    def select_tower_to_place(self, tower_type):
        global placing_tower_type, selected_tower
        cost = {"gatling": 100, "cannon": 250, "slowing": 150}[tower_type]
        if player_money >= cost:
            placing_tower_type = tower_type
            selected_tower = None

    def upgrade_selected_tower(self):
        if selected_tower:
            selected_tower.upgrade()

    def start_next_wave(self):
        global current_wave
        if not self.wave_spawn_list and current_wave < len(wave_definitions):
            current_wave += 1
            wave_data = wave_definitions[current_wave - 1]
            self.wave_spawn_list = []
            for enemy_type, count, delay in wave_data:
                for i in range(count):
                    self.wave_spawn_list.append((enemy_type, i * delay))
            # Sort by spawn time
            self.wave_spawn_list.sort(key=lambda x: x[1])
            self.wave_spawn_timer = 0
            self.wave_cooldown = 0
            self.start_wave_button.text = "Wave in Progress"

    def handle_events(self, events):
        global placing_tower_type, selected_tower
        for event in events:
            if event.type == pygame.QUIT:
                global game_running
                game_running = False

            # Button events
            for button in self.buttons:
                button.handle_event(event)

            # Mouse click for placing/selecting towers
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Check if clicking on the game area
                if mouse_pos[0] < SCREEN_WIDTH - GAME_PANEL_WIDTH:
                    if placing_tower_type:
                        self.place_tower(mouse_pos)
                    else:
                        # Select an existing tower
                        newly_selected = None
                        for tower in self.towers:
                            if distance(mouse_pos, tower.pos) < 20:
                                newly_selected = tower
                                break
                        selected_tower = newly_selected

    def place_tower(self, pos):
        global player_money, placing_tower_type

        # Check if placement is valid (not on path)
        path_rects = []
        for i in range(len(enemy_path) - 1):
            p1 = enemy_path[i]
            p2 = enemy_path[i + 1]
            path_rects.append(pygame.Rect(min(p1[0], p2[0]) - 25, min(p1[1], p2[1]) - 25, abs(p1[0] - p2[0]) + 50,
                                          abs(p1[1] - p2[1]) + 50))

        is_on_path = any(rect.collidepoint(pos) for rect in path_rects)
        is_overlapping = any(distance(pos, t.pos) < 40 for t in self.towers)  # Check for overlap

        if not is_on_path and not is_overlapping:
            new_tower = Tower(pos, placing_tower_type)
            if player_money >= new_tower.cost:
                player_money -= new_tower.cost
                self.towers.append(new_tower)
                placing_tower_type = None

    def update(self):
        if game_over:
            return

        # Update towers and projectiles
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

        for projectile in self.projectiles:
            projectile.update(self.enemies)

        # Update enemies
        for enemy in self.enemies:
            enemy.update()

        # Clean up dead/inactive objects
        self.enemies = [e for e in self.enemies if e.is_alive]
        self.projectiles = [p for p in self.projectiles if p.is_active]

        # Handle wave spawning
        if self.wave_spawn_list:
            self.wave_spawn_timer += 1
            if self.wave_spawn_list[0][1] < self.wave_spawn_timer:
                enemy_type, _ = self.wave_spawn_list.pop(0)
                self.enemies.append(Enemy(enemy_type, enemy_path[0]))
        elif not self.enemies:  # Wave is over
            if self.wave_cooldown < self.time_between_waves:
                self.wave_cooldown += 1
            if self.wave_cooldown >= self.time_between_waves and current_wave < len(wave_definitions):
                self.start_wave_button.text = f"Start Wave {current_wave + 1}"
            elif current_wave >= len(wave_definitions):
                self.start_wave_button.text = "YOU WIN!"

    def draw(self, surface):
        self.draw_map(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

        for tower in self.towers:
            tower.draw(surface)

        for projectile in self.projectiles:
            projectile.draw(surface)

        # Draw tower preview if placing
        if placing_tower_type:
            self.draw_placement_preview(surface)

        self.draw_ui(surface)

        if game_over:
            self.draw_game_over(surface)

    def draw_map(self, surface):
        surface.fill(COLOR_GRASS)
        # Draw path
        for i in range(len(enemy_path) - 1):
            pygame.draw.line(surface, COLOR_PATH, enemy_path[i], enemy_path[i + 1], 50)
        # Smooth path joints
        for point in enemy_path:
            pygame.draw.circle(surface, COLOR_PATH, point, 25)

    def draw_placement_preview(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > SCREEN_WIDTH - GAME_PANEL_WIDTH:
            return

        temp_tower = Tower(mouse_pos, placing_tower_type)

        # Draw transparent range circle
        range_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*COLOR_RANGE_CIRCLE[:3], 100), mouse_pos, temp_tower.range)
        surface.blit(range_surface, (0, 0))

        # Draw a semi-transparent tower base
        base_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        base_surf.fill((*temp_tower.base_color, 128))
        surface.blit(base_surf, (mouse_pos[0] - 20, mouse_pos[1] - 20))

    def draw_ui(self, surface):
        # Panel Background
        panel_rect = (SCREEN_WIDTH - GAME_PANEL_WIDTH, 0, GAME_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect)

        # Stats
        health_text = FONT_UI.render(f"Health: {player_health}", True, COLOR_TEXT)
        money_text = FONT_UI.render(f"Money: ${player_money}", True, COLOR_TEXT)
        wave_text = FONT_UI.render(f"Wave: {current_wave} / {len(wave_definitions)}", True, COLOR_TEXT)

        surface.blit(health_text, (panel_rect[0] + 20, 20))
        surface.blit(money_text, (panel_rect[0] + 20, 50))
        surface.blit(wave_text, (panel_rect[0] + 20, 80))

        # Tower placement title
        place_title = FONT_TITLE.render("Build Towers", True, COLOR_TEXT)
        surface.blit(place_title, (panel_rect[0] + 20, 130))

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

        # Selected Tower Info
        if selected_tower:
            info_title = FONT_TITLE.render(f"Level {selected_tower.level} {selected_tower.type.capitalize()}", True,
                                           COLOR_TEXT)
            surface.blit(info_title, (panel_rect[0] + 20, 380))

            damage_text = FONT_UI.render(f"Damage: {selected_tower.damage}", True, COLOR_TEXT)
            range_text = FONT_UI.render(f"Range: {selected_tower.range}", True, COLOR_TEXT)
            speed_text = FONT_UI.render(f"Speed: {round(60 / selected_tower.cooldown, 1)}/s", True, COLOR_TEXT)

            surface.blit(damage_text, (panel_rect[0] + 20, 420))
            surface.blit(range_text, (panel_rect[0] + 20, 445))
            surface.blit(speed_text, (panel_rect[0] + 20, 470))

            if selected_tower.level < 3:
                self.upgrade_button.text = f"Upgrade (${selected_tower.upgrade_cost})"
            else:
                self.upgrade_button.text = "Max Level"
        else:
            self.upgrade_button.text = "Upgrade"

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
        # Event Handling
        events = pygame.event.get()
        game.handle_events(events)

        # Game Logic
        game.update()

        # Check for game over condition
        if player_health <= 0:
            game_over = True

        # Drawing
        game.draw(screen)

        # Update Display
        pygame.display.flip()

        # Cap Frame Rate
        clock.tick(60)

    pygame.quit()