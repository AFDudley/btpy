"""Helper functions"""
import random
#import const   
from const import ELEMENTS, E, F, W, I, ORTH, KINDS, OPP, COMP
from defs import Scient, Squad, Stone

def t2c(tup):
    """Converts a tuple to a comp"""
    if len(tup) != 4: raise Exception("Incorrect number of values in tuple")
    comp = Comp()
    for i in range(4):
        comp[ELEMENTS[i]] = tup[i]
    return comp
    
def rand_element():
    """Reuturns a random element"""
    return random.choice(ELEMENTS)
    
def max_comp(suit, kind='Scient'):
    """Returns the maximum composition of 'kind' of element 'suit'"""
    comp = Stone()
    if kind == 'Scient':
        comp[suit] = 255
        comp[OPP[suit]] = 0
        comp[ORTH[suit][0]] = comp[ORTH[suit][1]] = 127
        return comp
    if kind == 'Weapon':
        comp2 = Comp()
        comp2[suit]          = comp[suit] = 63
        comp2[OPP[suit]]     = comp[OPP[suit]] = 0
        comp2[ORTH[suit][0]] = comp[ORTH[suit][1]] = 0
        comp2[ORTH[suit][1]] = comp[ORTH[suit][0]] = 63
        return (comp, comp2)
    if kind == 'Nescient':
        comp2 = Comp()
        comp2[suit]          = comp[suit] = 255
        comp2[OPP[suit]]     = comp[OPP[suit]] = 0
        comp2[ORTH[suit][0]] = comp[ORTH[suit][1]] = 0
        comp2[ORTH[suit][1]] = comp[ORTH[suit][0]] = 254
        return (comp, comp2)    
    if kind == 'Stone':
        for i in comp: comp[i] = 255
        return comp
        
    
def rand_comp(suit=None, kind=None):
    """Returns a random comp in 'suit' for use instaniating 'kind'
       If 'suit' is not valid, random element used.
       If 'kind' is not valid stone is used
       if 'kind' is 'Stone' suit ignored"""
    if not suit in ELEMENTS:
        suit = rand_element()
    
    comp = Stone()
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
        print unit
    return squad

def show_squad(squad):
    print squad(more=1)

def max_squad_by_value(value):
    """Takes an integer, ideally even because we round down, and returns a
    squad such that comp[element] == value, comp[orth] == value/2, comp[opp]
    == 0"""
    squad = Squad()
    value = value/2 #more logical, really.
    half = value/2
    for i in ELEMENTS:
        unit = Scient(i,Comp({E:half, F:half, I:half, W:half,}))
        unit.comp[unit.element] = value
        unit.comp[OPP[unit.element]] = 0
        unit.calcstats()
        squad.append(unit)
    return squad

def one_three_zeros(value):
    squad = Squad()
    for i in ELEMENTS:
        unit = Scient(i,{E:0, F:0, I:0, W:0})
        unit.comp[unit.element] = value
        unit.calcstats()
        squad.append(unit)
    return squad