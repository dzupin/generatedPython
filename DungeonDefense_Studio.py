import pygame
import math

# --- Configuration ---
# Colors
COLORS = {
    "background": (20, 20, 20),
    "path": (60, 60, 60),
    "wall": (40, 40, 40),
    "trap_slot": (80, 80, 80),
    "trap_spike": (180, 0, 0),
    "trap_magic": (0, 100, 200),
    "enemy_goblin": (0, 150, 0),
    "enemy_orc": (150, 75, 0),
    "text": (255, 255, 255),
    "ui_panel": (30, 30, 30),
    "ui_border": (100, 100, 100),
    "selection_highlight": (255, 255, 0),
    "projectile": (255, 255, 255),
    "health_bar_bg": (50, 50, 50),
    "health_bar_fill": (0, 200, 0),
}

# Game dimensions
GRID_SIZE = 20  # Number of cells in width/height (e.g., 20x20 grid)
CELL_SIZE = 40  # Pixels per cell
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + 100 # Add space for UI panel

# Trap/Enemy properties (example, will be expanded)
TRAP_TYPES = {
    "spike": {"cost": 50, "damage": 10, "range": 0, "cooldown": 60, "color": COLORS["trap_spike"]},
    "arrow": {"cost": 75, "damage": 15, "range": 3 * CELL_SIZE, "cooldown": 45, "color": COLORS["trap_spike"]}, # Placeholder, imagine a turret
    "magic": {"cost": 100, "damage": 20, "range": 2 * CELL_SIZE, "cooldown": 90, "color": COLORS["trap_magic"]}
}
ENEMY_TYPES = {
    "goblin": {"health": 50, "speed": 1, "reward": 10, "color": COLORS["enemy_goblin"], "size": CELL_SIZE // 3},
    "orc": {"health": 150, "speed": 0.7, "reward": 25, "color": COLORS["enemy_orc"], "size": CELL_SIZE // 2}
}

# Game State
GAME_STATE = {
    "placing_trap": None, # Stores the type of trap being placed
    "wave_active": False,
    "money": 5200,
    "score": 0,
    "wave_number": 0,
    "lives": 10,
    "start_wave_requested": False # NEW: Flag to request wave start
}

# --- Game Utility Functions ---
def world_to_grid(pos):
    """Converts pixel coordinates to grid coordinates."""
    return int(pos[0] // CELL_SIZE), int(pos[1] // CELL_SIZE)

def grid_to_world(grid_pos):
    """Converts grid coordinates to the center of a cell in pixel coordinates."""
    return grid_pos[0] * CELL_SIZE + CELL_SIZE // 2, grid_pos[1] * CELL_SIZE + CELL_SIZE // 2

# --- Game Classes ---

class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def draw(self, screen):
        raise NotImplementedError

    def update(self, dt):
        pass

class PathNode(GameObject):
    """Represents a segment of the enemy path."""
    def __init__(self, x, y, node_type="path"):
        super().__init__(x, y)
        self.node_type = node_type # "path", "start", "end"

    def draw(self, screen):
        # Path segments are drawn by the map
        pass

class Map:
    def __init__(self, grid):
        self.grid = grid # 2D list representing the dungeon layout
        self.path_nodes = []
        self.trap_slots = []
        self.start_node = None
        self.end_node = None
        self._parse_grid()

    def _parse_grid(self):
        """Parses the grid to identify path nodes, trap slots, start, and end."""
        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                cell_type = self.grid[r][c]
                world_x, world_y = c * CELL_SIZE, r * CELL_SIZE
                if cell_type == 'P': # Path
                    self.path_nodes.append(PathNode(world_x, world_y, "path"))
                elif cell_type == 'S': # Start
                    self.start_node = PathNode(world_x, world_y, "start")
                    self.path_nodes.insert(0, self.start_node) # Ensure start is first
                elif cell_type == 'E': # End
                    self.end_node = PathNode(world_x, world_y, "end")
                    self.path_nodes.append(self.end_node) # Ensure end is last
                elif cell_type == 'T': # Trap Slot
                    self.trap_slots.append((c, r)) # Store grid coordinates

        # Simple pathfinding (assuming linear path for now)
        # In a real game, you'd use A* or similar
        self.enemy_path = []
        if self.start_node and self.end_node:
            # For simplicity, assume path nodes are already ordered correctly in self.path_nodes
            # or implement a basic 'follow the next path node' logic here.
            # For now, let's just use the parsed order.
            self.enemy_path = [grid_to_world(world_to_grid((node.x, node.y))) for node in self.path_nodes]


    def draw(self, screen):
        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                cell_type = self.grid[r][c]
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if cell_type == '#': # Wall
                    pygame.draw.rect(screen, COLORS["wall"], rect)
                    # Add simple "stone block" texture (rectangles for shading)
                    pygame.draw.rect(screen, (50, 50, 50), rect, 2) # Border
                    pygame.draw.line(screen, (30, 30, 30), rect.topleft, rect.bottomright, 1)
                    pygame.draw.line(screen, (30, 30, 30), rect.topright, rect.bottomleft, 1)

                elif cell_type in ['P', 'S', 'E']: # Path
                    pygame.draw.rect(screen, COLORS["path"], rect)
                    # Add subtle path details
                    pygame.draw.rect(screen, (70, 70, 70), rect, 1)
                elif cell_type == 'T': # Trap Slot
                    pygame.draw.rect(screen, COLORS["trap_slot"], rect)
                    pygame.draw.rect(screen, COLORS["ui_border"], rect, 2) # Border for slots

class Trap(GameObject):
    def __init__(self, grid_x, grid_y, trap_type):
        world_x, world_y = grid_x * CELL_SIZE, grid_y * CELL_SIZE
        super().__init__(world_x, world_y)
        self.grid_pos = (grid_x, grid_y)
        self.type = trap_type
        self.properties = TRAP_TYPES[trap_type]
        self.damage = self.properties["damage"]
        self.range = self.properties["range"]
        self.cooldown_max = self.properties["cooldown"]
        self.cooldown_current = 0
        self.color = self.properties["color"]
        self.is_active = False # For animation or effect

    def draw(self, screen):
        center_x, center_y = self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2

        if self.type == "spike":
            # Draw spikes
            spike_height = CELL_SIZE // 3
            spike_width = CELL_SIZE // 4
            pygame.draw.polygon(screen, self.color, [
                (center_x - spike_width, center_y + spike_height),
                (center_x, center_y - spike_height),
                (center_x + spike_width, center_y + spike_height)
            ])
            pygame.draw.polygon(screen, self.color, [
                (self.x + CELL_SIZE // 4, self.y + CELL_SIZE * 3 // 4),
                (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 4),
                (self.x + CELL_SIZE * 3 // 4, self.y + CELL_SIZE * 3 // 4)
            ])
            # Base of the trap
            pygame.draw.rect(screen, (80, 0, 0), (self.x + CELL_SIZE // 8, self.y + CELL_SIZE * 3 // 4, CELL_SIZE * 3 // 4, CELL_SIZE // 8))

        elif self.type == "magic":
            # Draw a glowing rune/glyph
            pygame.draw.circle(screen, self.color, (center_x, center_y), CELL_SIZE // 3)
            pygame.draw.circle(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2), (center_x, center_y), CELL_SIZE // 3, 2)
            # Inner star/glyph pattern
            points = []
            for i in range(5):
                angle = math.pi * 2 * i / 5 - math.pi / 2 # Rotate to make one point up
                x_outer = center_x + CELL_SIZE // 3 * math.cos(angle)
                y_outer = center_y + CELL_SIZE // 3 * math.sin(angle)
                points.append((x_outer, y_outer))
                angle += math.pi / 5 # For inner point
                x_inner = center_x + CELL_SIZE // 6 * math.cos(angle)
                y_inner = center_y + CELL_SIZE // 6 * math.sin(angle)
                points.append((x_inner, y_inner))
            pygame.draw.polygon(screen, (255, 255, 255), points, 1)


        # Draw range indicator if selected or active
        if self.is_active: # Or if currently hovered/selected
             pygame.draw.circle(screen, (255, 255, 255, 50), (center_x, center_y), self.range, 1) # Transparent circle

    def update(self, dt, enemies):
        if self.cooldown_current > 0:
            self.cooldown_current -= dt
            self.is_active = False
        else:
            self.cooldown_current = 0
            # Check for enemies in range and attack
            if self.range > 0: # Ranged traps
                for enemy in enemies:
                    if self.distance_to(enemy) <= self.range:
                        # Simple attack logic, will be expanded with projectiles
                        enemy.take_damage(self.damage)
                        self.cooldown_current = self.cooldown_max
                        self.is_active = True
                        break # Only attack one enemy per cooldown
            else: # Melee/AoE traps (like spikes)
                for enemy in enemies:
                    if self.rect.colliderect(enemy.rect): # Enemy is on top of the trap
                        enemy.take_damage(self.damage)
                        self.cooldown_current = self.cooldown_max
                        self.is_active = True
                        break # Only activate for one enemy passing over (for now)

    def distance_to(self, other):
        """Calculates distance to another game object."""
        center_self = self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2
        center_other = other.x + other.size // 2, other.y + other.size // 2
        return math.hypot(center_self[0] - center_other[0], center_self[1] - center_other[1])


class Enemy(GameObject):
    def __init__(self, enemy_type, path, start_node_pos):
        # Start at the actual pixel coordinates of the start node, not just 0,0
        super().__init__(start_node_pos[0], start_node_pos[1])
        self.type = enemy_type
        self.properties = ENEMY_TYPES[enemy_type]
        self.health = self.properties["health"]
        self.max_health = self.health
        self.speed = self.properties["speed"]
        self.reward = self.properties["reward"]
        self.color = self.properties["color"]
        self.size = self.properties["size"] # Diameter for circles, side for squares

        self.path = path
        self.path_index = 0
        if self.path:
            self.target_pos = self.path[self.path_index]
        else:
            self.target_pos = (self.x, self.y) # No path, stay put

        self.alive = True
        self.reached_end = False

    def draw(self, screen):
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2

        if self.type == "goblin":
            pygame.draw.circle(screen, self.color, (center_x, center_y), self.size // 2)
            pygame.draw.circle(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2), (center_x, center_y), self.size // 2, 1) # Outline
            # Simple eyes
            pygame.draw.circle(screen, (255, 255, 255), (center_x - self.size // 6, center_y - self.size // 8), self.size // 8)
            pygame.draw.circle(screen, (255, 255, 255), (center_x + self.size // 6, center_y - self.size // 8), self.size // 8)
            pygame.draw.circle(screen, (0, 0, 0), (center_x - self.size // 6, center_y - self.size // 8), self.size // 16)
            pygame.draw.circle(screen, (0, 0, 0), (center_x + self.size // 6, center_y - self.size // 8), self.size // 16)

        elif self.type == "orc":
            # Draw a square with some details
            orc_rect = pygame.Rect(self.x, self.y, self.size, self.size)
            pygame.draw.rect(screen, self.color, orc_rect)
            pygame.draw.rect(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2), orc_rect, 2) # Outline
            # Tusks (simple triangles)
            pygame.draw.polygon(screen, (255, 255, 200), [
                (self.x + self.size // 4, self.y + self.size * 3 // 4),
                (self.x + self.size // 4 + self.size // 8, self.y + self.size),
                (self.x + self.size // 4 - self.size // 8, self.y + self.size)
            ])
            pygame.draw.polygon(screen, (255, 255, 200), [
                (self.x + self.size * 3 // 4, self.y + self.size * 3 // 4),
                (self.x + self.size * 3 // 4 + self.size // 8, self.y + self.size),
                (self.x + self.size * 3 // 4 - self.size // 8, self.y + self.size)
            ])


        # Health Bar
        health_bar_width = self.size
        health_bar_height = 5
        health_percent = self.health / self.max_health
        health_bar_x = self.x
        health_bar_y = self.y - health_bar_height - 2 # Above the enemy

        pygame.draw.rect(screen, COLORS["health_bar_bg"], (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, COLORS["health_bar_fill"], (health_bar_x, health_bar_y, health_bar_width * health_percent, health_bar_height))

        # Update rect for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)


    def update(self, dt):
        if not self.alive:
            return

        if self.path_index < len(self.path):
            self.target_pos = self.path[self.path_index]
            target_center_x, target_center_y = self.target_pos

            # Calculate vector to target
            dx = target_center_x - (self.x + self.size // 2)
            dy = target_center_y - (self.y + self.size // 2)
            distance = math.hypot(dx, dy)

            if distance < self.speed * dt: # Reached current target node
                self.x = target_center_x - self.size // 2
                self.y = target_center_y - self.size // 2
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.reached_end = True
                    self.alive = False # Enemy reached the end, "escaped"
            else:
                # Move towards target
                direction_x = dx / distance
                direction_y = dy / distance
                self.x += direction_x * self.speed * dt
                self.y += direction_y * self.speed * dt
        else:
            self.reached_end = True
            self.alive = False

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False

class Projectile(GameObject):
    def __init__(self, start_pos, target_enemy, damage, color):
        super().__init__(start_pos[0], start_pos[1])
        self.target_enemy = target_enemy
        self.damage = damage
        self.color = color
        self.speed = 10 # Pixels per frame
        self.size = 5
        self.alive = True

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def update(self, dt):
        if not self.alive:
            return

        if self.target_enemy.alive:
            target_x, target_y = self.target_enemy.x + self.target_enemy.size // 2, self.target_enemy.y + self.target_enemy.size // 2
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)

            if distance < self.speed * dt:
                self.x = target_x
                self.y = target_y
                self.target_enemy.take_damage(self.damage)
                self.alive = False
            else:
                direction_x = dx / distance
                direction_y = dy / distance
                self.x += direction_x * self.speed * dt
                self.y += direction_y * self.speed * dt
        else:
            self.alive = False # Target died before projectile reached it

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.panel_height = 100
        self.panel_rect = pygame.Rect(0, screen_height - self.panel_height, screen_width, self.panel_height)
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)

        # Add Start Wave Button
        self.start_wave_button = {
            "rect": pygame.Rect(self.screen_width // 2 - 70, self.panel_rect.top + 20, 170, 60),
            "text": "Start Wave (SPACE)"
        }

        # Trap buttons (example positions, will need dynamic placement)
        self.trap_buttons = {}
        button_width = 80
        button_height = 60
        button_padding = 10
        start_x = 20




        for i, (trap_type, props) in enumerate(TRAP_TYPES.items()):
            btn_x = start_x + (button_width + button_padding) * i
            btn_y = self.panel_rect.top + button_padding
            btn_rect = pygame.Rect(btn_x, btn_y, button_width, button_height)
            self.trap_buttons[trap_type] = {"rect": btn_rect, "cost": props["cost"]}


    def draw(self, screen, game_state):
        # Draw UI panel background
        pygame.draw.rect(screen, COLORS["ui_panel"], self.panel_rect)
        pygame.draw.rect(screen, COLORS["ui_border"], self.panel_rect, 2)

        # Game Stats
        money_text = self.font.render(f"Money: ${game_state['money']}", True, COLORS["text"])
        score_text = self.font.render(f"Score: {game_state['score']}", True, COLORS["text"])
        wave_text = self.font.render(f"Wave: {game_state['wave_number']}", True, COLORS["text"])
        lives_text = self.font.render(f"Lives: {game_state['lives']}", True, COLORS["text"])

        screen.blit(money_text, (self.screen_width - money_text.get_width() - 10, self.panel_rect.top + 10))
        screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, self.panel_rect.top + 30))
        screen.blit(wave_text, (self.screen_width - wave_text.get_width() - 10, self.panel_rect.top + 50))
        screen.blit(lives_text, (self.screen_width - lives_text.get_width() - 10, self.panel_rect.top + 70))

        # Draw Start Wave Button
        start_btn_rect = self.start_wave_button["rect"]
        start_btn_text = self.start_wave_button["text"]

        # If wave is active, make button inactive/greyed out
        btn_color = COLORS["ui_border"] if not game_state["wave_active"] else (80, 80, 80)
        text_color = COLORS["text"] if not game_state["wave_active"] else (150, 150, 150)

        pygame.draw.rect(screen, btn_color, start_btn_rect, 2)
        pygame.draw.rect(screen, (50, 50, 50), start_btn_rect)

        start_text_surface = self.font.render(start_btn_text, True, text_color)
        screen.blit(start_text_surface, (start_btn_rect.centerx - start_text_surface.get_width() // 2,
                                         start_btn_rect.centery - start_text_surface.get_height() // 2))

        # Trap Placement Buttons
        for trap_type, data in self.trap_buttons.items():
            rect = data["rect"]
            color = TRAP_TYPES[trap_type]["color"]

            # Highlight if selected for placement
            if game_state["placing_trap"] == trap_type:
                pygame.draw.rect(screen, COLORS["selection_highlight"], rect, 3) # Thicker border
            else:
                pygame.draw.rect(screen, COLORS["ui_border"], rect, 1)

            pygame.draw.rect(screen, (50, 50, 50), rect) # Button background

            # Draw a mini-representation of the trap
            if trap_type == "spike":
                pygame.draw.polygon(screen, color, [
                    (rect.centerx - rect.width // 6, rect.centery + rect.height // 6),
                    (rect.centerx, rect.centery - rect.height // 6),
                    (rect.centerx + rect.width // 6, rect.centery + rect.height // 6)
                ])
            elif trap_type == "magic":
                pygame.draw.circle(screen, color, (rect.centerx, rect.centery), rect.width // 4)
                pygame.draw.circle(screen, (255, 255, 255), (rect.centerx, rect.centery), rect.width // 8)

            cost_text = self.font.render(f"${data['cost']}", True, COLORS["text"])
            screen.blit(cost_text, (rect.centerx - cost_text.get_width() // 2, rect.bottom - cost_text.get_height() - 5))
            type_text = self.font.render(trap_type.capitalize(), True, COLORS["text"])
            screen.blit(type_text, (rect.centerx - type_text.get_width() // 2, rect.top + 5))


    def handle_click(self, mouse_pos, game_state):
        if self.panel_rect.collidepoint(mouse_pos):
            for trap_type, data in self.trap_buttons.items():
                if data["rect"].collidepoint(mouse_pos):
                    if game_state["money"] >= data["cost"]:
                        game_state["placing_trap"] = trap_type
                    else:
                        print("Not enough money!")  # Or show an in-game message
                    return True

            # Handle Start Wave button click
            if self.start_wave_button["rect"].collidepoint(mouse_pos):
                if not game_state["wave_active"]:
                    game_state["start_wave_requested"] = True # Signal to Game to start wave
                    return True  # Click handled
            return False  # Click was in UI panel but not on an interactive element
        return False  # Click was outside UI panel



# --- Game Logic ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Defense")
        self.clock = pygame.time.Clock()
        self.running = True

        # Example Grid (can be loaded from a file later)
        # #: Wall, P: Path, S: Start, E: End, T: Trap Slot
        self.dungeon_grid = [
            list("####################"),
            list("##S##############T##"),
            list("##P#################"),
            list("##P####T###########P"),
            list("##P#############T##P"),
            list("##P#####P##########P"),
            list("########P###T######P"),
            list("########P##########P"),
            list("########P####T#####P"),
            list("######T#P##########P"),
            list("########P##########P"),
            list("########P##########P"),
            list("########P##########P"),
            list("########P##########P"),
            list("########P##########P"),
            list("########P####T#####P"),
            list("########P##########P"),
            list("########P##########P"),
            list("####T###E##########P"),
            list("####################")
        ]
        self.map = Map(self.dungeon_grid)
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.traps = []
        self.enemies = []
        self.projectiles = []
        self.placed_trap_slots = set() # Store (grid_x, grid_y) of occupied slots

        # Wave Management
        self.wave_data = {
            1: {"enemies": [("goblin", 5)], "spawn_delay": 60}, # 5 goblins, 60 frames between each
            2: {"enemies": [("goblin", 10), ("orc", 2)], "spawn_delay": 50},
            # Add more waves for scalability
        }
        self.current_wave_enemies_to_spawn = []
        self.spawn_timer = 0
        self.spawn_delay = 0

    def start_wave(self):
        GAME_STATE["wave_number"] += 1
        if GAME_STATE["wave_number"] in self.wave_data:
            wave_info = self.wave_data[GAME_STATE["wave_number"]]
            self.current_wave_enemies_to_spawn = []
            for enemy_type, count in wave_info["enemies"]:
                for _ in range(count):
                    self.current_wave_enemies_to_spawn.append(enemy_type)
            self.spawn_delay = wave_info["spawn_delay"]
            self.spawn_timer = 0
            GAME_STATE["wave_active"] = True
            print(f"Starting Wave {GAME_STATE['wave_number']}!")
        else:
            print("No more waves defined! You win (for now!)")
            self.running = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    if self.ui.handle_click((mouse_x, mouse_y), GAME_STATE):
                        # UI handled the click
                        pass
                    if GAME_STATE["start_wave_requested"]:
                        self.start_wave()
                        GAME_STATE["start_wave_requested"] = False  # Reset the flag
                    elif GAME_STATE["placing_trap"] and mouse_y < SCREEN_HEIGHT - self.ui.panel_height:
                        # Attempt to place a trap
                        grid_x, grid_y = world_to_grid((mouse_x, mouse_y))
                        if (grid_x, grid_y) in self.map.trap_slots and (grid_x, grid_y) not in self.placed_trap_slots:
                            trap_type_to_place = GAME_STATE["placing_trap"]
                            trap_cost = TRAP_TYPES[trap_type_to_place]["cost"]
                            if GAME_STATE["money"] >= trap_cost:
                                self.traps.append(Trap(grid_x, grid_y, trap_type_to_place))
                                self.placed_trap_slots.add((grid_x, grid_y))
                                GAME_STATE["money"] -= trap_cost
                                GAME_STATE["placing_trap"] = None # Reset placement mode
                            else:
                                print("Not enough money for this trap!")
                        else:
                            print("Cannot place trap here (not a slot or occupied).")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not GAME_STATE["wave_active"] and not self.current_wave_enemies_to_spawn:
                        self.start_wave()

    def update(self, dt):
        # Enemy Spawning
        if GAME_STATE["wave_active"] and self.current_wave_enemies_to_spawn:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                enemy_type = self.current_wave_enemies_to_spawn.pop(0)
                start_pos_world = self.map.enemy_path[0] if self.map.enemy_path else (0,0)
                self.enemies.append(Enemy(enemy_type, self.map.enemy_path, start_pos_world))
                self.spawn_timer = 0
        elif GAME_STATE["wave_active"] and not self.current_wave_enemies_to_spawn and not self.enemies:
            # All enemies spawned and defeated
            GAME_STATE["wave_active"] = False
            print("Wave complete!")
            GAME_STATE["money"] += 100 # Bonus for completing wave

        # Update enemies
        for enemy in list(self.enemies): # Iterate over a copy to allow modification
            enemy.update(dt)
            if not enemy.alive:
                if enemy.reached_end:
                    GAME_STATE["lives"] -= 1
                    print(f"Enemy escaped! Lives left: {GAME_STATE['lives']}")
                else:
                    GAME_STATE["money"] += enemy.reward
                    GAME_STATE["score"] += enemy.reward
                self.enemies.remove(enemy)
        # Update traps
        for trap in self.traps:
            # For ranged traps, we'll implement projectile logic here for simplicity
            if trap.type == "arrow" or trap.type == "magic":  # Assuming these are ranged
                if trap.cooldown_current <= 0:
                    target = None
                    # Find closest enemy in range
                    closest_dist = float('inf')
                    for enemy in self.enemies:
                        dist = trap.distance_to(enemy)
                        if dist <= trap.range and dist < closest_dist:
                            closest_dist = dist
                            target = enemy
                    if target:
                        # Create a projectile
                        projectile_start_pos = (trap.x + CELL_SIZE // 2, trap.y + CELL_SIZE // 2)
                        self.projectiles.append(
                            Projectile(projectile_start_pos, target, trap.damage, COLORS["projectile"]))
                        trap.cooldown_current = trap.cooldown_max
                        trap.is_active = True  # Indicate it just fired
                else:
                    trap.cooldown_current -= dt
                    trap.is_active = False  # Reset active state after firing

            else:  # Melee traps (like spikes)
                trap.update(dt, self.enemies)  # Pass enemies for collision detection

        # Update projectiles
        for projectile in list(self.projectiles):
            projectile.update(dt)
            if not projectile.alive:
                self.projectiles.remove(projectile)

        # Check for Game Over
        if GAME_STATE["lives"] <= 0:
            print("Game Over!")
            self.running = False

    def draw(self):
        self.screen.fill(COLORS["background"])

        self.map.draw(self.screen)

        for trap in self.traps:
            trap.draw(self.screen)
            # If placing a trap, draw its ghost image and range
            if GAME_STATE["placing_trap"]:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = world_to_grid((mouse_x, mouse_y))
                temp_trap = Trap(grid_x, grid_y, GAME_STATE["placing_trap"])
                temp_trap.is_active = True  # To draw range

                # Draw translucent ghost
                s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                temp_trap.draw(s)
                s.set_alpha(100)  # Transparency
                self.screen.blit(s, (grid_x * CELL_SIZE, grid_y * CELL_SIZE))

                # Highlight potential placement slot
                if (grid_x, grid_y) in self.map.trap_slots and (grid_x, grid_y) not in self.placed_trap_slots:
                    pygame.draw.rect(self.screen, COLORS["selection_highlight"],
                                     (grid_x * CELL_SIZE, grid_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        self.ui.draw(self.screen, GAME_STATE)

        pygame.display.flip()

    def run(self):
        dt = 0
        while self.running:
            self.handle_input()
            self.update(dt)
            self.draw()

            dt = self.clock.tick(60) / 1000.0  # dt in seconds for smooth movement
            # We will use dt as frames for simplicity for now since cooldowns are in frames
            # For more accurate time-based movement, multiply speeds by dt
            # For this simple example, dt will be roughly 1 for 60fps if we divide by (1000/60)
            dt = 1  # Simplified for initial frame-based updates. For real game use actual dt.

        pygame.quit()


# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()