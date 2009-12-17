"""contains battlefield objects"""
from warnings import warn
from const import COMP, ELEMENTS, E, F, I, W, ORTH
import random
from defs import Scient

from helpers import rand_squad, unit_repr, show_squad

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
    There is some args/kwargs magic here, one day it will be documented    
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
                temp += Tile((xpos, ypos)),
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
    #should take two "squad" objects; if none given generate "random" squads
    def __init__(self):
        #grid is a tuple of tuples containing tiles
        self.grid = None
        self.graveyard = []
        self.clock = 0
        self.ticking = False
        self.queue = []
        self.status_effects = []
        self.squad1 = None
        self.squad2 = None
        
    def make_empty_grid(self):
        self.grid = Grid()
    
    def load_grid(self, grid=Grid()):
        """Loads grid into battlefield, otherwise loads an 'empty' grid"""
        self.grid = grid
    
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
    
    def rand_place_squad(self, squad):
        """place the units in a squad randomly on the battlefield"""
        for unit in range(len(squad)):
            #readable?
            def RandPos(): return (random.randint(0, (self.grid.x - 1)),
                random.randint(0, (self.grid.y - 1)))
            while squad[unit].location == None:
                try:
                    self.place_unit(squad[unit], RandPos())
                    break
                except Exception:
                    nope = RandPos()
                    self.place_unit(squad[unit], nope)
                    
    def find_units(self):
        list = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y].contents:
                    list.append((x,y))
        return list
        
    def flush_units(self):
        """remove all units from grid, returns number of units flushed"""
        count = 0
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y].contents:
                    self.grid[x][y].contents.location = None
                    self.grid[x][y].contents = None
                    count += 1
        return count

#    def process(self, command):
#        """Process a battle command (move, act, or both) for unit"""
#        fst_cmd, fst_args = command[0]
#        snd_cmd, snd_args = command[1]
#        fst_cmd(*fst_args)
#        snd_cmd(*snd_args)

#    def act(self, action, args):
#        action(*args)

