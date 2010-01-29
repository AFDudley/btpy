#
#  battle_view.py
#  
#
#  Created by AFD on 1/12/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
from operator import contains
import pygame
import battlefield
import battle
import pyconsole
from pygame.locals import *
from const import E,F,I,W, ELEMENTS, OPP, ORTH, PHY
from defs import Scient, Squad
from helpers import rand_comp, rand_element

black = [0,0,0]
darkg = [50, 50, 50]
blue  = [0, 0, 255]
red   = [255,0,0]
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

def max_squad_by_value(value):
    """Takes an integer, ideally even because we round down, and returns a
    squad such that comp[element] == value, comp[orth] == value/2, comp[opp]
    == 0"""
    squad = Squad()
    value = value/2 #more logical, really.
    half = value/2
    for i in ELEMENTS:
        unit = BattlePane.Scient(i,{E:half, F:half, I:half, W:half,})
        unit.comp[unit.element] = value
        unit.comp[OPP[unit.element]] = 0
        unit.calcstats()
        squad.append(unit)
    return squad

#pane stuff    
class Pane(pygame.sprite.Sprite):
    """window Pane class"""
    def __init__(self, size, title=None):
        pygame.sprite.Sprite.__init__(self)
        self.border_width = 2
        self.image = pygame.Surface(size)
        self.rect = pygame.Rect((0, 0), size)
        self.bgcolor = darkw
        self.border_color = green
        # Internal rectangle
        self.in_rect = pygame.Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        self.font = pygame.font.SysFont('droidsansmono',  12)
        self.font_color = [255, 255, 255]
        self.title = title
        self.text = []
        self.texttopoffset = 2
        self.textleftoffset = 2
        self.active = False
        self.last_line = 0
        self.cursor_pos = 0
        self.key = None
        
    def draw_text(self, text, tbgcolor=[50,50,50], color=white):
        """Draws text to self.surface"""
        textrect = self.font.render(text, True, color, tbgcolor)
        topleft = (self.in_rect.left + self.textleftoffset), \
            (self.in_rect.top + self.texttopoffset)
        self.image.blit(textrect, topleft)
        self.texttopoffset += textrect.get_height()
        
    def draw_title(self, title=None):
        if title == None:
            title = self.title
        self.draw_text(title, self.bgcolor)
            
    def update(self):
        """draw pane to subsurface"""
        if not self.active:
            self.image.fill(self.border_color)
        else:
            self.image.fill(white)
        self.image.fill(self.bgcolor, rect=self.in_rect)
        self.draw_title()
        if len(self.text) > 0:
            for i in xrange(len(self.text)):
                if i != self.cursor_pos:
                    self.draw_text(self.text[i][0], self.text[i][1], self.text[i][2])
                else:
                    self.draw_text(self.text[i][0], black, self.text[i][2])
        self.texttopoffset = 2

    def process_arrow(self, key):
        if self.last_line != 0:
            if key == K_DOWN:
                if self.cursor_pos < self.last_line:
                    self.cursor_pos += 1
                else:
                    self.cursor_pos = 0
            elif key == K_UP:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                else:
                    self.cursor_pos = self.last_line

    def process_key(self, key):
        if key == K_UP or key == K_DOWN:
            self.process_arrow(key)
        elif key == K_RETURN:
            self.process_return()
        else:
            pass
        view.current_state.draw_other_panes()
            
    def set_state(self):
        pass
    def draw_other_panes(self):
        pass
        
