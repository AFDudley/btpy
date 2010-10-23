#
#  mongo_store.py
#  
#
#  Created by RiX on 2/21/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""Store and retrieve game objects to and from mongodb."""

#Logs are really quite different from game objects and should be stored in a 
#different db.

from ordereddict import OrderedDict
from stores.store import convert_dict, persisted
from pymongo.objectid import ObjectId

def odict(dictonary):
    #It's kinda funny how hard it is to get an ordered dict out of python 2.6
    return OrderedDict(sorted(dictonary.items(), key=lambda t: t[0]))

def findtinsert(dictonary, collection):
    """Tries to insert a dictionary, if duplicate return id of original"""
    try:
        return collection.find_one(dictonary)['_id']
    except TypeError:
        return collection.insert(dictonary, safe=True)
def cls_to_col(db, cls):
    """converts a class name to a collection name."""
    col_name = cls + 's'
    if not col_name in db.collection_names():
        try:
            db.create_collection(col_name)
        except:
            raise
    return eval('db.' + col_name)
    
def insert_co(obj, db):
    """inserts a composite object into collection"""
    def insert_list(lst):
        new_lst = []
        for item in lst:
            new_lst.append(insert_co(item, db))
        return new_lst
    
    cls = obj.__class__.__name__.lower()
    if cls in persisted.keys():
        new_dict = {}
        #check values of obj.__dict__ for persisted objects
        for key in persisted[cls]:
            value_cls = obj.__dict__[key].__class__.__name__.lower()
            if key =='comp':
                new_dict[key] = findtinsert({key: odict(obj.__dict__[key])}, cls_to_col(db, key))
            #catch grid case
            elif key == 'tiles':
                new_dict[key] = {}
                for (k, v) in obj.__dict__[key].items():
                    new_x = {}
                    for (l, w) in v.items():
                        new_x.update({str(l): insert_co(w, db)})
                    new_dict[key].update({str(k): new_x})
            #For Player objects (not a composite)
            elif key == 'squads':
                new_dict[key] = insert_list(obj.__dict__[key])
            elif key == 'weapons':
                new_dict[key] = insert_list(obj.__dict__[key])
            elif key == 'stones':
                new_dict[key] = insert_list(obj.__dict__[key])
            elif key == 'units':
                new_dict[key] = insert_list(obj.__dict__[key])
            elif key == 'fields':
                new_dict[key] = insert_list(obj.__dict__[key])
            #For list of players (not a composite)
            elif key == 'players':
                new_dict[key] = insert_list(obj.__dict__[key])
            #For Squads: (squads should have a composition)
            elif key == 'data':
                new_dict[key] = insert_list(obj.__dict__[key])
            elif value_cls == 'dict':
                '''regardless of the key, these are all going to be comps,
                save them as such.'''
                new_dict[key] = findtinsert({'comp': odict(obj.__dict__[key])},
                                            cls_to_col(db, 'comp'))
                
            #if value are persisted, call self
            elif value_cls in persisted.keys():
                new_dict[key] = insert_co(obj.__dict__[key], db)
            #else put value into new_dict
            else:
                new_dict[key] = obj.__dict__[key]
        return findtinsert({cls: new_dict}, cls_to_col(db, cls))
    else:
        return obj

def get_dict(id, collection, db):
    """convert a SON object into a dict."""
    d = collection.find_one(id)
    
    try: #WTFBBQ
        del d['_id']
    except:
        pass
        
    for (key, value) in d.items():
        if key == 'grid':
            for (k, v) in value['tiles'].items():
                for (l, w) in v.items():
                    v[l] = get_dict(w, cls_to_col(db, k), db)
        
        if key == 'comp':
            return value
            
        if isinstance(value, dict):
            for (k, v) in value.items():
                if isinstance(v, ObjectId):
                    value[k] = get_dict(v, cls_to_col(db, k), db)
        
        if key == 'squad':
            data = value['data']
            td = []
            for unit in data:
                td.append(get_dict(unit, collection, db))
            value['data'] = td
        
        if key == 'player':
            squads = value['squads']
            new = []
            for squad in squads:
                new.append(get_dict(squad, collection, db))
            value['squads'] = new
    return d