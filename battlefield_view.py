"""Defines battlefield_view"""
import pygame
import battlefield

#temp colors
Fire = [228, 20, 20]
Earth = [20, 228, 20]
Ice = [20, 20, 228]
Wind = [255, 255, 30]
COLORS = {"Earth": Earth, "Fire" : Fire, "Ice" : Ice, "Wind" :Wind}

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
        self.font = pygame.font.SysFont('droidsansmono',  12)
        #self.font = pygame.font.SysFont('monaco',  16)
        self.font_color = [255, 255, 255]
        self.title = None
        self.texttopoffset = 2
        self.textleftoffset = 2
    
    def draw_text(self, text, tbgcolor=[50,50,50]):
        """Draws text to self.surface"""
        textrect = self.font.render(text, True, self.font_color, \
            tbgcolor)
        topleft = (self.in_rect.left + self.textleftoffset), \
            (self.in_rect.top + self.texttopoffset)
        self.surface.blit(textrect, topleft)
        self.texttopoffset += textrect.get_height()
    
    def draw_title(self):
        self.draw_text(self.title, [0, 0, 0])
    
    def draw(self):
        """draw pane to subsurface"""
        self.surface.fill(self.border_color)
        self.surface.fill(self.bgcolor,  rect=self.in_rect)


# i guess these should be global?
PANE_SPACING = 18
PANE_SIZE = (160, 160)
PANE_HEIGHT, PANE_WIDTH = PANE_SIZE
TOPINSET = 42
LEFTINSET = 42

class Board(object):
    """displays a battlefield for user interaction"""
    def __init__(self,  surface):
        self.tilesize = 32 #size of displayed bp.Tiles
        self.surface = surface

    
    class TopPane(Pane):
        """pane on the top left"""
        def __init__(self,  surface):
            Pane.__init__(self)
            self.surface = surface.subsurface(pygame.Rect((LEFTINSET, \
                TOPINSET), PANE_SIZE))
            self.rect = pygame.Rect((0, 0), PANE_SIZE)
            self.border_color = [255, 0, 0]
            self.bgcolor = [50, 50, 50]
            self.in_rect = pygame.Rect(
                self.rect.left + self.border_width,
                self.rect.top + self.border_width,
                self.rect.width - self.border_width * 2,
                self.rect.height - self.border_width * 2)
            #ugh i think i'm going to need a ton of textrects...
            #I really don't want to think about abstracting this... -rix
            self.title = "P1 Units | location:"
            #self.texttopoffset = 2
            #self.textleftoffset = 2
    
    
    class MiddlePane(Pane):
        """Pane in the middle left"""
        def __init__(self, surface):
            Pane.__init__(self)
            self.surface = surface.subsurface(pygame.Rect((LEFTINSET, \
                (TOPINSET + PANE_HEIGHT + PANE_SPACING)), PANE_SIZE))
            self.rect = pygame.Rect((0, 0), PANE_SIZE)
            self.border_color = [0, 255, 0]
            self.bgcolor = [50, 50, 50]
            self.in_rect = pygame.Rect(
                self.rect.left + self.border_width,
                self.rect.top + self.border_width,
                self.rect.width - self.border_width * 2,
                self.rect.height - self.border_width * 2)
            self.title = "Act:"
    
    
    class BottomPane(Pane):
        """lowest pane on the left"""
        def __init__(self, surface):
            Pane.__init__(self)
            self.surface = surface.subsurface(pygame.Rect((LEFTINSET, \
            (TOPINSET + 2 * (PANE_HEIGHT + PANE_SPACING))), PANE_SIZE))
            self.rect = pygame.Rect((0, 0), PANE_SIZE)
            self.border_color = [0, 0, 255]
            self.bgcolor = [50, 50, 50]
            self.in_rect = pygame.Rect(
                self.rect.left + self.border_width,
                self.rect.top + self.border_width,
                self.rect.width - self.border_width * 2,
                self.rect.height - self.border_width * 2)
            self.title = "Target:"
    
    
    class BattlePane(Pane,  battlefield.Battlefield):
        """Pane that displays the battlefield"""
        def __init__(self,  surface):
            battlefield.Battlefield.__init__(self)
            Pane.__init__(self)
            #self.tilesize should be a ratio of self.surface
            self.tilesize = 32
            #self.surface should be a percentage of surface not hardcoded
            self.surface = surface.subsurface(
                pygame.Rect((242, TOPINSET), (516, 516)))
            self.tiles = pygame.sprite.RenderUpdates()
            self.contents = pygame.sprite.RenderUpdates()
            self.load_grid()
            self.load_squads()
    
        
        def draw_tiles(self, size):
            """Draws tiles and their contents onto BattlePane surface"""
            #isn't there an easier way?
            for xpos in range(len(self.grid)):
                for ypos in range(len(self.grid[xpos])):
                    tile = self.Tile([(xpos*size) + 2, (ypos*size) + 2])
                    tile.location = self.grid[xpos][ypos].location
                    if self.grid[xpos][ypos].contents is not None:
                        tempy = self.grid[xpos][ypos]
                        xxx,yyy = tile.rect.topleft
                        scient = self.Scient(COLORS[tempy.contents.element], \
                            ((xxx + 8), (yyy + 8)))
                        scient.location = self.grid[xpos][ypos].location
                        self.contents.add(scient)
                    self.tiles.add(tile)
            self.tiles.draw(self.surface)
            self.contents.draw(self.surface)
        
        class Tile(pygame.sprite.Sprite,  battlefield.Tile):
            """it's a battlefield tile and a pygame sprite,  yo"""
            #this is wrong, BattlePane.Tile is really only a sprite. Fix.
            def __init__(self,  topleft):
                pygame.sprite.Sprite.__init__(self)
                battlefield.Tile.__init__(self)
                self.image = pygame.Surface([31, 31])
                self.image.fill([127, 127, 127])
                self.rect = self.image.get_rect()
                self.rect.topleft = topleft
        
        class Scient(pygame.sprite.Sprite):
            """tricky"""
            def __init__(self, color, topleft):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.Surface([15, 15])
                self.image.fill(color)
                self.rect = self.image.get_rect()
                self.rect.topleft = topleft
            
        
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


