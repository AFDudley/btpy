import pygame
import battlefield
import pyconsole
from pygame.locals import *
from const import E,F,I,W, ELEMENTS
from defs import Scient, Squad
from helpers import rand_comp, rand_element

#temp colors
Fire = [228, 20, 20]
Earth = [20, 228, 20]
Ice = [20, 20, 228]
Wind = [255, 255, 30]
COLORS = {"Earth": Earth, "Fire" : Fire, "Ice" : Ice, "Wind" :Wind}

def rand_unit(suit=None): #may change to rand_unit(suit, kind)
    """Returns a random Scient of suit. Random suit used if none given."""
    if not suit in ELEMENTS:
        suit = rand_element()
    return BattlePane.Scient(suit, rand_comp(suit, 'Scient'))

def rand_squad(suit=None):
    """Returns a Squad of five random Scients of suit. Random suit used
       if none given."""
    
    squad = Squad()
    size = 5
    if not suit in ELEMENTS:
        for _ in range(size):
            squad.append(rand_unit(rand_element()))
        return squad
    
    else:
        for _ in range(size):
            squad.append(rand_unit(suit))
        return squad

    
class Pane(pygame.sprite.Sprite):
    """window Pane class"""
    def __init__(self, size, title=None):
        pygame.sprite.Sprite.__init__(self)
        self.border_width = 2
        self.image = pygame.Surface(size)
        self.rect = pygame.Rect((0, 0), size)
        self.bgcolor = [200, 200, 200]
        self.border_color = [0, 255, 0]
        # Internal rectangle
        self.in_rect = pygame.Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        self.font = pygame.font.SysFont('droidsansmono',  12)
        #self.font = pygame.font.SysFont('monaco',  16)
        self.font_color = [255, 255, 255]
        self.title = title
        self.texttopoffset = 2
        self.textleftoffset = 2
    
    def draw_text(self, text, tbgcolor=[50,50,50]):
        """Draws text to self.surface"""
        textrect = self.font.render(text, True, self.font_color, \
            tbgcolor)
        topleft = (self.in_rect.left + self.textleftoffset), \
            (self.in_rect.top + self.texttopoffset)
        self.image.blit(textrect, topleft)
        self.texttopoffset += textrect.get_height()
        
    def draw_title(self):
        self.draw_text(self.title, [0, 0, 0])

    def update(self):
        """draw pane to subsurface"""
        self.image.fill(self.border_color)
        self.image.fill(self.bgcolor, rect=self.in_rect)
        
                
# i guess these should be global?
PANE_SPACING = 18
PANE_SIZE = (160, 160)
PANE_HEIGHT, PANE_WIDTH = PANE_SIZE
TOPINSET = 42
LEFTINSET = 42

class TopPane(Pane):
    """pane on the top left"""
    def __init__(self, position, size=PANE_SIZE,
                 title=None):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [255, 0, 0]
        self.bgcolor = [50, 50, 50]
        self.fps = ''

    def update(self):
        Pane.update(self)
        #self.draw_text(self.title, [0, 0, 0])
        text = "fps: " + str(self.fps)
        self.draw_text(text, [0, 0, 0])
        self.texttopoffset = 2 

        
class MiddlePane(Pane):
    """Pane in the middle left"""
    def __init__(self, position, size=PANE_SIZE, title=None):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 255, 0]
        self.bgcolor = [50, 50, 50]

    def update(self):
        Pane.update(self)
        self.draw_text(self.title, [0, 0, 0])
        self.texttopoffset = 2 

class BottomPane(Pane):
    """lowest pane on the left"""
    def __init__(self, position, size=PANE_SIZE, title=None):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 0, 255]
        self.bgcolor = [50, 50, 50]

    def update(self):
        Pane.update(self)
        self.draw_text(self.title, [0, 0, 0])
        self.texttopoffset = 2

