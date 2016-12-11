#!/usr/bin/env python2.7
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from http_parser.pyparser import HttpParser
from WebClient import WebCheckFactory, JobFactory
from DNSclient import DNSclient

class MonitorCore(object):

    def __init__(self, params, jobs):
        self.params = params
        self.jobs = jobs


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

    def proc_job(self):
        job = jobs.get_job()
        # DNS
        dnsobj = DNSclient(job)
        # Ping
        # Service walk
        factory = WebCheckFactory(job)
        reactor.connectTCP(job.get_ip(), params.get_port(), factory, params.get_timeout())


