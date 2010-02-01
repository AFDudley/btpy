"""Helpers for figuring out HTK averages, does not take into account healing,
"""

from defs import *
from const import *
from helpers import *
    
def pdmg_squad(unit, squad, debug=None):
    avg =[]
    if debug: print "Physical damage from:"; unit
    for x in squad:
        dmg = unit.pdmg(x)
        if dmg == 0:
            avg.append(0)
            htk = 0
            if debug: print "No damage dealt"
        else:
            dmg = float(dmg)
            htk = x.hp / dmg
            avg.append(htk)
            if debug: print "target Suit/HP: %s/%s DMG: %s HTK: %s" \
            %(x.element, x.hp, dmg, htk)
    
    ans = sum(avg)/len(avg)
    if debug: print "Average HTK: %s \n" %(ans)
    return ans
    
def mdmg_squad(unit, squad, debug=None):
    avg = []
    if debug: print "Magical damage from:"; unit
    for x in squad:
        dmg = abs(unit.mdmg(x, unit.element))
        if dmg == 0:
            avg.append(0)
            if debug: print "No damage dealt"
        else:
            dmg = float(dmg)
            htk = x.hp / dmg
            if dmg != 99999:
                avg.append(htk)
            if debug: print "target Suit/HP: %s/%s DMG: %s HTK: %s" \
                %(x.element, x.hp, dmg, htk)
    ans = sum(avg)/len(avg)
    if debug: print "Average of HTK (of hits that actually damage): %s \n" \
    %(ans)
    
    return ans
    
def pdmg_avg(squad, debug=None):
    grand = []
    for x in squad:
        grand.append(pdmg_squad(x, squad, debug))
    ans = sum(grand)/len(grand)
    if debug: print "Average of 16 pdmgs: %s \n" %(ans)
    return ans
    
def mdmg_avg(squad, debug=None):
    grand = []
    for x in squad:
        grand.append(mdmg_squad(x, squad, debug))
    ans = sum(grand)/len(grand)
    if debug: print "Average of 16 mdmgs: %s" %(ans)
    return ans
    
def better_suit(squad, debug=None):
    ans = {E:0, F:0, I:0, F:0} 
    for x in squad:
        pdmg = pdmg_squad(x, squad, debug)
        mdmg = mdmg_squad(x, squad, debug)
        avg  = (pdmg + mdmg)/2
        stuff = {'pdmg':pdmg, 'mdmg':mdmg, 'avg':avg }
        ans[x.element] = stuff
        if debug:
            print "Damage average for %s" %x.element
            print "average for %s: %s \n" %(x.element, avg)
    if debug:
        print "Average of p and m HTKs for each suit/element: \n"
        for ele in ELEMENTS:
            print "Attacker: %s" %ele
            print "\tpdmg HTK average: %s\n \tmdmg HTK average: %s\n \
\tdmg  HTK average: %s\n" %(ans[ele]['pdmg'], ans[ele]['mdmg'], ans[ele]['avg'])

    return ans

def drift(tuple):
    for i in tuple:
        print better_suit(i)
        print
            
#Shout out to Eureka Seven
lows  = max_squad_by_value(4)
mids  = max_squad_by_value(255)
highs = max_squad_by_value(510)    

small  = one_three_zeros(4)
medium = one_three_zeros(127) 
large  = one_three_zeros(255)

sounds = (lows, mids, highs)
sizes  = (small, medium, large)

def make_mess():

    print "Shows the variance of HTK by suit as value of (2,1,1,0) units increases:"
    drift(sounds)

    print "\n Shows the variance of HTK by suit as value of (1,0,0,0) units increases:"
    drift(sizes)

def make_grand(squad, debug=None):
    """grand average for squad"""
    grand = 0
    avgs = better_suit(squad, debug)
    for i in ELEMENTS:
        grand += avgs[i]['avg']
    return grand / len(squad)
    
    
    
    
    
    
