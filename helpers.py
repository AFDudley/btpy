"""Helper functions"""
import random
#import const   
from const import ELEMENTS, E, F, W, I, ORTH, KINDS
from defs import Scient

def unit_repr(u): #Needs work.
    """'Pretty' Scient Printer"""
    if u.name:
        title = u.name
    else:
        title = str(id(u))
    print "%s -> suit:% 2s | comp: (%s, %s, %s, %s) | p: %s \n HP: % 7s \
| PA/PD: (% 5s,% 5s) | MA/MD: (% 5s,% 5s)" % (title, u.element[0], \
u.comp[E], u.comp[F], u.comp[I], u.comp[W], u.p, \
u.hp, u.patk, u.pdef, u.matk, u.mdef)

def rand_element():
    """Reuturns a random element"""
    return random.choice(ELEMENTS)

def rand_comp(suit=None, kind=None):
    """Returns a random comp in 'suit' for use instaniating 'kind'
       If 'suit' is not valid, random element used.
       If 'kind' is not valid stone is used
       if 'kind' is 'Stone' suit ignored"""
    if not suit in ELEMENTS:
        suit = rand_element()
    
    comp = {E:0, F:0, I:0, W:0}
    if kind is None or kind not in KINDS:
        kind = 'Stone'
    
    if kind == 'Stone':
        for element in comp:
            comp[element] = random.randint(0, 255)
        return comp
    else:
        if kind == 'Scient':
            comp[suit] = random.randint(1, 255)
            for picked in ORTH[suit]:
                #NOTE: if comp[suit] = 1 orths will be 0.
                comp[picked] = random.randint(0, (comp[suit] / 2))
            return comp
        
        else: #Nescient is currently the only other kind
            comp[suit] = random.randint(1, 255)
            comp[random.choice(ORTH[suit])] = \
                random.randint(1, 255)
            return comp

def rand_unit(suit=None): #may change to rand_unit(suit, kind)
    """Returns a random Scient of suit. Random suit used if none given."""
    if not suit in ELEMENTS:
        suit = rand_element()
    return Scient(suit, rand_comp(suit, 'Scient'))

def rand_squad(suit=None):
    """Returns a Squad of five random Scients of suit. Random suit used
       if none given."""
    
    squad = []
    size = 5
    if not suit in ELEMENTS:
        for _ in range(size):
            squad.append(rand_unit(rand_element()))
        return squad
    
    else:
        for _ in range(size):
            squad.append(rand_unit(suit))
        return squad

def print_rand_squad(suit=None):
    squad = rand_squad(suit)
    for unit in squad:
        print unit_repr(unit)
    return squad
