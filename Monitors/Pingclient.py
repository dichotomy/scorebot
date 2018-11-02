#!/usr/bin/env python2

import re
import sys

from Jobs import Jobs

from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred


class PingProtocol(protocol.ProcessProtocol):

    def __init__(self, job, count="5"):
        self.job = job
        self.ipaddr = self.job.get_ip()
        self.data = ""
        self.received_re = re.compile("(\d) received")
        self.transmitted_re = re.compile("(\d) packets transmitted")
        self.recv = 0
        self.fail = 0
        self.transmitted = 0
        self.deferred = Deferred()
        self.ping_prog = "/usr/bin/ping" # TODO `which` this
        self.count = count

    def ping(self):
        reactor.spawnProcess(self, self.ping_prog, [self.ping_prog, "-c", self.count, self.ipaddr])

    def outReceived(self, data):
        self.data += data

    def outConnectionLost(self):
        self.recv = int(self.received_re.search(self.data).group(1))
        self.transmitted = int(self.transmitted_re.search(self.data).group(1))
        self.lost = self.transmitted - self.recv
        self.job.set_ping_sent(self.transmitted)
        self.job.set_ping_respond(self.recv)
        self.ratio = self.recv / self.transmitted
        if 0 <= self.ratio <= 100:
            self.d.callback(self)
        else:
            self.d.errback()

