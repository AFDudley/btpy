'''for a two player game. 
move = (ply,ply), game, num
ply = {'actions':'tuple of actions'}
act = {'unit':'id','action':'type', 'target':'loc'}

move = 0, no players have acted.
move = 1, all players in battlefield have acted once
move[n] returns ply n (which has a num of n + 1, for the sake of the people)
'''

action_types = ('move','attack','pass')

class move(tuple):
    """fix me"""
    def __new__(cls, *args, **kwargs):
        
        try:
            tup = []
            for i in range(kwargs['players']):
                tuple.append(ply(num=i+1))
            return tuple.__new__(cls, tuple(tup))
        except KeyError:
            return tuple.__new__(cls, (ply(num=1), ply(num=2)))
    
    def __init__(self, game_id, num):
        self.game_id = game_id
        self.num = num
        
class action(dict):
    """a dict of an action found inside a ply"""
    def __init__(self):
        dict.__init__(self, unit=None, type='pass', target=None)
     
class ply(dict):
    def __init__(self, num, actions=None):
        '''plys are numbered in the order they occur in the game, not within
        their respective move'''
        if actions == None:
            actions = (action(),)
        dict.__init__(self, num=num, actions=actions)
