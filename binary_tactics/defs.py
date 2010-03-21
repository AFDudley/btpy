"""Definitions for game units and unit interaction"""
from warnings import warn
from collections import namedtuple, Mapping
from UserList import UserList
from UserDict import UserDict
from operator import contains
from random import randint
from const import * #needs fix, maybe whole file needs rewrite
                    #why aren't there constants in python?


class Loc(namedtuple('Loc', 'x y')):
    __slots__ = ()
    def __repr__(self):
        return '(%r, %r)' % self
noloc = Loc(None,None)     

class Stone(Mapping):
    """ugh."""
    def __init__(self, comp=None):
        self.comp = {'Earth': 0, 'Fire': 0, 'Ice': 0, 'Wind': 0}
        #self.id = randint(1000000000, 2**32)
        if isinstance(comp, Stone):
            self.comp = comp.comp
        if comp == None:
            comp = self.comp
        try:
            iter(comp)
            if sorted(self.comp) == sorted(comp):
                self.comp = dict(comp)
            else:
                if len(comp) == 4 or len(comp) == 0:
                    for element in range(4):
                        if type(comp[element]) == type(1):
                            if 0 <= comp[element] < 256:
                                self.comp[ELEMENTS[element]] = comp[element]                        
                            else:
                                raise AttributeError
                        else:
                            raise TypeError
                else:
                    raise ValueError
        except TypeError:
            raise
        
    def __iter__(self):
         return iter(self.comp)
    def __contains__(self, value):
         return value in self.comp
    def __getitem__(self,key):
        return self.comp[key]
    def __setitem__(self,key,value):
        self.comp[key] = value
    def __len__(self):
         return len(self.comp)

    """
    __hash__ and __cmp__ are hacks to get around scients being mutable.
    I think the answer is to actually make stones immutable and
    have imbue return a different stone.
    """

    def __hash__(self):
        return id(self)
                
    def tup(self):
        tup = ()
        for key in sorted(self.comp):
            tup += (self.comp[key],)
        return tup
        
    def value(self):
        return sum(self.comp.values())

class Weapon(Stone):
    """Scients Equip weapons to do damage"""
    def __init__(self, element, comp, type=None):
        #this should return the correct weapon based on type. (?)
        Stone.__init__(self, comp)
        self.type ='None'
        self.element = element
    
    def __repr__(self):
        return dict.__repr__(self.__dict__)
    
    def map_to_grid(self, origin, grid_size):
        """maps pattern to grid centered on origin. 
        Returns list of tiles on grid. (Lots of room for optimization)"""
        orix,oriy = origin
        tiles = []
        if self.type != 'Wand':
            if self.type == 'Bow':
                no_hit = 4 #the scient move value
                min = -(2 * no_hit)
                max = -min + 1
                dist = range(min,max)
                attack_pattern = []
                #???
                [[attack_pattern.append((x,y)) for y in dist if (no_hit < (abs(x) + abs(y)) < max) ] for x in dist]
            else:
                attack_pattern = [(0,-1),(1,0),(0,1),(-1,0),(-1,-1),(-1,1),(1,1),(1,-1)]

            for i in attack_pattern:
                x,y = (i[0] + origin[0]),(i[1] + origin[1])
                if 0 <= x < grid_size[0]:
                    if 0 <= y < grid_size[1]:
                        tiles.append((x,y))
            return tiles
        else:
            def make_pattern(self, origin, distance, pointing):
                """generates a pattern based on an origin, distance, and
                direction. Returns a set of coords"""
                #TODO: use inversion to create Wand/Ice attack pattern.
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

class Sword(Weapon):
    """Close range physial weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Sword'
    
class Bow(Weapon):
    """Long range physical weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)      
        self.type = 'Bow'
        
