#!/usr/bin/env python2
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from http_parser.pyparser import HttpParser
from Parameters import Parameters
from Jobs import Jobs
import time
import re

class WebClient(protocol.Protocol):

    def __init__(self, factory):
        self.parser = HttpParser()
        self.factory = factory
        self.request = "GET %s HTTP/1.0\r\n%s\r\n" % (self.factory.get_url(), self.factory.get_headers())
        self.recv = ""
        self.body = ""

    def no_unicode(self, text):
        sys.stderr.write("Converting %s" % text)
        if isinstance(text, unicode):
            return text.encode('utf-8')
        else:
            return text

    def TimedOut(self):
        self.factory.add_fail("timeout")
        self.transport.loseConnection()

    def connectionMade(self):
        sys.stderr.write("Made connection to %s:%s\n" % (self.factory.get_ip(), self.factory.get_port()))
        reactor.callLater(self.factory.get_timeout(), self.TimedOut)
        sys.stderr.write("Sending: %s\n" % self.request)
        self.transport.write("%s\r\n" % self.request)

    def dataReceived(self, data):
        data_len = len(data)
        self.recv += data
        line = "="*80 + "\n"
        #sys.stderr.write(line)
        #sys.stderr.write("Received this response: \n\t%s\n" % self.recv)
        #sys.stderr.write(line)
        if self.factory.get_debug():
            sys.stderr.write( "ConnID %s: Received:\n %s" % (self.factory.get_conn_id(), self.recv))
        self.parser.execute(data, data_len)
        #sys.stderr.write(line)
        #sys.stderr.write("Received this body: \n\t%s\n" % self.parser.recv_body())
        #sys.stderr.write(line)
        if self.parser.is_headers_complete():
            code = self.parser.get_status_code()
            self.factory.set_status(code)
            headers = self.parser.get_headers()
            if "Location" in headers:
                location = headers["Location"]
            self.factory.set_server_headers(self.parser.get_headers())
        self.factory.proc_body(self.parser.recv_body())
        if self.parser.is_partial_body():
            self.body += self.parser.recv_body()
        # TODO - find a way to deal with this, SBE jobs currently don't trigger this check, but we need it for health checks
        if self.parser.is_message_complete():
            if self.factory.get_debug():
                sys.stderr.write( "ConnID %s: MESSAGE COMPLETE!" % self.factory.get_conn_id())
                sys.stderr.write("Received this body: %s" % self.body)
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
        self.status = ""
        self.server_headers = ""
        self.headers = ""
        self.body = ""
        # TODO Need to figure out how to populate this
        self.conn_id = 0
        self.cookie_re = re.compile("Set-cookie: (.*)")
        self.debug = False

    def buildProtocol(self, addr):
        self.start = time.time()
        return WebClient(self)

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
            print "%s: %s\r\n" % (header, self.server_headers[header])
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

