# Import necessary libraries
import pygame
import random
import math
from os import path # To potentially load assets later if needed

# PROMPT for Gemini 2.5 Pro Experimental 03-25 :  write asteroid game in python using pygame library. Make it visually appealing


# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Player properties
PLAYER_ACCELERATION = 0.3
PLAYER_FRICTION = -0.03 # Slight drag
PLAYER_TURN_SPEED = 5
PLAYER_GUN_COOLDOWN = 200 # milliseconds
PLAYER_INVULNERABILITY_TIME = 2000 # milliseconds after respawn
PLAYER_MAX_SPEED = 10
PLAYER_LIVES = 3

# Bullet properties
BULLET_SPEED = 10
BULLET_LIFESPAN = 500 # milliseconds
BULLET_RADIUS = 3

# Asteroid properties
ASTEROID_START_COUNT = 4
ASTEROID_SPEED_MIN = 1
ASTEROID_SPEED_MAX = 3
ASTEROID_SPAWN_EDGE_BUFFER = 100 # Don't spawn too close to center
ASTEROID_SIZES = {
    3: {'radius': 40, 'points': 12, 'score': 20}, # Large
    2: {'radius': 25, 'points': 10, 'score': 50}, # Medium
    1: {'radius': 15, 'points': 8,  'score': 100}  # Small
}

# --- Asset loading (Optional - we'll use drawing for now) ---
# asset_dir = path.join(path.dirname(__file__), 'assets')
# try:
#     player_img = pygame.image.load(path.join(asset_dir, 'playerShip.png')).convert()
#     # Add other images (asteroids, background)
# except pygame.error as e:
#     print(f"Warning: Could not load assets. Using drawing. Error: {e}")
#     # Set flags to use drawing instead

# --- Helper Functions ---
def draw_text(surface, text, size, x, y, color=WHITE, font_name=None):
    """Draws text on the screen."""
    if font_name is None:
        font_name = pygame.font.match_font('arial') # Or choose a nicer font if available
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def wrap_position(sprite, width, height):
    """Wraps sprite position around screen edges."""
    if sprite.rect.left > width:
        sprite.rect.right = 0
    if sprite.rect.right < 0:
        sprite.rect.left = width
    if sprite.rect.top > height:
        sprite.rect.bottom = 0
    if sprite.rect.bottom < 0:
        sprite.rect.top = height
    sprite.pos.x = sprite.rect.centerx
    sprite.pos.y = sprite.rect.centery

