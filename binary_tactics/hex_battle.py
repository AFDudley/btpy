#
#  battle.py
#  
#
#  Created by RiX on 3/21/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
'''
The $64 question is what holds state?
The battlefield doesn't hold state. but it has the damage queue :/
battle currently just takes actions from any ol' place.
the problem being that auth in fact does need to be outside of battle.py (way outside)
So... how is the validity of a message determined? 
Since battle can't really know about players, (the current player object is 
a placeholder.) it cannot make sure that each player is taking their turns correctly,
yet it assumes that there are two players... the problems with this code go on...
'''
from datetime import datetime
from collections import namedtuple
from binary_tactics.hex_battlefield import  Battlefield, Grid
from binary_tactics.helpers import rand_squad
from binary_tactics.units import Unit
from binary_tactics.player import Player

from stores.store import *
import json

def now():
    return str(datetime.utcnow())

class Action(dict):
    #'when' needs more thought.
    #type needs to != 'pass'
    def __init__(self, unit=None, type='pass', target=None, when=None, num=None):
        dict.__init__(self, unit=unit, type=type, target=target, num=num, 
                      when=now())
    
    @property
    def __dict__(self):
        return self

class Message(dict):
    def __init__(self, num, result):
        dict.__init__(self, num=num, result=result, when=now())
    
    @property
    def __dict__(self):
        return self
    
class Change_list(dict): #belongs in different file
    def __init__(self, event, kwargs):
        dict.__init__(self, event, **kwargs)
        
    @property
    def __dict__(self):
        return self
    
class Battle_changes(Change_list):
    def __init__(self, victors, prisoners, awards, event='battle'):
        dict.__init__(self, event=event, victors=victors,
                      prisoners=prisoners, awards=awards)

class Initial_state(dict):
    """A hack for serialization."""
    def __init__(self, log):
        #self.start_time = log['start_time']
        #self.players    = log['players']
        #self.units      = log['units']
        #self.grid       = log['grid']
        #self['init_locs']  = log['init_locs']
        dict.__init__(self, init_locs=log['init_locs'],
                            start_time=log['start_time'],
                            units=log['units'],
                            grid=log['grid'],
                            owners=log['owners'],)
        #self['owners'] = self.get_owners(log)

    @property
    def __dict__(self):
        return self
            
class Log(dict):
    def __init__(self, players, units, grid):
        """Records initial game state, timestamps log."""
        #dict.__init__(self, start_time=now(), players=players, grid=grid,
        #              end_time=None, winner=None, states=[], actions=[],
        #              messages=[], applied=[], condition=None)
        self['event']      = 'battle'
        self['change_list'] = None
        self['start_time'] = now()
        self['end_time']   = None
        self['players']    = players
        self['units']      = units
        self['grid']       = grid
        self['winner']     = None
        self['states']     = [] #Hmm, Does this really need to be here.
        self['actions']    = []
        self['messages']   = [] 
        self['applied']    = []
        self['condition']  = None
        self['owners']     = None
        self['init_locs']  = None
        
    @property
    def __dict__(self):
        return self
    
    def init_locs(self):
        #calling this in init is most likely not going to work as intended.
        locs = {}
        for u in self['units'].keys():
            locs.update({u: self['units'][u].location})
        return locs
    
    def close(self, winner, condition):
        """Writes final timestamp, called when game is over."""
        self['end_time'] = now()
        self['winner'] = winner
        self['condition'] = condition
    
    def get_owner(self, unit_num):
        """takes unit number returns player/owner."""
        #slow lookup
        target_squad = self['units'][unit_num].squad.name
        for player in self['players']:
            for squad in player.squads:
                if squad.name == target_squad:
                    owner = player
        return owner
    
    #LAZE BEAMS!!!!
    def get_owners(self):
        """mapping of unit number to player/owner."""
        owners = {}
        for unit in self['units'].keys():
            owners[unit] = self.get_owner(unit).name
        return owners
    
class State(dict):
    """A dictionary containing the current game state."""
    def __init__(self, num=1, pass_count=0, hp_count=0, old_defsquad_hp=0, queued={}, locs={}, HPs={}, game_over=False):
        dict.__init__(self, num=num, pass_count=pass_count,
                      hp_count=hp_count, old_defsquad_hp=old_defsquad_hp,
                      queued=queued, locs=locs, HPs=HPs, game_over=game_over)
    
    @property
    def __dict__(self):
        return self
    
    def check(self, game):
        """checks for game ending conditions. (assumes two players)"""
        num = self['num']
        last_type = game.log['actions'][num - 1]['type'] 
        if (last_type == 'pass') or (last_type == 'timed_out'):
            self['pass_count'] += 1
        else:
            self['pass_count'] = 0
        
        if num % 4 == 0:
            defsquad_hp = game.battlefield.defsquad.hp()
            if self['old_defsquad_hp']  <= defsquad_hp:
                self['hp_count'] += 1
            else:
                self['hp_count'] = 0
            
            #game over check:
            if self['hp_count'] == 4:
                game.winner = game.defender
                game.end("Attacker failed to deal sufficent damage.")
            else:
                self['old_defsquad_hp'] = defsquad_hp
        
        #check if game is over.
        if game.battlefield.defsquad.hp() == 0:
            game.winner = game.attacker
            game.end("Defender's squad is dead")
        
        if game.battlefield.atksquad.hp() == 0:
            game.winner = game.defender
            game.end("Attacker's squad is dead")
        
        if self['pass_count'] >= 8:
            game.winner = game.defender
            game.end("Both sides passed")
        
        self['queued'] = game.map_queue()
        self['HPs'], self['locs'] = game.update_unit_info()
        
        game.log['states'].append(State(**self))
        
        #game is not over, state is stored, update state.
        self['num'] += 1
    

