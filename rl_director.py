"""Dependency-free Q-learning board director for Snakes & Ladders."""

import json
import random
from pathlib import Path

from constants import CHALLENGE_SQUARES, LADDERS, SNAKES
from dice import roll_dice

MODEL_PATH = Path("data/board_director_q.json")
DATABASE_PATH = Path("data/snakes_ladders.sqlite3")
ACTIONS = ("wait", "ladder_near", "snake_near", "ladder_away", "snake_away")
DECISION_INTERVAL = 4
MAX_TURNS = 120
MAX_CHANGES = 3


def state_key(cell, changes_left, goal):
    return f"{cell // 10}:{changes_left}:{goal}"


def _valid_square(square, occupied):
    return 2 <= square <= 99 and square not in occupied and square not in CHALLENGE_SQUARES


def apply_action(snakes, ladders, cell, action):
    """Move one board feature, returning a readable description or ``None``."""
    if action == "wait":
        return None
    target = ladders if action.startswith("ladder") else snakes
    if not target:
        return None
    old_start, old_end = sorted(target.items())[0]
    occupied = set(snakes) | set(snakes.values()) | set(ladders) | set(ladders.values())
    direction = 1 if target is ladders else -1
    near = action.endswith("near")
    base, span = (4, 24) if near else (28, 10)
    # Nearby squares may be challenge squares or existing endpoints.  Search a
    # small deterministic neighbourhood so every valid decision visibly shifts
    # the board instead of silently failing.
    for offset in (0, 3, -3, 6, -6, 9, -9, 12, -12):
        proposed_start = max(2, min(98, cell + base + offset))
        proposed_end = max(2, min(99, proposed_start + direction * span))
        available = occupied - {old_start, old_end}
        if not _valid_square(proposed_start, available) or not _valid_square(proposed_end, available):
            continue
        if (target is ladders and proposed_end <= proposed_start) or (target is snakes and proposed_end >= proposed_start):
            continue
        del target[old_start]
        target[proposed_start] = proposed_end
        kind = "ladder" if target is ladders else "snake"
        return f"AI moved {kind} {old_start}→{old_end} to {proposed_start}→{proposed_end}"
    return None


class QDirector:
    def __init__(self, goal="help", q_values=None):
        self.goal = goal
        self.q_values = q_values or {}

    def choose(self, cell, changes_left, explore=0.0):
        key = state_key(cell, changes_left, self.goal)
        if random.random() < explore or key not in self.q_values:
            return random.choice(ACTIONS)
        values = self.q_values[key]
        best = max(values)
        return ACTIONS[random.choice([index for index, value in enumerate(values) if value == best])]

    def update(self, state, action, reward, next_state, done, alpha=0.12, gamma=0.96):
        values = self.q_values.setdefault(state, [0.0] * len(ACTIONS))
        next_values = self.q_values.setdefault(next_state, [0.0] * len(ACTIONS))
        index = ACTIONS.index(action)
        target = reward if done else reward + gamma * max(next_values)
        values[index] += alpha * (target - values[index])

    def save(self, path=MODEL_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"q_values": self.q_values}, separators=(",", ":")))

    @classmethod
    def load(cls, goal="help", path=MODEL_PATH):
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return cls(goal, data.get(goal, data.get("q_values", {})))


def log_decision(goal, turn, cell, action, description):
    """Keep the live game's board shifts beside the bot movement history."""
    import sqlite3
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS director_decisions (
            id INTEGER PRIMARY KEY, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            goal TEXT NOT NULL, turn_number INTEGER NOT NULL, player_cell INTEGER NOT NULL,
            action TEXT NOT NULL, description TEXT NOT NULL)""")
        connection.execute("INSERT INTO director_decisions (goal, turn_number, player_cell, action, description) VALUES (?, ?, ?, ?, ?)",
                           (goal, turn, cell, action, description))


def simulate_episode(agent, train=True):
    """One RL episode. `hinder` wins when the player times out at 120 turns."""
    snakes, ladders = dict(SNAKES), dict(LADDERS)
    cell, turns, changes_left = 0, 0, MAX_CHANGES
    previous_state, previous_action = None, None
    while turns < MAX_TURNS and cell < 100:
        turns += 1
        if changes_left and turns % DECISION_INTERVAL == 1:
            state = state_key(cell, changes_left, agent.goal)
            action = agent.choose(cell, changes_left, explore=0.14 if train else 0)
            if apply_action(snakes, ladders, cell, action):
                changes_left -= 1
            if previous_state is not None and train:
                agent.update(previous_state, previous_action, 0, state, False)
            previous_state, previous_action = state, action
        before, die = cell, roll_dice()
        if cell + die <= 100:
            cell += die
            if cell in snakes:
                cell = snakes[cell]
            elif cell in ladders:
                cell = ladders[cell]
            elif cell in CHALLENGE_SQUARES:
                cell = max(0, min(100, cell + (2 if random.random() < .55 else -1)))
        direction = 1 if agent.goal == "help" else -1
        reward = direction * (cell - before) / 25
        if previous_state is not None and train:
            next_state = state_key(cell, changes_left, agent.goal)
            agent.update(previous_state, previous_action, reward, next_state, False)
    success = (cell >= 100) if agent.goal == "help" else (cell < 100)
    if previous_state is not None and train:
        agent.update(previous_state, previous_action, 20 if success else -20,
                     state_key(cell, changes_left, agent.goal), True)
    return success
