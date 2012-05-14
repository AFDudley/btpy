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
    def __init__(self): #placeholder containers, need something smarter.
        self.stones  = persistent.list.PersistentList()
        self.weapons = persistent.list.PersistentList()
        self.units   = persistent.list.PersistentList()
        self.squads  = persistent.mapping.PersistentMapping()
        #needs a value limit based on the value of the grid that contains it.
        self.defenders = Squad(name='local defenders')
        self.defender_locs = persistent.list.PersistentList()


class wField(persistent.Persistent):
    def __init__(self, world_coord, owner, ply_window=4):
        self.world_coord = world_coord
        self.owner = owner
        self.grid = Grid()
        self.stronghold  = Stronghold()
        self.battlequeue = persistent.list.PersistentList()
        self.producers   = None #stuctures, input stones, output composites.
        self.value       = None
        self.expected_yield = None
        
        """
        ply_window: user definable time before a pass is automatically sent for a battle action.
            range between 4 and 360 minutes, default is 4
        """
        self.ply_window = ply_window
    
    def get_defenders(self):
        """gets the defenders of a wField, returns a random squad from stronghold
           if no defenders set."""
        if self.stronghold.defenders.value > 0:
            return self.stronghold.defenders
        else: #not really random.
            try:
                return self.stronghold.squads.values()[0]
            except:
                raise Exception("no squads available to defend Field.")

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

class World(object):
    def __init__(self, storage_name=('localhost', 9100),x=8, y=8, resigntime=360):
        self.storage = ClientStorage.ClientStorage(storage_name)
        self.resigntime = 360 #amount of time in minutes before attacker is forced to resign.
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
    
    def populate_defenders(self, wField):
        """populates the stronghold defenders of a field with random scients.
        (should be nescients)"""
        #this function should calcuate the composition of the units based on the
        #composition of the field, that will be handled in due time.
        #should verify that defenders is empty.
        squad = wField.stronghold.defenders
        while squad.free_spaces > 4:
            squad.append(rand_unit())
        wField.stronghold._p_changed = 1 #overloading squad fixes this.
        return transaction.commit()
    
    def populate_squads(self, wField, squad=None):
        """puts a squad into a stronghold. FOR TESTING"""
        if squad==None: squad = rand_squad()
        wField.stronghold.squads[squad.name] = squad
        wField.stronghold._p_changed = 1
        return transaction.commit()
    
    def move_squad(self, src, squad_name, dest):
        """Moves a squad from a stronghold to a queue."""
        #src and dest are both wFields
        #TODO: check for adjacency.
        squad = src.stronghold.squads[squad_name]
        try:
            dest.battlequeue.append((src.owner, squad))
            del src.stronghold.squads[squad_name]
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
