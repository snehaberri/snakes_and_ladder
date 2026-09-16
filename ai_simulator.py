"""Run automated solo games and save an audit trail in SQLite.

Usage: python3 ai_simulator.py
This appends 120 bot-played games to ``data/snakes_ladders.sqlite3`` by default.
"""

import argparse
import random
import sqlite3
from pathlib import Path

from constants import CHALLENGE_SQUARES, LADDERS, SNAKES
from dice import roll_dice

DATABASE_PATH = Path("data/snakes_ladders.sqlite3")
GAMES_PER_RUN = 10000


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            turns INTEGER NOT NULL DEFAULT 0,
            final_cell INTEGER,
            won INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL REFERENCES games(id),
            turn_number INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            from_cell INTEGER NOT NULL,
            to_cell INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            dice_value INTEGER,
            details TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_moves_game ON moves(game_id, turn_number, step_number);
    """)


def record_move(cursor, game_id, turn, step, start, end, event, dice_value=None, details=None):
    """Save one physical step or a zero-distance game event."""
    cursor.execute(
        """INSERT INTO moves
           (game_id, turn_number, step_number, from_cell, to_cell, event_type, dice_value, details)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (game_id, turn, step, start, end, event, dice_value, details),
    )


def walk(cursor, game_id, turn, step, cell, destination, event, dice_value=None):
    """Walk cell by cell, recording every individual board movement."""
    direction = 1 if destination >= cell else -1
    for next_cell in range(cell + direction, destination + direction, direction):
        step += 1
        record_move(cursor, game_id, turn, step, cell, next_cell, event, dice_value)
        cell = next_cell
    return cell, step


def play_tic_tac_toe_bot() -> bool:
    """Play X as a minimax bot against a random O opponent."""
    cells, wins = [None] * 9, ((0, 1, 2), (3, 4, 5), (6, 7, 8),
                                (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
    def winner(board):
        for a, b, c in wins:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def minimax(maximizing, depth):
        result = winner(cells)
        if result == "X":
            return 10 - depth
        if result == "O":
            return depth - 10
        open_cells = [index for index, value in enumerate(cells) if value is None]
        if not open_cells:
            return 0
        scores = []
        for index in open_cells:
            cells[index] = "X" if maximizing else "O"
            scores.append(minimax(not maximizing, depth + 1))
            cells[index] = None
        return max(scores) if maximizing else min(scores)

    for turn in range(9):
        open_cells = [index for index, value in enumerate(cells) if value is None]
        if not open_cells:
            return False
        if turn % 2 == 0:
            best_cell, best_score = open_cells[0], float("-inf")
            for index in open_cells:
                cells[index] = "X"
                score = minimax(False, 1)
                cells[index] = None
                if score > best_score:
                    best_cell, best_score = index, score
            cells[best_cell] = "X"
        else:
            cells[random.choice(open_cells)] = "O"
        if winner(cells):
            return winner(cells) == "X"
    return False


def play_one_game(connection: sqlite3.Connection) -> int:
    cursor = connection.cursor()
    cursor.execute("INSERT INTO games DEFAULT VALUES")
    game_id, cell, turns = cursor.lastrowid, 0, 0

    while cell < 100:
        turns += 1
        step = 0
        die = roll_dice()
        if cell + die > 100:
            record_move(cursor, game_id, turns, step, cell, cell, "exact_roll_miss", die,
                        "Roll would pass square 100")
            continue

        cell, step = walk(cursor, game_id, turns, step, cell, cell + die, "dice_step", die)

        # These are intentionally mutually exclusive, matching the interactive game's landing rules.
        if cell in SNAKES:
            destination = SNAKES[cell]
            step += 1
            record_move(cursor, game_id, turns, step, cell, destination, "snake")
            cell = destination
        elif cell in LADDERS:
            destination = LADDERS[cell]
            step += 1
            record_move(cursor, game_id, turns, step, cell, destination, "ladder")
            cell = destination
        elif cell in CHALLENGE_SQUARES:
            challenge = CHALLENGE_SQUARES[cell]
            if challenge == "tic_tac_toe":
                won = play_tic_tac_toe_bot()
                result = "win" if won else "loss_or_draw"
                details, change = f"tic_tac_toe:{result}", 2 if won else -1
            else:
                reaction = max(0.05, random.gauss(0.30, 0.09))
                won = reaction < 0.35
                details, change = f"reaction_time:{reaction:.3f}s", 2 if won else -1
            step += 1
            record_move(cursor, game_id, turns, step, cell, cell, "challenge_result", None, details)
            cell, step = walk(cursor, game_id, turns, step, cell, max(0, min(100, cell + change)), "challenge_move")

    cursor.execute(
        "UPDATE games SET completed_at = CURRENT_TIMESTAMP, turns = ?, final_cell = ?, won = 1 WHERE id = ?",
        (turns, cell, game_id),
    )
    return game_id


def run_simulation(game_count: int = GAMES_PER_RUN, database_path: Path = DATABASE_PATH, append: bool = False) -> None:
    """Record an exact fresh batch unless ``append`` is explicitly requested."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        create_schema(connection)
        if not append:
            # Delete dependent rows first.  This makes the database contain exactly
            # ``game_count`` games after a normal simulation run.
            connection.execute("DELETE FROM moves")
            connection.execute("DELETE FROM games")
        ids = [play_one_game(connection) for _ in range(game_count)]
        connection.commit()
        move_count = connection.execute("SELECT COUNT(*) FROM moves").fetchone()[0]
    print(f"Recorded exactly {game_count} bot games and {move_count} movements in {database_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record automated Snakes & Ladders games in SQLite.")
    parser.add_argument("--games", type=int, default=GAMES_PER_RUN, help="number of games to record (default: %(default)s)")
    parser.add_argument("--append", action="store_true", help="add to existing rows instead of replacing them")
    arguments = parser.parse_args()
    if arguments.games < 1:
        parser.error("--games must be at least 1")
    run_simulation(arguments.games, append=arguments.append)
