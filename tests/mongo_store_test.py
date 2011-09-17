"""
mongo_store_test.py

Created by AFD on 2010-10-14.
Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
"""

from stores.mongo_store import *
from stores.store import *
from pymongo.connection import Connection
from pymongo.database import Database

from binary_tactics.player  import Player
from binary_tactics.helpers import *
from binary_tactics.weapons import *
from binary_tactics.units   import *
from binary_tactics.stone   import *

connection = Connection(host='bt.hipeland.org')
db = Database(connection, 'binary_tactics')
db.authenticate('rix', 'fhpxguvf'.decode('rot13'))

exists = {'$exists': True}
#squads = db.binary_tactics.find({'squad': exists})
#grids  = db.binary_tactics.find({'grid': exists})

#squad   = [convert_dict(get_dict(db.binary_tactics.find({'squad.value': 1004})[0], db.binary_tactics, db))]
squad   = [rand_squad()]
units   = [n for n in squad[0]]
weapons = [n.weapon for n in squad[0]]
stones  = [rand_comp() for n in xrange(6)]
w = Player('The World', squad, stones, units, weapons, [])

