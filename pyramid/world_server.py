from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from datetime import datetime

from equanimity.zeo import Zeo

from copy import deepcopy

class AuthHandler(object):
    def __init__(self, world):
        self.world = world
        
    def view(self, request, action):
        return Response(str(self.world['Players']['World'].username))
        
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
    auth = AuthHandler(wr)
    players = PlayerHandler(wr)
    config = Configurator()
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
    config.add_route('auth', '/auth/{action}')
    config.add_view(auth.view, route_name='auth')
    config.add_route('players', '/players/*action')
    config.add_view(players.view, route_name='players')
    app = config.make_wsgi_app()
    
    server = make_server('0.0.0.0', 9090, app)
    server.serve_forever()