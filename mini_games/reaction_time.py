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


def reaction_time(save_path="data/reaction_state.json"):
    pygame.init()

    width, height = 600, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Reaction Speed Test")

    red = (200, 0, 0)
    green = (0, 200, 0)
    black = (0, 0, 0)
    white = (255, 255, 255)

    font = pygame.font.Font(None, 48)
    clock = pygame.time.Clock()

    def draw_text(text, color, y):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(width // 2, y))
        screen.blit(rendered, rect)

    wait_time = random.uniform(2, 5)
    wait_start = time.time()
    ready = False
    start_time = None

    while True:
        screen.fill(red if not ready else green)
        draw_text("Wait for GREEN..." if not ready else "CLICK!", white if not ready else black, height // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = {
                    "mini_game": "reaction_time",
                    "result": "quit",
                    "reaction_ms": None,
                    "wait_time_s": round(wait_time, 3),
                    "completed_at": int(time.time()),
                }
                _save_state(state, save_path)
                return state

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not ready:
                    state = {
                        "mini_game": "reaction_time",
                        "result": "too_soon",
                        "reaction_ms": None,
                        "wait_time_s": round(wait_time, 3),
                        "completed_at": int(time.time()),
                    }
                    _save_state(state, save_path)
                    return state

                reaction_ms = int((time.time() - start_time) * 1000)
                state = {
                    "mini_game": "reaction_time",
                    "result": "clicked",
                    "reaction_ms": reaction_ms,
                    "wait_time_s": round(wait_time, 3),
                    "completed_at": int(time.time()),
                }
                _save_state(state, save_path)
                return state

        if not ready and (time.time() - wait_start) >= wait_time:
            ready = True
            start_time = time.time()

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    print(reaction_time())
