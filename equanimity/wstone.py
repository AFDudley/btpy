from binary_tactics.stone import Stone as cStone
from persistent import Persistent

class Stone(Persistent, cStone):
    def __init__(self, comp=None):
        cStone.__init__(self, comp)
    
    def __repr__(self):
        return str(self.comp)
