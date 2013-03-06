#
#  store.py
#  
#
#  Created by RiX on 3/11/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""Functions shared between yaml_ and mongo_ store.py"""
from binary_tactics.units import Scient, Nescient, Part
from binary_tactics.unit_container import Squad
from binary_tactics.hex_battlefield import Grid, Tile, Loc
from binary_tactics.player import Player
from binary_tactics.weapons import *

c  = ('comp',)
ec = c + ('element',)
persisted = {'stone': c, 'sword': ec, 'bow': ec, 'wand': ec, 'glove': ec,
             'scient': ec + ('name','weapon','weapon_bonus','location', 'sex'),
             'nescient': ec + ('name', 'location', 'sex', 'body', 'facing'),
             'body': ('head', 'left', 'right', 'tail'),
             'part': ('location',),
             'squad': ('data', 'name', 'value', 'free_spaces'),
             'tile': c + ('contents',),
             'grid': c + ('tiles','x','y'),
             'player': ('name', 'squads'),
             'initial_state': ('start_time', 'init_locs', 'units', 'grid', 'owners', 'player_names',)
             }
             
persisted.update({'log': ('actions', 'applied', 'change_list', 'condition',
                          'end_time', 'event', 'grid', 'init_locs', 'messages',
                          'owners', 'players', 'start_time', 'states', 'units', 
                          'winner', 'world_coords'),
                     'action': ('when', 'type', 'target', 'unit'),
                     'message': ('text', 'num', 'when'),
                     'state': ('pass_count', 'num', 'hp_count', 'queued',
                               'old_squad2_hp', 'game_over'),
})

def get_persisted(obj):
    """Returns a dict of obj attributes that are persisted."""
    kind = obj.__class__.__name__.lower()
    #print "kind: %s" % kind
    if kind in persisted.keys():
        new_dict = {}
        #check values of obj.__dict__ for persisted objects
        for key in persisted[kind]:
            other_kind = obj.__dict__[key].__class__.__name__.lower()
            #print "other_kind: %s" % other_kind
            #catch grid case
            if key == 'tiles':
                new_dict['tiles'] = {}
                for (k, v) in obj.__dict__[key].items():
                    new_x = {}
                    for (l, w) in v.items():
                        new_x.update({l: get_persisted(w)})
                    new_dict['tiles'].update({k: new_x})
            #For Logs
            elif key == 'units':
                new_dict['units'] = {}
                for (n, s) in obj.__dict__[key].items():
                    new_dict['units'][n] = get_persisted(s)
            
            elif key == 'init_locs':
                new_dict['init_locs'] = {}
                for (n, s) in obj.__dict__[key].items():
                    new_dict['init_locs'][n] = get_persisted(s)
            
            elif key =='queued':
                que = obj.__dict__[key]
                if que != None:
                    new_dict['queued'] = que
                else:
                    new_dict['queued'] = {}
            
            elif key == 'body':
                new_dict['body'] = {}
                for (n, s) in obj.__dict__[key].items():
                    #print n, s
                    new_dict['body'][n] = get_persisted(s)
            
            elif key == 'squad_list':
                sl = []
                for s in obj.__dict__[key]:
                        sl.append(get_persisted(s))
                new_dict['squad_list'] = sl
            
            elif key == 'players':
                ps = []
                for p in obj.__dict__[key]:
                        ps.append(get_persisted(p))
                new_dict['players'] = ps
            
            #special case for the .data of Squad:
            elif key == 'data':
                data = []
                for item in obj.__dict__[key]:
                    data.append(get_persisted(item))
                new_dict[key] = data
            
            #if value are persisted, call self
            elif other_kind in persisted.keys():
                new_dict[key] = get_persisted(obj.__dict__[key])
            #else put value into new_dict
            else:
                new_dict[key] = obj.__dict__[key]
        return {kind: new_dict} 
    else:
        return obj
    
def convert_dict(dict):
    """takes a dict and returns composite objects."""
    key, value = dict.items()[0]
    if key == 'tile':
        #this obviously dramatically slows down the instanciation of a
        #previously instanciated grid, but when would this be done in real-time?
        if value['contents'] == None:
            return Tile(**eval("".join(str(value).replace("u'", "'"))))
        else:
            contents = convert_dict(value['contents'])
            del value['contents']
            tile = Tile(**eval("".join(str(value).replace("u'", "'"))))
            tile.contents = contents
            return tile
    elif key == 'grid':
        #It's dat eval hammer, boy!!! WOOO!!!
        comp = eval("".join(str(value['comp']).replace("u'", "'")))
        tiles = {}
        x = value['x']
        y = value['y']
        for i in xrange(x):
            new_x = {}
            for j in xrange(y):
                new_x.update({j: convert_dict(value['tiles'][str(i)][str(j)])})
            tiles.update({i: new_x})
        return Grid(comp, x, y, tiles)
        
    elif key == 'squad':
        squad = Squad(name=value['name'])
        data = value['data']
        for unit in data:
            squad.append(convert_dict(unit))
        return squad
    
    elif key == 'scient':
        scient = {}
        scient['element'] = value['element']
        scient['comp'] = value['comp']
        scient['name'] = value['name']
        scient = Scient(**scient)
        if not value['weapon'] == None:
            scient.weapon = convert_dict(value['weapon'])
        if not value['location'] == None:
            scient.location = Loc(value['location'][0], value['location'][1])
        return scient
    
    elif key == 'nescient':
        nescient = {}
        nescient['element'] = value['element']
        nescient['comp'] = value['comp']
        nescient['name'] = value['name']
        nescient['facing'] = value['facing']
        nescient['body'] = {}
        for part in value['body'].keys():
            nescient['body'][part] = Part(None, value['body'][part]['part']['location'])
        nescient = Nescient(**nescient)
        if not value['location'] == None:
            nescient.location = Loc(value['location'][0], value['location'][1])
        return nescient
    
    elif key == 'player':
        squads = []
        for squad in value['squads']:
            squads.append(convert_dict(squad))
        return Player(value['name'], squads)
    
    else:
        #for weapons
        return eval(key.capitalize())(**eval(''.join(str(value).replace("u'", "'"))))
