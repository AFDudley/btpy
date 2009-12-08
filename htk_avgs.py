from defs import *
from const import *
from helpers import *
maxes = []

for x in ELEMENTS:
    u = Scient(x,{E:127, F:127, I:127, W:127,})
    u.comp[u.element] = 255
    u.comp[OPP[u.element]] = 0
    u.calcstats()
    maxes.append(u)

#SO LAZY
fours = []    
for x in ELEMENTS:
    u = Scient(x,{E:1, F:1, I:1, W:1,})
    u.comp[u.element] = 2
    u.comp[OPP[u.element]] = 0
    u.calcstats()
    fours.append(u)
    
def show_squad(squad):
    for u in squad:
        print u.element
        unit_repr(u)
        print

def pdmg_squad(unit, squad):
    print "Physical damage from:"
    avg =[]
    unit_repr(unit)
    for x in squad:
        dmg = unit.phys_damage(x)
        htk = x.hp / (dmg + .0)
        avg.append(htk)
        print "target Suit/HP: %s/%s DMG: %s HTK: %s" %(x.element, x.hp, dmg, htk)
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
            print "target Suit/HP: %s/%s DMG: %s HTK: %s" %(x.element, x.hp, dmg, htk)
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
    print "Average of the 16 (which excludes the 4 heals on the chart): %s" %(ans)
    return ans
    
def better_suit(squad):
    ans = {E:0, F:0, I:0, F:0} 
    for x in squad:
        print "Damage average for %s" %x.element
        avg = (pdmg_squad(x, squad) + mdmg_squad(x, squad))/2
        ans[x.element] = avg
        #print "average for %s: %s \n" %(x.element, avg)
    for i in ans:
        print "average for %s: %s \n" %(i, ans[i])
    return ans
    
    
    
    