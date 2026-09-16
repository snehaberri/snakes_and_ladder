import os
import random
import sys
import asyncio

import pygame

import board
from dice import roll_dice
from rl_director import DECISION_INTERVAL, MAX_CHANGES, MAX_TURNS, QDirector, apply_action, log_decision
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, BOARD_AREA, BACKGROUND, PANEL_BG,
    TEXT_COL, BUTTON_COL, BUTTON_HOVER, BUTTON_TEXT, PLAYER_COLORS, SNAKES,
    LADDERS, CHALLENGE_SQUARES, TIC_TAC_TOE_COL, REACTION_COL,
)

MOVE_DELAY_MS = 160
PAUSE_MS = 350
ROLL_DURATION_MS = 700
ROLL_FRAME_MS = 65


class Player:
    def __init__(self):
        self.name, self.color, self.cell, self.won = "Player 1", PLAYER_COLORS[0], 0, False


class Game:
    def __init__(self):
        self.player = Player()
        self.last_roll = None
        self.pending_roll, self.roll_started_at, self.roll_seed = None, None, 0
        self.roll_shift = None
        self.activity = ["Game started — roll the dice."]
        self.message = "Roll the dice to start your adventure."
        self.state = "WAITING_ROLL"
        self._queue, self._timer = [], 0
        self.tic_board, self.tic_result = [None] * 9, None
        self.reaction_started, self.reaction_ready_at = None, None
        self.snakes, self.ladders = dict(SNAKES), dict(LADDERS)
        self.turns, self.changes_left = 0, MAX_CHANGES
        self.ai_goal = os.environ.get("BOARD_AI_GOAL", "help").lower()
        if self.ai_goal not in ("help", "hinder"):
            self.ai_goal = "help"
        self.director = QDirector.load(self.ai_goal)

    def roll_dice(self):
        if self.state != "WAITING_ROLL":
            return
        self.turns += 1
        self.roll_shift = self._direct_board()
        self.pending_roll = roll_dice()
        self.roll_started_at = pygame.time.get_ticks()
        self.roll_seed = random.randrange(6)
        self.state = "ROLLING"
        self.message = "Rolling the dice..."

    def _finish_roll(self):
        self.last_roll = self.pending_roll
        target = self.player.cell + self.last_roll
        if target > 100:
            self.message = f"{self.roll_shift + ' ' if self.roll_shift else ''}You rolled {self.last_roll}. You need an exact roll to reach 100."
            self._add_activity(f"Rolled {self.last_roll}: exact roll needed.")
            self.state = "WAITING_ROLL"
            self._timeout_check()
            return
        self._add_activity(f"Rolled {self.last_roll}: moving to {target}.")
        self._start_move(target, f"{self.roll_shift + ' ' if self.roll_shift else ''}You rolled {self.last_roll}.")

    def die_face(self):
        if self.state == "ROLLING":
            elapsed = pygame.time.get_ticks() - self.roll_started_at
            return (self.roll_seed + elapsed // ROLL_FRAME_MS) % 6 + 1
        return self.last_roll

    def _add_activity(self, event):
        self.activity.insert(0, event)
        self.activity = self.activity[:5]

    def _direct_board(self):
        if not self.director or not self.changes_left or (self.turns - 1) % DECISION_INTERVAL:
            return None
        action = self.director.choose(self.player.cell, self.changes_left)
        description = apply_action(self.snakes, self.ladders, self.player.cell, action)
        if description:
            self.changes_left -= 1
            log_decision(self.ai_goal, self.turns, self.player.cell, action, description)
            self._add_activity(f"RL chose {action}: {description[3:]}")
            return description + "."
        self._add_activity(f"RL chose {action}: board unchanged.")
        return None

    def _timeout_check(self):
        if self.turns >= MAX_TURNS and not self.player.won:
            self.state = "GAME_OVER"
            self.message = "The board outlasted you after 120 rolls. Try again!"

    def _start_move(self, target, message):
        target = max(0, min(100, target))
        step = 1 if target >= self.player.cell else -1
        self._queue = list(range(self.player.cell + step, target + step, step))
        self._timer = pygame.time.get_ticks()
        self.state, self.message = "MOVING", message

    def tick(self):
        now = pygame.time.get_ticks()
        if self.state == "ROLLING":
            if now - self.roll_started_at >= ROLL_DURATION_MS:
                self._finish_roll()
        elif self.state == "MOVING" and now - self._timer >= MOVE_DELAY_MS:
            if self._queue:
                self.player.cell = self._queue.pop(0)
                self._timer = now
            else:
                self._land()
        elif self.state == "PAUSE" and now - self._timer >= PAUSE_MS:
            self._land(check_square=False)

    def _land(self, check_square=True):
        p = self.player
        if p.cell >= 100:
            p.cell, p.won, self.state, self.message = 100, True, "GAME_OVER", "You reached 100 — you win!"
            self._add_activity("You reached square 100 — you win!")
        elif check_square and p.cell in self.snakes:
            start = p.cell
            p.cell, self.state, self._timer = self.snakes[p.cell], "PAUSE", pygame.time.get_ticks()
            self.message = f"A snake! Slide down to {p.cell}."
            self._add_activity(f"Snake: {start} → {p.cell}.")
        elif check_square and p.cell in self.ladders:
            start = p.cell
            p.cell, self.state, self._timer = self.ladders[p.cell], "PAUSE", pygame.time.get_ticks()
            self.message = f"A ladder! Climb up to {p.cell}."
            self._add_activity(f"Ladder: {start} → {p.cell}.")
        elif check_square and p.cell in CHALLENGE_SQUARES:
            if CHALLENGE_SQUARES[p.cell] == "tic_tac_toe":
                self.state, self.tic_board = "TIC_TAC_TOE", [None] * 9
                self.message = "Tic-tac-toe: make three Xs to move +2; otherwise -1."
                self._add_activity(f"Star tile {p.cell}: tic-tac-toe.")
            else:
                self.state = "REACTION_WAIT"
                self.reaction_started = pygame.time.get_ticks()
                self.reaction_ready_at = self.reaction_started + random.randint(1200, 2600)
                self.message = "Reaction test: wait for green, then click. Under 0.35 sec = +2; otherwise -1."
                self._add_activity(f"Star tile {p.cell}: reaction test.")
        else:
            self.state, self.message = "WAITING_ROLL", "Roll the dice."
            self._timeout_check()

    def tic_click(self, pos, modal):
        if self.state != "TIC_TAC_TOE" or not modal.collidepoint(pos):
            return
        cell_w, cell_h = modal.width // 3, modal.height // 3
        col, row = (pos[0] - modal.x) // cell_w, (pos[1] - modal.y) // cell_h
        index = row * 3 + col
        if self.tic_board[index] is not None:
            return
        self.tic_board[index] = "X"
        if self._winner() == "X":
            self._challenge_result(True, "You won tic-tac-toe! Move 2 steps forward.")
            return
        if None not in self.tic_board:
            self._challenge_result(False, "Tic-tac-toe draw. Move 1 step back.")
            return
        bot_cell = self._best_tic_move()
        if bot_cell is not None:
            self.tic_board[bot_cell] = "O"
        if self._winner() == "O" or None not in self.tic_board:
            self._challenge_result(False, "Tic-tac-toe lost or drawn. Move 1 step back.")

    def _best_tic_move(self):
        """Choose the strongest available move for O using minimax."""
        def minimax(board, maximizing, depth):
            winner = self._winner_for(board)
            if winner == "O":
                return 10 - depth
            if winner == "X":
                return depth - 10
            empty = [i for i, mark in enumerate(board) if mark is None]
            if not empty:
                return 0

            scores = []
            for cell in empty:
                board[cell] = "O" if maximizing else "X"
                scores.append(minimax(board, not maximizing, depth + 1))
                board[cell] = None
            return max(scores) if maximizing else min(scores)

        empty = [i for i, mark in enumerate(self.tic_board) if mark is None]
        if not empty:
            return None
        best_score = float("-inf")
        best_cell = empty[0]
        for cell in empty:
            self.tic_board[cell] = "O"
            score = minimax(self.tic_board, False, 1)
            self.tic_board[cell] = None
            if score > best_score:
                best_score, best_cell = score, cell
        return best_cell

    def _winner_for(self, board):
        for a, b, c in ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)):
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def _winner(self):
        return self._winner_for(self.tic_board)

    def reaction_click(self):
        if self.state not in ("REACTION_WAIT", "REACTION_READY"):
            return
        now = pygame.time.get_ticks()
        if self.state == "REACTION_WAIT" and now < self.reaction_ready_at:
            self._challenge_result(False, "Too early! Move 1 step back.")
        else:
            seconds = (now - self.reaction_ready_at) / 1000
            self._challenge_result(seconds < .35, f"Reaction: {seconds:.3f}s. " + ("Move 2 steps forward!" if seconds < .35 else "Move 1 step back."))

    def _challenge_result(self, won, message):
        self._add_activity("Challenge won: +2 squares." if won else "Challenge lost: -1 square.")
        self._start_move(self.player.cell + (2 if won else -1), message)

    def reset(self):
        self.__init__()


