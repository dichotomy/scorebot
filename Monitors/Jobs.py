#!/usr/bin/env python2.7
import sys
import time
import json
import base64
import pprint

class Jobs(object):

    def __init__(self, debug=False):
        # Jobs
        self.jobs = {}
        # List of IDs of the jobs to be done
        self.todo = []
        # List of IDs of the jobs being done
        self.proc = []
        # List of jobs done
        self.done = []
        # List of jobs being submitted
        self.pending_submitted = []
        # List of jobs submitted
        self.submitted = []
        # The oldest job ID
        self.latest_job_id = 0
        self.debug = debug

    def add(self, job_json_str):
        self.latest_job_id += 1
        self.jobs[self.latest_job_id] = Job(job_json_str, self.debug)
        self.jobs[self.latest_job_id].set_job_id(self.latest_job_id)
        self.todo.append(self.latest_job_id)
        sys.stderr.write("Job %s added\n" % self.latest_job_id)
        return self.latest_job_id

    def find_done_jobs(self):
        for job_id in self.proc:
            if self.jobs[job_id].is_done():
                self.done.append(job_id)
        for job_id in self.done:
            self.proc.remove(job_id)
        return self.done

    def finish_job(self, job_id, reason):
        if job_id in self.done:
            self.done.remove(job_id)
            sys.stdout.write("Job %s: Closing out finished job because %s\n" % (job_id, reason))
        elif job_id in self.proc:
            self.proc.remove(job_id)
            sys.stdout.write("Job %s: Prematurely closing out job while in process because %s!\n" % (job_id, reason))
        elif job_id in self.todo:
            self.todo.remove(job_id)
            sys.stdout.write("Job %s: Prematurely closing out job before starting it because %s!\n" % (job_id, reason))
        job = self.jobs[job_id]
        self.pending_submitted.append(job_id)
        return job

    def submitted_job(self, job_id):
        if job_id in self.pending_submitted:
            self.submitted.append(job_id)
            self.pending_submitted.remove(job_id)
            del(self.jobs[job_id])
        else:
            raise Exception("Job %s: marked submitted but not done.")

    def get_job(self, job_id=None):
        if job_id:
            return self.jobs[job_id]
        else:
            if len(self.todo):
                job_id = self.todo.pop(0)
                self.proc.append(job_id)
                return self.jobs[job_id]
            else:
                return None

