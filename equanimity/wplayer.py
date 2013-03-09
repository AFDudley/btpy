import hashlib
import persistent

class wPlayer(persistent.Persistent):
    """Object that contains player infomration."""
    def __init__(self, username, password=None):
        persistent.Persistent.__init__(self)
        self.username = username
        self.email = None
        #this is not secure, need to figure that out sometime
        if password != None:
            self.password = hashlib.md5(password).hexdigest()
        else:
            self.password = None
        self.Fields  = persistent.mapping.PersistentMapping()
        self.cookie   = None
        self.roads    = None
        self.treaties = None
    