def wrap(text, font, width):
    lines, line = [], ""
    for word in text.split():
        proposal = f"{line} {word}".strip()
        if line and font.size(proposal)[0] > width:
            lines.append(line); line = word
        else: line = proposal
    return lines + ([line] if line else [])


def draw_panel(screen, game, fonts, button, mouse, dice_images):
    title, normal, small = fonts
    pygame.draw.rect(screen, PANEL_BG, (BOARD_AREA, 0, screen.get_width()-BOARD_AREA, screen.get_height()))
    screen.blit(title.render("Snakes & Ladders", True, TEXT_COL), (BOARD_AREA + 18, 24))
    pygame.draw.circle(screen, game.player.color, (BOARD_AREA + 31, 95), 10)
    screen.blit(normal.render(f"Player: square {game.player.cell}", True, TEXT_COL), (BOARD_AREA + 50, 84))
    screen.blit(small.render("Dice", True, TEXT_COL), (BOARD_AREA + 20, 124))
    face = game.die_face()
    if face:
        die = dice_images[face - 1]
        if game.state == "ROLLING":
            elapsed = pygame.time.get_ticks() - game.roll_started_at
            angle = 12 if (elapsed // ROLL_FRAME_MS) % 2 else -12
            scale = 1.12 if (elapsed // (ROLL_FRAME_MS * 2)) % 2 else 0.96
            die = pygame.transform.rotozoom(die, angle, scale)
        screen.blit(die, die.get_rect(center=(BOARD_AREA + 130, 188)))
    else:
        pygame.draw.rect(screen, (210, 210, 210), (BOARD_AREA + 90, 148, 80, 80), border_radius=10)
        screen.blit(normal.render("?", True, BUTTON_TEXT), normal.render("?", True, BUTTON_TEXT).get_rect(center=(BOARD_AREA + 130, 188)))
    screen.blit(small.render(f"Board AI: {game.ai_goal} ({game.changes_left} shifts)", True, TEXT_COL), (BOARD_AREA + 20, 245))
    screen.blit(small.render("Pink: tic-tac-toe", True, TIC_TAC_TOE_COL), (BOARD_AREA + 20, 267))
    screen.blit(small.render("Blue: reaction test", True, REACTION_COL), (BOARD_AREA + 20, 289))
    y = 325
    for line in wrap(game.message, small, screen.get_width() - BOARD_AREA - 38):
        screen.blit(small.render(line, True, TEXT_COL), (BOARD_AREA + 20, y)); y += 22
    y = max(y + 10, 395)
    screen.blit(small.render("Game activity", True, (255, 215, 0)), (BOARD_AREA + 20, y))
    y += 22
    for event in game.activity[:4]:
        for line in wrap(f"• {event}", small, screen.get_width() - BOARD_AREA - 38):
            screen.blit(small.render(line, True, TEXT_COL), (BOARD_AREA + 20, y)); y += 18
        y += 4
    color = BUTTON_HOVER if button.collidepoint(mouse) else BUTTON_COL
    pygame.draw.rect(screen, color, button, border_radius=8)
    label = "Play Again" if game.state == "GAME_OVER" else ("Roll Dice" if game.state == "WAITING_ROLL" else ("Rolling..." if game.state == "ROLLING" else "Challenge in progress"))
    screen.blit(normal.render(label, True, BUTTON_TEXT), normal.render(label, True, BUTTON_TEXT).get_rect(center=button.center))


def draw_tic(screen, game, font):
    box = pygame.Rect(170, 170, 440, 440)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((0, 0, 0, 175)); screen.blit(overlay, (0, 0))
    pygame.draw.rect(screen, (55, 30, 75), box, border_radius=14)
    for n in (1, 2):
        pygame.draw.line(screen, TEXT_COL, (box.x+n*box.width//3, box.y), (box.x+n*box.width//3, box.bottom), 3)
        pygame.draw.line(screen, TEXT_COL, (box.x, box.y+n*box.height//3), (box.right, box.y+n*box.height//3), 3)
    for i, mark in enumerate(game.tic_board):
        if mark:
            text = font.render(mark, True, TIC_TAC_TOE_COL if mark == "X" else REACTION_COL)
            rect = text.get_rect(center=(box.x+(i%3)*box.width//3+box.width//6, box.y+(i//3)*box.height//3+box.height//6))
            screen.blit(text, rect)
    return box


def draw_reaction(screen, game, fonts):
    title, normal, _ = fonts
    ready = pygame.time.get_ticks() >= game.reaction_ready_at
    game.state = "REACTION_READY" if ready else "REACTION_WAIT"
    colour = (45, 175, 80) if ready else (185, 55, 55)
    pygame.draw.rect(screen, colour, (110, 230, 560, 290), border_radius=16)
    message = "CLICK NOW!" if ready else "Wait for green..."
    screen.blit(title.render("Reaction Time", True, TEXT_COL), title.render("Reaction Time", True, TEXT_COL).get_rect(center=(390, 285)))
    screen.blit(normal.render(message, True, TEXT_COL), normal.render(message, True, TEXT_COL).get_rect(center=(390, 390)))


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)); pygame.display.set_caption("Solo Snakes & Ladders")
    clock = pygame.time.Clock(); fonts = (pygame.font.SysFont("arial", 26, bold=True), pygame.font.SysFont("arial", 20), pygame.font.SysFont("arial", 14))
    dice_images = [pygame.transform.smoothscale(pygame.image.load(f"assets/dice/{face}.png").convert_alpha(), (80, 80)) for face in range(1, 7)]
    game, running = Game(), True
    button = pygame.Rect(BOARD_AREA + 20, WINDOW_HEIGHT - 80, 215, 50)
    auto = os.environ.get("AUTO_TEST") == "1"; frames = 0
    while running:
        tic_box = pygame.Rect(170, 170, 440, 440)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: game.roll_dice()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "TIC_TAC_TOE": game.tic_click(event.pos, tic_box)
                elif game.state in ("REACTION_WAIT", "REACTION_READY"): game.reaction_click()
                elif button.collidepoint(event.pos): game.reset() if game.state == "GAME_OVER" else game.roll_dice()
        if auto and game.state == "WAITING_ROLL": game.roll_dice()
        game.tick(); screen.fill(BACKGROUND); board.draw_board(screen, fonts[2]); board.draw_ladders(screen, game.ladders); board.draw_snakes(screen, game.snakes)
        if game.player.cell: pygame.draw.circle(screen, game.player.color, board.cell_to_pos(game.player.cell), 11); pygame.draw.circle(screen, (0,0,0), board.cell_to_pos(game.player.cell), 11, 1)
        draw_panel(screen, game, fonts, button, pygame.mouse.get_pos(), dice_images)
        if game.state == "TIC_TAC_TOE": draw_tic(screen, game, fonts[0])
        elif game.state in ("REACTION_WAIT", "REACTION_READY"): draw_reaction(screen, game, fonts)
        pygame.display.flip(); clock.tick(FPS); frames += 1
        if auto and (game.player.won or frames > 5000): running = False
        pygame.display.flip(); frames += 1
        if auto and (game.player.won or frames > 5000): running = False
        clock.tick(FPS)
        await asyncio.sleep(0)
    pygame.quit(); sys.exit()


asyncio.run(main())
