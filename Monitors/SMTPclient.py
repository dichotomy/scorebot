#!/usr/bin/env python2

import sys
import time

from twisted.internet import reactor, protocol

from GenSocket import GenCoreFactory
from common import errormsg, no_unicode


class SMTPClient(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.job_id = self.factory.get_job_id()
        self.fqdn = "mail.scorebot.prosversusjoes.net"
        self.addr = self.factory.get_ip()
        self.port = self.factory.get_port()
        self.request = "HELO %s\n" % self.fqdn
        self.recv = ""

    def TimedOut(self):
        self.transport.loseConnection()
        self.factory.add_fail("timeout")

    def connectionMade(self):
        if self.job_id:
            print "Job %s: Made connection to %s:%s" % \
                (self.job_id, self.factory.get_ip(), self.factory.get_port())
        else:
            print "Made connection to %s:%s" % \
                (self.factory.get_ip(), self.factory.get_port())

    def dataReceived(self, data):
        self.recv += data
        print "Job %s: Received %s" % (self.job_id, data)
        self.factory.add_data(data)
        sys.stderr.write(data)
        if "220" in data and "SMTP" in data:
            print "Job %s: Sending %s" % (self.job_id, self.request)
            self.transport.write(no_unicode(self.request))
            return
        elif "250" in data:
            self.transport.loseConnection()

class SMTPFactory(GenCoreFactory):

    def __init__(self, params, job, service):
        GenCoreFactory.__init__(self)
        self.params = params
        self.job = job
        self.job_id = self.job.get_job_id()
        self.fqdn = self.job.get_fqdn()
        self.ip = self.job.get_ip()
        self.service = service
        self.fqdn = self.job.get_fqdn()

    def buildProtocol(self, addr):
        self.addr = addr
        self.start = time.time() # TODO is this used?!?!?!
        return SMTPClient(self)

    def check_service(self):
        connector = reactor.connectTCP(self.job.get_ip(),
                                       self.service.get_port(),
                                       self,
                                       self.params.timeout)
        deferred = self.get_deferred(connector)
        deferred.addCallback(self.service_pass)
        deferred.addErrback(self.service_fail)

    # TODO is reason needed for twisted?
    def service_pass(self, reason):
        self.service.pass_conn()
        print "Job %s: Successfully checked SMTP connection for %s(%s)" % \
            (self.job_id, self.fqdn, self.ip)

    def service_fail(self, failure):
        self.service.pass_conn(failure)
        errormsg("Job %s: Failed check of SMTP connection for %s(%s)" % \
            (self.job_id, self.fqdn, self.ip))

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            errormsg("Job %s: clientConnectionFailed:" % self.job.get_job_id())
            errormsg("reason %s" % reason)
            errormsg("self.reason: %s" % self.reason)
        conn_time = None
        if self.start:
            conn_time = self.end - self.start
        else:
            self.service.timeout(self.data)
            return
        self.deferreds[connector].errback(reason)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            errormsg("Job %s: clientConnectionLost" % self.job.get_job_id())
            errormsg("given reason: %s" % reason)
            errormsg("self.reason: %s" % self.reason)
        if self.data:
            self.service.set_data(self.data)
        if self.fail and self.reason:
            self.service.fail_conn(self.reason, self.data)
            self.deferreds[connector].errback(reason)
        elif self.fail and not self.reason:
            self.service.fail_conn(reason.getErrorMessage(), self.data)
            self.deferreds[connector].errback(reason)
        elif "non-clean" in reason.getErrorMessage():
            self.service.fail_conn("other", self.data)
            self.deferreds[connector].errback(reason)
        else:
            self.service.pass_conn()
            self.deferreds[connector].callback(self.job.get_job_id())