#scratch

pygame.init()
screen = pygame.display.set_mode([800, 600])

def wipe(): pygame.display.update(screen.fill([0, 0, 0]))
def find_units():
    for x in range(len(bp.grid)):
        for y in range(len(bp.grid[x])):
            if bp.grid[x][y].contents:
                print bp.grid[x][y].contents
                print x,y

def clear_grid():
    for x in range(len(bp.grid)):
        for y in range(len(bp.grid[x])):
            if bp.grid[x][y].contents:
                bp.grid[x][y].contents = None

def draw_unit_hashes():
    for scient in bp.squad1:
        s = str(scient.__hash__())
        b = " | "
        l = str(scient.location)
        tp.draw_text(s + b+ l)


b = Board(screen)

bp = b.BattlePane(b.surface)
bp.rand_place_squad(bp.squad1)
bp.rand_place_squad(bp.squad2)
bp.draw()
bp.draw_tiles(bp.tilesize)
#bp.tiles.draw(bp.surface)
bp.draw_tiles(b.tilesize)

tp = b.TopPane(b.surface); tp.draw(); tp.draw_title()
mp = b.MiddlePane(b.surface); mp.draw(); mp.draw_title()
lp = b.BottomPane(b.surface); lp.draw(); lp.draw_title()

draw_unit_hashes()

pygame.display.update()

#TODO
#active pane
#HILIGHT_COLOR
#HIGHLIGHT_TEXT
#HIGHLIGHT_TILE
#menu (for inside a pane, holds a list of textrects, gets "focus")