from UserList import UserList
from stone import Stone
from const import ELEMENTS, E, F, I, W, ORTH, OPP, WEP_LIST
from datetime import datetime
from weapons import Sword, Bow, Wand, Glove

class Unit(Stone):
    def __init__(self, element, comp, name=None, location=None, sex='female'):
        if not element in ELEMENTS:
            raise Exception("Invalid element: %s, valid elements are %s" \
            % (element, ELEMENTS))
        if comp[element] == 0:
            raise ValueError("Units' primary element must be greater than 0.")
        
        if comp[OPP[element]] != 0:
            raise ValueError("Units' opposite element must equal 0.")

        Stone.__init__(self, comp)
        self.element = element
        if name == None:
            self.name = self.__hash__()
        self.name = name
        self.location = location
        self.sex = sex
        self.DOB = datetime.utcnow()
        self.DOD = None
        self.val = self.value()
        def __repr__(self):
            return self.name

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
        #does this make sense? It was wrong for a long time.
        self.hp   = 4 * ((self.pdef + self.mdef) + self.value())
        
class Scient(Unit):
    """A Scient (playable character) unit.
    
    Initializer takes element and comp:
      * element - this unit's element (E, F, I, or W) aka 'suit'
      * comp - dictionary of this unit's composition on (0..255) {E: earth, 
      F: fire, I: ice, W: wind}
    """
    
    def equip(self, weapon): #TODO move to battlefield
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
    
    def unequip(self):
        """removes weapon from scient, returns weapon."""
        weapon = self.weapon
        self.weapon = None
        return weapon
    
    def __init__(self, element, comp, name=None, weapon=None,
                 weapon_bonus=None, location=None, sex='female'):
        for orth in ORTH[element]:
            if comp[orth] > comp[element] / 2:
                raise ValueError("Scients' orthogonal elements cannot be \
                                  more than half the primary element's value.")
        Unit.__init__(self, element, comp, name, location, sex)
        self.move = 4
        self.weapon = weapon
        if weapon_bonus == None:
            self.weapon_bonus = Stone()
        else:
            self.weapon_bonus = weapon_bonus
        self.equip_limit = Stone({E:1, F:1 ,I:1 ,W:1})
        for i in self.equip_limit:
            self.equip_limit[i] = self.equip_limit[i] + self.comp[i] \
            + self.weapon_bonus[i]
        self.calcstats()
        
        #equiping weapons should be done someplace else.
        self.equip(self.weapon)

class Part(object):
    '''
    @property
    def pdef(self):
        return self.nescient.pdef
    '''
    def hp_fget(self):
        return self.nescient.hp
        
    def hp_fset(self, hp):
        self.nescient.hp = hp
        
    hp = property(hp_fget, hp_fset)
        
    def __init__(self, nescient, location=None):
        self.nescient = nescient
        self.location = location

class Nescient(Unit):
    """A non-playable unit."""
    
    def take_body(self, new_body):
        """Takes locations from new_body and applies them to body."""
        for part in new_body:
            new_body[part].nescient = self
            self.body = new_body
            
    def calcstats(self):
        Unit.calcstats(self)
        self.atk  = (2*(self.comp[F] + self.comp[I]) + 
                        self.comp[E] + self.comp[W]) + (4 * self.value())
        self.hp = self.hp * 4 #This is an open question.
    
    def __init__(self, element, comp, name=None, weapon=None,
                 location=None, sex='female', facing=None, 
                 body={'head': None, 'left':None, 'right':None, 'tail':None}):
        comp = Stone(comp)
        for orth in ORTH[element]:
            if comp[orth] != 0:
                if comp[OPP[orth]] != 0:
                    raise ValueError("Nescients' cannot have values greater \
                                      than zero for both orthogonal elements.")
            elif comp[orth] > comp[element]:
                raise ValueError("Nescients' orthogonal value cannot exceed \
                                  the primary element value.")
            
        Unit.__init__(self, element, comp, name, location, sex)
        self.move = 4
        #Set nescient type.
        if self.element == 'Earth':
            self.kind = 'p'
            if self.comp[F] == 0:
                self.type = 'Avalanche' #AOE Full
            else:
                self.type = 'Magma' #ranged Full
                
        elif self.element == 'Fire':
            self.kind = 'p'
            if self.comp[E] == 0:
                self.type = 'Firestorm' #ranged DOT
                self.time = 3
            else:
                self.type = 'Forestfire' #ranged Full
                
        elif self.element == 'Ice':
            self.kind = 'm'
            if self.comp[E] == 0:
                self.type = 'Icestorm' #AOE DOT
                self.time = 3
            else:
                self.type = 'Permafrost' #AOE Full
        else: #Wind
            self.kind = 'm'
            self.time = 3
            if self.comp[F] == 0:
                self.type = 'Blizzard' #AOE DOT
            else:
                self.type = 'Pyrocumulus' #ranged DOT
                
             
        self.calcstats()
        for part in body: #MESSY!!!!
            body[part] = Part(self)
        self.body = body
        self.location  = location #...
        self.facing = facing
        self.weapon = self #hack for attack logic.

       
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

    def __init__(self, data=None, name=None, kind=None, element=None):
        self.val = 0
        self.free_spaces = 8
        self.name = name
        UserList.__init__(self)
        if data == None:
            # The code below creates 4 units of element with a comp
            # of (4,2,2,0). Each unit is equiped with a unique weapon.
            if kind == 'mins':
                if element != None:
                    s = Stone()
                    s[element] = 4
                    s[OPP[element]] = 0
                    for o in ORTH[element]:
                        s[o] = 2
                    for wep in WEP_LIST:
                        scient = Scient(element, s)
                        scient.equip(eval(wep)(element, Stone()))
                        scient.name = "Ms. " + wep
                        self.append(scient)
                else:
                    raise("Kind requires element from %s." %ELEMENTS)
                if self.name == None:
                    self.name = element + " " + 'mins'
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
        self.val += val.value()
        self.free_spaces -= size
        key.squad = self
        
    def __delitem__(self, key):
        del self.data[key].squad
        temp = self[key].value()
        self.free_spaces += self.unit_size(self[key])
        self.data.__delitem__(key)
        self.val -= temp
        
    def append(self, item):
        size = self.unit_size(item)
        if self.free_spaces < size:
            raise Exception( \
            "There is not enough space in the squad for this unit")
        self.data.append(item)
        self.val += item.value()
        self.free_spaces -= size
        item.squad = self
            
    def __repr__(self, more=None):
        """This could be done better..."""
        if more != None:
            if self.val > 0:
                s = ''
                for i in range(len(self)):
                    s += str(i) + ': ' + str(self[i].name) + '\n'
                return "Name: %s, Value: %s, Free spaces: %s \n%s" \
                %(self.name, self.val, self.free_spaces, s)
        else:
            return "Name: %s, Value: %s, Free spaces: %s \n" %(self.name, \
            self.val, self.free_spaces)
    
    def __call__(self, more=None):
        return self.__repr__(more)
