#!/usr/bin/env python2

import time

from twisted.internet import reactor, protocol
from http_parser.pyparser import HttpParser

from GenSocket import GenCoreFactory
from common import errormsg, no_unicode

class Cookie(object):

    def __init__(self):
        self.name = ""
        self.value = ""
        self.domain = ""
        self.path = ""
        # TODO add code to handle cookie expiry
        self.expires = ""
        self.httponly = False

    def parse_str(self, cookie_str):
        pieces = cookie_str.split(";")
        pieces.reverse()
        cookie = pieces.pop()
        pieces.reverse()
        (self.name, self.value) = cookie.split("=")
        for piece in pieces:
            if "=" in piece:
                (key, value) = piece.split("=")
                if key == "path":
                    self.path = value
                elif key == "Expires":
                    self.expires = value
            # TODO what is going on here?
            elif "HttpOnly":
                self.httponly = True
            else:
                raise Exception("Unknown token %s in Cookie %s!" % (piece, cookie_str))

    def get(self):
        return "%s=%s" % (self.name, self.value)

class CookieJar(object):

    def __init__(self):
        self.cookies = []

    def add(self, cookie_str):
        new_cookie = Cookie()
        new_cookie.parse_str(cookie_str)
        self.cookies.append(new_cookie)

    def get(self):
        if self.cookies:
            cookies_str = "Cookie: "
            cookies_str_a = []
            for cookie in self.cookies:
                cookies_str_a.append(cookie.get())
            cookies_str += "; ".join(cookies_str_a)
            return cookies_str
        else:
            return None

class WebClient(protocol.Protocol):

    def __init__(self, factory, verb="GET", url="/index.html", conn=None, conn_id=None, authing=False, isjob=False):
        self.parser = HttpParser()
        self.isjob = isjob
        self.factory = factory
        self.verb = verb
        self.conn = conn
        self.url = url if not self.conn else conn.get_url()
        self.conn_id = conn_id
        self.job_id = self.factory.get_job_id()
        self.authing = authing
        headers = self.factory.get_headers()
        cookies = self.factory.get_cookies()
        if cookies:
            headers += cookies
        if self.authing:
            data = self.factory.get_authdata()
            header = self.prep_data(data)
            headers += header
            self.request = no_unicode("%s %s HTTP/1.0\r\n%s\r\n%s\r\n\r\n" %
                                      (self.verb, self.url, headers, data))
        elif "POST" in self.verb:
            data = self.factory.postdata
            header = self.prep_data(data)
            headers += header
            self.request = no_unicode("%s %s HTTP/1.0\r\n%s\r\n%s\r\n\r\n" %
                                      (self.verb, self.url, headers, data))
        else:
            self.request = no_unicode("%s %s HTTP/1.0\r\n%s\r\n\r\n" %
                                      (self.verb, self.url, headers))
        self.recv = ""
        self.body = ""
        # We don't wait forever...
        reactor.callLater(self.factory.get_timeout(), self.TimedOut)

    @staticmethod
    def prep_data(data):
        header = "Content-Length: %s\r\n" % str(len(data))
        return header

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
        self.transport.write("%s\r\n" % self.request)

    def dataReceived(self, data):
        data_len = len(data)
        self.recv += data
        self.factory.add_data(data)
        if self.factory.get_debug():
            print "Job %s: ConnID %s: Received:\n %s" % \
                (self.job_id, self.factory.get_conn_id(), self.recv)
        self.parser.execute(data, data_len)
        if self.parser.is_headers_complete():
            status = self.parser.get_status_code()
            print "Job %s: Returned status %s" % (self.job_id, status)
            if self.authing:
                if status != 302:
                    raise Exception("Job %s: Failed authentication" % (self.job_id))
            if self.isjob:
                self.factory.set_code(status)
                if status == 204:
                    self.transport.loseConnection()
                    return
                elif status == 400:
                    self.transport.loseConnection()
                    self.factory.set_job_fail()
                    return
            #if self.factory.get_debug():
            if self.conn_id:
                conn_id = self.conn_id
            else:
                conn_id = self.factory.get_conn_id()
            headers = self.parser.get_headers()
            print "Job %s: ConnID %s: HEADER COMPLETE!\n\t%s" % \
                (self.job_id, conn_id, headers)
            if "Set-Cookie" in headers:
                self.factory.set_cookie(headers["Set-Cookie"])
            self.factory.set_server_headers(self.parser.get_headers())
        self.factory.proc_body(self.parser.recv_body())
        if self.parser.is_partial_body():
            self.body += self.parser.recv_body()
            if self.factory.get_debug():
                errormsg("Current self.body: %s" % self.body)
        # TODO - find a way to deal with this, SBE jobs currently don't trigger
        #        this check, but we need it for health checks
        if self.parser.is_message_complete():
            print "Job %s: ConnID %s: MESSAGE COMPLETE for %s!" % \
                (self.job_id, self.factory.get_conn_id(), self.url)
            if self.conn:
                self.conn.verify_page(self.body)
            if self.factory.get_debug():
                errormsg("Job %s: Received this body: %s" % (self.job_id, self.body))
            self.factory.proc_body(self.body)
            self.parser = None
            self.transport.loseConnection()

