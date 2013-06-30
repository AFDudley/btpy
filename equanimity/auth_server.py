import sys
import cyclone.web
from twisted.python import log
from twisted.internet import reactor, defer
from equanimity.zeo import Zeo

class BaseHandler(cyclone.web.RequestHandler):
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
            <html><body><form action="/auth/signup" method="post">
            Desired username: <input type="text" name="u"></br>
            password: <input type="password" name="p"></br>
            <input type="submit" value="Signup"></br>
            %s
            </body></html>
            """ % (err == "invalid" and "invalid username or password" or ""))
    
    @defer.inlineCallbacks
    def post(self):
        u = self.get_argument("u")
        password = self.get_argument("p")
        try:
            assert self.settings.zeo.get_password(u)
            log.err("User already exists")
            raise cyclone.web.HTTPError(400, "User already Exists")
        
        except Exception, e:
            self.settings.zeo.set_username(u, password.encode("utf-8"))
            #This should have redirected to login, not returned a cookie :(
            self.set_secure_cookie("user", cyclone.escape.json_encode(u))
            #self.redirect("/")
    
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
        password = self.get_argument("p")
        try:
            stored_pw = yield self.settings.zeo.get_password(u)
            assert password == stored_pw
                
        except Exception, e:
            log.err("Login Failed: %r" % e)
            self.write('{"login": "failed"}')
            self.flush()
            raise cyclone.web.HTTPError(503)
        
        if u:
            self.set_secure_cookie("user", cyclone.escape.json_encode(u))
            self.write('{"login": "successful"}')
            self.flush()
        else:
            self.redirect("/auth/login?e=invalid")
        
class LogoutHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.clear_cookie("user")
        #self.redirect("/")
    
def main():
    zeo = Zeo()
    static_path = "./web"
    application = cyclone.web.Application([
        (r"/static/(.*)", cyclone.web.StaticFileHandler, {"path": static_path}),
        #proxied handlers
        (r"/signup", SignupHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
    ],
    zeo=zeo,
    static_path = static_path,
    debug=True,
    login_url="/auth/login",
    cookie_secret="secret!!!!"
    )
    
    reactor.listenTCP(8889, application)
    reactor.run()

if __name__ == "__main__":    
    log.startLogging(open('logs/auth.log', 'a'))
    main()
