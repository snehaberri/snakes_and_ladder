import pygame
import sys

BLACK = (200, 200, 200)
BACKGROUND = (16, 75, 30)

# Dimensions
WINDOW_HEIGHT = 400
WINDOW_WIDTH = 400
BLOCK_SIZE = 40  # size of each grid cell

def draw_grid(surface):
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, BLACK, rect, 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BACKGROUND)
        draw_grid(screen)
        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