class WebCoreFactory(GenCoreFactory):

    def __init__(self):
        GenCoreFactory.__init__(self)
        self.recv_bytes = 0
        self.sent_bytes = 0
        self.code = None
        self.server_headers = ""
        self.headers = ""
        self.body = ""
        self.conn_id = 0
        self.cj = CookieJar()
        self.data = ""
        self.verb = "GET"
        self.postdata = ""
        self.authdata = ""
        self.url = None

    def set_cookie(self, cookie_str):
        # TODO make this debug level later
        print "Job %s: Parsing cookie string %s" % (self.get_job_id(), cookie_str)
        self.cj.add(cookie_str)

    def get_cookies(self):
        return self.cj.get()

    def buildProtocol(self, addr):
        self.addr = addr
        self.start = time.time()
        return WebClient(self)

    def set_server_headers(self, headers):
        self.server_headers = headers

    def get_server_headers(self):
        header_str = ""
        for header in self.server_headers:
            header_str += "%s: %s\r\n" % (header, self.server_headers[header])
        return header_str

    def proc_headers(self, headers):
        self.headers = headers

    def proc_body(self, body):
        self.body += body

    def get_url(self):
        return self.url

    def get_headers(self):
        return self.headers

    def get_body(self):
        return self.body

class JobFactory(WebCoreFactory):

    def __init__(self, params, jobs, op, job=None):
        WebCoreFactory.__init__(self)
        self.params = params
        self.jobs = jobs
        self.url = self.params.url
        self.headers = self.params.get_headers()
        self.ip = self.params.sb_ip
        self.port = self.params.sb_port
        self.timeout = self.params.timeout
        self.debug = self.params.debug
        self.op = op
        self.job = job
        self.code = None
        self.job_fail = False
        if "get" in self.op:
            self.verb = "GET"
        elif "put" in self.op:
            self.verb = "POST"
            self.postdata = self.job.get_result_json_str()
            print "Job %s: Starting Job Post, sending JSON: %s" % \
                (self.job.get_job_id(), self.postdata)
        else:
            raise Exception("Job %s: Unknown operation %s" % (self.job_id, op))

    def set_code(self, code):
        self.code = int(code)

    def set_job_fail(self):
        self.job_fail = True

    def get_job_fail(self):
        return self.job_fail

    def buildProtocol(self, addr):
        self.addr = addr
        self.start = time.time()
        return WebClient(self, verb=self.verb, url=self.url, isjob=True)

    def clientConnectionFailed(self, connector, reason):
        if self.params.debug:
            if "put" in self.op:
                errormsg("Job %s:  JobFactory Put clientConnectionFailed" % self.job.get_job_id())
            else:
                errormsg("Job GET request clientConnectionFailed" % self.job.get_job_id())
                errormsg("given reason: %s" % reason)
                errormsg("self.reason: %s" % self.reason)
            if self.debug:
                errormsg("\nReceived: %s\n" % self.get_server_headers())
        if connector in self.deferreds:
            self.deferreds[connector].errback(reason)

    def clientConnectionLost(self, connector, reason):
        if "put" in self.op:
            job_id = self.job.get_job_id()
            print "Job %s: Received code %s" % (job_id, self.code)
            if self.code == 202:
                print "Job %s: submitted." % job_id
                self.deferreds[connector].callback("Connection closed")
                return
            else:
                self.deferreds[connector].errback(reason)
                errormsg("Job %s: JobFactory Put clientConnectionLost, received code %s" % \
                    (job_id, self.code))
                return
        elif "get" in self.op:
            if self.get_debug():
                errormsg("Job GET request clientConnectionLost")
            errormsg("Received code %s:" % self.code)
            if self.debug:
                errormsg("\nReceived: %s\n" % self.get_server_headers())
            if self.code == 403:
                # This means that SBE has no running games, so just die quietly.
                errormsg("Got code 403, quitting")
                errormsg("Got %s from server" % self.body)
                return
            if self.fail:
                errormsg("Fail bit set")
                errormsg("given reason: %s" % reason)
                errormsg("self.reason: %s" % self.reason)
                errormsg("error message:\n%s" % reason.getErrorMessage())
            else:
                #Connection closed cleanly, process the results
                if self.body:
                    if "<!DOCTYPE html>" in self.body:
                        filename = "sbe/%s.out" % \
                            time.strftime("%Y-%m-%d_%H%M%S", time.localtime(time.time()))
                        with open(filename, "w") as fileobj:
                            fileobj.write(self.body)
                        print "HTML response from SBE detected, written to %s" % filename
                    else:
                        print "Adding as job:\n %s" % self.body
                        self.jobs.add(self.body)
                else:
                    errormsg("No job to add!")
        else:
            raise Exception("Unknown op: %s" % self.op)

