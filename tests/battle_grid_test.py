import pygame
import battlefield
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

class BattlePane(Pane, battlefield.Battlefield):
    """Pane that displays the battlefield"""
    def __init__(self,  position, tilesize, tiles):
        pane_area = (((tilesize * tiles[0]) + 4), ((tilesize * tiles[1]) +4))
        battlefield.Battlefield.__init__(self)
        Pane.__init__(self, pane_area, title=None)
        self.rect.x, self.rect.y = position
        self.grid = self.Grid(tiles=tiles, tilesize=tilesize )
        self.contentimgs = pygame.sprite.RenderUpdates()
        #self.place_point(self.Point([255,255,255]), (8,8))
        #self.place_point(self.Point([0,255,0]), (8, 2))
        #self.draw_range([0,0,50], (8, 8))
        self.get_contents_image()
        
    def get_contents_image(self):
        for x in range(self.grid.x):
            for y in range(self.grid.y):
                if self.grid[x][y].contents:
                    topleft = ((self.grid[x][y].rect.x + 9), \
                               (self.grid[x][y].rect.y + 9))
                    self.grid[x][y].contents.rect.topleft = topleft 
                    self.contentimgs.add(self.grid[x][y].contents)
        
    def update(self):
        Pane.update(self)        
        self.image.blit(self.grid.image, (1,1))
        self.contentimgs.draw(self.image)
                
    class Point(pygame.sprite.Sprite):
        def __init__(self, color):
            pygame.sprite.Sprite.__init__(self) 
            self.image = pygame.Surface([15,15])
            self.image.fill(color)
            self.rect = self.image.get_rect()
            self.location = (None, None)
    
    def draw_range(self, color, loc):
        ha = []
        [[ha.append((x,y)) for y in range(-8,9) if (4 < (abs(x) + abs(y)) < 9) ] for x in range(-8,9)]
        for x in range(len(ha)):
            self.mark_tiles(color, ((loc[0] + ha[x][0]), (loc[0] + ha[x][1])))
            #self.place_point(self.Point([0,0,0]), ((8 + ha[x][0]), (8 + ha[x][1])))
    def draw_center(self):
        #too lazy
        self.mark_tiles([255,255,255], (7,7))
        self.mark_tiles([255,255,255], (7,8))
        self.mark_tiles([255,255,255], (8,7))
        self.mark_tiles([255,255,255], (8,8))
    
    def draw_incoming(self):
        laze = []
        '''
        for y in range(4):
            for x in range(self.grid.x):
                laze.append((x,y))
        '''
        for y in (15,14,13,12):
            for x in range(self.grid.x):
                laze.append((x,y))
        '''
        for x in range(4):
            for y in range(self.grid.y):
                laze.append((x,y))
        
        for x in (15,14,13,12):
            for y in range(self.grid.y):
                laze.append((x,y))
        '''
        for i in laze:
            self.mark_tiles([0,0,255], i)
    
    def draw_area(self, color, loc):
        pass
        
    def mark_tiles(self, color, tile):
        x,y = tile
        tt = self.grid[x][y]
        tt.image.fill(color)
        self.grid.image.blit(tt.image, tt.rect)
        
    def place_point(self, unit, dest):
        battlefield.Battlefield.place_unit(self, unit, dest)
        xpos, ypos = dest
        temp = self.grid[xpos][ypos].rect
        topleft = ((temp.x + 8),(temp.y + 8))
        self.grid[xpos][ypos].contents.rect.topleft = topleft
        self.contentimgs.add(self.grid[xpos][ypos].contents)

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
            self.tilesize = kwargs['tilesize']
            self.tiles    = kwargs['tiles']
            self.image    = pygame.Surface(tuple([self.tilesize * i for i in self.tiles]))
            self.rect     = self.image.get_rect()
            self.rect.x, self.rect.y = (242, TOPINSET)
            self.x,self.y = self.tiles
            # bug in battlefield.py
            for x in range(self.x):
                for y in range(self.y):
                    self.image.blit(self[x][y].image, self[x][y].rect)
            self.image.set_colorkey((0,0,0))
            
        #fix me
        def __new__(cls, *args, **kwargs):
            if not args:
                try:
                    tilesize = kwargs['tilesize']
                    tiles = kwargs['tiles']
                except KeyError:
                    tilesize = 32
                    tiles = (16, 16)
            else:
                tilesize = args[0]
                tiles = args[1]
            
            x,y = tiles
            grid = ()
            for xpos in xrange(x):
                temp = ()
                for ypos in xrange(y):
                    tile = BattlePane.Tile((xpos,ypos)),
                    tile[0].rect.topleft = [(xpos*tilesize) + 2, (ypos*tilesize) + 2]
                    temp += tile
                grid += temp,
            return tuple.__new__(cls, grid)


pygame.init()        
screen = pygame.display.set_mode([800, 600])

#the name battle is hardcoded into pyconsole.py

battle = BattlePane((20, 20), tilesize=32, tiles=(16,16))

stuff = pygame.sprite.RenderUpdates()
stuff.add(battle)
point = battle.grid[8][8].contents
grey  = [127,127,127]
blue  = [0,0,255]
def update_screen():
    stuff.update(); stuff.draw(screen);pygame.display.update()
def grey_tiles():
    for x in xrange(18):
        for y in xrange(18):
            battle.mark_tiles(grey,(x,y))
    update_screen()

def make_triange(self, src=(0,0), num=8, pointing='North'):
    sid = 2 * num
    area = []
    for i in xrange(sid):
        if i % 2:
            in_range = xrange(-(i/2),((i/2)+1))
            for j in xrange(len(in_range)):
                if   pointing == 'North':
                    area.append((src[0] + in_range[j], (src[1] - (1 +(i/2)))))
                elif pointing =='South':
                    area.append((src[0] + in_range[j], (src[1] + (1 +(i/2)))))
                elif pointing =='East':
                    area.append((src[0] +  (1 +(i/2)), (src[1] - in_range[j])))
                elif pointing =='West':
                    area.append((src[0] -  (1 +(i/2)), (src[1] - in_range[j])))
    return area

def blue_lines(num, pointing='North'):
    grey_tiles()
    for i in make_triange(num, point.location, pointing):
        if i[0] >= 0 and i[0] < battle.grid.tiles[0]:
            if i[1] >= 0 and i[1] < battle.grid.tiles[1]:
                battle.mark_tiles(blue,i)
            #the elses below should be in make_area
            else:
                raise Exception("i[1] value %s is off the grid" %i[1])
        else:
            raise Exception("i[0] value %s is off the grid" %i[0])

    update_screen()

def ds():
    """hacky hacky"""
    screen.fill([0,0,0])
    stuff.update()
    stuff.draw(screen)

while pygame.key.get_pressed()[K_ESCAPE] == False:
    ds()
    #battle.draw_range([0, 0, 50], (8, 8))
    #battle.draw_range([127,127,127], (8, 8))
    battle.draw_center()
    battle.draw_incoming()
    pygame.event.pump()
    pygame.display.update()
    
pygame.quit()

