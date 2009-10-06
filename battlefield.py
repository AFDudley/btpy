from comp import COMP

#there is a serious problem in this logic. it assumes that units fit on one tile, nesceints do not.
class Tile(object):
    def __init__(self):
        self.comp = COMP
        self.contents = None
        
class Grid(object):
    def __init__(self):
        self.tiles = {} #Tiles indexed by (x,y)
        self.units = {} 
    
    def place_tiles(self, width, length):
        """Creates Tiles and places them in grid"""
        for x in range(width):
            for y in range(length):
                self.tiles[(x,y)] = Tile()
                
    def get_tile(self, tile):
        """Returns the object at tile location (x,y)"""
        return self.tiles[tile]

#    def clear_tile(self, tile):
#        """Clears the unit from tile (x,y)"""
#        del self.units[self.tiles[tile]] #XXX: maybe just assign to None, don't delete it
#        del self.tiles[tile]

    def place_unit(self, u, tile):
        """Places unit u at tile (x,y)"""
        self.units[u] = tile
        self.tiles[tile].contents = u

    def move_unit(self, u, tile):
        """Moves unit u from its current location to tile"""
        #del self.tiles[self.units[u]]
        #self.tiles[tile].contents = u
        #self.units[u] = tile
        
    def get_unit(self, u):
        """Returns the location of unit u"""
        return self.units[u]

    def remove_unit(self, u):
        """Removes the unit from the tile it is on"""
        del self.tiles[self.units[u]]
        del self.units[u] #XXX: maybe just assign to None, don't delete it


class Battlefield(Grid):
    """A battlefield is a map of tiles which contains units and the logic for their movement and status."""
    def __init__(self):
        self.graveyard = []
        self.clock = 0
        self.ticking = False
        self.queue = []
        self.status_effects = []
        super(Battlefield, self).__init__()
    
    def place_unit(self, unit, tile):
        """Places unit at tile (x,y), raises exception if a unit is already on that tile"""
        x,y = tile
        if not self.tiles[tile].contents in self.tiles:
            super(Battlefield, self).place_unit(unit, tile)
        else:
            raise Exception("Unit already in place on that tile")

    def kill_unit(self, tile):
        """Kills the unit at tile (x,y), raises exception if no unit is found"""
        #needs to check that it's actually a unit and not a stone.
        if self.tiles[tile] != None:
            self.graveyard.append(self.tiles[tile].contents)
            self.grid[x][y] = None #TODO: drop that unit's stone at this tile
        else:
            raise Exception("No unit found at that tile")

    def move_unit(self, unit, tile):
        x,y = tile
        if not tile in self.tiles:
            x0,y0 = self.get_unit(unit)
            if abs(x-x0) + abs(y-y0) <= unit.move:
                super(Battlefield, self).move_unit(unit, tile)
                pass
            else:
                raise Exception("Moved too many spaces")

    def process(self, command):
        """Process a battle command (move, act, or both) for unit"""
        fst_cmd, fst_args = command[0]
        snd_cmd, snd_args = command[1]
        fst_cmd(*fst_args)
        snd_cmd(*snd_args)

    def act(self, action, args):
        action(*args)
