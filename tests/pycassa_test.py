from binary_tactics.player import Player
from binary_tactics.units import Squad
from stores.store import get_persisted #which is actually buggy in this case.
import pycassa

pool = pycassa.connect('bt')
cf = pycassa.ColumnFamily(pool, 'PLAYERS')
p =  Player({}, 'player 1', get_persisted(Squad()), {}, {}, {})
foo = {'1': p}
cf.insert(foo.keys()[0], foo['1'])


===


from stores.store import *
from binary_tactics.player  import Player
from binary_tactics.helpers import *
from binary_tactics.weapons import *
from binary_tactics.units   import *
from binary_tactics.stone   import *
