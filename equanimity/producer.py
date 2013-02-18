import persistent
import transaction

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.units import Squad, Scient
from binary_tactics.weapons import Sword, Bow, Wand, Glove

from binary_tactics.helpers import *

class Producer(persistent.Persistent):
    def __init__(self):
        self.has_armory = False
        self.has_stable = False
        self.has_homes  = False
        self.has_farms  = False
    
class Factory(persistent.Persistent):
    def __init__(self):
        pass