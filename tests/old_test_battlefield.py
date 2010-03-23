from binary_tactics.battlefield import *
from binary_tactics.helpers import *
import pydb
btl = Battlefield(Grid(), rand_squad(), rand_squad())
#btl.rand_place_squad(btl.squad1) 
#btl.rand_place_squad(btl.squad2)
sq    = Squad(Scient(E, max_comp(E)))
sq.append(Scient(F, max_comp(F)))
sq.append(Scient(I, max_comp(I)))
sq.append(Scient(W, max_comp(W)))
sq.append(Scient(W, {W:255, F:0, I:0, E:0}))

sq[0].name = 'Puligist'
sq[1].name = 'Shooter'
sq[2].name = 'Blaster'
sq[3].name = 'Theurgist'
sq[4].name  = 'ur'

btl.place_unit(sq[0], (0,0))
btl.place_unit(sq[4], (1,0))
btl.place_unit(sq[3], (0,1))
btl.place_unit(sq[2], (0,2))

btl.attack(sq[2], (0,0))
btl.attack(sq[4], (0,0))
btl.attack(sq[3], (1,0))
#btl.attack(wiz, (0,0))
