import pygame
from mini_games import reaction_time
pygame.init()
screen = pygame.display.set_mode((640, 640))

print("Reaction:", reaction_time.reaction_time(screen))
pygame.time.wait(1500)