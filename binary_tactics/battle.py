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

from stores.store import get_persisted
        
def now():
    return datetime.utcnow()

    
class Player(dict):
    """object that contains player information (insecure)"""
    #just basic battlefield stuff, no world stuff.
    def __init__(self):
        dict.__init__(self, name=None, squad_list=[])
    
    #laze beams:
    @apply
    def name():
        def fget(self):
            return self['name']
        def fset(self, value):
            self['name'] = value
        return property(**locals())
    
    @apply
    def squad_list():
        def fget(self):
            return self['squad_list']
        def fset(self, value):
            self['squad_list'] = value
        return property(**locals())

    #ya see... what i'm going to do is take this here shoehorn...
    @property
    def __dict__(self):
        return self

class state():
    """Drives the game, marshalls data between persistant storage and Battlefield"""
    #fix me
    def __init__(self, grid=Grid(), player1=Player(), player2=Player(), battlefield=None):
        self.current_ply = ply(num=1)
        self.current_move = move(num=1)
        self.game_id = 0
        self.pass_count = 0
        self.hp_count = 0
        self.squad1_old_hp = 0
        self.squad2_old_hp = 0
        self.game_over = False
        
        if battlefield == None:
            self.player1 = player1
            self.player2 = player2
            self.battlefield = Battlefield(grid, self.player1.squad_list[rand_squad()], self.player2.squad_list[rand_squad()])
        else:
            self.battlefield = battlefield
            self.player1 = self.battlefield.player1
            self.player2 = self.battlefield.player2
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
                self.current_move['message'] += text
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
                self.current_move['message'] += text
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
                self.current_move['message'] += text
                return text
            except:
                raise
                #If player2 attacks a player1 unit that will die when queued
                #damage is applied, the game crashes... I assume because the
                #dies before battlefield.attack is called. This will be tricky
                #to fix, it has to do with when in the turn queued damage is
                #applied. 
                #raise Exception("Attack action failed.")
        else:
            raise Exception("Action is of unknown type")
            
    def append_action(self, action):
        """appends action to current_ply, calls transition()."""
        action.update({'when': now()})
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
        some_ply.update({'when': now()})
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
            print "player 2 wins"
            self.end(now(), self.player2)

        if len(self.battlefield.squad2) == 0:
            if len(self.battlefield.squad1) > 0:
                print "player 1 wins"
                self.end(now(), self.player1)
        #if the last 8 actions are passes, attacker loses/bounces
        if self.pass_count >= 8:
            print "Player 2 wins by way of passing."
            self.end(now(), self.player2)
            
        #if the attacker isn't making any progress, bounce them:
        sq1hp = self.battlefield.squad1.hp()
        sq2hp = self.battlefield.squad2.hp()
        if (sq1hp >= self.squad1_old_hp):
            if (sq2hp >= self.squad2_old_hp):
                self.hp_count += 1        
            else:
                self.hp_count = 0
        elif (sq2hp >= self.squad2_old_hp):
            if (sq1hp >= self.squad1_old_hp):    
                self.hp_count += 1
            else:
                self.hp_count = 0
        else:
            self.hp_count = 0

        if self.hp_count >= 16:
            self.end(now(), self.player2)
        else:
            self.squad1_old_hp = sq1hp
            self.squad2_old_hp = sq2hp
        if self.game_over == False:
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
                    m = self.battlefield.apply_queued()
                    self.current_move['message'] += m
                    self.current_move.update({'when': now()})
                    self.log['moves'].append(self.current_move)
                    self.current_move = move(num=self.current_move['num'] + 1)
                    return m
        else:
            raise Exception("Game Over")
            
    def start(self):
        """attach players and grid to battlefield, start battle."""
        #self.current_move['message'] += ["%s: " %self.player1.name] 
        pass
        
    def end(self, end_time, winner):
        #should add a win_type at some point.
        self.game_over = True
        self.log.close(end_time, winner)
            
class Log(dict):
    def __init__(self, game_id, players, grid, start_time):
        dict.__init__(self)
        self['players'] = players
        self['grid'] = grid
        self['start_time'] = start_time
        self['moves'] = []
        self['end_time'] = None
        self['winner'] = None 
    
    @property
    def __dict__(self):
        #how nasty is this?
        return self
            
    def close(self, end_time, winner):
        self['end_time'] = end_time
        self['winner'] = winner

class message(dict):
    pass
    
class move(dict):
    def __init__(self, num, ply1=None, ply2=None, queued=None):
        self['num']    = num
        self['ply1']   = ply1
        self['ply2']   = ply2
        self['queued'] = queued
        self['message'] = []

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

