"""Definitions for game units and unit interaction"""

import random
from math import log

from const import * #needs fix, maybe whole file needs rewrite
                    #why aren't there constants in python?

################################################################################

class Skill(object):
    """Contains the logic for how a skill works and applies it"""
    def __init__(self, element, name, logic):
        self.element = element
        self.name = name
        self.logic = logic
    
    def use(self, unit, tile, battlefield):
        target = battlefield.get_tile(tile)
        self.logic(unit, target, battlefield)
    
## fighter skills ##############################################################

test_skill = Skill(F, "Test skill (phys damage)", lambda (u,t,b): None)

def maim_leg_logic(u,t,b):
    t.move = t.move-1

def maim_arm_logic(unit, target, battlefield):
    target.patk = target.patk*(31/32.)
    battlefield.status_effects.append((target, "Disable skill...")) #TODO: chance of disabling all skills for a turn.

def break_armor_logic(u,target,b):
    target.pdef = target.pdef*(63/64.) #TODO: need a real value
    target.mdef = target.mdef*(63/64.) #TODO: need a real value

def break_weapon_logic(u,target,b):
    target.patk = target.patk*(63/64.) #TODO: need a real value
    target.matk = target.matk*(63/64.) #TOOD: need a real value

maim_leg = Skill(E, "Maim leg", maim_leg_logic)
maim_arm = Skill(F, "Maim arm", maim_arm_logic)
break_armor = Skill(I, "Break armor", break_armor_logic)
break_weapon = Skill(W, "Break weapon", break_weapon_logic)

## theurgist skills ############################################################

def make_dot_logic(element):
    def inner(unit, target, battlefield):
        dmg = unit.mdmg(target, element)
        battlefield.status_effects.append((target, "DOT...")) 
        #dot: [1/(2^(turn-1)][mdmg]
        #1: calculate the number of DOT turns (int((log(dmg) / log(2.0)))
        #2: record the initial damage and number of terms (or just store the whole list of dmg values)
        #3: store this in status_effects
        #4: battlefield uses this data every turn to calc DOTs
    return inner
etouch, ftouch, itouch, wtouch = map(Skill, ELEMENTS, ["Blast"]*4, map(make_dot_logic, ELEMENTS))

## shooter skills ##############################################################

## wizard skills ###############################################################
#def make_blast_logic(element):
#    def inner(unit, target, battlefield):
#        unit.mdmg(target, element)
#        orign = battlefield.get_unit(target)

## set up skill arrays #########################################################

SKILL_ORDER = ['SS_2', 'SR_1', 'OR_1', 'SS_3', 'OS_2', 'SL_1', 'OL_1', 'SS_4', 'SR_2', 'SL_2', 'SS_5', 'OS_3', 'SR_3', 'OR_2', 'SS_6', 'SL_3', 'OL_2', 'SS_7', 'OS_4', 'SR_4', 'SL_4', 'SS_8']

SKILLS = {FT: {E: maim_leg,   F: maim_arm,   I: "Break armor",    W: "Break weapon", "test": test_skill},
          TH: {E: etouch,     F: ftouch,     I: itouch,           W: wtouch,         "test": test_skill},
          SH: {E: "Pierce",   F: "Spray",    I: "Charged attack", W: "Fortitude",    "test": test_skill},
          WZ: {E: "Blast",    F: "Blast",    I: "Blast",          W: "Blast",        "test": test_skill}}

################################################################################

class Stone:
    def __init__(self, comp):
        self.comp = comp
    
    def value(self):
        """Returns sum of comp, overload as needed"""
        sum = 0
        for value in self.comp:
            sum + value
        return sum
    
    def imbue(self):
        pass

class Unit(object):
    def __init__(self, element, comp):
        if not element in ELEMENTS:
            raise Exception("Invalid element: %s, valid elements are %s" % (element, ELEMENTS))
        self.element = element
        self.comp = comp

        self.patk = None
        self.pdef = None
        self.matk = None
        self.mdef = None
        self.age = None
        self.name = None
    
    def value(self):
        """Returns sum of comp, overload as needed"""
        sum = 0
        for x in self.comp.keys():
            sum = sum + self.comp[x]
        return sum
        
    
    #def repr(self):
    #    return "%s -> HP:% 5s | MP:% 5s | Element:% 5s | P Atk/Def: (% 3s,% 3s) | M Atk/Def: (% 3s,% 3s)" % (id(u), u.hp, u.mp, u.element, u.patk, u.pdef, u.matk, u.mdef)
#TODO: inheriting from Unit is not buying anything for us here (in terms of Scient,
# which just overwrites Unit's __init__ (unless you use super?))