class JobFactory(WebCoreFactory):

    def __init__(self, params, jobs):
        WebCoreFactory.__init__(self)
        self.params = params
        self.jobs = jobs
        self.url = self.params.get_url()
        self.headers = self.params.get_headers()
        self.ip = self.params.get_sb_ip()
        self.port = self.params.get_sb_port()
        self.timeout = self.params.get_timeout()
        self.debug = self.params.get_debug()

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "="*80 + "\n")
            sys.stderr.write( "clientConnectionFailed\n")
            sys.stderr.write( "given reason: %s\n" % reason)
            sys.stderr.write( "self.reason: %s\n" % self.reason)
            sys.stderr.write( "Received:\n")
            sys.stderr.write( self.get_server_headers())
            sys.stderr.write( "="*80 + "\n")
        conn_time = None
        if self.start:
            conn_time = self.end - self.start
        else:
            self.params.fail_conn("client timeout", conn_time, \
                               self.sent_bytes, self.recv_bytes)
            return
        if self.status:
            self.job.add_status(self.status)
        self.params.fail_conn(reason.getErrorMessage(), conn_time, \
                           self.sent_bytes, self.recv_bytes)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "="*80 + "\n")
            sys.stderr.write( "clientConnectionLost\n")
            sys.stderr.write( "given reason: %s\n" % reason)
            sys.stderr.write( "self.reason: %s\n" % self.reason)
            sys.stderr.write( "Received:\n")
            sys.stderr.write(self.get_server_headers())
            sys.stderr.write( "="*80 + "\n")
        conn_time = self.end - self.start
        if self.fail and self.reason:
            self.params.fail_conn(self.status, self.reason, self.get_server_headers(), \
                                  conn_time, self.sent_bytes, self.recv_bytes)
        elif self.fail and not self.reason:
            self.params.fail_conn(self.status, reason.getErrorMessage(), self.get_server_headers(), \
                                  conn_time, self.sent_bytes, self.recv_bytes)
        elif "non-clean" in reason.getErrorMessage():
            self.params.fail_conn(self.status, "other", self.get_server_headers(),
                                  conn_time, self.sent_bytes, self.recv_bytes)
        else:
            #Connection closed cleanly, process the results
            #self.params.fin_conn(self.status, reason.getErrorMessage(), self.headers, self.body)
            self.jobs.add(self.body)

class WebCheckFactory(WebCoreFactory):

    def __init__(self, service):
        WebCoreFactory.__init__(self)
        self.service = service
        self.url = self.service.get_url()
        self.headers = self.service.get_headers()
        self.ip = self.service.get_sb_ip()
        self.port = self.service.get_sb_port()
        self.timeout = self.service.get_timeout()

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "="*80 + "\n")
            sys.stderr.write( "clientConnectionFailed\n")
            sys.stderr.write( "given reason: %s\n" % reason)
            sys.stderr.write( "self.reason: %s\n" % self.reason)
            sys.stderr.write( "Received:\n")
            sys.stderr.write( self.get_server_headers())
            sys.stderr.write( "="*80 + "\n")
        conn_time = None
        if self.start:
            conn_time = self.end - self.start
        else:
            self.service.fail_conn("client timeout", conn_time, \
                                    self.sent_bytes, self.recv_bytes)
            return
        if self.status:
            self.service.add_status(self.status)
        self.service.fail_conn(reason.getErrorMessage(), conn_time, \
                                self.sent_bytes, self.recv_bytes)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "="*80 + "\n")
            sys.stderr.write( "clientConnectionLost\n")
            sys.stderr.write( "given reason: %s\n" % reason)
            sys.stderr.write( "self.reason: %s\n" % self.reason)
            sys.stderr.write( "Received:\n")
            sys.stderr.write( self.get_server_headers())
            sys.stderr.write( "="*80 + "\n")
        conn_time = self.end - self.start
        if self.status:
            self.service.add_status(self.status)
        if self.fail and self.reason:
            self.service.fail_conn(self.reason, conn_time, \
                                    self.sent_bytes, self.recv_bytes)
        elif self.fail and not self.reason:
            self.service.fail_conn(reason.getErrorMessage(), conn_time, \
                                    self.sent_bytes, self.recv_bytes)
        elif "non-clean" in reason.getErrorMessage():
            self.service.fail_conn("other", conn_time, \
                                    self.sent_bytes, self.recv_bytes)
        else:
            self.service.fin_conn(reason.getErrorMessage(), \
                                   conn_time, self.sent_bytes, self.recv_bytes)

if __name__ == "__main__":
    import sys
    sys.stderr.write( "Testing %s\n" % sys.argv[0])
    params = Parameters()
    jobs = Jobs()
    factory = JobFactory(params, jobs)
    reactor.connectTCP(params.get_sb_ip(), params.get_sb_port(), factory, params.get_timeout())
    reactor.callLater(5, check_job, jobs)
    reactor.run()

