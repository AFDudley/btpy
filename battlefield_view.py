import pygame
import battlefield
import pyconsole
from pygame.locals import *
from const import E,F,I,W, ELEMENTS
from defs import Scient, Squad
from helpers import rand_comp, rand_element
from moves import action_types

black = [0,0,0]
darkg = [50, 50, 50]
blue  = [0, 0, 255]
green = [0, 255, 0]
pink  = [255,20,50]
grey  = [127,127,127]
white = [255,255,255]
darkw = [200,200,200]
purp  = [127,10,152]

#temp colors
Fire  = [228, 20, 20]
Earth = [20, 228, 20]
Ice   = [20, 20, 228]
Wind  = [255, 255, 30]
COLORS = {"Earth": Earth, "Fire" : Fire, "Ice" : Ice, "Wind" :Wind}

#Pane params
PANE_SPACING = 18
PANE_SIZE = (160, 160)
PANE_HEIGHT, PANE_WIDTH = PANE_SIZE
TOPINSET = 42
LEFTINSET = 42

class Squad(Squad):
    def locs(self):
        """location of units in squad"""
        s = ''
        for x in range(len(self)):
            s += str(x) + '-> ' + 'loc: ' + str(self[x].location) + ' Suit: ' \
            + str(self[x].element) + ' HP: ' + str(self[x].hp) + ' PA/PD: ' \
            + str(self[x].patk) + '/' + str(self[x].pdef) + ' MA/MD: ' \
            + str(self[x].matk) + '/' + str(self[x].mdef) + '\n'
        print s
  
def rand_unit(suit=None): #may change to rand_unit(suit, kind)
    """Returns a random Scient of suit. Random suit used if none given."""
    if not suit in ELEMENTS:
        suit = rand_element()
    return BattlePane.Scient(element=suit, comp=rand_comp(suit, 'Scient'))

def rand_squad(suit=None):
    """Returns a Squad of five random Scients of suit. Random suit used
       if none given."""
    size = 5 #max num units in squad
    if not suit in ELEMENTS:
        return Squad([rand_unit(rand_element()) for i in range(size)])
    
    else:
        return Squad([rand_unit(suit) for i in range(size)])
    
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
        self.highlight = False
        self.line_highlight = 0
        
    def draw_text(self, text, tbgcolor=[50,50,50], color=white):
        """Draws text to self.surface"""
        textrect = self.font.render(text, True, color, tbgcolor)
        topleft = (self.in_rect.left + self.textleftoffset), \
            (self.in_rect.top + self.texttopoffset)
        self.image.blit(textrect, topleft)
        self.texttopoffset += textrect.get_height()
        
    def draw_title(self):
        self.draw_text(self.title, self.bgcolor)
        
    def update(self):
        """draw pane to subsurface"""
        if not self.highlight:
            self.image.fill(self.border_color)
        else:
            self.image.fill([255,255,255])
        self.image.fill(self.bgcolor, rect=self.in_rect)

class TopPane(Pane):
    """pane on the top left"""
    def __init__(self, position, size=PANE_SIZE, title='Units:'):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [255, 0, 0]
        self.bgcolor = [50, 50, 50]
        self.text = ''
        self.squad = None
        self.max_line = 10
        
    def draw_body(self, squad):
        #bit of an indexing kludge
        for i in xrange(len(squad)):
            text =  str(squad[i].location) + ' value: ' + str(squad[i].value())
            if self.line_highlight != i:
                self.draw_text(text, self.bgcolor)
            else:
                self.draw_text(text, black)
    
    def update(self):
        Pane.update(self)
        self.draw_title()
        self.draw_body(self.squad)
        self.texttopoffset = 2 
        
class MiddlePane(Pane):
    """Pane in the middle left"""
    def __init__(self, position, size=PANE_SIZE, title='Actions:'):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 255, 0]
        self.bgcolor = [50, 50, 50]
        self.text = None
        self.max_line = 3
    
    def update(self):
        Pane.update(self)
        self.draw_title()
        for x in self.text:
            self.draw_text(x[0], color=x[1], tbgcolor=x[2])

        self.texttopoffset = 2

