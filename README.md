# Snakes & Ladders — Adaptive RL

A Snakes and Ladders game where the board reconfigures in real-time.
A trained RL agent repositions snakes and ladders after every turn
to maximise game tension — keeping the player engaged, never making
it feel impossible.

---

## Project Structure

```
snakes-rl/
├── backend/
│   ├── game/
│   │   ├── board.py        # Board state + snake/ladder repositioning
│   │   ├── state.py        # Player state, minigame types/results
│   │   └── engine.py       # Turn logic, dice rolls, minigame resolution
│   ├── rl/
│   │   ├── environment.py  # Gymnasium env — used for training
│   │   ├── configs.py      # Pre-defined board layouts (agent's action space)
│   │   ├── train.py        # Q-learning training loop (10k episodes)
│   │   ├── agent.py        # Loads Q-table, picks config during live games
│   │   └── q_table.npy     # Saved after training (git-ignored)
│   ├── api/
│   │   └── routes.py       # FastAPI endpoints
│   └── main.py             # App entry point
├── frontend/
│   └── src/
│       ├── components/     # Board, Dice, MiniGame components
│       └── pages/          # Game page
├── notebooks/
│   └── explore.ipynb       # Training analysis + reward curves
└── requirements.txt
```

---

## Setup

```bash
pip install -r requirements.txt
```

## Step 1 — Train the agent

```bash
python -m backend.rl.train --episodes 10000
```

Saves `q_table.npy` to `backend/rl/`. Takes ~30 seconds.

## Step 2 — Run the API

```bash
uvicorn backend.main:app --reload
```

API available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

## Step 3 — Run the frontend

```bash
cd frontend
npm install
npm run dev
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/game/new` | Start a new game |
| POST | `/game/{id}/roll` | Roll dice + agent adapts board |
| POST | `/game/{id}/minigame` | Submit minigame result (`win`/`loss`) |
| GET | `/game/{id}/state` | Get current game state |
| DELETE | `/game/{id}` | End session |

---

## How the RL works

The agent trains on the `SnakesLaddersEnv` Gymnasium environment.

- **State:** `(player_position, win_rate_bucket)` — 101 × 5 = 505 states
- **Action:** pick one of 6 pre-defined board configurations
- **Reward:** +1 per turn alive, +5 bonus for finishing near 30 turns, -2 for games exceeding 60 turns
- **Algorithm:** Q-learning with ε-greedy exploration

After training, the Q-table is a `(101, 5, 6)` array. During a live game,
the agent looks up `Q[position][win_bucket]` and picks the config with
the highest value — repositioning the board before each roll.

---

## Minigames

| Tile(s) | Type | Mechanic |
|---------|------|----------|
| 10, 70 | Tic-tac-toe | Play against a bot — skill-based |
| 30, 85 | Reaction time | Click within a window — mixed |
| 50 | Chance | Coin flip — pure random |

Win → 2 steps forward. Loss → 1 step back.
