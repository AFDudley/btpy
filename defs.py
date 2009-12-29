"""Definitions for game units and unit interaction"""

import random
from math import log

from const import * #needs fix, maybe whole file needs rewrite
                    #why aren't there constants in python?
                    
class Stone(object):
    def __init__(self, comp):
        self.comp = comp
    
    def value(self):
        """Returns sum of comp, overload as needed"""
        sum = 0
        for x in self.comp.keys():
            sum += self.comp[x]
        return sum

    def imbue(self, stone):
        for i in self.comp:
            self.comp[i] += stone.comp[i]

attack = ('phit','mhit','Pugil','Shoot','Blast','Theurge')

class Weapon(Stone): #the names of all these functions is quite confusing; fix.
    """Scients Equip weapons to do damage"""
    def __init__(self, element, comp):
        Stone.__init__(self, comp)
        self.element = element
        self.type ='None'
        self.attack_pattern = [(0,-1),(1,0),(0,1),(-1,0)]
    
    def map_to_grid(self, origin, grid_size):
        """maps pattern to grid centered on origin. 
        Returns list of tiles on grid."""
        orix,oriy = origin
        tiles = []
        for i in self.attack_pattern:
            if 0 <= (i[0] + origin[0]) < gridx:
                if 0 <= (i[1] + origin[1]) < gridy:
                    tiles.append(i)
        return tiles
    
class Sword(Weapon):
    """Close range physial weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Earth'
        self.targets = [(0,-1),(1,0),(0,1),(-1,0)]
    
class Bow(Weapon):
    """Long range physical weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Fire'
        def make_attack_pattern():
            no_hit = 4 #the scient move value
            min = -8
            max = 9
            dist = range(min,max)
            temp = []
            [[temp.append((x,y)) for y in dist if (no_hit < (abs(x) \
            + abs(y)) < max) ] for x in dist]
            return temp
        self.attack_pattern = make_attack_pattern()
    
class Wand(Weapon):
    """Long range magical weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Ice'
        self.targets = []
    def make_pattern(self, origin, distance, pointing):
        """generates a pattern based on an origin, distance, and
        direction. Returns a set of coords"""
        
        #needs lots o checking
        src = origin
        sid = 2 * distance
        pattern = []
        tiles = []
        for i in xrange(sid): #generate pattern based on distance from origin
            if i % 2:
                in_range = xrange(-(i/2),((i/2)+1))
                #rotate pattern based on direction
                for j in xrange(len(in_range)): 
                    if pointing == 'North':
                        pattern.append((src[0] + in_range[j], (src[1] - (1 +(i/2)))))
                    elif pointing =='South':
                        pattern.append((src[0] + in_range[j], (src[1] + (1 +(i/2)))))
                    elif pointing =='East':
                        pattern.append((src[0] +  (1 +(i/2)), (src[1] - in_range[j])))
                    elif pointing =='West':
                        pattern.append((src[0] -  (1 +(i/2)), (src[1] - in_range[j])))
        
        return pattern
        
    def map_to_grid(self, origin, grid_size):
        """Maps pattern to grid centered on origin.
        Returns list of tiles on grid.
        
        (This is much more complex than default function because in the case 
        of Wands the attack_pattern is based on the origin in relation to the 
        parimiter of the grid)"""
        direction = {0:'West', 1:'North', 2:'East', 3:'South'}
        maxes = (origin[0], origin[1], (grid_size[0] - 1 - origin[0]), \
        (grid_size[1] - 1 - origin[1]),)
        tiles = []
        for i in direction:
            for j in  self.make_pattern(origin, maxes[i], direction[i]):
                if 0 <= j[0] < grid_size[0]:
                    if 0 <= j[1] < grid_size[1]:
                        tiles.append(j)
        return tiles

class Glove(Weapon):
    """Close range magical weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Wind'
        self.time = 3
        self.targets = [(0,-1),(1,0),(0,1),(-1,0)]
    
class Unit(object):
    def __init__(self, element, comp):
        if not element in ELEMENTS:
            raise Exception("Invalid element: %s, valid elements are %s" \
            % (element, ELEMENTS))
        self.element = element
        self.comp = comp
        self.p    = None
        self.m    = None
        self.defe = None
        self.atk  = None
        self.patk = None
        self.pdef = None
        self.matk = None
        self.mdef = None
        self.hp   = None
        self.age  = None
        self.name = None
        self.location = None
        self.weapon = None
        
    def value(self):
        """Returns sum of comp, overload as needed"""
        sum = 0
        for x in self.comp.keys():
            sum += self.comp[x]
        return sum
        
    def __repr__(self):
        if self.name:
            title = self.name
        else:
            title = str(id(self))
            
        #There is some cleaner way to write these things...
        return "%s -> suit:% 2s | val: %s | loc: %s | comp: (%s, %s, %s, %s) \
| p: %s \nHP: % 7s | PA/PD: (% 5s,% 5s) | MA/MD: (% 5s,% 5s) \n" % (title, \
    self.element[0], self.value(), self.location, self.comp[E], self.comp[F], \
    self.comp[I], self.comp[W], self.p, self.hp, self.patk, self.pdef, \
    self.matk, self.mdef) 


