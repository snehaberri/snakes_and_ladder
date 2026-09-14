import pygame
import sys
import random
import math

# ─── Constants ────────────────────────────────────────────────────────────────
GRID_SIZE   = 10
CELL_SIZE   = 70
MARGIN      = 30
BOARD_SIZE  = GRID_SIZE * CELL_SIZE         # 700
PANEL_W     = 260                           # right-side UI panel
WIN_W       = MARGIN + BOARD_SIZE + MARGIN + PANEL_W
WIN_H       = MARGIN + BOARD_SIZE + MARGIN  # 760

FPS         = 60
ANIM_SPEED  = 4          # cells advanced per second during movement animation

# ─── Colors ───────────────────────────────────────────────────────────────────
BG          = (245, 240, 230)
GRID_COL    = (90,  76,  58)
CELL_LIGHT  = (255, 248, 235)
CELL_DARK   = (230, 210, 175)
SNAKE_COL   = (190,  40,  40)
LADDER_COL  = (40,  150,  60)
P1_COL      = (70,  130, 210)
P2_COL      = (210,  80,  80)
TEXT_DARK   = (50,   42,  30)
TEXT_LIGHT  = (255, 255, 255)
PANEL_BG    = (235, 228, 212)
BTN_COL     = (80,   65,  45)
BTN_HOV     = (110,  90,  60)
BTN_TXT     = (255, 248, 235)
HIGHLIGHT   = (255, 215,   0)

# ─── Board layout ─────────────────────────────────────────────────────────────
LADDERS = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
SNAKES  = {17: 7, 54: 34, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}

# ─── Helper: board cell → pixel center ────────────────────────────────────────
def cell_to_pos(cell: int) -> tuple[int, int]:
    """Convert cell 1-100 to pixel center, respecting boustrophedon layout."""
    idx        = cell - 1
    row        = idx // GRID_SIZE
    col        = idx % GRID_SIZE
    if row % 2 == 1:
        col = GRID_SIZE - 1 - col          # odd rows go right→left
    screen_row = GRID_SIZE - 1 - row       # row 0 is at the bottom visually
    x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + screen_row * CELL_SIZE + CELL_SIZE // 2
    return (x, y)

# ─── Helper: draw rounded rect ────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius=10):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

# ─── Draw board tiles ─────────────────────────────────────────────────────────
def draw_board(surface: pygame.Surface, font_small) -> None:
    for cell in range(1, 101):
        idx        = cell - 1
        row        = idx // GRID_SIZE
        col        = idx % GRID_SIZE
        if row % 2 == 1:
            col = GRID_SIZE - 1 - col
        screen_row = GRID_SIZE - 1 - row
        rx = MARGIN + col * CELL_SIZE
        ry = MARGIN + screen_row * CELL_SIZE

        tile_col = CELL_LIGHT if (row + col) % 2 == 0 else CELL_DARK
        pygame.draw.rect(surface, tile_col, (rx, ry, CELL_SIZE, CELL_SIZE))

        # Snake head tile
        if cell in SNAKES:
            pygame.draw.rect(surface, (255, 200, 200),
                             (rx+2, ry+2, CELL_SIZE-4, CELL_SIZE-4), border_radius=6)
        # Ladder foot tile
        elif cell in LADDERS:
            pygame.draw.rect(surface, (200, 240, 200),
                             (rx+2, ry+2, CELL_SIZE-4, CELL_SIZE-4), border_radius=6)

        # Cell number
        num_surf = font_small.render(str(cell), True, GRID_COL)
        surface.blit(num_surf, (rx + 4, ry + 4))

    # Grid lines on top
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(surface, GRID_COL,
                         (MARGIN, MARGIN + i * CELL_SIZE),
                         (MARGIN + BOARD_SIZE, MARGIN + i * CELL_SIZE), 1)
        pygame.draw.line(surface, GRID_COL,
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, MARGIN + BOARD_SIZE), 1)

