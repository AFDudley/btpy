import persistent
import transaction


import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch
from binary_tactics.units import Squad, Scient
from binary_tactics.weapons import Sword, Bow, Wand, Glove
from binary_tactics.const import ELEMENTS, E, F, I, W, ORTH, OPP

from binary_tactics.helpers import *
from equanimity.factory import Factory, Stable
from equanimity.clock import now

class Silo(Stone):
    """A silo is a really big stone that returns stones when requested."""
    def set_limit(self, limit):
        self.limit.update(limit)
        self._p_changed = 1
        transaction.commit()
    
    def __init__(self, limit=None):
        Stone.__init__(self)
        #the limit will be set to 1.5 times a years harvest.
        if limit != None:
            self.set_limit(self, limit)
    
    def transmute(self, comp):
        """attempts to transmute existing points into Stone of equested comp."""
        #whoops this is an actual math problem.
        #2 to 1 for orth elements
        #4 to 1 for opp elements (which is the same as doing orth twice :)
        negcomp = {"Earth": 0, "Fire":0, "Ice": 0, "Wind": 0}
        for element in ELEMENTS:
            neg = self.comp[element] - comp[element]
            if neg < 0:
                negcomp[element] += neg
            else:
                del negcomp[element]
        
        for element in sorted(negcomp.keys()):
            cost = 2 * abs(negcomp[element]) #the abs is for clarity.
            orthsum = sum([self.comp[x] for x in ORTH[element]])
            remainder = orthsum - cost
            if remainder < 0:
                new_cost = 2 * abs(remainder)
                if new_cost > self.comp[OPP[element]]:
                    raise Exception("There are not enough points to complete the transmutation.")
                else:
                    self.comp[ORTH[element][0]] = 0
                    self.comp[ORTH[element][1]] = 0
                    self.comp[OPP[element]] -= new_cost
            
            else:
                new_remainder = self.comp[ORTH[element][0]] - cost
                if new_remainder > 0:
                    self.comp[ORTH[element][0]] -= cost
                else:
                    self.comp[ORTH[element][0]] = 0
                    self.comp[ORTH[element][1]] -= new_remainder
        #s = Stone()
        #s.limit.update(comp)
        #s.comp = comp #nasty hack for "Big" stones.
        return Stone(comp)
    
    def get(self, comp):
        """Attempts to split the requsted stone, attempts transmuation if split fails."""
        if sum(comp.values()) > self.value():
            raise ValueError("There are not enough points in the silo to create a stone of %s" %comp)
        else:
            #these will fail if comp > limit
            try:
                s = self.split(comp)
                self._p_changed = 1
                transaction.commit()
                return s
            except:
                s = self.transmute(comp)
                self._p_changed = 1
                transaction.commit()
                return s
    
    def imbue_list(self, loS):
        """surplus is destroyed."""
        for stone in loS:
            self.imbue(stone)

