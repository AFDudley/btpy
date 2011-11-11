from ZEO import ClientStorage
from ZODB import DB
import transaction

addr = 'localhost', 9100
storage = ClientStorage.ClientStorage(addr)
db = DB(storage)
conn = db.open()
root = conn.root()
