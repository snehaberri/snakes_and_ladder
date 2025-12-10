import pygame
from mini_games import reaction_time
from dice import dice
from ladder import ladder
pygame.init()

screen = pygame.display.set_mode((640, 640))
ladder_img=pygame.image.load("assets/ladders_snake/ladder.png").convert_alpha()
print("Reaction:", reaction_time.reaction_time(screen))
pygame.time.wait(1500)