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
from binary_tactics.grid import Grid
from binary_tactics.units import Squad, Scient
from binary_tactics.weapons import Sword, Bow, Wand, Glove
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
    
    def _add_stones(self, stones):
        """Extends self.stones with list of stones FOR TESTING."""
        #this should only be done by the harvest process.
        self.stones.extend(stones)
        self._p_changed = 1
        return transaction.commit()
    
    def _form_weapon(self, element, stone_num, weap_type):
        """Takes a stone from stronghold and turns it into a Weapon."""
        #for testing!!!!!
        #!!!!!!!!WEAP_TYPE NEEDS TO BE CHECKED BEFORE PASSED TO EVAL!!!!!!!!!!!
        #(or I could just fix Weapon, duh)
        weapon = eval(weap_type)(element, self.stones.pop(stone_num))
        self.weapons.append(weapon)
        self._p_changed = 1
        return transaction.commit()
        
    def _form_scient(self, element, stone_num, name=None):
        """Takes a stone from stronghold and turns it into a Scient."""
        #this should only be done by the production process.
        if name == None: name = rand_string()
        self.units.append(Scient(element, self.stones.pop(stone_num), name))
        self._p_changed = 1
        return transaction.commit()
    
    def equip_scient(self, unit_num, weapon_num):
        """Moves a weapon from the weapon list to a scient."""
        scient = self.units[unit_num]
        #WARNING! This is destructive.
        scient.equip(self.weapons.pop(weapon_num))
        scient._p_changed = 1
        self._p_changed = 1
        return transaction.commit()
    
    def unequip_scient(self, unit_num):
        """Moves a weapon from a scient to the stronghold."""
        scient = self.units[unit_num]
        self.weapons.append(scient.unequip())
        scient._p_changed = 1
        self._p_changed = 1
        return transaction.commit()
    
    def form_squad(self, unit_num_list=None, name=None):
        """Forms a squad and places it in the stronghold."""
        sq = Squad(name=name)
        for n in unit_num_list:
            sq.append(self.units.pop(n))
        self.squads.append(sq)
        self._p_changed = 1
        return transaction.commit()
         
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
    def __init__(self, world_coord, ply_time=240):
        self.world_coord = world_coord
        self.owner = 'World'
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
    def __init__(self, username, password=None):
        persistent.Persistent.__init__(self)
        self.username = username
        #this is not secure, need to figure that out sometime
        if password != None:
            self.password = hashlib.md5(password).hexdigest()
        else:
            self.password = None
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
                print "The ZODB already contains a world of that version."
            else:
                pass
        except: 
            pass
        self.root['resigntime'] = 21600#amount of time in seconds before attacker is forced to resign.
        self.root['version'] = version
        self.root['x'] = x
        self.root['y'] = y
        self.root['DOB'] = datetime.utcnow()
        #Fields should be a frozendict
        #http://stackoverflow.com/questions/2703599/what-would-be-a-frozen-dict
        self.root['Fields']  = {}
        self.root['Players'] = persistent.mapping.PersistentMapping()
        self.player = wPlayer('World', None)
        self.root['Players']['World'] = self.player
        self.make_wFields(self.root['x'], self.root['y'])
        transaction.commit()

        return self.root
    
    def make_wFields(self, range_x, range_y):
        """creates all wFields used in a game."""
        #right now the World and the wFields are square, they should both be hexagons.
        wf0 = self.root['Players']['World'].wFields
        wf1 = self.root['Fields']
        for coord_x in xrange(range_x):
            for coord_y in xrange(range_y):
                world_coord = (coord_x, coord_y)
                wf1[str(world_coord)] = wf0[str(world_coord)] =\
                wField(world_coord)
        transaction.commit() #required for wf1
    
    def award_field(self, old_owner, wField_coords, new_owner):
        """Transfers a field from one owner to another."""
        #is this atomic?
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
        
"""This doesn't work because of pickle's scope requirements.
if __name__ == '__main__':
    world = World()
    wr = world.root
    world.open_connection()
"""

