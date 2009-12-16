import pygame
from pygame.locals import *
import pyconsole

class UpDownBox(pygame.sprite.Sprite):
    def __init__(self, color, initial_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([15, 15])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position
        self.going_down = True
        self.next_update_time = 0
            
    def update(self, current_time, bottom):
        if self.next_update_time < current_time:
            if self.rect.bottom == bottom - 1: self.going_down = False
            elif self.rect.top == 0: self.going_down = True
            
            if self.going_down: self.rect.top += 1
            else: self.rect.top -= 1
        
            self.next_update_time = current_time + 10
        
pygame.init()
boxes = pygame.sprite.Group()
for color, location in [([255, 0, 0], [0, 0]), ([0, 255, 0], [60, 60]),
([0, 0, 255], [120, 120])]:
    boxes.add(UpDownBox(color, location))

screen = pygame.display.set_mode([800, 600])
console = pyconsole.Console(screen, (2,400,796,198),)
pygame.mouse.set_pos(300,240)
vs = {"cheat":False,"a":100, "b":200, "c":300}
console.setvars(vs)
console.setvar("python_mode", not console.getvar("python_mode"))
console.set_interpreter()

while 1:
    screen.fill([0, 0, 0])
    console.process_input()
    boxes.update(pygame.time.get_ticks(), 150)
    for b in boxes: screen.blit(b.image, b.rect)
    console.draw()
    pygame.display.update()


    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_w and pygame.key.get_mods() & KMOD_CTRL:
                console.set_active()
#    pygame.time.wait(10)
