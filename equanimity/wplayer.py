import persistent

class wPlayer(persistent.Persistent):
    """Object that contains player infomration."""
    def __init__(self, username, password=None):
        persistent.Persistent.__init__(self)
        self.username = username
        self.email = None
        #NOT SECURE!
        if password != None:
            self.password = password
        else:
            self.password = None
        self.Fields  = persistent.mapping.PersistentMapping()
        self.cookie   = None
        self.roads    = None
        self.treaties = None
    
