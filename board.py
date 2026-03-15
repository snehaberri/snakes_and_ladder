import sys

import pygame


BLACK = (200, 200, 200)
BACKGROUND = (16, 75, 30)
WINDOW_HEIGHT = 900
WINDOW_WIDTH = 900
BLOCK_SIZE = 40


def draw_grid(surface: pygame.Surface) -> None:
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, BLACK, rect, 1)


def draw_board(surface: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    draw_grid(surface)


def board() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_board(screen)
        pygame.display.update()
        clock.tick(60)
