#
#  battle_test.py
#  
#
#  Created by RiX on 3/22/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#

from binary_tactics.hex_battle import *
from stores.yaml_store import *
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.player import Player

def hp():
    for s in btl.squads:
        print s.name
        for u in s:
            print "     %s\n    %s" %(u.name, u.hp)
        print ""

p1   = Player(name='p1', squads=[load('yaml/ice_maxes.yaml')])
p2   = Player(name='p2', squads=[load('yaml/fire_maxes.yaml')])

game = Game(defender=p1, attacker=p2,
            battlefield=Battlefield(defsquad=p1.squads[0], atksquad=p2.squads[0]),)

btl = game.battlefield

for s in range(2):
    for x in range(4):
        btl.place_object(btl.squads[s][x], defs.Loc(x, s))

game.log['init_locs'] = game.log.init_locs()

def show_squad(squad):
    for u in squad:
        print u.name, u.location, u.hp

def show_squads():
    for s in btl.squads:
        print "%s:" %s.name
        show_squad(s)
        print ""


print game.process_action(Action(btl.defsquad[0], 'move'  , (2,2)))
print game.process_action(Action(btl.defsquad[0], 'attack', (2,1)))

print game.process_action(Action(btl.atksquad[2], 'attack', (2,2)))
print game.process_action(Action(btl.atksquad[2], 'move'  , (2,5)))

print game.process_action(Action(btl.defsquad[3], 'move'  , (2,1)))
print game.process_action(Action(btl.defsquad[3], 'attack', (2,0)))

print game.process_action(Action(btl.atksquad[2], 'move'  , (2,3)))
print game.process_action(Action(btl.atksquad[2], 'attack', (2,2)))

print game.process_action(Action(btl.defsquad[0], 'attack', (2,3)))
print game.process_action(Action(btl.defsquad[0], 'pass', None))

print game.process_action(Action(btl.atksquad[2], 'move'  , (3,2)))
print game.process_action(Action(btl.atksquad[2], 'attack', (2,1)))

print game.process_action(Action(btl.defsquad[0], 'attack', (3,2)))
print game.process_action(Action(btl.defsquad[0], 'move'  , (6,2)))

print game.process_action(Action(btl.atksquad[1], 'move'  , (1,5)))
print game.process_action(Action(btl.atksquad[1], 'attack', (6,2)))

print game.process_action(Action(btl.defsquad[3], 'move'  , (2,5)))
print game.process_action(Action(btl.defsquad[3], 'attack', (1,5)))

print game.process_action(Action(btl.atksquad[1], 'move'  , (5,5)))
print game.process_action(Action(btl.atksquad[1], 'attack', (2,0)))

print game.process_action(Action(btl.defsquad[3], 'move'  , (6,4)))
print game.process_action(Action(btl.defsquad[3], 'attack', (5,5)))

print game.process_action(Action(btl.atksquad[1], 'move'  , (5,9)))
print game.process_action(Action(btl.atksquad[1], 'attack', (6,4)))

print game.process_action(Action(btl.defsquad[3], 'move'  , (6,9)))
print game.process_action(Action(btl.defsquad[3], 'attack', (5,9)))

print game.process_action(Action(btl.atksquad[0], 'move'  , (0,5)))
print game.process_action(Action(btl.atksquad[0], 'attack', (6,9)))

print game.process_action(Action(btl.defsquad[3], 'move'  , (6,5)))
print game.process_action(Action(None, 'pass', None))

print game.process_action(Action(btl.atksquad[0], 'move'  , (4,5)))
print game.process_action(Action(btl.atksquad[0], 'attack', (6,5)))

print game.process_action(Action(btl.defsquad[3], 'move'  , (5,4)))
print game.process_action(Action(btl.defsquad[3], 'attack', (4,5)))

print game.process_action(Action(btl.atksquad[0], 'move'  , (5,5)))
print game.process_action(Action(btl.atksquad[0], 'attack', (5,4)))

print game.process_action(Action(btl.defsquad[3], 'attack', (5,5)))
print game.process_action(Action(None, 'pass', None))

print game.process_action(Action(btl.atksquad[0], 'attack', (5,4)))
print game.process_action(Action(None, 'pass', None))

print game.process_action(Action(btl.defsquad[3], 'move'  , (3,2)))
print game.process_action(Action(btl.defsquad[3], 'attack', (3,1)))

print game.process_action(Action(btl.atksquad[0], 'move'  , (3,3)))
print game.process_action(Action(btl.atksquad[0], 'attack', (3,2)))

print game.process_action(Action(btl.defsquad[3], 'attack', (3,1)))
print game.process_action(Action(btl.defsquad[3], 'move'  , (7,2)))

print game.process_action(Action(btl.atksquad[0], 'move'  , (7,3)))
print game.process_action(Action(btl.atksquad[0], 'attack', (7,2)))

print game.process_action(Action(btl.defsquad[3], 'attack'  , (7,3)))
print game.process_action(Action(None, 'pass', None))

print game.process_action(Action(btl.atksquad[3], 'move'  , (2,1)))
print game.process_action(Action(btl.atksquad[3], 'attack', (2,0)))

print game.process_action(Action(btl.defsquad[2], 'attack', (2,1)))
#print game.process_action(Action(None, 'pass', None))
