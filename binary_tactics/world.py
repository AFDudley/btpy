from binary_tactics.battlefield import Tile, Grid
from binary_tactics.battle import player

class World(object):
    """Object that contains all the fields within a world.""" 
    def __init__(self, name, x=16, y=16):
        self.name = name
        self.x, self.y = self.size = (x, y)
        self.fields = {}
        for i in range(x):
            bar = {}
            for j in range(y):
                bar.update({j: Grid()})
            self.fields.update({i: bar})

    def __iter__(self):
        return iter(self.fields)
    def __contains__(self, value):
        return value in self.fields
    def __getitem__(self,key):
        return self.fields[key]
    def __setitem__(self,key,value):
        self.fields[key] = value
    def __len__(self):
        return len(self.fields)
    def __repr__(self):
        return dict.__repr__(self.fields)        