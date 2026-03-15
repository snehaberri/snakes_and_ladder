import random
import time
from pathlib import Path

import pygame

from board import draw_board as draw_existing_board
from mini_games.reaction_time import reaction_time
from mini_games.tic_tac_toe import tic_tac_toe
from snakes import Snake


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 760
BOARD_SIZE = 700
MARGIN = 30
GRID_SIZE = 10
CELL_SIZE = BOARD_SIZE // GRID_SIZE
PANEL_X = MARGIN + BOARD_SIZE + 25
FPS = 60

BG_COLOR = (247, 241, 225)
GRID_COLOR = (90, 76, 58)
TEXT_COLOR = (55, 44, 33)
PLAYER_COLOR = (214, 72, 72)
GOAL_COLOR = (57, 122, 80)
BUTTON_COLOR = (49, 111, 164)
BUTTON_DISABLED = (146, 165, 184)
BUTTON_TEXT = (248, 250, 252)
SNAKE_COLOR = (178, 54, 54)
LADDER_COLOR = (198, 142, 61)
MINIGAME_COLOR = (110, 66, 153)

DICE_ASSET_DIR = Path("assets/dice")

SNAKES = {
    16: 6,
    47: 26,
    49: 11,
    56: 53,
    62: 19,
    64: 60,
    87: 24,
    93: 73,
    95: 75,
    98: 78,
}

LADDERS = {
    1: 38,
    4: 14,
    9: 31,
    21: 42,
    28: 84,
    36: 44,
    51: 67,
    71: 91,
    80: 100,
}

MINIGAME_TILES = {
    13: "reaction",
    34: "tictactoe",
    58: "reaction",
    79: "tictactoe",
}


def tile_to_pixel(tile: int) -> tuple[int, int]:
    index = tile - 1
    row_from_bottom = index // GRID_SIZE
    col_in_row = index % GRID_SIZE
    if row_from_bottom % 2 == 1:
        col_in_row = GRID_SIZE - 1 - col_in_row

    x = MARGIN + col_in_row * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + BOARD_SIZE - (row_from_bottom * CELL_SIZE) - CELL_SIZE // 2
    return x, y


def build_ladder_map() -> dict[int, int]:
    return dict(LADDERS)


def load_dice_images() -> list[pygame.Surface]:
    images = []
    for face in range(1, 7):
        path = DICE_ASSET_DIR / f"{face}.png"
        if not path.exists():
            return []
        image = pygame.image.load(str(path)).convert_alpha()
        images.append(pygame.transform.smoothscale(image, (120, 120)))
    return images


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, color: tuple[int, int, int], pos: tuple[int, int]) -> None:
    rendered = font.render(text, True, color)
    surface.blit(rendered, pos)


def draw_centered_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    center: tuple[int, int],
) -> None:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