class Job(object):
    """ json structure
        {
            "status": "job",
            "game_id": 1,
            "model": "apicore.job",
            "pk": "71",
            "fields": {
                "job_timeout":  300,
                "job_dns": [
                    "10.100.101.100",
                    "10.100.101.50"
                ],
                "job_host": {
                    "fqdn": "mail.gamma.net",
                    "ip_address":  "",
                    "host_ping_ratio": "100",
                    "services": [{
                        "port": "443",
                        "application": "http"|"https"|"ssh"|"telnet"|"ftp",
                        "protocol": "tcp",
                        "connect": "success"|"reset"|"timeout",
                        "auth":  [{
                            "login_url": "http://www.gamma.net/login",
                            "auth_type": "<type>",
                            "username": "bob",
                            "username_field": "username",
                            "password": "password",
                            "password_field": "password",
                            "login": "pass"|"fail"
                        }],
                        "content": [{
                            "verb": "GET"|"POST"|"POST",
                            "url": "",
                            "type": "text",
                            "connect": "success"|"reset"|"timeout",
                            "data": ""
                        }]
                    }]
                }
            }
        }
    """

    def __init__(self, job_json_str, debug=False):
        # todo make this debug
        print "Attempting to parse json: %s" % job_json_str
        self.json = json.loads(job_json_str)
        self.services = []
        for service in self.json["fields"]["job_host"]["services"]:
            self.services.append(Service(service, self, debug))
        self.headers = {}
        self.headers["Connection"] = "keep-alive"
        #self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["Accept"] = "*/*"
        self.scheme = "http"
        self.timeout = 90
        self.job_id = 0
        self.debug = debug
        # todo - remove this code after the SBE stops giving it out
        #if self.json["fields"]["job_host"]["ping_lost"]:
        #    del self.json["fields"]["job_host"]["ping_lost"]
        #if self.json["fields"]["job_host"]["ping_received"]:
        #    del self.json["fields"]["job_host"]["ping_received"]
        self.json["fields"]["job_host"]["host_ping_ratio"] = ""

    def get_timeout(self):
        return self.json["job_timeout"]

    def set_job_id(self, job_id):
        self.job_id = job_id

    def get_game_id(self):
        return self.json["game_id"]

    def get_job_id(self):
        return self.job_id

    def get_json_str(self):
        #TODO - should this call self.get_json()?
        sys.stderr.write("Job %s: Converting to JSON\n" % self.job_id)
        return json.dumps(self.get_json())

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
        return self.json["fields"]["job_host"]["fqdn"]

    def set_ip(self, ip_address):
        # Should add code here to sanity check the IP
        self.json["fields"]["job_host"]["ip_address"] = ip_address

    def get_ip(self):
        return self.json["fields"]["job_host"]["ip_address"]

    def get_url(self):
        # TODO replace this placeholder when the datastructure given by SBE is updated
        return "/index.html"

    def set_ping_ratio(self, ratio):
        self.json["fields"]["job_host"]["host_ping_ratio"] = ratio
        if 0 <= ratio <= 100 :
            return True
        else:
            return False

    def set_ping_lost(self, lost):
        if 0 <= lost <= 100 :
            self.json["fields"]["job_host"]["ping_lost"] = lost
            return True
        else:
            self.json["fields"]["job_host"]["ping_lost"] = 0
            return False

    def get_ping_lost(self):
        return self.json["fields"]["job_host"]["ping_lost"]

    def set_ping_recv(self, recv):
        if 0 <= recv <= 100 :
            self.json["fields"]["job_host"]["ping_received"] = recv
            return True
        else:
            self.json["fields"]["job_host"]["ping_received"] = 0
            return False

    def get_ping_recv(self):
        return self.json["fields"]["job_host"]["ping_received"]

    def get_json(self):
        json_services = []
        for service in self.services:
            json_services.append(service.get_json())
        self.json["fields"]["job_host"]["services"] = json_services
        sys.stderr.write("Job %s: converting to json:\n" % self.job_id)
        if self.debug:
            pp = pprint.PrettyPrinter(depth=4)
            pp.pprint(self.json)
        return self.json

    def is_done(self):
        for service in self.services:
            if service.is_done():
                continue
            else:
                return False
        return True

class Service(object):

    """ json structure
            "services": [{
                "port": "443",
                "application": "http"|"https"|"ssh"|"telnet"|"ftp",
                "protocol": "tcp",
                "connect": "success"|"reset"|"timeout",
                "data":"",
                "auth":    [{
                    "auth_type": "<type>",
                    "username": "bob",
                    "username_field": "username",
                    "password": "password",
                    "password_field": "password",
                    "login": "pass"|"fail"
                }],
                "content": [{
                    "verb": "GET"|"POST"|"POST",
                    "url": "",
                    "type": "text",
                    "connect": "success"|"reset"|"timeout",
                    "data": ""
                }]

    """

    def __init__(self, json, job, debug=False):
        self.json = json
        self.contents = []
        self.job = job
        self.debug = debug
        for content in self.json["content"]:
            content_obj = Content(content, self.job)
            self.contents.append(content_obj)
        # todo - handle headers centrally somewhere, not here.
        self.headers = {}
        # Default values
        self.headers["Connection"] = "keep-alive"
        #self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["Accept"] = "*/*"
        # temp variable until JSON is updated
        self.url = "/index.html"

    def is_done(self):
        for content in self.contents:
            if content.check():
                continue
            else:
                return False
        return True

    def get_passive(self):
        #todo - implement passive FTP bit
        return 0

    def get_contents(self):
        return self.contents

    def has_auth(self):
        if len(self.json["auth"]):
            return True
        else:
            return False

    def get_login_url(self):
        return self.json["auth"]["login_url"]

    def get_username(self, index=0):
        return self.json["auth"][index]["username"]

    def get_username_field(self, index=0):
        return self.json["auth"][index]["username_field"]

    def get_password(self, index=0):
        return self.json["auth"][index]["password"]

    def get_password_field(self, index=0):
        return self.json["auth"][index]["password_field"]

    def timeout(self, data):
        self.set_data(data)
        self.json["connect"] = "timeout"

    def pass_conn(self):
        self.json["connect"] = "success"

    def fail_conn(self, failure, data=None):
        self.json["connect"] = failure

    def pass_login(self, index=0):
        self.json["auth"][index]["login"] = "pass"

    def fail_login(self, index=0):
        self.json["auth"][index]["login"] = "fail"

    def set_data(self, data):
        today = time.strftime("%Y%m%d" ,time.gmtime())
        data_file = open("raw/%s_Job_%s_data" % (today, self.job.get_job_id()), "w")
        self.json["content"] = base64.b64encode(data)
        data_file.write(base64.b64encode(data))
        data_file.close()

    def get_url(self):
        # TODO - replace with real code after the JSON is updated
        return self.url

    def get_port(self):
        return int(self.json["port"])

    def get_proto(self):
        return self.json["protocol"]

    def get_app(self):
        return self.json["application"]

    def get_json(self):
        json_content = []
        for content in self.contents:
            json_content.append(content.get_json())
        self.json["content"] = json_content
        if self.debug:
            pp = pprint.PrettyPrinter(depth=4)
            pp.pprint(self.json)
        return self.json

    def get_headers(self):
        # Dummy function until the JSON structure is updated
        # TODO - replace with real code
        header_txt = ""
        for header in self.headers:
            header_txt += "%s: %s\r\n" % (header, self.headers[header])
        return header_txt

