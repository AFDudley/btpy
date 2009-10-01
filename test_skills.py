from test_battlefield import *
from defs import *
from battlefield import *

def test_status_effects():
    bf = Battlefield()
    attacker = rand_unit("Alice")
    dummies_lvl1 = map(rand_unit, map(str, range(1000)))
    dummies_lvl2 = map(rand_unit, map(str, range(1000,2000)))

    for dummy in dummies_lvl1:
        bf.place_unit(dummy, (1,0))
        attacker.strikes((1,0), 1, F, bf) #should have (1/16.) chance for status effect
        bf.remove_unit(dummy)

    lvl1_statuses = len(bf.status_effects)

    for dummy in dummies_lvl2:
        bf.place_unit(dummy, (1,0))
        attacker.strikes((1,0), 2, F, bf) #should have (1/8.) chance
        bf.remove_unit(dummy)

    lvl2_statuses = len(bf.status_effects) - lvl1_statuses

    print lvl1_statuses/1000., lvl2_statuses/1000.

    assert 40 < lvl1_statuses < 80 #1000 * (1/16.) is 62.5 units with status effects
    assert 100 < lvl2_statuses < 150 #1000 * (1/8.) is 125 units with status effects
    assert lvl1_statuses < lvl2_statuses
