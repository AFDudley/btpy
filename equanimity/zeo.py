from ZEO import ClientStorage
from ZODB import DB
import transaction

#ZODB needs to log stuff
import logging
logging.basicConfig()

class Zeo(object):
    def open(self):
        self.conn = self.db.open()
        self.root = self.conn.root()
        
    def __init__(self, addr=('localhost', 9100)):
        self.addr = addr
        self.storage = ClientStorage.ClientStorage(self.addr)
        self.db = DB(self.storage)
        self.open()
    
    def close(self):
        return self.db.close()
        
    def get_username(self, username): #FIX
        self.conn.sync()
        return self.root['Players'][username].password
    
    def set_username(self, username, password): #FIX
        try:
            self.conn.sync()
            assert not self.root['Players'][username].password
        except Exception: #this exception looks dangerous
            self.root['Players'][username] = wPlayer(username, password)
            self.root._p_changed = 1
            return transaction.commit()
    
if __name__ == '__main__':
    from equanimity.world import *
    world = Zeo().root