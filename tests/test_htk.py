from binary_tactics.const import *
from binary_tactics.stone import Stone
from binary_tactics.weapons import *
from binary_tactics.units import Unit, Scient
from binary_tactics.unit_container import Squad
from binary_tactics.hex_battlefield import Grid, Battlefield
from fractions import Fraction
from operator import itemgetter
from collections import OrderedDict
import sys

def test_dmg(atkr, dfndr):
    btl = Battlefield(Grid(x=1,y=2), Squad(dfndr), Squad(atkr))
    btl.place_object(dfndr, (0, 0))
    btl.place_object(atkr, (0, 1))
    dmg = btl.dmg(atkr, dfndr)
    dfndr.location = None
    atkr.location = None
    return dmg 

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

def get_htks():
    lists = make_lists()
    for l in lists:
        print "%s attacks:" %l
        for dfndr in lists[l][0]:
            #print "dfndr name: %s" %dfndr.name
            for atkr in lists[l][1]:
                dmg = test_dmg(atkr, dfndr)
                hp = dfndr.hp
                #htk = max(0, Fraction(float(hp)/dmg).limit_denominator(100))
                if dmg == 0:
                    htk = float("inf")
                else:
                    htk = float(hp)/dmg
                print "\t%s -> %s HTK: %s " %(atkr.name, dfndr.name, htk)
            print " "

class Dude(object):
    def __init__(self):
        self.element = None
        self.comp = None
        self.weapon = None
        self.name = None
        
    def set_element(self, stuff):
        if stuff[0].lower() == 'e':
            self.element = E
        elif stuff[0].lower() == 'f':
            self.element = F
        elif stuff[0].lower() == 'i':
            self.element = I
        elif stuff[0].lower() == 'w':
            self.element = W
        else:
            print "Element must start with E, F, I, or W."
            return None
    
    def set_comp(self, comp):
        try:
            stone = Stone(eval(comp))
        except:
            print "Specify comp in form of (w,x,y,z)"
        if stone:
            s = sorted(stone.comp.iteritems(), key=itemgetter(1), reverse=True)
            if s[0][1] > 0:
                if s[0][0] == self.element:
                    self.comp = stone.comp
                else:
                    print "Primary element in composition must match primary element in unit."
            else:
                print "Primary element must be greater than zero."
        
    def set_weapon(self, stuff):
        if stuff[0].lower() == 's':
            self.weapon = Sword(self.element, Stone())
        elif stuff[0].lower() == 'b':
            self.weapon = Bow(self.element, Stone())
        elif stuff[0].lower() == 'w':
            self.weapon = Wand(self.element, Stone())
        elif stuff[0].lower() == 'g':
            self.weapon = Glove(self.element, Stone())
        else:
            print "Weapon must start with s, b, w, or g."

    def make_unit(self):
        while self.name == None:
            self.name = raw_input("Name unit: ")
        while self.element == None:
            self.set_element(raw_input("Specify primary element for %s: " %self.name))
        while self.comp == None:
            self.set_comp(raw_input("Specify a composition for %s: " %self.name))
        while self.weapon == None:
            self.set_weapon(raw_input("Specify a weapon for %s: " %self.name))
        return Scient(self.element, self.comp, self.name, self.weapon)

def print_dudes(dudes, d=False):
    for n in xrange(len(dudes)):
        print "%s: %s" %(n, dudes[n].name)
        if d:
            for k,v in dudes[n].stats().items():
                print "\t%s: %s" %(k,v)

def command(dudes, cmd):
    if cmd[0].lower() == 't':
        atkr_num = int(raw_input("Select Attacker: "))
        print_dudes(dudes)
        if atkr_num in range(len(dudes)):
            dfndr_num = int(raw_input("Select Defender: "))
            print_dudes(dudes)
            if dfndr_num in range(len(dudes)):
                print test_dmg(dudes[atkr_num], dudes[dfndr_num])
    elif cmd[0].lower() == 'l':
        print_dudes(dudes, True)
    elif cmd[0].lower() == 'a':
        dudes.append(Dude().make_unit())
    elif cmd[0].lower() == 'q':
        sys.exit()
def main():
    dudes = []
    while len(dudes) < 2: 
        dudes.append(Dude().make_unit())
    while True:
        cmd = raw_input("What would you like to do next?\n \t(t)est dmg.\n \t(l)ist units.\n \t(a)dd unit.\n \t(q)uit.\n > ")
        if cmd[0].lower() == 't':
            print "Select Attacker by number:"
            print_dudes(dudes)
            atkr_num = int(raw_input("> "))
            if atkr_num in range(len(dudes)):
                print "Select Defender by number:"
                print_dudes(dudes)
                dfndr_num = int(raw_input("> "))
                if dfndr_num in range(len(dudes)):
                    print test_dmg(dudes[atkr_num], dudes[dfndr_num])
        elif cmd[0].lower() == 'l':
            print_dudes(dudes, True)
        elif cmd[0].lower() == 'a':
            dudes.append(Dude().make_unit())
        elif cmd[0].lower() == 'q':
            sys.exit()
if __name__ == '__main__':
    main()
