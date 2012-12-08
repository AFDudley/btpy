"""Reverse proxy server for aggregating Equnimity services."""
import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.web import static, proxy, server

"""lovingly jacked from: http://leonardinius.galeoconsulting.com/2012/07/testing-ajax-crossdomain-issue-python-to-rescue/"""
path = "./web"  # path to static resources (html, js etc..)
root = static.File(path)     # will be served under '/'
ip = '127.0.0.1'
# http://166.84.136.68:8888/auth redirects to http://166.84.136.68:8889/
root.putChild('auth', proxy.ReverseProxyResource(ip, 8889, ''))
 
# http://166.84.136.68:8888/battle redirects to http://166.84.136.68:8890/
root.putChild('battle', proxy.ReverseProxyResource(ip, 8890, ''))

def main():
    site = server.Site(root)
    reactor.listenTCP(8888, site)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    main()