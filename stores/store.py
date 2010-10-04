#
#  store.py
#  
#
#  Created by RiX on 3/11/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""Functions shared between yaml_ and mongo_ store.py"""
import binary_tactics.defs as defs

from binary_tactics.battlefield import Grid, Tile

c  = ('comp',)
ec = c + ('element',)
persisted = {'stone': c, 'sword': ec, 'bow': ec, 'wand': ec, 'glove': ec,
             'scient': ec + ('name','weapon','weapon_bonus','location'),
             'nescient': ec + ('name', 'location'),
             'squad': ('data', 'name', 'value', 'free_spaces'),
             'tile': c + ('contents',),
             'grid': c + ('tiles','x','y'),
             'player': ('name', 'squad_list'),
             'log': ('applied', 'start_time', 'winner', 'messages', 'actions',
                     'states', 'players', 'grid', 'end_time', 'condition',
                     'units', 'init_locs',),
             'action': ('when', 'type', 'target', 'unit'),
             'message': ('text', 'num', 'when'),
             'state': ('pass_count', 'num', 'hp_count', 'queued', 'old_squad2_hp', 'game_over'),}
             
def get_persisted(obj):
    """Returns a dict of obj attributes that are persisted."""    
    kind = obj.__class__.__name__.lower()
    if kind in persisted.keys():
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
        return Tile(**eval("".join(str(value).replace("u'", "'"))))
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

    elif key == 'player':
        from binary_tactics.battle import Player
        squad_list = []
        for squad in value['squad_list']:
            squad_list.append(convert_dict(squad))
        return Player(value['name'], squad_list)

    else:
        #for weapons
        return eval(u'defs.'+ key.capitalize())(**eval(''.join(str(value).replace("u'", "'"))))
    