from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid_rpc.jsonrpc import jsonrpc_method

@jsonrpc_method(endpoint='api')
def say_hello(request, name):
    #return str(request) + " " + str(name)
    return 'hello, %s!' % name

if __name__ == '__main__':
    config = Configurator()
    config.include('pyramid_rpc.jsonrpc')
    config.add_jsonrpc_endpoint('api', '/api')
    config.scan()
    app = config.make_wsgi_app()
    
    server = make_server('0.0.0.0', 9090, app)
    server.serve_forever()