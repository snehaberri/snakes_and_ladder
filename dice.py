import pygame
import random
import time

pygame.init()
def dice():
    WIDTH, HEIGHT = 150, 150
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Load images
    dice_imgs = []
    use_imgs = False
    try:
        for i in range(1, 7):
            img = pygame.image.load(f"assets/dice/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (150, 150))
            dice_imgs.append(img)
        use_imgs = True
    except:
        print("Using fallback.")

    def roll_dice_animation():
        """Roll dice for 1 second at ~60fps and pick final face."""
        duration = 1.0
        start = time.time()
        final_value = 1

        while time.time() - start < duration:
            # Handle window events DURING animation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # random face
            final_value = random.randint(1, 6)

            # draw
            screen.fill((40, 40, 40))
            screen.blit(dice_imgs[final_value - 1], (0, 0))

            pygame.display.update()
            clock.tick(60)   # Smooth 60fps animation

        return final_value

    running = True
    rolled_value = None

    while running:
        screen.fill((60, 60, 60))

        # Show final rolled value
        if rolled_value:
            screen.blit(dice_imgs[rolled_value - 1], (0, 0))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                rolled_value = roll_dice_animation()   # run animation

    pygame.quit()