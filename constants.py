# constants.py — shared config for game logic AND renderer
# No pygame import here so the bot can use this headless.

GRID_SIZE  = 10
CELL_SIZE  = 70
MARGIN     = 30
BOARD_SIZE = GRID_SIZE * CELL_SIZE   # 700
PANEL_W    = 260
WIN_W      = MARGIN + BOARD_SIZE + MARGIN + PANEL_W
WIN_H      = MARGIN + BOARD_SIZE + MARGIN

FPS        = 60
ANIM_SPEED = 4   # cells per second during movement animation

# ── Board layout ──────────────────────────────────────────────────────────────
# Keys = tile that triggers the event, Values = destination
LADDERS: dict[int, int] = {
     4: 14,
     9: 31,
    20: 38,
    28: 84,
    40: 59,
    51: 67,
    63: 81,
    71: 91,
}

SNAKES: dict[int, int] = {
    17:  7,
    54: 34,
    62: 19,
    64: 60,
    87: 24,
    93: 73,
    95: 75,
    99: 78,
}

# ── Colours (only needed by renderer/board.py) ────────────────────────────────
BG         = (245, 240, 230)
GRID_COL   = ( 90,  76,  58)
CELL_LIGHT = (255, 248, 235)
CELL_DARK  = (230, 210, 175)
SNAKE_COL  = (190,  40,  40)
LADDER_COL = ( 40, 150,  60)
P1_COL     = ( 70, 130, 210)
P2_COL     = (210,  80,  80)
TEXT_DARK  = ( 50,  42,  30)
TEXT_LIGHT = (255, 255, 255)
PANEL_BG   = (235, 228, 212)
BTN_COL    = ( 80,  65,  45)
BTN_HOV    = (110,  90,  60)
BTN_TXT    = (255, 248, 235)
HIGHLIGHT  = (255, 215,   0)