<img width="673" height="509" alt="Screenshot 2026-09-20 at 10 27 35 PM" src="https://github.com/user-attachments/assets/1b201af6-7f8c-4bcd-af9c-1f77a3f6cb71" />
# Snakes & Ladders — Adaptive RL

A classic Snakes & Ladders game with a twist: the board isn't fixed. A trained
reinforcement-learning agent repositions snakes and ladders in real time as
you play, aiming to keep every game tense and winnable — never a runaway
lucky streak, never an unwinnable slog.

---

## How it works

Instead of a static board, an RL "director" watches the game every few turns
and decides whether to leave the board alone or move a snake or ladder closer
to (or further from) the player. It's trained offline with Q-learning, then
loaded at play time to make live decisions.

- **State:** player position (bucketed) + board changes remaining + agent goal
- **Action space:** `wait`, `ladder_near`, `snake_near`, `ladder_away`, `snake_away`
- **Reward:** shaped by turn-by-turn progress, with a bonus for steering the
  game toward a target length and a penalty for games that run too long
- **Algorithm:** tabular Q-learning with ε-greedy exploration, no external ML
  dependencies

The agent is capped at a small number of board changes per game and only
acts at fixed intervals, so the board stays recognizable as Snakes & Ladders
rather than constantly reshuffling under you.

---

## Minigames

A few tiles hand control to a minigame instead of a plain dice resolution:

| Tile(s) | Minigame        | Type          |
|---------|------------------|---------------|
| 10, 70  | Tic-tac-toe vs. a bot | Skill-based   |
| 30, 85  | Reaction-time click   | Mixed         |
| 50      | Coin flip             | Pure chance   |

Win → move 2 steps forward. Lose → move 1 step back.

---

## Project structure

```
snakes_and_ladder/
├── main.py            # Entry point — run a game
├── board.py            # Board state and snake/ladder resolution
├── constants.py         # Snake/ladder positions, challenge squares
├── dice.py              # Dice roll logic
├── ladder.py             # Ladder-specific movement logic
├── rl_director.py        # The Q-learning agent: state encoding, action
│                          # selection, board edits, training update rule
├── train_rl.py           # Runs simulated episodes to train the director
├── ai_simulator.py        # Simulates/evaluates agent behavior across games
├── assets/               # Game assets
├── data/                 # Saved Q-table + decision-log database (git-ignored)
└── mini_games/            # Minigame implementations
```

> This reflects the current state of the repo. An earlier version of this
> README described a `backend/`/`frontend`/`notebooks` layout with a FastAPI
> API and web frontend — that's the direction the project is heading in, not
> what's implemented yet. See [Roadmap](#roadmap).

---

## Setup

```bash
pip install -r requirements.txt
```

### 1. Train the agent

```bash
python train_rl.py
```

This runs a batch of simulated episodes and saves the learned Q-table to
`data/`. See `train_rl.py` for configurable options (episode count, target
goal, etc.).

### 2. Play

```bash
python main.py
```

---

## RL details

| | |
|---|---|
| State encoding | `f"{cell // 10}:{changes_left}:{goal}"` |
| Actions | 5 discrete actions (see above) |
| Max board changes per game | 3 |
| Decision interval | every 4 turns |
| Max turns per episode | 120 |
| Learning rate (α) | 0.12 |
| Discount factor (γ) | 0.96 |

Every director decision — goal, turn number, player position, action taken,
and a human-readable description — is logged to a SQLite database in `data/`
alongside the saved Q-table, so live games can be audited after the fact.

---

## Roadmap

- [ ] FastAPI backend exposing game/RL endpoints for a live web client
- [ ] Web frontend (board, dice, minigame UI)
- [ ] Training notebook with reward curves and evaluation plots
- [ ] Baseline comparison: RL-directed games vs. a static board

---

## License

No license specified yet.
