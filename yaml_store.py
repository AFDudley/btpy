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
from operator import contains
from helpers import rand_unit, rand_squad, rand_comp

sq = rand_squad()

def loc_representer(dumper, data):
    return dumper.represent_scalar(u'!loc', u'(%2s,%2s)' % data)
 
yaml.add_representer(defs.Loc, loc_representer)

def loc_constructor(loader, node):
    value = loader.construct_scalar(node)
    try:
        x, y = map(int, value.strip('()').split(','))
    except ValueError: #This isn't so bad.
        x = y = None    
    return defs.Loc(x,y)

yaml.add_constructor(u'!loc', loc_constructor)    

loc_pat = re.compile(r'^\(\s*\d+\s*,\s*\d+\s*\)\s*$')
none_pat = re.compile(r'^\(\s*None\s*,\s*None\s*\)\s*$')
yaml.add_implicit_resolver(u'!loc', loc_pat)
yaml.add_implicit_resolver(u'!loc', none_pat)

def convert_dict(dict):
    """takes a dict and returns composite objects."""
    key, value = dict.items()[0]
    if key == 'squad':
        squad = defs.Squad(name=value['name'])
        data = value['data']
        for unit in data:
            squad.append(convert_dict(unit))
        return squad
    elif key == 'scient':
        scient = {}
        scient['comp'] = value['comp']
        scient['element'] = value['element']
        scient = defs.Scient(**scient)
        scient.weapon = convert_dict(value['weapon'])
        scient.location = defs.Loc(value['location'][0], value['location'][1])
        return scient
    return eval(u'defs.'+ key.capitalize())(**eval(''.join(str(value).replace("u'", "'"))))
