#!/usr/bin/env python2
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from twisted.internet.defer import Deferred
from GenSocket import GenCoreFactory
import time
import sys


class SMTPClient(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.job_id = self.factory.get_job_id()
        self.fqdn = "mail.scorebot.prosversusjoes.net"
        self.addr = self.factory.get_ip()
        self.port = self.factory.get_port()
        self.request = "HELO %s\n" % self.fqdn
        self.recv = ""

    def no_unicode(self, text):
        #sys.stderr.write("\nJob %s: Converting %s" % (self.job_id, text))
        if isinstance(text, unicode):
            return text.encode('utf-8')
        else:
            return text

    def TimedOut(self):
        self.transport.loseConnection()
        self.factory.add_fail("timeout")

    def connectionMade(self):
        if self.job_id:
            sys.stderr.write("Job %s: Made connection to %s:%s\n" % (self.job_id, self.factory.get_ip(), self.factory.get_port()))
        else:
            sys.stderr.write("Made connection to %s:%s\n" % (self.factory.get_ip(), self.factory.get_port()))
        #sys.stderr.write("Sending: %s\n" % self.request)

    def dataReceived(self, data):
        data_len = len(data)
        self.recv += data
        sys.stderr.write("Job %s: Received %s" % (self.job_id, data))
        self.factory.add_data(data)
        sys.stderr.write(data)
        if "220" in data and "SMTP" in data:
            sys.stderr.write("Job %s: Sending %s" % (self.job_id, self.request))
            self.transport.write(self.no_unicode(self.request))
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
        self.start = time.time()
        return SMTPClient(self)

    def check_service(self):
        connector = reactor.connectTCP(self.job.get_ip(), self.service.get_port(), self, self.params.get_timeout())
        deferred = self.get_deferred(connector)
        deferred.addCallback(self.service_pass)
        deferred.addErrback(self.service_fail)

    def service_pass(self, reason):
        self.service.pass_conn()
        sys.stdout.write("Job %s: Successfully checked SMTP connection for %s(%s)\n" % (self.job_id, self.fqdn, self.ip))

    def service_fail(self, failure):
        self.service.pass_conn(failure)
        sys.stdout.write("Job %s: Failed check of SMTP connection for %s(%s)\n" % (self.job_id, self.fqdn, self.ip))

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write("Job %s: clientConnectionFailed:\t" % self.job.get_job_id())
            sys.stderr.write("reason %s\t" % reason)
            sys.stderr.write("self.reason: %s\t" % self.reason)
            sys.stderr.write("\nReceived: %s\n" % self.get_server_headers())
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
            sys.stderr.write("Job %s: clientConnectionLost\t" % self.job.get_job_id())
            sys.stderr.write("given reason: %s\t" % reason)
            sys.stderr.write("self.reason: %s\t" % self.reason)
            #sys.stderr.write("\nReceived: %s\n" % self.get_server_headers())
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