class Wand(Weapon):
    """Long range magical weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Wand'

    def make_pattern(self, origin, distance, pointing):
        """generates a pattern based on an origin, distance, and
        direction. Returns a set of coords"""
        #TODO: use inversion to create wand attack pattern.
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
                        pattern.append((src[0] + in_range[j], (src[1] -
                                       (1 +(i/2)))))
                    elif pointing =='South':
                        pattern.append((src[0] + in_range[j], (src[1] + 
                                       (1 +(i/2)))))
                    elif pointing =='East':
                        pattern.append((src[0] +  (1 +(i/2)), (src[1] - 
                                        in_range[j])))
                    elif pointing =='West':
                        pattern.append((src[0] -  (1 +(i/2)), (src[1] -
                                        in_range[j])))
        
        return pattern

class Glove(Weapon):
    """Close range magical weapon"""
    def __init__(self, element, comp):
        Weapon.__init__(self, element, comp)
        self.type = 'Glove'
        self.time = 3
           
class Unit(Stone):
    def __init__(self, element, comp, name=None, location=noloc):
        if not element in ELEMENTS:
            raise Exception("Invalid element: %s, valid elements are %s" \
            % (element, ELEMENTS))
        Stone.__init__(self, comp)
        self.element = element
        if name == None:
            self.name = self.__hash__()
        self.name = name
        self.location = location
        self.val = self.value()
    
class Scient(Unit):
    """A Scient (playable character) unit.
    
    Initializer takes element and comp:
      * element - this unit's element (E, F, I, or W) aka 'suit'
      * comp - dictionary of this unit's composition on (0..255) {E: earth, 
      F: fire, I: ice, W: wind}
    """
    
    def __init__(self, element, comp, name=None, weapon=None,
                 weapon_bonus=dict(Stone()), location=noloc):
        Unit.__init__(self, element, comp, name, location)
        self.move = 4
        self.weapon = weapon
        self.weapon_bonus = weapon_bonus
        self.equip_limit = {E:1, F:1 ,I:1 ,W:1}
        for i in self.equip_limit:
            self.equip_limit[i] = self.equip_limit[i] + self.comp[i] \
            + self.weapon_bonus[i]
        self.calcstats()
        self.equip(self.weapon)

    def calcstats(self):
        self.p    = (2*(self.comp[F] + self.comp[E]) +
                        self.comp[I] + self.comp[W]) 
        self.m    = (2*(self.comp[I] + self.comp[W]) +
                        self.comp[F] + self.comp[E])
        self.atk  = (2*(self.comp[F] + self.comp[I]) + 
                        self.comp[E] + self.comp[W]) + (2 * self.value())
        self.defe = (2*(self.comp[E] + self.comp[W]) + 
                        self.comp[F] + self.comp[I]) 
        
        self.pdef = self.p + self.defe + (2 * self.comp[E])
        self.patk = self.p + self.atk  + (2 * self.comp[F])
        self.matk = self.m + self.atk  + (2 * self.comp[I])
        self.mdef = self.m + self.defe + (2 * self.comp[W])
        self.hp   = 4 * (self.pdef + self.mdef) + self.value()

    def equip(self, weapon):
        """
        A function that automagically equips items based on element.
        should be moved someplace else.
        """
        if weapon == None:
            if self.element == 'Earth':
                self.weapon = Sword(self.element, Stone())
            elif self.element == 'Fire':
                self.weapon = Bow(self.element, Stone())
            elif self.element == 'Ice':
                self.weapon = Wand(self.element, Stone())
            else:
                self.weapon = Glove(self.element, Stone())
            
        else:
            '''
            if weapon.value() > self.equip_limit[weapon.type]:
                raise Exception("This unit cannot equip this weapon")
            else:
                self.weapon = weapon
            '''
            self.weapon = weapon
            
class Nescient(Unit):
        def bite(self, target):
            pass
        def breath(self, target):
            pass

class Squad(UserList):
    """contains a number of Units. Takes a list of Units"""
    def unit_size(self, object):
        if isinstance(object, Unit) == False:
            raise TypeError("Squads can contain only Units")
        else:
            if isinstance(object, Scient):
                return 1
            else:
                return 2
    
    def hp(self):
        """Returns the total HP of the Squad."""
        return sum([unit.hp for unit in self])

    def __init__(self, data=None, name=None):
        self.value = 0
        self.free_spaces = 8
        self.name = name
        UserList.__init__(self)
        if data == None:
            return
            
        if isinstance(data, list):
            for x in data: 
                self.append(x)
        else:
            self.append(data)
            
    def __setitem__(self, key, val):
        #need to change how value of a squad is calculated.
        #does the value of a squad go down when a unit dies?
        #how do survival bonuses change squad values?
        size = self.unit_size(key)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the squad for this unit")
        list.__setitem__(self, key, val)
        self.value += val.value()
        self.free_spaces -= size
        key.squad = self
        
    def __delitem__(self, key):
        del self.data[key].squad
        temp = self[key].value()
        self.free_spaces += self.unit_size(self[key])
        self.data.__delitem__(self, key)
        self.value -= temp
        
    def append(self, item):
        size = self.unit_size(item)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the squad for this unit")
        self.data.append(item)
        self.value += item.value()
        self.free_spaces -= size
        item.squad = self
            
    def __repr__(self, more=None):
        """This could be done better..."""
        if more != None:
            if self.value > 0:
                s = ''
                for i in range(len(self)):
                    s += str(i) + ': ' + str(self[i].name) + '\n'
                return "Name: %s, Value: %s, Free spaces: %s \n%s" \
                %(self.name, self.value, self.free_spaces, s)
        else:
            return "Name: %s, Value: %s, Free spaces: %s \n" %(self.name, \
            self.value, self.free_spaces)
    
    def __call__(self, more=None):
        return self.__repr__(more)
