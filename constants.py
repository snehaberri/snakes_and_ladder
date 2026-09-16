
# constants.py — shared config for the Snakes & Ladders game.
# Nothing here draws or plays anything; it's just numbers and colours
# that board.py and main.py both need.

# ── Board geometry ──────────────────────────────────────────────────────────
GRID_SIZE  = 10                        # 10x10 board
CELL_SIZE  = 70                        # pixels per cell
MARGIN     = 40                        # space around the board for edge labels
BOARD_SIZE = GRID_SIZE * CELL_SIZE     # 700 — total board width/height (no margin)

BOARD_AREA = BOARD_SIZE + 2 * MARGIN   # 780 — full board incl. margins on both sides
PANEL_WIDTH = 260                      # side panel: dice, turn, messages

WINDOW_WIDTH  = BOARD_AREA + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_AREA
FPS = 60

# ── Colours ──────────────────────────────────────────────────────────────
BACKGROUND  = (16, 75, 30)
GRID_COL    = [
    "#ec2029",
    "#0976bb",
    "#0f954a",
    "#fff5d2",
    "#d7e02c"]
GRID_LINE_COL = (60, 60, 60)
MINIGAME_CELL_COL = "#fff5d2"
CELL_LIGHT  = (240, 240, 214)
CELL_DARK   = (206, 204, 168)
SNAKE_COL   = (200, 60, 60)
LADDER_COL  = (60, 140, 70)
PANEL_BG    = (24, 90, 40)
TEXT_COL    = (255, 255, 255)
BUTTON_COL  = (230, 180, 40)
BUTTON_HOVER = (245, 200, 70)
BUTTON_TEXT = (30, 30, 30)

PLAYER_COLORS = [
    (220, 50, 50),   # red
    (50, 100, 220),  # blue
    (240, 200, 40),  # yellow
    (140, 70, 210),  # purple
]

# ── Snakes and ladders ──────────────────────────────────────────────────
# key = start cell (head / bottom of ladder), value = end cell (tail / top)
SNAKES = {
    16: 6,
    47: 26,
    49: 11,
    56: 53,
    62: 19,
    64: 60,
    87: 24,
    72: 50,
    95: 86,
    99: 77,
}
tic_tac_toe = {}
LADDERS = {
    7: 38,
    9: 31,
    21: 42,
    28: 65,
    36: 44,
    43: 60,
    51: 67,
    71: 91,
    80: 100,
}

# Five coloured mini-game squares: purple is tic-tac-toe; cyan is reaction.
CHALLENGE_SQUARES = {13: "tic_tac_toe",
                    22: "tic_tac_toe", 
                    30: "reaction_time",
                    30: "reaction_time", 
                    45: "tic_tac_toe", 
                    68: "reaction_time", 
                    86: "tic_tac_toe", 
                    19: "reaction_time",
                    60: "tic_tac_toe",
                    5: "reaction_time",
                    78: "tic_tac_toe",
                    97: "tic_tac_toe"
                    }

TIC_TAC_TOE_COL = (155, 95, 210)
REACTION_COL = (35, 180, 205)
