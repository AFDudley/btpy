from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction
#ZODB needs to log stuff
import logging
logging.basicConfig()

import binary_tactics.stone
from binary_tactics.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.grid import Grid
from binary_tactics.units import Squad
from binary_tactics.hex_battle import Game
from helpers import *

class Stronghold(object):
    def __init__(self):
        self.stones  = {}
        self.weapons = {}
        self.units   = {}
        self.squads  = {} #this needs some intelligence.
        #needs a value limit based on the value of the grid that contains it.
        self.defenders = Squad(name='local defenders')

class wField(object):
    def __init__(self, world_coord):
        self.grid = Grid()
        self.world_coord = world_coord
        self.stronghold  = Stronghold()
        self.battlequeue = []
        self.producers   = None #stuctures, input stones, output composites.
        self.value       = None
        self.expected_yield = None
        
    def get_defenders(self):
        """gets the defenders of a wField, returns a random squad from stronghold
           if no defenders set."""
        if self.stronghold.defenders.value() > 0:
            return self.stronghold.defenders
        else:
            return self.stronghold.squads.values()[0]
               
class wPlayer(object):
    """Object that contains player infomration."""
    def __init__(self, username=None, wFields=None):
        self.username = username
        self.wFields  = wFields
        self.roads    = None
        self.treaties = None
        

class World(object): #needs a better name. 
    def __init__(self, storage_name='ZODB/Data.fs', x=8, y=8):
        self.x = x
        self.y = y
        self.storage = FileStorage(storage_name)
        self.db = DB(self.storage)
        self.connection = self.open_connection(self.db)
        self.root = self.get_root(self.connection)
        self.player = self.attach_player_object()
        
    def open_connection(self, db):
        return db.open()
        
    def get_root(self, connection):
        return connection.root()
    
    def add_player(self, player):
        if not(player.username in self.root.keys()):
            self.root['Players'][player.username] = player
            return transaction.commit()
        else:
            raise Exception("A player with that name is already registered, \
                             use another name.")
    
    def make_wFields(self):
        """creates all wFields used in a game."""
        #right now the World and the wFields are square, they should both be hexagons.
        wf = {}
        for coord_x in xrange(self.x):
            for coord_y in xrange(self.y):
                world_coord = (coord_x, coord_y)
                wf[str(world_coord)] = wField(world_coord)
        return wf
    
    def attach_player_object(self):
        """Attempts to attach the world object in zodb, creates new one otherwise."""
        try:
            #this needs deeper checking... or to be part of a thoughtout object model?
            return self.root["Players"]["World"]
        except Exception as excpt:
            if 'World' in excpt.args:
                return self.add_player(wPlayer('World', self.make_wFields()))
        
    def move_squad(self, src, squad_name, dest):
        """Moves a squad from a stronghold to a queue."""
        #src and dest are both wGrids
        try:
            dest.battlequeue.append((squad_name.owner,
                                     src.stronghold.squads[squad_name]))
            return self.transaction.commit()
        except:
            print "the move didn't work."
            
        