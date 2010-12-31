from stone import Stone
class Field(object):
    def __init__(self, grid, attack_queue=None, owner=None):
        self.attack_queue = attack_queue
        self.grid = grid
        '''fiels should only be created at world creation time and should init
           with The World as the owner.'''
        self.owner = owner
        
    def set_owner(self, owner):
        self.owner = owner
        
    def harvest_stones(self):
        """returns set of stones generated at harvest"""
        stones = Stone()
        for x in xrange(self.grid.x):
            for y in xrange(self.grid.y):
                for suit, value in self.grid[x][y].comp.iteritems():
                    stones[suit] += value
        return stones