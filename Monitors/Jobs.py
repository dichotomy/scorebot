#!/usr/bin/env python2.7
import sys
import time
import json
import base64
import pprint

statuses = ["pass", "reset", "timeout", "refused", "invalid"]

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
        self.max_submitted = 100
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
                sys.stderr.write("Job %s is done, processing." % job_id)
                self.done.append(job_id)
        for job_id in self.done:
            if job_id in self.proc:
                self.proc.remove(job_id)
            else:
                sys.stderr.write("WTF? Job %s is done but not in self.proc!" % job_id)
        return self.done

    def finish_job(self, job_id, reason):
        if "DNS failed" in reason:
            self.jobs[job_id].fail_dns()
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
            if len(self.submitted) > self.max_submitted:
                self.submitted.reverse()
                self.submitted.pop()
                self.submitted.reverse()
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
                        "connect": "pass"|"reset"|"timeout",
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
                            "connect": "pass"|"reset"|"timeout",
                            "data": ""
                        }]
                    }]
                }
            }
        }
    """

    def __init__(self, job_json_str, debug=False):
        # todo make this debug
        self.job_id = 0
        #print "Attempting to parse json: %s" % job_json_str
        self.json = json.loads(job_json_str)
        self.services = []
        for service in self.json["host"]["services"]:
            self.services.append(Service(service, self, debug))
        self.headers = {}
        self.headers["Connection"] = "keep-alive"
        #self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["Accept"] = "*/*"
        self.scheme = "http"
        self.timeout = 90
        self.debug = debug
        self.factory = None
        self.json["host"]["ping_respond"] = ""
        self.json["host"]["ping_sent"] = ""


    def set_factory(self, factory):
        self.factory = factory

    def get_factory(self):
        return self.factory

    def get_timeout(self):
        # We want to leave enough time to get the job back before SBE gives up
        if "timeout" in self.json:
            return int(self.json["timeout"] * 0.9)

    def get_service_timeout(self):
        # We want to leave enough time to get the job ready to go back before SBE gives up
        return int(self.get_timeout() * 0.9)

    def set_job_id(self, job_id):
        self.job_id = job_id

    def get_job_id(self):
        return self.job_id

    def get_json_str(self):
        #TODO - should this call self.get_json()?
        sys.stderr.write("Job %s: Converting to JSON\n" % self.job_id)
        return json.dumps(self.get_json())

    def get_result_json_str(self):
        #TODO - should this call self.get_json()?
        sys.stderr.write("Job %s: Converting to result JSON\n" % self.job_id)
        return json.dumps(self.get_result_json())

    def get_dns(self):
        return self.json["dns"][0]

    def fail_dns(self):
        self.set_ping_respond(0)
        self.set_ping_sent(0)

    def get_services(self):
        return self.services

    def get_headers(self):
        header_txt = ""
        for header in self.headers:
            header_txt += "%s: %s\r\n" % (header, self.headers[header])
        return header_txt

    def get_scheme(self):
        return self.scheme

    def get_hostname(self):
        return self.json["host"]["fqdn"]

    def get_fqdn(self):
        return self.json["host"]["fqdn"]

    def set_ip(self, ip_address):
        # Should add code here to sanity check the IP
        self.json["host"]["ip_address"] = ip_address

    def get_ip(self):
        return self.json["host"]["ip_address"]

    def get_url(self):
        # TODO replace this placeholder when the datastructure given by SBE is updated
        return "/index.html"

    def get_ping_sent(self):
        if "ping_sent" in self.json["host"]:
            return self.json["host"]["ping_sent"]
        else:
            return False

    def set_ping_sent(self, sent):
        self.json["host"]["ping_sent"] = sent

    def get_ping_respond(self):
        if "ping_respond" in self.json["host"]:
            return self.json["host"]["ping_respond"]
        else:
            return False

    def set_ping_respond(self, respond):
        self.json["host"]["ping_respond"] = respond

    def get_result_json(self):
        result_json = {}
        result_json["id"] = self.json["id"]
        result_json["host"] = {}
        result_json["host"]["ping_respond"] = self.json["host"]["ping_respond"]
        result_json["host"]["ping_sent"] = self.json["host"]["ping_sent"]
        if result_json["host"]["ping_respond"] == 0 and result_json["host"]["ping_sent"] == 0:
            return result_json
        result_json["host"]["services"] = []
        json_services = result_json["host"]["services"]
        for service in self.services:
            json_services.append(service.get_result_json())
        return result_json

    def get_json(self):
        json_services = []
        for service in self.services:
            json_services.append(service.get_json())
        self.json["host"]["services"] = json_services
        sys.stderr.write("Job %s: converting to json:\n" % self.job_id)
        if self.debug:
            pp = pprint.PrettyPrinter(depth=4)
            pp.pprint(self.json)
        return self.json

    def is_done(self):
        if self.get_ping_sent() and self.get_ping_respond():
            pass
        else:
            return False
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
                "connect": "pass"|"reset"|"timeout|refused",
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
                    "connect": "pass"|"reset"|"timeout",
                    "data": ""
                }]

    """

    def __init__(self, json, job, debug=False):
        self.json = json
        self.contents = []
        self.job = job
        self.debug = debug
        self.contents = []
        if "content" in self.json:
            if self.json["content"]:
                if "content" in self.json["content"]:
                    if "urls" in self.json["content"]["content"]:
                        urls = self.json["content"]["content"]["urls"]
                        for url in urls:
                            self.contents.append(Content(url, self.job))
                    elif "files" in self.json["content"]["content"]:
                        files = self.json["content"]["content"]["files"]
                        for file in files:
                            self.contents.append(Content(file, self.job))
                    elif "pages" in self.json["content"]["content"]:
                        pages = self.json["content"]["content"]["pages"]
                        for page in pages:
                            self.contents.append(Content(page, self.job))
                    else:
                        raise Exception ("Job %s: Unknown content type %s for job" % (self.job.get_job_id(), "|".join(self.json["content"]["content"].keys())))
                else:
                    raise Exception ("Job %s: Illegal content type in json" % self.job.get_job_id())
            else:
                pass
        else:
            self.contents = None
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
        if "status" in self.json:
            if self.json["status"] in statuses:
                pass
            else:
                return False
            for content in self.contents:
                if content.check():
                    continue
                else:
                    return False
        else:
            return False
        return True

    def get_application(self):
        return self.json["application"]

    def get_type(self):
        return self.json["type"]

    def get_passive(self):
        #todo - implement passive FTP bit
        return 0

    def get_contents(self):
        return self.contents

    def has_auth(self):
        if "content" in self.json:
            if self.json["content"]:
                if "content" in self.json["content"]:
                    if "auth" in self.json["content"]["content"]:
                        if self.json["content"]["content"]["auth"].keys():
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_auth(self):
        if "content" in self.json:
            if self.json["content"]:
                if "content" in self.json["content"]:
                    if "auth" in self.json["content"]["content"]:
                        return self.json["content"]["content"]["auth"]
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_login_url(self, index=0):
        auth = self.get_auth()
        if auth:
            if "url" in auth:
                return auth["url"]
            else:
                return None
        else:
            return None

    def get_username(self, index=0):
        auth = self.get_auth()
        if auth:
            if "username" in auth:
                return auth["username"]
            return None
        else:
            return None

    def get_username_field(self, index=0):
        auth = self.get_auth()
        if auth:
            if "username_field" in auth:
                return auth["username_field"]
            else:
                return None
        else:
            return None

    def get_password(self, index=0):
        auth = self.get_auth()
        if auth:
            if "password" in auth:
                return auth["password"]
            else:
                return None
        else:
            return None

    def get_password_field(self, index=0):
        auth = self.get_auth()
        if auth:
            if "password_field" in auth:
                return auth["password_field"]
            else:
                return None
        else:
            return None

    def timeout(self, data):
        #self.set_data(data)
        self.json["status"] = "timeout"

    def pass_conn(self):
        self.json["status"] = "pass"

    def fail_conn(self, failure, data=None):
        if "timeout" in failure:
            self.json["status"] = "timeout"
        elif "reset" in failure:
            self.json["status"] = "reset"
        elif "refused" in failure:
            self.json["status"] = "refused"
        else:
            self.json["status"] = "invalid"

    def pass_auth(self, index=0):
        self.json["auth"][index]["login"] = "pass"

    def fail_auth(self, index=0):
        self.json["auth"][index]["login"] = "fail"

    def set_data(self, data):
        today = time.strftime("%Y%m%d" ,time.gmtime())
        data_file = open("raw/%s_Job_%s_data" % (today, self.job.get_job_id()), "w")
        self.json["content"] = base64.b64encode(data)
        data_file.write(base64.b64encode(data))
        data_file.close()

    def get_url(self):
        sys.stderr.write("FUCK REMOVE THIS SHIT!")
        sys.stderr.write("FUCK REMOVE THIS SHIT!")
        sys.stderr.write("FUCK REMOVE THIS SHIT!")
        # TODO - replace with real code after the JSON is updated
        return self.url

    def get_port(self):
        return int(self.json["port"])

    def get_proto(self):
        return self.json["protocol"]

    def get_result_json(self):
        result_json = {}
        result_json["application"] = self.json["application"]
        result_json["port"] = self.json["port"]
        result_json["protocol"] = self.json["protocol"]
        if "status" in self.json:
            result_json["status"] = self.json["status"]
        else:
            result_json["status"] = "invalid"
        total = 0
        num_contents = 0
        if self.contents:
            for content in self.contents:
                total += content.get_result()
                num_contents += 1
            score = int(float(total) / num_contents) * 100
            result_json["content"] = {"status": score}
        else:
            result_json["content"] = None
        return result_json


    def get_json(self):
        json_content = []
        for content in self.contents:
            json_content.append(content.get_json())
        if "content" in self.json:
            if self.json["content"]:
                if "content" in self.json["content"]:
                    if "urls" in self.json["content"]["content"]:
                        self.json["urls"] = json_content
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
    """ JSON structure for web
                "content": {
                    "content": {
                        "auth": {
                            "password": "pass",
                            "password_field": "pas",
                            "url": "/login",
                            "username": "user",
                            "username_field": "usr"
                        },
                        "urls": [
                            {
                                "keywords": [
                                    "Hello",
                                    "Wordpress",
                                    "First"
                                ],
                                "size": 990,
                                "url": "/index.html"
                            },
                            {
                                "keywords": [
                                    "Hello",
                                    "Wordpress",
                                    "First"
                                ],
                                "size": 990,
                                "url": "/index.html"
                            }
                        ]
                    },
                    "type": "web"
                },

    """
    """ JSON structure for FTP
                "content": {
                    "content": {
                        "auth": {
                            "username": "blueteam",
                            "password": "scorebot"
                        },
                        "files": [
                            {
                                "name": "file1.txt",
                                "size": 16,
                                "data": "This is a file"
                            },
                            {
                                "name": "file2.txt",
                                "size": 32,
                                "data": "This is another file"
                            }
                        ],
                    },
                    "type": "files"
                },
    
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
        self.current_index = 0
        self.max_index = 0

    def get_size(self):
        if "size" in self.json:
            return self.json["size"]
        else:
            return None

    def get_verb(self):
        #return self.json["verb"]
        # todo - add support for post, but SBE must support
        return "GET"

    def get_url(self):
        if "url" in self.json:
            return self.json["url"]
        else:
            return None

    def get_filename(self):
        if "name" in self.json:
            return self.json["name"]

    def get_type(self):
        return self.json["type"]

    def check(self):
        if "connect" in self.json:
            if self.json["connect"] in statuses:
                return True
            else:
                return False
        else:
            return False

    def set_data(self, data):
        today = time.strftime("%Y%m%d" ,time.gmtime())
        data_file = open("raw/%s_Job_%s_data" % (today, self.job.get_job_id()), "w")
        self.json["data"] = base64.b64encode(data)
        data_file.write(base64.b64encode(data))
        data_file.close()

    def get_data(self):
        if "data" in self.json:
            return self.json["data"]
        elif "keywords" in self.json:
            return ",".join(self.json["keywords"])

    def get_json(self):
        return self.json

    def get_result(self):
        if "connect" in self.json:
            if self.json["connect"] == "pass":
                return 1
            else:
                return 0
        else:
            return 0

    def reset(self):
        self.json["connect"] = "reset"

    def timeout(self):
        self.json["connect"] = "timeout"

    def success(self):
        self.json["connect"] = "pass"

    def refused(self):
        self.json["connect"] = "refused"

    def invalid(self):
        self.json["connect"] = "invalid"

    def fail(self, failure):
        if "timeout" in failure:
            self.json["connect"] = "timeout"
        elif "reset" in failure:
            self.json["connect"] = "reset"
        elif "refused" in failure:
            self.json["connect"] = "refused"
        else:
            self.json["connect"] = "invalid"

if __name__ == "__main__":
    import random
    test_json_str = """ 
   {
    "dns": [
        "10.10.10.10"
    ],
    "timeout": 300,
    "host": {
        "fqdn": "mail.alpha.net",
        "services": [
            {
                "application": "smtp",
                "content": null,
                "port": 25,
                "protocol": "tcp"
            },
            {
                "application": "http",
                "content": {
                    "content": {
                        "auth": {
                            "password": "pass",
                            "password_field": "pas",
                            "url": "/login",
                            "username": "user",
                            "username_field": "usr"
                        },
                        "urls": [
                            {
                                "keywords": [
                                    "Hello",
                                    "Wordpress",
                                    "First"
                                ],
                                "size": 990,
                                "url": "/index.html"
                            },
                            {
                                "keywords": [
                                    "Hello",
                                    "Wordpress",
                                    "First"
                                ],
                                "size": 990,
                                "url": "/index.html"
                            }
                        ]
                    },
                    "type": "web"
                },
                "port": 80,
                "protocol": "tcp"
            },
            {
                "application": "ftp",
                "content": {
                    "content": {
                        "auth": {
                            "username": "blueteam",
                            "password": "scorebot"
                        },
                        "files": [
                            {
                                "name": "file1.txt",
                                "size": 16,
                                "data": "This is a file"
                            },
                            {
                                "name": "file2.txt",
                                "size": 32,
                                "data": "This is another file"
                            }
                        ]
                    },
                    "type": "files"
                },
                "port": 21,
                "protocol": "tcp"
            },
            {
                "application": "imap",
                "content": null,
                "port": 143,
                "protocol": "tcp"
            }
        ]
    },
    "id": 19
} 
    """
    #json.loads(test_json_str)
    jobs = Jobs()
    jobs.add(test_json_str)
    job = jobs.get_job()
    job_str = job.get_json_str()
    json_obj = json.loads(job_str)
    json_str = json.dumps(json_obj, indent=4)
    print json_str
    print "Job timeout: ", job.get_timeout()
    print "Job service timeout: ", job.get_service_timeout()
    print "Job ID: ", job.get_job_id()
    print "Job DNS: ", job.get_dns()
    print "Job FQDN: ", job.get_fqdn()
    print "Job FQDN: ", job.get_hostname()
    print "Setting IP 1.1.1.1"
    job.set_ip("1.1.1.1")
    print "Job IP: ", job.get_ip()
    print "Setting ping sent to 5"
    job.set_ping_sent(5)
    print "Job ping sent: ", job.get_ping_sent()
    print "Setting ping respond to 3"
    job.set_ping_respond(3)
    print "Job ping respond: ", job.get_ping_respond()
    print "Is job done? ", job.is_done()
    print "Processing services"
    for service in job.get_services():
        print
        print "\tPort: %s/%s" % (service.get_port(), service.get_proto())
        print "\tApplication %s" % service.get_application()
        print "\tChecking for auth: ", service.has_auth()
        print "\t\tLogin URL: ", service.get_login_url()
        print "\t\tUsername Field: ", service.get_username_field()
        print "\t\tPassword Field: ", service.get_password_field()
        print "\t\tUsername: ", service.get_username()
        print "\t\tPassword: ", service.get_password()
        print "\tTimeout: ", service.timeout("timeout")
        print "\tProcessing content"
        for content in service.get_contents():
            print
            print "\t\tVerb: ", content.get_verb()
            print "\t\tURL: ", content.get_url()
            print "\t\tFilename: ", content.get_filename()
            print "\t\tData: ", content.get_data()
            print "\t\tSetting reset ", content.reset()
            print "\t\tSetting timeout ", content.timeout()
            print "\t\tSetting success ", content.success()
            print "\t\tSetting refused ", content.refused()
            print "\t\tSetting invalid ", content.invalid()
        print "\tSetting service status..."
        option = random.random()
        if option < .5:
            service.pass_conn()
        elif 0.5 <= option < 0.6:
            service.fail_conn("reset")
        elif 0.6 <= option < 0.7:
            service.fail_conn("timeout")
        elif 0.7 <= option < 0.8:
            service.fail_conn("refused")
        else:
            service.fail_conn("foo")
    print "Checking job completeness: ", job.is_done()
    print job.get_result_json_str()
    done =  jobs.find_done_jobs()
    for job_id in done:
        print jobs.finish_job(job_id, "done")
