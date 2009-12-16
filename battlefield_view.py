import pygame
import battlefield
import pyconsole
from pygame.locals import *

#temp colors
Fire = [228, 20, 20]
Earth = [20, 228, 20]
Ice = [20, 20, 228]
Wind = [255, 255, 30]
COLORS = {"Earth": Earth, "Fire" : Fire, "Ice" : Ice, "Wind" :Wind}

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
    def __init__(self, position, size=PANE_SIZE, title="P1 Units | location:"):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [255, 0, 0]
        self.bgcolor = [50, 50, 50]
        self.fps = ''

    def update(self, current_time, bottom):
        Pane.update(self)
        self.draw_text(self.title, [0, 0, 0])
        text = "fps: " + str(self.fps)
        self.draw_text(text, [0, 0, 0])
        self.texttopoffset = 2 

        
class MiddlePane(Pane):
    """Pane in the middle left"""
    def __init__(self, position, size=PANE_SIZE, title="Act:"):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 255, 0]
        self.bgcolor = [50, 50, 50]

    def update(self, current_time, bottom):
        Pane.update(self)
        self.draw_text(self.title, [0, 0, 0])
        self.texttopoffset = 2 

class BottomPane(Pane):
    """lowest pane on the left"""
    def __init__(self, position, size=PANE_SIZE, title="Target:"):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 0, 255]
        self.bgcolor = [50, 50, 50]

    def update(self, current_time, bottom):
        Pane.update(self)
        self.draw_text(self.title, [0, 0, 0])
        self.texttopoffset = 2

class BattlePane(Pane, battlefield.Battlefield):
    """Pane that displays the battlefield"""
    def __init__(self,  position, size, group):
        battlefield.Battlefield.__init__(self)
        Pane.__init__(self, size, title=None)
        self.rect.x, self.rect.y = position
        #self.tilesize should be a ratio of self.surface
        self.tilesize = 32
        self.tiles = pygame.sprite.RenderUpdates()
        self.contents = group
        self.load_grid()
        self.load_squads()
        self.rand_place_squad(self.squad1)
        self.rand_place_squad(self.squad2)
        self.draw_tiles(self.tilesize)
        Pane.update(self)
        self.tiles.draw(self.image)
    
    def update(self, current_time, bottom):
        pass
                
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
            self.font = pygame.font.SysFont('droidsansmono',  12)
            self.font_color = [255, 255, 255]

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

two = pygame.sprite.RenderUpdates()
battle = BattlePane((242, TOPINSET), (516, 516), two)

stuff = pygame.sprite.RenderUpdates()
for pane in (tp, mp, bp, battle):
    stuff.add(pane)

casting = cast()
yup = pygame.sprite.RenderUpdates()
yup.add(casting)
#console code
console = pyconsole.Console(screen, (0,0,800,600),)
pygame.mouse.set_pos(300,240)
console.setvar("python_mode", not console.getvar("python_mode"))
console.set_interpreter()
clock = pygame.time.Clock()
    
while 1:
    screen.fill([0,0,0])
    clock.tick()
    console.process_input()
    tp.fps = clock.get_fps()
    stuff.update(pygame.time.get_ticks(), 150)
    two.update()
    two.draw(battle.image)
    stuff.draw(screen)
    console.draw()
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_w and pygame.key.get_mods() & KMOD_CTRL:
                console.set_active()

#>>>> __IPYTHON__.user_ns['object']

''' old functions
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
'''
    