class BottomPane(Pane):
    """lowest pane on the left"""
    def __init__(self, position, size=PANE_SIZE, title='Info:'):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 0, 255]
        self.bgcolor = [50, 50, 50]
        self.text = None
        self.max_line = 0
        
    def update(self):
        Pane.update(self)
        self.draw_title()
        '''if self.fps != None:
            self.draw_text("fps: " + str(self.fps), self.bgcolor)
            self.texttopoffset = 2'''
        if self.text != None:
            self.draw_text(self.text, darkg)
        self.texttopoffset = 2    
        
class BattlePane(Pane, battlefield.Battlefield):
    """Pane that displays the battlefield"""
    def __init__(self,  position, tilesize, tiles):
        pane_area = (((tilesize* tiles[0]) + 4), ((tilesize * tiles[1]) +4))
        battlefield.Battlefield.__init__(self)
        Pane.__init__(self, pane_area, title=None)
        self.rect.x, self.rect.y = position
        self.grid = self.Grid(tiles=tiles, tilesize=tilesize )
        self.contentimgs = pygame.sprite.RenderUpdates()
        self.squad1 = rand_squad()
        self.squad2 = rand_squad()
        self.squad1.name = 'p1'
        self.squad1.num  = '1'
        self.squad2.name = 'p2'
        self.squad2.num  = '2'
        self.rand_place_squad(self.squad1)
        self.rand_place_squad(self.squad2)
        
        for s in (self.squad1, self.squad2):
            for i in s:
                i.draw_text()
        self.get_contents_image()
        
    def update(self):
        Pane.update(self)        
        self.image.blit(self.grid.image, (1,1))
        self.contentimgs.draw(self.image)
    
    def set_tile_color(self, tile, color):
        tt = self.grid[tile[0]][tile[1]]
        tt.set_color(color)
        self.grid.image.blit(tt.image, tt.rect)

    def add_tile_color(self, tile, color):
        tt = self.grid[tile[0]][tile[1]]
        oc = list(tt.image.get_at((0,0)))
        oc.pop()
        new = oc,color
        tt.set_color([min(sum(a),255) for a in zip(*new)])
        self.grid.image.blit(tt.image, tt.rect)
    
    def color_tiles(self, tiles, color):
        #this *_tile_color, and tile.set_color could be improved.
        for i in tiles:
            self.set_tile_color(i, color)
    
    def get_contents_image(self):
        for x in range(self.grid.x):
            for y in range(self.grid.y):
                if self.grid[x][y].contents:
                    topleft = ((self.grid[x][y].rect.x + 9), \
                               (self.grid[x][y].rect.y + 9))
                    self.grid[x][y].contents.rect.topleft = topleft
                    self.grid[x][y].contents.draw_text()
                    self.contentimgs.add(self.grid[x][y].contents)
    
    def move_unit(self, src, dest):
            battlefield.Battlefield.move_unit(self, src, dest)
            xpos, ypos = dest
            temp = self.grid[xpos][ypos].rect
            topleft = ((temp.x + 8),(temp.y + 8))
            self.grid[xpos][ypos].contents.rect.topleft = topleft
            self.set_tile_color(src, grey)
            #self.set_tile_color(dest, black)
            
    def place_unit(self, unit, dest):
        battlefield.Battlefield.place_unit(self, unit, dest)
        xpos, ypos = dest
        temp = self.grid[xpos][ypos].rect
        topleft = ((temp.x + 8),(temp.y + 8))
        self.grid[xpos][ypos].contents.rect.topleft = topleft
        self.contentimgs.add(self.grid[xpos][ypos].contents)
        
    def flush_units(self):
        battlefield.Battlefield.flush_units(self)
        self.contentimgs.empty()
        
    def make_move(self, unit):
        """generates a list of tiles within the move range of unit."""
        m = unit.move
        xo, yo = unit.location
        tiles = []
        for x in range(-m,(m + 1)):
            for y in range(-m,(m + 1)):
                if abs(x) + abs(y) <= m:
                    tile = (xo + x), (yo + y)
                    if 0 <= tile[0] < self.grid.x:
                        if 0 <= tile[1] < self.grid.y:
                            tiles.append(tile)
        return tiles    
    
    class Scient(pygame.sprite.Sprite, Scient):
        """tricky"""
        def __init__(self, element=None, comp=None):
            pygame.sprite.Sprite.__init__(self)
            if element == None:
                element = rand_element()
            if comp == None:
                comp = rand_comp(suit=element, kind='Scient')
                
            Scient.__init__(self, comp=comp, element=element) 
            self.image = pygame.Surface([15, 15])
            self.image.fill(COLORS[element])
            self.rect = self.image.get_rect()
            
        def draw_text(self):
            """a crude, crude hack."""
            self.font = pygame.font.SysFont('droidsansmono',  12)
            self.font_color = [0, 0, 0]
            textrect = self.font.render(self.squad.num, True, self.font_color, \
            COLORS[self.element])
            self.image.blit(textrect, (3.5,0))
            
        def __repr__(self):
            return Scient.__repr__(self)

    class Tile(pygame.sprite.Sprite, battlefield.Tile):
        """it's a battlefield tile and a pygame sprite,  yo"""
        def __init__(self,  topleft):
            pygame.sprite.Sprite.__init__(self)
            battlefield.Tile.__init__(self)
            self.image = pygame.Surface([31, 31])
            self.image.fill(grey)
            self.rect = self.image.get_rect()
            self.rect.topleft = topleft
        
        def set_color(self, color):
            self.image.fill(color)

    class Grid(pygame.sprite.Sprite, battlefield.Grid):
        def __init__(self, *args, **kwargs):
            pygame.sprite.Sprite.__init__(self)
            battlefield.Grid.__init__(self, *args, **kwargs)
            self.tilesize = kwargs['tilesize']
            self.tiles    = kwargs['tiles']
            self.image    = pygame.Surface(tuple([self.tilesize * x for x in self.tiles]))
            self.rect     = self.image.get_rect()
            self.rect.x, self.rect.y = (242, TOPINSET)
            self.x,self.y = self.tiles
            for x in xrange(self.x):
                for y in xrange(self.y):
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

