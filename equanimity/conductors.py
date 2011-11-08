from ZEO import ClientStorage
from ZODB import DB
import transaction

from ampoule import child
from random import randrange
import time

class Conductor(child.AMPChild):
    """Base class for Conductor object"""
    def __init__(self, dbaddr='/tmp/zeosocket', AMPCommands=None, key=None):
        Process.__init__(self)
        self.dbaddr = dbaddr
        self.AMPCommands = AMPCommands
        self.key = key
        
        self.storage = None #just in case.
        self.db = None
        self.conn = None
        self.root = None
    
    def start(self):
        """opens DB connection."""
        self.storage = ClientStorage.ClientStorage(self.dbaddr)
        self.db = DB(self.storage)
        self.conn = self.db.open()
        self.root = self.conn.root()
    
    def end(self):
        """closes DB connection."""
        pass
    
    def get_object(self, kind, key):
        """returns an object from zodb."""
        #TODO defer
        return self.root[kind][key]
    

class WorldConductor(Conductor):
    """Conducts world."""
    def __init__(self, dbaddr, AMPCommands=None, key=None):
        Conductor.__init__(self, dbaddr, AMPCommands=None, key=None)
        self.player = self._attach_player_object()
        self.process_pool = None
    
    def _make_wFields(self):
        """creates all wFields used in a world instance."""
        #right now the World and the wFields are square, they should both be hexagons.
        #considering how often this function is called, maybe it should not be in every
        #WorldConductor.
        wf = {}
        for coord_x in xrange(self.x):
            for coord_y in xrange(self.y):
                world_coord = (coord_x, coord_y)
                wf[str(world_coord)] = wField(world_coord)
        return wf
    
    def _attach_player_object(self):
        """Attempts to attach the world object in zodb,
           creates new one otherwise."""
        try:
            #this needs deeper checking... or to be part of a thoughtout object model?
            return self.get_object('Players', 'World')
        except Exception as excpt:
            if 'World' in excpt.args:
                return self.add_player(wPlayer('World', self._make_wFields()))
    
    def add_player(self, player):
        """Adds a player to the world."""
        if not(player.username in self.root.keys()):
            self.root['Players'][player.username] = player
            #return transaction.commit()
            return #need a statement here.
        else:
            raise Exception("A player with that name is already registered, \
                             use another name.")
    
    def move_squad(self, src, squad_name, dest):
        """Moves a squad from a stronghold to a queue."""
        #src and dest are both wFields
        #TODO defer
        try:
            dest.battlequeue.append((squad_name.owner,
                                     src.stronghold.squads[squad_name]))
            return transaction.commit()
        except:
            print "the move didn't work."
    
    def send_battle(self, attacker, defender, field):
        """places a battle_request into the process pool."""
        pass
    

class BattleConductor(Conductor):
    """Conducts battles."""
    def __init__(self):
        Conductor.__init__(self)
        self.wField  = None
        self.Player1 = None
        self.Player2 = None
        self.game    = None
        self.results = None
    
    def register(self, player):
        """Allows player to send commands to BattleConductor."""
        pass
    
    @do_battle.responder
    def start_battle(self, attacker, defender, field, callback):
        """creates a hex_battle.Game"""
        #return self.results
        pass
    
    def process_action(self, action):
        """processes an action from a registered player."""
        #TODO defer
        pass
    
    