# ─── Draw snakes (wavy bezier-style via small segments) ───────────────────────
def draw_snakes(surface: pygame.Surface) -> None:
    for start, end in SNAKES.items():
        x1, y1 = cell_to_pos(start)
        x2, y2 = cell_to_pos(end)
        # Draw thick body
        _draw_wavy_line(surface, SNAKE_COL, x1, y1, x2, y2, width=6, waves=5)
        # Head circle
        pygame.draw.circle(surface, SNAKE_COL, (x1, y1), 10)
        pygame.draw.circle(surface, (230, 80, 80), (x1, y1), 7)
        # Eyes
        ex1 = int(x1 + 4 * math.cos(math.atan2(y2-y1, x2-x1) - 0.6))
        ey1 = int(y1 + 4 * math.sin(math.atan2(y2-y1, x2-x1) - 0.6))
        ex2 = int(x1 + 4 * math.cos(math.atan2(y2-y1, x2-x1) + 0.6))
        ey2 = int(y1 + 4 * math.sin(math.atan2(y2-y1, x2-x1) + 0.6))
        pygame.draw.circle(surface, (255, 255, 255), (ex1, ey1), 2)
        pygame.draw.circle(surface, (255, 255, 255), (ex2, ey2), 2)
        # Tail circle
        pygame.draw.circle(surface, SNAKE_COL, (x2, y2), 4)

def _draw_wavy_line(surf, color, x1, y1, x2, y2, width=4, waves=4):
    """Draw a wavy line between two points using short segments."""
    steps   = waves * 8
    dx      = x2 - x1
    dy      = y2 - y1
    length  = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy  = dx / length, dy / length       # unit vector along path
    px, py  = -uy, ux                        # perpendicular
    amp     = min(CELL_SIZE * 0.18, 10)

    pts = []
    for i in range(steps + 1):
        t     = i / steps
        cx    = x1 + t * dx
        cy    = y1 + t * dy
        wave  = amp * math.sin(t * waves * 2 * math.pi)
        pts.append((int(cx + wave * px), int(cy + wave * py)))

    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, width)

# ─── Draw ladders (two rails + rungs) ─────────────────────────────────────────
def draw_ladders(surface: pygame.Surface) -> None:
    for start, end in LADDERS.items():
        x1, y1 = cell_to_pos(start)
        x2, y2 = cell_to_pos(end)
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        px, py = -dy / length * 6, dx / length * 6    # perpendicular offset

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

# ─── Load/create dice images ──────────────────────────────────────────────────
def load_dice() -> list:
    dice_imgs = []
    for i in range(1, 7):
        try:
            img = pygame.image.load(f'assets/dice/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (90, 90))
            dice_imgs.append(img)
        except Exception:
            surf = pygame.Surface((90, 90), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 255, 255), (0, 0, 90, 90), border_radius=12)
            pygame.draw.rect(surf, (200, 200, 200), (0, 0, 90, 90), 2, border_radius=12)
            fnt  = pygame.font.SysFont("Arial", 42, bold=True)
            txt  = fnt.render(str(i), True, (30, 30, 30))
            surf.blit(txt, txt.get_rect(center=(45, 45)))
            dice_imgs.append(surf)
    return dice_imgs

# ─── Player token drawing ─────────────────────────────────────────────────────
def draw_token(surface, x, y, color, label, font):
    pygame.draw.circle(surface, (0, 0, 0), (x+2, y+2), 14)   # shadow
    pygame.draw.circle(surface, color, (x, y), 14)
    pygame.draw.circle(surface, (255, 255, 255), (x, y), 14, 2)
    lbl = font.render(label, True, TEXT_LIGHT)
    surface.blit(lbl, lbl.get_rect(center=(x, y)))

