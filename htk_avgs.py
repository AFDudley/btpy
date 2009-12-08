"""Helpers for figuring out HTK averages, does not take into account healing,
   because it hasn't be coded properly yet."""

from defs import *
from const import *
from helpers import *
    
def pdmg_squad(unit, squad):
    print "Physical damage from:"
    avg =[]
    unit_repr(unit)
    for x in squad:
        dmg = unit.phys_damage(x)
        if dmg == 0:
            avg.append(0)
            htk = 0
            print "No damage dealt"
        else:
            dmg = float(dmg)
            htk = x.hp / dmg
            avg.append(htk)
        print "target Suit/HP: %s/%s DMG: %s HTK: %s" \
            %(x.element, x.hp, dmg, htk)
    ans = sum(avg)/len(avg)
    print "Average HTK: %s \n" %(ans)
    return ans
    
def mdmg_squad(unit, squad):
    print "Magical damage from:"
    avg = []
    unit_repr(unit)
    for x in squad:
        dmg = unit.mag_damage(x, unit.element)
        if dmg == 0:
            avg.append(0)
            print "No damage dealt"
        else:
            dmg = float(dmg)
            htk = x.hp / dmg
            if dmg != 99999:
                avg.append(htk)
            print "target Suit/HP: %s/%s DMG: %s HTK: %s" \
                %(x.element, x.hp, dmg, htk)
    ans = sum(avg)/len(avg)
    print "Average of HTK (of hits that actually damage): %s \n" %(ans)
    return ans
    
def pdmg_avg(squad):
    grand = []
    for x in squad:
        grand.append(pdmg_squad(x, squad))
    ans = sum(grand)/len(grand)
    print "Average of the 16: %s \n" %(ans)
    return ans
    
def mdmg_avg(squad):
    grand = []
    for x in squad:
        grand.append(mdmg_squad(x, squad))
    ans = sum(grand)/len(grand)
    print "Average of the 16 (which excludes the 4 heals on the chart): %s" \
        %(ans)
    return ans
    
def better_suit(squad):
    ans = {E:0, F:0, I:0, F:0} 
    for x in squad:
        print "Damage average for %s" %x.element
        avg = (pdmg_squad(x, squad) + mdmg_squad(x, squad))/2
        ans[x.element] = avg
        #print "average for %s: %s \n" %(x.element, avg)
    print "Average of p and m HTKs for each suit/element: \n"
    for i in ans:
        print "%s: %s" %(i, ans[i])
    print "End of better_suit\n"
    return ans
    
def drift(tuple):
    for i in tuple:
        for j in ELEMENTS:
            print " %s: %s" %(j, i[j])
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
def betters(tuple):
    stats = ()
    """Say Word."""
    for i in tuple:
        stats += (better_suit(i),)
    return stats

fullones = betters(sounds)
notfull  = betters(sizes)
print "Shows the variance of HTK by suit as value of (2,1,1,0) units increases:"
drift(fullones)

print "\n Shows the variance of HTK by suit as value of (1,0,0,0) units increases:"
drift(notfull)   
    