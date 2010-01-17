'''for a two player game. 
move = (ply,ply), game, num
ply = {'actions':'tuple of actions'}
act = {'unit':'id','action':'type', 'target':'loc'}

move = 0, no players have acted.
move = 1, all players in battlefield have acted once
move[n] returns ply n (which has a num of n + 1, for the sake of the people)
'''
#TODO: Time stamps.
action_types = ('move','attack','pass', 'queued')
class move(list):
    """contains the actions and damage queue generated during nth move."""
    def __init__(self, num, ply1=None, ply2=None, queued=None):
        self.num = num
        list.__init__(self, [ply1, ply2, queued])

class ply(list):
    def __init__(self, num=None, action1=None, action2=None):
        '''plys are numbered in the order they occur in the game, not within
        their respective move'''
        self.num = num
        list.__init__(self, [action1, action2])

class action(list):
    """A action found inside a ply"""
    def __init__(self, unit=None, type=None, target=None):
        list.__init__(self, [unit, type, target])
     

