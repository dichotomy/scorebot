#!/usr/bin/env python2
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from twisted.names import dns
from Jobs import Jobs
import sys

class DNSclient(object):
    # TODO - handle closing DNS connections properly!

    def __init__(self, job, timeout=30):
        self.proto = dns.DNSDatagramProtocol(controller=None)
        self.port = reactor.listenUDP(0, self.proto)
        self.job = job
        self.fqdn = self.job.get_hostname()
        self.dnssvr = self.job.get_dns()[0]
        self.timeout = timeout

    def query(self):
        #print "Querying %s for %s" % (self.dnssvr, self.fqdn)
        self.d = self.proto.query((self.dnssvr, 53), [dns.Query(self.fqdn, dns.A)], timeout=self.timeout)
        self.d.addCallback(self.getResults)
        return self.d

    def getResults(self, res):
        if len(res.answers):
            answer_str = '%s' % res.answers[0].payload
            ip_addr = answer_str.split(" ")[1].split("=")[1]
            self.job.set_ip(ip_addr)
            # todo make this a proper debug statement
            sys.stderr.write("Job %s:  DNS lookup for %s gave %s\n" % \
                                (self.job.get_job_id(), res.answers[0].name, self.job.get_ip()))
        else:
            raise Exception("No results obtained")

    def errorHandler(self, failure):
        # Need to implement error handling
        sys.stderr.write(str(failure))
        pass

    def close(self):
        self.port.stopListening()

if __name__ == "__main__":
    import sys
    sys.stderr.write( "Testing %s\n" % sys.argv[0])
    json_str1 = '{"pk": 120, "model": "scorebot.job", "fields": {"job_dns": ["10.100.101.60"], "job_host": {"host_services": [{"service_protocol": "tcp", "service_port": 80, "service_connect": "ERROR", "service_content": {}}], "host_ping_ratio": 50, "host_fqdn": "www.alpha.net"}}, "status": "job"}'
    json_str2 = '{"pk": 120, "model": "scorebot.job", "fields": {"job_dns": ["10.100.101.60"], "job_host": {"host_services": [{"service_protocol": "tcp", "service_port": 80, "service_connect": "ERROR", "service_content": {}}], "host_ping_ratio": 50, "host_fqdn": "ftppub.alpha.net"}}, "status": "job"}'
    json_str3 = '{"pk": 120, "model": "scorebot.job", "fields": {"job_dns": ["10.100.101.60"], "job_host": {"host_services": [{"service_protocol": "tcp", "service_port": 80, "service_connect": "ERROR", "service_content": {}}], "host_ping_ratio": 50, "host_fqdn": "mail.alpha.net"}}, "status": "job"}'
    jobs_obj = Jobs()
    jobs_obj.add(json_str1)
    jobs_obj.add(json_str2)
    jobs_obj.add(json_str3)
    job = jobs_obj.get_job()
    dnsobj = DNSclient(job)
    query_defered = dnsobj.query()
    job2 = jobs_obj.get_job()
    dnsobj2 = DNSclient(job2)
    query2_defered = dnsobj2.query()
    job3 = jobs_obj.get_job()
    dnsobj3 = DNSclient(job3)
    query3_defered = dnsobj3.query()
    reactor.callLater(5, reactor.stop)
    reactor.run()