#needs work.
class Squad(object):
    """contains a number of Units. Takes a list of Units"""
    def __init__(self, units=[]):
        self.units = units
        self.size = len(self.units)
        self.value = sum([i for i in units.comp.values()])

class Scient(Unit):
    """A Scient (playable character) unit.
    
    Initializer takes element and comp:
      * element - this unit's element (E, F, I, or W) aka 'suit'
      * comp - dictionary of this unit's composition on (0..255) {E: earth, F: fire, I: ice, W: wind}
    """
    def __init__(self, element, comp):
        Unit.__init__(self, element, comp)
        #self.element = element
        #self.comp = comp
        self.age = 16
        #self.level = 0 # i think this needs to be removed - rix 10-2-09
        self.current_job = FT
        self.past_jobs = dict(zip(JOBS, [0, 0, 0, 0])) #set all job levels to 0
        self.skills = [] #Should be calculated from past_jobs and current job
        self.move = 4
        self.location = None
        
        #these get set by calcstat
        self.p = 0
        self.m = 0
        self.atk = 0
        self.defe = 0
        self.pdef = 0
        self.patk = 0
        self.matk = 0
        self.mdef = 0
        self.hp = 0
        self.mp = 0
        self.calcstats()
    
    def calcstats(self): #This function is a work in progress
        #CAN ONLY BE CALLED ONCE!!!
        self.p    = (2*(self.comp[F] + self.comp[E]) + self.comp[I] + \
                    self.comp[W]) 
        self.m    = (2*(self.comp[I] + self.comp[W]) + self.comp[F] + \
                    self.comp[E])
        self.atk  = (2*(self.comp[F] + self.comp[I]) + self.comp[E] + \
                    self.comp[W]) + (2 * self.value())
        self.defe = (2*(self.comp[E] + self.comp[W]) + self.comp[F] + \
                    self.comp[I]) 
        self.pdef = self.p + self.defe + (2 * self.comp[E])
        self.patk = self.p + self.atk  + (2 * self.comp[F])
        self.matk = self.m + self.atk  + (2 * self.comp[I])
        self.mdef = self.m + self.defe + (2 * self.comp[W])
        self.hp   = 4 * (self.pdef + self.mdef) + self.value()
        self.mp = 0  # Soon to be deleted.

    def comp_as_tuple(self):
        tuple = ()
        for x in ELEMENTS:
            tuple += (self.comp[x],)
        return tuple
    
    def pdmg(self, target):
        """Calculates the physical damage of an attack"""
        damage_dealt = {E: 0, F: 0, I: 0, W: 0}
        
        for element in damage_dealt:
            dmg = (self.p + self.patk + (2 * self.comp[element])) - \
                  (target.p + target.pdef + (2 * target.comp[element]))
            dmg = max(dmg, 0)
            damage_dealt[element] = dmg
             
        damage = sum(damage_dealt.values())
        return damage

    def mdmg(self, target, element):
        """Calculates the magical damage of an attack"""
        damage_dealt = {E: 0, F: 0, I: 0, W: 0}
        
        for ele in damage_dealt:
                dmg = (self.m + self.matk + (2 * self.comp[ele])) - \
                      (target.m + target.mdef + (2 * target.comp[ele]))
                dmg = max(dmg, 0)
                damage_dealt[ele] = dmg
        damage = sum(damage_dealt.values())
        
        #turns suit damage into healing
        if element == target.element:
            damage = 0 - damage
        
        return damage
    
    def phit(self, coord, battlefield):
        """Physically hit a location on the battlefield grid"""
        xa,ya = self.location
        xt,yt = coord
        #Are contents in range?
        if abs(xt - xa) <= 1 and abs(yt - ya) <= 1:
            #Can the contents be hit?
            if battlefield.grid[xt][yt].contents != None:
                if battlefield.grid[xt][yt].contents.hp:
                    #Damage is calculated here.
                    dmg = self.pdmg(battlefield.grid[xt][yt].contents)
                    if dmg < 0:
                        print "negative damage from a physical attack, something is \
                        wrong."
                    elif dmg == 0:
                        print "No Damage Dealt."
                    else:
                        #Damage is applied here.
                        if dmg >= battlefield.grid[xt][yt].contents.hp:
                            battlefield.grid[xt][yt].contents.hp = 0
                            battlefield.grid[xt][yt].contents.location = None
                            battlefield.grid[xt][yt].contents    = None
                            print "%s point(s) of damage dealt, target \
Killed." %dmg
                        else:
                            battlefield.grid[xt][yt].contents.hp -= dmg
                            print "%s point(s) of damage dealt" %dmg
                else: 
                    print "contents of (%s,%s) cannot take damage" %(xt,yt)
            else:
                print "(%s,%s) is empty, nothing to hit" %(xt,yt)
        else:
            print "(%s,%s) is too far away to hit." %(xt,yt)
        
    
    def mhit(self, coord, battlefield, element=None):
        """Magically hit a location on the battlefield grid, defaults to element
        of attacker"""
        if element == None:
            element = self.element
        xa,ya = self.location
        xt,yt = coord
        #Are contents in range?
        if abs(xt - xa) <= 1 and abs(yt - ya) <= 1:
            #Can the contents be hit?
            if battlefield.grid[xt][yt].contents != None:
                if battlefield.grid[xt][yt].contents.hp:
                    #Damage is calculated here.
                    dmg = self.mdmg(battlefield.grid[xt][yt].contents, element)
                    if dmg < 0:
                        #heal
                        battlefield.grid[xt][yt].contents.hp += abs(dmg)
                        print "Target healed %s point(s)" %abs(dmg)
                    elif dmg == 0:
                        print "No Damage Dealt."
                    else:
                        #Damage is applied here.
                        if dmg >= battlefield.grid[xt][yt].contents.hp:
                            battlefield.grid[xt][yt].contents.hp = 0
                            battlefield.grid[xt][yt].contents.location = None
                            battlefield.grid[xt][yt].contents = None
                            print "%s point(s) of %s damage dealt, target \
Killed." %(dmg, element)
                        else:
                            battlefield.grid[xt][yt].contents.hp -= dmg
                            print "%s point(s) of %s damage dealt" \
                            %(dmg, element)
                else: 
                    print "contents of %s cannot take damage" %coord
            else:
                print "%s is empty, nothing to hit" %coord
        else:
            print "X: %s, Y: %s is too far away to hit." %(xt,yt)

    def strikes(self, tile, level, element, battlefield):
        """Fighter's attack, short-range"""
        target = battlefield.get_tile(tile)
        damage = self.pdmg(target)
        chance = (1/16.) * level
        if random.random() < chance:
            SKILLS[FT][element].use(self, tile, battlefield)
        
        #apply damage
        target.hp -= damage
    
    def shoots(self, target, level, element): #TODO: convert target to tile (and for all other actions)
        """Shooter's attack, long-range"""
        #all shots go 4 squares in lines, hitting whatever is in their path.
        #hitting the 1st square at 1.0*damage, 2nd@.75dmg, 3rd@.5dmg 4th@.25dmg
        damage = self.pdmg(target)
        if self.element == E:
            chance = (1/16.) * level
            pass
        if self.element == F:
            pass
        if self.element == I:
            pass
        if self.element == W:
            pass
    
    def touches(self, target, level, element):
        """Theurgist's attack, close-range"""
        if level == 1:
            damage = .5*(self.mdmg(target, element))
            pass
        damage = (0.5+(1/16.)*level)*(self.mdmg(target, element)) #TODO: correct?
        pass
    
    def blasts(self, target, level, element):
        """Wizard's attack, long-range"""
        #TODO:
        pass

    def change_job(self, newjob):
        if not newjob in JOBS:
            raise Exception("%s is not a valid job" % newjob)
        elif newjob == self.current_job:
            print "I am already working on that job"
        else:
            self.current_job = newjob
            print "I am now working on %s" % self.current_job
    
    def year_up(self):
        """Ages the unit one year, leveling and applying bonuses/penalties"""
        self.age += 1
        self.level += 1
        self.past_jobs[self.current_job] += 1
        bonuses = dict(zip(["p", "m", "patk", "pdef", "mdef", "mdef"], [2]*6))
        
        #set bonuses
        if self.current_job == FT:
            bonuses["p"] = 8
            bonuses["matk"] = 4
        elif self.current_job == SH:
            bonuses["p"] = 8
            bonuses["pdef"] = 4
        elif self.current_job == TH:
            bonuses["m"] = 8
            bonuses["matk"] = 4
        elif self.current_job == WZ:
            bonuses["m"] = 8
            bonuses["mdef"] = 4
        
        #calculate penalty
        for attr in bonuses:
            bonuses[attr] += -1*(self.age // 16) + 1
        
        #apply the bonuses to the actual stats
        for attr in bonuses:
            setattr(self, attr, bonuses[attr])
        
        #recalculate stats
        self.calcstats()
    
    def level_up():
        """determines which skill will be learned this level_up"""
        #TODO: a mess, we got rid of levels (in the documentation because we
        #forgot about this...)
        self.level = self.level + 1
    

class Nescient(Unit):
        def bite(self, target):
            pass
        
        def breath(self, target):
            pass



