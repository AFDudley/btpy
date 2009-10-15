from comp import COMP
from defs import Scient
#there is a serious problem in this logic. it assumes that units fit on one tile, nesceints do not.
class Tile(object):
    def __init__(self, location = ()):
        self.comp = COMP
        self.contents = None
        self.location = location # makes abstraction a little easier.


class Battlefield(object):
    """A battlefield is a map of tiles which contains units and the logic for their movement and status."""
    #should take two "squad" objects; if none given generate "random" squads
    def __init__(self):
        #grid is a tuple of tuples containing tiles
        self.grid = ()
        self.graveyard = []
        self.clock = 0
        self.ticking = False
        self.queue = []
        self.status_effects = []
    
    def make_empty_grid(self, width, length):
        """makes a list of empty tiles"""
        for x in range(width):
            qui = ()
            for y in range(length):
                qui = qui + (Tile((x,y)),)
            self.grid = self.grid + (qui,)
    
    def place_unit(self, unit, tile):
        """Places unit at tile (x,y), raises exception if a unit is already on that tile"""
        x,y = tile
        if not self.grid[x][y].contents:
            self.grid[x][y].contents = unit
        else:
            raise Exception("tile is already filled")
    
    def kill_unit(self, tile):
        """Kills the unit at tile (x,y), raises exception if no unit is found"""
        #needs to check that it's actually a unit and not a stone.
        if self.tiles[tile] != None:
            self.graveyard.append(self.tiles[tile].contents)
            self.grid[x][y] = None #TODO: drop that unit's stone at this tile
        else:
            raise Exception("No unit found at that tile")
    
    def move_scient(self, src, dest):
        "move scient from a tile to another tile"
        xs,ys = src
        xd,yd = dest
        if self.grid[xs][ys].contents:
            if not self.grid[xd][yd].contents:
                if abs(xs-xd) + abs(ys-yd) <= self.grid[xs][ys].contents.move:
                    self.grid[xd][yd].contents = self.grid[xs][ys].contents
                    self.grid[xs][ys].contents = None
                    pass
                else:
                    raise Exception("Moved too many spaces")
            else:
                raise Exception("There is already something at dest")
        else:
            raise Exception("There is nothing at src")
    
    def process(self, command):
        """Process a battle command (move, act, or both) for unit"""
        fst_cmd, fst_args = command[0]
        snd_cmd, snd_args = command[1]
        fst_cmd(*fst_args)
        snd_cmd(*snd_args)
    
    def act(self, action, args):
        action(*args)
    