class TopPane(Pane):
    def __init__(self, position, size=PANE_SIZE, title=None):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [255, 0, 0]
        self.bgcolor = [50, 50, 50]
       
    def set_state(self):
        self.cursor_pos = 0
        view.middle.cursor_pos = -1
        view.bottom.title = "Info:"
        view.bottom.text = []
        if view.battle_state.current_ply.num % 2 == 1:
            self.squad = view.battle.squad1
        else:
            self.squad = view.battle.squad2
        if len(self.squad) > 0:
            self.text = []
            self.title = self.squad.name + " Inital Value: " + str(self.squad.value)
            self.last_line = - 1
            #cpu time < human time:
            self.squad.text = []
            for i in reversed(xrange(len(self.squad))):
                #Some of these values only need to be computed once.
                #This should really be done by a function in battlepane.scient
                unit = self.squad[i]
                unit.text = [] #oops...
                if self.squad[i].name == None:
                    name = str(self.squad[i].location)
                squ_txt = name + " V: " + str(self.squad[i].value())
                self.text.append((squ_txt, darkg, white))
                unit.text.append("HP: " + str(unit.hp))
                unit.text.append("E, F, I, W")
                unit.text.append(str(unit.comp[E]) + ", " + str(unit.comp[F]) + ", " + str(unit.comp[I]) +  ", " + str(unit.comp[W]))
                if contains(PHY, unit.weapon.type):
                    atk = "PA: " + str(unit.patk)
                else:
                    atk = "MA: " + str(unit.matk)
                unit.text.append("Weapon: " + unit.weapon.type)
                unit.text.append(atk)
                unit.text.append("PD: " + str(unit.pdef) + " MD: " + str(unit.mdef))
                unit.text.append("Location: " + str(unit.location))
            self.text.reverse()
            self.last_line = len(self.squad) - 1
        else:
            #set next move to pass; send to battle_state; which should end the game.
            
            view.set_action(None, 'pass', None)
            view.send_action()
            print "Game Over."

    def draw_other_panes(self):
        if len(self.squad) != 0:
            self.unit = self.squad[self.cursor_pos]
            view.make_tile_sets(self.unit)
            view.draw_grid(None)
            view.middle.text = []
            #won't be able to test for a while...
            if len(view.move) == 0 and len(view.targets) == 0:
                view.middle.title = "Unit cannot act."
            else:
                view.middle.title = "Unit can: "
                if len(view.move) != 0 and view.last_action_type != 'move':
                    view.middle.title += "Move "
                if len(view.targets) != 0 and view.last_action_type != 'attack':
                    view.middle.title += "Attack "
            for i in view.unit.text:
                view.middle.text.append((i, darkg, white))
            view.bottom.title = "Enemy Info:"
            #enemies in range
            #
            
        else:
            self.text = []
            self.title = "There is no other"
            self.text.append(("squad.", darkg, white))
            self.text.append(("Press Esc to quit or", darkg, white))
            self.text.append(("ctrl-w for console.", darkg, white))
            self.last_line = 0
            self.cursor_pos = -1
            view.middle.title = None
            view.bottom.title = None
            view.middle.text = []
            view.bottom.text = []
            
    def process_return(self):
        if len(self.squad) != 0:
            view.set_action(self.unit, view.current_action[1], view.current_action[2])
            view.transition(view.middle)
        else:
            view.current_state = view.top
            view.current_state.active = True
            view.current_state.set_state()
            view.current_state.draw_other_panes()
            #TODO: Flush or Write Log
            view.transition(view.top)
            
class MiddlePane(Pane):
    """Pane in the middle left"""
    def __init__(self, position, size=PANE_SIZE, title=None):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 255, 0]
        self.bgcolor = [50, 50, 50]
        self.text = []
        
    def set_state(self):
        self.cursor_pos = 0
        self.text = []
        if len(view.move) != 0 and view.last_action_type != 'move':
            view.middle.text.append(("Move", darkg, blue))
        if len(view.targets) != 0 and view.last_action_type != 'attack':
            view.middle.text.append(("Attack", darkg, pink))
        view.middle.text.append(("Pass", darkg, white))
    
        if view.battle_state.current_ply[0] == None:
            self.text.append(("Cancel", darkg, red))
        self.last_line = len(self.text) - 1
        
    def draw_other_panes(self):
        view.draw_grid(self.text[self.cursor_pos][0])
        view.bottom.text = []
        view.bottom.cursor_pos = -1
        view.bottom.title = "Info:"
        if self.text[self.cursor_pos][0] == 'Attack':
            view.draw_grid('Targets')
            view.bottom.title = "Targets:"
            targets = list(view.targets)
            targets.sort()
            #The panes can only hold 10 lines.
            for i in xrange(len(targets)):
                text = str(i) + ": " + str(targets[i]) + " HP: " + \
                str(view.battle.grid[targets[i][0]][targets[i][1]].contents.hp)
                view.bottom.text.append((text, darkg, white))
        if self.text[self.cursor_pos][0] == 'Move':
            view.bottom.title = "Info:"
        if self.text[self.cursor_pos][0] == 'Pass':
            text = []
            if view.battle_state.current_ply[0] == None:
                view.bottom.title = "Skip both actions?"
            else:
                view.bottom.title = "Skip second action?"
            view.bottom.text.append(("Cancel", darkg, red))
            view.bottom.text.append(("Confirm", darkg, green))
        if self.text[self.cursor_pos][0] == 'Cancel':
            view.bottom.title = "Select another Unit?"
            
    def process_return(self):
        if self.text[self.cursor_pos][0] != 'Cancel':
            type = self.text[self.cursor_pos][0].lower()
            view.set_action(view.current_action[0], type, view.current_action[2])
            view.transition(view.bottom)
        else:
            #TODO: keep the privous view.top.cursor_pos; harder than it sounds.
            view.transition(view.top)
            
