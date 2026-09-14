"""Train the board director from simulated bot games.

Usage: python3 train_rl.py --episodes 30000
"""
import argparse
import sqlite3

from rl_director import DATABASE_PATH, MODEL_PATH, QDirector, simulate_episode


def historical_games():
    if not DATABASE_PATH.exists():
        return 0
    with sqlite3.connect(DATABASE_PATH) as connection:
        return connection.execute("SELECT COUNT(*) FROM games").fetchone()[0]


def train(goal, episodes):
    agent = QDirector(goal)
    wins = sum(simulate_episode(agent) for _ in range(episodes))
    return agent, wins


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=30000)
    arguments = parser.parse_args()
    if arguments.episodes < 1:
        parser.error("--episodes must be positive")
    models = {}
    for goal in ("help", "hinder"):
        agent, successes = train(goal, arguments.episodes)
        models[goal] = agent.q_values
        print(f"{goal}: {successes}/{arguments.episodes} desired outcomes")
    QDirector("help", models["help"]).save(MODEL_PATH)
    # Store both policies in one model file.
    import json
    MODEL_PATH.write_text(json.dumps({"help": models["help"], "hinder": models["hinder"]}, separators=(",", ":")))
    print(f"Existing {historical_games()} bot-game records retained; saved policy to {MODEL_PATH}.")