def generate_asteroid_shape(radius, num_points):
    """Generates points for an irregular asteroid polygon."""
    points = []
    angle_step = 2 * math.pi / num_points
    for i in range(num_points):
        angle = i * angle_step
        # Vary radius slightly for irregularity
        r = radius * random.uniform(0.75, 1.25)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        points.append((x, y))
    return points

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.radius = 15 # For collision detection
        # Use a Surface for drawing and rotation
        self.image_orig = pygame.Surface((self.radius * 2.5, self.radius * 2.5), pygame.SRCALPHA)
        # Draw the ship (triangle) - pointing right initially (0 degrees)
        ship_points = [(self.radius, 0), (-self.radius * 0.6, -self.radius * 0.8), (-self.radius * 0.6, self.radius * 0.8)]
        # Offset points to center them on the surface
        offset_x = self.radius * 1.25
        offset_y = self.radius * 1.25
        shifted_points = [(p[0] + offset_x, p[1] + offset_y) for p in ship_points]
        pygame.draw.polygon(self.image_orig, CYAN, shifted_points, 2) # Draw outline

        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0 # Degrees, 0 = right, 90 = down, etc.
        self.last_shot_time = pygame.time.get_ticks()
        self.lives = PLAYER_LIVES
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.invulnerable = False
        self.invulnerable_timer = pygame.time.get_ticks()

    def update(self):
        # Handle invulnerability after respawn
        now = pygame.time.get_ticks()
        if self.hidden and now - self.hide_timer > PLAYER_INVULNERABILITY_TIME:
            self.hidden = False
            self.invulnerable = True
            self.invulnerable_timer = now
            self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.pos = pygame.math.Vector2(self.rect.center)
            self.vel = pygame.math.Vector2(0, 0)
            self.angle = 0

        if self.invulnerable and now - self.invulnerable_timer > PLAYER_INVULNERABILITY_TIME:
            self.invulnerable = False

        if self.hidden:
            return # Don't process movement/input if hidden

        # Process input
        self.vel += pygame.math.Vector2(0, 0) # Re-initialize acceleration this frame
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.angle += PLAYER_TURN_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.angle -= PLAYER_TURN_SPEED
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            # Accelerate in the direction the ship is facing
            acceleration = pygame.math.Vector2(PLAYER_ACCELERATION, 0).rotate(-self.angle)
            self.vel += acceleration
            # Draw thrust flame (simple)
            self.draw_thrust(True)
        else:
            self.draw_thrust(False) # Ensure flame is removed/not drawn if not thrusting

        if keystate[pygame.K_SPACE]:
            self.shoot()

        # Apply friction
        self.vel += self.vel * PLAYER_FRICTION

        # Limit speed
        if self.vel.length() > PLAYER_MAX_SPEED:
            self.vel.scale_to_length(PLAYER_MAX_SPEED)

        # Update position based on velocity
        self.pos += self.vel
        self.rect.center = self.pos

        # Wrap around screen edges
        wrap_position(self, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Rotate image
        self.angle %= 360 # Keep angle between 0 and 359
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def draw_thrust(self, thrusting):
        # Re-draw the base ship without flame first if needed (or make flame separate sprite)
        # For simplicity, we redraw the ship each frame anyway during rotation
        if thrusting:
             # Calculate flame points relative to ship center, then rotate
            flame_length = self.radius * 0.8
            flame_width = self.radius * 0.5
            # Points relative to origin (0,0) when ship points right (angle 0)
            p1 = (-self.radius * 0.6, 0) # Back center of ship body
            p2 = (-self.radius * 0.6 - flame_length, -flame_width / 2)
            p3 = (-self.radius * 0.6 - flame_length, flame_width / 2)

            # Rotate points by the ship's angle
            rad_angle = math.radians(-self.angle) # Pygame rotation is clockwise, math is anti-clockwise
            cos_a = math.cos(rad_angle)
            sin_a = math.sin(rad_angle)

            def rotate_point(p):
                return (p[0] * cos_a - p[1] * sin_a, p[0] * sin_a + p[1] * cos_a)

            rp1 = rotate_point(p1)
            rp2 = rotate_point(p2)
            rp3 = rotate_point(p3)

            # Translate points to ship's current position on the main screen surface
            draw_points = [
                (self.rect.centerx + rp1[0], self.rect.centery + rp1[1]),
                (self.rect.centerx + rp2[0], self.rect.centery + rp2[1]),
                (self.rect.centerx + rp3[0], self.rect.centery + rp3[1])
            ]
            pygame.draw.polygon(self.game.screen, RED, draw_points) # Draw flame on main screen


    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > PLAYER_GUN_COOLDOWN:
            self.last_shot_time = now
            # Calculate bullet start position (tip of the ship)
            offset = pygame.math.Vector2(self.radius, 0).rotate(-self.angle)
            start_pos = self.pos + offset
            # Calculate bullet velocity vector
            direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
            bullet = Bullet(start_pos.x, start_pos.y, direction, self)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)

    def hide(self):
        """Temporarily hide the player after being hit."""
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (-200, -200) # Move off-screen
        self.lives -= 1

    def draw(self, surface):
        # Make player blink when invulnerable
        if self.invulnerable:
            if (pygame.time.get_ticks() // 200) % 2 == 0: # Blink every 200ms
                 surface.blit(self.image, self.rect)
        else:
             surface.blit(self.image, self.rect)


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size, pos=None, vel=None):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.properties = ASTEROID_SIZES[self.size]
        self.radius = self.properties['radius']
        self.score_value = self.properties['score']

        # Generate shape points relative to (0,0)
        self.shape_points = generate_asteroid_shape(self.radius, self.properties['points'])

        # Create image surface large enough for the asteroid
        self.image_orig = pygame.Surface((self.radius * 2.5, self.radius * 2.5), pygame.SRCALPHA)
        # Center the drawing on the surface
        center_offset = self.radius * 1.25
        draw_points = [(p[0] + center_offset, p[1] + center_offset) for p in self.shape_points]
        pygame.draw.polygon(self.image_orig, GRAY, draw_points, 2) # Draw outline

        self.image = self.image_orig.copy() # Start with non-rotated image
        self.rect = self.image.get_rect()

        # Position and Velocity
        if pos is None:
            # Spawn at edge
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                x = random.randrange(-ASTEROID_SPAWN_EDGE_BUFFER, 0)
                y = random.randrange(0, SCREEN_HEIGHT)
            elif side == 'right':
                x = random.randrange(SCREEN_WIDTH, SCREEN_WIDTH + ASTEROID_SPAWN_EDGE_BUFFER)
                y = random.randrange(0, SCREEN_HEIGHT)
            elif side == 'top':
                x = random.randrange(0, SCREEN_WIDTH)
                y = random.randrange(-ASTEROID_SPAWN_EDGE_BUFFER, 0)
            else: # bottom
                x = random.randrange(0, SCREEN_WIDTH)
                y = random.randrange(SCREEN_HEIGHT, SCREEN_HEIGHT + ASTEROID_SPAWN_EDGE_BUFFER)
            self.pos = pygame.math.Vector2(x, y)
        else:
            self.pos = pygame.math.Vector2(pos)

        if vel is None:
            speed = random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
            angle = random.uniform(0, 2 * math.pi) # Radians
            self.vel = pygame.math.Vector2(speed * math.cos(angle), speed * math.sin(angle))
        else:
            self.vel = pygame.math.Vector2(vel)

        self.rect.center = self.pos

        # Rotation properties
        self.angle = 0
        self.rot_speed = random.uniform(-1, 1) # Degrees per frame

    def update(self):
        # Movement
        self.pos += self.vel
        self.rect.center = self.pos

        # Rotation
        self.angle = (self.angle + self.rot_speed) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        # Wrap around screen edges
        wrap_position(self, SCREEN_WIDTH, SCREEN_HEIGHT)

    def break_apart(self, asteroids_group, all_sprites_group):
        """Creates smaller asteroids when destroyed."""
        if self.size > 1:
            new_size = self.size - 1
            # Create 2 smaller asteroids
            for _ in range(2):
                # Slightly randomized velocity based on original
                angle_offset = random.uniform(-math.pi/4, math.pi/4) # +/- 45 degrees
                speed_mult = random.uniform(1.1, 1.5)
                new_vel = self.vel.rotate(math.degrees(angle_offset)) * speed_mult
                new_ast = Asteroid(new_size, pos=self.pos, vel=new_vel)
                asteroids_group.add(new_ast)
                all_sprites_group.add(new_ast)
        self.kill() # Remove the current asteroid


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player # Reference to the player who shot it (if needed later)
        self.radius = BULLET_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, CYAN, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        self.vel = direction_vector.normalize() * BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        # Remove if bullet flies off screen (optional: wrap instead)
        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
             self.kill()
        # Remove after lifespan
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFESPAN:
            self.kill()


