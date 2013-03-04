import sys
import cyclone.web
from twisted.internet import reactor
from equanimity.zeo import Zeo

class BaseJSONHandler(jsonrpc.JsonrpcRequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_get_username(self):
        """Takes a cookie and returns the username encoded within it."""
        username = yield self.get_current_user().strip('"')
        defer.returnValue(username)

    @defer.inlineCallbacks
    def jsonrpc_time_left(self):
        now = datetime.utcnow()
        ply = datetime.utcfromtimestamp(self.settings.ply_timer.call.getTime())
        timeleft = yield {'battle': str(self.settings.ART - now), 'ply': str(ply - now)}

class Handler(cyclone.web.RequestHandler):
    def get(self):
        self.write(str(world_coords))


class BattleHandler(jsonrpc.JsonrpcRequestHandler):
    def __init__(self):
        pass
def main(args): #improve.
    lport = args[0]
    zeo_addr = list(args[1])
    global world_coords
    world_coords = str(args[2])
    
    zeo = Zeo(zeo_addr)
    #world  = zeo.root
    app = cyclone.web.Application([(r"/", Handler),
                                   (r"/battle",BattleHandler),
                                   (r"/produce", ProduceHandler),
                                   (r"/view", ViewHandler),])
    
    reactor.listenTCP(lport, app)
    reactor.run()
    
if __name__ == "__main__":
    #if sys.argv[1]:
    #    args = sys.argv[1:]
    
    args = [9101, ('localhost', 9100), '(0, 0)']
    main(args)