class Content(object):
    """ JSON structure
                "content": [{
                    "verb": "GET"|"POST"|"POST",
                    "url": "",
                    "type": "text",
                    "data": "",
                    "connect": "success"|"reset"|"timeout"
                }]
    """

    def __init__(self, json, job):
        self.job = job
        self.json = json
        # todo - handle headers centrally somewhere, not here.
        self.headers = {}
        # Default values
        self.headers["Connection"] = "keep-alive"
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["Accept"] = "*/*"

    def get_verb(self):
        return self.json["verb"]

    def get_url(self):
        return self.json["url"]

    def get_filename(self):
        return self.json["filename"]

    def get_type(self):
        return self.json["type"]

    def check(self):
        if self.json["check"] == "success":
            return True
        elif self.json["check"] == "fail":
            return False
        else:
            raise Exception("Unknown check status %s" % self.json["check"])

    def set_data(self, data):
        today = time.strftime("%Y%m%d" ,time.gmtime())
        data_file = open("raw/%s_Job_%s_data" % (today, self.job.get_job_id()), "w")
        self.json["data"] = base64.b64encode(data)
        data_file.write(base64.b64encode(data))
        data_file.close()

    def get_data(self):
        return self.json["data"]

    def get_json(self):
        return self.json

    def timeout(self, data):
        self.set_data(data)
        self.json["connect"] = "timeout"

    def success(self):
        self.json["connect"] = "success"

    def fail(self, data):
        self.set_data(data)
        self.json["connect"] = "fail"

if __name__ == "__main__":
    test_json_str = """ {
            "status": "job",
            "model": "apicore.job",
            "pk": "71",
            "fields": {
                "job_dns": [
                    "10.100.101.100",
                    "10.100.101.50"
                ],
                "job_host": {
                    "fqdn": "mail.gamma.net",
                    "ip_address":  "",
                    "host_ping_ratio": "100",
                    "services": [{
                        "port": "443",
                        "application": "http",
                        "protocol": "tcp",
                        "connect": "success",
                        "auth":  [{
                            "login_url": "http://www.gamma.net/login",
                            "auth_type": "<type>",
                            "username": "bob",
                            "username_field": "username",
                            "password": "password",
                            "password_field": "password",
                            "login": "pass"
                        }],
                        "content": [{
                            "verb": "GET",
                            "url": "",
                            "type": "text",
                            "connect": "success",
                            "data": ""
                        }]
                    }]
                }
            }
        }
    """
    json.loads(test_json_str)
    job = Job(test_json_str)
    job_str = job.get_json_str()
    json_obj = json.loads(job_str)
    json_str = json.dumps(json_obj, indent=4)
    print json_str

