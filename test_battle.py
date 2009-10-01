"""Simulate a battle (sanity checking the Unit implementation)"""

from defs import Item, Stone, Unit, Scient, Nescient, ELEMENTS, E, F, I, W

import random

def unit_repr(u):
        return "%s -> HP:% 5s | MP:% 5s | Element:% 5s | P Atk/Def: (% 3s,% 3s) | M Atk/Def: (% 3s,% 3s)" % (id(u), u.hp, u.mp, u.element, u.p_attack, u.p_defense, u.m_attack, u.m_defense)

def test_random_battle():
    comps = [(random.randint(0,100), random.randint(0,100)) for _ in range(5)]
    units = [Scient(random.choice(ELEMENTS),
                    {E:comps[i][0],F:comps[i][1],I:100-comps[i][1],W:100-comps[i][0]},
                   ) for i in range(5)] #create 5 units with somewhat random stats

    for u in units:
        print unit_repr(u)

    print "="*80
    print "u0 attacks u1"
    print unit_repr(units[1])
    units[0].phys_damage(units[1])
    print unit_repr(units[1])
    
    assert units[1].hp > 0
