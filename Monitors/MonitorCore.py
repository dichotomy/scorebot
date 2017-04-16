#!/usr/bin/env python2.7
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from twisted.python import log
from http_parser.pyparser import HttpParser
from WebClient import WebContentCheckFactory, WebServiceCheckFactory, JobFactory
from DNSclient import DNSclient
from Pingclient import PingProtocol
from twisted.python import log
import traceback
import sys

class MonitorCore(object):

    def __init__(self, params, jobs):
        self.params = params
        self.resubmit_interval = 30
        self.jobs = jobs
        self.ping = "/usr/bin/ping"
        self.ping_cnt = str(5)
        self.jobs_done = []

    def get_job(self):
        factory = JobFactory(self.params, self.jobs, "get")
        if self.params.get_scheme() == "https":
            ssl_obj = ssl.CertificateOptions()
            reactor.connectSSL(self.params.get_ip(), self.params.get_port(), factory, ssl_obj,\
                                            self.params.get_timeout())
        elif self.params.get_scheme() == "http":
            reactor.connectTCP(self.params.get_sb_ip(), self.params.get_sb_port(), factory, \
                    self.params.get_timeout())
        else:
            raise Exception("Unknown scheme:  %s" % self.params.get_scheme())
        # Keep looking for more work
        reactor.callLater(0.1, self.get_job)

    def start_job(self):
        # Get the next job started
        job = self.jobs.get_job()
        if job:
            job_id = job.get_job_id()
            # DNS
            try:
                dnsobj = DNSclient(job)
            except:
                sys.stderr.write("Job %s: Failure starting job %s:\n" % (job_id, job.get_json_str()))
                traceback.print_tb()
            # Execute the query
            query_d = dnsobj.query()
            # Handle a DNS success - move on to ping
            query_d.addCallback(self.dns_pass, job, dnsobj)
            # Handle a DNS failure - fail the host
            query_d.addErrback(self.dns_fail, job, dnsobj)
            # We post the job when the timeout says, whatever is done or not.
            reactor.callLater(job.get_timeout(), self.timeout_job, job.get_job_id())
        reactor.callLater(0.01, self.start_job)

    def timeout_job(self, job_id):
        if job_id not in self.jobs_done:
            job = self.jobs.finish_job(job_id, "timeout")
            self.post_job(job)

    def finish_jobs(self):
        done_jobs = self.jobs.find_done_jobs()
        for job_id in done_jobs:
            job = self.jobs.finish_job(job_id, "job finished")
            self.post_job(job)
        reactor.callLater(0.1, self.finish_jobs)

    def post_job(self, job):
        factory = JobFactory(self.params, self.jobs, "put", job)
        deferred = factory.get_deferred()
        reactor.connectTCP(self.params.get_sb_ip(), self.params.get_sb_port(), factory, \
                           self.params.get_timeout())
        deferred.addCallback(self.job_submit_pass, job)
        deferred.addErrback(self.job_submit_fail, job)

    def job_submit_pass(self, result, job):
        job_id = job.get_job_id()
        sys.stderr.write("Job %s submitted successfully: %s" % (job_id, result))
        self.jobs_done.append(job_id)
        self.jobs.submitted_job(job_id)

    def job_submit_fail(self, failure, job):
        job_id = job.get_job_id()
        sys.stderr.write("Job %s failed due to %s retrying in %s." % (job_id, failure, self.resubmit_interval))
        reactor.callLater(self.resubmit_interval, self.post_job(job))

    def dns_fail(self, failure, job, dnsobj):
        # Do this if the DNS check failed
        job_id = job.get_job_id()
        sys.stderr.write("Job %s:  DNS failed. %s\n" % (job_id, failure))
        job = self.jobs.finish_job(job_id, "DNS failed")
        job.set_ip("fail")
        self.post_job(job)
        dnsobj.close()
        dnsobj = None

    def dns_pass(self, result, job, dnsobj):
        jobid = job.get_job_id()
        print "Job %s:  DNS passed: %s" % (jobid, result)
        reactor.callLater(0.1, self.pinghost, job)
        dnsobj.close()
        dnsobj = None

    def pinghost(self, job):
        pingobj = PingProtocol(job)
        ping_d = pingobj.getDeferred()
        ping_d.addCallback(self.ping_pass, job)
        ping_d.addErrback(self.ping_fail, job)
        pingobj.ping()

    def ping_pass(self, result, job):
        jobid = job.get_job_id()
        sys.stderr.write("Job %s:  Ping passed. %s\n" % (jobid, result))
        reactor.callLater(1, self.check_services, job)

    def ping_fail(self, failure, job):
        jobid = job.get_job_id()
        sys.stderr.write("Job %s:  Ping failed. %s\n" % (jobid, failure))
        job = self.jobs.finish_job(job_id, "Ping failed")
        job.set_ip("fail")
        self.post_job(job)

    def check_services(self, job):
        # Service walk
        for service in job.get_services():
            if "tcp" in service.get_proto():
                factory = None
                if service.get_port() == 80:
                    factory = WebServiceCheckFactory(self.params, job, service)
                    deferred = factory.get_deferred()
                    deferred.addCallback(self.web_service_connect_pass, job, service)
                    deferred.addErrback(self.web_service_connect_fail, job, service)
                    reactor.connectTCP(job.get_ip(), service.get_port(), factory, self.params.get_timeout())
                else:
                    service.fail_conn(failure)
                    jobid = job.get_job_id()
                    sys.stderr.write(("Job %s: Unexpected service %s/%s" % (jobid, service.get_port(), service.get_proto())))
            else:
                # todo - handle the error by reporting the problem with the job in the json
                # and sending that back with the job report back.
                pass

    def web_service_connect_pass(self, result, job, service):
        service.pass_conn()
        proto = service.get_proto()
        port = service.get_port()
        jobid = job.get_job_id()
        sys.stderr.write("Job %s:  Service %s/%s passed. %s\n" % (jobid, proto, port, result))
        #todo - add code to auth if the app is authenticated.  Get the cookie and use
        # with the subsequent content checks.  Add cookie code to the service object
        for content in service.get_contents():
            factory = WebContentCheckFactory(self.params, job, service, content)
            deferred = factory.get_deferred()
            deferred.addCallback(self.web_content_pass, job, service, content)
            deferred.addErrback(self.web_content_fail, job, service, content)
            reactor.connectTCP(job.get_ip(), service.get_port(), factory, self.params.get_timeout())

    def web_service_connect_fail(self, failure, job, service):
        service.fail_conn(failure)
        proto = service.get_proto()
        port = service.get_port()
        jobid = job.get_job_id()
        sys.stderr.write("Job %s:  Service %s/%s failed:\n\t%s\n" % (jobid, proto, port, failure))

    def web_content_pass(self, result, job, service, content):
        # What to do here?
        job_id = job.get_job_id()
        port = service.get_port()
        proto = service.get_proto()
        url = content.get_url()
        sys.stdout.write("Finished content check with result %s for job %s:  %s/%s | %s\n" % (result, job_id, port, proto, url))

    def web_content_fail(self, failure, job, service, content):
        # What to do here?
        job_id = job.get_job_id()
        port = service.get_port()
        proto = service.get_proto()
        url = content.get_url()
        sys.stdout.write("Finished content check with result %s for job %s:  %s/%s | %s\n" % (failure, job_id, port, proto, url))

if __name__=="__main__":
    # Testing with an artificial job file
    from Parameters import Parameters
    from Jobs import Jobs
    log.startLogging(open('log/MonitorCore.log', 'w'))
    params = Parameters()
    jobs = Jobs()
    mon_obj = MonitorCore(params, jobs)
    reactor.callLater(5, mon_obj.get_job)
    reactor.callLater(10, mon_obj.start_job)
    reactor.run()
