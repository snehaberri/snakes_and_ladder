import json
import random
import time
from pathlib import Path

import pygame


def _save_state(state, save_path):
    if not save_path:
        return
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def tic_tac_toe(save_path="data/tic_tac_toe_state.json"):
    width, height = 600, 600
    line_color = "#ffb3b3"
    bg_color = "#4d0000"
    x_color = "#ffd1ae"
    o_color = "#ffcce5"
    line_width = 5
    cross_width = 15
    circle_width = 15
    cell_size = width // 3

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mini-Game: Tic Tac Toe")
    clock = pygame.time.Clock()

    def new_board():
        return [None] * 9

    def draw_grid():
        pygame.draw.line(screen, line_color, (cell_size, 0), (cell_size, height), line_width)
        pygame.draw.line(screen, line_color, (cell_size * 2, 0), (cell_size * 2, height), line_width)
        pygame.draw.line(screen, line_color, (0, cell_size), (width, cell_size), line_width)
        pygame.draw.line(screen, line_color, (0, cell_size * 2), (width, cell_size * 2), line_width)

    def draw_x(cell_index):
        row = cell_index // 3
        col = cell_index % 3
        padding = cell_size // 6
        x1 = col * cell_size + padding
        y1 = row * cell_size + padding
        x2 = (col + 1) * cell_size - padding
        y2 = (row + 1) * cell_size - padding
        pygame.draw.line(screen, x_color, (x1, y1), (x2, y2), cross_width)
        pygame.draw.line(screen, x_color, (x1, y2), (x2, y1), cross_width)

    def draw_o(cell_index):
        row = cell_index // 3
        col = cell_index % 3
        center = (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2)
        radius = cell_size // 3
        pygame.draw.circle(screen, o_color, center, radius, circle_width)

    def draw_board(board):
        screen.fill(bg_color)
        draw_grid()
        for i, mark in enumerate(board):
            if mark == "X":
                draw_x(i)
            elif mark == "O":
                draw_o(i)
        pygame.display.update()

    def check_winner(board):
        wins = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6],
        ]
        for combo in wins:
            if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
                return board[combo[0]]
        return None

    def get_empty_cells(board):
        return [i for i, cell in enumerate(board) if cell is None]

    board = new_board()
    current_player = "X"
    game_over = False
    winner = None
    player_reaction_times_ms = []
    player_turn_started_at = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = {
                    "mini_game": "tic_tac_toe",
                    "result": "quit",
                    "winner": None,
                    "board": board,
                    "moves_played": sum(1 for cell in board if cell is not None),
                    "player_reaction_times_ms": player_reaction_times_ms,
                    "avg_player_reaction_ms": (
                        int(sum(player_reaction_times_ms) / len(player_reaction_times_ms))
                        if player_reaction_times_ms
                        else None
                    ),
                    "completed_at": int(time.time()),
                }
                _save_state(state, save_path)
                return state

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and current_player == "X":
                col = pygame.mouse.get_pos()[0] // cell_size
                row = pygame.mouse.get_pos()[1] // cell_size
                cell_index = row * 3 + col

                if cell_index in get_empty_cells(board):
                    player_reaction_times_ms.append(int((time.time() - player_turn_started_at) * 1000))
                    board[cell_index] = "X"

                    if check_winner(board):
                        winner = "X"
                        game_over = True
                    elif not get_empty_cells(board):
                        game_over = True
                    else:
                        current_player = "O"

        if current_player == "O" and not game_over:
            pygame.time.wait(500)
            bot_cell = random.choice(get_empty_cells(board))
            board[bot_cell] = "O"

            if check_winner(board):
                winner = "O"
                game_over = True
            elif not get_empty_cells(board):
                game_over = True
            else:
                current_player = "X"
                player_turn_started_at = time.time()

        draw_board(board)

        if game_over:
            if winner == "X":
                result = "player_win"
            elif winner == "O":
                result = "bot_win"
            else:
                result = "draw"

            state = {
                "mini_game": "tic_tac_toe",
                "result": result,
                "winner": winner,
                "board": board,
                "moves_played": sum(1 for cell in board if cell is not None),
                "player_reaction_times_ms": player_reaction_times_ms,
                "avg_player_reaction_ms": (
                    int(sum(player_reaction_times_ms) / len(player_reaction_times_ms))
                    if player_reaction_times_ms
                    else None
                ),
                "completed_at": int(time.time()),
            }
            _save_state(state, save_path)
            return state

        clock.tick(60)


if __name__ == "__main__":
    print(tic_tac_toe())
