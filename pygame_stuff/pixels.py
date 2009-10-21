import pygame
from pygame.locals import *
from boxes import Box
import random
from comp import *



comp = {E:0, F:0, I:0, W:0}
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

pygame.init()
screen = pygame.display.set_mode([256,256])
def rand_pix(colors):
    for x in range(256):
        for y in range(256):
            screen.set_at((x, y), (random.choice(colors)))
            #boxes.append(Box(([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]), ([(x*16),(y*16)])))
            # print (x,y)
        
black = screen.fill([0,0,0])


def doit(colors):
    pygame.display.update(black)
    rand_pix(colors)
    pygame.display.update()

doit(colors)
