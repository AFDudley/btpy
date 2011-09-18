#from binary_tactics.player import Player
from binary_tactics.grid import Grid
from binary_tactics.units import Squad
from binary_tactics.hex_battle import Game
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
        

class World(wPlayer):
    def __init__(self, username, x=8, y=8):
        wPlayer.__init__(self, username=username, wFields={})
        self.x = x
        self.y = y
        
    def make_wFields(self):
        """creates a world player and wFields"""
        #right now the World and the wFields are square, they should both be hexagons.
        for coord_x in xrange(self.x):
            for coord_y in xrange(self.y):
                world_coord = (coord_x, coord_y)
                self.wFields[str(world_coord)] = wField(world_coord)
     
class Mover(object):
    def __init__(self, transaction):
        self.transaction = transaction
    
    def move_squad(self, src, squad_name, dest):
        """Moves a squad from a stronghold to a queue."""
        #src and dest are both wGrids
        try:
            dest.battlequeue.append((squad_name.owner,
                                     src.stronghold.squads[squad_name]))
            return self.transaction.commit()
        except:
            print "the move didn't work."
            
class Conductor(object):
    """Conducts a set of actions"""
    def __init__(self):
        self.wField = None

class BattleConductor(Conductor):
    """Conducts battles."""
    def __init__(self):
        Conductor.__init__(self)
        self.wField  = None
        self.Player1 = None
        self.Player2 = None
        self.game    = None
        
    def create_game(self, self.wField.grid, self.player1, self.player2,):
        """creates a hex_battle.Game"""
        self.game = Game(self.wField.grid, self.player1, self.player2)
        