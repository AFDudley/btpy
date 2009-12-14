import pygame
from pygame.locals import *
from boxes import UpDownBox

pygame.init()
boxes = pygame.sprite.Group()
for color, location in [([255, 0, 0], [0, 0]), ([0, 255, 0], [60, 60]),
([0, 0, 255], [120, 120])]:
    boxes.add(UpDownBox(color, location))

screen = pygame.display.set_mode([800, 600])
while pygame.event.poll().type != KEYDOWN:
    screen.fill([0, 0, 0])
    boxes.update(pygame.time.get_ticks(), 150)
    for b in boxes: screen.blit(b.image, b.rect)
    pygame.display.update()
