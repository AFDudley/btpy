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
from binary_tactics.grid import Loc
from stores.store import convert_dict

def loc_representer(dumper, data):
    return dumper.represent_scalar(u'!loc', u'(%2s,%2s)' % data)
 
yaml.add_representer(Loc, loc_representer)

def loc_constructor(loader, node):
    value = loader.construct_scalar(node)
    try:
        x, y = map(int, value.strip('()').split(','))
    except ValueError: #This isn't so bad.
        x = y = None    
    return Loc(x,y)

yaml.add_constructor(u'!loc', loc_constructor)    

loc_pat = re.compile(r'^\(\s*\d+\s*,\s*\d+\s*\)\s*$')
none_pat = re.compile(r'^\(\s*None\s*,\s*None\s*\)\s*$')
yaml.add_implicit_resolver(u'!loc', loc_pat)
yaml.add_implicit_resolver(u'!loc', none_pat)
    
def load(filename):
    return convert_dict(yaml.load(open(filename, 'r')))
