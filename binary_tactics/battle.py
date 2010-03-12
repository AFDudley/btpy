#
#  battle.py
#  bintact
#
#  Created by A. Frederick Dudley on 1/9/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
'''
This file contains logic for conducting and recording a battle
'''
from datetime import datetime
from collections import namedtuple
from battlefield import  Battlefield, Grid
from helpers import rand_squad
import defs

def now():
    return datetime.utcnow()

    
class Player(object):
    """object that contains player information insecure"""
    #just basic battlefield stuff, no world stuff.
    def __init__(self):
        self.key = None#TBD
        self.name = None
        self.id = None
        self.unit_list  = None #pointer to all units currently controlled. (query?)
        self.weapon_list = None
        self.squad_list = None #pre-configured squads
'''    
class Player(namedtuple('Player', 'key name id squad_list')):
    """object that contains player information insecure"""
    __slots__ = ()
'''

class state():
    """Drives the game, marshalls data between databases, Log and Battlefield"""
    #fix me
    def __init__(self, grid=Grid(), player1=Player(), player2=Player(), battlefield=None):
        self.current_ply = ply(num=1)
        self.current_move = move(num=1)
        self.player1 = player1
        self.player2 = player2
        self.player1.squad_list = [rand_squad()]
        self.player2.squad_list = [rand_squad()]
        self.game_id = 0
        self.winner = None
        self.pass_count = 0
        self.hp_count = 0
        self.old_total_hp = 0
        self.total_hp = 0
        if battlefield == None:
            self.battlefield = Battlefield(grid, self.player1.squad_list[0], self.player2.squad_list[0])
        else:
            self.battlefield = battlefield
        self.log = Log(self.game_id, [self.player1, self.player2], grid, datetime.now())

    def process_action(self, action):
        """Recieves action from client/player, drives state machine"""
        text = []
        if action['type'] == 'pass':
            try:
                que = self.append_action(action)
                if que != None:
                    text += que
                text += ["Action passed."]
                return text
            except:
                raise
        elif action['type'] == 'move':
            try:
                #move or place?
                self.battlefield.move_unit(action['unit'].location, action['target'])
                que = self.append_action(action)
                if que != None:
                    text += que
                text += ["%s moved to %s" %(action['unit'].name, action['target'])]
                return text
            except:
                raise
                #raise Exception("Move action failed.")
        elif action['type'] == 'attack':
            try:
                que = self.append_action(action)
                if que != None:
                    text += que
                text += (self.battlefield.attack(action['unit'], action['target']))
                return text
            except:
                raise
                #raise Exception("Attack action failed.")
        else:
            raise Exception("Action is of unknown type")
    
    def append_action(self, action):
        """appends action to current_ply, calls transition()."""
        if self.current_ply['action1'] != None:
            if self.current_ply['action2'] == None:
                self.current_ply['action2'] = action
                if action['type'] == 'pass':
                    self.pass_count += 1
                else:
                    self.pass_count = 0
            else:
                raise Exception("Tried to append action to an already full ply")
        else:
            self.current_ply['action1'] = action
            if action['type'] == 'pass':
                self.pass_count += 1
            else:
                self.pass_count = 0        
        return self.transition()

    def append_ply(self, some_ply):
        """appends current_ply to current_move"""
        if self.current_move['ply1'] != None:
            if self.current_move['ply2'] == None:
                self.current_move['ply2'] = some_ply
            else:
                raise Exception("Tried to append ply to an already full move")
        else:
            self.current_move['ply1'] = some_ply
        self.current_ply = ply(num=self.current_ply['num'] + 1)
        
    def transition(self):
        """state changer""" #NOTE: Attackers bounce on draws
        #if a squad is empty, other player won.
        if len(self.battlefield.squad1) == 0:
            self.winner = self.player2
            print "player 2 wins"
        if len(self.battlefield.squad2) == 0:
            if len(self.battlefield.squad1) > 0:
                self.winner = self.player1
                print "player 1 wins"
        #if the last 8 actions are passes, attacker loses/bounces
        if self.pass_count >= 8:
            self.winner = self.player2
            print "Player 2 wins by way of passing."
        #if the last 4 moves have more total hp than each move previous, attacker loses/bounces.
        #rude and crude
        for squad in (self.battlefield.squad1, self.battlefield.squad2):
            for unit in xrange(len(squad) - 1):
                self.total_hp += squad[unit].hp
        if self.old_total_hp != 0:
            if self.total_hp > self.old_total_hp:
                self.hp_count += 1
            else:
                self.hp_count = 0
            self.old_total_hp = self.total_hp
        if self.hp_count >= 4:
            self.winner = self.player2
            print "Player 2 wins by way of Love."
            
        if isinstance(self.current_ply['action2'], action):
            self.append_ply(self.current_ply)
            if isinstance(self.current_move['ply2'], ply):
                new_dict = {}
                for (key, value) in self.battlefield.dmg_queue.items():
                    new_lst = []
                    for lst in value:
                        new_lst.append(tuple(lst))
                    new_dict[key] = new_lst
                self.current_move['queued'] = new_dict
                self.log['moves'].append(self.current_move)
                #if time is up on the battle, attacker loses/bounces.
                self.current_move = move(num=self.current_move['num'] + 1)
                return self.battlefield.apply_queued()
             
    def start(self, player1, player2, grid):
        """attach players and grid to battlefield, start battle."""
        pass
        
    def end(self, log, log_dest):
        """write log to someplace"""
        pass
            