class BottomPane(Pane):
    """lowest pane on the left"""
    def __init__(self, position, size=PANE_SIZE, title='Info:'):
        Pane.__init__(self, size, title)
        self.rect.x, self.rect.y = position
        self.border_color = [0, 0, 255]
        self.bgcolor = [50, 50, 50]
        self.text = []
        self.inside_confirm = False
    #need to overload update.
    def set_state(self):
        self.last_line = len(self.text) - 1
        self.cursor_pos = 0
        if self.inside_confirm == False:
            if view.middle.text[view.middle.cursor_pos][0] == 'Attack':
                self.action = 'attack'
                self.targets = list(view.targets)
                self.targets.sort()
                view.battle.set_tile_color(self.targets[self.cursor_pos], red)
            elif view.middle.text[view.middle.cursor_pos][0] == 'Move':
                self.action = 'move'
                self.title = "Move to:"
                self.move = list(view.move)
                self.move.sort()            
            else:
                self.action = 'pass'
                self.inside_confirm = True
            
    def draw_other_panes(self):
        if self.inside_confirm == False:
            if self.action == 'move':
                self.last_line = len(self.move) - 1 
                self.text = []
                self.text.append((str(self.cursor_pos) + ": " + str(self.move[self.cursor_pos]) + "?", black, white))
                view.draw_grid('Move')
                view.battle.set_tile_color(self.move[self.cursor_pos], white)
                area  = set(view.unit.weapon.map_to_grid(self.move[self.cursor_pos], view.grid.size))
                area -= view.loc
                view.battle.color_tiles(area - view.move, pink)
                view.battle.color_tiles(area & view.move, purp)
            if self.action == 'attack':
                view.draw_grid('Targets')
                if view.unit.weapon.type == 'Ice':
                    area = view.battle.calc_wand_area(view.unit, self.targets[self.cursor_pos])
                    view.battle.color_tiles(area, black)
                    print "area:", len(area)
                view.battle.set_tile_color(self.targets[self.cursor_pos], red)
            if self.action == 'pass':
                pass
    def process_return(self):
        #the trickist
        if self.inside_confirm == True:
            if self.text[self.cursor_pos][0] != 'Cancel':
                self.inside_confirm = False
                if self.action == 'move':
                    dest = self.move[self.old_cursor]
                elif self.action == 'attack':
                    dest = self.targets[self.old_cursor]
                else:
                    dest = None
                view.set_action(view.current_action[0], view.current_action[1], dest)
                view.send_action()
                ###
            else:
                if self.action != 'pass':
                    self.text           = self.old_text
                    self.title          = self.old_title
                    self.cursor_pos     = self.old_cursor
                    self.last_line      = self.old_last_line
                    self.inside_confirm = False
                    self.draw_other_panes()
                else:
                    view.middle.title = "berries"
                    view.transition(view.middle)
        else:
            self.old_text       = self.text
            self.old_title      = self.title
            self.old_cursor     = self.cursor_pos
            self.old_last_line  = self.last_line
            self.inside_confirm = True
            self.title = "Are you sure?"
            self.text = []
            self.text.append(("Cancel", darkg, red))
            self.text.append(("Confirm", darkg, green))                
            self.cursor_pos = 0
            self.last_line = 1
            view.transition(self)       
                
class BattlePane(Pane, battlefield.Battlefield):
    """Pane that displays the battlefield"""
    def __init__(self,  position, grid, tilesize, tiles):
        #NOTE: This object has Player information that a battlefield does not have.
        pane_area = (((tilesize* tiles[0]) + 4), ((tilesize * tiles[1]) +4))
        battlefield.Battlefield.__init__(self)
        Pane.__init__(self, pane_area, title=None)
        self.rect.x, self.rect.y = position
        self.grid = grid
        self.contentimgs = pygame.sprite.RenderUpdates()
        self.player1 = battle.Player()
        self.player2 = battle.Player()
        self.player1.squad_list = [rand_squad()]
        self.player2.squad_list = [rand_squad()]
        self.squad1 = self.player1.squad_list[0]
        self.squad2 = self.player2.squad_list[0]
        
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
            
    def place_unit(self, unit, dest):
        battlefield.Battlefield.place_unit(self, unit, dest)
        xpos, ypos = dest
        temp = self.grid[xpos][ypos].rect
        topleft = ((temp.x + 8),(temp.y + 8))
        self.grid[xpos][ypos].contents.rect.topleft = topleft
        self.contentimgs.add(self.grid[xpos][ypos].contents)
    
    def bury(self, unit):
        battlefield.Battlefield.bury(self, unit)
        unit.remove(unit.groups())
        
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
            self.text = []
            
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
        """it's a battlefield tile and a pygame sprite, yo"""
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
            
