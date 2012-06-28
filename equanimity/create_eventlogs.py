"""creates the battle log object. VERY DESTRUCTIVE."""
from ZEO import ClientStorage
from ZODB import DB
import transaction
import persistent.mapping
#from equanimity.world import wField, wPlayer, World

addr = 'localhost', 9101
storage = ClientStorage.ClientStorage(addr)
db = DB(storage)
conn = db.open()
logs = conn.root()

#TODO: index logs by when and where the battle happened.
def create():
    logs['battle'] = persistent.mapping.PersistentMapping()
    transaction.commit()