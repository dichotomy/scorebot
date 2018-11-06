#!/usr/bin/env python2

from twisted.internet import reactor
from twisted.names import dns

from common import errormsg


class DNSclient(object):
    # TODO - handle closing DNS connections properly!

    def __init__(self, job, timeout=30):
        self.proto = dns.DNSDatagramProtocol(controller=None)
        self.port = reactor.listenUDP(0, self.proto)
        self.job = job
        self.job_id = self.job.get_job_id()
        self.fqdn = self.job.get_hostname()
        self.dnssvr = self.job.get_dns()
        self.timeout = timeout

    def query(self):
        print "Job %s: starting DNS for FQDN %s using server %s" % \
            (self.job_id, self.fqdn, self.dnssvr)
        dnsjob = self.proto.query((self.dnssvr, 53),
                                  [dns.Query(self.fqdn, dns.A)],
                                  timeout=self.timeout)
        dnsjob.addCallback(self.getResults)
        return dnsjob

    def getResults(self, res):
        if len(res.answers):
            answer_str = '%s' % res.answers[0].payload
            ip_addr = answer_str.split(" ")[1].split("=")[1]
            self.job.set_ip(ip_addr)
            print "Job %s:  DNS lookup for %s gave %s" % \
                (self.job.get_job_id(), res.answers[0].name, self.job.get_ip())
        else:
            # TODO should this throw an exception?
            self.job.set_ping_sent(0)
            self.job.set_ping_respond(0)
            raise Exception("No results obtained")

    @staticmethod
    def errorHandler(failure):
        # TODO Need to implement error handling
        errormsg(str(failure))

    def close(self):
        self.port.stopListening()

