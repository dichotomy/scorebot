#!/usr/bin/env python2.7

class Service(object):

    def __init__(self, proto, port, service):
        self.proto = proto
        self.port = port
        self.service = service
        self.content = []
        self.status = None

    def set_green(self):
        self.status = "green"

    def set_yellow(self):
        self.status = "yellow"

    def set_red(self):
        self.status = "red"

    def status(self):
        return self.status

class Jobs(object):

    def __init__(self):
        self.todo = {}
        self.proc = {}
        self.done = {}
        self.jobs = []

    def add(self, job_json):
        pass

    def get_job(self):
        pass

class Job(object):

    def __init__(self, hostname):
        self.hostname = hostname
        self.ip_address = None
        self.services = []

    def set_ip(self, ip_address):
        # Should add code here to sanity check the IP
        self.ip_address = ip_address

    def add_service(self, proto, port, service):
        self.services.append(Service(proto, port, service))