class Log(dict):
    def __init__(self, game_id, players, grid, start_time):
        self['game_id'] = game_id
        self['players'] = players
        self['grid'] = grid
        self['limits'] = None
        self['initial_state'] = None
        self['start_time'] = start_time
        self['moves'] = []
        self['end_time'] = None
        self['winner'] = None #player or 'draw'

    def get_initial_state(self, battlefield):
        """get the initial state of battlefield, Logs it."""
        initial_state = {limits:None, unit_locs:unit_locs}
        unit_locs = []
        for i in players:
            #.get_locs returns tuple of (unit_id, location)
            unit_locs.append(i.squad.get_locs)
        initial_state['unit_locs'] = unit_locs
        
    def close(self, end_time, winner):
        self['end_time'] = now()
        self['winner'] = winner
    
    def to_dict(self):
        """I like to massage data."""
        #deep copy doesn't work on units for some reason. 
        #I find it painfully stupid that I have to use references to
        #de-reference my objects... obviously, if something else was put into
        #the actions and queues, etc... but that requires another mapping someplace...
        beep = {}
        for (key, value) in self.items():
            beep[key] = value
            if key == 'moves':
                lst = []
                for i in value:
                    new_move = {}
                    for (k, v) in i.items():
                        if k == 'num':
                            new_move[k] = v
                        elif k == 'queued':
                            new_q = {}
                            for (w, f) in i[k].items():
                                new_q[id(w)] = f
                            new_move[k] = new_q
                        else:
                            new_move[k] = {}
                            for (ke, va) in i[k].items():
                                if ke != 'num':
                                    new_move[k][ke] = {}
                                    for (l, r) in va.items():
                                        if l == 'unit':
                                            new_move[k][ke][l] = id(i[k][ke]['unit'])
                                        else:
                                            new_move[k][ke][l] = r
                                        
                                else:
                                    new_move[k][ke] = i[k][ke]
                    lst.append(new_move)
                beep[key] = lst
        return beep

'''
class Log(dict):
    def __init__(self, grid=None, players= ()):
        self['moves']      = []
        self['grid']       = grid
        self['players']    = players
        self['start_time'] = now()
        self['end_time']   = None
        self['winner']     = None 
'''

#TODO: Time stamps.
class move(dict):
    def __init__(self, num, ply1=None, ply2=None, queued=None):
        self['num']    = num
        self['ply1']   = ply1
        self['ply2']   = ply2
        self['queued'] = queued

class ply(dict):
    def __init__(self, num=None, action1=None, action2=None):
        """plys are numbered in the order they occur in the game, not within
        their respective move"""
        self['num']     = num
        self['action1'] = action1
        self['action2'] = action2

class action(dict):
    """A action found inside a ply"""
    def __init__(self, unit=None, type=None, target=None):
        self['unit']   = unit
        self['type']   = type
        self['target'] = target

