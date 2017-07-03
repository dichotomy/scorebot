#!/usr/bin/env python2
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from twisted.internet.defer import Deferred
from http_parser.pyparser import HttpParser
from Parameters import Parameters
from Jobs import Jobs
import time
import sys
import re

class GenClient(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.job_id = self.factory.get_job_id()
        reactor.callLater(self.factory.get_timeout(), self.TimedOut)
        # todo - add the ability to pass data for the client to transmit to the server
        self.request = None

    def TimedOut(self):
        self.factory.add_fail("timeout")
        self.transport.loseConnection()

    def connectionMade(self):
        if self.job_id:
            sys.stderr.write("Job %s: Made connection to %s:%s\n" % (self.job_id, self.factory.get_ip(), self.factory.get_port()))
        else:
            sys.stderr.write("Made connection to %s:%s\n" % (self.factory.get_ip(), self.factory.get_port()))
        reactor.callLater(self.factory.get_timeout(), self.TimedOut)
        #sys.stderr.write("Sending: %s\n" % self.request)
        if self.request:
            self.transport.write("%s\r\n" % self.request)
        else:
            self.factory.add_data("Simple socke connected, now terminating.\n")
            self.transport.loseConnection()

    def dataReceived(self, data):
        self.recv += data
        self.factory.add_data(data)
        # todo - How do we know when to stop receiving data?
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

    def get_deferred(self, key):
        deferred = Deferred()
        # We use the connect object returned by reactor.connectTCP() as our key.
        # This is ugly as fuck, but it works.
        self.deferreds[key] = deferred
        return deferred

    def startedConnecting(self, connector):
        if self.job:
            sys.stderr.write("Job %s:  Starting connection test\n" % self.job.get_job_id())

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

    def get_conn_id(self):
        return self.conn_id

    def get_ip(self):
        return self.ip

    def get_fqdn(self):
        return self.fqdn

    def get_port(self):
        return self.port

    def get_debug(self):
        return self.debug

    def get_job_id(self):
        return None

class GenCheckFactory(GenCoreFactory):

    def __init__(self, params, job, service):
        GenCoreFactory.__init__(self)
        self.job = job
        self.params = params
        self.service = service
        self.ip = job.get_ip()
        self.port = self.service.get_port()
        self.timeout = self.params.get_timeout()

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
            sys.stderr.write( "Job %s: clientConnectionFailed:\t" % self.job.get_job_id())
            sys.stderr.write( "reason %s\t" % reason)
            sys.stderr.write( "self.reason: %s\t" % self.reason)
            if self.debug:
                sys.stderr.write( "\nReceived: %s\n" % self.get_server_headers())
        conn_time = None
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
            sys.stderr.write( "Job %s: clientConnectionLost\t" % self.job.get_job_id())
            sys.stderr.write( "given reason: %s\t" % reason)
            sys.stderr.write( "self.reason: %s\t" % self.reason)
            if self.debug:
                sys.stderr.write( "\nReceived: %s\n" % self.get_server_headers())
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

if __name__ == "__main__":
    from twisted.python import log
    from DNSclient import DNSclient
    from WebClient import JobFactory
    import sys

    def post_job(job_id):
        factory = JobFactory(params, jobs, "put", job_id)
        reactor.connectTCP(params.get_sb_ip(), params.get_sb_port(), factory, params.get_timeout())

    def check_web(result, params, job):
        print "Got %s %s %s" % (result, params, job)
        print "Checking services for %s" % job.get_ip()
        for service in job.get_services():
            factory = WebServiceCheckFactory(params, job, service)
            deferred = factory.get_deferred()
            deferred.addCallback(post_job)
            reactor.connectTCP(job.get_ip(), service.get_port(), factory, params.get_timeout())

    def dns_fail(failure, job):
        jobid = job.get_job_id()
        print "DNS Failed for job %s! %s" % (jobid, failure)
        job.set_ip("fail")
        raise Exception("Fail Host")

    def job_fail(failure, job):
        jobid = job.get_job_id()
        print "job %s Failed! %s" % (jobid, failure)
        print job.get_json_str()
        post_job(jobid)
        return True

    def check_job(params, jobs):
        job = jobs.get_job()
        if job:
            #DNS?
            dnsobj = DNSclient(job, 3)
            # Execute the query
            query_d = dnsobj.query()
            # Handle a DNS failure - fail the host
            query_d.addErrback(dns_fail, job)
            # Handle a DNS success - move on to ping
            query_d.addCallback(check_web, params, job)
            query_d.addErrback(job_fail, job)

    log.startLogging(open('log/gensockettest.log', 'w'))
    jobs = Jobs()
    sys.stderr.write( "Testing %s\n" % sys.argv[0])
    params = Parameters()
    factory = JobFactory(params, jobs, "get")
    reactor.connectTCP(params.get_sb_ip(), params.get_sb_port(), factory, params.get_timeout())
    reactor.callLater(5, check_job, params, jobs)
    reactor.callLater(30, reactor.stop)
    reactor.run()
    print "Finished normally"

