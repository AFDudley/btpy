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
from cyclone import jsonrpc

from twisted.python import log
from twisted.internet import reactor, defer, task

from equanimity.world_zeo import World_zeo

#One day logs of battles will need to go into a database
#DO NOT UNCOMMENT.
#from binary_tactics.zodb_hex_battle import Game, Action
#from stores.zodb_store import get_persisted

import binary_tactics.stone
from equanimity.wstone import Stone
binary_tactics.stone.Stone = Stone #Monkey Patch

from binary_tactics.hex_battle import Game, Action
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.player import Player
from binary_tactics.grid import Loc

from stores.store import get_persisted
import copy

class BaseJSONHandler(jsonrpc.JsonrpcRequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
class BattleHandler(BaseJSONHandler):
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_get_username(self):
        """Takes a cookie and returns the username encoded within it."""
        username = yield self.get_current_user().strip('"')
        defer.returnValue(username)
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_initial_state(self):
        #needs to filter 
        if self.settings.init_state == None:
            self.settings.init_state = \
            yield get_persisted(self.settings.game.initial_state())
        defer.returnValue(self.settings.init_state)
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_get_states(self):
        state = yield self.settings.get_states
        defer.returnValue(state)
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_get_last_state(self):
        state = yield self.settings.get_last_state
        defer.returnValue(state)
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_last_result(self):
        result = yield self.settings.last_result
        defer.returnValue(result)
        
    @defer.inlineCallbacks
    def jsonrpc_time_left(self):
        now = datetime.utcnow()
        ply = datetime.utcfromtimestamp(self.settings.ply_timer.call.getTime())
        timeleft = yield {'battle': str(self.settings.ART - now), 'ply': str(ply - now)}
        defer.returnValue(timeleft)
        
    @defer.inlineCallbacks
    def jsonrpc_game_log(self): #FOR TESTING
        log = yield self.settings.game.log
        defer.returnValue(str(log))
        
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_process_action(self, args):
        err = self.get_argument("e", None)
        username = self.get_current_user().strip('"')
        print "username: %s" %username
        print "whose_action: %s " %self.settings.game.state['whose_action']
        try:
            if username != self.settings.game.state['whose_action']:
                raise Exception("It is not your turn.")
            else: #WIP.
                if args[1] == 'pass':
                    action = Action(None, 'pass', None)
                else:
                    unit_num = int(args[0])
                    unit_owner = self.settings.game.log.get_owner(unit_num).name
                    if username == unit_owner:
                        units = self.settings.game.units
                        action = Action(units[unit_num], args[1], tuple(args[2]))
                    else:
                        raise Exception("user cannot command unit, try a different unit.")
                self.settings.last_result = result = yield self.settings.game.process_action(action)
                #ply_timer needs to change when the ply changes.
                self.settings.ply_timer.call.reset(self.settings.ply_time)
                self.settings.get_states  = self.settings.game.get_states()
                self.settings.get_last_state = self.settings.game.get_last_state()
                print result
                defer.returnValue(result)
                    
        except Exception , e:
            #This code is buggy. must be fixed asap.
            if e.args[0] == 'Game Over':
                #change to correct state. (Harvest or Produce)
                #write_battlelog()
                reactor.stop()
                
            else:
                log.err("process_action failed: %r" % e)
                raise cyclone.web.HTTPError(500, "%r" % e.args[0])
            
class TimeLeftHandler(cyclone.web.RequestHandler):
    #DOS prevention needs to be added.
    #should be optimized for accuracy. 
    def get(self):
        now = datetime.utcnow()
        ply = datetime.utcfromtimestamp(self.settings.ply_timer.call.getTime())
        timeleft = {'battle': str(self.settings.ART - now), 'ply': str(ply - now)}
        self.write(str(timeleft))
        self.flush()
        
def main(args):
    coords, lport = args
    def write_battlelog():
        """writes the battle log to persistent storage."""
        print "writing battle log here."
        """addr = 'localhost', 9101
        storage = ClientStorage.ClientStorage(addr)
        db = DB(storage)
        conn = db.open()
        logs = conn.root()"""
        
        '''logs should be indexed by a hash of starttime and
           where the battle happened. ...or something
        '''
        game.log['world_coords'] = world_coords
        out = get_persisted(game.log)
        #print "out type %s" %type(out)
        ##logs['battle'][game.log['end_time']] = out
        #main.out = out
        ##transaction.commit()
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
            #print "Pass Count: %s" %(app.settings.game.state["pass_count"])
            action = Action(None, 'timed_out', None)
            app.settings.last_result = result = yield app.settings.game.process_action(action)
            app.settings.get_states  = app.settings.game.get_states()
            app.settings.get_last_state = app.settings.game.get_last_state()
        except Exception , e:
            if e.args[0] == 'Game Over':
                write_battlelog()
                reactor.stop()
                
    world_zeo = World_zeo()
    world  = world_zeo.root
    maxsecs = timedelta(0, world['resigntime'])
    world_coords = coords
    #this copy is really important, copies the objects out of the zeo and into memory.
    f = copy.deepcopy(world['Fields']['(0, 0)'])
    #f = copy.deepcopy(world['Fields'][world_coords])
    ply_time = 600 #for testing ending conditions
    #ply_time = f.ply_time
    atkr_name, atksquad = f.battlequeue[0]
    defsquad = f.get_defenders()
    #TODO rewrite player and hex_battle
    dfndr = Player(f.owner, [defsquad])
    atkr  = Player(atkr_name, [atksquad])
    game  = Game(grid=f.grid, defender=dfndr, attacker=atkr)
    btl   = game.battlefield

    #!!!obviously for testing only.
    #The locations should be pushed to world before battle is started.
    """
    for s in xrange(2):
        l = len(btl.squads[s])
        for x in xrange(l):
            btl.place_object(btl.squads[s][x], Loc(x, s))
    """
    #TODO CLEANUP
    for s in xrange(2):
        l = len(btl.squads[s])
        for x in xrange(l):
            loc = btl.squads[s][x].location
            btl.squads[s][x].location = None
            btl.place_object(btl.squads[s][x], loc)
            
    game.log['init_locs'] = game.log.init_locs()
    start_time  = datetime.strptime(game.log['start_time'], "%Y-%m-%d %H:%M:%S.%f")
    ART = start_time + maxsecs #attacker resign time
    static_path = "./web"
    
    app = cyclone.web.Application([
                    (r"/", BattleHandler),
                    (r"/time_left.json", TimeLeftHandler),
                    (r"/static/(.*)", cyclone.web.StaticFileHandler, {"path": static_path}),
                  ],
    gzip=True,
    template_path="./web",
    game=game,
    ART=ART,
    static_path=static_path,
    debug=True,
    login_url="/auth/login",
    cookie_secret="secret!!!!",
    last_state='{}',
    get_states='{}', #WRONG.
    last_result='{}',
    init_state=None,
    ply_time=ply_time,
    ply_timer=task.LoopingCall(forcedpass),
    reactor=None,
    )
    
    reactor.listenTCP(lport, app)
    # is there a better way to do this, this will always be late.
    app.reactor = reactor
    task.deferLater(reactor, maxsecs.seconds, ARTendgame) 
    app.settings.ply_timer.start(ply_time, now=False)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(open('logs/battle.log', 'a'))
    lport = 8890
    coords = str(sys.argv[1])
    args =(coords, lport)
    main(args)