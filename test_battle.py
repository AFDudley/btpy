"""Simulate a battle (sanity checking the Unit implementation)"""

from defs import Stone, Unit, Scient, Nescient
from const import ELEMENTS, E, F, I, W
from helpers import unit_repr, rand_comp, rand_squad, rand_unit

import random

def test_random_battle():
    units = rand_squad()
    for u in units:
        print "%s \n" %unit_repr(u) 

    print "="*80
    print "u0 attacks u1"
    print "%s \n" %unit_repr(units[1])
    units[0].phys_damage(units[1])
    unit_repr(units[1])
    assert units[1].hp > 0

print "Making min units..."
PATK = Scient(F, {E:0, F:1, I:0, W:0})
PATK.name = 'PATK'
unit_repr(PATK)
print
 
PDEF = Scient(E, {E:1, F:0, I:0, W:0})
PDEF.name = 'PDEF'
unit_repr(PDEF)
print

MATK = Scient(I, {E:0, F:0, I:1, W:0})
MATK.name = 'MATK'
unit_repr(MATK)
print
 
MDEF = Scient(W, {E:0, F:0, I:0, W:1}) 
MDEF.name = 'MDEF'
unit_repr(MDEF)

