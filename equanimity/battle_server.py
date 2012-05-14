'''
TODO:
    write world_server that calls this dynamically.
    Write a serializing wrapper around battle.
    Filter information based on authenticated player.
    write frontend.
'''
import sys
from datetime import datetime, timedelta
import json
import cyclone.web

from twisted.python import log
from twisted.internet import reactor, defer, task

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
    def jsonrpc_get_username(self):
        """Takes a cookie and returns the username encoded within it."""
        username = yield self.get_current_user().strip('"')
        defer.returnValue(username)
    
    @defer.inlineCallbacks
    def jsonrpc_initial_state(self):
        #needs to filter 
        if self.settings.init_state == None:
            self.settings.init_state = \
            yield get_persisted(self.settings.game.initial_state())
        defer.returnValue(self.settings.init_state)
    
    @defer.inlineCallbacks
    def jsonrpc_get_state(self):
        state = yield self.settings.game.last_state()
        defer.returnValue(state)
    
    @defer.inlineCallbacks
    def jsonrpc_game_log(self):
        log = yield self.settings.game.log
        defer.returnValue(str(log))
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_process_action(self, args):
        err = self.get_argument("e", None)
        username = self.get_current_user().strip('"')
        try:
            units = self.settings.game.units
            unit_num = int(args[0])
            unit_owner = self.settings.game.log.get_owner(unit_num).name
            if username == unit_owner:
                action = Action(units[unit_num], args[1], tuple(args[2]))
                result = yield self.settings.game.process_action(action)
                self.settings.last_state = self.settings.game.last_state()
                defer.returnValue(result)
            else:
                raise Exception("user cannot command unit, try a different unit.")
                
        except Exception , e:
            log.err("process_action failed: %r" % e)
            raise cyclone.web.HTTPError(500, "%r" % e.args[0])
    
class LastStateHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write(self.settings.last_state)
        self.flush()

class TimeLeftHandler(cyclone.web.RequestHandler):
    #DOS prevention needs to be added.
    #should be optimized for accuracy. 
    def get(self):
        art = self.settings.ART
        now = datetime.utcnow()
        timeleft = {'battle': str(art - now), 'ply': 'N/A'}
        self.write(str(timeleft))
        self.flush()
        
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
    #maxsecs = timedelta(0, 30) #for testing only 
    maxsecs = timedelta(0, world['resigntime'])
    #this copy is really important, copies the objects out of the zeo and into memory.
    f = copy.deepcopy(world['Fields'][str(sys.argv[1])])
    atkr_name, atksquad = f.battlequeue[0]
    defsquad = f.get_defenders()
    #TODO rewrite player and hex_battle
    dfndr = Player(f.owner, [defsquad])
    atkr = Player(atkr_name, [atksquad])
    game = Game(defender=dfndr, attacker=atkr
                battlefield=Battlefield(f.grid, defsquad, atksquad))
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
    start_time  = datetime.strptime(game.log['start_time'], "%Y-%m-%d %H:%M:%S.%f")
    ART = start_time + maxsecs #attacker resign time
    static_path = "./web"
    application = cyclone.web.Application([
                    (r"/", BattleHandler),
                    (r"/last_state.json", LastStateHandler),
                    (r"/time_left.json", TimeLeftHandler),
                    (r"/static/(.*)", cyclone.web.StaticFileHandler, {"path": static_path}),
                  ],
    zeo=zeo,
    template_path="./web",
    game=game,
    ART=ART,
    static_path=static_path,
    debug=True,
    login_url="/auth/login",
    cookie_secret="secret!!!!",
    last_state='{}',
    init_state=None,
    )
    def forcedpass(player):
        game.process_action(Action(None, 'timed_out', None))
        
    def endgame():
        """ends the game"""
        try:
            game.winner = game.player2
            game.end("Player1 failed to defeat Player2 in time.")
        except:
            #push log to transaction store.
            reactor.stop()
    
    reactor.listenTCP(8890, application)
    # is there a better way to do this, this will always be late.
    task.deferLater(reactor, maxsecs.seconds, endgame) 
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    main()
