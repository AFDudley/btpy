"""creates the World object and populates it with fields. VERY DESTRUCTIVE."""
from ZEO import ClientStorage
from ZODB import DB
import transaction
import persistent.mapping
from equanimity.world import wField, wPlayer, World

addr = 'localhost', 9100
storage = ClientStorage.ClientStorage(addr)
db = DB(storage)
conn = db.open()
world = conn.root()

def make_wFields(x, y):
    """creates all wFields used in a game."""
    #right now the World and the wFields are square, they should both be hexagons.
    wf0 = world['Players']['World'].wFields
    wf1 = world['Fields']
    for coord_x in xrange(x):
        for coord_y in xrange(y):
            world_coord = (coord_x, coord_y)
            wf1[str(world_coord)] = wf0[str(world_coord)] =\
            wField(world_coord, 'World')
    transaction.commit() #required for wf1
    
def create_world(version, x, y):
    version = 0.0
    try:
        assert world['version'] == version
    except:
        world['version'] = version
        world['x'] = x
        world['y'] = y
        #Fields should be a frozendict
        #http://stackoverflow.com/questions/2703599/what-would-be-a-frozen-dict
        world['Fields']  = {}
        world['Players'] = persistent.mapping.PersistentMapping()
        player = wPlayer('World', None)
        world['Players']['World'] = player
        make_wFields(8, 8)

        transaction.commit()

        