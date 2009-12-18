"""Helper functions"""
import random
#import const   
from const import ELEMENTS, E, F, W, I, ORTH, KINDS, OPP
from defs import Scient, Squad

def unit_repr(u): #Needs work.
    """'Pretty' Scient Printer"""
    if u.name:
        title = u.name
    else:
        title = str(id(u))
    return "%s -> suit:% 2s | val: %s | loc: %s | comp: (%s, %s, %s, %s) | \
p: %s \nHP: % 7s | PA/PD: (% 5s,% 5s) | MA/MD: (% 5s,% 5s) \n" % (title, \
    u.element[0], u.value(), u.location, u.comp[E], u.comp[F], u.comp[I], \
    u.comp[W], u.p, u.hp, u.patk, u.pdef, u.matk, u.mdef)

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
    
    squad = Squad()
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

def show_squad(squad):
    for unit in squad:
        print unit_repr(unit)

def max_squad_by_value(value):
    """Takes an integer, ideally even because we round down, and returns a
    squad such that comp[element] == value, comp[orth] == value/2, comp[opp]
    == 0"""
    squad = []
    value = value/2 #more logical, really.
    half = value/2
    for i in ELEMENTS:
        unit = Scient(i,{E:half, F:half, I:half, W:half,})
        unit.comp[unit.element] = value
        unit.comp[OPP[unit.element]] = 0
        unit.calcstats()
        squad.append(unit)
    return squad

def one_three_zeros(value):
    squad = []
    for i in ELEMENTS:
        unit = Scient(i,{E:0, F:0, I:0, W:0})
        unit.comp[unit.element] = value
        unit.calcstats()
        squad.append(unit)
    return squad


    