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


''' 
in case you were wondering what the for loop below does, it's something like this:   
def bow_representer(dumper, data):
    return dumper.represent_mapping(u'!bow', get_attribs(bow, data))

yaml.add_representer(defs.Bow, bow_representer)
      
def bow_constructor(loader, node):
    value = loader.construct_mapping(node, deep=True)
    return defs.Bow(value['element'], value['comp'])
    
yaml.add_constructor(u'!bow', bow_constructor)
'''
def make_constructor(kind, trick):
    str =''
    attribs = attrib_list[kind]
    for value in attribs:
        str += trick + "['" + value + "'], "
    return str

def get_attribs(kind, data):
    tmp = {}
    for attrib in attrib_list[kind]:
        tmp[attrib] = data.__dict__[attrib]
    return tmp
    
#meta what the hell did you just call me boy?
for kind in ('sword', 'bow', 'wand', 'glove', 'scient', 'squad'):
    def hack(kind=kind):
        ts = u'!' + kind
        tobj = eval('defs.'+ kind.capitalize())
        trick = 'loader.construct_mapping(node, deep=True)'
        yaml.add_representer(tobj, lambda dumper, data: dumper.represent_mapping(ts, get_attribs(kind, data)))
        yaml.add_constructor(ts, lambda loader, node: eval('defs.'+ kind.capitalize() +'(' + make_constructor(kind,trick) + ')'))        
    hack(kind)

ec = ('element','comp')
attrib_list = {'sword': ec, 'bow': ec, 'wand': ec, 'glove': ec,
               'scient': ec + ('name','weapon','weapon_bonus','location'),
               'squad': defs.Squad().__dict__.keys()}
#remake constructor to ignore free_spaces and value.
#this protection against loading impossible squads
#could be done any number of ways in any number of places.
#This will do until objects are correctly checked at init/deserialization
def squad_constructor(loader, node):
    kwargs = loader.construct_mapping(node, deep=True)
    #Don't fudge
    del kwargs['free_spaces']
    del kwargs['value']
    return defs.Squad(**kwargs)

yaml.add_constructor(u'!squad', squad_constructor)

def load(filename):
    return yaml.load(open(filename, 'r'))