#!/usr/bin/env python

from twisted.internet import reactor, protocol, reactor, ssl
from twisted.protocols import basic
from http_parser.pyparser import HttpParser
from urlparse import urlparse
import sys
import json
import pprint

prefix="/scorebot/api/v1.0"
pprinter = pprint.PrettyPrinter(indent=4)

# Host checking job
#  starts with hostname, ends with IP
class HostJob(object):

    def __init__(self, hostname):
        self.hostname = hostname
        self.ipaddress = None

# Service checking job
#  starts with IP, port, and protocol, ends with connection
class ServiceJob(object):

    def __init__(self, ipaddress, port, protocol):
        self.ipaddress = ipaddress
        self.port = port
        self.protocol = protocol


# Authentication checking
#  starts with 

# Content checking job
# 



class Job(object):

    def __init__(self):
        self.ip = None
        self.port = None
        self.timeout = None
        self.scheme = None

class Jobs(object):

    def __init__(self):
        self.jobs = {}
        self.sleep_time = None
        # Global vars
        self.verbose = False
        self.debug = False
        self.payload_filename = None
        self.console = False

    def get_job(self):
        pass

    def add_host_job(self, hostname):
        pass
        
    def add_service_job(self, hostname, service):
        pass

    def get_ip(self):
        pass

    def get_port(self):
        pass

    def get_timeout(self):
        pass

    def get_scheme(self):
        pass

    def get_sleep_time(self):
        pass

class JobClient(protocol.Protocol):

    def __init__(self, factory, params):
        self.parser = HttpParser()
        self.params = params
        self.verb = self.params.get_verb()
        self.headers = self.params.get_headers()
        self.uris = {}
        self.uris["getgame"] = "%s/game" % prefix
        self.uris["gethost"] = "%s/host" % prefix
        self.uris["getservice"] = "%s/service" % prefix
        self.recv = ""
        self.request = ""
        self.payload = None

    def no_unicode(self, text):
        if isinstance(text, unicode):
            return text.encode('utf-8')
        else:
            return text

    def check_json(self):
        try:
            return json.loads(self.recv)
        except:
            return False

    def TimedOut(self):
        pass

    def connectionMade(self):
        if self.verb == "GET":
            self.request = "GET %s HTTP/1.1\r\n%s\r\n" % (self.url, self.headers)
        elif self.verb == "POST":
            self.payload = self.params.get_payload()
            self.request = "POST %s HTTP/1.1\r\n%s\r\n%s" % \
                             (self.url, self.headers, self.payload)
        self.transport.write(self.request)

    def dataReceived(self, data):
        self.parser.execute(data, len(data))
        if self.parser.is_headers_complete():
            self.headers = self.parser.get_headers()
        if self.parser.is_partial_body():
            self.recv += self.parser.recv_body()
        if self.parser.is_message_complete():
            if self.check_json():
                self.proc_response()
            else:
                print "Problem with %s" % self.recv

    def proc_response(self):
        #Override in subclass
        pass

class HostJob(JobClient):

    def __init__(self, factory, params):
        JobClient.__init__(self, factory, params)
        self.uri = self.uris['gethost']
        self.uri = "%s/hosts/" % prefix
        self.params.set_path(self.uri)
        self.params.build_url()
        self.url = self.params.get_url()

    def proc_response(self):
        # Need to parse the data and stow it in a datastore (via the factory)
        jsonified = json.loads(self.recv)
        if jsonified:
            #process data
            pprinter.pprint(jsonified)
        else:
            print "Only received %s" % self.recv
            pass

class JobFactory(protocol.ClientFactory):

    def __init__(self, parameters):
        self.parameters = parameters

    def buildProtocol(self, addr):
        return HostJob(self, self.parameters)

    def clientConnectionFailed(self, connector, reason):
        pass

    def clientConnectionLost(self, connector, reason):
        pass

