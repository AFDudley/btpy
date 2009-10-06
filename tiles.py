import pygame
from pygame.locals import *
from boxes import Box
import random 
from comp import *

comp = COMP
suit = random.choice(ELEMENTS)
comp[suit] = random.randint(1,255)
for x in ORTH[suit]: comp[x] = comp[suit] / 2

brown  = [122,57,20]

green  = [20,220,20]
yellow = [255,255,30]
red    = [220,20,20]
blue   = [20,20,220]

hunter     = [10,173,18]
cobalt     = [10,65,173]
watermelon = [129,15,48]
soleil     = [236,139,15]

beige   = [198,175,115] 
scarlet = [232,25,55]
indigo  = [85,25,232]
lemon   = [240,255,0]

colors = (hunter, scarlet, indigo, lemon)
boxes = []
pygame.init()
def tiles():
    for x in range(16):
        for y in range(16):
            boxes.append(Box([127,127,127], ([((x*32) + 200), ((y*32) + 44)])))
            #boxes.append(Box(([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]), ([(x*16),(y*16)])))
            # print (x,y)
        

screen = pygame.display.set_mode([800,600])
black = screen.fill([0,0,0])
def doit():
    pygame.display.update(screen.fill([200,200,200]))
    tiles()
    for b in boxes: screen.blit(b.image, b.rect)
    pygame.display.update()
#while pygame.event.poll().type != KEYDOWN:
#    pygame.time.delay(10)
doit()
