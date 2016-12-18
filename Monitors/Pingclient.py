#!/usr/bin/env python2
from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred
import re

class PingProtocol(protocol.ProcessProtocol):

    def __init__(self, ipaddr):
        self.ipaddr = ipaddr
        self.data = ""
        self.received_re = re.compile("(\d) received")
        self.transmitted_re = re.compile("(\d) packets transmitted")
        self.recv = 0
        self.trans = 0
        self.d = Deferred()
        self.d.addCallback()

    def getDeferred(self):
        return self.d

    def outReceived(self, data):
        self.data += data

    def outConnectionLost(self):
        self.recv = int(self.received_re.search(self.data).group(1))
        self.trans = int(self.transmitted_re.search(self.data).group(1))
        self.d.callback()

    def get_recv(self):
        return self.recv

    def get_fail(self):
        return self.trans - self.recv

if __name__=="__main__":
    import sys
    ping = "/usr/bin/ping"
    ipaddr = sys.argv[1]
    count = str(5)
    pingproc = PingProtocol(ipaddr)
    reactor.spawnProcess(pingproc, ping, [ping, "-c", count, ipaddr])
    reactor.callLater(8, reactor.stop)
    reactor.run()
    print "Got %s good pings" % pingproc.get_recv()
    print "Got %s bad pings" % pingproc.get_fail()
