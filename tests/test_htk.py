from binary_tactics.const import *
from binary_tactics.stone import Stone
from binary_tactics.weapons import *
from binary_tactics.units import Unit, Scient
from binary_tactics.unit_container import Squad
from binary_tactics.hex_battlefield import Grid, Battlefield
from fractions import Fraction
def make_lists():
    lists = {'physical': ([], []), 'magical': ([], [])}
    for kind in lists.keys():
        for suit in ELEMENTS:
            s = Stone()
            s.comp[suit] = 1
            #s.comp[suit] = 4
            #s.comp[OPP[suit]] = 0
            #for o in ORTH[suit]: s.comp[o] = 2
            if suit == 'Earth':
                name = 'PDEF'
            elif suit == 'Fire':
                name = 'PATK'
            elif suit == 'Ice':
                name = 'MATK'
            else:
                name = 'MDEF'
            lists[kind][0].append(Scient(suit, s, name))
            lists[kind][1].append(Scient(suit, s, name, Weapon(F, Stone(), None, kind[0])))
    return lists
lists = make_lists()
for l in lists:
    print "%s attacks:" %l
    for dfndr in lists[l][0]:
        #print "dfndr name: %s" %dfndr.name
        for atkr in lists[l][1]:
            btl = Battlefield(Grid(x=1,y=2), Squad(dfndr), Squad(atkr))
            btl.place_object(dfndr, (0, 0))
            btl.place_object(atkr, (0, 1))
            dmg = btl.dmg(atkr, dfndr)
            hp = dfndr.hp
            #htk = max(0, Fraction(float(hp)/dmg).limit_denominator(100))
            if dmg == 0:
                htk = 0
            else:
                htk = max(0, float(hp)/dmg)
            dfndr.location = None
            atkr.location = None
            print "\t%s -> %s HTK: %s " %(atkr.name, dfndr.name, htk)
