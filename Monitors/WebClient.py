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

class WebClient(protocol.Protocol):

    def __init__(self, factory):
        self.parser = HttpParser()
        self.factory = factory
        self.verb = self.factory.get_verb()
        self.job_id = self.factory.get_job_id()
        if "POST" in self.verb:
            data = self.factory.get_postdata()
            headers = self.factory.get_headers()
            length = len(data)
            headers += "Content-Length: %s\r\n" % str(length)
            self.request = self.no_unicode("%s %s HTTP/1.0\r\n%s\r\n%s\r\n\r\n" % \
                           (self.verb, self.factory.get_url(), headers, data))
        else:
            self.request = self.no_unicode("%s %s HTTP/1.0\r\n%s\r\n\r\n" % \
                       (self.verb, self.factory.get_url(), self.factory.get_headers()))
        self.recv = ""
        self.body = ""

    def no_unicode(self, text):
        sys.stderr.write("Job %s: Converting %s" % (self.job_id, text))
        if isinstance(text, unicode):
            return text.encode('utf-8')
        else:
            return text

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
        self.transport.write("%s\r\n" % self.request)

    def dataReceived(self, data):
        data_len = len(data)
        self.recv += data
        self.factory.add_data(data)
        line = "="*80 + "\n"
        #sys.stderr.write(line)
        #sys.stderr.write("Received this response: \n\t%s\n" % self.recv)
        #sys.stderr.write(line)
        if self.factory.get_debug():
            sys.stderr.write( "Job %s: ConnID %s: Received:\n %s" % (self.job_id, self.factory.get_conn_id(), self.recv))
        self.parser.execute(data, data_len)
        #sys.stderr.write(line)
        #sys.stderr.write("Received this body: \n\t%s\n" % self.parser.recv_body())
        #sys.stderr.write(line)
        if self.parser.is_headers_complete():
            headers = self.parser.get_headers()
            if "Location" in headers:
                location = headers["Location"]
            self.factory.set_server_headers(self.parser.get_headers())
            if "POST" in self.verb:
                self.transport.loseConnection()
        self.factory.proc_body(self.parser.recv_body())
        if self.parser.is_partial_body():
            self.body += self.parser.recv_body()
        # TODO - find a way to deal with this, SBE jobs currently don't trigger this check, but we need it for health checks
        if self.parser.is_message_complete():
            if self.factory.get_debug():
                sys.stderr.write( "Job %s: ConnID %s: MESSAGE COMPLETE!\n" % (self.job_id, self.factory.get_conn_id()))
                sys.stderr.write("Job %s: Received this body: %s" % (self.job_id, self.body))
            self.factory.proc_body(self.body)
            self.parser = None
            self.transport.loseConnection()

class WebCoreFactory(protocol.ClientFactory):

    def __init__(self):
        self.recv_bytes = 0
        self.sent_bytes = 0
        self.fail = False
        self.reason = None
        self.start = None
        self.end = None
        self.code = None
        self.status = ""
        self.server_headers = ""
        self.headers = ""
        self.body = ""
        self.conn_id = 0
        self.cookie_re = re.compile("Set-cookie: (.*)")
        self.debug = False
        self.data = ""
        self.verb = "GET"
        self.addr = None
        self.postdata = ""
        self.deferred = Deferred()
        self.url = None

    def get_deferred(self):
        return self.deferred

    def startedConnecting(self, connector):
        if self.job:
            sys.stderr.write("Job %s:  Starting connection test\n" % self.job.get_job_id())

    def get_postdata(self):
        return self.postdata

    def get_verb(self):
       return self.verb

    def buildProtocol(self, addr):
        self.addr = addr
        self.start = time.time()
        return WebClient(self)

    def add_data(self, data):
        self.data += data

    def add_fail(self, reason):
        self.reason = reason
        self.fail = True

    def set_status(self, status):
        self.status = status

    def set_server_headers(self, headers):
        self.server_headers = headers

    def get_server_headers(self):
        header_str = ""
        for header in self.server_headers:
            header_str += "%s: %s\r\n" % (header, self.server_headers[header])
            #print "%s: %s\r\n" % (header, self.server_headers[header])
        return header_str

    def proc_headers(self, headers):
        self.headers = headers

    def proc_body(self, body):
        self.body = body

    def get_url(self):
        return self.url

    def get_headers(self):
        return self.headers

    def get_conn_id(self):
        return self.conn_id

    def get_timeout(self):
        return self.timeout

    def get_conn_id(self):
        return self.conn_id

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def get_debug(self):
        return self.debug

    def get_job_id(self):
        return None

