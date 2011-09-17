class Player(object):
    """object that contains player information (insecure)"""
    def __init__(self, name=None, squads=None, stones=None, units=None,
                 weapons=None, fields=None):
        self.name    = name
        self.squads  = squads
        self.stones  = stones
        self.units   = units
        self.weapons = weapons
        self.fields  = fields

class Inventory(object):
    """objet which contains player inventory information"""
    def __init__(self):
        pass