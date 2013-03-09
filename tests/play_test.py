from binary_tactics.defs import Loc
from binary_tactics.units import Scient, Squad, Stone
from stores import yaml_store
from binary_tactics.weapons import *
from stores.store import get_persisted
from stores.yaml_store import *
from copy import deepcopy

sq1 = Squad()
s = Scient('Fire', Stone((2,4,0,2)))
s.equip(Sword('Fire', Stone()))
for n in xrange(3):
    sq1.append(deepcopy(s))

s = Scient('Wind', Stone((0,2,2,4)))
s.equip(Wand('Wind', Stone()))
for n in xrange(2):
    sq1.append(deepcopy(s))

i = Scient('Ice', Stone((2,0,4,2)))
i.equip(Glove('Ice', Stone()))
for n in xrange(3):
    sq1.append(deepcopy(i))

sq0 = deepcopy(sq1)
sq0.name = "pt_0"
sq1.name = "pt_1" 
for n in xrange(len(sq0)):
    sq0[n].location = Loc(n+4, 4)
    sq1[n].location = Loc(n+4, 11)
yaml.dump(get_persisted(sq0), file('pt_0.yaml', 'w'))
yaml.dump(get_persisted(sq1), file('pt_1.yaml', 'w'))