import transaction
import persistent
import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.helpers import *
from binary_tactics.units import Squad
from binary_tactics.grid import Grid
from equanimity.stronghold import Stronghold
from equanimity.clock import Clock
from operator import itemgetter
from random import choice


class Field(persistent.Persistent):
    def set_element(self):
        """Sets the element of the field based on grid.comp and magic."""
        sort = sorted(self.grid.comp.iteritems(), key=itemgetter(1), reverse=True)
        if sort[0][1] == sort[3][1]: #they are all equal
            self.element = choice(sort)[0]
        elif sort[0][1] == sort[2][1]:
            self.element = choice(sort[:3])[0]
        elif sort[0][1] == sort[1][1]:
            self.element = choice(sort[:2])[0]
        else:
            self.element = sort[0][0]
        return transaction.commit()
            
    def __init__(self, world_coord, ply_time=240):
        self.world_coord = world_coord
        self.owner = 'World'
        self.grid = Grid()
        self.element = self.set_element()
        self.stronghold  = Stronghold(self.create_defenders())
        self.battlequeue = persistent.list.PersistentList()
        self.producers   = None #stuctures, input stones, output composites.
        self.value       = None
        self.expected_yield = None
        self.state = 'produce' #Default state
    
        """
        ply_time: user definable time before a pass is automatically sent for a battle action.
            range between 4 and 360 minutes, default is 4 (in seconds)
        """
        self.ply_time = ply_time
        
    def set_owner(self, owner):
        self.owner = owner
        return tranaction.commit()
    
    def change_state(self):
        if self.battleque:
            self.state = 'battle'
        elif self.element == Clock().get_time('season'):
            self.state = 'harvest'
        else:
            self.state = 'produce'
        return transaction.commit()
        
    def create_defenders(self):
        """creates the stronghold defenders of a field with random scients.
        (should be nescients)"""
        #this function should calcuate the composition of the units based on the
        #composition of the grid, that will be handled in due time.
        return Squad(kind='mins', element=self.element)

    def get_defenders(self):
        """gets the defenders of a Field."""
        try:
            return self.stronghold.defenders
        except:
            raise Exception("Stronghold has no defenders.")
    
    def plant(self, tileLoc, stone):
        """Plants a stone on a tile."""
        self.grid.imbue_tile(tileLoc, stone)
        self.grid[tileLoc[0]][tileLoc[1]]._p_changed = 1
        self.grid._p_changed = 1
        self.set_element()
        return transaction.commit()
        
    def harvest(self):
        """returns set of stones generated at harvest"""
        #this needs to be more clever and relate to the units in
        #the stronghold somehow.
        stone_list = []
        for x in xrange(self.grid.x):
            for y in xrange(self.grid.y):
                stone = Stone()
                for suit, value in self.grid[x][y].comp.iteritems():
                    stone[suit] += value / 8 #this 8 will need to be tweaked.
                if stone.value() != 0:
                    stone_list += [stone]
        self.stronghold.stones += stone_list
        return transaction.commit()
    
