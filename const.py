"""File containing global constants, tricky to use don't forget about .copy()"""
ELEMENTS = ("Earth", "Fire", "Ice", "Wind")
E = "Earth"
F = "Fire"
I = "Ice"
W = "Wind"
ORTH = {E: (F, I),  #Earth is orthogonal to Fire and Ice
        F: (E, W),  #Fire  is orthogonal to Earth and Wind
        I: (E, W),  #Ice   is orthogonal to Earth and Wind
        W: (F, I),} #Wind  is orthogonal to Fire and Ice

OPP = {E: W, W: E, #Earth and Wind are opposites
       F: I, I: F} #Fire and Ice are opposites

COMP = {E:0, F:0, I:0, W:0}

KINDS = ("Stone", "Scient", "Nescient")

JOBS = FT, TH, SH, WZ = ("Fighter", "Theurgist", "Shooter", "Wizard")

#max level is (112 years - 16 years) / 2 lvls per year = 48
MAXLEVEL = int((112-16)/2.0)