class View:
    def __init__(self, screen, grid):
        self.grid = grid
        self.top    = TopPane((LEFTINSET,TOPINSET))
        self.middle = MiddlePane((LEFTINSET, (TOPINSET + PANE_HEIGHT + PANE_SPACING)))
        self.bottom = BottomPane((LEFTINSET, (TOPINSET + 2 *(PANE_HEIGHT + PANE_SPACING))))
        #the name battle is hardcoded into pyconsole.py
        self.battle = BattlePane((242, TOPINSET), self.grid, tilesize=32, tiles=(16,16))
        self.battle_state = battle.state(grid=self.grid, battlefield=self.battle)
        #console code
        self.console = pyconsole.Console(screen, (2,398,794,200))
        self.console.set_interpreter()
        self.last_action_type = None
        
    #not needed.
    def coroutine(func):
        def start(*args,**kwargs):
            cr = func(*args,**kwargs)
            cr.next()
            return cr
        return start
    
    @coroutine
    def get_key(self):
        """handles state changes"""
        #initalize state
        self.current_state = self.top
        self.current_state.active = True
        self.current_state.set_state()
        self.current_state.draw_other_panes()
        self.current_action = battle.action()
        self.last_action_type = None
        while True:
            key = (yield)
            self.current_state.process_key(key)
    
    def clean(self):
        """Resets the color of all tiles"""
        for x in range(self.battle.grid.x):
            for y in range(self.battle.grid.y):
                self.battle.set_tile_color((x,y), grey)  
    
    def make_tile_sets(self, unit):
        """Make area, move, targets tile sets for unit."""
        self.unit  = unit
        self.area  = set(self.unit.weapon.map_to_grid(self.unit.location, self.grid.size))
        self.move  = set(self.battle.make_move(self.unit))
        self.units = set(self.battle.find_units())
        self.move -= self.units #can't moved to occupied tiles
        self.loc   = set((self.unit.location,),)
        self.targets = self.area & self.units

    def draw_grid(self, tiles_to_color=None):
        """takes a list of (tiles, color) tuples, applies colors,
        draws grid contents"""
        #un-optimized
        self.clean()
        if tiles_to_color == None:
            view.battle.color_tiles(self.area, pink)
            view.battle.color_tiles(self.move, blue)
            view.battle.color_tiles(self.area & self.move, purp)
            view.battle.color_tiles(self.targets, white)
        elif tiles_to_color == 'Move':
            view.battle.color_tiles(self.move, blue)
        elif tiles_to_color == 'Attack':
            view.battle.color_tiles(self.area, pink)
        elif tiles_to_color == 'Targets':
            view.battle.color_tiles(self.targets, white)
        else:
            pass
    def set_action(self, unit, type, target):
        """sets the properties of the current action"""
        self.current_action = battle.action(unit, type, target)
            
    def send_action(self):
        """sends the current action to the battle_state"""
        #if first action in ply is pass, set second to same
        text = []
        if self.current_action[1] == 'pass':
            if self.battle_state.current_ply[0] == None:
                text += self.battle_state.process_action(self.current_action)
        text += self.battle_state.process_action(self.current_action)
        '''
        send_action is only called from the bottom pane and we should move to
        the top pane only when the ply is full, otherwise, move to the middle.
        '''
        if self.battle_state.current_ply[0] == None:
            self.last_action_type = None
            self.transition(view.top)
        else:
            self.make_tile_sets(self.unit)
            self.last_action_type = self.current_action[1]
            self.transition(view.middle)
        for i in text:
            print i
            view.console.output(i)
            
    def transition(self, dest_state):
        """transitions from current_state to dest_state"""
        self.current_state.active = False
        self.current_state = dest_state
        self.current_state.active = True
        self.current_state.set_state()
        self.current_state.draw_other_panes()
    
    def print_log(self):
        print self.battle_state.log.moves

###
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode([800, 600])
    grid = BattlePane.Grid(tiles=(16,16), tilesize=32)
    view = View(screen, grid)
    view.state = view.get_key()
    view.battle_state.player1.name = "Player 1"
    view.battle_state.player2.name = "Player 2"
    view.console.active = 0
    paneimgs = pygame.sprite.RenderUpdates()
    for pane in (view.top, view.middle, view.bottom, view.battle):
        paneimgs.add(pane)
        
    while pygame.key.get_pressed()[K_ESCAPE] == False:
        pygame.event.pump()
        screen.fill([0,0,0])
        view.console.process_input()
        paneimgs.update()
        paneimgs.draw(screen)
        view.console.draw()
        
        
        if view.console.active == 0:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key != K_w:
                        view.state.send(event.key)
                    elif pygame.key.get_mods() & KMOD_CTRL:
                            view.console.set_active()
                                
        pygame.display.update()
        pygame.event.pump()
        
    pygame.quit()

