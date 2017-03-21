#!/usr/bin/env python2.7
import sys
import json

class Jobs(object):

    def __init__(self):
        # Jobs
        self.jobs = {}
        # List of IDs of the jobs to be done
        self.todo = []
        # List of IDs of the jobs being done
        self.proc = []
        # List of jobs done
        self.done = []
        # The oldest job ID
        self.latest_job_id = 0

    def add(self, job_json_str):
        self.latest_job_id += 1
        self.jobs[self.latest_job_id] = Job(job_json_str)
        self.jobs[self.latest_job_id].set_job_id(self.latest_job_id)
        self.todo.append(self.latest_job_id)
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
            sys.stdout.write("Closing out finished job %s because %s" % (job_id, reason))
        elif job_id in self.proc:
            self.proc.remove(job_id)
            sys.stdout.write("Prematurely closing out job %s while in process because %s!" % (job_id, reason))
        elif job_id in self.todo:
            self.todo.remove(job_id)
            sys.stdout.write("Prematurely closing out job %s before starting it because %s!" % (job_id, reason))
        job = self.jobs[job_id]
        del(self.jobs[job_id])
        return job


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
                    "ping_lost": "100",
                    "ping_received": "100",
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

    def __init__(self, job_json_str):
        # todo make this debug
        print "Attempting to parse json: %s" % job_json_str
        self.json = json.loads(job_json_str)
        self.services = []
        for service in self.json["fields"]["job_host"]["services"]:
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

    def get_timeout(self):
        return self.json["job_timeout"]

    def set_job_id(self, job_id):
        self.job_id = job_id

    def get_job_id(self):
        return self.job_id

    def get_json_str(self):
        #TODO - should this call self.get_json()?
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

    def __init__(self, json):
        self.json = json
        self.contents = []
        for content in self.json["content"]:
            content_obj = Content(content)
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
            if content.has_data():
                continue
            else:
                return False
        return True

    def get_contents(self):
        return self.contents

    def has_auth(self):
        if len(self.json["auth"]):
            return True
        else:
            return False

    def get_login_url(self):
        return self.json["auth"]["login_url"]

    def get_username(self):
        return self.json["auth"]["username"]

    def get_username_field(self):
        return self.json["auth"]["username_field"]

    def get_password(self):
        return self.json["auth"]["password"]

    def get_password_field(self):
        return self.json["auth"]["password_field"]

    def timeout(self, data):
        self.set_data(data)
        self.json["connect"] = "timeout"

    def pass_conn(self):
        self.json["connect"] = "success"

    def fail_conn(self, reason, data):
        self.set_data(data)
        self.json["connect"] = reason

    def set_data(self, data):
        self.json["content"] = data

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

    def __init__(self, json):
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

    def get_type(self):
        return self.json["type"]

    def set_data(self, data):
        self.json["data"] = data

    def has_data(self):
        if self.json["data"]:
            return True
        else:
            return False

    def get_json(self):
        return self.json

    def timeout(self, data):
        self.set_data(data)
        self.json["connect"] = "timeout"

    def pass_conn(self):
        self.json["connect"] = "success"

    def fail_conn(self, reason, data):
        self.set_data(data)
        self.json["connect"] = reason

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
                    "ping_lost": "100",
                    "ping_received": "100",
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

