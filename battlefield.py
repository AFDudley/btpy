"""contains battlefield objects"""
from warnings import warn
from operator import contains
import random

from const import COMP, ELEMENTS, E, F, I, W, ORTH
from defs import Scient
from helpers import rand_squad

#Battlefield needs a coord class
#there is a serious problem in this logic. it assumes that units fit on one
#tile, nesceints do not.
class Tile(object):
    """Tiles are contained in battlefields and hold units and stones"""
    def __init__(self, location = ()):
        self.comp = COMP.copy() #Currently any 4 values 0...255
        self.contents = None
        self.location = location # makes abstraction a little easier.

class Grid(tuple):
    """
    Creates a grid of empty tiles sized 2-tuple
    There is some args/kwargs magic here, one day it will be documented or
    removed.  
    """
    #boy do i ever need some type checking :D
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
        for xpos in range(x):
            temp = ()
            for ypos in range(y):
                temp += Tile((xpos,ypos)),
            grid += temp,
        return tuple.__new__(cls, grid)

    def __init__(self, *args, **kwargs):
        # make a grid, if no size given make it (16, 16) 
        if not args:
            try:
                self.size = kwargs['size']
            except KeyError:
                self.size = (16, 16)
        else:    
            self.size = args[0]
        self.x,self.y = self.size
        try: 
            self.comp = kwargs['comp']
            self.make_grid(self.comp)
        except KeyError:
            self.comp = {E:0, F:0, I:0, W:0}
                
    def make_grid(self, avg):
        """
        transforms an empty grid to one with an average composition of COMP
        called by __init__
        """
        print "make_grid was called"
 
