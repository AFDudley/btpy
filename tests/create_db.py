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
    
def create_world(version=0.0, x=2, y=2):
    def do_it():
        world['version'] = version
        world['x'] = x
        world['y'] = y
        #Fields should be a frozendict
        #http://stackoverflow.com/questions/2703599/what-would-be-a-frozen-dict
        world['Fields']  = {}
        world['Players'] = persistent.mapping.PersistentMapping()
        player = wPlayer('World', None)
        world['Players']['World'] = player
        make_wFields(world['x'], world['y'])
        transaction.commit()
    try: #If the world version is the same, do nothing.
       if world['version'] == version:
           print "The ZODB already contains a world of that version."
       else: do_it()
    except: do_it()
    return world

if __name__ == '__main__':
    print create_world(0.0, 2,2)
    
