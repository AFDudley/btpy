import pygame        
from pygame.locals import *

screen = pygame.display.set_mode([640,480])
names = ('white','grey','black')
blink = []
for x in names:
    x = pygame.Surface([640,480])
    blink.append(x)

blink[0].fill([255,255,255])
blink[1].fill([127,127,127])
blink[2].fill([0,0,0])

while pygame.event.poll != KEYDOWN: 
    for x in blink:
        pygame.time.delay(10)
        screen.blit(x, [0,0])
        pygame.display.update()

