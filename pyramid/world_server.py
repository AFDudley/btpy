from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid_rpc.jsonrpc import jsonrpc_method
from datetime import datetime
from equanimity.zeo import Zeo
from copy import deepcopy

import hashlib
import transaction

class AuthHandler(object):
    def __init__(self, zeo):
        self.zeo = zeo
        self.world = zeo.root
    
    def signup(self, request):
        """Signup via json-rpc post"""
        #example: {"jsonrpc": "2.0", "method": "signup", "params": {"username": "tom", "password": "silly"}, "id": 1}
        try:
            username = request.rpc_args['username']
            password = request.rpc_args['password']
            if self.zeo.get_username(username):
                return {"error": "Already a user with that name."}
            else:
                p = hashlib.md5(password).hexdigest()
                p = p.encode("utf-8")
                print "password: %s \n hash: %s" %(password, p)
                self.zeo.set_username(str(username), p)
                request.response.set_cookie('user', value=p)
            return {"sucess": "Username created."}
        
        except Exception as e:
            error = str(e)
            print error
            if error == "'password'":
                message = 'signup requires password'
            elif error == "'username'":
                message = 'signup requires username'
            else:
                message = error
            return {"error": message}
    
    def login(self, request): pass
    def logout(self, request): pass
    """def view(self, request):
        action = request.matchdict['action'].lower()
        return Response(action)"""
        
class WorldHandler(object):
    def __init__(self, world):
        self.world = world
        
    def view(self, request, params):
        return Response(str(self.world))
    
class FieldHandler(object):
    def __init__(self, world, worldcoord):
        self.world = world
        self.field = deepcopy(self.world['Fields'][worldcoord])
            
    def view(self, request, params):
        action = params.matchdict['action']
        if len(action) > 0:
            lowered = action[0].lower()
            if lowered == 'stronghold':
                return Response(str(vars(self.field.stronghold)))
            elif lowered == 'battle':
                return Response(str(vars(self.field.game)))
            elif lowered == 'factories':
                return "fix me"
        else:
            return Response(str(self.field.owner))

class PlayerHandler(object):
    def __init__(self, world):
        self.world = world
    def view(self, request, params):
        stuff = params.matchdict['stuff']
        name = None
        attrib = None
        if len(stuff) > 0:
            name = stuff[0]
            if len(stuff) > 1:
                attrib = stuff[1]
            
            if attrib == None:
                player = deepcopy(self.world['Players'][name])
                return Response(str(player.__dict__))
            else:
                player = deepcopy(self.world['Players'][name])
                if attrib.lower() == 'fields':
                    info = {}
                    fields = player.Fields.keys()
                    for field in fields:
                        info[field] = self.world['Fields'][field].state
                    return Response(str(info))
        else:
            return Response(str(stuff.matchdict))

if __name__ == '__main__':

    zeo = Zeo()
    wr = zeo.root
    world = WorldHandler(wr)
    auth = AuthHandler(zeo)
    players = PlayerHandler(wr)
    config = Configurator()
    config.include('pyramid_rpc.jsonrpc')
    config.add_jsonrpc_endpoint('signup', '/auth/signup')
    config.add_jsonrpc_method(auth.signup, endpoint='signup', method='signup')
    #We don't need no sinking decorators.
    fieldhandlers = {}
    for x in xrange(wr['x']):
        fieldhandlers[x] = {}
        for y in xrange(wr['y']):
            worldcoord = str((x,y))
            fieldhandlers[x][y] = FieldHandler(wr, worldcoord)
            base =  str(x) + '/' + str(y)
            pattern = '/' + base + '/*action'
            config.add_route('%s/%s'%(x,y), pattern)
            config.add_view(fieldhandlers[x][y].view, route_name=base)
    
    config.add_route('world', '/world')
    config.add_view(world.view, route_name='world')
    config.add_route('players', '/players/*stuff')
    config.add_view(players.view, route_name='players')
    app = config.make_wsgi_app()
    
    server = make_server('0.0.0.0', 9090, app)
    server.serve_forever()