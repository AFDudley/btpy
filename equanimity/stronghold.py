import persistent
import transaction

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.units import Squad, Scient
from binary_tactics.weapons import Sword, Bow, Wand, Glove

from binary_tactics.helpers import *
from equanimity.factory import Factory

class Stronghold(persistent.Persistent):
    def create_factory(self, kind):
        self.factories.append(Factory(kind))
        return transaction.commit()
        
    def __init__(self, field_element): #placeholder containers, need something smarter.
        self.stones = persistent.list.PersistentList()
        self.weapons = persistent.list.PersistentList()
        self.units = persistent.mapping.PersistentMapping()
        self.squads = persistent.list.PersistentList()
        self.factories = persistent.list.PersistentList()
        self.capacity = 8 #squad points. scient == 1, nescient == 2
        #needs a value limit based on the value of the grid that contains it.
        self.defenders = Squad(kind='mins', element=field_element) #kind should be nescients.
        self.defender_locs = persistent.list.PersistentList()
        self.factories = persistent.list.PersistentList()
        self.create_factory(field_element)
        return transaction.commit()
        
    def _add_stones(self, stones):
        """Extends self.stones with list of stones FOR TESTING."""
        #this should only be done by the harvest process.
        self.stones.extend(stones)
        self._p_changed = 1
        return transaction.commit()

    def split_stone(self, stone, comp):
        """Splits comp from stone and places it in stones."""
        self.stones.append(stone.split(comp))
        stone._p_changed = 1
        self.stones._p_changed = 1
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
        scient = Scient(element, self.stones.pop(stone_num), name)
        self.units[scient.id] = scient
        self._p_changed = 1
        return transaction.commit()
        
    def equip_scient(self, unit_id, weapon_num):
        """Moves a weapon from the weapon list to a scient."""
        scient = self.units[unit_id]
        #WARNING! This is destructive.
        scient.equip(self.weapons.pop(weapon_num))
        scient._p_changed = 1
        self._p_changed = 1
        return transaction.commit()
    
    def unequip_scient(self, unit_id):
        """Moves a weapon from a scient to the stronghold."""
        scient = self.units[unit_id]
        self.weapons.append(scient.unequip())
        scient._p_changed = 1
        self._p_changed = 1
        return transaction.commit()
    
    def form_squad(self, unit_id_list=None, name=None):
        """Forms a squad and places it in the stronghold."""
        sq = Squad(name=name)
        try: 
            for unit_id in unit_id_list:
                unit = self.units[unit_id]
                if not unit.container:
                    sq.append(unit) #DOES NOT REMOVE UNIT FROM LIST.
                else:
                    raise Exception("%s is already in a container." %unit)
            self.squads.append(sq)
            self._p_changed = 1
            return transaction.commit()
        except:
            return transaction.abort()
            
    def remove_squad(self, squad_num):
        """Removes units from from self.units, effectively moving the squad out of the stronghold."""
        squad = self.squads[squad_num]
        for unit in squad:
            del self.units[unit.id]
        return transaction.commit()
    
    def apply_locs_to_squad(self, squad, list_of_locs):
        """takes a list of locations and appliees them to the units in a squad"""
        #TODO loc sanity check. on_grid is a start, but not completely correct.
        if len(squad) == len(list_of_locs):
            for n in xrange(len(squad)):
                squad[n].location = list_of_locs[n]
                squad[n]._p_changed = 1
            return transaction.commit()
        else:
            raise Exception("The squad and the list of locations must be the same length.")
            
    def set_squad_locs(self, squad_num, list_of_locs):
        return self.apply_locs_to_squad(self.squads[squad_num], list_of_locs)
    
    def set_defender_locs(self, list_of_locs):
        return self.apply_locs_to_squad(self.defenders, list_of_locs)
            
    def _set_defenders(self, squad_num):
        """If defenders is empty set squad as defenders."""
        # I don't remember how transactions work so I broke this function in
        # two, which might actually make it worse...
        
        # TODO: there should be a check to make sure the squad is not
        # stronger than the grid.
        # (Which is why self.defenders != self.squad[0])
        
        self.defenders = self.squads[squad_num]
        del self.squads[squad_num]
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
    
    def add_unit_to(self, container, unit_id):
        """Add unit to container."""
        #wrapper to keep containers private.
        self.container.append(self.units[unit_id])
        self.container._p_changed = 1
        return transaction.commit()
        
    def add_unit_to_defenders(self, unit_id):
        return self.add_unit_to(self.defenders, unit_id)
    
    def add_unit_to_factory(self, factory_num, unit_id):
        return self.add_unit_to(self.factories[factory_num], unit_id)
        
    def add_unit_to_squad(self, squad_num, unit_id):
        return self.add_unit_to(self, self.squads[squad_num], unit_id)

    def remove_unit_from(self, container, unit_id):
        """remove unit from container."""
        for n in xrange(len(container)):
            if container[n].id == unit_id:
                container[n].container = None
                container.pop(n)
        self.container._p_changed = 1
        return transaction.commit()
    
    def remove_unit_from_defenders(self, unit_id):
        return self.remove_unit_from(self.defenders, unit_id)
        
    def remove_unit_from_factory(self, factory_num, unit_id):
        return self.remove_unit_from(self.factories[factory_num], unit_id)
        
    def remove_unit_from_squad(self, squad_num, unit_id):
        return self.remove_unit_from(self.squads[squad_num], unit_id)
        
    def transmute(self, target_stone):
        """"Converts stones from one type to another."""
        #2 to 1 for orth elements
        #4 to 1 for opp elements (which is the same as doing orth twice :)
        
    def feed_units(self, now):
        """Attempts to feed units. Happens daily."""
        # A scient eats their composition's worth of stones in 2 months.
        # every two months from when the unit was born, discount the inventory the unit's value.
        # Two weeks without food a unit dies.
        # 1. feed scients first.
        # 2. feed nescients.
        
        