#
#  store.py
#  
#
#  Created by RiX on 3/11/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""Functions shared between yaml_ and mongo_ store.py"""
from binary_tactics.defs import Loc
from binary_tactics.units import Scient, Squad
from binary_tactics.battlefield import Grid, Tile
from binary_tactics.player import Player
from binary_tactics.weapons import *

c  = ('comp',)
ec = c + ('element',)
persisted = {'stone': c, 'sword': ec, 'bow': ec, 'wand': ec, 'glove': ec,
             'scient': ec + ('name','weapon','weapon_bonus','location'),
             'nescient': ec + ('name', 'location'),
             'squad': ('data', 'name', 'value', 'free_spaces'),
             'tile': c + ('contents',),
             'grid': c + ('tiles','x','y'),
             'player': ('fields', 'name', 'squads', 'stones', 'units', 'weapons'),
             }
not_persisted_now = {'log': ('applied', 'start_time', 'winner', 'messages', 'actions',
                             'states', 'players', 'grid', 'end_time', 'condition',
                             'units', 'init_locs',),
                     'action': ('when', 'type', 'target', 'unit'),
                     'message': ('text', 'num', 'when'),
                     'state': ('pass_count', 'num', 'hp_count', 'queued',
                               'old_squad2_hp', 'game_over'),
}
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

    elif key == 'player':

        squads = []
        for squad in value['squads']:
            squads.append(convert_dict(squad))
        return Player(value['name'], squads)

    else:
        #for weapons
        return eval(key.capitalize())(**eval(''.join(str(value).replace("u'", "'"))))
    