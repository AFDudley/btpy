"""contains battlefield objects"""
from const import COMP, ELEMENTS, ORTH
import random
from defs import Scient
def rand_scient():
    """Returns a not that random scient"""
    comp = COMP
    suit = random.choice(ELEMENTS)
    comp[suit] = random.randint(1, 255)
    for zippy in ORTH[suit]: comp[zippy] = comp[suit] / 2
    return Scient(suit, comp)

def rand_squad():
    """Returns a squad of 5 "random" Scients"""
    squad = []
    for times in range(5):
        squad.append(rand_scient())
    return squad

#there is a serious problem in this logic. it assumes that units fit on one
#tile, nesceints do not.
class Tile(object):
    """Tiles are contained in battlefields and hold units and stones"""
    def __init__(self, location = ()):
        self.comp = COMP
        self.contents = None
        self.location = location # makes abstraction a little easier.


class Battlefield(object):
    """A battlefield is a map of tiles which contains units and the logic for
    their movement and status."""
    #should take two "squad" objects; if none given generate "random" squads
    def __init__(self):
        #grid is a tuple of tuples containing tiles
        self.grid = ()
        self.gridx = None
        self.gridy = None #is this line and 1 below confusing?
        #self.gridsize = self.gridx*self.gridy
        self.graveyard = []
        self.clock = 0
        self.ticking = False
        self.queue = []
        self.status_effects = []
        self.squad1 = None
        self.squad2 = None
        
    def make_empty_grid(self):
        """makes a list of empty tiles"""
        if self.gridx == None or self.gridy == None:
            Exception("didn't set grid x and/or y")
        else:
            for xpos in range(self.gridx):
                qui = ()
                for ypos in range(self.gridy):
                    qui = qui + (Tile((xpos, ypos)), )
                self.grid = self.grid + (qui,)
    
    def load_grid(self, grid=None):
        """Loads grid into battlefield, otherwise loads an 'empty' grid"""
        #should do some checking here (duh)
        if grid is not None:
            self.grid = grid
        else:
            self.gridx = 16
            self.gridy = 16 #hope i remember this is here...
            self.make_empty_grid()
    
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
        """Places unit at tile (x,y), raises exception if a unit is already on
        that tile"""
        xpos, ypos = tile
        if not self.grid[xpos][ypos].contents:
            self.grid[xpos][ypos].contents = unit
            unit.location = (xpos, ypos)
        else:
            raise Exception("tile is already filled")
    
    def rand_place_squad(self, squad):
        """place the units in a squad randomly on the battlefield"""
        #non-destructive; tricky? should be done with exceptions
        for scient in range(len(squad)):
            #bullheaded
            xpos = random.randint(0, (self.gridx - 1))
            ypos = random.randint(0, (self.gridy - 1))
            while self.grid[xpos][ypos].contents is not scient:
                if self.grid[xpos][ypos].contents is not None:
                    xpos = random.randint(0, (self.gridx - 1))
                    ypos = random.randint(0, (self.gridy - 1))
                    break
                else:
                    self.place_unit(squad[scient], (xpos, ypos))
    
    def move_scient(self, src, dest):
        """move scient from a tile to another tile"""
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
                    raise Exception("Moved too many spaces")
            else:
                raise Exception("There is already something at dest")
        else:
            raise Exception("There is nothing at src")
    

#    def process(self, command):
#        """Process a battle command (move, act, or both) for unit"""
#        fst_cmd, fst_args = command[0]
#        snd_cmd, snd_args = command[1]
#        fst_cmd(*fst_args)
#        snd_cmd(*snd_args)

#    def act(self, action, args):
#        action(*args)
    