class View(object):
    """Contains all the panes and some logic"""
    def __init__(self,screen):
        self.screen = screen
        self.tp = TopPane((LEFTINSET,TOPINSET))
        self.mp = MiddlePane((LEFTINSET, (TOPINSET + PANE_HEIGHT + PANE_SPACING)))
        self.bp = BottomPane((LEFTINSET, (TOPINSET + 2 *(PANE_HEIGHT + PANE_SPACING))))
        #the name battle is hardcoded into pyconsole.py
        self.battle = BattlePane((242, TOPINSET), tilesize=32, tiles=(16,16))
        self.panes = (self.tp, self.mp, self.bp, self.battle)
        self.paneimgs = pygame.sprite.RenderUpdates()
        for pane in self.panes:
            self.paneimgs.add(pane)
        self.lit = -1
        #console code
        self.console = pyconsole.Console(screen, (2,398,794,200), vars={"repeat_rate":200})
        #pygame.mouse.set_pos(300,240)
        self.console.setvar("python_mode", not self.console.getvar("python_mode"))
        self.console.set_interpreter()
        self.light(0, self.lit)
        
    def light(self, pane, lit):
        self.panes[lit].highlight  = 0
        self.panes[pane].highlight = 1
        self.lit = pane

    def clean(self):
        """Resets the color of all tiles"""
        for x in range(self.battle.grid.x):
            for y in range(self.battle.grid.y):
                self.battle.set_tile_color((x,y), grey)       
    
    #not needed.
    def coroutine(func):
        def start(*args,**kwargs):
            cr = func(*args,**kwargs)
            cr.next()
            return cr
        return start
        
    @coroutine
    def states(self):
        """this code is wrong, work in progress"""
        statetuple = ('top','middle','bottom')
        current_pane = 0
        current_ply = 0
        current_action = 0
        self.last_ply = -1
        print "inside states"
        #temp#
        self.mp.texttopoffset = 2
        self.mp.text = (("Move To", blue, darkg),("Attack", pink, darkg))
        #self.bp.text = None
        #self.bp.fps = clock.get_fps()
        ###temp set squad
        self.tp.squad = self.battle.squad1
        self.tp.max_line = len(self.tp.squad) - 1
        ###
        unit = self.tp.squad[self.tp.line_highlight]
        area  = set(unit.weapon.map_to_grid(unit.location, self.battle.grid.size))
        move  = set(self.battle.make_move(unit))
        units = set(self.battle.find_units())
        move -= units #can't moved to occupied tiles
        loc   = set((unit.location,),)
        targets = area & units
        self.battle.color_tiles(area, pink)
        self.battle.color_tiles(move, blue)
        self.battle.color_tiles(area & move, purp)
        self.battle.color_tiles(targets, white)
        #end temp#
        
        while True:
            key = (yield)
            print key
            if key == K_DOWN:
                print "key down", statetuple[current_pane]
                if self.panes[current_pane].max_line != 0: #?
                        if self.panes[current_pane].line_highlight < self.panes[current_pane].max_line:
                            self.panes[current_pane].line_highlight += 1
                        else:
                            self.panes[current_pane].line_highlight = 0
            elif key == K_UP:
                print "key up", statetuple[current_pane]
                if self.panes[current_pane].max_line != 0:
                    if self.panes[current_pane].line_highlight > 0:
                        self.panes[current_pane].line_highlight -= 1
                    else:
                        self.panes[current_pane].line_highlight = self.panes[current_pane].max_line
            elif key == K_RETURN:
                print "return", statetuple[current_pane]
                if current_pane == 0:
                    current_pane += 1
                    self.light(current_pane, (current_pane -1))
                elif current_pane == 1:
                    if self.mp.line_highlight == len(self.mp.text) -1:
                        current_pane = 0
                        self.light(0, 1)
                    else:
                        current_pane += 1
                        self.light(current_pane, (current_pane -1))                    
                elif current_pane == 2:
                    self.mp.line_highlight = 0
                    #do end of ply stuff
                    if ply_action == action_types[0]:
                        self.battle.move_unit(unit.location, temp[self.bp.line_highlight])
                        
                    if ply_action == action_types[1]:
                        dx,dy = temp[self.bp.line_highlight]
                        defdr = self.battle.grid[dx][dy].contents
                        self.battle.attack(unit, defdr)
                    if ply_action == action_types[2]:
                        self.battle.moves[-1][current_ply]['actions'][current_action]['target'] = None
                    else:
                        self.battle.moves[-1][current_ply]['actions'][current_action]['target'] = temp[self.bp.line_highlight]
                    self.battle.moves[-1][current_ply]['actions'][current_action]['type'] = ply_action
                    self.battle.moves[-1][current_ply]['actions'][current_action]['unit'] = unit.__hash__()
                    
                    #there are two actions in a ply. and two plies in a move.
                    if current_action == 0:
                        current_action = 1
                        current_pane = 1
                        self.light(current_pane, 2)
                    else: 
                        current_ply = not current_ply
                        self.last_ply += 1
                        current_action = 0
                        current_pane = 0
                        if current_ply % 2 == 1:                            
                            self.battle.moves.append(battlefield.move( \
                            self.battle.game_id, self.battle.moves[-1].num + 1, last_ply=self.last_ply))
                        self.light(current_pane, 2)
                    
            view.clean()
            #from draw_colored_tiles: make tile sets
            unit  = self.tp.squad[self.tp.line_highlight]
            area  = set(unit.weapon.map_to_grid(unit.location, self.battle.grid.size))
            move  = set(self.battle.make_move(unit))
            units = set(self.battle.find_units())
            move -= units #can't moved to occupied tiles
            loc   = set((unit.location,),)
            targets = area & units
        
            if current_pane == 0:
                print "current_ply", current_ply
                print "last_ply", self.last_ply
                #need current_ply and ply_num. can't use current_ply to sent num in k-return state change
                #or i can just change how plys and moves are instanciated.
                if self.battle.moves[-1][current_ply]['num'] % 2 == 1:
                    self.tp.squad = self.battle.squad1
                    self.tp.title = self.battle.squad1.name
                else:
                    self.tp.squad = self.battle.squad2
                    self.tp.title = self.battle.squad2.name
                self.tp.max_line = len(self.tp.squad) - 1
                unit  = self.tp.squad[self.tp.line_highlight]                
                #from draw_colored_tiles
                self.battle.color_tiles(area, pink)
                self.battle.color_tiles(move, blue)
                self.battle.color_tiles(area & move, purp)
                self.battle.color_tiles(targets, white)
            
                #from draw_pane
                self.mp.texttopoffset = 2
                self.mp.text = (("Move To", blue, darkg),("Attack", pink, darkg))
                #self.bp.text = None
            elif current_pane == 1:
                #from draw_pane (I am so sorry)
                self.mp.texttopoffset = 2
                text_list = ['Move To', 'Attack', 'Pass', 'Cancel']
                color_list = [blue, pink, white, black]
                #if unit has moved, remove move to from list
                print "current_ply", current_ply
                print "current_action", current_action
                if current_action % 2 == 1:
                    print "Last time: ", self.battle.moves[-1][current_ply]['actions'][0]['type']
                    if self.battle.moves[-1][current_ply]['actions'][0]['type'] == 'move':
                        del text_list[0]
                        del color_list[0]
                    #if unit has attacked or has no targets remove attack from list
                    if self.battle.moves[-1][current_ply]['actions'][0]['type'] \
                        == 'attack' or len(targets) == 0:
                        del text_list[1]
                        del color_list[1]
                self.mp.text = []    
                for i in xrange(len(text_list)):
                    if self.mp.line_highlight != i:
                        self.mp.text.append((text_list[i], color_list[i], darkg))
                    else:
                        self.mp.text.append((text_list[i], color_list[i], black))                               
                self.mp.max_line = len(self.mp.text) - 1 
                #from draw_colored_tiles
                if self.mp.text[self.mp.line_highlight][0] == 'Move To': # move to
                    self.battle.color_tiles(move, blue)
                    self.bp.text = None
                if self.mp.text[self.mp.line_highlight][0] == 'Attack': # attack
                    self.battle.color_tiles(targets,white)
                    self.bp.text = None
                if self.mp.text[self.mp.line_highlight][0] == 'Pass': #pass
                    self.bp.text = "Skip action?"
                if self.mp.text[self.mp.line_highlight][0] == 'Cancel': #cancel
                    self.bp.text = "Select another unit?"
            
            elif current_pane == 2:
                if self.mp.text[self.mp.line_highlight][0] == 'Move To':
                    self.bp.text = None
                    ply_action = action_types[0]
                    self.bp.max_line = len(move) - 1
                    self.battle.color_tiles(move, blue)
                    temp = list(move)
                    temp.sort()
                    self.battle.set_tile_color(temp[self.bp.line_highlight], white)
                    love = 'Move to ' + str(temp[self.bp.line_highlight]) + '?'
                    self.bp.text = love
                    
                if self.mp.text[self.mp.line_highlight][0] == 'Attack':
                    self.bp.text = None
                    ply_action = action_types[1]
                    self.bp.max_line = len(targets) - 1
                    self.battle.color_tiles(targets,white)
                    temp = list(targets)
                    temp.sort()
                    if self.bp.line_highlight > len(temp): # "highlight" the line with the target on it 
                        self.bp.line_highlight = 0
                    self.battle.set_tile_color(temp[self.bp.line_highlight], pink) 
                    love = 'Attack' + str(temp[self.bp.line_highlight]) + '?'
                    print temp[self.bp.line_highlight]
                    self.bp.text = love
                    
                if self.mp.text[self.mp.line_highlight][0] == 'Pass':
                    ply_action = action_types[2]
                    
            #from draw_colored_tiles
            self.battle.set_tile_color(unit.location, black)
        
    def go(self, screen):
        while pygame.key.get_pressed()[K_ESCAPE] == False:
            pygame.event.pump()
            screen.fill([0,0,0])
            #clock.tick()
            self.console.process_input()
            #self.bp.fps = clock.get_fps()
            self.paneimgs.update()
            self.paneimgs.draw(screen)
            self.console.draw()
            
            if self.console.active == 0:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key != K_w:
                            game_state.send(event.key)
                        elif pygame.key.get_mods() & KMOD_CTRL:
                                self.console.set_active()
                                    
            pygame.display.update()
            pygame.event.pump()

if __name__ == '__main__':

    #def wipe(): pygame.display.update(screen.fill([0,0,0]))
    
    pygame.init()
    #clock = pygame.time.Clock()      
    screen = pygame.display.set_mode([800, 600])
    view = View(screen)
    btl = view.battle
    grid = view.battle.grid

    view.console.active = 0
    ###
    
    from defs import Wand
    from const import COMP
    happy = Wand(W, COMP.copy())
    size = (16,16)
    center = (7,7)

    ###
    game_state = view.states()
    view.go(screen)
    pygame.quit()

