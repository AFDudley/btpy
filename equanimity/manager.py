import sys

from ZEO import ClientStorage
from ZODB import DB

from twisted.python import log
from twisted.internet import reactor
from twisted.web import static, proxy, server
from equanimity.world_zeo import World_zeo
import field_server
import battle_server
import auth_server

        
class Manager():
    """Starts and monitors all the services required for a game equanimity."""
    #TODO using twisted and subprocess/multiprocess seems redundant.
    

    def worker(self, cmd, args):
        def sub_proc(cmd, args):
            while True: subprocess.call(cmd(args))
        return multiprocessing.Process(target=sub_proc, args=(cmd, args))
        
    def get_next_port(self):
        self.next_port += 1
        return self.next_port
        
    def make_children(self, name, ):
        pass
        
    def add_child(self, name, ip, port):
        return self.root.putChild(name, proxy.ReVerseProxyResource(ip, port, ''))

    def __init__(self, host='127.0.0.1', zeo_host='127.0.0.1', zeo_port='9100'):
        self.host = host
        self.next_port = int(zeo_port)
        self.world_zeo = World_zeo((zeo_host, zeo_port))
        self.site_root = static.File("./web")
        self.site = server.Site(self.site_root)
        self.workers = {}
        

def main():
    site = setup(sys.argv[1])
    reactor.listenTCP(8888, site)
    reactor.run()

if __name__ == "__main__":
    #log.startLogging(sys.stdout)
    log.startLogging(open('logs/manager.log', 'a'))
    main()    