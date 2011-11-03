from collections import Mapping
from persistent import Persistent
from binary_tactics.const import ELEMENTS, E, F, I, W

class Stone(Persistent, Mapping):
    """ugh."""
    def __init__(self, comp=None):
        self.comp = {'Earth': 0, 'Fire': 0, 'Ice': 0, 'Wind': 0}
        #self.id = randint(1000000000, 2**32)
        if isinstance(comp, Stone):
            self.comp = comp.comp
        if comp == None:
            comp = self.comp
        else:
            try:
                iter(comp)
                if sorted(self.comp) == sorted(comp):
                    self.comp = dict(comp)
                else:
                    if len(comp) == 4 or len(comp) == 0:
                        for element in range(4):
                            if type(comp[element]) == type(1):
                                if 0 <= comp[element] < 256:
                                    self.comp[ELEMENTS[element]] = comp[element]                        
                                else:
                                    raise AttributeError
                            else:
                                raise TypeError
                    else:
                        raise ValueError
            except TypeError:
                raise
        
    def __iter__(self):
         return iter(self.comp)
    def __contains__(self, value):
         return value in self.comp
    def __getitem__(self,key):
        return self.comp[key]
    def __setitem__(self,key,value):
        self.comp[key] = value
    def __len__(self):
         return len(self.comp)

    """
    __hash__ and __cmp__ are hacks to get around scients being mutable.
    I think the answer is to actually make stones immutable and
    have imbue return a different stone.
    """

    def __hash__(self):
        return id(self)
                
    def tup(self):
        tup = ()
        for key in sorted(self.comp):
            tup += (self.comp[key],)
        return tup
        
    def value(self):
        return sum(self.comp.values())
