#!/usr/bin/env python2.7
import json

class Jobs(object):

    def __init__(self):
        # Jobs
        self.jobs = {}
        # List of IDs of the jobs to be done
        self.todo = []
        # List of IDs of the jobs being done
        self.proc = []
        # The oldest job ID
        self.latest_job_id = 0

    def add(self, job_json_str):
        self.latest_job_id += 1
        self.jobs[self.latest_job_id] = Job(job_json_str)
        self.jobs[self.latest_job_id].set_job_id(self.latest_job_id)
        self.todo.append(self.latest_job_id)
        return self.latest_job_id

    def get_job(self, job_id=None):
        if job_id:
            return self.jobs[job_id]
        else:
            if len(self.todo):
                job = self.todo.pop(0)
                self.proc.append(job)
                return self.jobs[job]
            else:
                return None

class Job(object):
    """ json structure
        {
            "status": "job",
            "pk": "80",
            "model": "apicore.job",
            "fields": {
                "job_dns": ["10.100.101.60"],
                "job_host": {
                    "status": {
                        "ping_lost": "100",
                        "ping_received": "100",
                        "ip_address": ""
                    },
                    "host_fqdn": "domain.alpha.net",
                    "host_services": [
                        {
                            "service_protocol": "tcp",
                            "service_port": "80",
                            "service_status": "green",
                            "service_connect": "ERROR"
                        }
                    ]
                }
            }
        }
    """

    def __init__(self, job_json_str):
        # todo make this debug
        #print "Attempting to parse json: %s" % job_json_str
        self.json = json.loads(job_json_str)
        self.services = []
        for service in self.json["fields"]["job_host"]["host_services"]:
            self.services.append(Service(service))
        self.headers = {}
        self.headers["Connection"] = "keep-alive"
        #self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["Accept"] = "*/*"
        self.scheme = "http"
        self.timeout = 90
        self.job_id = 0

    def set_job_id(self, job_id):
        self.job_id = job_id

    def get_job_id(self):
        return self.job_id

    def get_json_str(self):
        #TODO - should this call self.get_json()?
        return json.dumps(self.json)

    def get_dns(self):
        return self.json["fields"]["job_dns"]

    def get_services(self):
        return self.services

    def get_headers(self):
        header_txt = ""
        for header in self.headers:
            header_txt += "%s: %s\r\n" % (header, self.headers[header])
        return header_txt

    def get_scheme(self):
        return self.scheme

    def get_timeout(self):
        return self.timeout

    def get_hostname(self):
        return self.json["fields"]["job_host"]["host_fqdn"]

    def set_ip(self, ip_address):
        # Should add code here to sanity check the IP
        if "status" in self.json["fields"]["job_host"]:
            self.json["fields"]["job_host"]["status"]["ip_address"] = ip_address
        else:
            self.json["fields"]["job_host"]["status"] = {}
            self.json["fields"]["job_host"]["status"]["ip_address"] = ip_address

    def get_ip(self):
        return self.json["fields"]["job_host"]["status"]["ip_address"]


    def get_url(self):
        # TODO replace this placeholder when the datastructure given by SBE is updated
        return "/index.html"

    def set_ping_lost(self, lost):
        if 0 <= lost <= 100 :
            self.json["fields"]["job_host"]["status"]["ping_lost"] = lost
            return True
        else:
            self.json["fields"]["job_host"]["status"]["ping_lost"] = 0
            return False

    def get_ping_lost(self):
        return self.json["fields"]["job_host"]["status"]["ping_lost"]

    def set_ping_recv(self, recv):
        if 0 <= recv <= 100 :
            self.json["fields"]["job_host"]["status"]["ping_received"] = recv
            return True
        else:
            self.json["fields"]["job_host"]["status"]["ping_received"] = 0
            return False

    def get_ping_recv(self):
        return self.json["fields"]["job_host"]["status"]["ping_received"]

    def get_json(self):
        json_services = []
        for service in self.services:
            json_services.append(service.get_json())
        self.json["fields"]["job_host"]["host_services"] = json_services
        return self.json

class Service(object):

    """ json structure
            {
                "service_protocol": "tcp",
                "service_port": "80",
                "service_status": "green",
                "service_connect": "ERROR"
            }
    """

    def __init__(self, json):
        self.json = json
        self.headers = {}
        # Default values
        self.headers["Connection"] = "keep-alive"
        #self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["Accept"] = "*/*"
        # temp variable until JSON is updated
        self.url = "/index.html"

    def has_auth(self):
        # TODO - write this code after the json is updated with service creds in SBE
        return False

    def set_data(self, data):
        self.json["content_data_recv"] = data

    def set_green(self):
        self.json["service_status"] = "green"

    def set_yellow(self):
        self.json["service_status"] = "yellow"

    def set_red(self):
        self.json["service_status"] = "red"

    def fail_conn(self, reason, data):
        self.set_data(data)
        self.json["service_connect"] = False

    def timeout(self, conn_time, data):
        self.conn_time = conn_time
        self.set_data(data)
        self.json["service_connect"] = False

    def set_conn_pass(self):
        self.json["service_connect"] = True

    def status(self):
        return self.json["service_status"]

    def get_url(self):
        # TODO - replace with real code after the JSON is updated
        return self.url

    def get_port(self):
        return self.json["service_port"]

    def get_proto(self):
        return self.json["service_proto"]

    def get_json(self):
        return self.json

    def get_headers(self):
        # Dummy function until the JSON structure is updated
        # TODO - replace with real code
        header_txt = ""
        for header in self.headers:
            header_txt += "%s: %s\r\n" % (header, self.headers[header])
        return header_txt

if __name__ == "__main__":
    test_json_str = """ {
            "status": "job",
            "pk": "80",
            "model": "apicore.job",
            "fields": {
                "job_host": {
                    "status": {
                        "ping_lost": "100",
                        "ping_received": "100",
                        "ip_address": ""
                    },
                    "host_fqdn": "domain.alpha.net",
                    "host_services": [
                        {
                            "service_protocol": "tcp",
                            "service_port": "80",
                            "service_status": "green",
                            "service_connect": "ERROR"
                        }
                    ]
                }
            }
        }"""
    json.loads(test_json_str)