class JobFactory(WebCoreFactory):

    def __init__(self, params, jobs, op, job=None):
        WebCoreFactory.__init__(self)
        self.params = params
        self.jobs = jobs
        self.url = self.params.get_url()
        self.headers = self.params.get_headers()
        self.ip = self.params.get_sb_ip()
        self.port = self.params.get_sb_port()
        self.timeout = self.params.get_timeout()
        self.debug = self.params.get_debug()
        self.op = op
        self.job = job
        if "get" in self.op:
            self.verb = "GET"
        elif "put" in self.op:
            self.verb = "POST"
            self.postdata = self.job.get_json_str()
            sys.stderr.write("Job %s: Starting Job Post\n" % self.job.get_job_id())
        else:
            raise Exception("Job %s: Unknown operation %s" % (self.job_id, op))

    def clientConnectionFailed(self, connector, reason):
        if self.params.debug:
            if "put" in self.op:
                sys.stderr.write( "Job %s:  JobFactoryClientConnectionFailed\t" % self.job.get_job_id())
            else:
                sys.stderr.write( "Job GET request clientConnectionFailed\t" % self.job.get_job_id())
            sys.stderr.write( "given reason: %s\t" % reason)
            sys.stderr.write( "self.reason: %s\t" % self.reason)
            if self.debug:
                sys.stderr.write( "\nReceived: %s\n" % self.get_server_headers())
        self.params.fail_conn("Job %s connection failed" % (self.op), reason.getErrorMessage(), self.get_server_headers())

    def clientConnectionLost(self, connector, reason):
        if self.params.debug:
            if "put" in self.op:
                sys.stderr.write( "Job %s: clientConnectionLost\t" % self.job.get_job_id())
            else:
                sys.stderr.write( "Job GET request clientConnectionLost\t")
            sys.stderr.write( "given reason: %s\t" % reason)
            sys.stderr.write( "self.reason: %s\t" % self.reason)
            if self.debug:
                sys.stderr.write( "\nReceived: %s\n" % self.get_server_headers())
        if "put" in self.op:
            pass
        elif self.fail and self.reason:
            self.params.fail_conn(self.status, self.reason, self.get_server_headers())
        elif self.fail and not self.reason:
            self.params.fail_conn(self.status, reason.getErrorMessage(), self.get_server_headers())
        elif "non-clean" in reason.getErrorMessage():
            self.params.fail_conn(self.status, "other", self.get_server_headers())
        else:
            #Connection closed cleanly, process the results
            self.jobs.add(self.body)

class WebServiceCheckFactory(WebCoreFactory):

    def __init__(self, params, job, service, url="/index.html"):
        WebCoreFactory.__init__(self)
        self.job = job
        self.params = params
        self.service = service
        self.url = url
        self.headers = self.service.get_headers()
        self.ip = job.get_ip()
        self.port = self.service.get_port()
        self.timeout = self.params.get_timeout()

    def add_fail(self, reason):
        if "timeout" in reason:
            self.service.timeout("%s\r\n%s" % (self.get_server_headers(), self.body))
        else:
            self.service.fail_conn(reason, "%s\r\n%s" % (self.get_server_headers(), self.body))

    def get_job(self):
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
            self.service.timeout(conn_time, self.data)
            return
        if self.status:
            self.service.add_status(self.status)
        self.service.fail_conn(reason.getErrorMessage(), self.data)
        self.deferred.errback(reason)

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
            self.deferred.callback(self.job.get_job_id())

class WebContentCheckFactory(WebCoreFactory):

    def __init__(self, params, job, service, content):
        WebCoreFactory.__init__(self)
        self.job = job
        self.params = params
        self.service = service
        self.content = content
        self.url = self.content.get_url()
        self.headers = self.service.get_headers()
        self.ip = job.get_ip()
        self.port = self.service.get_port()
        self.timeout = self.params.get_timeout()

    def add_fail(self, reason):
        if "timeout" in reason:
            self.content.timeout("%s\r\n%s" % (self.get_server_headers(), self.body))
        else:
            self.content.fail_conn(reason, "%s\r\n%s" % (self.get_server_headers(), self.body))

    def clientConnectionFailed(self, connector, reason):
        # TODO - implement handling of failure to connect.  Should it retry?
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "Job %s: clientConnectionFailed\t" % self.job.get_job_id())
            sys.stderr.write( "given reason: %s\t" % reason)
            sys.stderr.write( "self.reason: %s\t" % self.reason)
            if self.debug:
                sys.stderr.write( "\nReceived: %s" % self.get_server_headers())
        conn_time = None
        if self.start:
            conn_time = self.end - self.start
        else:
            self.content.timeout(conn_time, self.data)
            return
        if self.status:
            self.content.add_status(self.status)
        self.content.fail_conn(reason.getErrorMessage(), self.data)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "Job %s: clientConnectionLost\t" % self.job.get_job_id())
            sys.stderr.write( "given reason: %s\t" % reason)
            sys.stderr.write( "self.reason: %s\t" % self.reason)
            if self.debug:
                sys.stderr.write( "\nReceived: %s" % self.get_server_headers())
        conn_time = self.end - self.start
        if self.data:
            self.content.set_data(self.data)
        if self.fail and self.reason:
            self.content.fail_conn(self.reason, self.data)
        elif self.fail and not self.reason:
            self.content.fail_conn(reason.getErrorMessage(), self.data)
        elif "non-clean" in reason.getErrorMessage():
            self.content.fail_conn("other", self.data)
        else:
            self.content.pass_conn()
            self.deferred.callback(self.job.get_job_id())

if __name__ == "__main__":
    from twisted.python import log
    from DNSclient import DNSclient
    import sys
    log.startLogging(open('log/webtest.log', 'w'))
    jobs = Jobs()
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

    sys.stderr.write( "Testing %s\n" % sys.argv[0])
    params = Parameters()
    factory = JobFactory(params, jobs, "get")
    reactor.connectTCP(params.get_sb_ip(), params.get_sb_port(), factory, params.get_timeout())
    reactor.callLater(5, check_job, params, jobs)
    reactor.callLater(30, reactor.stop)
    reactor.run()
    print "Finished normally"