def draw_tile_labels(surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            board_row = GRID_SIZE - 1 - row
            tile_number = board_row * GRID_SIZE + (col + 1)
            if board_row % 2 == 1:
                tile_number = board_row * GRID_SIZE + (GRID_SIZE - col)

            rect = pygame.Rect(
                MARGIN + col * CELL_SIZE,
                MARGIN + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            label_color = TEXT_COLOR
            if tile_number in MINIGAME_TILES:
                label_color = MINIGAME_COLOR
            elif tile_number in SNAKES:
                label_color = SNAKE_COLOR
            elif tile_number in LADDERS:
                label_color = LADDER_COLOR

            draw_text(surface, fonts["small"], str(tile_number), label_color, (rect.x + 8, rect.y + 6))


def build_snake_paths(snakes: dict[int, int]) -> dict[int, list[tuple[int, int]]]:
    paths = {}
    for start, end in snakes.items():
        start_pos = tile_to_pixel(start)
        end_pos = tile_to_pixel(end)
        midpoint_seed = start * 17 + end * 31
        rng = random.Random(midpoint_seed)
        mid_x = (start_pos[0] + end_pos[0]) // 2 + rng.randint(-35, 35)
        mid_y = (start_pos[1] + end_pos[1]) // 2 + rng.randint(-35, 35)
        paths[start] = [start_pos, (mid_x, mid_y), end_pos]
    return paths


def draw_connections(
    surface: pygame.Surface,
    snakes: dict[int, int],
    ladders: dict[int, int],
    snake_paths: dict[int, list[tuple[int, int]]],
) -> None:
    for start, end in ladders.items():
        start_pos = tile_to_pixel(start)
        end_pos = tile_to_pixel(end)
        pygame.draw.line(surface, LADDER_COLOR, start_pos, end_pos, 6)

        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = max((dx * dx + dy * dy) ** 0.5, 1)
        offset_x = int(-dy / length * 12)
        offset_y = int(dx / length * 12)
        pygame.draw.line(
            surface,
            LADDER_COLOR,
            (start_pos[0] + offset_x, start_pos[1] + offset_y),
            (end_pos[0] + offset_x, end_pos[1] + offset_y),
            4,
        )
        pygame.draw.line(
            surface,
            LADDER_COLOR,
            (start_pos[0] - offset_x, start_pos[1] - offset_y),
            (end_pos[0] - offset_x, end_pos[1] - offset_y),
            4,
        )

    for start, end in snakes.items():
        start_pos = tile_to_pixel(start)
        points = snake_paths[start]
        pygame.draw.lines(surface, SNAKE_COLOR, False, points, 7)
        pygame.draw.circle(surface, SNAKE_COLOR, start_pos, 11)


def draw_player(surface: pygame.Surface, tile: int) -> None:
    x, y = tile_to_pixel(tile)
    pygame.draw.circle(surface, PLAYER_COLOR, (x, y), 18)
    pygame.draw.circle(surface, (255, 244, 244), (x, y), 18, 3)


def draw_button(surface: pygame.Surface, rect: pygame.Rect, label: str, font: pygame.font.Font, enabled: bool) -> None:
    color = BUTTON_COLOR if enabled else BUTTON_DISABLED
    pygame.draw.rect(surface, color, rect, border_radius=14)
    draw_centered_text(surface, font, label, BUTTON_TEXT, rect.center)


def draw_dice(surface: pygame.Surface, dice_images: list[pygame.Surface], value: int, font: pygame.font.Font) -> None:
    dice_rect = pygame.Rect(PANEL_X + 18, 180, 120, 120)
    pygame.draw.rect(surface, (255, 255, 255), dice_rect, border_radius=16)
    pygame.draw.rect(surface, GRID_COLOR, dice_rect, 2, border_radius=16)

    if dice_images:
        surface.blit(dice_images[value - 1], dice_rect.topleft)
    else:
        draw_centered_text(surface, font, str(value), TEXT_COLOR, dice_rect.center)


def animate_roll(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    fonts: dict[str, pygame.font.Font],
    dice_images: list[pygame.Surface],
    state: dict,
) -> int:
    duration = 0.8
    started = time.time()
    value = 1

    while time.time() - started < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit(0)

        value = random.randint(1, 6)
        state["dice_value"] = value
        render(screen, fonts, dice_images, state)
        pygame.display.flip()
        clock.tick(FPS)

    return value


def move_player(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    fonts: dict[str, pygame.font.Font],
    dice_images: list[pygame.Surface],
    state: dict,
    destination: int,
) -> None:
    while state["player_tile"] < destination:
        state["player_tile"] += 1
        render(screen, fonts, dice_images, state)
        pygame.display.flip()
        clock.tick(8)


def launch_minigame(minigame_name: str) -> tuple[bool, str]:
    if minigame_name == "reaction":
        result = reaction_time()
        success = result.get("result") == "clicked"
        message = (
            f"Reaction challenge: {result.get('result')}"
            if result.get("reaction_ms") is None
            else f"Reaction challenge: {result['reaction_ms']} ms"
        )
    else:
        result = tic_tac_toe()
        success = result.get("result") == "player_win"
        message = f"Tic Tac Toe: {result.get('result', 'finished')}"

    return success, message


def apply_special_tile(tile: int, snakes: dict[int, int], ladders: dict[int, int]) -> tuple[int, str]:
    if tile in ladders:
        return ladders[tile], f"Ladder! Climbed from {tile} to {ladders[tile]}."
    if tile in snakes:
        return snakes[tile], f"Snake! Slid from {tile} to {snakes[tile]}."
    return tile, ""


def render(screen: pygame.Surface, fonts: dict[str, pygame.font.Font], dice_images: list[pygame.Surface], state: dict) -> None:
    screen.fill(BG_COLOR)

    pygame.draw.rect(
        screen,
        (245, 236, 216),
        (MARGIN - 10, MARGIN - 10, BOARD_SIZE + 20, BOARD_SIZE + 20),
        border_radius=20,
    )
    draw_existing_board(screen)
    draw_tile_labels(screen, fonts)
    draw_connections(screen, state["snakes"], state["ladders"], state["snake_paths"])
    draw_player(screen, state["player_tile"])

    draw_text(screen, fonts["title"], "Snakes and Ladders", TEXT_COLOR, (PANEL_X, 40))
    draw_text(screen, fonts["body"], "Goal: Reach tile 100", TEXT_COLOR, (PANEL_X, 95))
    draw_text(screen, fonts["body"], f"Current tile: {state['player_tile']}", TEXT_COLOR, (PANEL_X, 130))

    draw_dice(screen, dice_images, state["dice_value"], fonts["title"])
    draw_text(screen, fonts["body"], f"Last roll: {state['dice_value']}", TEXT_COLOR, (PANEL_X, 320))
    draw_text(screen, fonts["body"], f"Turns played: {state['turns']}", TEXT_COLOR, (PANEL_X, 355))

    draw_button(screen, state["roll_button"], "Roll Dice", fonts["body"], not state["game_over"])

    draw_text(screen, fonts["body"], "Mini-game tiles:", TEXT_COLOR, (PANEL_X, 440))
    draw_text(screen, fonts["small"], "13, 58 -> Reaction Time", MINIGAME_COLOR, (PANEL_X, 472))
    draw_text(screen, fonts["small"], "34, 79 -> Tic Tac Toe", MINIGAME_COLOR, (PANEL_X, 500))

    status_lines = [
        state["message"],
        state["extra_message"],
    ]
    y = 560
    for line in status_lines:
        if line:
            draw_text(screen, fonts["small"], line, TEXT_COLOR, (PANEL_X, y))
            y += 34

    if state["game_over"]:
        overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        overlay.fill((21, 47, 33, 150))
        screen.blit(overlay, (MARGIN, MARGIN))
        draw_centered_text(
            screen,
            fonts["title"],
            "You Win!",
            (255, 248, 235),
            (MARGIN + BOARD_SIZE // 2, MARGIN + BOARD_SIZE // 2 - 10),
        )
        draw_centered_text(
            screen,
            fonts["body"],
            "Close the window to finish.",
            (255, 248, 235),
            (MARGIN + BOARD_SIZE // 2, MARGIN + BOARD_SIZE // 2 + 35),
        )


def main() -> int:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snakes and Ladders")
    clock = pygame.time.Clock()

    fonts = {
        "title": pygame.font.SysFont("arial", 36, bold=True),
        "body": pygame.font.SysFont("arial", 24),
        "small": pygame.font.SysFont("arial", 20),
    }

    roll_button = pygame.Rect(PANEL_X, 390, 170, 42)
    dice_images = load_dice_images()

    snake_manager = Snake()
    snake_manager.snakes = dict(SNAKES)
    snakes = dict(snake_manager.snakes)
    ladders = build_ladder_map()
    snake_paths = build_snake_paths(snakes)

    state = {
        "player_tile": 1,
        "dice_value": 1,
        "message": "Click Roll Dice to start playing.",
        "extra_message": "Landing on a mini-game tile launches a challenge.",
        "turns": 0,
        "game_over": False,
        "roll_button": roll_button,
        "snakes": snakes,
        "ladders": ladders,
        "snake_paths": snake_paths,
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0

            if event.type == pygame.MOUSEBUTTONDOWN and not state["game_over"]:
                if state["roll_button"].collidepoint(event.pos):
                    roll = animate_roll(screen, clock, fonts, dice_images, state)
                    state["dice_value"] = roll
                    state["turns"] += 1

                    if state["player_tile"] + roll > 100:
                        state["message"] = f"Rolled {roll}. Need an exact roll to reach 100."
                        state["extra_message"] = ""
                    else:
                        destination = state["player_tile"] + roll
                        move_player(screen, clock, fonts, dice_images, state, destination)

                        new_tile, message = apply_special_tile(destination, snakes, ladders)
                        state["player_tile"] = new_tile
                        state["message"] = message or f"Rolled {roll}. Now on tile {new_tile}."
                        state["extra_message"] = ""

                        if destination in MINIGAME_TILES:
                            won_bonus, minigame_message = launch_minigame(MINIGAME_TILES[destination])
                            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                            pygame.display.set_caption("Snakes and Ladders")
                            if won_bonus and state["player_tile"] < 100:
                                bonus_tile = min(100, state["player_tile"] + 3)
                                state["extra_message"] = f"{minigame_message}. Bonus climb to {bonus_tile}."
                                state["player_tile"] = bonus_tile
                            else:
                                state["extra_message"] = minigame_message

                        if state["player_tile"] == 100:
                            state["game_over"] = True
                            state["message"] = "You reached tile 100."
                            state["extra_message"] = "Game complete."

        render(screen, fonts, dice_images, state)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    raise SystemExit(main())
