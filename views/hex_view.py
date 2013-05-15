#
#  hex_view.py
#
#
#  Created by AFD on 1/12/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
import sys
sys.path[0:0] = '../'
from math import sin, cos, radians, ceil, floor
import pygame
from pygame.locals import * #need them all so the game doesn't crash when someone presses the wrong key :D
#from pygame.locals import K_ESCAPE, KEYDOWN, K_w, K_UP, K_DOWN, K_RETURN
from binary_tactics.hex_battlefield import Tile, Grid, Battlefield, Loc, noloc
import binary_tactics.hex_battle as battle

from binary_tactics.const import E,F,I,W, ELEMENTS, OPP, ORTH
from binary_tactics.units import Scient, Nescient
from binary_tactics.unit_container import Squad
from binary_tactics.helpers import rand_comp, rand_element
import stores.yaml_store as yaml_store

try:
    import pyconsole
except ImportError, message:
    import views.pyconsole as pyconsole

#Magic Sprinkles!!!

black = [0, 0, 0]
darkg = [50, 50, 50]
blue  = [0, 0, 255]
red   = [255,0,0]
green = [0, 255, 0]
pink  = [255,20,50]
grey  = [127,127,127]
white = [255,255,255]
darkw = [0, 0, 200]
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

def roof(num):
    return int(ceil(num))

def get_hex_params(recw):
    r = recw/2
    s = int(floor(r/cos(radians(30))))
    hexh = roof(sin(radians(30))*s)
    rech = s + (2*hexh)
    size = [roof(recw), roof(rech)]
    return r,s,hexh,rech,size

def make_hex(hexparams, colr, parent_surface=None):
    """returns a Surface containing a hextile"""
    r,s,hexh,rech,size = hexparams
    recw = 2 * r
    pl = [(0, hexh), (r,0), (recw,hexh), (recw, rech-hexh), (.5*recw, rech), (0, rech - hexh)]
    pl2 = [(1, 1+hexh), (.5*recw,2), (recw-2,hexh+1), (recw-2, rech-hexh-1), (.5*recw, rech-2), (2, rech - hexh-1)]
    if parent_surface == None:
        hexa = pygame.Surface(size)
    else:
        hexa = parent_surface.subsurface((0,0), size)
    hexa.fill(black)
    hexa.set_colorkey(black)
    pygame.draw.polygon(hexa, darkg, pl,)
    pygame.draw.polygon(hexa, colr, pl2,)
    return hexa

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
        return Squad([rand_unit(rand_element(),'Scient') for i in range(size)])
    
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
        self.font = FONT
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
        
        if view.game.state['num'] == 1:
            self.squad = view.battle.defsquad
            self.not_squad = view.battle.atksquad
        elif view.game.state['num'] % 2 == 1:
            self.squad, self.not_squad = self.not_squad, self.squad
        
        if len(self.squad) > 0:
            squad = Squad()
            squad.name = self.squad.name
            for x in reversed(sorted(self.squad, key=lambda t: t.hp)): squad.append(x)
            self.squad = squad
            self.text = []
            self.title = self.squad.name + " Inital Value: " + str(self.squad.value)
            self.last_line = - 1
            #cpu time < human time:
            self.squad.text = []
            #ugh the units are sorted by something...
            for i in xrange(len(self.squad)):
                #Some of these values only need to be computed once.
                #This should really be done by a function in battlepane.Scient
                unit = self.squad[i]
                if unit.hp > 0:
                    unit.text = [] #oops...
                    if self.squad[i].name == None:
                        name = str(self.squad[i].location)
                    else:
                        name = self.squad[i].name
                    
                    squ_txt = name + " V: " + str(self.squad[i].value())
                    self.text.append((squ_txt, darkg, white))
                    unit.text.append("HP: " + str(unit.hp))
                    unit.text.append("E, F, I, W")
                    unit.text.append(str(unit.comp[E]) + ", " + str(unit.comp[F]) + ", " + str(unit.comp[I]) +  ", " + str(unit.comp[W]))
                    if unit.weapon.type in ('Sword', 'Bow'):
                        atk = "PA: " + str(unit.patk)
                    else:
                        atk = "MA: " + str(unit.matk)
                    unit.text.append("Weapon: " + unit.weapon.type)
                    unit.text.append(atk)
                    unit.text.append("PD: " + str(unit.pdef) + " MD: " + str(unit.mdef))
                    unit.text.append("Location: " + str(unit.location))
            
            self.text
            self.last_line = len(self.text) - 1
        else:
            #set next move to pass; send to game; which should end the game.
            
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
            view.set_action(self.unit, view.current_action['type'], view.current_action['target'])
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
        
        if view.game.state['num'] % 2 == 1:
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
            if view.game.state['num'] % 2 == 1:
                view.bottom.title = "Skip both actions?"
            else:
                view.bottom.title = "Skip second action?"
            view.bottom.text.append(("Cancel", darkg, red))
            view.bottom.text.append(("Confirm", darkg, green))
        if self.text[self.cursor_pos][0] == 'Cancel':
            view.bottom.title = "Select another Unit?"
    
    def process_return(self):
        if self.text[self.cursor_pos][0] != 'Cancel':
            atype = self.text[self.cursor_pos][0].lower()
            view.set_action(view.current_action['unit'], atype, view.current_action['target'])
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
                area  = set(view.battle.map_to_grid(self.move[self.cursor_pos], view.unit.weapon))
                area -= view.loc
                view.battle.color_tiles(area - view.move, pink)
                view.battle.color_tiles(area & view.move, purp)
                view.battle.set_tile_color(self.move[self.cursor_pos], white)
            if self.action == 'attack':
                view.draw_grid('Targets')
                if view.unit.weapon.type == 'Wand':
                    area = view.battle.calc_AOE(view.unit, self.targets[self.cursor_pos])
                    view.battle.color_tiles(area, green)
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
                view.set_action(view.current_action['unit'], view.current_action['type'], dest)
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
    

