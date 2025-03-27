import pygame
import os

# PROMPT for Gemini 2.5 Pro Experimental 03-25 :  Write Space Invaders game in python using pygame library. Make it visually appealing
# PROMPT for Gemini 2.5 Pro Experimental 03-25 : can you generate image assets used in this game for me?
# PROMPT for Gemini 2.5 Pro Experimental 03-25 :  WrCombine Asset Generation script  with updated Space Invaders python game to single python file to make game check if assets are available when game starts and if assets are missing generate them automatically and start game. If assets are already available in asset directory skip generation assets part and start game immediately.
# Write single python code file that I can copy and paste
# PROMPT for Gemini 2.5 Pro Experimental 03-25 :  when checking your code getting following error in several lines:
# ERROR:  An illegal target for variable annotation  when checking your code getting following error in several lines:
# ERROR:  An illegal target for variable annotation





# --- Configuration (Match these with your game constants if they differ) ---
ASSET_DIR = "assets"
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 20
INVADER_WIDTH = 30
INVADER_HEIGHT = 20
BULLET_WIDTH = 4
BULLET_HEIGHT = 10

# Colors (Match your game colors or choose classic ones)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0) # Use for background transparency

# Game Colors (from the code)
PLAYER_COLOR = (0, 255, 0) # GREEN
BULLET_COLOR = (255, 255, 0) # YELLOW
INVADER_COLORS = [
    (200, 200, 200), # Row 0/3/4 type (e.g., Squid) - Was GRAY-ish
    (150, 150, 250), # Row 1/2 type (e.g., Crab) - Was BLUE-ish
    (250, 150, 150), # Row 2 type (e.g., Octopus) - Was RED-ish
    # If you have more distinct types, add colors here
]

# --- Helper Function ---
def save_surface(surface, filename):
    """Saves a Pygame surface to a file in the asset directory."""
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
    filepath = os.path.join(ASSET_DIR, filename)
    try:
        pygame.image.save(surface, filepath)
        print(f"Successfully saved: {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# --- Asset Creation Functions ---

def create_player():
    """Creates the player ship asset."""
    surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    # Simple cannon shape
    # Base
    pygame.draw.rect(surface, PLAYER_COLOR, (0, PLAYER_HEIGHT - 8, PLAYER_WIDTH, 8))
    # Middle part
    pygame.draw.rect(surface, PLAYER_COLOR, (PLAYER_WIDTH // 2 - 8, PLAYER_HEIGHT - 14, 16, 6))
    # Nozzle
    pygame.draw.rect(surface, PLAYER_COLOR, (PLAYER_WIDTH // 2 - 3, 0, 6, PLAYER_HEIGHT - 10))
    # Small white detail
    pygame.draw.rect(surface, WHITE, (PLAYER_WIDTH // 2 - 1, 2, 2, 4))

    save_surface(surface, "player.png")

def create_bullet():
    """Creates the bullet asset."""
    surface = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    pygame.draw.rect(surface, BULLET_COLOR, (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
    save_surface(surface, "bullet.png")


def create_invader(row_type, frame):
    """Creates an invader asset.
       row_type: 0, 1, 2 (indexes into INVADER_COLORS)
       frame: 'a' or 'b' for animation
    """
    surface = pygame.Surface((INVADER_WIDTH, INVADER_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    color = INVADER_COLORS[row_type % len(INVADER_COLORS)] # Use modulo for safety

    # Simplified Pixel Art - using 2x2 blocks for larger "pixels"
    pixel_size = 2
    mid_x = INVADER_WIDTH // (2*pixel_size)
    mid_y = INVADER_HEIGHT // (2*pixel_size)

    def draw_pixel(x, y, c=color):
        # Draws a 'pixel' block relative to center
        px = (mid_x + x) * pixel_size
        py = (mid_y + y - 3) * pixel_size # Adjust vertical offset
        pygame.draw.rect(surface, c, (px, py, pixel_size, pixel_size))

    # --- Design Invaders (Adjust these pixel patterns!) ---
    if row_type == 0: # Squid-like (Top)
        # Body
        for dx in [-1, 0, 1]: draw_pixel(dx, 0)
        for dx in [-2, -1, 0, 1, 2]: draw_pixel(dx, 1)
        for dx in [-3, -2, -1, 0, 1, 2, 3]: draw_pixel(dx, 2)
        for dx in [-3, -1, 0, 1, 3]: draw_pixel(dx, 3) # Eyes/Gaps
        for dx in [-3, -2, 0, 2, 3]: draw_pixel(dx, 4)
        # Tentacles Frame A
        if frame == 'a':
            for dx in [-2, 2]: draw_pixel(dx, 5)
            for dx in [-1, 1]: draw_pixel(dx, 6)
        # Tentacles Frame B
        else:
             for dx in [-1, 1]: draw_pixel(dx, 5)
             for dx in [-2, 2]: draw_pixel(dx, 6)

    elif row_type == 1: # Crab-like (Middle)
         # Body
        for dx in [-2, -1, 0, 1, 2]: draw_pixel(dx, 1)
        for dx in [-3, -2, -1, 0, 1, 2, 3]: draw_pixel(dx, 2)
        for dx in [-4,-3, -1, 0, 1, 3, 4]: draw_pixel(dx, 3) # Eyes/gaps
        for dx in [-4,-3, -2, -1, 0, 1, 2, 3, 4]: draw_pixel(dx, 4)
        # Legs Frame A
        if frame == 'a':
             for dx in [-4, 4]: draw_pixel(dx, 2)
             for dx in [-3, 3]: draw_pixel(dx, 5)
             for dx in [-2, -1, 1, 2]: draw_pixel(dx, 5)
        # Legs Frame B
        else:
             for dx in [-4, 4]: draw_pixel(dx, 5)
             for dx in [-3, 3]: draw_pixel(dx, 4)
             draw_pixel(-1, 5); draw_pixel(1, 5)


    elif row_type == 2: # Octopus-like (Bottom)
        # Body
        for dx in [-2,-1, 0, 1, 2]: draw_pixel(dx, 0)
        for dx in [-3,-2, -1, 0, 1, 2, 3]: draw_pixel(dx, 1)
        for dx in [-4,-3,-2,-1, 0, 1, 2, 3, 4]: draw_pixel(dx, 2)
        for dx in [-4, -2,-1, 0, 1, 2, 4]: draw_pixel(dx, 3) # Eyes/Gaps
        for dx in [-3,-2, 2, 3]: draw_pixel(dx, 4)
        # Tentacles Frame A
        if frame == 'a':
            for dx in [-3, -1, 1, 3]: draw_pixel(dx, 5)
            for dx in [-2, 2]: draw_pixel(dx, 6)
        # Tentacles Frame B
        else:
            for dx in [-2, -1, 1, 2]: draw_pixel(dx, 5)
            for dx in [-3, 3]: draw_pixel(dx, 6)


    # Save the specific invader file
    filename = f"invader_row{row_type}_{frame}.png"
    save_surface(surface, filename)


# --- Main Generation ---
if __name__ == "__main__":
    print("Initializing Pygame to generate assets...")
    pygame.init()

    print("\nCreating assets...")
    create_player()
    create_bullet()

    # Create invaders for types 0, 1, 2 and frames 'a', 'b'
    for type_index in range(len(INVADER_COLORS)): # Create for all defined colors
        create_invader(type_index, 'a')
        create_invader(type_index, 'b')

    print("\nAsset generation complete.")
    pygame.quit()
    print("Pygame quit.")