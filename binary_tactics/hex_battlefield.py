"""contains battlefield objects"""
import random
from math import ceil

from const import E, F, I, W
from defs import Loc, noloc
from stone import Stone
from weapons import Sword, Bow, Wand, Glove

class Tile(Stone):
    """Tiles contain units or stones and are used to make battlefields."""
    def __init__(self, comp=Stone(), contents=None):
        Stone.__init__(self, comp)
        self.contents = contents

class Grid(Stone):
    """Tiles are stones, Grids most likely should be too."""
    def __init__(self, comp=None, x=16, y=16, tiles=None):
        Stone.__init__(self)
        self.x, self.y = self.size = (x, y)
        if tiles == None:
            self.tiles = {}
            for i in range(x):
                row = {}
                for j in range(y):
                    row.update({j: Tile()})
                self.tiles.update({i: row})
        else:
            self.tiles = tiles
    
    def __iter__(self):
        return iter(self.tiles)
    def __contains__(self, value):
        return value in self.tiles
    def __getitem__(self,key):
        return self.tiles[key]
    def __setitem__(self,key,value):
        self.tiles[key] = value
    def __len__(self):
        return len(self.tiles)
    def __repr__(self):
        return dict.__repr__(self.tiles)

class Battlefield(object):
    """contains grid, units and the logic for damage and movement."""
    def __init__(self, grid=None, squad1=None, squad2=None):
        #grid is a tuple of tuples containing tiles
        self.game_id = 0 #?
        self.grid = grid
        self.graveyard = []
        self.squad1 = squad1
        self.squad2 = squad2
        self.dmg_queue = {}
        self.squads = (self.squad1, self.squad2)
        self.units = self.get_units()
        self.direction = {0:'North', 1:'Northeast', 2:'Southeast', 3:'South', 4:'Southwest', 5:'Northwest'}
        self.ranged = ('Bow',   'Magma',     'Firestorm', 'Forestfire', 'Pyrocumulus')
        self.DOT    = ('Glove', 'Firestorm', 'Icestorm',  'Blizzard',   'Pyrocumulus')
        self.AOE    = ('Wand',  'Avalanche', 'Icestorm',  'Blizzard',   'Permafrost',)
        self.Full   = ('Sword', 'Magma',     'Avalanche', 'Forestfire', 'Permafrost')
        
    def get_units(self):
        """looks in squads, returns all units in squads."""
        #Squads should be made immutable somewhere in Battlefield.
        units = []
        for squad in self.squads:
            if squad != None:
                for unit in squad:
                    units.append(unit)
        return tuple(units)
    
    def on_grid(self, tile):
        """returns True if tile is on grid"""
        if 0 <= tile[0] < self.grid.x:
            if 0 <= tile[1] < self.grid.y:
                return True
            else:
                return False
        else:
            return False
    
    def get_adjacent(self, tile, direction="All"):
        """returns a set of hextiles adjacent to the tile provided, if they are in fact on the grid."""
        direction = direction
        xpos,ypos = tile
        directions = {"East":((xpos + 1, ypos),), "West":((xpos - 1, ypos),),}
        if ypos&1: #sub-optimal
            directions.update({"North":((xpos + 1, ypos - 1),(xpos, ypos - 1)),
                          "South":((xpos + 1, ypos + 1), (xpos, ypos + 1)),
                          "Northeast":((xpos + 1, ypos - 1), (xpos + 1, ypos)),
                          "Southeast":((xpos + 1, ypos + 1), (xpos + 1, ypos)),
                          "Southwest":((xpos, ypos + 1), (xpos - 1, ypos)),
                          "Northwest":((xpos, ypos - 1), (xpos - 1, ypos)),})
        else:
            directions.update({"North":((xpos, ypos - 1),(xpos - 1, ypos - 1)),
                          "South":((xpos, ypos + 1), (xpos - 1, ypos + 1)),
                          "Northeast":((xpos, ypos - 1), (xpos + 1, ypos)),
                          "Southeast":((xpos, ypos + 1), (xpos + 1, ypos)),
                          "Southwest":((xpos - 1, ypos + 1), (xpos - 1, ypos)),
                          "Northwest":((xpos - 1, ypos - 1), (xpos - 1, ypos)),})
        directions["All"] = directions["North"] + directions["East"] + directions["South"] + directions["West"]
        out = []
        for loc in directions[direction]:
            if self.on_grid(loc):
                out.append(loc)
        return set(out)
    
    def make_pattern(self, location, distance, pointing):
        """generates a pattern based on an origin, distance, and
        direction. Returns a set of coords"""
        location  = location
        dist = distance
        pointing = pointing
        tiles = []
        pattern = []
        head = self.get_adjacent(location, pointing)
        cols = 1 #maintain dist = 1 behavior.
        while cols != dist:
            pattern += list(head)
            temp_head = head
            head = set()
            for loc in temp_head:
                head |= self.get_adjacent(loc, pointing)
            cols += 1
        return pattern
    
    def map_to_grid(self, location, weapon):
        """returns tiles within range of location using weapon. called in hex_view.py"""
        weapon = weapon
        xpos, ypos = location = location
        tiles = []
        if weapon.type in self.ranged:
            move = 4
            no_hit = self.make_range(location, move)
            hit    = self.make_range(location, 2*move)
            return hit - no_hit
        elif weapon.type in self.AOE:
            #lazy hack: AOE can now hit everywhere.
            tiles  = set([(x, y) for x in xrange(self.grid.x) for y in xrange(self.grid.y)])
            tiles -= set(((location),),)
            return list(tiles)
        else:
            return self.get_adjacent(location)
    
    def make_range(self, location, distance):
        """generates a list of tiles within distance of location."""
        location = location
        dist = distance
        
        tiles = []
        #so far from optimal
        tiles.append(self.get_adjacent(location))
        while len(tiles) < dist:
            new = set()
            for tile in tiles[-1]:
                new |= self.get_adjacent(tile)
            tiles.append(new)
        group = set()
        for x in tiles: group |= x
        return group
    
    def move_unit(self, src, dest):
        """move unit from src tile to dest tile"""
        if self.on_grid(src):
            xsrc, ysrc = src
        else:
            raise Exception("Source %s is off grid" %src)
        
        if self.on_grid(dest):
            xdest, ydest = dest
        else:
            raise Exception("Destination %s is off grid" %dest)
        
        if self.grid[xsrc][ysrc].contents:
            if not self.grid[xdest][ydest].contents:
                move = self.grid[xsrc][ysrc].contents.move
                if dest in self.make_range(src, move):
                #if abs(xsrc-xdest) + abs(ysrc-ydest) <= move:
                    self.grid[xdest][ydest].contents = \
                    self.grid[xsrc][ysrc].contents
                    self.grid[xdest][ydest].contents.location = Loc(xdest, ydest)
                    self.grid[xsrc][ysrc].contents = None
                    return True
                else:
                    raise Exception("tried moving more than %s tiles" %move)
            else:
                raise Exception("There is already something at %s" %str(dest))
        else:
            raise Exception("There is nothing at %s" %str(src))
    
    def place_unit(self, unit, tile):
        """Places unit at tile, if already on grid, move_unit is called"""
        if self.on_grid(tile):
            xpos, ypos = tile
        else:
            raise Exception("Tile %s is off grid" %tile)
        
        if unit.location == noloc:
            if self.grid[xpos][ypos].contents == None:
                self.grid[xpos][ypos].contents = unit
                unit.location = Loc(xpos, ypos)
                self.dmg_queue[unit] = [] #append unit to dmg_queue
                return True
            
            elif unit.location == Loc(xpos, ypos):
                raise Exception("This unit is already on (%s,%s)" %(xpos, ypos))
            
            elif self.grid[xpos][ypos].contents != None:
                raise Exception("(%s, %s) is not empty" %(xpos, ypos))
        else:
            return self.move_unit(unit.location, tile)
    
    def find_units(self):
        """returns a list of units in grid."""
        lst = []
        for x in range(len(self.grid)): #maybe using .x and .y would be faster?
            for y in range(len(self.grid[x])):
                if self.grid[x][y].contents:
                    lst.append((x, y)) #maybe this should be a loc?
        return lst
    
    def rand_place_unit(self, unit):
        """Randomly place a unit on the grid."""
        #readable?
        inset = 0 #place units in a smaller area, for testing.
        def Randpos():
            """returns a random position in grid."""
            return (random.randint(0, ((self.grid.x - 1) - inset)),
            random.randint(0, ((self.grid.y - 1) - inset)))
        if len(self.find_units()) == (self.grid.x * self.grid.y):
            raise Exception("Grid is full")
        else:
            while unit.location == noloc:
                try:
                    self.place_unit(unit, Randpos())
                    break
                except Exception:
                    pass
    
    def rand_place_squad(self, squad):
        """place the units in a squad randomly on the battlefield"""
        for unit in range(len(squad)):
            self.rand_place_unit(squad[unit])
    
    def flush_units(self):
        """
        remove all units from grid, returns number of units flushed,
        does not put them in the graveyard. (for testing)
        """
        #maybe find_unit should be used here...
        num = 0
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y].contents:
                    self.grid[x][y].contents.location = noloc
                    self.grid[x][y].contents = None
                    num += 1
        return num
    
    
    #Attack/Damage stuff
    def dmg(self, atkr, defdr, type):
        """Calculates the damage of an attack"""
        dloc = defdr.location
        damage_dealt = {E: 0, F: 0, I: 0, W: 0}
        if self.on_grid(dloc):
            if atkr.weapon.kind == 'p':
                for element in damage_dealt:
                    dmg = (atkr.p + atkr.patk + (2 * atkr.comp[element]) +
                    atkr.weapon.comp[element]) - (defdr.p + defdr.pdef +
                    (2 * defdr.comp[element]) + self.grid[dloc.x][dloc.y].comp[element])
                    dmg = max(dmg, 0)
                    damage_dealt[element] = dmg
                damage = sum(damage_dealt.values())
                return damage
            else:
                for element in damage_dealt:
                    dmg = (atkr.m + atkr.matk + (2 * atkr.comp[element]) +
                    atkr.weapon.comp[element]) - (defdr.m + defdr.mdef +
                    (2 * defdr.comp[element]) + self.grid[dloc.x][dloc.y].comp[element])
                    dmg = max(dmg, 0)
                    damage_dealt[element] = dmg
                
                damage = sum(damage_dealt.values())
                if atkr.element == defdr.element:
                    return 0 - damage
                else:
                    return damage
        else:
            raise Exception("Defender is off grid")
    
    def make_distances(self, src, dest):
        ax,ay = src
        dx,dy = dest
        xdist = abs(dx - ax)
        ydist = abs(dy - ay)
        zdist = xdist + ydist/2 + 1
        ranges = {}
        for index in range(6):
            ranges[index] = zdist
        
        ranges.update({0:ydist + 1, 3:ydist + 1,})
        if ay & 1:
            if not dy & 1:
                ranges.update({4:zdist + 1, 5:zdist + 1,})
        else:
            if dy & 1:
                ranges.update({1:zdist + 1, 2:zdist + 1,})
        return ranges
    
    def maxes(self, src):
        '''NOTE: Currently, AOE weapons can hit every tile on the grid so this is
                 really quite moot.
                 
                 At some point LOS style blasting might be added at which
                 point this would be needed.
        '''
        #sub-optimal should check ay % 1 and change the + 1 and + 2 accordingly.
        ax, ay = src
        maxes = {
                0:ay + 1,
                1:(self.grid.x - ax) + ay/2,
                2:(self.grid.x - ax) + (self.grid.y - ay)/2, 
                3:self.grid.y - ay,
                4:ax + (self.grid.y - ay)/2 + 1,
                5: ax + ay/2 + 2,
                }
        return maxes
    
    def calc_AOE(self, atkr, target):
        """Returns the AOE of a spell. Called once in hex_view.py"""
        xpos, ypos = aloc = atkr.location
        dloc = Loc._make(target)
        dists = self.make_distances(aloc, dloc)
        maxes = self.maxes(aloc)
        for i in self.direction:
            pat = self.make_pattern(aloc, maxes[i], self.direction[i])
            if dloc in pat:
                #all of this could be done in-place.
                pat_ = self.make_pattern(aloc, dists[i], self.direction[i])
                new_pat = []
                for i in pat_:
                    if self.on_grid(i):
                        new_pat.append(i)
                return new_pat
    
    def calc_damage(self, atkr, defdr):
        """Calcuate damage delt to defdr from atkr. Also calculates the damage of
        all units within a blast range. if weapon has a AOE list of
        [[target, dmg]] is returned. otherwise just (target, dmg) is returned"""
        #Broken: dmg_queue is applied at the wrong time in battle.py
        weapon = atkr.weapon
        aloc = atkr.location
        dloc = defdr.location
        dmg_lst = []
        in_range = self.map_to_grid(aloc, weapon)
        if not(dloc in in_range):
            raise Exception( \
            "Defender's location: %s is outside of attacker's range" %str(dloc))
        else:
            #calculate how many units will be damaged.
            if weapon.type in self.AOE:
                pat = self.calc_AOE(atkr, dloc)
                targets = list(set(self.find_units()) & set(pat))
                area = len(pat)
                for t in targets:
                    defdr = self.grid[t[0]][t[1]].contents
                    temp_dmg = self.dmg(atkr, defdr, weapon.type)
                    if temp_dmg != 0:
                        #currently the only non-full, non-DOT AOE weapon
                        if weapon.type != 'Wand':
                            dmg_lst.append((defdr, temp_dmg))
                        else:
                            temp_dmg /= area
                            if temp_dmg != 0:
                                dmg_lst.append((defdr, temp_dmg))
                    else:
                        pass # no damage was dealt, don't append anything.

            elif weapon.type in self.ranged:
                #this is a placeholder until calc_ranged is written.
                dmg_lst.append((defdr, self.dmg(atkr, defdr, weapon.type) / 4))
            else: #attack is only hitting one unit.
                dmg_lst.append((defdr, self.dmg(atkr, defdr, weapon.type)))

            if weapon.type in self.DOT:
                dmg_lst = [(t[0], t[1] / weapon.time) for t in dmg_lst]

            if len(dmg_lst):
                return dmg_lst
            else:
                return None
    def apply_dmg(self, target, damage):
        """applies damage to target, called by attack() and
        apply_queued() returns damage applied"""
        if damage >= target.hp:
            try:
                self.bury(target)
                return "Dead."
                #return target.hp
            except:
                raise Exception("STOP BEING GREEDY.")
        else:
            target.hp -= damage
            return damage
    
    def bury(self, unit):
        """moves unit to graveyard"""
        x,y = unit.location
        unit.hp = 0
        self.grid[x][y].contents = None
        unit.location = Loc(-1,-1)
        del self.dmg_queue[unit]
        self.graveyard.append(unit)
        return True
    
    def attack(self, atkr, target):
        """calls calc_damage, applies result, Handles death."""
        defdr = self.grid[target[0]][target[1]].contents
        dmg = self.calc_damage(atkr, defdr)
        if dmg != None:
            if isinstance(dmg, int) == True: #with new calc_damage this should never hit
                print "why did I hit?"
                if dmg != 0:
                    recieved_dmg = self.apply_dmg(defdr, dmg)
                else:
                    return [[defdr, 0]]
                if defdr.hp > 0:
                    if atkr.weapon.type in self.DOT:
                        self.dmg_queue[defdr].append([dmg, atkr.weapon.time - 1])
                return [[defdr, recieved_dmg]]
            
            else:
                defdr_HPs = []
                for i in dmg:
                    if i[0].hp > 0:
                        defdr_HPs.append([i[0], self.apply_dmg(i[0], i[1]) ])
                return defdr_HPs
        
        else:
            #no damage
            return []
    
    def get_dmg_queue(self):
        """returns a copy of the dmg_queue."""
        new_dict = {}
        for (key, value) in self.dmg_queue.items():
            new_lst = []
            for lst in value:
                new_lst.append(tuple(lst))
                new_dict[key] = new_lst
        return new_dict
    
    def apply_queued(self):
        """applies damage to targets stored in dmg_queue"""
        defdr_HPs = []
        for i in self.dmg_queue.keys():
            udmg = []
            for dmg_lst in reversed(xrange(len(self.dmg_queue[i]))):
                udmg.append(self.dmg_queue[i][dmg_lst][0])
                self.dmg_queue[i][dmg_lst][1] -= 1
                if self.dmg_queue[i][dmg_lst][1] == 0:
                    del self.dmg_queue[i][dmg_lst]
            
            udmg = sum(udmg)
            if udmg != 0:
                defdr_HPs.append([i, self.apply_dmg(i, udmg)])
        return defdr_HPs
    
