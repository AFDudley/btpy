#
#  battle_test.py
#  
#
#  Created by RiX on 3/22/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#

from binary_tactics.battle import *
from stores.yaml_store import *

def hp():
    for s in btl.squads:
        print s.name
        for u in s:
            print "     %s\n    %s" %(u.name, u.hp)
        print ""
'''            
game = Game(player1=Player(name='p1',
                            squad_list=[load('yaml/ice_maxes.yaml')]),
             player2=Player(name='p2',
                            squad_list=[load('yaml/fire_mins.yaml')]))
'''
                            
game = Game(player1=Player(name='p1',
                            squad_list=[load('yaml/ice_maxes.yaml')]),
             player2=Player(name='p2',
                            squad_list=[load('yaml/fire_maxes.yaml')]))
                            

btl = game.battlefield

for s in range(2):
    for x in range(4):
        btl.place_unit(btl.squads[s][x], defs.Loc(x, s))
game.log['init_locs'] = game.log.init_locs()

def show_squad(squad):
    for u in squad:
        print u.name, u.location, u.hp
        
def show_squads():
    for s in btl.squads:
        print "%s:" %s.name
        show_squad(s)
        print ""
        
game.process_action(Action(btl.squad1[0], 'move'  , (2,2)))
game.process_action(Action(btl.squad1[0], 'attack', (2,1)))

game.process_action(Action(btl.squad2[2], 'attack', (2,2)))
game.process_action(Action(btl.squad2[2], 'move'  , (2,5)))

game.process_action(Action(btl.squad1[3], 'move'  , (2,1)))
game.process_action(Action(btl.squad1[3], 'attack', (2,0)))

game.process_action(Action(btl.squad2[2], 'move'  , (2,3)))
game.process_action(Action(btl.squad2[2], 'attack', (2,2)))

game.process_action(Action(btl.squad1[0], 'attack', (2,3)))
game.process_action(Action(None, 'pass', None))

game.process_action(Action(btl.squad2[2], 'move'  , (3,2)))
game.process_action(Action(btl.squad2[2], 'attack', (2,1)))

game.process_action(Action(btl.squad1[0], 'attack', (3,2)))
game.process_action(Action(btl.squad1[0], 'move'  , (6,2)))

game.process_action(Action(btl.squad2[1], 'move'  , (1,5)))
game.process_action(Action(btl.squad2[1], 'attack', (6,2)))

game.process_action(Action(btl.squad1[3], 'move'  , (2,5)))
game.process_action(Action(btl.squad1[3], 'attack', (1,5)))

game.process_action(Action(btl.squad2[1], 'move'  , (5,5)))
game.process_action(Action(btl.squad2[1], 'attack', (2,0)))

game.process_action(Action(btl.squad1[3], 'move'  , (6,5)))
game.process_action(Action(btl.squad1[3], 'attack', (5,5)))

game.process_action(Action(btl.squad2[1], 'move'  , (5,9)))
game.process_action(Action(btl.squad2[1], 'attack', (6,5)))

game.process_action(Action(btl.squad1[3], 'move'  , (6,9)))
game.process_action(Action(btl.squad1[3], 'attack', (5,9)))

game.process_action(Action(btl.squad2[0], 'move'  , (0,5)))
game.process_action(Action(btl.squad2[0], 'attack', (6,9)))

game.process_action(Action(btl.squad1[3], 'move'  , (6,5)))
game.process_action(Action(None, 'pass', None))

game.process_action(Action(btl.squad2[0], 'move'  , (4,5)))
game.process_action(Action(btl.squad2[0], 'attack', (6,5)))

game.process_action(Action(btl.squad1[3], 'move'  , (5,4)))
game.process_action(Action(btl.squad1[3], 'attack', (4,5)))

game.process_action(Action(btl.squad2[0], 'move'  , (5,5)))
game.process_action(Action(btl.squad2[0], 'attack', (5,4)))

game.process_action(Action(btl.squad1[3], 'attack', (5,5)))
game.process_action(Action(None, 'pass', None))

game.process_action(Action(btl.squad2[0], 'attack', (5,4)))
game.process_action(Action(None, 'pass', None))

game.process_action(Action(btl.squad1[3], 'move'  , (3,2)))
game.process_action(Action(btl.squad1[3], 'attack', (3,1)))

game.process_action(Action(btl.squad2[0], 'move'  , (3,3)))
game.process_action(Action(btl.squad2[0], 'attack', (3,2)))

game.process_action(Action(btl.squad1[3], 'attack', (3,1)))
game.process_action(Action(btl.squad1[3], 'move'  , (7,2)))

game.process_action(Action(btl.squad2[0], 'move'  , (7,3)))
game.process_action(Action(btl.squad2[0], 'attack', (7,2)))

game.process_action(Action(btl.squad1[3], 'attack'  , (7,3)))
game.process_action(Action(None, 'pass', None))

game.process_action(Action(btl.squad2[3], 'move'  , (2,1)))
game.process_action(Action(btl.squad2[3], 'attack', (2,0)))

game.process_action(Action(btl.squad1[2], 'attack', (2,1)))
#game.process_action(Action(None, 'pass', None))