class BattlePane(Pane, Battlefield):
    """Pane that displays the battlefield"""
    def __init__(self,  position, grid, tilesize, tiles):
        #NOTE: This object has Player information that a battlefield does not have.
        #pane_area = (((tilesize* tiles[0]) + tilesize/2), ((tilesize * tiles[1]) +4))
        pane_area = ((34 * (tiles[0] + 1) + 5), (30 * tiles[1]) + 5)
        Battlefield.__init__(self)
        
        Pane.__init__(self, pane_area, title=None)
        self.bgcolor = black
        self.rect.x, self.rect.y = position
        
        self.grid = grid
        self.contentimgs = pygame.sprite.RenderUpdates()
        self.defender = battle.Player()
        self.attacker = battle.Player()
        self.defender.squads = [self.trans_squad(yaml_store.load('yaml/ice_mins.yaml'))]
        self.attacker.squads = [self.trans_squad(yaml_store.load('yaml/fire_mins.yaml'))]
        
        self.defsquad = self.defender.squads[0]
        self.atksquad = self.attacker.squads[0]
        
        self.defender.name = 'Defender'
        self.defsquad.num  = '1'
        
        self.attacker.name = 'Attacker'
        self.atksquad.num  = '2'
                
        self.squads = (self.defsquad, self.atksquad)
        self.units = self.get_units()
        for u in self.units:
            u.draw_text()
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
        for x in xrange(self.grid.x):
            for y in xrange(self.grid.y):
                if self.grid[x][y].contents:
                    self.grid[x][y].contents.rect.topleft = \
                    self.grid[x][y].rect.x, self.grid[x][y].rect.y
                    self.grid[x][y].contents.draw_text()
                    self.contentimgs.add(self.grid[x][y].contents)
    
    def move_scient(self, src, dest):
        Battlefield.move_scient(self, src, dest)
        xpos, ypos = dest
        self.grid[xpos][ypos].contents.rect.topleft = \
        self.grid[xpos][ypos].rect.x, self.grid[xpos][ypos].rect.y
        self.set_tile_color(src, grey)
        return True #need this for logging.
    
    def place_nescient(self, nescient, dest):
        nsci = nescient 
        Battlefield.place_nescient(self, nsci, dest)
        r,s,hexh,rech,size = nsci.hexparams
        nsci.image.fill(black)
        for part in nsci.body:
            if part != None:
                xpos, ypos = nsci.body[part].location
                p_i = nsci.rects[part]
                if ypos&1:
                    p_i.topleft = [((xpos * p_i.width) + .5*p_i.width), (ypos*(hexh + s))]
                else:
                    p_i.topleft = [(xpos * p_i.width), (ypos*(hexh + s))]
                nsci.image.blit(nsci.hex, p_i)
        self.contentimgs.add(nsci)
    
    def place_object(self, unit, dest):
        Battlefield.place_object(self, unit, dest)
        """
        xpos, ypos = dest
        self.grid[xpos][ypos].contents.rect.topleft = \
        self.grid[xpos][ypos].rect.x, self.grid[xpos][ypos].rect.y
        self.contentimgs.add(self.grid[xpos][ypos].contents)
        """
    
    def bury(self, unit):
        unit.remove(unit.groups())
        Battlefield.bury(self, unit)
    
    def flush_units(self):
        Battlefield.flush_units(self)
        self.contentimgs.empty()
    
    class Part(object):
        def hp_fget(self):
            return self.nescient.hp
            
        def hp_fset(self, hp):
            self.nescient.hp = hp
            
        hp = property(hp_fget, hp_fset)
        
        def __init__(self, nescient, location=None):
            self.nescient = nescient
            self.location = location
            self.image = None
            self.rect = pygame.rect.Rect((0,0), [34, 39])
    
    def make_parts(self, part_locs):
        new_body = {}
        for part in part_locs:
            new_body[part] = self.Part(None, part_locs[part])
    
    def trans_squad(self, squad):
        """hack to get a squad from yaml_store"""
        out = Squad()
        out.name = squad.name
        for unit in squad:
            if isinstance(unit, Scient):
                dude = BattlePane.Scient(scient=unit)
            else:
                dude = BattlePane.Nescient(nescient=unit)
                for (k, v) in dude.__dict__.items():
                    print "%s: %s" %(k, v)
            
            if dude.location == noloc:
                self.rand_place_scient(dude)
            else:
                loc = dude.location
                dude.location = noloc
                self.place_object(dude, loc)
            out.append(dude)
        return out
    
    class Scient(pygame.sprite.Sprite, Scient):
        """tricky"""
        def __init__(self, element=None, comp=None, scient=None, hexparams=get_hex_params(35)):
            if scient != None:
                Scient.__init__(self, scient.element, scient.comp, scient.name,
                                scient.weapon, scient.weapon_bonus, scient.location)
            else:
                if element == None:
                    element = rand_element()
                if comp == None:
                    comp = rand_comp(suit=element, kind='Scient')
                Scient.__init__(self, comp=comp, element=element)
            pygame.sprite.Sprite.__init__(self)
            self.hexparams = hexparams
            r,s,hexh,rech,size = self.hexparams
            self.size = size
            self.image = pygame.Surface(size)
            self.image.fill(COLORS[self.element])
            self.image.fill(black)
            if self.weapon.type == 'Sword':
                x = r/2
                y = hexh
                self.rect = pygame.draw.polygon(self.image, COLORS[self.element], [(x, y), (x+s, y), (x+s, y+s), (x, y+s)]) #square
            elif self.weapon.type == 'Bow':
                self.rect = pygame.draw.circle(self.image, COLORS[self.element], ((size[0]/2) + 1, (size[1]/2) + 1), size[0]/2 - hexh/2) # cirlcle
            elif self.weapon.type == 'Wand':
                self.rect  = pygame.draw.polygon(self.image, COLORS[self.element], [(r+1,3), (2*r - 1 , rech-2*hexh), (r+1, rech-3), (2, rech - 2*hexh)])
            elif self.weapon.type == 'Glove':
                self.rect = pygame.draw.polygon(self.image, COLORS[self.element], [(r,2), (2*r-2, rech-hexh-1), (2, rech - hexh-1)]) # triangle
            self.image.set_colorkey(black)
            self.text = []
        
        def __repr__(self):
            return Scient.__repr__(self)
            
        def draw_text(self):
            """a crude, crude hack."""
            self.font = FONT
            self.font_color = [0, 0, 0]
            textrect = self.font.render(self.container.num, True, self.font_color, \
            COLORS[self.element])
            self.image.blit(textrect, (self.size[0]/2 - 4, self.size[1]/3))
    
    class Nescient(pygame.sprite.Sprite, Nescient):
        """trickier"""
        def __init__(self, element=None, comp=None, nescient=None, hexparams=get_hex_params(35)):
            if nescient != None:
                Nescient.__init__(self, nescient.element, nescient.comp, nescient.name,
                                nescient.weapon, nescient.location, nescient.facing, nescient.body)
            else:
                if element == None:
                    element = rand_element()
                if comp == None:
                    comp = rand_comp(suit=element, kind='Nescient')
                Nescient.__init__(self, comp=comp, element=element)
            
            pygame.sprite.Sprite.__init__(self)
            self.hexparams  = hexparams
            self.image = pygame.Surface((577, 560))
            self.hex = make_hex(self.hexparams, COLORS[self.element])
            self.body = None
            
            self.images = {'head':None, 'left':None, 'right':None, 'tail':None}
            self.rects  = {'head':None, 'left':None, 'right':None, 'tail':None}
            
            for part in self.images:
                #self.images[part] = make_hex(self.hexparams, COLORS[self.element], self.image)
                #self.rects[part]  = self.images[part].get_rect()
                self.rects[part]  = pygame.rect.Rect((0,0), self.hexparams[-1])
            self.rect = self.image.get_rect()
            self.image.set_colorkey(black)
            self.text = []
        
        def __repr__(self):
            return Nescient.__repr__(self)
        
        def draw_text(self):
            """a crude, crude hack."""
            self.font = FONT
            self.font_color = [0, 0, 0]
            textrect = self.font.render(self.squad.num, True, self.font_color, \
            COLORS[self.element])
            self.image.blit(textrect, (self.rect.width/2 - 4, self.rect.height/3))
    
    class Tile(pygame.sprite.Sprite, Tile):
        """it's a battlefield tile and a pygame sprite, yo"""
        def make_hex(self, hexparams, colr):
            """returns a Surface containing a hextile"""
            r,s,hexh,rech,size = hexparams
            recw = 2 * r
            pl = [(0, hexh), (r,0), (recw,hexh), (recw, rech-hexh), (.5*recw, rech), (0, rech - hexh)]
            pl2 = [(1, 1+hexh), (.5*recw,2), (recw-2,hexh+1), (recw-2, rech-hexh-1), (.5*recw, rech-2), (2, rech - hexh-1)]
            hexa = pygame.Surface(size)
            hexa.fill(black)
            hexa.set_colorkey(black)
            pygame.draw.polygon(hexa, darkg, pl,)
            pygame.draw.polygon(hexa, colr, pl2,)
            return hexa
        
        def __init__(self,  topleft, hexparams, colr=grey):
            pygame.sprite.Sprite.__init__(self)
            Tile.__init__(self)
            self.hexparams = hexparams
            self.image = make_hex(self.hexparams, colr)
            self.rect = self.image.get_rect()
            self.rect.topleft = topleft
        
        def set_color(self, color):
            self.image = make_hex(self.hexparams, color)
            #self.image.fill(color)
    
    class Grid(pygame.sprite.Sprite, Grid):
        def __init__(self, *args, **kwargs):
            pygame.sprite.Sprite.__init__(self)
            self.tilesize = kwargs['tilesize']
            self.tiles    = kwargs['tiles']
            self.image    = pygame.Surface(((self.tilesize*self.tiles[0] + int(self.tilesize/2)), self.tilesize*self.tiles[1]))
            self.image.set_colorkey(black)
            self.rect     = self.image.get_rect()
            self.rect.x, self.rect.y = (242, TOPINSET)
            self.x,self.y = self.tiles
            Grid.__init__(self, x=self.x, y=self.y)
            
            self.hexparams = kwargs['hexparams']
            hexh = self.hexparams[2]
            s    = self.hexparams[1]
            for xpos in range(self.x):
                for ypos in range(self.y):
                    tile = BattlePane.Tile((xpos,ypos), self.hexparams, grey)
                    if ypos&1:
                        tile.rect.topleft = [(xpos*tile.rect.width) + .5*tile.rect.width + 4, (ypos*(hexh +s)) + 4]
                        self.image.blit(tile.image, tile.rect)
                    else:
                        tile.rect.topleft = [(xpos*tile.rect.width) + 4, (ypos*(hexh + s)) + 4]
                        self.image.blit(tile.image, tile.rect)
                    self[xpos][ypos] = tile
            self.image.set_colorkey(black)

