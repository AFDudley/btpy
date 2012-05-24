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

#For testing
from os import fork

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
        print "username: %s" %username
        print "whose_turn: %s " %self.settings.game.whose_turn.name
        try:
            if username != self.settings.game.whose_turn.name:
                raise Exception("It is not your turn.")
            units = self.settings.game.units
            unit_num = int(args[0])
            unit_owner = self.settings.game.log.get_owner(unit_num).name
            if username == unit_owner:
                action = Action(units[unit_num], args[1], tuple(args[2]))
                self.settings.last_result = result = yield self.settings.game.process_action(action)
                self.settings.ply_timer.call.reset(self.settings.ply_time)
                self.settings.last_state  = self.settings.game.last_state()
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
        
class LastResultHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write(self.settings.last_result)
        self.flush()
        
class TimeLeftHandler(cyclone.web.RequestHandler):
    #DOS prevention needs to be added.
    #should be optimized for accuracy. 
    def get(self):
        now = datetime.utcnow()
        ply = datetime.utcfromtimestamp(self.settings.ply_timer.call.getTime())
        timeleft = {'battle': str(self.settings.ART - now), 'ply': str(ply - now)}
        self.write(str(timeleft))
        self.flush()

       
        
class World_zeo(object):
    def __init__(self, addr=('localhost', 9100)):
        self.addr = addr
        self.storage = ClientStorage.ClientStorage(self.addr)
        self.db = DB(self.storage)
        self.conn = self.db.open()
        self.root = self.conn.root()
        
def main():
    def write_battlelog():
        """writes the battle log to persistent storage."""
        print "writing battle log here."
        addr = 'localhost', 9101
        storage = ClientStorage.ClientStorage(addr)
        db = DB(storage)
        conn = db.open()
        logs = conn.root()
        
        '''logs should be indexed by a hash of starttime and
           where the battle happened.'''
        logs['logs'].append(game.log)
        transaction.commit()
        print game.log['change_list']
        

    def ARTendgame():
        """ends the game"""
        try:
            game.winner = game.player2
            game.end("Player1 failed to defeat Player2 in time.")
        except:
            write_battlelog()
            reactor.stop()
            
    @defer.inlineCallbacks
    def forcedpass():
        try:
            print "Forced pass."
            action = Action(None, 'timed_out', None)
            app.settings.last_result = result = yield app.settings.game.process_action(action)
            app.settings.last_state  = app.settings.game.last_state()
        except Exception , e:
            if e.args[0] == 'Game Over':
                write_battlelog()
                reactor.stop()
                
    world_zeo = World_zeo()
    world  = world_zeo.root
    maxsecs = timedelta(0, world['resigntime'])
    #this copy is really important, copies the objects out of the zeo and into memory.
    f = copy.deepcopy(world['Fields'][str(sys.argv[1])])

    ply_time = f.ply_timer
    atkr_name, atksquad = f.battlequeue[0]
    defsquad = f.get_defenders()
    #TODO rewrite player and hex_battle
    dfndr = Player(f.owner, [defsquad])
    atkr = Player(atkr_name, [atksquad])
    game = Game(defender=dfndr, attacker=atkr,
                battlefield=Battlefield(f.grid, defsquad, atksquad))
    btl = game.battlefield
    #obviously for testing only.
    for squad in btl.squads: #location wonkiness in hex_battlefield.
        for unit in squad:
            unit.location = Loc(None, None)
    for s in xrange(2):
        l = len(btl.squads[s])
        for x in xrange(l):
            btl.place_object(btl.squads[s][x], Loc(x, s))

    game.log['init_locs'] = game.log.init_locs()
    start_time  = datetime.strptime(game.log['start_time'], "%Y-%m-%d %H:%M:%S.%f")
    ART = start_time + maxsecs #attacker resign time
    static_path = "./web"
    
    app = cyclone.web.Application([
                    (r"/", BattleHandler),
                    (r"/last_state.json", LastStateHandler),
                    (r"/last_result.json", LastResultHandler),
                    (r"/time_left.json", TimeLeftHandler),
                    (r"/static/(.*)", cyclone.web.StaticFileHandler, {"path": static_path}),
                  ],
    template_path="./web",
    game=game,
    ART=ART,
    static_path=static_path,
    debug=True,
    login_url="/auth/login",
    cookie_secret="secret!!!!",
    last_state='{}',
    last_result='{}',
    init_state=None,
    ply_time=ply_time,
    ply_timer=task.LoopingCall(forcedpass)
    )
    
    reactor.listenTCP(8890, app)
    # is there a better way to do this, this will always be late.
    task.deferLater(reactor, maxsecs.seconds, ARTendgame) 
    app.settings.ply_timer.start(ply_time, now=False)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    #log.startLogging(open('/home/rix/logs/battle_log.log', 'a'))
    main()
