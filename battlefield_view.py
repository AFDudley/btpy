import pygame
from pygame.locals import *
from battlefield import Battlefield
import battlefield
import defs
import widgets

class Board(object):
    """displays a battlefield for user interaction"""
    def __init__(self, surface):
        self.surface = surface
        
        
    class battle_pane(widgets.Pane, Battlefield):
        #contains a battlefield (kludgy?)
        #maybe this inherit from Pane and Battlefield and overload place tiles?
        def __init__(self, surface):
            super(widgets.Pane, self).__init__()
            super(Battlefield, self).__init__()
            self.surface = surface
            self.rect = Rect((10,10), [512,512])
            self.border_width = 2
            # Internal rectangle
            self.in_rect = Rect(
                self.rect.left + self.border_width,
                self.rect.top + self.border_width,
                self.rect.width - self.border_width * 2,
                self.rect.height - self.border_width * 2)
            self.bgcolor = [200,200,200]
            self.border_color = [0,255,0]
            self.tiles = pygame.sprite.RenderUpdates()
            self.place_tiles(16,16)
            
        class Tile(pygame.sprite.Sprite, battlefield.Tile):
            """it's a battlefield tile and a pygame sprite, yo"""
            def __init__(self, location):
                battlefield.Tile.__init__(self)
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.Surface([31,31])
                self.image.fill([127,127,127])
                self.rect = self.image.get_rect()
                self.rect.topleft = location
                def update():
                    """pull tile info, push to surface"""
                    #call update on the contents. Tricky.
                    pass
                
        def place_tiles(self, width, height):
            for x in range(width):
                for y in range(height):
                    self.tiles.add(self.Tile([(x*32), (y*32)]))

        #def populate():
           # "draws the Tiles unto the battle_pane"""
           # pass
        
pygame.init()
screen = pygame.display.set_mode([800,600])
test = Board(screen)
bp = test.battle_pane(test.surface)