class Game(object):
    """Almost-state-machine that maintains game state."""
    def __init__(self, grid=Grid(), defender=None, attacker=None, battlefield=None):
        self.grid = grid
        self.defender = defender
        self.attacker = attacker
        self.battlefield = battlefield
        #player/battlefield logic for testing
        if self.defender == None:
            self.defender = Player('Defender', squads=[rand_squad()])
        if self.attacker == None:
            self.attacker = Player('Attacker', squads=[rand_squad()])
        if self.battlefield == None:
            self.battlefield = Battlefield(grid, self.defender.squads[0],
                                           self.attacker.squads[0])
        self.state = State()
        self.players = (self.defender, self.attacker)
        self.map = self.unit_map() 
        self.winner = None
        self.units = self.map_unit()
        self.log = Log(self.players, self.units, self.battlefield.grid)
        self.log['owners'] = self.log.get_owners()
        self.state['old_defsquad_hp'] = self.battlefield.defsquad.hp()
        self.whose_turn = self.defender
    
    def unit_map(self):
        """mapping of unit ids to objects, used for serialization."""
        mapping = {}
        for unit in self.battlefield.units: mapping[unit] = id(unit)
        return mapping
    
    def map_unit(self):
        units = {}
        for (k,v) in self.map.items(): units[v] = k
        return units
    
    def map_locs(self):
        """maps unit name unto locations, only returns live units"""
        locs = {}
        for unit in self.map:
            loc = unit.location
            if loc[0] >= 0:
                locs[self.map[unit]] = loc
        return locs
    
    def HPs(self):
        """Hit points by unit."""
        HPs ={}
        for unit in self.map:
            hp = unit.hp
            if hp > 0:
                HPs[self.map[unit]] = hp
        return HPs
        
    def update_unit_info(self):
        """returns HPs, Locs."""
        HPs   = {}
        locs  = {}
        
        for unit in self.map:
            num = self.map[unit]
            loc = unit.location
            if loc[0] >= 0:
                locs[num] = loc
                HPs[num] = unit.hp
        
        return HPs, locs
        
    def map_queue(self):
        """apply unit mapping to units in queue."""
        old = self.battlefield.get_dmg_queue()
        if isinstance(old, dict):
            new = {}
            for key in old.keys():
                new[str(id(key))] = old[key]
            return new
        else:
            return None
    
    def map_result(self, result):
        if result != None:
            for t in result:
                if isinstance(t[0], Unit):
                    t[0] = id(t[0])
            return result
    
    def map_action(self, action):
        """replaces unit refrences to referencing their hash."""
        new = Action(**action)
        if new['unit'] != None:
            new['unit'] = id(new['unit'])
        else:
            new['unit'] = None
            #raise TypeError("Acting unit cannont be 'NoneType'")
        return new
    
    def last_message(self):
        text = self.log['messages'][-1]['result']
        if text != None:
            return self.log['messages'][-1]['result']
        else:
            return ["There was no message."]
    
    def process_action(self, action):
        action['when'] = now()
        action['num']  = num = self.state['num']
        if action['type'] == 'timed_out':
            text = [["failed to act."]]
        elif action['type'] == 'pass':
            text = [["Action Passed."]]
        elif action['type'] == 'move': #TODO fix move in hex_battlefield.
            text = self.battlefield.move_scient(action['unit'].location,
                                              action['target'])
            if text:
                text = [[id(action['unit']), action['target']]]
        
        elif action['type'] == 'attack':
            text = self.battlefield.attack(action['unit'], action['target'])
        else:
            raise Exception("Action is of unknown type")
        
        self.log['actions'].append(self.map_action(action))
        self.log['messages'].append(Message(num, self.map_result(text)))
        
        if num % 4 == 0: #explain please.
            self.apply_queued()
        else:
            self.state.check(self)
        
        #switches whose_turn.
        if self.whose_turn == self.defender:
            self.whose_turn = self.attacker
        else:
            self.whose_turn = self.defender
        if num % 4 == 0:
            return {'command': self.log['actions'][-1], 'response': self.log['messages'][-1],
                    'applied': self.log['applied'][-1]}
        else:
            return {'command': self.log['actions'][-1], 'response': self.log['messages'][-1]}
            
    
    def apply_queued(self):
        """queued damage is applied to units from this state"""
        text = self.battlefield.apply_queued()
        self.log['applied'].append(Message(self.state['num'], self.map_result(text)))
        self.state.check(self)
    
    def last_state(self):
        """Returns location and HP of all units. As well as proximity to winning conditions."""
        try:
            return self.log['states'][-1]
        except:
            return None
    
    def initial_state(self):
        """Returns stuff to create the client side of the game"""
        return Initial_state(self.log)
    
    def end(self, condition):
        """game over state, handles log closing, writes change list for world"""
        log = self.log
        self.state['game_over'] = True
        log['states'].append(self.state)
        log.close(self.winner, condition)
        #make change list
        victors = []
        prisoners = []

        #split survivors into victors and prisoners
        for unit in log['states'][-1]['HPs'].keys():
            if log['winner'].name == log['owners'][unit]:
                victors.append(unit)
            else:
                prisoners.append(unit)
        #calculate awards
        awards    = {} #should be a stone.
        self.log['change_list'] = Battle_changes(victors, prisoners, awards)
        raise Exception("Game Over")
    
