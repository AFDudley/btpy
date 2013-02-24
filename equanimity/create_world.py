"""creates the World object and populates it with fields. VERY DESTRUCTIVE."""
#from stores.yaml_store import load
from binary_tactics.const import *
import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from equanimity.world import wPlayer, World

w = World()
wr = w.root
try:
    w.create()

    #player stuff
    w.add_player(wPlayer('dfndr', 'dfndr'))
    w.add_player(wPlayer('atkr', 'atkr'))

    w.award_field('World', '(0, 0)', 'dfndr')
    w.award_field('World', '(0, 1)', 'atkr')

    #Fields are automatically populated with Ice mins.
    #below we create attacking Fire mins.
    #get fields
    af = wr['Players']['atkr'].Fields['(0, 1)']
    df = wr['Players']['dfndr'].Fields['(0, 0)']
    #get stronghold.
    afs = af.stronghold

    #put Fire min stones into stronghold.
    afs.silo.imbue_list([Stone((2,4,0,2)) for n in xrange(4)])

    #create scients.
    for n in xrange(4): afs.form_scient('Fire', Stone((2,4,0,2)).comp)

    #put empty stones into stronhold.

    #create weapons.
    for n in WEP_LIST: afs.form_weapon('Fire', Stone().comp, n)

    #equip scients.
    for n in xrange(4): afs.equip_scient(afs.units.keys()[n], -1)

    #form squad
    afs.form_squad([afs.units.keys()[n] for n in xrange(4)] , 'Fire Attackers')

    #set squad locations
    df.stronghold.set_defender_locs([(6,4), (7,4), (8,4,), (9,4)])
    df.stronghold.apply_defender_locs()
    afs.apply_squad_locs(0, [(6,10), (7,10), (8,10), (9,10)])

    #move squad to battlequeue
    w.move_squad(af, -1, df)
except:
    raise
    #raise Exception("Pre-existing world not modified.")
