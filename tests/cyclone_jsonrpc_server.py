import sys
import base64
import functools

import cyclone.web
import cyclone.redis

from twisted.python import log
from twisted.internet import reactor, defer

from binary_tactics.hex_battle import *
from stores.yaml_store import *
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.player import Player

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
        err = self._get_argument("e", None)
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
        password = hashlib.md5(p).hexdigest() #If I actaully cared I would do this client-side or via ssl.
        try:
            password = yield self.settings.redis.get("cyclone:%s" % usr)
            log.err("User already exists")
            raise cyclone.web.HTTPError(400, "User already Exists")
        except Exception, e:
            yield self.settings.redis.set("cyclone:%s" % u, password.encode("utf-8"))
        
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
            #user = yield self.settings.mongo.mydb.users.find_one({"u":u, "p":password}, fields=["u"])
            stored_pw = yield self.settings.redis.get("cyclone:%s" % usr)
            assert password == stored_pw
        except Exception, e:
            log.err("Login Failed")
            raise cyclone.web.HTTPError(503)
        
        if user:
            user["_id"] = str(user["_id"])
            self.set_secure_cookie("user", cyclone.escape.json_encode(user))
            self.redirect("/")
        else:
            self.redirect("/auth/login?e=invalid")
        
class LogoutHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")

class BattleHandler(BaseJSONHandler):
    @defer.inlineCallbacks
    def jsonrpc_process_action(self, args):
        #obviously this needs to be more robust.
        #so nasty.
        action = Action(eval(args[0]), args[1], eval(args[2]))
        result = yield game.process_action(action)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def jsonrpc_get_state(self):
        state = yield game.state
        defer.returnValue(state)

    @defer.inlineCallbacks
    def jsonrpc_initial_state(self):
        init_state = yield game.initial_state()
        defer.returnValue(str(init_state))

def main():
    redis = cyclone.redis.lazyRedisConnectionPool()
    application = cyclone.web.Application([
        (r"/", MainHandler),
        (r"/signup", SignupHandler),
        (r"/auth/login", LoginHandler),
        (r"/auth/logout", LogoutHandler),
        (r"/battle", BattleHandler),
    ],
    redis=redis)
    
    reactor.listenTCP(8888, application)
    reactor.run()
    
if __name__ == "__main__":
    #battle setup.
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
    print game.state
    log.startLogging(sys.stdout)
    main()
