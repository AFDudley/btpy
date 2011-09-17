from binary_tactics.battlefield import Tile, Grid
from binary_tactics.player import Player

from stores.mongo_store import fintinsert, odict, get_dict
from pymongo.connection import Connection
from pymongo.database import Database
from pymongo.objectid import ObjectId
#database testing stuff:

def make_db(host='bt.hipeland.org', username='rix',
            password='fhpxguvf'.decode('rot13')):
    if not db:
        try:
            global db = Database(Connection(host), 'binary_tactics')
            db.authenticate(username, password)
            return db
        except:
            raise
    else:
        return db
exists = {'$exists': True}

class World(object):
    """Object that contains all the fields within a world.""" 
    #should map to mongodb
    def __init__(self):
        self.db = make_db()
        self.grids = self.db.binary_tactics.find({'grid': exists})
        self.players = self.db.binary_tactics.find({'player': exists})
        #logs should be in their own DB...
        self.logs = self.db.binary_tactics.find({'log': exists})
        
    def battles(self):
        """Returns list of active battles"""
        pass
        
    def get_field(self, x, y):
        """returns datafor field (x, y)"""
        pass
        
    def get_players(self):
        """returns a list of all players in database."""
        pass


