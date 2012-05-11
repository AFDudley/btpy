from stone import Stone
class Field(object):
    def __init__(self, grid, attack_queue=None, owner=None):
        self.attack_queue = attack_queue
        self.grid = grid
        '''fiels should only be created at world creation time and should init
           with The World as the owner.'''
        self.owner = owner
        """
        ply_window: user definable time before a pass is automatically sent for a battle action.
            range between 4 and 360 minutes, default is 4
        """
        self.ply_window = 4
        
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