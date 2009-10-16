"""Defines battlefield_view"""
import pygame
import battlefield

class Pane(object):
    """window Pane class"""
    def __init__(self):
        self.border_width = 2
        self.rect = pygame.Rect((0, 0), (516, 516))
        self.bgcolor = [200, 200, 200]
        self.border_color = [0, 255, 0]
        self.surface = None
        # Internal rectangle
        self.in_rect = pygame.Rect(
            self.rect.left + self.border_width, 
            self.rect.top + self.border_width, 
            self.rect.width - self.border_width * 2, 
            self.rect.height - self.border_width * 2)
        self.font = pygame.font.SysFont('Droid Sans Mono',  16)
        self.font_color = [255, 255, 255]
        self.text = None
    
    def draw(self):
        """draw pane to subsurface"""
        self.surface.fill(self.border_color)
        self.surface.fill(self.bgcolor,  rect=self.in_rect)
        
        if self.text:
            x_pos = self.in_rect.left
            y_pos = self.in_rect.top
            #for line in self.text:
            line_sf = self.font.render(self.text,  True,  self.font_color,
                self.bgcolor)
            #if ( line_sf.get_width() + x_pos > self.rect.right or
            #    line_sf.get_height() + y_pos > self.rect.bottom):
            #    raise LayoutError('Cannot fit line "%s" in widget' % line)
                
            self.surface.blit(line_sf,  (x_pos,  y_pos))
            y_pos += line_sf.get_height()
    

class Board(object):
    """displays a battlefield for user interaction"""
    def __init__(self,  surface):
        self.tilesize = 32 #size of displayed bp.Tiles
        self.surface = surface
    
        class Player(object):
            """unit container (and later ui stuffs?)"""
            #player: a dict that contains units and items at the very least.
            #units: a dict that contains units (duh)
            def __init__(self):
                pass
            def get_units(self, store,  player):
                """Retrieve units owned by player in store"""
                pass
            def push_units(self, field):
                """send units owned by self to battlefield"""
                pass
        
    class StatPane(Pane):
        """pane containing information about the currently selected tile"""
        def __init__(self,  surface):
            Pane.__init__(self)
            self.surface = surface.subsurface(pygame.Rect((42, 42), (170, 170)))
            self.rect = pygame.Rect((0, 0), (170, 170))
            self.border_color = [255, 0, 0]
            self.bgcolor = [50, 50, 50]
            self.in_rect = pygame.Rect(
                self.rect.left + self.border_width, 
                self.rect.top + self.border_width, 
                self.rect.width - self.border_width * 2, 
                self.rect.height - self.border_width * 2)
            self.text = "testy testing"
            self.draw()
        
    class InfoPane(Pane):
        """Displays info about current battle and debug info"""
        def __init__(self):
            Pane.__init__(self)
    
    class BattlePane(Pane,  battlefield.Battlefield):
        """Pane that displays the battlefield"""
        def __init__(self,  surface):
            battlefield.Battlefield.__init__(self)
            Pane.__init__(self)
            #self.tilesize should be a ratio of self.surface
            self.tilesize = 32
            #self.surface should be a percentage of surface not hardcoded
            self.surface = surface.subsurface(
                pygame.Rect((242, 42), (516, 516)))
            self.tiles = pygame.sprite.RenderUpdates()
            self.load_grid()
            self.load_squads()


        def draw_tiles(self, size):
            """Draws tiles and their contents onto BattlePane surface"""
            #isn't there an easier way?
            for xpos in range(len(self.grid)):
                for ypos in range(len(self.grid[xpos])):
                    self.tiles.add(self.Tile([(xpos*size) + 2,
                        (ypos*size) + 2]))
            self.tiles.draw(self.surface)
        
        def draw_contents(self, size):
            """Draws the contents of the tiles, this might be kinda slow"""
            pass
        class Tile(pygame.sprite.Sprite,  battlefield.Tile):
            """it's a battlefield tile and a pygame sprite,  yo"""
            def __init__(self,  location):
                pygame.sprite.Sprite.__init__(self)
                battlefield.Tile.__init__(self)
                self.image = pygame.Surface([31, 31])
                self.image.fill([127, 127, 127])
                self.rect = self.image.get_rect()
                self.rect.topleft = location
            
        
        class Scient(pygame.sprite.Sprite, defs.Scient):
            """tricky"""
    

#scratch
pygame.init()
screen = pygame.display.set_mode([800, 600])
#put some stuff here
b = Board(screen)
bp = Board.BattlePane(b.surface)
bp.rand_place_squad(bp.squad1)
bp.rand_place_squad(bp.squad2)
bp.draw_tiles(bp.tilesize)
bp.draw()
#bp.tiles.draw(bp.surface)
bp.draw_tiles(b.tilesize)
pygame.display.update()
def find_units():
    for x in range(len(bp.grid)):
        for y in range(len(bp.grid[x])):
            if bp.grid[x][y].contents:
                print bp.grid[x][y].contents
                print x,y
    
def wipe(): pygame.display.update(screen.fill([0, 0, 0]))
