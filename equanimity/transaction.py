#TODO store in AODB, txtdb or some other append only solution.
class Transaction(dict):
    """A record of a world event."""
    def __init__(self, who, when, what):
        dict.__init__(self, who=who, when=when, what=what)
        self.sig = None
    
    @property
    def __dict__(self):
        return self