import pygame 
import random
import time

pygame.init()
WIDTH, HEIGHT= 500,400
screen= pygame.display.set_mode((WIDTH, HEIGHT))
clock= pygame.time.Clock()

dice_imgs=[]
use_imgs= False
try:
    for i in range(1,7):
        img= pygame.image.load(f"{i}.png").convert_alpha()
        dice_imgs.append(img)
    use_imgs= True
except:
    pass
dice_imgs = [pygame.transform.scale(img, (150, 150)) for img in dice_imgs]
print("Loaded dice images:", len(dice_imgs))

def roll_dice_animation():
    roll_start= time.time()
    animation_duration =1.0
    last_value=1
    
    while time.time()- roll_start<animation_duration:
        last_value= random.randint(1,6)
        screen.fill((30,30,30))
        screen.blit(dice_imgs[last_value-1],(125,125))
        pygame.display.update()
        pygame.time.delay(70)
    return last_value

running= True
rolled_value= None

while running:
    screen.fill((50,50,50))
    
    if rolled_value:
        screen.blit(dice_imgs[rolled_value-1],(125,125))
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running= False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            rolled_value= roll_dice_animation()

pygame.quit()
    