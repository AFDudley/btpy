import pygame
from pygame.locals import *
import battlefield

import defs

class Pane(object):
    def __init__(self):
        self.border_width = 2
        self.rect = Rect((0,0),(516,516))
        self.bgcolor = [200,200,200]
        self.border_color = [0,255,0]
        self.surface = None
    # Internal rectangle
    #    self.in_rect = Rect(
    #        self.rect.left + self.border_width,
    #        self.rect.top + self.border_width,
    #        self.rect.width - self.border_width * 2,
    #        self.rect.height - self.border_width * 2)
     
        
    #def draw(self):
    #    self.surface.fill(self.border_color)
    #    self.surface.fill(self.bgcolor, rect=self.in_rect)

class Board(object):
    """displays a battlefield for user interaction"""
    def __init__(self, surface):
        self.tilesize = 32 #size of displayed bp.Tiles
        self.surface = surface
        
            
    #class Stat_pane(self.Pane):
     #   def __init__(self):
      #      return
    
    #class Info_pane(self.Pane):
     #   def __init__(self):
      #      return
    
    class Battle_pane(Pane, battlefield.Battlefield):
        #is a battlefield (kludgy?)
        #the pane code is borked. don't know why.
        def __init__(self, surface):
#            super(self, Pane).__init__()
#            super(self, battlefield.Battlefield).__init__()
            self.surface = surface.subsurface(Rect((100,0),(516,516)))
            self.tiles = pygame.sprite.RenderUpdates()
            self.place_tiles(16,16)

        def place_tiles(self, width, height):
            for x in range(width):
                for y in range(height):
                    self.tiles.add(self.Tile([(x*32) + 2, (y*32) + 2]))
                    
        class Tile(pygame.sprite.Sprite, battlefield.Tile):
            """it's a battlefield tile and a pygame sprite, yo"""
            def __init__(self, location):
#                super(self, battlefield.Tile).__init__()
#                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.Surface([31,31])
                self.image.fill([127,127,127])
                self.rect = self.image.get_rect()
                self.rect.topleft = location
           
                def update():
                    """pull tile info, push to surface"""
                    #call update on the contents. Tricky.
                    pass
                


#scratch        
#pygame.init()
#screen = pygame.display.set_mode([800,600])
#test = Board(screen)
#bp = test.Battle_pane(test.surface)
#bp.draw()
#bp.tiles.draw(bp.surface)
#pygame.display.update()

#def wipe(): pygame.display.update(screen.fill([0,0,0]))