class Game(battle.Game):
    def __init__(self, grid, defender, attacker, battlefield):
        battle.Game.__init__(self, grid, defender, attacker)
        self.battlefield = battlefield
        
class View:
    def __init__(self, screen, grid):
        self.grid = grid
        self.top    = TopPane((LEFTINSET,TOPINSET))
        self.middle = MiddlePane((LEFTINSET, (TOPINSET + PANE_HEIGHT + PANE_SPACING)))
        self.bottom = BottomPane((LEFTINSET, (TOPINSET + 2 *(PANE_HEIGHT + PANE_SPACING))))
        #the name battle is hardcoded into pyconsole.py
        #self.defender = battle.Player()
        #self.attacker = battle.Player()
        
        self.battle = BattlePane((242, TOPINSET + 1), self.grid, tilesize=51, tiles=(16,16))
        self.game = Game(self.grid, self.battle.defender, self.battle.attacker,
                                self.battle)
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
        self.current_action = battle.Action()
        self.last_action_type = None
        while True:
            key = (yield)
            self.current_state.process_key(key)
    
    def clean(self):
        """Resets the color of all tiles"""
        for x in range(self.battle.grid.x):
            for y in range(self.battle.grid.y):
                self.battle.set_tile_color((x,y), grey)
    
    def make_tile_sets(self, unit): #TODO move to py
        """Make area, move, targets tile sets for unit."""
        self.unit  = unit
        self.area  = set(self.battle.map_to_grid(self.unit.location, self.unit.weapon))
        self.move  = set(self.battle.make_range(self.unit.location, self.unit.move))
        self.units = set(self.battle.find_units())
        self.move -= self.units #can't moved to occupied tiles
        self.loc   = set((self.unit.location,),)
        self.targets = self.area & (self.units)
    
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
    
    def set_action(self, unit, atype, target):
        """sets the properties of the current action"""
        self.current_action = battle.Action(unit, atype, target)
    
    def send_action(self):
        """sends the current action to the game"""
        #if first action in ply is pass, set second to same
        text = []
        if self.current_action['type'] == 'pass':
            if view.game.state['num'] % 2 == 1:
                text += self.game.process_action(self.current_action)
        text += self.game.process_action(self.current_action)
        '''
        send_action is only called from the bottom pane and we should move to
        the top pane only when the ply is full, otherwise, move to the middle.
        '''
        if view.game.state['num'] % 2 == 1:
            self.last_action_type = None
            self.transition(view.top)
        else:
            self.make_tile_sets(self.unit)
            self.last_action_type = self.current_action['type']
            self.transition(view.middle)
        
        """if view.game.state['num'] % 4 == 0: #buggy?
            #for x in view.battle.dmg_queue.iteritems(): print x
        for i in text:
            print i
            view.console.output(i)"""
        
    def transition(self, dest_state):
        """transitions from current_state to dest_state"""
        self.current_state.active = False
        self.current_state = dest_state
        self.current_state.active = True
        self.current_state.set_state()
        self.current_state.draw_other_panes()
    
###
if __name__ == '__main__':
    print "Copyright (c) 2010 A. Frederick Dudley. All rights reserved. PLEASE DO NOT REDISTRIBUTE"
    pygame.init()
    FONT =  pygame.font.Font('views/DroidSansMono.ttf', 12)
    screen = pygame.display.set_mode([850, 600])
    
    grid = BattlePane.Grid(tiles=(16,16), tilesize=35, hexparams=get_hex_params(35))
    view = View(screen, grid)
    view.state = view.get_key()
    view.game.defender.name = "Defender"
    view.game.attacker.name = "Attacker"
    view.console.active = 0
    paneimgs = pygame.sprite.RenderUpdates()
    for pane in (view.top, view.middle, view.bottom, view.battle):
        paneimgs.add(pane)
    ############
    '''
    def bye():
        view.clean()
        view.battle.flush_units()
    right = (7,6)
    body = view.battle.make_body(right, 'North')
    rotate = view.battle.rotate
    draw   = view.battle.set_tile_color
    n = BattlePane.Nescient(E, (4,4,0,0))
    view.battle.place_object(n, (4,4))
    '''
    ###############
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

