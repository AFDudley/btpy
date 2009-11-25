"This constraint program generates all valid Scients with a comp value of 1"
from defs import Scient
from const import COMP, ELEMENTS, E, F, I, W
from constraint import *
#tff = range(0,255)
#tfs = range(1,256)
ten = range(12000, 600, -1)
twok =range(1500000, 13800000, -1)
ugh = Problem()
ugh.addVariables(["E","F","I","W"], [0,127,255])
ugh.addVariable("suit", [1,2,3,4])
ugh.addVariable("value", [509])
ugh.addConstraint(lambda suit, E, F, I, W: (suit == 1 and E > 0 and W < 1 and E > (F + I))  \
                                        or (suit == 2 and F > 0 and I < 1 and F > (E + W))  \
                                        or (suit == 3 and I > 0 and F < 1 and I > (E + W))  \
                                        or (suit == 4 and W > 0 and E < 1 and W > (F + I)), \
                                        ["suit", "E", "F", "I", "W"])

ugh.addConstraint(lambda E, F, I, W, value: value == E + F + W + I, \
                  ["E","F","I","W","value"])

ugh.addVariable("str", ten)
ugh.addConstraint(lambda E, F, I, W, str: str == (2 * (E + F)) + I + W, \
                  ["E","F","I","W","str"])

ugh.addVariable("int", ten)
ugh.addConstraint(lambda E, F, I, W, int: int == (2 * (I + W)) + E + F, \
                  ["E","F","I","W","int"])

ugh.addVariable("PDEF", ten)
ugh.addConstraint(lambda E, F, I, W, str, PDEF: PDEF == E + str, \
                  ["E", "F", "I", "W", "str", "PDEF"])

ugh.addVariable("PATK", ten)
ugh.addConstraint(lambda E, F, I, W, str, PATK: PATK == F + str, \
                  ["E", "F", "I", "W", "str", "PATK"])

ugh.addVariable("MATK", ten)
ugh.addConstraint(lambda E, F, I, W, int, MATK: MATK == I + int, 
                  ["E", "F", "I", "W", "int", "MATK"])

ugh.addVariable("MDEF", ten)
ugh.addConstraint(lambda E, F, I, W, int, MDEF: MDEF == W + int, \
                  ["E", "F", "I", "W", "int", "MDEF"])

ugh.addVariable("HP", twok)
ugh.addConstraint(lambda E, F, I, W, str, int, PDEF, MDEF, HP: HP ==  \
                  (str * PDEF) + (int * MDEF), ["E","F","I","W","str", \
                  "int", "PDEF", "MDEF", "HP"])

#ugh.addVariable("c1", ten)
class scient2(Scient):
    def __init__(self, e, f, i, w, int, str, pdef, patk, matk, mdef, hp):
        Scient.__init__(self, 'Fire', {E:e, F:f, I:i, W:w})
        self.int  = int
        self.str  = str
        self.pdef = pdef
        self.patk = patk
        self.matk = matk
        self.mdef = mdef
        self.hp   = hp

#so realllllllllllll
def NMC():
    """Need More Clever"""
    yeah = ugh.getSolutions()
    mess = []
    #there is a more clever way of doing this using .key() but whateva
    for x in yeah:
        naked = scient2(x['E'], x['F'], x['I'], x['W'], x['int'], \
            x['str'], x['PDEF'], x['PATK'], x['MATK'], x['MDEF'], x['HP'], )
        naked.element = 'nope'
        mess.append(naked)
    return mess

