#!/usr/bin/env python2.7
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from http_parser.pyparser import HttpParser
from WebClient import WebCheckFactory, JobFactory
from DNSclient import DNSclient
from Pingclient import PingProtocol

class MonitorCore(object):

    def __init__(self, params, jobs):
        self.params = params
        self.jobs = jobs
        self.ping = "/usr/bin/ping"
        self.ping_cnt = str(5)


    def get_job(self):
        factory = JobFactory(self.params, self.jobs)
        if self.params.get_scheme() == "https":
            ssl_obj = ssl.CertificateOptions()
            reactor.connectSSL(self.params.get_ip(), self.params.get_port(), factory, ssl_obj,\
                                            self.params.get_timeout())
        elif self.params.get_scheme() == "http":
            reactor.connectTCP(self.params.get_ip(), self.params.get_port(), factory, \
                    self.params.get_timeout())
        else:
            raise Exception("Unknown scheme:  %s" % self.params.get_scheme())

    def dns_fail(self, job):
        # Todo - add code to handle DNS check failure
        # Do this if the DNS check failed

    def ping_fail(self, job):
    # Todo - add code to handle ping failure
        # Do this if the Ping check failed

    def ping(self, job):
        # Ping
        ipaddr = job.get_ip()
        pingobj = PingProtocol(ipaddr)
        ping_d = pingobj.getDeferred()
        ping_d.addCallback(self.check_services, job)
        ping_d.addErrback(self.ping_fail, job)
        reactor.spawnProcess(pingobj, self.ping, [self.ping, "-c", self.ping_cnt, ipaddr])

    def check_services(self, job):
        # Service walk
        for service in job.get_services():
            factory = WebCheckFactory(service)
            if "tcp" in service.get_proto():
                reactor.connectTCP(job.get_ip(), service.get_port(), factory, self.params.get_timeout())
            elif "udp" in service.get_proto():
                # TODO - write the code to handle UDP checks
                pass
            else:
                raise Exception("Unknown protocol %s!" % service.get_proto())

    def start_job(self):
        # Get the next job started
        job = self.jobs.get_job()
        # DNS
        dnsobj = DNSclient(job)
        # Execute the query
        query_d = dnsobj.query()
        # Handle a DNS failure - fail the host
        query_d.addErrback(self.dns_fail, job)
        # Handle a DNS success - move on to ping
        query_d.addCallback(self.ping, job)


if __name__=="__main__":
    # TODO - add code to test the job

