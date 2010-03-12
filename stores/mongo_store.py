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
from stores.store import convert_dict, persisted


def findtinsert(dict, collection):
    """Tries to insert a dictionary, if duplicate return id of original"""
    try:
        return collection.find_one(dict)['_id']
    except TypeError:
        return collection.insert(dict, safe=True)

def insert_co(obj, collection):
    """inserts a composite object into collection"""
    #This function is conspicuously similar to get_persisted, could be fixed witawapper[sic]
    kind = obj.__class__.__name__.lower()
    if contains(persisted.keys(), kind):
        new_dict = {}
        #check values of obj.__dict__ for persisted objects
        for key in persisted[kind]:
            other_kind = obj.__dict__[key].__class__.__name__.lower()
            #catch grid case
            if key == 'tiles':
                new_dict['tiles'] = {}
                for (k, v) in obj.__dict__[key].items():
                    new_x = {}
                    for (l, w) in v.items():
                        new_x.update({str(l): insert_co(w, collection)})
                    new_dict['tiles'].update({str(k): new_x})
            
            #special case for the .data of Squad:
            elif other_kind == 'list':
                data = []
                for item in obj.__dict__[key]:
                    uc = item.__class__.__name__.lower()
                    data.append({uc: insert_co(item, collection)})
                new_dict[key] = data
            elif other_kind == 'dict':
                '''regardless of the key, these are all going to be comps,
                save them as such.'''
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

def get_dict(id, collection):
    d = collection.find_one(id)
    del d['_id']
    for (key, value) in d.items():
        if key == 'grid':
            for (k, v) in value['tiles'].items():
                for (l, w) in v.items():
                    v[l] = get_dict(w, collection)
                
        if key == 'comp':
            return value
        if isinstance(value, dict):
            for (k, v) in value.items():
                if isinstance(v, ObjectId):
                    value[k] = get_dict(v, collection)
        if key == 'squad':
            data = value['data']
            td = []
            for unit in data:
                kind, id = unit.items()[0]
                td.append(get_dict(id, collection))
            value['data'] = td
    return d
    
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