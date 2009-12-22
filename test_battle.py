"""Simulate a battle (sanity checking the Unit implementation)"""

from defs import Stone, Unit, Scient, Nescient
from const import ELEMENTS, E, F, I, W
from helpers import rand_comp, rand_squad, rand_unit

import random

def test_random_battle():
    units = rand_squad()
    for u in units:
        print "%s \n" %u 

    print "="*80
    print "u0 attacks u1"
    print "%s \n" %units[1]
    units[0].pdmg(units[1])
    units[1]
    assert units[1].hp > 0

print "Making min units..."
PATK = Scient(F, {E:0, F:1, I:0, W:0})
PATK.name = 'PATK'
PATK
print
 
PDEF = Scient(E, {E:1, F:0, I:0, W:0})
PDEF.name = 'PDEF'
PDEF
print

MATK = Scient(I, {E:0, F:0, I:1, W:0})
MATK.name = 'MATK'
MATK
print
 
MDEF = Scient(W, {E:0, F:0, I:0, W:1}) 
MDEF.name = 'MDEF'
MDEF

