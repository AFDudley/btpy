from UserList import UserList
import persistent
import transaction

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.units import Squad, Scient
from binary_tactics.weapons import Sword, Bow, Wand, Glove

from binary_tactics.helpers import *

class Factory(persistent.Persistent, UserList):
    """contains a number of Units. Takes a list of Units"""
    def unit_size(self, object):
        if isinstance(object, Unit) == False:
            raise TypeError("Factories can contain only Units")
        else:
            if isinstance(object, Scient):
                return 1
            else:
                return 2

    def __init__(self, kind=None):
        self.val = 0
        self.free_spaces = 8
        UserList.__init__(self)
        if kind == 'Stable' or kind == 'Earth':
            self.kind = 'Stable'
        elif kind == 'Armory' or kind == 'Fire':
            self.kind = 'Armory'
        elif kind == 'Home' or kind == 'Ice':
            self.kind = 'Home'
        elif kind == 'Farm' or kind =='Wind':
            self.kind = 'Farm'
        else:
            raise Exception("kind must be 'Stable'|'Earth', 'Armory'|'Fire', 'Home'|'Ice', 'Farm'|'Wind." )
    
    def __setitem__(self, key, val):
        size = self.unit_size(key)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the factory for this unit")
        list.__setitem__(self, key, val)
        self.val += val.value()
        self.free_spaces -= size
        key.factory = self

    def __delitem__(self, key):
        del self.data[key].factory
        temp = self[key].value()
        self.free_spaces += self.unit_size(self[key])
        self.data.__delitem__(key)
        self.val -= temp

    def append(self, item):
        size = self.unit_size(item)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the factory for this unit")
        self.data.append(item)
        self.val += item.value()
        self.free_spaces -= size
        item.factory = self

    def value(self):
        return self.val
    
    def upgrade(self):
        self.free_spaces += 1
