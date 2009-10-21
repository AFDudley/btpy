from defs import Scient
from const import COMP, ELEMENTS, E, F, I, W
from constraint import *
#tff = range(0,255)
#tfs = range(1,256)
ten = range(10)
twok =range(2001)
ugh = Problem()
ugh.addVariables(["E","F","I","W"], [0,1])
ugh.addVariable("a", [2])

#there has got to be an easier way of doing this
ugh.addConstraint(lambda E, F, I, W, a: a==2 and (E > 0) and (W < 1), ["E","F","I","W","a"])
ugh.addConstraint(lambda E, F, I, W, a: a == E + F + W + I, ["E","F","I","W","a"])
'''
ugh.addVariable("str", ten)
ugh.addVariable("int", ten)
ugh.addVariable("MDEF", ten)
ugh.addVariable("PDEF", ten)
ugh.addVariable("PATK", ten)
ugh.addVariable("MATK", ten)
#ugh.addVariable("c1", ten)
ugh.addVariable("HP", twok)

ugh.addConstraint(lambda E, F, I, W, str: str == 2 * (E + F) \
                    + I + W, ["E","F","I","W","str"])
ugh.addConstraint(lambda E, F, I, W, int: int == 2 * \
                    (I + W) + E + F, ["E","F","I","W","int"])

ugh.addConstraint(lambda E, F, I, W, str, PDEF: PDEF == E + str, ["E", "F", "I", "W", "int", "PDEF"])
ugh.addConstraint(lambda E, F, I, W, str, PATK: PATK == F + str, ["E", "F", "I", "W", "int", "PATK"])
ugh.addConstraint(lambda E, F, I, W, int, MATK: MATK == I + int, ["E", "F", "I", "W", "int", "MATK"])
ugh.addConstraint(lambda E, F, I, W, int, MDEF: MDEF == W + int, ["E", "F", "I", "W", "int", "MDEF"])
ugh.addConstraint(lambda E, F, I, W, str, int, PDEF, MDEF, HP: HP == (str * PDEF) \
                    + (int * MDEF), ["E","F","I","W","str", \
                    "int", "PDEF", "MDEF", "HP"])
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
'''