# ─── Game state ───────────────────────────────────────────────────────────────
class GameState:
    def __init__(self):
        self.positions   = [1, 1]          # P1, P2 start at cell 1
        self.turn        = 0               # 0=P1, 1=P2
        self.dice_val    = None
        self.log         = []
        self.winner      = None

        # Animation
        self.animating   = False
        self.anim_cell   = 1               # current visual cell during move
        self.anim_target = 1               # logical final cell (after snake/ladder)
        self.anim_steps  = []              # list of cells to walk through
        self.anim_idx    = 0
        self.anim_timer  = 0.0

        # Dice roll animation
        self.roll_anim   = False
        self.roll_frames = 0
        self.roll_display= None

    def roll_dice(self):
        if self.animating or self.winner:
            return
        self.roll_anim   = True
        self.roll_frames = 18              # ~0.3s at 60fps

    def _finish_roll(self):
        val  = random.randint(1, 6)
        self.dice_val = val
        cur  = self.positions[self.turn]
        dest = cur + val

        name = f"P{self.turn+1}"
        if dest > 100:
            self.log.append(f"{name} rolled {val} — no move (overshoot)")
            self._end_turn()
            return

        # Build walk path
        steps = list(range(cur + 1, dest + 1))

        # Check snake / ladder at destination
        final = dest
        if dest in SNAKES:
            final = SNAKES[dest]
            self.log.append(f"{name} rolled {val}: {cur}→{dest} 🐍→{final}")
        elif dest in LADDERS:
            final = LADDERS[dest]
            self.log.append(f"{name} rolled {val}: {cur}→{dest} 🪜→{final}")
        else:
            self.log.append(f"{name} rolled {val}: {cur}→{dest}")

        self.anim_steps  = steps
        self.anim_target = final
        self.anim_cell   = cur
        self.anim_idx    = 0
        self.anim_timer  = 0.0
        self.animating   = True

    def update(self, dt: float):
        # Dice roll animation
        if self.roll_anim:
            self.roll_frames -= 1
            self.roll_display = random.randint(0, 5)
            if self.roll_frames <= 0:
                self.roll_anim = False
                self._finish_roll()
            return

        if not self.animating:
            return

        self.anim_timer += dt
        step_dur = 1.0 / (ANIM_SPEED * 2)     # seconds per cell

        while self.anim_timer >= step_dur and self.animating:
            self.anim_timer -= step_dur
            if self.anim_idx < len(self.anim_steps):
                self.anim_cell = self.anim_steps[self.anim_idx]
                self.anim_idx += 1
            else:
                # Walking done — snap to final (snake/ladder destination)
                self.anim_cell = self.anim_target
                self.positions[self.turn] = self.anim_target
                self.animating = False
                if self.anim_target == 100:
                    self.winner = self.turn
                else:
                    self._end_turn()

    def _end_turn(self):
        self.turn = 1 - self.turn

