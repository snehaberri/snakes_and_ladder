# board.py — pygame rendering for the 10×10 board, snakes, and ladders.
# Pure drawing: no game state, no logic.

import math
import random
import pygame
from constants import (
    GRID_SIZE, CELL_SIZE, MARGIN, BOARD_SIZE,
    GRID_COL, GRID_LINE_COL,
    SNAKE_COL, LADDER_COL,
    SNAKES, LADDERS, CHALLENGE_SQUARES, TIC_TAC_TOE_COL, REACTION_COL,
)


_palette = tuple(pygame.Color(colour) for colour in GRID_COL)
SNAKE_COLORS = (
    pygame.Color("#77859b"),
    pygame.Color("#c2bbb8"), #repeat for two snakes, inner colors
    pygame.Color("#d6df45"),
    pygame.Color("#703182"),
    pygame.Color("#FFFFFF"),
)

# Each row uses the same deliberate color sequence.
# board.py
TILE_COLOURS = [
    # Top row
    ["#ec2029", "#0976bb", "#0f954a", "#fff5d2", "#d7e02c",
     "#0976bb", "#ec2029", "#0f954a", "#fff5d2", "#d7e02c"],

    ["#0976bb", "#fff5d2", "#d7e02c", "#ec2029", "#0f954a",
     "#ec2029", "#d7e02c", "#fff5d2", "#0976bb", "#0f954a"],

    ["#0f954a", "#fff5d2", "#ec2029", "#d7e02c", "#0976bb",
     "#ec2029", "#d7e02c", "#ec2029", "#0f954a", "#0976bb"],

    ["#fff5d2", "#ec2029", "#0976bb", "#0f954a", "#d7e02c",
     "#fff5d2", "#ec2029", "#0976bb", "#0f954a", "#d7e02c"],

    ["#d7e02c", "#0f954a", "#fff5d2", "#0976bb", "#ec2029",
     "#d7e02c", "#0f954a", "#fff5d2", "#0976bb", "#ec2029"],

    # Repeat or customize five more rows
] * 2

def cell_to_pos(cell: int) -> tuple[int, int]:
    """
    Convert a cell number (1-100) to its pixel centre on screen.
    Uses boustrophedon (zig-zag) layout: odd rows left→right,
    even rows right→left; row 0 is visually at the bottom.
    """
    idx        = cell - 1
    row        = idx // GRID_SIZE
    col        = idx % GRID_SIZE
    if row % 2 == 1:
        col = GRID_SIZE - 1 - col
    screen_row = GRID_SIZE - 1 - row
    x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + screen_row * CELL_SIZE + CELL_SIZE // 2
    return (x, y)


