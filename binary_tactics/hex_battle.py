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
        """Records inital game state, timestamps log."""
        #dict.__init__(self, start_time=now(), players=players, grid=grid,
        #              end_time=None, winner=None, states=[], actions=[],
        #              messages=[], applied=[], condition=None)
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
    
    def to_english(self, number, time=True): #BROKEN!!!!!
        """returns a string of english containing an action and mission set from ply number."""
        #still missing DOT, AOE messages, game over messages, etc.
        #oops, this needs to be done client side.
        num = number
        s = "Failed to parse."
        try:
            action  = self['actions'][num]
            message = self['messages'][num]
        except:
            raise Exception("number out of range")
        #really slow lookup but will work for any number of players or squads on field.
        #fix is to store unit-player mapping in log.
        for player in self['players']:
            for squad in player.squads:
                if squad == self['units'][int(action['unit'])].squad:
                    actor = player
        s = actor.name 
        if action['type'] == 'move':
            s += "'s " + self['units'][int(action['unit'])].name
            s += " moved to " + str(action['target'])
        elif action['type'] == 'attack':
            if len(message['result']) > 1: #this catches both DOT and AOE :(
                if message['result'][0][0] != message['result'][1][0]: #if it is an AOE attack?
                    s += "'s " + self['units'][int(action['unit'])].name + ":"
                    for result in message['result']:
                        s += "\n"
                        dmg = result[1]
                        target_owner = self.get_owner(int(result[0]))
                        whom = target_owner.name + "'s " + self['units'][int(result[0])].name
                        if type(dmg) == int:
                            if dmg > 0:
                                s += " dealt " + str(dmg)
                                s += " points of damage to " + whom 
                            else:
                                s += " healed " + whom
                                s += " for " + str(abs(dmg)) + " points"
                        elif type(dmg) == str:
                            s += " killed " + whom
                else: #it's a DOT attack.
                    pass
            else:
                s += "'s " + self['units'][int(action['unit'])].name
                dmg = message['result'][0][1]
                target_owner = self.get_owner(int(message['result'][0][0]))
                whom = target_owner.name + "'s " + self['units'][int(message['result'][0][0])].name
                if type(dmg) == int:
                    if dmg > 0:
                        s += " dealt " + str(dmg)
                        s += " points of damage to " + whom 
                    else:
                        s += " healed " + whom
                        s += " for " + str(abs(dmg)) + " points"
                elif type(dmg) == str:
                    s += " killed " + whom
        elif action['type'] == 'pass':
            s += " passed"
        if time: s += " at " + message['when'] #.isoformat(' ')
        s += "."
        if num % 4 == 0 and num != 0: #MODULO!!!!
            idx = num / 4
            try:
                applied = self['applied'][idx]
                if len(applied['result']) > 0: #was damage was applied.
                    if time:
                        s += "\n  " + "At " + applied['when'] + ":"
                    for (unit, dmg) in applied['result']:
                        s += "\n    "
                        s += self.get_owner(int(unit)).name + "'s " + self['units'][int(unit)].name + " was "
                        if type(dmg) == int:
                            if dmg > 0:
                                s += "damaged " + str(dmg) + " points "
                            else:
                                s += "healed " + str(abs(dmg)) + " points "
                            s += "by the queue."
                        else:
                            s += "killed by damage from the queue."
            except: pass #???
        print s
        return s

class State(dict):
    """A dictionary containing the current game state."""
    def __init__(self, num=1, pass_count=0, hp_count=0, old_squad2_hp=0,
                 queued={}, locs={}, HPs={}, game_over=False):
        dict.__init__(self, num=num, pass_count=pass_count,
                      hp_count=hp_count, old_squad2_hp=old_squad2_hp,
                      queued=queued, locs=locs, HPs=HPs, game_over=game_over)
    
    @property
    def __dict__(self):
        return self
    
    def check(self, game):
        """checks for game ending conditions. (assumes two players)"""
        #REMEMBER PLAYER 1 IS THE ATTACKER.
        num = self['num']
        if game.log['actions'][num - 1]['type'] == 'pass':
            self['pass_count'] += 1
        else:
            self['pass_count'] = 0
        
        if num % 4 == 0:
            squad2_hp = game.battlefield.squad2.hp()
            if self['old_squad2_hp']  <= squad2_hp:
                self['hp_count'] += 1
            else:
                self['hp_count'] = 0
            
            #game over check:
            if self['hp_count'] == 4:
                game.winner = game.player2
                game.end("Player1 failed to deal sufficent damage.")
            else:
                self['old_squad2_hp'] = squad2_hp
        
        #check if game is over.
        if game.battlefield.squad1.hp() == 0:
            game.winner = game.player2
            game.end("Player1's squad is dead")
        
        if game.battlefield.squad2.hp() == 0:
            game.winner = game.player1
            game.end("Player2's squad is dead")
        
        if self['pass_count'] >= 8:
            game.winner = game.player2
            game.end("Both sides passed")
        
        self['queued'] = game.map_queue()
        #self['HPs']    = game.HPs()
        #self['locs']   = game.map_locs()
        self['HPs'], self['locs'] = game.update_unit_info()
        
        game.log['states'].append(State(**self))
        
        #game is not over, state is stored, update state.
        
        self['num'] += 1
    
class Game(object):
    """Almost-state-machine that maintains game state."""
    def __init__(self, grid=Grid(), player1=None, player2=None, battlefield=None):
        self.grid = grid
        self.player1 = player1
        self.player2 = player2
        self.battlefield = battlefield
        #player/battlefield logic for testing
        if self.player1 == None:
            self.player1 = Player('p1', squads=[rand_squad()])
        if self.player2 == None:
            self.player2 = Player('p2', squads=[rand_squad()])
        if self.battlefield == None:
            self.battlefield = Battlefield(grid, self.player1.squads[0],
                                           self.player2.squads[0])
        self.state = State()
        self.players = (self.player1, self.player2)
        self.map = self.unit_map() 
        self.winner = None
        self.units = self.map_unit()
        self.log = Log(self.players, self.units, self.grid)
        self.log['owners'] = self.log.get_owners()
        self.state['old_squad2_hp'] = self.battlefield.squad2.hp()
    
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
            raise TypeError("Acting unit cannont be 'NoneType'")
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
        if action['type'] == 'pass':
            text = [["Action Passed."]]
        elif action['type'] == 'move': #TODO fix move in hex_battlefield.
            text = self.battlefield.move_scient(action['unit'].location,
                                              action['target'])
            if text:
                text = [[id(action['unit']), action['target']]]
        
        elif action['type'] == 'attack':
            text = self.battlefield.attack(action['unit'], action['target'])
        else:
            raise Exception("Action is of unkown type")
        
        self.log['actions'].append(self.map_action(action))
        self.log['messages'].append(Message(num, self.map_result(text)))
        #self.log['messages'].append(Message(num, text))
        
        if num % 4 == 0:
            self.apply_queued()
            #why would I do this??!!?!?!
            #text.append(self.log['applied'][0]['text'])
        else:
            self.state.check(self)
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
        """game over state, handles log closing, updating player stats, TBD"""
        self.state['game_over'] = True
        self.log['states'].append(self.state)
        self.log.close(self.winner, condition)
        print self.log['condition']
        raise Exception("Game Over")
    
