import sys
import cyclone.web

from twisted.python import log
from twisted.internet import reactor, defer

from equanimity.world import wPlayer
from ZEO import ClientStorage
from ZODB import DB
import transaction

from binary_tactics.hex_battle import *
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.defs import Loc
        
class BaseJSONHandler(cyclone.web.JsonrpcRequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
class BattleHandler(BaseJSONHandler):
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_register(self):
        """Takes a cookie and registers it in a battlefield."""
        current_user = yield self.get_current_user()
        defer.returnValue(current_user)
        
    @defer.inlineCallbacks
    def jsonrpc_initial_state(self):
        init_state = yield self.settings.game.initial_state()
        defer.returnValue(str(init_state))
        
    @defer.inlineCallbacks
    def jsonrpc_get_state(self):
        state = yield self.settings.game.state
        defer.returnValue(state)
        
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_process_action(self, args):
        err = self.get_argument("e", None)
        print self.get_current_user()
        try:
            #obviously this needs to be more robust.
            #so nasty.
            action = Action(eval(args[0]), args[1], eval(args[2]))
            result = yield self.settings.game.process_action(action)
            defer.returnValue(result)
        except Exception , e:
            log.err("process_action failed: %r" % e)
            raise cyclone.web.HTTPError(500, "%r" % e.args[0])
            
class Zeo(object):
    def __init__(self, addr=('localhost', 9100)):
        self.addr = addr
        self.storage = ClientStorage.ClientStorage(self.addr)
        self.db = DB(self.storage)
        self.conn = self.db.open()
        self.root = self.conn.root()
        
    def get(self, username): #FIX
        self.conn.sync()
        return self.root['Players'][username].password
        
    def set(self, username, password): #FIX
        try:
            self.conn.sync()
            assert not self.root['Players'][username].password
        except Exception: #this exception looks dangerous
            self.root['Players'][username] = wPlayer(username, password)
            self.root._p_changed = 1
            return transaction.commit()
    
def main():
    zeo    = Zeo()
    world  = zeo.root
    wField = world['Fields'][str(sys.argv[1])]
    grid = wField.grid
    attacker, squad1 = wField.battlequeue[0]
    squad2 = wField.get_defenders()
    #player1 is attacker
    game = Game(player1=attacker, player2=wField.owner,
                battlefield=Battlefield(grid, squad1, squad2))
    btl = game.battlefield
    #obviously for testing only.
    for squad in btl.squads:
        btl.rand_place_squad(squad)
    
    game.log['init_locs'] = game.log.init_locs()
    application = cyclone.web.Application([(r"/", BattleHandler)],
    zeo = zeo,
    game = game,
    login_url="/auth/login",
    cookie_secret="secret!!!!"
    )
    
    reactor.listenTCP(8890, application)
    reactor.run()

if __name__ == "__main__":    
    log.startLogging(sys.stdout)
    main()