# ─── Draw right panel ─────────────────────────────────────────────────────────
def draw_panel(surface, gs: GameState, dice_imgs, font, font_sm, font_xs):
    px = MARGIN + BOARD_SIZE + MARGIN
    py = MARGIN

    draw_rounded_rect(surface, PANEL_BG, (px-10, py-10, PANEL_W, WIN_H - MARGIN), radius=14)

    # Title
    title = font.render("Snakes & Ladders", True, TEXT_DARK)
    surface.blit(title, (px + PANEL_W//2 - title.get_width()//2 - 10, py + 4))

    # Player info boxes
    colors = [P1_COL, P2_COL]
    names  = ["Player 1", "Player 2"]
    for i in range(2):
        bx = px + (i * (PANEL_W // 2)) - 10
        by = py + 40
        active = gs.turn == i and not gs.winner
        border = HIGHLIGHT if active else PANEL_BG
        draw_rounded_rect(surface, border, (bx, by, PANEL_W//2 - 4, 54), radius=8)
        draw_rounded_rect(surface, colors[i], (bx+3, by+3, PANEL_W//2 - 10, 48), radius=6)
        nm  = font_sm.render(names[i], True, TEXT_LIGHT)
        pos = font_sm.render(f"Cell {gs.positions[i]}", True, TEXT_LIGHT)
        surface.blit(nm,  (bx+8, by+8))
        surface.blit(pos, (bx+8, by+28))

    # Dice
    dice_y = py + 110
    label  = font_sm.render("Dice", True, TEXT_DARK)
    surface.blit(label, (px + PANEL_W//2 - label.get_width()//2 - 10, dice_y))

    if gs.roll_anim and gs.roll_display is not None:
        surface.blit(dice_imgs[gs.roll_display],
                     (px + PANEL_W//2 - 55, dice_y + 22))
    elif gs.dice_val is not None:
        surface.blit(dice_imgs[gs.dice_val - 1],
                     (px + PANEL_W//2 - 55, dice_y + 22))
    else:
        placeholder = font.render("?", True, TEXT_DARK)
        surface.blit(placeholder, (px + PANEL_W//2 - placeholder.get_width()//2 - 10,
                                   dice_y + 40))

    # Roll button
    btn_x = px + PANEL_W//2 - 65
    btn_y = dice_y + 130
    mx, my = pygame.mouse.get_pos()
    hovering = btn_x <= mx <= btn_x+130 and btn_y <= my <= btn_y+40
    btn_col  = BTN_HOV if hovering else BTN_COL
    draw_rounded_rect(surface, btn_col, (btn_x, btn_y, 130, 40), radius=10)
    if gs.winner is not None:
        txt = font_sm.render("New Game", True, BTN_TXT)
    elif gs.animating or gs.roll_anim:
        txt = font_sm.render("Rolling…", True, BTN_TXT)
    else:
        txt = font_sm.render("Roll Dice", True, BTN_TXT)
    surface.blit(txt, txt.get_rect(center=(btn_x+65, btn_y+20)))

    # Log
    log_y = btn_y + 60
    log_lbl = font_sm.render("History", True, TEXT_DARK)
    surface.blit(log_lbl, (px, log_y))
    draw_rounded_rect(surface, (220, 212, 195),
                      (px-6, log_y+20, PANEL_W-4, WIN_H - MARGIN - log_y - 30),
                      radius=8)
    recent = gs.log[-10:]
    for j, entry in enumerate(reversed(recent)):
        col = P1_COL if "P1" in entry else P2_COL
        line = font_xs.render(entry[:30], True, col)
        surface.blit(line, (px, log_y + 26 + j * 18))

    # Winner banner
    if gs.winner is not None:
        draw_rounded_rect(surface, HIGHLIGHT,
                          (px - 10, WIN_H//2 - 40, PANEL_W, 70), radius=12)
        win_txt = font.render(f"P{gs.winner+1} Wins! 🎉", True, TEXT_DARK)
        surface.blit(win_txt, win_txt.get_rect(center=(px + PANEL_W//2 - 10, WIN_H//2 - 5)))

    return (btn_x, btn_y, 130, 40)   # return button rect for click detection

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snakes & Ladders")
    clock  = pygame.time.Clock()

    font    = pygame.font.SysFont("Georgia",     18, bold=True)
    font_sm = pygame.font.SysFont("Arial",       15, bold=True)
    font_xs = pygame.font.SysFont("Arial",       12)
    font_token = pygame.font.SysFont("Arial",    11, bold=True)

    dice_imgs = load_dice()
    gs        = GameState()

    # Pre-render static board layers onto a surface so we don't redraw each frame
    board_surf = pygame.Surface((WIN_W, WIN_H))
    board_surf.fill(BG)
    draw_board(board_surf, font_xs)
    draw_ladders(board_surf)
    draw_snakes(board_surf)

    btn_rect = (0, 0, 0, 0)

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bx, by, bw, bh = btn_rect
                if bx <= event.pos[0] <= bx+bw and by <= event.pos[1] <= by+bh:
                    if gs.winner is not None:
                        gs = GameState()             # restart
                    else:
                        gs.roll_dice()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if gs.winner is not None:
                        gs = GameState()
                    else:
                        gs.roll_dice()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        gs.update(dt)

        # Blit static board
        screen.blit(board_surf, (0, 0))

        # Draw tokens
        for i, cell in enumerate(gs.positions):
            draw_cell = gs.anim_cell if gs.animating and gs.turn == i else cell
            col       = P1_COL if i == 0 else P2_COL
            offset    = -16 if i == 0 else 16       # side-by-side offset when same cell
            if gs.positions[0] == gs.positions[1]:
                ox = offset
            else:
                ox = 0
            x, y = cell_to_pos(draw_cell)
            draw_token(screen, x + ox, y, col, f"P{i+1}", font_token)

        # Draw panel
        btn_rect = draw_panel(screen, gs, dice_imgs, font, font_sm, font_xs)

        pygame.display.flip()

if __name__ == "__main__":
    main()