class BattlePane(Pane, battlefield.Battlefield):
    """Pane that displays the battlefield"""
    def __init__(self,  position, area):
        battlefield.Battlefield.__init__(self)
        Pane.__init__(self, area, title=None)
        self.rect.x, self.rect.y = position
        self.grid = self.Grid()
        self.contentimgs = pygame.sprite.RenderUpdates()
        self.squad1 = rand_squad()
        self.squad2 = rand_squad()
        self.rand_place_squad(self.squad1)
        self.rand_place_squad(self.squad2)
        self.get_contents_image()
        
    def update(self):
        Pane.update(self)        
        self.image.blit(self.grid.image, (1,1))
        self.contentimgs.draw(self.image)
                
    def get_contents_image(self):
        for x in range(self.grid.x):
            for y in range(self.grid.y):
                if self.grid[x][y].contents:
                    topleft = ((self.grid[x][y].rect.x + 8), \
                               (self.grid[x][y].rect.y + 8))
                    self.grid[x][y].contents.rect.topleft = topleft
                    self.contentimgs.add(self.grid[x][y].contents)
    
    def move_unit(self, src, dest):
            battlefield.Battlefield.move_unit(self, src, dest)
            xpos, ypos = dest
            temp = self.grid[xpos][ypos].rect
            topleft = ((temp.x + 8),(temp.y + 8))
            self.grid[xpos][ypos].contents.rect.topleft = topleft
            #self.contentimgs.update()
    
    def phit(self, src, dest):
        atk  = self.grid[src[0]][src[1]].contents
        deph = self.grid[dest[0]][dest[1]].contents
        BattlePane.Scient.phit(atk, dest, self)
        if deph.hp <=0:
            self.grid[dest[0]][dest[1]].contents = None
            deph.location = None
            #might change this much later
            deph.remove(deph.groups())
    
    def mhit(self, src, dest, element=None):
        atk  = self.grid[src[0]][src[1]].contents
        deph = self.grid[dest[0]][dest[1]].contents
        BattlePane.Scient.mhit(atk, dest, self, element)
        if deph.hp <=0:
            self.grid[dest[0]][dest[1]].contents = None
            deph.location = None
            #might change this much later
            deph.remove(deph.groups())
            
    class Scient(pygame.sprite.Sprite, Scient):
        """tricky"""
        def __init__(self, ele, topleft):
            pygame.sprite.Sprite.__init__(self)
            Scient.__init__(self,comp=rand_comp(suit=ele, kind='Scient'), element=ele) 
            self.image = pygame.Surface([15, 15])
            self.image.fill(COLORS[ele])
            self.rect = self.image.get_rect()
            self.font = pygame.font.SysFont('droidsansmono',  12)
            self.font_color = [255, 255, 255]
        
    class Tile(pygame.sprite.Sprite, battlefield.Tile):
        """it's a battlefield tile and a pygame sprite,  yo"""
        def __init__(self,  topleft):
            pygame.sprite.Sprite.__init__(self)
            battlefield.Tile.__init__(self)
            self.image = pygame.Surface([31, 31])
            self.image.fill([127, 127, 127])
            self.rect = self.image.get_rect()
            self.rect.topleft = topleft
            
    
    class Grid(pygame.sprite.Sprite, battlefield.Grid):
        def __init__(self, *args, **kwargs):
            pygame.sprite.Sprite.__init__(self)
            battlefield.Grid.__init__(self, *args, **kwargs)
            self.tilesize = 32
            self.image = pygame.Surface((512, 512))
            self.rect  = self.image.get_rect()
            self.rect.x, self.rect.y = (242, TOPINSET)
            # le sigh
            for x in range(self.x):
                for y in range(self.y):
                    self.image.blit(self[x][y].image, self[x][y].rect)
            self.image.set_colorkey((0,0,0))
            
        #fix me
        def __new__(cls, *args, **kwargs):
            if not args:
                try:
                    size = kwargs['size']
                except KeyError:
                    size = (16,16)
            else:
                size = args[0]
            x,y = size

            grid = ()
            tilesize = 32
            for xpos in range(x):
                temp = ()
                for ypos in range(y):
                    tile = BattlePane.Tile((xpos,ypos)),
                    tile[0].rect.topleft = [(xpos*tilesize) + 2, (ypos*tilesize) + 2]
                    temp += tile
                grid += temp,
            return tuple.__new__(cls, grid)
            



class cast(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([600,150])
        self.image.fill([0, 0, 0])
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = (100,300)
        
def wipe(): pygame.display.update(screen.fill([0,0,0]))

pygame.init()        
screen = pygame.display.set_mode([800, 600])

tp = TopPane((LEFTINSET,TOPINSET))
mp = MiddlePane((LEFTINSET, (TOPINSET + PANE_HEIGHT + PANE_SPACING)))
bp = BottomPane((LEFTINSET, (TOPINSET + 2 *(PANE_HEIGHT + PANE_SPACING))))

battle = BattlePane((242, TOPINSET), (516, 516))

stuff = pygame.sprite.RenderUpdates()
for pane in (tp, mp, bp, battle):
    stuff.add(pane)

casting = cast()
yup = pygame.sprite.RenderUpdates()
yup.add(casting)
#console code
console = pyconsole.Console(screen, (2,398,794,200), vars={"repeat_rate":200})
#pygame.mouse.set_pos(300,240)
console.setvar("python_mode", not console.getvar("python_mode"))
console.set_interpreter()

clock = pygame.time.Clock()

def ds():
    """hacky hacky"""
    screen.fill([0,0,0])
    clock.tick()
    console.process_input()
    tp.fps = clock.get_fps()
    stuff.update()
    stuff.draw(screen)
    console.draw()
    
while 1:
    ds()
    '''
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_w and pygame.key.get_mods() & KMOD_CTRL:
                console.set_active()
    '''
    pygame.display.update()
    
#>>>> __IPYTHON__.user_ns['object']

'''
 old functions

def draw_unit_hashes():
    for scient in bp.squad1:
        s = str(scient.__hash__())
        b = " | "
        l = str(scient.location)
        tp.draw_text(s + b+ l)
'''
    