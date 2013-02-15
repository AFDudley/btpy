import persistent
import transaction

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.units import Squad, Scient
from binary_tactics.weapons import Sword, Bow, Wand, Glove

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
