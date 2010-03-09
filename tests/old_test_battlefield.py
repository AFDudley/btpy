from battlefield import *
from helpers import *
import pydb
btl = Battlefield(Grid(), rand_squad(), rand_squad())
#btl.rand_place_squad(btl.squad1) 
#btl.rand_place_squad(btl.squad2)

pul   = Scient(E, max_comp(E))
sho   = Scient(F, max_comp(F))
wiz   = Scient(I, max_comp(I))
urg   = Scient(W, max_comp(W))
ur    = Scient(W, {W:255, F:0, I:0, E:0})

pul.name = 'Puligist'
sho.name = 'Shooter'
wiz.name = 'Blaster'
urg.name = 'Theurgist'
ur.name  = 'ur'

btl.place_unit(pul, (0,0))
btl.place_unit(ur, (1,0))
btl.place_unit(urg, (0,1))
btl.place_unit(wiz, (0,2))

btl.attack(urg, (0,0))
btl.attack(ur, (0,0))
btl.attack(urg, (1,0))
#btl.attack(wiz, (0,0))