class WebServiceCheckFactory(WebCoreFactory):

    def __init__(self, params, job, service):
        WebCoreFactory.__init__(self)
        self.job = job
        self.params = params
        self.debug = self.params.debug
        self.service = service
        self.headers = self.service.get_headers()
        self.ip = job.get_ip()
        self.port = self.service.get_port()
        self.timeout = self.params.timeout
        self.conns_done = 0
        self.contents = self.service.get_contents()
        self.authenticated = False
        self.authenticating = False
        self.checking_contents = False
        self.status = None

    def get_authdata(self):
        username = self.service.get_username()
        password = self.service.get_password()
        username_field = self.service.get_username_field()
        password_field = self.service.get_password_field()
        # auth format: email=test%40delta.net&password=password&action=Login
        auth_data = "%s=%s&%s=%s&action=Login" % \
            (username_field, username, password_field, password)
        print "Job %s: authdata %s" % (self.get_job_id(), auth_data)
        return auth_data

    def buildProtocol(self, addr):
        self.addr = addr
        self.start = time.time()
        if self.authenticating:
            # This isn't technically true, but we're close enough. We just needed to
            # carry state to the WebClient() instance
            return WebClient(self, verb="POST", url=self.service.get_login_url(), authing=True)
        elif self.checking_contents:
            this_conn = self.contents[self.conns_done]
            self.conns_done += 1
            return WebClient(self, verb="GET", conn=this_conn, conn_id=self.conns_done)
        else:
            return WebClient(self, verb="GET")

    def authenticate(self):
        if self.service.has_auth():
            self.authenticating = True
            connector = reactor.connectTCP(self.job.get_ip(),
                                           self.service.get_port(),
                                           self,
                                           self.params.timeout)
            deferred = self.get_deferred(connector)
            deferred.addCallback(self.auth_pass)
            deferred.addErrback(self.auth_fail)
        else:
            self.check_contents()

    def auth_pass(self, result):
        self.authenticating = False
        print "Job %s: Successfully authenticated against %s: %s" % \
            (self.get_job_id(), self.addr, result)
        self.check_contents()

    def auth_fail(self, failure):
        self.authenticating = False
        errormsg("Job %s: Authentication failed against %s: %s" % \
            (self.get_job_id(), self.addr, failure))
        self.check_contents()

    def check_content(self, content):
        connector = reactor.connectTCP(self.job.get_ip(),
                                       self.service.get_port(),
                                       self,
                                       self.job.get_service_timeout())
        deferred = self.get_deferred(connector)
        deferred.addCallback(self.content_pass, content)
        deferred.addErrback(self.content_fail, content)

    def check_contents(self):
        if self.authenticating:
            # We can't do anything until the authentication buildProtocol is done...
            reactor.callLater(1, self.check_contents)
        else:
            # Why wait?  So we can collect cookies.  Otherwise, all requests go out instantly
            wait_for = 0.1
            waiting = 0
            contents = self.service.get_contents()
            if contents:
                self.checking_contents = True
                for content in contents:
                    waiting += wait_for
                    reactor.callLater(waiting, self.check_content, content)
            else:
                connector = reactor.connectTCP(self.job.get_ip(),
                                               self.service.get_port(),
                                               self,
                                               self.params.timeout)
                deferred = self.get_deferred(connector)
                deferred.addCallback(self.conn_pass)
                deferred.addErrback(self.conn_fail)

    def conn_pass(self, result):
        print "Job %s: Successfully connected to %s: %s" % (self.get_job_id(), self.addr, result)
        self.service.pass_conn()

    def conn_fail(self, failure):
        errormsg("Job %s: Failed connect on content check with result %s:  %s/%s" % \
                 (self.job.get_job_id(),
                  failure,
                  self.service.get_port(),
                  self.service.get_proto()))
        errormsg(failure)
        self.service.fail_conn()

    # TODO is result being used??
    def content_pass(self, result, content):
        content.success()
        self.service.pass_conn()
        print "Job %s: Finished content check for  %s/%s | %s" % \
            (self.job.get_job_id(),
             self.service.get_port(),
             self.service.get_proto(),
             content.get_url())

    def content_fail(self, failure, content):
        content.fail(failure)
        errormsg("Job %s: Failed content integrity check with result %s:  %s/%s | %s" % \
                 (self.job.get_job_id(),
                  failure,
                  self.service.get_port(),
                  self.service.get_proto(),
                  content.get_url()))
        print failure

    def add_fail(self, reason):
        if "timeout" in reason:
            errormsg("Job %s service %s timed out" % (self.get_job_id(), self.port))
            self.service.timeout("%s\r\n%s" % (self.get_server_headers(), self.body))
        else:
            self.service.fail_conn(reason, "%s\r\n%s" % (self.get_server_headers(), self.body))

    def get_job_id(self):
        return self.job.get_job_id()

    def clientConnectionFailed(self, connector, reason):
        self.end = time.time()

        errormsg("Job %s: clientConnectionFailed:" % self.job.get_job_id())
        errormsg("reason %s" % reason.getErrorMessage())
        reason.printTraceback()
        errormsg("\nReceived: %s\n" % self.get_server_headers())

        conn_time = None
        if self.start:
            conn_time = self.end - self.start
        else:
            self.service.timeout(self.data)
            return
        self.deferreds[connector].errback(reason)

    def clientConnectionLost(self, connector, reason):
        self.end = time.time()

        errormsg("Job %s: clientConnectionLost" % self.job.get_job_id())
        errormsg("given reason: %s" % reason.getErrorMessage())
        errormsg("self.reason: %s" % self.reason)
        errormsg("\nReceived: %s\n" % self.get_server_headers())

        conn_time = self.end - self.start

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

