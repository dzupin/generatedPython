#!/usr/bin/env python3

import os
import random
from PIL import Image, ImageDraw


ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)


# Increase or decrease SCALE to make sprites bigger/smaller.
# For classic tiny Space Invaders style, use SCALE = 1.
# For modern windows, SCALE = 3 or 4 often looks better.
SCALE = 3
BULLET_SCALE = 2


PALETTE = {
    "G": (102, 255, 102, 255),     # green
    "M": (255, 102, 170, 255),     # pink/magenta
    "Y": (255, 235, 102, 255),     # yellow
    "W": (240, 240, 240, 255),     # white
    "C": (120, 220, 255, 255),     # cyan
    "B": (70, 70, 90, 255),        # dark blue/gray
    "O": (255, 140, 50, 255),      # orange
    "R": (255, 80, 80, 255),       # red
}


def make_sprite(grid, scale=SCALE, background=(0, 0, 0, 0)):
    """
    Convert a text grid into a transparent PNG sprite.

    Example:
    [
        "..X..",
        ".XXX.",
        "XXXXX"
    ]

    "." means transparent.
    Letters are colors defined in PALETTE.
    """
    width = max(len(row) for row in grid)
    height = len(grid)

    img = Image.new("RGBA", (width * scale, height * scale), background)
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == ".":
                continue

            color = PALETTE.get(ch, (255, 0, 255, 255))

            draw.rectangle(
                [
                    x * scale,
                    y * scale,
                    (x + 1) * scale - 1,
                    (y + 1) * scale - 1,
                ],
                fill=color,
            )

    return img


def save_image(img, filename):
    path = os.path.join(ASSETS_DIR, filename)
    img.save(path)
    print("Wrote", path)


# ----------------------------------------------------------------------
# Player ship
# ----------------------------------------------------------------------
PLAYER = [
    "......C......",
    ".....CCC.....",
    ".....CCC.....",
    "...CCCCCCC...",
    ".CCCCCCCCCCC.",
    "CCCCCCCCCCCCC",
    "CCCCCCCCCCCCC",
    "CBCCCCCBCCCCC",
    "CCCBCCCBCCCCC",
]


# ----------------------------------------------------------------------
# Invaders
# ----------------------------------------------------------------------
INVADER_GREEN_1 = [
    "....G.G....",
    "...G...G...",
    "..GGGGGGG..",
    ".GG.GGG.GG.",
    "GGGGGGGGGGG",
    "G.GGGGGGG.G",
    "G.G.....G.G",
    "...G...G...",
]

INVADER_GREEN_2 = [
    "....G.G....",
    "...G...G...",
    "..GGGGGGG..",
    ".GG.GGG.GG.",
    "GGGGGGGGGGG",
    ".GG.GGG.GG.",
    ".G.G...G.G.",
    "GG.......GG",
]

INVADER_PINK_1 = [
    "..M....M...",
    "...M..M....",
    "..MMMMMM...",
    ".M.MMM.M...",
    "MMMMMMMMMM.",
    "M.MMMMMMM.M",
    "M..M...M..M",
    "...M...M...",
]

INVADER_PINK_2 = [
    "..M....M...",
    "...M..M....",
    "..MMMMMM...",
    ".M.MMM.M...",
    "MMMMMMMMMM.",
    ".MMMMMMMMM.",
    ".M..MMM..M.",
    ".MM.MMM.MM.",
]

INVADER_YELLOW_1 = [
    "...YYYYY...",
    "..YYYYYYY..",
    ".YYY.Y.YYY.",
    "YYYYYYYYYYY",
    "YYYYYYYYYYY",
    ".YY.YYYY.YY",
    "...YY.YY...",
    "..Y.....Y..",
]

INVADER_YELLOW_2 = [
    "...YYYYY...",
    "..YYYYYYY..",
    ".YYY.Y.YYY.",
    "YYYYYYYYYYY",
    "YYYYYYYYYYY",
    ".YY.YYYY.YY",
    "..Y.Y..Y.Y.",
    "..Y.Y..Y.Y.",
]


# ----------------------------------------------------------------------
# Bullets
# ----------------------------------------------------------------------
PLAYER_BULLET = [
    "W",
    "W",
    "W",
    "W",
]

ENEMY_BULLET_1 = [
    ".M.",
    "M.M",
    "M.M",
    ".M.",
    "M.M",
    ".M.",
]

ENEMY_BULLET_2 = [
    "M.M",
    ".M.",
    "M.M",
    ".M.",
    "M.M",
    ".M.",
]


# ----------------------------------------------------------------------
# Explosions
# ----------------------------------------------------------------------
EXPLOSION_1 = [
    "....O....",
    "...O.O...",
    ".O..O..O.",
    "..O.O.O..",
    "O.O.O.O.O",
    "..O.O.O..",
    ".O..O..O.",
    "...O.O...",
    "....O....",
]

EXPLOSION_2 = [
    "O.O.O.O.O",
    ".OO.O.OO.",
    "O..OO..O.",
    ".O.O.O.O.",
    "O..OO..O.",
    ".OO.O.OO.",
    "O.O.O.O.O",
]


# ----------------------------------------------------------------------
# Simple space background
# ----------------------------------------------------------------------
def make_background(size=256, star_count=90, seed=42):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    rng = random.Random(seed)

    # Small stars
    for _ in range(star_count):
        x = rng.randrange(size)
        y = rng.randrange(size)
        v = rng.randrange(70, 255)
        draw.point((x, y), fill=(v, v, v, 255))

    # A few larger glowing stars
    for _ in range(10):
        x = rng.randrange(size)
        y = rng.randrange(size)
        r = rng.randrange(1, 3)
        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=(255, 255, 255, 160),
        )

    return img


if __name__ == "__main__":
    save_image(make_sprite(PLAYER), "player.png")

    save_image(make_sprite(INVADER_GREEN_1), "invader_green_1.png")
    save_image(make_sprite(INVADER_GREEN_2), "invader_green_2.png")

    save_image(make_sprite(INVADER_PINK_1), "invader_pink_1.png")
    save_image(make_sprite(INVADER_PINK_2), "invader_pink_2.png")

    save_image(make_sprite(INVADER_YELLOW_1), "invader_yellow_1.png")
    save_image(make_sprite(INVADER_YELLOW_2), "invader_yellow_2.png")

    save_image(
        make_sprite(PLAYER_BULLET, scale=BULLET_SCALE),
        "bullet_player.png",
    )

    save_image(
        make_sprite(ENEMY_BULLET_1, scale=BULLET_SCALE),
        "bullet_enemy_1.png",
    )

    save_image(
        make_sprite(ENEMY_BULLET_2, scale=BULLET_SCALE),
        "bullet_enemy_2.png",
    )

    save_image(make_sprite(EXPLOSION_1), "explosion_1.png")
    save_image(make_sprite(EXPLOSION_2), "explosion_2.png")

    save_image(make_background(), "background.png")

    print("\nDone. Assets are in:", ASSETS_DIR)
