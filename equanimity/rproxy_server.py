"""Reverse proxy server for aggregating Equnimity services."""
import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.web import static, proxy, server

"""lovingly jacked from: http://leonardinius.galeoconsulting.com/2012/07/testing-ajax-crossdomain-issue-python-to-rescue/"""
path = "/web"  # path to static resources (html, js etc..)
root = static.File(path)     # will be served under '/'

# reverse proxy, served under '/svc'
# http://test.company.com/service1/v1/JsonService -> becomes http://localhost/svc/service1/v1/JsonService
root.putChild('auth', proxy.ReverseProxyResource('166.84.136.68', 8889, ''))
root.putChild('battle', proxy.ReverseProxyResource('166.84.136.68', 8890, ''))

# the magic
def main():
    site = server.Site(root)
    reactor.listenTCP(8888, site)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    main()