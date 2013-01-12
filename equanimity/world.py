from ZEO import ClientStorage
#from ZODB.FileStorage import FileStorage
from ZODB import DB
import transaction
import persistent
#ZODB needs to log stuff
import logging
logging.basicConfig()

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.grid import Grid
from binary_tactics.units import Squad
from binary_tactics.hex_battle import Game
from binary_tactics.helpers import *

class Stronghold(persistent.Persistent):
    def __init__(self, defenders): #placeholder containers, need something smarter.
        self.stones  = persistent.list.PersistentList()
        self.weapons = persistent.list.PersistentList()
        self.units   = persistent.list.PersistentList()
        self.squads  = persistent.list.PersistentList()
        #needs a value limit based on the value of the grid that contains it.
        self.defenders = defenders
        self.defender_locs = persistent.list.PersistentList()
    
    def _set_defenders(self, squad_num):
        """If defenders is empty set squad as defenders."""
        # I don't remember how transactions work so I broke this function in
        # two, which might actually make it worse...
        
        # TODO: there should be a check to make sure the squad is not
        # stronger than the grid.
        # (Which is why self.defenders != self.squad[0])
        
        self.defenders = self.squad[squad_num]
        del self.squad[squad_num]
        self._p_changed = 1
        return transaction.commit()
    
    def _unset_defenders(self):
        """Moves old defenders into stronghold"""
        #use wisely.
        self.squads.append(self.defenders)
        self.defenders = None;
        self._p_changed = 1
        return transaction.commit()
    
    def move_squad_to_defenders(self, squad_num):
        """Moves a squad from self.squads to self.defenders"""
        try:
            self._unset_defenders()
            self._set_defenders(squad_num)
            return
        except:
            raise("There was an error moving squad to defenders.")

class wField(persistent.Persistent):
    def __init__(self, world_coord, owner, ply_time=240):
        self.world_coord = world_coord
        self.owner = owner
        self.grid = Grid()
        self.stronghold  = Stronghold(self.create_defenders())
        self.battlequeue = persistent.list.PersistentList()
        self.producers   = None #stuctures, input stones, output composites.
        self.value       = None
        self.expected_yield = None
        
        """
        ply_time: user definable time before a pass is automatically sent for a battle action.
            range between 4 and 360 minutes, default is 4 (in seconds)
        """
        self.ply_time = ply_time
    
    def create_defenders(self):
        """creates the stronghold defenders of a field with random scients.
        (should be nescients)"""
        #this function should calcuate the composition of the units based on the
        #composition of the grid, that will be handled in due time.
        return Squad(kind='mins', element=rand_element())
    
    def get_defenders(self):
        """gets the defenders of a wField."""
        try:
            return self.stronghold.defenders
        except:
            raise Exception("Stronghold has no defenders.")

class wPlayer(persistent.Persistent):
    """Object that contains player infomration."""
    def __init__(self, username=None, password=None):
        persistent.Persistent.__init__(self)
        self.username = username
        self.password = password
        self.wFields  = persistent.mapping.PersistentMapping()
        self.cookie   = None
        self.roads    = None
        self.treaties = None

class World(object): #this object needs to be refactored.
    def __init__(self, storage_name=('localhost', 9100)):
        self.storage = ClientStorage.ClientStorage(storage_name)
        self.db = DB(self.storage)
        self.connection = self.open_connection(self.db)
        self.root = self.get_root(self.connection)
    
    def open_connection(self, db):
        return db.open()
    
    def get_root(self, connection):
        return connection.root()
    
    def add_player(self, player):
        if not(player.username in self.root.keys()):
            self.root['Players'][player.username] = player
            self.root._p_changed = 1
            return transaction.commit()
        else:
            raise Exception("A player with that name is already registered, \
                             use another name.")
    
    def award_field(self, old_owner, wField_coords, new_owner):
        """Transfers a field from one owner to another."""
        #this should be atomic.
        self.root['Players'][new_owner].wFields[str(wField_coords)] = \
        self.root['Players'][old_owner].wFields[str(wField_coords)]
        del self.root['Players'][old_owner].wFields[str(wField_coords)]
        self.root['Players'][new_owner].wFields[str(wField_coords)].owner =\
        new_owner
        return transaction.commit()

    
    
    
    def move_squad(self, src, squad_num, dest):
        """Moves a squad from a stronghold to a queue."""
        #src and dest are both wFields
        #TODO: check for adjacency.
        squad = src.stronghold.squads[squad_num]
        try:
            dest.battlequeue.append((src.owner, squad))
            del src.stronghold.squads[squad_num]
            return transaction.commit()
        except:
            print "the move didn't work."
    
    def delete_player(self, player):
        """removes a player from the database and returns their fields to
        the world."""
        for field in self.root['Players'][player].wFields.keys():
            self.award_field(player, field, 'World')
        del self.root['Players'][player]
        return transaction.commit()
    
    def start_battle(self, field_loc):
        """Starts a battle on a wField. FOR TESTING"""
        pass