def draw_board(surface: pygame.Surface, font_small: pygame.font.Font) -> None:
    """Draw colourful, randomly placed cell colours and board markers."""
    for cell in range(1, 101):
        idx        = cell - 1
        row        = idx // GRID_SIZE
        col        = idx % GRID_SIZE
        if row % 2 == 1:
            col = GRID_SIZE - 1 - col
        screen_row = GRID_SIZE - 1 - row
        rx = MARGIN + col * CELL_SIZE
        ry = MARGIN + screen_row * CELL_SIZE

        pygame.draw.rect(
            surface,
            pygame.Color(TILE_COLOURS[screen_row][col]),
            (rx, ry, CELL_SIZE, CELL_SIZE),
        )

        if cell in LADDERS:
            pygame.draw.rect(surface, (200, 240, 200),
                             (rx+2, ry+2, CELL_SIZE-4, CELL_SIZE-4),
                             border_radius=6)
        elif cell in CHALLENGE_SQUARES:
            challenge_colour = (
                TIC_TAC_TOE_COL
                if CHALLENGE_SQUARES[cell] == "tic_tac_toe"
                else REACTION_COL
            )
            pygame.draw.rect(
                surface,
                challenge_colour,
                (rx + 2, ry + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                border_radius=6,
            )
            _draw_star(surface, rx + CELL_SIZE // 2, ry + CELL_SIZE // 2)

        num = font_small.render(str(cell), True, GRID_LINE_COL)
        surface.blit(num, (rx + 4, ry + 4))
    # Grid lines on top
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(surface, (0, 0, 0),
                         (MARGIN, MARGIN + i * CELL_SIZE),
                         (MARGIN + BOARD_SIZE, MARGIN + i * CELL_SIZE), 4)
        pygame.draw.line(surface, (0, 0, 0),
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, MARGIN + BOARD_SIZE), 4)


def draw_snakes(surface: pygame.Surface, snakes=None) -> None:
    """Draw snakes as bold, illustrated curves over the board."""
    for start, end in (SNAKES if snakes is None else snakes).items():
        x1, y1 = cell_to_pos(start)
        x2, y2 = cell_to_pos(end)
        points = _snake_points(x1, y1, x2, y2)
        outline = (35, 25, 25)
        color_seed = start * 1009 + end * 9176
        body = random.Random(color_seed).choice(SNAKE_COLORS)

        shadow = [(x + 3, y + 4) for x, y in points]
        pygame.draw.lines(surface, (0, 0, 0, 55), False, shadow, 13)
        pygame.draw.lines(surface, outline, False, points, 15)
        pygame.draw.lines(surface, body, False, points, 11)
        pattern_points = _snake_zigzag(points)
        pygame.draw.lines(surface, (255, 255, 255), False, pattern_points, 3)

        # Head
        angle = math.atan2(points[1][1] - y1, points[1][0] - x1)
        pygame.draw.circle(surface, outline, (x1, y1), 11)
        pygame.draw.circle(surface, body, (x1, y1), 9)

        forward = (math.cos(angle) * 7, math.sin(angle) * 7)
        side = (-math.sin(angle) * 7, math.cos(angle) * 7)
        for sign in (-1, 1):
            eye = (int(x1 + forward[0] + side[0] * sign),
                   int(y1 + forward[1] + side[1] * sign))
            pygame.draw.circle(surface, (250, 235, 190), eye, 4)
            pygame.draw.circle(surface, (25, 20, 20), eye, 2)

        tongue_start = (int(x1 + math.cos(angle) * 13), int(y1 + math.sin(angle) * 13))
        tongue_tip = (int(x1 + math.cos(angle) * 22), int(y1 + math.sin(angle) * 22))
        pygame.draw.line(surface, (210, 45, 65), tongue_start, tongue_tip, 2)
        for sign in (-1, 1):
            fork = (int(tongue_tip[0] + math.cos(angle + sign * 0.55) * 6),
                    int(tongue_tip[1] + math.sin(angle + sign * 0.55) * 6))
            pygame.draw.line(surface, (210, 45, 65), tongue_tip, fork, 2)

        # Tail
        pygame.draw.circle(surface, outline, (x2, y2), 5)
        pygame.draw.circle(surface, body, (x2, y2), 3)


def draw_ladders(surface: pygame.Surface, ladders=None) -> None:
    """Draw all ladders as two rails with evenly-spaced rungs."""
    for start, end in (LADDERS if ladders is None else ladders).items():
        x1, y1 = cell_to_pos(start)
        x2, y2 = cell_to_pos(end)
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        px, py = -dy / length * 6, dx / length * 6   # perpendicular offset

        # Rails
        pygame.draw.line(surface, LADDER_COL,
                 (int(x1+px), int(y1+py)), (int(x2+px), int(y2+py)), 7)
        pygame.draw.line(surface, LADDER_COL,
                 (int(x1-px), int(y1-py)), (int(x2-px), int(y2-py)), 7)

        # Rungs
        rungs = max(3, int(length / 30))
        for r in range(1, rungs):
            t  = r / rungs
            rx = int(x1 + t * dx)
            ry = int(y1 + t * dy)
            pygame.draw.line(surface, LADDER_COL,
                             (int(rx+px), int(ry+py)),
                             (int(rx-px), int(ry-py)), 6)

# ── Internal helper ───────────────────────────────────────────────────────────

def _draw_star(surface: pygame.Surface, center_x: int, center_y: int) -> None:
    """Draw a prominent gold five-point star for a mini-game tile."""
    points = []
    for point in range(10):
        radius = 27 if point % 2 == 0 else 12
        angle = math.radians(-90 + point * 36)
        points.append((
            int(center_x + radius * math.cos(angle)),
            int(center_y + radius * math.sin(angle)),
        ))
    pygame.draw.polygon(surface, (255, 215, 0), points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 2)

def _snake_points(x1, y1, x2, y2):
    steps = 32
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return [(x1, y1), (x2, y2)]
    px, py = -dy / length, dx / length
    amplitude = min(CELL_SIZE * 0.28, 20)

    pts = []
    for i in range(steps + 1):
        t    = i / steps
        cx   = x1 + t * dx
        cy   = y1 + t * dy
        wave = amplitude * math.sin(t * 3 * math.pi)
        pts.append((int(cx + wave * px), int(cy + wave * py)))
    return pts


def _snake_zigzag(points):
    """Build a white zig-zag stripe that follows the snake's curved body."""
    pattern = []
    for index, (x, y) in enumerate(points):
        previous = points[max(0, index - 1)]
        following = points[min(len(points) - 1, index + 1)]
        dx = following[0] - previous[0]
        dy = following[1] - previous[1]
        length = math.hypot(dx, dy) or 1
        normal_x, normal_y = -dy / length, dx / length
        offset = 4 if (index // 2) % 2 == 0 else -4
        pattern.append((int(x + normal_x * offset), int(y + normal_y * offset)))
    return pattern
