# board.py — pygame rendering for the 10×10 board, snakes, and ladders.
# Pure drawing: no game state, no logic.

import math
import random
import pygame
from constants import (
    GRID_SIZE, CELL_SIZE, MARGIN, BOARD_SIZE,
    GRID_COL, GRID_LINE_COL, MINIGAME_CELL_COL,
    SNAKE_COL, LADDER_COL,
    SNAKES, LADDERS, CHALLENGE_SQUARES, TIC_TAC_TOE_COL, REACTION_COL,
)

# Pick the palette placement once when the application starts.  Choosing a
# colour while drawing would make cells change colour every frame.
_palette = tuple(pygame.Color(colour) for colour in GRID_COL)
_cell_colours = {cell: random.choice(_palette) for cell in range(1, 101)}


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

        pygame.draw.rect(surface, _cell_colours[cell], (rx, ry, CELL_SIZE, CELL_SIZE))

        if cell in SNAKES:
            pygame.draw.rect(surface, (255, 200, 200),
                             (rx+2, ry+2, CELL_SIZE-4, CELL_SIZE-4),
                             border_radius=6)
        elif cell in LADDERS:
            pygame.draw.rect(surface, (200, 240, 200),
                             (rx+2, ry+2, CELL_SIZE-4, CELL_SIZE-4),
                             border_radius=6)
        elif cell in CHALLENGE_SQUARES:
            pygame.draw.rect(surface, MINIGAME_CELL_COL,
                             (rx+2, ry+2, CELL_SIZE-4, CELL_SIZE-4), border_radius=6)

        num = font_small.render(str(cell), True, GRID_LINE_COL)
        surface.blit(num, (rx + 4, ry + 4))
        if cell in CHALLENGE_SQUARES:
            colour = TIC_TAC_TOE_COL if CHALLENGE_SQUARES[cell] == "tic_tac_toe" else REACTION_COL
            pygame.draw.circle(surface, colour, (rx + CELL_SIZE - 12, ry + CELL_SIZE - 12), 8)
            pygame.draw.circle(surface, GRID_LINE_COL, (rx + CELL_SIZE - 12, ry + CELL_SIZE - 12), 8, 1)

    # Grid lines on top
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(surface, GRID_LINE_COL,
                         (MARGIN, MARGIN + i * CELL_SIZE),
                         (MARGIN + BOARD_SIZE, MARGIN + i * CELL_SIZE), 1)
        pygame.draw.line(surface, GRID_LINE_COL,
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, MARGIN + BOARD_SIZE), 1)


def draw_snakes(surface: pygame.Surface, snakes=None) -> None:
    """Draw all snakes as wavy lines with a head circle and eye dots."""
    for start, end in (SNAKES if snakes is None else snakes).items():
        x1, y1 = cell_to_pos(start)
        x2, y2 = cell_to_pos(end)
        _draw_wavy_line(surface, SNAKE_COL, x1, y1, x2, y2, width=6, waves=5)

        # Head
        pygame.draw.circle(surface, SNAKE_COL, (x1, y1), 10)
        pygame.draw.circle(surface, (230, 80, 80), (x1, y1), 7)

        # Eyes
        angle = math.atan2(y2 - y1, x2 - x1)
        for sign in (-0.6, 0.6):
            ex = int(x1 + 4 * math.cos(angle - sign))
            ey = int(y1 + 4 * math.sin(angle - sign))
            pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 2)

        # Tail
        pygame.draw.circle(surface, SNAKE_COL, (x2, y2), 4)


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
                         (int(x1+px), int(y1+py)), (int(x2+px), int(y2+py)), 4)
        pygame.draw.line(surface, LADDER_COL,
                         (int(x1-px), int(y1-py)), (int(x2-px), int(y2-py)), 4)

        # Rungs
        rungs = max(3, int(length / 30))
        for r in range(1, rungs):
            t  = r / rungs
            rx = int(x1 + t * dx)
            ry = int(y1 + t * dy)
            pygame.draw.line(surface, LADDER_COL,
                             (int(rx+px), int(ry+py)),
                             (int(rx-px), int(ry-py)), 3)

        # End dots
        pygame.draw.circle(surface, LADDER_COL, (x1, y1), 6)
        pygame.draw.circle(surface, LADDER_COL, (x2, y2), 6)


# ── Internal helper ───────────────────────────────────────────────────────────

def _draw_wavy_line(surf, color, x1, y1, x2, y2, width=4, waves=4):
    steps  = waves * 8
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    amp    = min(CELL_SIZE * 0.18, 10)

    pts = []
    for i in range(steps + 1):
        t    = i / steps
        cx   = x1 + t * dx
        cy   = y1 + t * dy
        wave = amp * math.sin(t * waves * 2 * math.pi)
        pts.append((int(cx + wave * px), int(cy + wave * py)))

    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, width)
    steps  = waves * 8
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    amp    = min(CELL_SIZE * 0.18, 10)

    pts = []
    for i in range(steps + 1):
        t    = i / steps
        cx   = x1 + t * dx
        cy   = y1 + t * dy
        wave = amp * math.sin(t * waves * 2 * math.pi)
        pts.append((int(cx + wave * px), int(cy + wave * py)))

    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, width)
