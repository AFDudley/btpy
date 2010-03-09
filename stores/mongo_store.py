#
#  mongo_store.py
#  
#
#  Created by RiX on 2/21/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""Store and retrieve game objects to and from mongodb."""
from operator import contains
from pymongo.connection import Connection
from pymongo.binary import Binary
from pymongo.objectid import ObjectId

from binary_tactics.const import *
from binary_tactics import defs

c  = ('comp',)
ec = c + ('element',)
persisted = {'stone': c, 'sword': ec, 'bow': ec, 'wand': ec, 'glove': ec,
             'scient': ec + ('name','weapon','weapon_bonus','location'),
             'squad': ('data', 'name', 'value', 'free_spaces'),}

def findtinsert(dict, collection):
    """Tries to insert a dictionary, if duplicate return id of original"""
    try:
        return collection.find_one(dict)['_id']
    except TypeError:
        return collection.insert(dict, safe=True)

def insert_co(obj, collection):
    """inserts a composite object into collection"""
    kind = obj.__class__.__name__.lower()
    if contains(persisted.keys(), kind):
        new_dict = {}
        #check values of obj.__dict__ for persisted objects
        for key in persisted[kind]:
            other_kind = obj.__dict__[key].__class__.__name__.lower()
            #special case for the .data of Squad:
            if other_kind == 'list':
                data = []
                for item in obj.__dict__[key]:
                    uc = item.__class__.__name__.lower()
                    data.append({uc: insert_co(item, collection)})
                new_dict[key] = data
            elif other_kind == 'dict':
                '''regardless of the key, these are all going to be comps,
                save them as such.'''
                #print "%s: %s" %(key, obj.__dict__[key])
                #new_dict[key] = insert_dict(obj.__dict__[key], collection)
                new_dict[key] = findtinsert({'comp': obj.__dict__[key]}, collection)
            #if value are persisted, call self
            elif contains(persisted.keys(), other_kind):
                new_dict[key] = insert_co(obj.__dict__[key], collection)
            #else put value into new_dict
            else:
                new_dict[key] = obj.__dict__[key]
        return findtinsert({kind: new_dict}, collection)
    else:
        return obj
'''
def extract_co(id, collection):
    """returns a composite object from db."""
    son = collection.find_one(id)
    # I don't need you.
    del son['_id']
    for (key, value) in son.items():
        """All the 'crazy' eval/.replace stuff is due to a bug in python 2.6,
        fixed in 2.7+, If/when this is ported to 2.7+ all of this should be
        rewritten..."""
        if contains(persisted.keys(), key):
            if key == 'squad':
                squad = defs.Squad(name=value['name'])
                data = value['data']
                for unit in data:
                    key, value = unit.items()[0]
                    squad.append(extract_co(value, collection))
                return squad
            for subkey in value.keys():
                if isinstance(value[subkey], ObjectId):
                    value[subkey] = extract_co(value[subkey], collection)
            if key == 'scient':
                scient = {}
                scient['comp'] = value['comp']
                scient['element'] = value['element']
                scient = defs.Scient(**scient)
                scient.weapon = value['weapon']
                scient.location = defs.Loc(value['location'][0], value['location'][1])
                return scient
                
        elif key == 'comp':
            return defs.Stone(eval(''.join(str(value).replace("u'", "'"))))
        #This should only catch weapons.
        return eval(u'defs.'+ key.capitalize())(**eval(''.join(str(value).replace("u'", "'"))))
'''

def get_dict(id, collection):
    d = collection.find_one(id)
    del d['_id']
    for (key, value) in son.items():
        if key =='comp':
            return value
        if isinstance(value, dict):
            for (k, v) in value.items():
                if isinstance(v, ObjectId):
                    print v
                    value[k] = get_dict(v, collection)
        if key == 'squad':
            data = value['data']
            td = []
            for unit in data:
                kind, id = unit.items()[0]
                td.append(get_dict(id, collection))
            value['data'] = td
    return d
            
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
        scient['element'] = value['element']
        scient['comp'] = value['comp']
        scient['name'] = value['name']
        scient = defs.Scient(**scient)
        scient.weapon = convert_dict(value['weapon'])
        scient.location = defs.Loc(value['location'][0], value['location'][1])
        return scient
    return eval(u'defs.'+ key.capitalize())(**eval(''.join(str(value).replace("u'", "'"))))
    
if __name__ == '__main__':
    from binary_tactics.helpers import rand_unit, rand_squad, rand_comp, t2c
    connection = Connection()
    db = connection.test
    db.test.drop_indexes()
    exists = {'$exists': True}
    '''
    db.test.create_index('Earth', unique=True)
    db.test.create_index('Fire', unique=True)
    db.test.create_index('Ice', unique=True)
    db.test.create_index('Wind', unique=True)
    '''