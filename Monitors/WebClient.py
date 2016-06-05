#!/usr/bin/env python2.7
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from http_parser.pyparser import HttpParser
from Parameters import Parameters
from Jobs import Jobs
import time
import sys
import re


class WebClient(protocol.Protocol):

    def __init__(self, factory, params, job):
        self.parser = HttpParser()
        self.factory = factory
        self.params = params
        self.job = job
        if self.job:
            self.url = self.no_unicode(job.get_path())
            self.headers = self.no_unicode(self.job.get_headers())
        else:
            self.url = self.params.get_url()
            self.headers = self.no_unicode(self.params.get_headers())
        self.request = "GET %s HTTP/1.1\r\n%s\r\n" % (self.url, self.headers)
        self.parser = HttpParser()
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
        sys.stderr.write("Made connection to %s:%s\n" % (self.params.get_sb_ip(), self.params.get_sb_port()))
        self.timeout = reactor.callLater(self.params.get_timeout(), self.TimedOut)
        self.transport.write(self.request)

    def dataReceived(self, data):
        data_len = len(data)
        self.recv += data
        if self.params.debug:
            sys.stderr.write( "ConnID %s: Received:\n %s" % (self.conn_id, self.recv))
        self.parser.execute(data, data_len)
        if self.parser.is_headers_complete():
            code = self.parser.get_status_code()
            self.factory.set_status(code)
            headers = self.parser.get_headers()
            if "Location" in headers:
                location = headers["Location"]
            if self.params.debug:
                self.factory.set_server_headers(self.parser.get_headers())
            self.factory.proc_headers(headers)
        if self.parser.is_partial_body():
            self.body += self.parser.recv_body()
        if self.parser.is_message_complete():
            if self.params.debug:
                sys.stderr.write( "ConnID %s: MESSAGE COMPLETE!" % self.conn_id)
            self.factory.proc_body(self.body)
            self.parser = None
            self.transport.loseConnection()
            return

class WebFactory(protocol.ClientFactory):

    def __init__(self, params, job=None):
        self.params = params
        self.job = job
        self.recv_bytes = 0
        self.sent_bytes = 0
        self.fail = False
        self.reason = None
        self.start = None
        self.end = None
        self.status = None
        self.server_headers = None
        self.headers = ""
        self.body = ""
        self.cookie_re = re.compile("Set-cookie: (.*)")

    def add_fail(self, reason):
        self.reason = reason
        self.fail = True

    def set_status(self, status):
        self.status = status

    def buildProtocol(self, addr):
        self.start = time.time()
        return WebClient(self, self.params, self.job)

    def proc_response(self, response):
        # What do we do here?
        pass

    def proc_headers(self, headers):
        self.headers = headers

    def proc_body(self, body):
        self.body = body

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "="*80 + "\n")
            sys.stderr.write( "clientConnectionFailed\n")
            sys.stderr.write( "given reason: %s\n" % reason)
            sys.stderr.write( "self.reason: %s\n" % self.reason)
            sys.stderr.write( "Received:\n")
            sys.stderr.write( self.server_headers)
            sys.stderr.write( "="*80 + "\n")
        conn_time = None
        if self.start:
            conn_time = self.end - self.start
        else:
            self.job.fail_conn("client timeout", conn_time, \
                                    self.sent_bytes, self.recv_bytes)
            return
        if self.status:
            self.job.add_status(self.status)
        self.job.fail_conn(reason.getErrorMessage(), conn_time, \
                                self.sent_bytes, self.recv_bytes)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()
        if self.params.debug:
            sys.stderr.write( "="*80 + "\n")
            sys.stderr.write( "clientConnectionLost\n")
            sys.stderr.write( "given reason: %s\n" % reason)
            sys.stderr.write( "self.reason: %s\n" % self.reason)
            sys.stderr.write( "Received:\n")
            sys.stderr.write( self.server_headers)
            sys.stderr.write( "="*80 + "\n")
        conn_time = self.end - self.start
        if self.job:
            if self.status:
                self.job.add_status(self.status)
            if self.fail and self.reason:
                self.job.fail_conn(self.reason, conn_time, \
                                        self.sent_bytes, self.recv_bytes)
            elif self.fail and not self.reason:
                self.job.fail_conn(reason.getErrorMessage(), conn_time, \
                                        self.sent_bytes, self.recv_bytes)
            elif "non-clean" in reason.getErrorMessage():
                self.job.fail_conn("other", conn_time, \
                                        self.sent_bytes, self.recv_bytes)
            else:
                self.job.fin_conn(reason.getErrorMessage(), \
                                       conn_time, self.sent_bytes, self.recv_bytes)
        else:
            if self.fail and self.reason:
                self.params.fail_conn(self.status, self.reason, self.server_headers, \
                                      conn_time, self.sent_bytes, self.recv_bytes)
            elif self.fail and not self.reason:
                self.params.fail_conn(self.status, reason.getErrorMessage(), self.server_headers, \
                                      conn_time, self.sent_bytes, self.recv_bytes)
            elif "non-clean" in reason.getErrorMessage():
                self.params.fail_conn(self.status, "other", self.server_headers,
                                      conn_time, self.sent_bytes, self.recv_bytes)
            else:
                #Connection closed cleanly, process the results
                self.params.fin_conn(self.status, reason.getErrorMessage(), self.headers, self.body)

if __name__ == "__main__":
    import sys
    sys.stderr.write( "Testing %s\n" % sys.argv[0])
    params = Parameters()
    jobs = Jobs()
    factory = WebFactory(params)
    reactor.connectTCP(params.get_sb_ip(), params.get_sb_port(), factory, params.get_timeout())
    reactor.run()

