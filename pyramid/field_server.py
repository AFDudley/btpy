from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from datetime import datetime

def now():
    return datetime.utcnow()

global d
#works as expected. d = datetime(2013, 2, 24, 14, 11, 45, 57143)
d = datetime.utcnow() #works as expected

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

def time(request):
    return Response('The time is %s' %now())
    
def then(request):
    return Response('The time was %s' %d)

    
if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_view(hello_world, route_name='hello')
    config.add_route('time', '/time/')
    config.add_view(time, route_name='time')
    config.add_route('then', '/then/')
    config.add_view(then, route_name='then')
    app = config.make_wsgi_app()
    
    server = make_server('0.0.0.0', 9090, app)
    server.serve_forever()