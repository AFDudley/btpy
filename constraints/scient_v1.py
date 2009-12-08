"This constraint program generates all valid Scients with a comp value of 1"
from defs import Scient
from const import COMP, ELEMENTS, E, F, I, W
from constraint import *
#tff = range(0,255)
#tfs = range(1,256)

ten = range(10)
twok =range(2001)
class scient2(Scient):
    def __init__(self, suit, e, f, i, w, m, p, pdef, patk, matk, mdef, hp):
        Scient.__init__(self, suit, {E:e, F:f, I:i, W:w})
        self.m  = m
        self.p  = p
        self.pdef = pdef
        self.patk = patk
        self.matk = matk
        self.mdef = mdef
        self.hp   = hp
    

def convert_to_squad(solutions):
    """Returns a squad made from CP values"""
    group = []
    group.extend(solutions)
    squad = []
    for x in group:
        remap = {1:E, 2:F, 3:I, 4:W}
        unit = scient2(remap[x['suit']], x['E'], x['F'], x['I'], x['W'], x['m'], \
            x['p'], x['pdef'], x['patk'], x['matk'], x['mdef'], x['HP'],)
        squad.append(unit)
    del group
    return squad

def make_v1():
    """creates the 4 possible units with a value of 1"""
    x = Problem()
    x.addVariables(["E","F","I","W"], [0,1])
    x.addVariable("suit", [1,2,3,4])
    x.addVariable("value", [1])
    x.addConstraint(lambda suit, E, F, I, W: (suit == 1 and E > 0 and W < 1)  \
                                        or (suit == 2 and F > 0 and I < 1)  \
                                        or (suit == 3 and I > 0 and F < 1)  \
                                        or (suit == 4 and W > 0 and E < 1), \
                                        ["suit", "E", "F", "I", "W"])
                                        
    x.addConstraint(lambda E, F, I, W, value: value == E + F + W + I, \
                  ["E","F","I","W","value"])
                  
    x.addVariable("p", ten)
    x.addConstraint(lambda E, F, I, W, p: p == (2 * (E + F)) + I + W, \
                  ["E","F","I","W","p"])
                  
    x.addVariable("m", ten)
    x.addConstraint(lambda E, F, I, W, m: m == (2 * (I + W)) + E + F, \
                  ["E","F","I","W","m"])
    
    x.addVariable("atk", ten)
    x.addConstraint(lambda E, F, I, W, value, atk: atk == ((2 * (F + I) + E + W)  \
                    + (2 * value)), ["E","F","I","W","value","atk"])

    x.addVariable("defe", ten)
    x.addConstraint(lambda E, F, I, W, value, defe: defe == ((2 * (E + W) + F + I)  \
                    ), ["E","F","I","W","value","defe"])

    x.addVariable("pdef", ten)
    x.addConstraint(lambda E, F, I, W, p, defe, pdef: pdef == p + defe, \
                  ["E", "F", "I", "W", "p", "defe", "pdef"])
                  
    x.addVariable("patk", ten)
    x.addConstraint(lambda E, F, I, W, p, atk, patk: patk == p + atk, \
                  ["E", "F", "I", "W", "p", "atk", "patk"])
                  
    x.addVariable("matk", ten)
    x.addConstraint(lambda E, F, I, W, m, atk, matk: matk == m + atk, 
                  ["E", "F", "I", "W", "m", "atk", "matk"])
                  
    x.addVariable("mdef", ten)
    x.addConstraint(lambda E, F, I, W, m, defe, mdef: mdef == m + defe, \
                  ["E", "F", "I", "W", "m", "defe", "mdef"])
                  
    x.addVariable("HP", twok)
    x.addConstraint(lambda E, F, I, W, p, m, pdef, mdef, HP: HP ==  \
                  (p + pdef) + (m + mdef), ["E","F","I","W","p", \
                  "m", "pdef", "mdef", "HP"])
                  
    return x.getSolutions()

#dmg == (the function for it)
def tough():
    down =range(500,1,-1)
    up = range(510)
    y = Problem()
    y.addVariable("suit", [1,2,3,4])
    y.addVariable("value", [up])
    y.addConstraint(lambda suit, E, F, I, W: (suit == 1 and E > 0 and W < 1 and E > (F + I))  \
                                            or (suit == 2 and F > 0 and I < 1 and F > (E + W))  \
                                            or (suit == 3 and I > 0 and F < 1 and I > (E + W))  \
                                            or (suit == 4 and W > 0 and E < 1 and W > (F + I)), \
                                            ["suit", "E", "F", "I", "W"])
                                        
    y.addConstraint(lambda E, F, I, W, value: value == E + F + W + I, \
                  ["E","F","I","W","value"])
    y.addVariable("HP", down)
    y.addVariables(["E", "F", "I","W"], up)
    y.addConstraint(lambda E, F, I, W, HP: ((2 * (E + F) + I + W) * (E +(2 * (E + F) + I + W))) + ((2 * (W + I) + F + E) * (W +(2 * (W + I) + F + E))) == HP, ["E","F","I","W","HP"])
    return y.getSolutions()
