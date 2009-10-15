"""Definitions for game units and unit interaction"""

import random
from math import log

ELEMENTS = E, F, I, W = ("Earth", "Fire", "Ice", "Wind")

ORTH = {E: (F, I), #Earth is orthogonal to Fire and Ice
        F: (E, W), #Fire  is orthogonal to Earth and Wind
        I: (E, W), #Ice   is orthogonal to Earth and Wind
        W: (F, I), #Wind  is orthogonal to Fire and Ice
        "test": (E, W)}

OPP = {E: W, W: E, #Earth and Wind are opposites
       F: I, I: F} #Fire and Ice are opposites

JOBS = FT, TH, SH, WZ = ("Fighter", "Theurgist", "Shooter", "Wizard")

MAXLEVEL = int((112-16)/2.0) #max level is (112 years - 16 years) / 2 lvls per year = 48

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
    target.p_attack = target.p_attack*(31/32.)
    battlefield.status_effects.append((target, "Disable skill...")) #TODO: chance of disabling all skills for a turn.
def break_armor_logic(u,target,b):
    target.p_defense = target.p_defense*(63/64.) #TODO: need a real value
    target.m_defense = target.m_defense*(63/64.) #TODO: need a real value
def break_weapon_logic(u,target,b):
    target.p_attack = target.p_attack*(63/64.) #TODO: need a real value
    target.m_attack = target.m_attack*(63/64.) #TOOD: need a real value
maim_leg = Skill(E, "Maim leg", maim_leg_logic)
maim_arm = Skill(F, "Maim arm", maim_arm_logic)
break_armor = Skill(I, "Break armor", break_armor_logic)
break_weapon = Skill(W, "Break weapon", break_weapon_logic)

## theurgist skills ############################################################

def make_dot_logic(element):
    def inner(unit, target, battlefield):
        dmg = unit.mag_damage(target, element)
        battlefield.status_effects.append((target, "DOT...")) #TODO: see chat window
        #dot: [1/(2^(turn-1)][mag_damage]
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
#        unit.mag_damage(target, element)
#        orign = battlefield.get_unit(target)

## set up skill arrays #########################################################

SKILL_ORDER = ['SS_2', 'SR_1', 'OR_1', 'SS_3', 'OS_2', 'SL_1', 'OL_1', 'SS_4', 'SR_2', 'SL_2', 'SS_5', 'OS_3', 'SR_3', 'OR_2', 'SS_6', 'SL_3', 'OL_2', 'SS_7', 'OS_4', 'SR_4', 'SL_4', 'SS_8']

SKILLS = {FT: {E: maim_leg,   F: maim_arm,   I: "Break armor",    W: "Break weapon", "test": test_skill},
          TH: {E: etouch,     F: ftouch,     I: itouch,           W: wtouch,         "test": test_skill},
          SH: {E: "Pierce",   F: "Spray",    I: "Charged attack", W: "Fortitude",    "test": test_skill},
          WZ: {E: "Blast",    F: "Blast",    I: "Blast",          W: "Blast",        "test": test_skill}}

################################################################################

class Item:
    def __init__(self, type, owner):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def equip(self):
        pass

    def remove(self):
        pass

    def use(self):
        pass

class Stone:
    def __init__(self, earth, fire, ice, wind):
        self.comp = {E: earth, F: fire, I: ice, W: wind}

    def imbue(self):
        pass

class Unit(object):
    def __init__(self, element, comp):
        self.element = element
        self.comp = comp

        self.p_attack = None
        self.p_defense = None
        self.m_attack = None
        self.m_defense = None
        self.age = None
    
   # def repr(self):
   #     return "%s -> HP:% 5s | MP:% 5s | Element:% 5s | P Atk/Def: (% 3s,% 3s) | M Atk/Def: (% 3s,% 3s)" % (id(u), u.hp, u.mp, u.element, u.p_attack, u.p_defense, u.m_attack, u.m_defense)
#TODO: inheriting from Unit is not buying anything for us here (in terms of Scient,
# which just overwrites Unit's __init__ (unless you use super?))

