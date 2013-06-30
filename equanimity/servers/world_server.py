import sys
import multiprocessing
import subprocess
import cyclone.web
from twisted.python import log
from twisted.internet import reactor

from ZEO import ClientStorage
from ZODB import DB
import transaction
import worker

class BaseHandler(cyclone.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class WorldHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write("it works.")

class FieldHandler(cyclone.web.RedirectHandler):
    """routes messages to the correct field_worker."""
    def get(self, x, y):
        #print port.getHost()
        self.url = 'http://166.84.136.68:' + str(world_zeo.ports[x][y])
        #self.redirect(url, permanent=True)
        #self.write(str([x,y]))

class World_zeo(object):
    def make_ex(self):
        x = self.root['x']
        y = self.root['y']
        return r"/([0-%s])/([0-%s])" %(x,y)
    
    def work(self, args):
        print args
        while True: subprocess.call(worker.main(args))
    
    def make_workers(self):
        print "Adding workers."
        workers = {}
        ports = {}
        for x in xrange(self.root['x']):
            workers[x] = {}
            ports[x] = {}
            for y in xrange(self.root['y']):
                world_coords = '(%s, %s)' %(x,y)
                lport = self.get_next_port()
                ports[x][y] = lport
                args = [lport, self.addr, world_coords]
                workers[x][y] = multiprocessing.Process(target=self.work, args=(args,))
                workers[x][y].start()
                
                print "\tAdded worker: %s" %world_coords
        return workers, ports

    def __init__(self, addr=('localhost', 9100)):
        self.addr = addr
        self.storage = ClientStorage.ClientStorage(self.addr)
        self.db = DB(self.storage)
        self.conn = self.db.open()
        self.root = self.conn.root()
        self.regex = self.make_ex()
        self.next_port = self.addr[1]
        self.workers, self.ports = self.make_workers()
        
    def get_next_port(self):
        self.next_port += 1
        return self.next_port
    
    def make_handlers(self, handlers):
        """makes the hanlders for the workers."""
        for x in xrange(self.root['x']):
            for y in xrange(self.root['y']):
                url0 = r"/%s/%s/.*$" %(x,y)
                url1 = u"http://" + host + ":" + str(self.ports[x][y])
                handlers.append((url0, cyclone.web.RedirectHandler, {"url": url1}))

def main(args):
    global host
    host = args[0]

    global world_zeo
    world_zeo = World_zeo()
    handlers = [(r"/", WorldHandler)]
    world_zeo.make_handlers(handlers)
    app = cyclone.web.Application(handlers)
    print app.handlers
    reactor.listenTCP(8765, app, interface=host)
    reactor.run()
    
if __name__ == "__main__":
    log.startLogging(sys.stdout)
    try:
        sys.argv[1]
        main(sys.argv[1:])
    except:
        main(("0.0.0.0",))
        
