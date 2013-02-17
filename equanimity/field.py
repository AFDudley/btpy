import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.units import Squad
from binary_tactics.grid import Grid
from equanimity.stronghold import Stronghold

class wField(persistent.Persistent):
    def __init__(self, world_coord, ply_time=240):
        self.world_coord = world_coord
        self.owner = 'World'
        self.grid = Grid()
        self.stronghold  = Stronghold(self.create_defenders())
        self.battlequeue = persistent.list.PersistentList()
        self.producers   = None #stuctures, input stones, output composites.
        self.value       = None
        self.expected_yield = None

        """
        ply_time: user definable time before a pass is automatically sent for a battle action.
            range between 4 and 360 minutes, default is 4 (in seconds)
        """
        self.ply_time = ply_time

    def create_defenders(self):
        """creates the stronghold defenders of a field with random scients.
        (should be nescients)"""
        #this function should calcuate the composition of the units based on the
        #composition of the grid, that will be handled in due time.
        return Squad(kind='mins', element=rand_element())

    def get_defenders(self):
        """gets the defenders of a wField."""
        try:
            return self.stronghold.defenders
        except:
            raise Exception("Stronghold has no defenders.")
            
    def set_owner(self, owner):
        self.owner = owner

    def harvest_stones(self):
        """returns set of stones generated at harvest"""
        stones = Stone()
        for x in xrange(self.grid.x):
            for y in xrange(self.grid.y):
                for suit, value in self.grid[x][y].comp.iteritems():
                    stones[suit] += value
        for suit, value in stones.iteritems():
            stones[suit] /= 8 #8 seems like a good number... 
        return stones