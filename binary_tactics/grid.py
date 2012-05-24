from collections import namedtuple
import random
from math import ceil, sqrt

from stone import Stone

class Loc(namedtuple('Loc', 'x y')):
    __slots__ = ()
    def __repr__(self):
        return '(%r, %r)' %self
noloc = Loc(None, None)

class Tile(Stone):
    """Tiles contain units or stones and are used to make battlefields."""
    def __init__(self, comp=Stone(), contents=None):
        Stone.__init__(self, comp)
        self.contents = contents
        
class Grid(Stone):
    """A grid is a collection of tiles."""
    #The code for generating a set of tiles based on a comp could use clean up
    def __init__(self, comp=Stone(), x=16, y=16, tiles=None):
        Stone.__init__(self, comp)
        self.x, self.y = self.size = (x, y)
        if self.value() == 0:
            if tiles == None:
                self.tiles = {}
                for i in range(x):
                    row = {}
                    for j in range(y):
                        row.update({j: Tile()})
                    self.tiles.update({i: row})
            else:
                for x in xrange(self.x):
                    for y in xrange(self.y):
                        for suit, value in tiles[x][y].iteritems():
                            self.comp[suit] += value
                for suit in self.comp.keys():
                    self.comp[suit] /= self.x * self.y 
                self.tiles = tiles
        else:
            #needs to check for comp/tiles match currently assumes if comp, no tiles.
            #creates a pool of comp points to pull from.
            pool = {}
            for suit, value in self.comp.iteritems():
                pool[suit] = value * self.x * self.y 
            #pulls comp points from the pool using basis and skew to determine the range of random
            #values used create tiles. Tiles are then shuffled.
            tiles_l = []
            for i in xrange(x-1):
                row_l = []
                for j in xrange(y):
                    """This is pretty close, needs tweeking."""
                    new_tile = {}
                    for suit, value in pool.iteritems():
                        '''This determines the range of the tile comps.'''
                        #good enough for the time being.
                        basis = self.comp[suit]
                        skew  = 2*random.randint(2,8)
                        pull  = random.randint(basis-skew, basis+skew)
                        nv = min(pull, pool[suit])
                        pool[suit] -= nv
                        new_tile[suit] = nv
                    row_l.append(new_tile)
                row = {}
                random.shuffle(row_l) #shuffles tiles in temp. row.
                tiles_l.append(row_l)
            #special error correcting row
            row_e = []
            for k in xrange(y): 
                new_tile = {}
                for suit, value in pool.iteritems():
                    if pool[suit] != 0:
                        fract = pool[suit]/max(1, k)
                    else:
                        fract = 0
                    nv = min(fract, pool[suit])
                    pool[suit] -= nv
                    new_tile[suit] = nv
                row_e.append(new_tile)
            #hacks upon hacks pt2
            del row_e[-1]
            half = {}
            for suit, value in row_e[-1].iteritems():
                half[suit] = int(value/2)
                row_e[-1][suit] -= half[suit]
            row_e.append(half)
            tiles_l.append(row_e)
            self.tiles = {}
            random.shuffle(tiles_l) #shuffles temp rows.
            for x in xrange(self.x):
                row = {}
                for y in xrange(self.y): #This shuffles the tiles before putting them in the grid.
                    r_index = random.choice(range(len(tiles_l))) # pick a row
                    c_index = random.choice(range(len(tiles_l[r_index]))) #pick a tile
                    row.update({y: Tile(tiles_l[r_index][c_index])}) #place tile in grid
                    del tiles_l[r_index][c_index] #remove used tile
                    if len(tiles_l[r_index]) == 0: #remove empty rows from tiles_l
                        del tiles_l[r_index]
                self.tiles.update({x: row})
            del tiles_l
    def __iter__(self):
        return iter(self.tiles)
    def __contains__(self, value):
        return value in self.tiles
    def __getitem__(self,key):
        return self.tiles[key]
    def __setitem__(self,key,value):
        self.tiles[key] = value
    def __len__(self):
        return len(self.tiles)
    def __repr__(self):
        return dict.__repr__(self.tiles)
