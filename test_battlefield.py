from battlefield import *
from helpers import *
import pydb
btl = Battlefield(Grid(), rand_squad(), rand_squad())
btl.rand_place_squad(btl.squad1) 
btl.rand_place_squad(btl.squad2)

hit   = Scient(E, max_comp(E))
sho   = Scient(F, max_comp(F))
wiz   = Scient(I, max_comp(I))
urg   = Scient(W, max_comp(W))

hit.name = 'Puligist'
sho.name = 'Shooter'
wiz.name = 'Blaster'
urg.name = 'Theurgist'