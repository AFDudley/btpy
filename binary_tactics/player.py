class Player(object):
    """object that contains player information (insecure)"""
    def __init__(self, name=None, squads=None, stones=None, units=None,
                 weapons=None, grids=None):
        self.name    = name
        self.squads  = squads
        self.stones  = stones
        self.units   = units
        self.weapons = weapons
        self.grids  = grids