class Headers(object):

    def __init__(self):
        self.user_agent = "scorebot/3.0"
        self.user_agent_header = "User-Agent: %s\r\n"
        self.host = None
        self.host_header = "Host: %s:%s\r\n"
        self.accept = "*/*"
        self.accept_header = "Accept: %s\r\n"
        self.content_type = "application/json"
        self.content_type_header =  "Content-Type: %s\r\n"
        self.content_length = None
        self.content_length_header = "Content-Length: %s\r\n"

    def set_user_agent(self, agent):
        self.user_agent = agent

    def set_host(self, host):
        self.host = host

    def set_accept(self, accept):
        self.accept = accept

    def set_content_type(self, content_type):
        self.content_type = content_type

    def set_content_length(self, content_length):
        self.content_length = content_length

    def get_headers(self):
        header = ""
        if self.user_agent:
            header += self.user_agent_header % self.user_agent
        if self.host:
            header += self.host_header % self.host
        if self.accept:
            header += self.accept_header % self.accept
        if self.content_type:
            header += self.content_type_header % self.content_type
        if self.content_length:
            header += self.content_length_header % self.content_length
        return header

class WebParameters(object):

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.headers = Headers()
        self.url = ""
        self.path = ""
        self.scheme = ""
        self.server = None
        self.payload = None
        self.verbose = True
        self.sleep_time = 1
        self.verb = None

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def get_verb(self):
        return self.verb

    def get_sleep_time(self):
        return self.sleep_time

    def get_ip(self):
        return self.host

    def get_port(self):
        return self.port

    def get_timeout(self):
        return self.timeout

    def build_url(self):
        if self.scheme:
            pass
        else:
            raise Exception("No scheme!")
        if self.host:
            pass
        else:
            raise Exception("No host!")
        if self.port:
            if self.path:
                self.url = "%s://%s:%s/%s" % (self.scheme, self.host, self.port, self.path)
            else:
                self.url = "%s://%s:%s/" % (self.scheme, self.host, self.port)
        else:
            if self.path:
                self.url = "%s://%s/%s" % (self.scheme, self.host, self.path)
            else:
                self.url = "%s://%s/" % (self.scheme, self.host)

    def set_url(self, url):
        self.url = url
        parsed_url_obj = urlparse(url)
        if sys.version_info < (2, 7):
            self.scheme = parsed_url_obj[0]
            if self.server:
                pass
            else:
                self.server = parsed_url_obj[1]
            self.path = parsed_url_obj[2]
        else:
            self.scheme = parsed_url_obj.scheme
            if self.server:
                pass
            else:
                self.server = parsed_url_obj.netloc
            if parsed_url_obj.query:
                self.path = "%s?%s" % (parsed_url_obj.path, parsed_url_obj.query)
            else:
                self.path = parsed_url_obj.path

    def get_url(self):
        return self.url

    def set_scheme(self, scheme):
        self.scheme = scheme

    def get_scheme(self):
        return self.scheme

    def set_payload(self, payload):
        self.payload = payload
        payload_len = len(payload)
        self.headers.set_content_length(payload_len)

    def get_payload(self):
        return self.payload

    def get_headers(self):
        return self.headers.get_headers()

class HealthChecker(object):

    def __init__(self, parameters):
        self.params = parameters
        self.sleep_time = 10

    def spawn(self):
        # General algorithm
        # Query the central server what the active game is
        # Query the webserver for Hosts in that game and HostStatus of those hosts
        # See if last HostStatus entry is within the threshold
        # If so, queue a check for the host
        # Upon check, update the database with the result and schedule the next query for the host
        # Repeat process for each Service and ServiceStatus for each Host
        # Repeat process for each Content and Content Status for each Service
        # Validate credentials for service and/or content along the way
        #
        # Now the details...
        # Get the active game
        jobs = JobFactory(self.params)
        if self.params.get_scheme() == "https":
            ssl_obj = ssl.CertificateOptions()
            reactor.connectSSL(self.params.get_ip(), self.params.get_port(), jobs, ssl_obj,\
                                            self.params.get_timeout())
        elif self.params.get_scheme() == "http":
            reactor.connectTCP(self.params.get_ip(), self.params.get_port(), jobs, \
                    self.params.get_timeout())
        else:
            raise Exception("Unknown scheme:  %s" % self.params.get_scheme())
        reactor.callLater(self.sleep_time, self.spawn)

def main(params):
    healthobj = HealthChecker(params)
    #if params.verbose:
        #reactor.callLater(2, healthobj.stat_report)
    reactor.callLater(params.get_sleep_time(), healthobj.spawn)
    reactor.run()

if __name__ == "__main__":
    ipaddress = "127.0.0.1"
    port = 5000
    timeout  = 60
    params = WebParameters(ipaddress, port, timeout)
    params.set_scheme("http")
    params.build_url()
    params.verb = "GET"
    main(params)

