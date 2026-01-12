import pygame
import random
import time
import sys

def reaction_time():
    pygame.init()

    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reaction Speed Test")

    RED = (200, 0, 0)
    GREEN = (0, 200, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Font
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)

    clock = pygame.time.Clock()

    def draw_text(text, font, color, y):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(WIDTH // 2, y))
        screen.blit(rendered, rect)

    def reaction_test():
        waiting = True
        ready = False
        start_time = 0

        # Random wait (2–5 seconds)
        wait_time = random.uniform(2, 5)
        wait_start = time.time()

        running = True
        while running:
            screen.fill(RED)
            draw_text("Wait for GREEN...", font, WHITE, HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ready:
                        reaction_time = int((time.time() - start_time) * 1000)
                        result_screen(reaction_time)
                        return
                    else:
                        # Clicked too early
                        result_screen(None)
                        return

            # Switch to green after delay
            if waiting and time.time() - wait_start >= wait_time:
                waiting = False
                ready = True
                start_time = time.time()

            if ready:
                screen.fill(GREEN)
                draw_text("CLICK!", font, BLACK, HEIGHT // 2)

            pygame.display.update()
            clock.tick(60)

    def result_screen(reaction_time):
        showing = True
        while showing:
            screen.fill(BLACK)

            if reaction_time is None:
                draw_text("Too Soon!", font, RED, HEIGHT // 2 - 20)
            else:
                draw_text(f"{reaction_time} ms", font, GREEN, HEIGHT // 2 - 20)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    showing = False

            pygame.display.update()
            clock.tick(60)