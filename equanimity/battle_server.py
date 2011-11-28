'''
TODO:
    write world_server that calls this dynamically.
    Write a serializing wrapper around battle.
    Filter information based on authenticated player.
    write frontend.
'''
import sys
import json
import cyclone.web

from twisted.python import log
from twisted.internet import reactor, defer

from equanimity.world import wPlayer
from ZEO import ClientStorage
from ZODB import DB
import transaction

from binary_tactics.hex_battle import Game, Action
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.player import Player
from binary_tactics.defs import Loc

from stores.store import get_persisted
import copy

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
        #hill larry ous
        init_state = yield get_persisted(self.settings.game.initial_state())
        defer.returnValue(init_state)
    
    @defer.inlineCallbacks
    def jsonrpc_get_state(self):
        state = yield self.settings.game.last_state()
        defer.returnValue(state)
    
    @defer.inlineCallbacks
    def jsonrpc_game_log(self):
        log = yield self.settings.game.log
        defer.returnValue(str(log))
    
    #@cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_process_action(self, args):
        err = self.get_argument("e", None)
        print self.get_current_user()
        try:
            #obviously this needs to be more robust.
            #so nasty.
            units = self.settings.game.units
            action = Action(units[int(args[0])], args[1], eval(args[2]))
            result = yield self.settings.game.process_action(action)
            #this should not be an actual file
	    f = open("./web/last_state.json", 'w')
	    f.write(str(self.settings.game.last_state()))
	    f.close()
	    defer.returnValue(result)

        except Exception , e:
	    log.err("action: %s" % action)
            log.err("process_action failed: %r" % e)
            raise cyclone.web.HTTPError(500, "%r" % e.args[0])

class LastStateHandler(cyclone.web.RequestHandler):
    def get(self):
        self.render("last_state.json")

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
    f = copy.deepcopy(world['Fields'][str(sys.argv[1])])
    atkr_name, squad1 = f.battlequeue[0]
    squad2 = f.get_defenders()
    #TODO rewrite player and hex_battle
    atkr = Player(atkr_name, [squad1])
    dfndr = Player(f.owner, [squad2])
    game = Game(player1=atkr, player2=dfndr,
                battlefield=Battlefield(f.grid, squad1, squad2))
    btl = game.battlefield
    #obviously for testing only.
    for s in btl.squads: #location wonkiness in hex_battlefield.
        for u in s:
            u.location = Loc(None, None)
    for s in xrange(2):
        l = len(btl.squads[s])
        for x in xrange(l):
            btl.place_object(btl.squads[s][x], Loc(x, s))
    
    game.log['init_locs'] = game.log.init_locs()
    static_path = "./web"
    application = cyclone.web.Application([
                    (r"/", BattleHandler),
                    (r"/last_state", LastStateHandler),
                    (r"/static/(.*)", cyclone.web.StaticFileHandler, {"path": static_path}),
                  ],
    zeo = zeo,
    template_path = "./web",
    game = game,
    static_path = static_path,
    debug=True,
    login_url="/auth/login",
    cookie_secret="secret!!!!"
    )
    
    reactor.listenTCP(8890, application)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    main()