class Battlefield(object):
    """A battlefield is a map of tiles which contains units and the logic for
    their movement and status."""
    def __init__(self, squad1=None, squad2=None):
        #grid is a tuple of tuples containing tiles
        self.grid = None
        self.turn = 0
        self.graveyard = []
        self.dmg_queue = []
        self.squad1 = squad1
        self.squad2 = squad2

    def load_squads(self, squad1=None, squad2=None):
        """loads squads into battlefield, uses random if none provided"""
        #need better checks, duh
        if squad1 is not None:
            self.squad1 = squad1
        else:
            self.squad1 = rand_squad()

        if squad2 is not None:
            self.squad2 = squad2
        else:
            self.squad2 = rand_squad()
    
    def place_unit(self, unit, tile):
        """Places unit at tile, if already on grid, move_unit is called"""
        xpos, ypos = tile 
        if unit.location == None and self.grid[xpos][ypos].contents == None:
            self.grid[xpos][ypos].contents = unit
            unit.location = (xpos, ypos)
            
        elif unit.location == (xpos, ypos):
            raise Exception("This unit is already on (%s,%s)" %(xpos, ypos))
        
        elif self.grid[unit.location[0]][unit.location[1]].contents != unit:
            raise Exception(
            "unit and battlefield do not agree on unit location")
        
        elif self.grid[xpos][ypos].contents != None:
            raise Exception("(%s, %s) is not empty" %(xpos, ypos))
        
        else:
            warn("Place_unit called instead of move_unit")
            self.move_unit(unit.location, (xpos, ypos))

    def move_unit(self, src, dest):
        """move unit from src tile to dest tile"""
        xsrc, ysrc = src
        xdest, ydest = dest
        if self.grid[xsrc][ysrc].contents:
            if not self.grid[xdest][ydest].contents:
                if abs(xsrc-xdest) + abs(ysrc-ydest) <= \
                self.grid[xsrc][ysrc].contents.move:
                    self.grid[xdest][ydest].contents = \
                    self.grid[xsrc][ysrc].contents
                    self.grid[xdest][ydest].contents.location = (xdest, ydest)
                    self.grid[xsrc][ysrc].contents = None
                else:
                    raise Exception("tried moving too many spaces")
            else:
                raise Exception("There is already something at dest")
        else:
            raise Exception("There is nothing at src")

    def find_units(self):
        list = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y].contents:
                    list.append((x,y))
        return list    
        
    def dmg(atkr, defdr, type):
        """Calculates the damage of an attack"""
        damage_dealt = {E: 0, F: 0, I: 0, W: 0}
        xdef,ydef = defdr.location
        for element in damage_dealt:
            dmg = (atkr.p + atkr.patk + (2 * atkr.comp[element]) \
            + atkr.weapon.comp[element]) - (defdr.p + defdr.pdef \
            + (2 * defdr.comp[element]) + self.grid[x][y].comp[element])
            dmg = max(dmg, 0)
            damage_dealt[element] = dmg
             
        damage = sum(damage_dealt.values())
        if type == 'm':
            if atkr.element == defdr.element:
                damage = 0 - damage
        return damage
    
    def find_targets(self, tiles):
        """finds valid targets on tiles. returns list of coords"""
        return list(set(find_units()) & set(tiles))
        

    def calc_damage(self, unit, vector):
        """Calculates damage of all units "between" unit and vector
        Returns list of (target, dmg) tuples"""        
        #this all happens here because the battlefield needs tile info
        #this can be optimized, the logic is skewed toward ranged attacks.
        atkr = unit
        weapon = atkr.weapon
        vecx,vecy = vector
        dmg_list = []
        tiles = weapon.map_to_grid(unit.location, self.grid)
        if tiles <= 0: 
            raise Exception("somehow the weapon attack pattern doesn't map")
        targets = self.find_targets(tiles)
        if targets == None: 
            raise Exception("No Valid Targets in range")
        for i in xrange(len(targets)): # sub-optimal, readable.
            defdr = self.grid[targets[i][0]][targets[i][1]].contents
            if contains(ORTH[W], weapon.type): #physical attacks
                dmg = self.dmg(atkr, defdr, 'p')
                if dmg != 0:
                    if weapon.type == 'Earth':
                        dmg_list.append(defdr, dmg)
                    else:
                        dmg_list.append(defdr, (dmg / 4))
            else: #magical attacks
                dmg = self.dmg(atkr, defdr, 'm')
                if dmg > 0:
                    if weapon.type == 'Wind':
                        dmg /= 3
                        dmg_list.append(defdr, dmg)
                        self.dmg_queue.append(defdr, dmg, 2) 
                    else:
                        dmg_list.append(defdr, dmg / len(tiles))
        return dmg_list

    def apply_damage(self, dmg_list):
        """applies damage to unit"""
        for i in dmg_list:
            defndr,dmg = i
            if dmg >= defdr.hp:
                defdr.hp = 0
                self.grid[defdr.location[0]][defdr.location[1]].contents = None
                defdr.location = None
                #Do some squad stuff
                #Do some graveyard stuff
            else:
                defdr.hp -= dmg

    def attack(self, atkr, defdr):
        self.apply_damage(self.calc_damage(atkr,defdr))
        
    def rand_place_squad(self, squad):
        """!!!BROKEN!!! place the units in a squad randomly on the battlefield"""
        for unit in range(len(squad)):
            #readable?
            inset = 10
            def RandPos(): return (random.randint(0, (self.grid.x - inset)),
                random.randint(0, (self.grid.y - inset)))
            while squad[unit].location == None:
                try:
                    self.place_unit(squad[unit], RandPos())
                    break
                except Exception:
                    nope = RandPos()
                    self.place_unit(squad[unit], nope)
                    
    def flush_units(self):
        """
        remove all units from grid, returns number of units flushed,
        does not put them in the graveyard
        """
        count = 0
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y].contents:
                    self.grid[x][y].contents.location = None
                    self.grid[x][y].contents = None
                    count += 1
        return count

    def logger(self):
        """Logs game and optionally stores it in data store"""
        pass
        
    def config(self):
        """Configure the battlefield"""
        '''
        Load Player info
        Create Squads
        Place Squads
        turn on logging
        '''
    
    def start(self):
        """Starts a human controlled game"""
        pass


