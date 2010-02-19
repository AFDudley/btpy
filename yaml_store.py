#
#  yaml_store.py
#  
#
#  Created by RiX on 2/14/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""This code converts game objects to and from yaml streams"""
import re
import yaml
import defs
#from helpers import t2c, rand_squad

def loc_representer(dumper, data):
    return dumper.represent_scalar(u'!loc', u'(%2s,%2s)' % data)
 
yaml.add_representer(defs.loc, loc_representer)

def loc_constructor(loader, node):
    value = loader.construct_scalar(node)
    try:
        x, y = map(int, value.strip('()').split(','))
    except ValueError: #This isn't so bad.
        x = y = None    
    return defs.loc(x,y)

yaml.add_constructor(u'!loc', loc_constructor)    

loc_pat = re.compile(r'^\(\s*\d+\s*,\s*\d+\s*\)\s*$')
none_pat = re.compile(r'^\(\s*None\s*,\s*None\s*\)\s*$')
yaml.add_implicit_resolver(u'!loc', loc_pat)
yaml.add_implicit_resolver(u'!loc', none_pat)


class Scient(yaml.YAMLObject):
    yaml_tag =u'!Scient'
    def __init__(self, scient):
        self.element= scient.element
        self.comp = scient.comp
        self.name = scient.name
        self.weapon = scient.weapon
        self.weapon_bonus = scient.weapon_bonus
        self.location = scient.location

    def to_defs(self):
        #haha (part 1)
        if  not(isinstance(self.weapon, defs.Weapon)):
            self.weapon = Weapon().load(self.weapon)
        return defs.Scient(self.element, self.comp, self.name, self.weapon,
                           self.weapon_bonus, self.location)
    def dump(self):
        #haha (part 2)
        if isinstance(self.weapon, defs.Weapon):
            self.weapon =  Weapon().dump(self.weapon)
        return yaml.dump(self, explicit_start=True, explicit_end=True)
        
class Squad(yaml.YAMLObject):
    yaml_tag = u'!Squad'
    def __init__(self, squad):
        '''
        I am so confused. In order for this to work, the number of units in
        the squad cannot change after init... this is so stupid.
        '''
        self.__dict__ = squad.__dict__
        self.lst = []
        for unit in squad:
            if isinstance(unit, defs.Scient):
                self.lst.append(Scient(unit))
        
    def to_defs(self):
        lst = []
        for unit in self.lst:
            lst.append(unit.to_defs())
        return defs.Squad(lst, self.name)
        
    def dump(self):
        tlst = self.lst
        txt = ''
        for unit in self.lst:
            txt += unit.dump()
        del self.lst
        stuff  = yaml.dump(self, explicit_start=True, explicit_end=True)
        self.lst = tlst
        return stuff + txt
           
class Weapon(yaml.YAMLObject):
    yaml_tag = u'!Weapon'
    def load(self, document):
        obj = yaml.load(document)
        if   obj.type == 'Earth':
            return defs.Sword(obj.element, obj.comp)
        elif obj.type == 'Fire':
            return defs.Bow(obj.element, obj.comp)
        elif obj.type == 'Ice':
            return defs.Wand(obj.element, obj.comp)            
        else:
            return defs.Glove(obj.element, obj.comp)
            
    def dump(self, weapon, stream=None):
        self.type = weapon.type
        self.element = weapon.element
        self.comp = weapon.comp
        return yaml.dump(self, stream, explicit_start=True)

def load_squad(filename):
    contents = []
    for x in yaml.load_all(open(filename, 'r')): contents.append(x)
    squad = contents.pop(0)
    squad.lst = contents
    return squad.to_defs()