class Scient(Unit):
    """A Scient (playable character) unit.
    
    Initializer takes element and comp:
      * element - this unit's element (E, F, I, or W) aka 'suit'
      * comp - dictionary of this unit's composition on (0..255) {E: earth, 
      F: fire, I: ice, W: wind}
    """
    
    def __init__(self, element, comp):
        Unit.__init__(self, element, comp)
        #self.element = element
        #self.comp = comp
        self.age = 16
        self.move = 4
        self.weapon_bonus = COMP.copy()
        self.equip_limit = {E:1, F:1 ,I:1 ,W:1}
        for i in self.equip_limit:
            self.equip_limit[i] = self.equip_limit[i] + self.comp[i] \
            + self.weapon_bonus[i]            
        self.calcstats()
        self.equip()
   
    '''
    def attack(self, battlefield, target):
        "returns a list of targets damage"""
        if self.weapon.type == 'Earth' or self.weapon.type == 'Wind':
            return self.weapon.attack(target)
        else:
            self.valid_targets
            return self.weapon.attack(battlefield, target)
    '''

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
    
    def equip(self, weapon=None):
        if weapon == None:
            if self.element == 'Earth':
                self.weapon = Sword(self.element, COMP.copy())
            elif self.element == 'Fire':
                self.weapon = Bow(self.element, COMP.copy())
            elif self.element == 'Ice':
                self.weapon = Wand(self.element, COMP.copy())
            else:
                self.weapon = Glove(self.element, COMP.copy())
            
        else:
            if weapon.value() > self.equip_limit[weapon.type]:
                raise Exception("This unit cannot equip this weapon")
            else:
                self.weapon = weapon
        
    '''
    def phit(self, coord, battlefield):
        """Physically hit a location on the battlefield grid"""
        if self.location == coord:
            raise Exception("Stop hitting yourself")
            
        xa,ya = self.location
        xt,yt = coord
        #Are contents in range?
        if abs(xt - xa) <= 1 and abs(yt - ya) <= 1:
            #Can the contents be hit?
            if battlefield.grid[xt][yt].contents != None:
                if battlefield.grid[xt][yt].contents.hp:
                    #Damage is calculated here.
                    dmg = Weapon.pdmg(battlefield.grid[xt][yt].contents)
                    if dmg < 0:
                        raise Exception("negative damage from a physical \
attack, something is wrong.")
                    elif dmg == 0:
                        print "No Damage Dealt."
                    else:
                        #Damage is applied here.
                        if dmg >= battlefield.grid[xt][yt].contents.hp:
                            battlefield.grid[xt][yt].contents.hp = 0
                            battlefield.grid[xt][yt].contents.location = None
                            battlefield.grid[xt][yt].contents = None
                            print "%s point(s) of damage dealt, target \
Killed." %dmg
                        else:
                            battlefield.grid[xt][yt].contents.hp -= dmg
                            print "%s point(s) of damage dealt" %dmg
                else: 
                    raise Exception("contents of (%s,%s) cannot take damage" \
                    %(xt,yt))
            else:
                raise Exception("(%s,%s) is empty, nothing to hit" %(xt,yt))
        else:
            raise Exception("(%s,%s) is too far away to hit." %(xt,yt))        
    '''
    
    '''
    def mhit(self, coord, battlefield, element=None):
        """Magically hit a location on the battlefield grid, defaults to element
        of attacker"""
        if self.location == coord:
            raise Exception("Stop Hitting yourself")
        
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
                    raise Exception("contents of (%s, %s) cannot take damage" \
                    %(xt,yt))
            else:
                raise Exception("(%s, %s) is empty, nothing to hit" %(xt,yt))
        else:
            raise Exception( "(%s, %s) is too far away to hit." %(xt,yt))
    '''
        
    def shoots(self, target, battlefield): 
        """Shooter's attack, long-range"""
        if self.location == target:
            raise Exception("Stop hitting yourself")
        xa,ya = self.location
        in_range = []
        #Because list comprehension is so easy to understand.
        [[in_range.append((x,y)) for y in range(-8,9) if (4 < (abs(x) \
        + abs(y)) < 9) ] for x in range(-8,9)]
        for i in range(len(in_range)):
            in_range[i] = ((in_range[i][0] + xa), (in_range[i][1] + ya))
            
        if in_range.__contains__(target) == False:
            raise Exception("Target is not in range")
        else:
            damage = self.pdmg(target)
        
        return damage/4
    
class Nescient(Unit):
        def bite(self, target):
            pass
        
        def breath(self, target):
            pass

class Squad(list):
    """contains a number of Units. Takes a list of Units"""
    def unit_size(self, object):
        if isinstance(object, Unit) == False:
            raise TypeError("Squads can contain only Units")
        else:
            if isinstance(object, Scient):
                return 1
            else:
                return 2
                
    def __init__(self, lst=None, name=None):
        self.value = 0
        self.free_spaces = 8
        self.name = name
        list.__init__(self)
        if lst == None:
            return
        
        if isinstance(lst, list):
            for x in lst: self.append(x)
        
        else:
            self.append(lst)
            
    def __setitem__(self, key, val):
        size = self.unit_size(key)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the squad for this unit")
        list.__setitem__(self, key, val)
        self.value += val.value()
        self.free_spaces -= size
        key.squad = self
        
    def __delitem__(self, key):
        del key.squad
        temp = self[key].value()
        self.free_spaces += self.unit_size(self[key])
        list.__delitem__(self, key)
        self.value -= temp
        
    def append(self, item):
        size = self.unit_size(item)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the squad for this unit")
        list.append(self, item)
        self.value += item.value()
        self.free_spaces -= size
        item.squad = self
            
    def __repr__(self, more=None):
        """This could be done better..."""
        if more != None:
            if self.value > 0:
                s = ''
                for i in range(len(self)):
                    s += str(i) + ': ' + str(self[i]) + '\n'
                return "Name: %s, Value: %s, Free spaces: %s \n%s" \
                %(self.name, self.value, self.free_spaces, s)
        else:
            return "Name: %s, Value: %s, Free spaces: %s \n" %(self.name, \
            self.value, self.free_spaces)
    
    def __call__(self, more=None):
        return self.__repr__(more)
