#!/usr/bin/env python2

import time

from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred

from common import errormsg


class GenClient(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.job_id = self.factory.get_job_id()
        reactor.callLater(self.factory.get_timeout(), self.TimedOut)
        # TODO add the ability to pass data for the client to transmit to the server
        self.request = None

    def TimedOut(self):
        self.factory.add_fail("timeout")
        self.transport.loseConnection()

    def connectionMade(self):
        if self.job_id:
            print "Job %s: Made connection to %s:%s" % \
                (self.job_id, self.factory.get_ip(), self.factory.get_port())
        else:
            print "Made connection to %s:%s" % \
                (self.factory.get_ip(), self.factory.get_port())
        reactor.callLater(self.factory.get_timeout(), self.TimedOut)
        if self.request:
            self.transport.write("%s\r\n" % self.request)
        else:
            self.factory.add_data("Simple socket connected, now terminating.\n")
            self.transport.loseConnection()

    def dataReceived(self, data):
        self.recv += data
        self.factory.add_data(data)
        # TODO How do we know when to stop receiving data?
        # We shouldn't just close the connection after some data.
        self.transport.loseConnection()

class GenCoreFactory(protocol.ClientFactory):

    def __init__(self):
        self.fail = False
        self.reason = None
        self.start = None
        self.end = None
        self.debug = False
        self.data = ""
        self.addr = None
        self.deferreds = {}
        self.fqdn = ""
        self.port = 0
        self.timeout = 30
        self.noisy = False

    def get_deferred(self, key):
        deferred = Deferred()
        # We use the connect object returned by reactor.connectTCP() as our key.
        # This is ugly as fuck, but it works.
        self.deferreds[key] = deferred
        return deferred

    def startedConnecting(self, connector):
        if self.job:
            print "Job %s:  Starting connection" % self.job.get_job_id()

    def buildProtocol(self, addr):
        self.addr = addr
        self.start = time.time()
        return GenClient(self)

    def add_data(self, data):
        self.data += data

    def add_fail(self, reason):
        self.reason = reason
        self.fail = True

    def get_conn_id(self):
        return self.conn_id

    def get_timeout(self):
        return self.timeout

    def get_ip(self):
        return self.ip

    def get_fqdn(self):
        return self.fqdn

    def get_port(self):
        return self.port

    def get_debug(self):
        return self.debug

    # TODO is this used?!~
    @staticmethod
    def get_job_id():
        return None

class GenCheckFactory(GenCoreFactory):

    def __init__(self, params, job, service):
        GenCoreFactory.__init__(self)
        self.job = job
        self.params = params
        self.service = service
        self.ip = job.get_ip()
        self.port = self.service.get_port()
        self.timeout = self.job.get_timeout()

    def add_fail(self, reason):
        if "timeout" in reason:
            self.service.timeout("General socket connection failure")
        else:
            self.service.fail_conn(reason, "%s\r\n%s" % (self.get_server_headers(), self.body))

    def get_job_id(self):
        return self.job.get_job_id()

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            errormsg("Job %s: clientConnectionFailed:" % self.job.get_job_id())
            errormsg("reason %s" % reason)
            errormsg("self.reason: %s" % self.reason)
            if self.debug:
                errormsg("\nReceived: %s\n" % self.get_server_headers())
        conn_time = None # TODO is this used?!
        if self.start:
            conn_time = self.end - self.start
        else:
            self.service.timeout(self.data)
            return
        self.service.fail_conn(reason.getErrorMessage(), self.data)
        self.deferreds[connector].errback(reason)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            errormsg("Job %s: clientConnectionLost" % self.job.get_job_id())
            errormsg("given reason: %s" % reason)
            errormsg("self.reason: %s" % self.reason)
            if self.debug:
                errormsg("\nReceived: %s\n" % self.get_server_headers())
        conn_time = self.end - self.start
        if self.data:
            self.service.set_data(self.data)
        if self.fail and self.reason:
            self.service.fail_conn(self.reason, self.data)
        elif self.fail and not self.reason:
            self.service.fail_conn(reason.getErrorMessage(), self.data)
        elif "non-clean" in reason.getErrorMessage():
            self.service.fail_conn("other", self.data)
        else:
            self.service.pass_conn()
            self.deferreds[connector].callback(self.job.get_job_id())

