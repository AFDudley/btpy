import hashlib
from datetime import datetime
from ZEO import ClientStorage
from ZODB import DB
import transaction
import persistent
#ZODB needs to log stuff
import logging
logging.basicConfig()

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from equanimity.field import Field

class wPlayer(persistent.Persistent):
    """Object that contains player infomration."""
    def __init__(self, username, password=None):
        persistent.Persistent.__init__(self)
        self.username = username
        #this is not secure, need to figure that out sometime
        if password != None:
            self.password = hashlib.md5(password).hexdigest()
        else:
            self.password = None
        self.Fields  = persistent.mapping.PersistentMapping()
        self.cookie   = None
        self.roads    = None
        self.treaties = None

class World(object): #this object needs to be refactored.
    def __init__(self, storage_name=('localhost', 9100)):
        self.storage = ClientStorage.ClientStorage(storage_name)
        self.db = DB(self.storage)
        self.connection = self.open_connection(self.db)
        self.root = self.get_root(self.connection)
    
    def open_connection(self, db=None):
        if db == None:
            return self.db.open()
        else:    
            return db.open()
    
    def get_root(self, connection):
        return connection.root()
    
    def add_player(self, player):
        if not(player.username in self.root.keys()):
            self.root['Players'][player.username] = player
            self.root._p_changed = 1
            return transaction.commit()
        else:
            raise Exception("A player with that name is already registered, "
                             "use another name.")
    
    def create(self, version=0.0, x=2, y=2):
        #there should be a more elegant way of doing this.
        try: #If the world version is the same, do nothing.
            if self.root['version'] == version:
                return Exception("The ZODB already contains a world of that version.")
            else:
                pass
        except: 
            pass
        self.root['dayLength'] = 240 #length of game day in seconds.
        self.root['resigntime'] = 21600#amount of time in seconds before attacker is forced to resign.
        self.root['maxduration'] = 5040 #in gametime days (5040 is one generation, two weeks real-time)
        self.root['version'] = version
        self.root['x'] = x
        self.root['y'] = y
        self.root['DOB'] = datetime.utcnow()
        #Fields should be a frozendict
        #http://stackoverflow.com/questions/2703599/what-would-be-a-frozen-dict
        self.root['Fields']  = persistent.mapping.PersistentMapping()
        self.root['Players'] = persistent.mapping.PersistentMapping()
        self.player = wPlayer('World', None)
        self.root['Players']['World'] = self.player
        self.make_Fields(self.root['x'], self.root['y'])
        transaction.commit()
        return self.root
    
    def make_Fields(self, range_x, range_y):
        """creates all Fields used in a game."""
        #right now the World and the Fields are square, they should both be hexagons.
        wf0 = self.root['Players']['World'].Fields
        wf1 = self.root['Fields']
        for coord_x in xrange(range_x):
            for coord_y in xrange(range_y):
                world_coord = (coord_x, coord_y)
                f = Field(world_coord)
                wf0[str(world_coord)] = f
                wf1[str(world_coord)] = f
                transaction.commit() #required for wf1
    
    def award_field(self, old_owner, Field_coords, new_owner):
        """Transfers a field from one owner to another."""
        #is this atomic?
        self.root['Players'][new_owner].Fields[str(Field_coords)] = \
        self.root['Players'][old_owner].Fields[str(Field_coords)]
        del self.root['Players'][old_owner].Fields[str(Field_coords)]
        self.root['Players'][new_owner].Fields[str(Field_coords)].owner =\
        new_owner
        return transaction.commit()
    
    def move_squad(self, src, squad_num, dest):
        """Moves a squad from a stronghold to a queue."""
        #src and dest are both Fields
        #TODO: check for adjacency.
        squad = src.stronghold.squads[squad_num]
        dest.battlequeue.append((src.owner, squad))
        src.stronghold.remove_squad(squad_num)
        return transaction.commit()
    
    def delete_player(self, player):
        """removes a player from the database and returns their fields to
        the world."""
        for field in self.root['Players'][player].Fields.keys():
            self.award_field(player, field, 'World')
        del self.root['Players'][player]
        return transaction.commit()
    
    def start_battle(self, field_loc):
        """Starts a battle on a Field. FOR TESTING"""
        pass