class Scient(Unit):
    """A Scient (playable character) unit.

    Initializer takes element and comp:
      * element - this unit's element (E, F, I, or W) aka 'suit'
      * comp - dictionary of this unit's composition on (0..255) {E: earth, F: fire, I: ice, W: wind}
    """
    def __init__(self, element, comp):
        if not element in ELEMENTS:
            raise Exception("Invalid element: %s, valid elements are %s" % (element, ELEMENTS))
        self.element = element
        self.comp = comp
        self.age = 16
        self.level = 0 # i think this needs to be removed - rix 10-2-09
        self.current_job = FT
        self.past_jobs = dict(zip(JOBS, [0, 0, 0, 0])) #set all job levels to 0
        self.skills = []
        self.move = 4

        #these get set by calcstat
        self.str = 0
        self.int = 0
        self.p_defense = 0
        self.p_attack = 0
        self.m_attack = 0
        self.m_defense = 0
        self.hp = 0
        self.mp = 0
        self.calcstats()

    def calcstats(self):
        self.str = 2*(self.comp[F] + self.comp[E]) + self.comp[I] + self.comp[W] # 0..1280
        self.int = 2*(self.comp[I] + self.comp[W]) + self.comp[F] + self.comp[E] # 0..1280
        self.p_defense = self.comp[E] + self.str # 0..1536
        self.p_attack = self.comp[F] + self.str # 0..1536
        self.m_defense = self.comp[W] + self.int # 0..1536
        self.m_attack = self.comp[I] + self.int # 0..1536
        self.hp = int((self.str * self.p_defense) / 128.) # 0..15360 (check)
        self.mp = int((self.int * self.m_attack) / 128.) # 0..15360 (check)

    def strikes(self, tile, level, element, battlefield):
        """Fighter's attack, short-range"""
        target = battlefield.get_tile(tile)
        damage = self.phys_damage(target)
        chance = (1/16.) * level
        if random.random() < chance:
            SKILLS[FT][element].use(self, tile, battlefield)

        #apply damage
        target.hp -= damage

    def shoots(self, target, level, element): #TODO: convert target to tile (and for all other actions)
        """Shooter's attack, long-range"""
        #all shots go 4 squares in lines, hitting whatever is in their path.
        #hitting the 1st square at 1.0*damage, 2nd@.75dmg, 3rd@.5dmg 4th@.25dmg
        damage = self.phys_damage(target) 
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
            damage = .5*(self.mag_damage(target, element))
            pass
        damage = (0.5+(1/16.)*level)*(self.mag_damage(target, element)) #TODO: correct?
        pass

    def blasts(self, target, level, element):
        """Wizard's attack, long-range"""
        #TODO:
        pass

    def phys_damage(self, target):
        """Calculates the physical damage of an attack"""
        damage_dealt = {E: 0, F: 0, I: 0, W: 0}

        #xdamage is (A' times comp[X]) minus (D' times comp[X])
        #negative values are the same as 0
        for element in damage_dealt:
            dmg = (self.str * self.p_attack * self.comp[element]) - (target.str * target.p_defense * target.comp[element])
            dmg = max(dmg, 0) #to set negative values to zero
            damage_dealt[element] = dmg

        #for the elements orthogonal to the attacker, halve the damage
        for element in ORTH[self.element]:
            damage_dealt[element] /= 2.0

        #i think the 512 value should be based on age/level @rix
        for element in damage_dealt:
            damage_dealt[element] /= 2**(16+2.0/self.age)

        damage = sum(damage_dealt.values())

        return damage

    def mag_damage(self, target, element):
        """Calculates the damage of a magical attack"""
        damage = {E: 0, F: 0, I: 0, W: 0}

        damage[element] = ((2 * self.int * self.m_attack * self.comp[element]) - (2 * target.int * target.m_defense * target.comp[element])) / 32.0

        return damage[self.element]

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
        bonuses = dict(zip(["str", "int", "p_attack", "p_defense", "m_attack", "m_defense"], [2]*6))

        #set bonuses
        if self.current_job == FT:
            bonuses["str"] = 8
            bonuses["p_attack"] = 4
        elif self.current_job == SH:
            bonuses["str"] = 8
            bonuses["p_defense"] = 4
        elif self.current_job == TH:
            bonuses["int"] = 8
            bonuses["m_attack"] = 4
        elif self.current_job == WZ:
            bonuses["int"] = 8
            bonuses["m_defense"] = 4

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

