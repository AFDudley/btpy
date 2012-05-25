from ZEO import ClientStorage
from ZODB import DB
import transaction

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.hex_battle import Game
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.player import Player
from binary_tactics.grid import Loc
from stores.store import get_persisted
from copy import deepcopy

addr = 'localhost', 9100
storage = ClientStorage.ClientStorage(addr)
db = DB(storage)
conn = db.open()
root = conn.root()

#assuming world_editor.py has been run first
#this pulls the battle out of ZODB, maintains the atomicity of the battle.
f = deepcopy(root['Fields']['(0, 0)'])
atkr_name, squad1 = f.battlequeue[0]
squad2 = f.get_defenders()
atkr = Player(atkr_name, [squad1])
dfndr = Player(f.owner, [squad2])
game = Game(player1=atkr, player2=dfndr,
            battlefield=Battlefield(f.grid, squad1, squad2))
btl = game.battlefield

for s in btl.squads: #location wonkiness in hex_battlefield.
    for u in s:
        u.location = Loc(None, None)
for s in range(2):
    for x in range(4):
        btl.place_object(btl.squads[s][x], Loc(x, s))

game.log['init_locs'] = game.log.init_locs()
