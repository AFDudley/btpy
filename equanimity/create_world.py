"""creates the World object and populates it with fields. VERY DESTRUCTIVE."""
from equanimity.world import wPlayer, World
#from stores.yaml_store import load
from binary_tactics.const import *

w = World()
wr = w.root
w.open_connection()
w.create()

#player stuff
w.add_player(wPlayer('dfndr', 'dfndr'))
w.add_player(wPlayer('atkr', 'atkr'))

w.award_field('World', '(0, 0)', 'dfndr')
w.award_field('World', '(0, 1)', 'atkr')

#Fields are automatically populated with Ice mins.
#below we create attacking Fire mins.
#get fields
af = wr['Players']['atkr'].wFields['(0, 1)']
df = wr['Players']['dfndr'].wFields['(0, 0)']
#get stronghold.
afs = af.stronghold

#put Fire min stones into stronghold.
afs._add_stones([Stone((2,4,0,2)) for n in xrange(4)])

#create scients.
for n in xrange(4): afs._form_scient('Fire', -1)

#put empty stones into stronhold.
afs._add_stones([Stone() for n in xrange(4)])

#create weapons.
for n in WEP_LIST: afs._form_weapon('Fire', -1, n)

#equip scients.
for n in xrange(4): afs.equip_scient(-1, -1)

#form squad
afs.form_squad([-1,-1,-1,-1], 'Fire Attackers')

#move squad to battlequeue
w.move_squad(af, -1, df)