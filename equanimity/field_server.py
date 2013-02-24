import sys
import cyclone.web
from twisted.internet import reactor
from equanimity.zeo import Zeo

class BaseHandler(cyclone.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class Handler(cyclone.web.RequestHandler):
    def get(self):
        self.write(str(world_coords))
        
def main(args): #improve.
    lport = args[0]
    zeo_addr = list(args[1])
    global world_coords
    world_coords = str(args[2])
    
    zeo = Zeo(zeo_addr)
    #world  = zeo.root
    app = cyclone.web.Application([(r"/", Handler)])
    
    reactor.listenTCP(lport, app)
    reactor.run()
    
if __name__ == "__main__":
    #if sys.argv[1]:
    #    args = sys.argv[1:]
    
    args = [9101, ('localhost', 9100), '(0, 0)']
    main(args)
