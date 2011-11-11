import sys
import base64
import functools
import hashlib

import cyclone.web
import cyclone.redis

from twisted.python import log
from twisted.internet import reactor, defer

from equanimity.world import wPlayer
from ZEO import ClientStorage
from ZODB import DB
import transaction

class BaseHandler(cyclone.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
class BaseJSONHandler(cyclone.web.JsonrpcRequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
class MainHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.write('great! <a href="/auth/logout">logout</a>')

class SignupHandler(BaseHandler):
    def get(self):
        err = self.get_argument("e", None)
        self.finish("""
            <html><body><form action="/signup" method="post">
            Desired username: <input type="text" name="u"></br>
            password: <input type="password" name="p"></br>
            <input type="submit" value="Signup"></br>
            %s
            </body></html>
            """ % (err == "invalid" and "invalid username or password" or ""))
        
    @defer.inlineCallbacks
    def post(self):
        u = self.get_argument("u")
        p = self.get_argument("p")
        password = hashlib.md5(p).hexdigest() #NOT SECURE!!!
        try:
            assert self.settings.zeo.get(u)
            log.err("User already exists")
            raise cyclone.web.HTTPError(400, "User already Exists")
        
        except Exception, e:
            self.settings.zeo.set(u, password.encode("utf-8"))
            self.set_secure_cookie("user", cyclone.escape.json_encode(u))
            self.redirect("/")
                
class LoginHandler(BaseHandler):
    def get(self):
        err = self.get_argument("e", None)
        self.finish("""
            <html><body><form action="/auth/login" method="post">
            username: <input type="text" name="u"><br>
            password: <input type="password" name="p"><br>
            <input type="submit" value="sign in"><br>
            %s
            </body></html>
        """ % (err == "invalid" and "invalid username or password" or ""))
        
    @defer.inlineCallbacks
    def post(self):
        u = self.get_argument("u")
        p = self.get_argument("p")
        password = hashlib.md5(p).hexdigest()
        try:
            stored_pw = yield self.settings.zeo.get(u)
            assert password == stored_pw
                
        except Exception, e:
            log.err("Login Failed: %r" % e)
            raise cyclone.web.HTTPError(503)
        
        if u:
            self.set_secure_cookie("user", cyclone.escape.json_encode(u))
            self.redirect("/")
        else:
            self.redirect("/auth/login?e=invalid")
        
class LogoutHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")

class BattleHandler(BaseJSONHandler):
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def jsonrpc_register(self):
        """Takes a cookie and registers it in a battlefield."""
        current_user = yield self.get_current_user()
        defer.returnValue(current_user)
        
    @defer.inlineCallbacks
    def jsonrpc_initial_state(self):
        init_state = yield game.initial_state()
        defer.returnValue(str(init_state))
        
    @defer.inlineCallbacks
    def jsonrpc_get_state(self):
        state = yield game.state
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
            result = yield game.process_action(action)
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
    zeo = Zeo()
    application = cyclone.web.Application([
        (r"/", MainHandler),
        (r"/signup", SignupHandler),
        (r"/auth/login", LoginHandler),
        (r"/auth/logout", LogoutHandler),
        (r"/battle", BattleHandler),
    ],
    zeo = zeo,
    login_url="/auth/login",
    cookie_secret="secret!!!!"
    )
    
    reactor.listenTCP(8888, application)
    reactor.run()

if __name__ == "__main__":    
    #battle setup.
    from binary_tactics.hex_battle import *
    from stores.yaml_store import *
    from binary_tactics.hex_battlefield import Battlefield
    from binary_tactics.player import Player
    p1   = Player(name='p1', squads=[load('yaml/ice_maxes.yaml')])
    p2   = Player(name='p2', squads=[load('yaml/fire_maxes.yaml')])
    game = Game(player1=p1, player2=p2,
                battlefield=Battlefield(squad1=p1.squads[0],
                squad2=p2.squads[0]),)
    btl = game.battlefield
    
    for s in range(2):
        for x in range(4):
            btl.place_object(btl.squads[s][x], defs.Loc(x, s))
    
    game.log['init_locs'] = game.log.init_locs()
    log.startLogging(sys.stdout)
    main()
    