# --- Game Class ---
class Game:
    def __init__(self):
        # Initialize Pygame and create window
        pygame.init()
        pygame.mixer.init() # For sound (optional)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.font_name = pygame.font.match_font('arial') # Or specify a font file
        self.state = "START" # Possible states: START, PLAYING, GAME_OVER
        self.starfield = self.create_starfield()

    def create_starfield(self, num_stars=150):
        """Creates a list of star positions and sizes for the background."""
        stars = []
        for _ in range(num_stars):
            x = random.randrange(0, SCREEN_WIDTH)
            y = random.randrange(0, SCREEN_HEIGHT)
            size = random.choice([1, 2, 2, 3]) # More smaller stars
            stars.append(((x, y), size))
        return stars

    def draw_starfield(self):
        """Draws the pre-generated starfield."""
        for pos, size in self.starfield:
            if size == 1:
                pygame.draw.circle(self.screen, GRAY, pos, size)
            else:
                 pygame.draw.circle(self.screen, WHITE, pos, size // 2) # Make larger stars brighter points


    def new_game(self):
        # Start a new game
        self.score = 0
        self.state = "PLAYING"
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        # Create player ship
        self.player = Player(self)
        self.all_sprites.add(self.player)
        # Spawn starting asteroids
        for _ in range(ASTEROID_START_COUNT):
            self.spawn_asteroid()

        self.run() # Start the main game loop

    def spawn_asteroid(self, size=3, pos=None, vel=None):
        """Spawns a single asteroid and adds it to groups."""
        asteroid = Asteroid(size, pos, vel)
        self.all_sprites.add(asteroid)
        self.asteroids.add(asteroid)


    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            if self.state == "PLAYING":
                self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

        # Check for bullet hitting asteroid
        # pygame.sprite.groupcollide(group1, group2, dokill1, dokill2, collided=None)
        # dokill=True removes the sprite from ALL groups it belongs to
        hits = pygame.sprite.groupcollide(self.asteroids, self.bullets, False, True) # Don't kill asteroid yet, kill bullet
        for asteroid_hit in hits: # The keys of the dict are the asteroids hit
            self.score += asteroid_hit.score_value
            # TODO: Add explosion effect here
            asteroid_hit.break_apart(self.asteroids, self.all_sprites) # Handle breaking/removal

        # Check for player hitting asteroid
        # Use circle collision for more accuracy
        if not self.player.hidden and not self.player.invulnerable:
            hits = pygame.sprite.spritecollide(self.player, self.asteroids, True, pygame.sprite.collide_circle_ratio(0.7))
            # The third argument 'True' kills the asteroid upon collision
            if hits:
                 # TODO: Player explosion effect
                 self.player.hide()
                 # Respawn the asteroids that hit the player (optional, makes it harder)
                 # for hit_ast in hits:
                 #      self.spawn_asteroid(hit_ast.size, hit_ast.pos, hit_ast.vel)
                 if self.player.lives <= 0:
                     self.state = "GAME_OVER"


        # Check if player runs out of lives
        if self.player.lives <= 0 and not self.player.hidden : # Wait until hide animation finishes
            self.state = "GAME_OVER"
            self.playing = False # Exit the inner playing loop, but not the main 'running' loop


        # Spawn new asteroids if few are left (optional wave system)
        if len(self.asteroids) < ASTEROID_START_COUNT // 2 :
             self.spawn_asteroid()


    def events(self):
        # Game Loop - Events
        for event in pygame.event.get():
            # Check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # Handle input for different states
            if self.state == "START":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Press Enter to start
                        self.new_game()
                    if event.key == pygame.K_ESCAPE:
                         self.running = False
            elif self.state == "PLAYING":
                 if event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_ESCAPE: # Optional: Pause or Quit during game
                         self.playing = False
                         self.running = False # Or implement pause state
            elif self.state == "GAME_OVER":
                 if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Press Enter to play again
                        self.state = "START" # Go back to start screen
                        # Or call self.new_game() directly to restart immediately
                    if event.key == pygame.K_ESCAPE:
                         self.running = False


    def draw(self):
        # Game Loop - Draw
        self.screen.fill(BLACK) # Black background
        self.draw_starfield()   # Draw stars

        if self.state == "START":
            self.show_start_screen()
        elif self.state == "PLAYING":
            # Draw all sprites (using the custom draw for player blinking)
            for sprite in self.all_sprites:
                 if isinstance(sprite, Player):
                     sprite.draw(self.screen) # Use custom draw method if invulnerable
                 elif not sprite.alive(): # Skip drawing if sprite kill() was called but group not updated yet?
                     pass
                 else:
                     self.screen.blit(sprite.image, sprite.rect)

            # Draw Score
            draw_text(self.screen, f"Score: {self.score}", 24, SCREEN_WIDTH / 2, 10)
            # Draw Lives (simple icons)
            for i in range(self.player.lives):
                 # Draw small ship icons for lives
                 life_icon_rect = self.player.image_orig.get_rect()
                 life_icon_scaled = pygame.transform.scale(self.player.image_orig, (life_icon_rect.width // 2, life_icon_rect.height // 2))
                 life_icon_rect = life_icon_scaled.get_rect()
                 life_icon_rect.center = (30 + i * (life_icon_rect.width + 5) , 25)
                 self.screen.blit(life_icon_scaled, life_icon_rect)

        elif self.state == "GAME_OVER":
            self.show_game_over_screen()

        # *after* drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        draw_text(self.screen, "ASTEROIDS", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, "Arrows/WASD to move, Space to shoot", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "Press ENTER to begin", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)

    def show_game_over_screen(self):
        draw_text(self.screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, f"Final Score: {self.score}", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "Press ENTER to play again", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        draw_text(self.screen, "Press ESCAPE to quit", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 40)


# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    while game.running:
        if game.state == "START":
            game.show_start_screen()
            pygame.display.flip() # Update screen for start menu
            game.events() # Need to process events to start/quit
        elif game.state == "PLAYING": # Should be handled by new_game calling run()
            # This state is entered via new_game() which has its own loop
             pass # Should not be reached directly in this outer loop normally
        elif game.state == "GAME_OVER":
            game.show_game_over_screen()
            pygame.display.flip() # Update screen for game over
            game.events() # Need to process events to restart/quit

    pygame.quit()