class Stronghold(persistent.Persistent):
    def create_factory(self, kind):
        """Adds a factory to a stronghold, raises exception if factory already exists."""
        f = Factory(kind)
        #factories should cost something.
        if f.kind =='Stable':
            if not self.stable:
                self.stable = Stable()
            else:
                raise Exception("This stronghold already has a stable.")
        elif f.kind == 'Armory':
            if not self.armory:
                self.armory = Armory()
            else:
                raise Exception("This stronghold already has an armory.")
        elif f.kind == 'Home':
            if not self.home:
                self.home = Home()
            else:
                raise Exception("This stronghold already has a home.")
        elif f.kind == 'Farm':
            if not self.farm:
                self.farm = Farm()
            else:
                raise Exception("This stronghold already has a farm.")
        self._p_changed = 1
        return transaction.commit()
    
    def __init__(self, field_element, clock):
        self.clock = clock
        self.silo = Silo()
        self.weapons = persistent.list.PersistentList()
        self.units = persistent.mapping.PersistentMapping()
        self.squads = persistent.list.PersistentList()
        self.capacity = 8 #squad points. scient == 1, nescient == 2
        #needs a value limit based on the value of the grid that contains it.
        self.defenders = Squad(kind='mins', element=field_element) #kind should be nescients.
        self.defender_locs = persistent.list.PersistentList()
        self.stable = None
        self.armory = None
        self.home = None
        self.farm = None
        self.create_factory(field_element)
        return transaction.commit()
    
    def form_weapon(self, element, comp, weap_type):
        """Takes a stone from stronghold and turns it into a Weapon."""
        #for testing!!!!!
        #!!!!!!!!WEAP_TYPE NEEDS TO BE CHECKED BEFORE PASSED TO EVAL!!!!!!!!!!!
        #(or I could just fix Weapon, duh)
        weapon = eval(weap_type)(element, self.silo.get(comp))
        self.weapons.append(weapon)
        self._p_changed = 1
        return transaction.commit()
    
    def imbue_weapon(self, comp, weapon_num):
        """Imbue a weapon with stone of comp from silo."""
        stone = self.silo.get(comp)
        self.silo._p_changed = 1
        self.weapons[weapon_num].imbue(stone)
        self.weapons[weapon_num]._p_changed = 1
        return transaction.commit()
    
    def split_weapon(self, comp, weapon_num):
        """Splits comp from weapon, places it in silo."""
        stone = self.weapons[weapon_num].split(comp)
        self.silo.imbue(stone)
        self.weapons[weapon_num]._p_changed = 1
        self.silo._p_changed = 1
        return transaction.commit()
    
    def form_scient(self, element, comp, name=None):
        """Takes a stone from stronghold and turns it into a Scient."""
        if name == None: name = rand_string()
        scient = Scient(element, self.silo.get(comp), name)
        self.units[scient.id] = scient
        self.feed_unit(scient.id)
        self._p_changed = 1
        return transaction.commit()
    
    def imbue_scient(self, comp, unit_id):
        """Imbue a scient with stone of comp from silo."""
        stone = self.silo.get(comp)
        self.silo._p_changed = 1
        scient = self.units[unit_id]
        scient.imbue(stone)
        scient._p_changed = 1
        if scient.container:
            scient.container.update_value()
            scient.container._p_changed = 1
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
    
    def apply_squad_locs(self, squad_num, list_of_locs):
        return self.apply_locs_to_squad(self.squads[squad_num], list_of_locs)
    
    def set_defender_locs(self, list_of_locs):
        self.defender_locs = list_of_locs
        self._p_changed = 1
        return transaction.commit()
    
    def apply_defender_locs(self):
        return self.apply_locs_to_squad(self.defenders, self.defender_locs)
    
    def set_defenders(self, squad_num):
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
    
    def unset_defenders(self):
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
    
    def add_unit_to_factory(self, kind, unit_id):
        if kind == 'Stable':
            return self.add_unit_to(self.stable, unit_id)
        elif kind == 'Armory':
            return self.add_unit_to(self.armory, unit_id)
        elif kind == 'Home':
            return self.add_unit_to(self.home, unit_id)
        elif kind == 'Farm':
            return self.add_unit_to(self.farm, unit_id)
    
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
    
    def remove_unit_from_factory(self, kind, unit_id):
        if kind == 'Stable':
            return self.remove_unit_from(self.stable, unit_id)
        elif kind == 'Armory':
            return self.remove_unit_from(self.armory, unit_id)
        elif kind == 'Home':
            return self.remove_unit_from(self.home, unit_id)
        elif kind == 'Farm':
            return self.remove_unit_from(self.farm, unit_id)
    
    def remove_unit_from_squad(self, squad_num, unit_id):
        return self.remove_unit_from(self.squads[squad_num], unit_id)
    
    def bury_unit(self, unit_id):
        """Bury units that die outside of battle."""
        unit = self.units[unit_id]
        self.unequip_scient(unit)
        self.remove_unit_from(unit.container, unit.id)
        remains = Stone({k: v/2 for k,v in unit.iteritems()})
        self.silo.imbue(remains)
        return
    
    def feed_unit(self, unit_id): #maybe it should take a clock.
        """feeds a unit from the silo, most they can be fed is every 60 days"""
        # A scient eats their composition's worth of stones in 2 months. (60 days)
        # every two months from when the unit was born, discount the inventory the unit's value.
        # Two weeks without food a unit dies.
        
        def feed():
            self.silo.get(unit.comp)
            self.silo._p_changed = 1
            unit.fed_on = now
            unit._p_changed = 1
            return transaction.commit()
        
        if unit.fed_on == None:
            feed()
        else:
            unit = self.units[unit_id]
            now = now()
            delta = now - unit.fed_on
            dsecs = delta.total_seconds()
            if dsecs > (self.clock.duration['day'] * 60):
                if dsecs < (self.clock.duration['day'] * 72):
                    feed()
                else:
                    self.bury_unit(unit_id)
            else:
                pass #unit already fed.
    
    def feed_units(self):
        """Attempts to feed units. check happens every game day."""
        # 1. feed scients first.
        # 2. feed nescients.
        #should not happen when field is embattled.
        now = now()
        for uid,unit in self.units.iteritems():
            d = now - unit.fed_on
            dsecs = d.total_seconds()
            if dsecs > (self.clock.duration['day'] * 60):
                self.feed_unit(uid)
        
