#!/usr/bin/env python2.7

import sys
import json

class Parameters(object):

    def __init__(self):
        self.debug = False
        self.timeout = 90
        #self.sbe_auth = "0987654321"
        #self.sb_ip = "10.200.100.50"
        self.sbe_auth = "12c367a2-f7e8-47aa-88fd-44d052772043"
        self.sb_ip = "10.200.100.110"
        self.sb_port = 80
        #self.sb_ip = "10.200.100.205"
        #self.sb_ip = "172.25.20.211"
        #self.sb_port = 8080
        self.job_url = "/api/job"
        self.reason = ""
        self.headers = {}
        self.headers["Connection"] = "keep-alive"
        #self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["SBE-AUTH"] = self.sbe_auth
        self.headers["Accept"] = "*/*"
        self.scheme = "http"

    def get_debug(self):
        return self.debug

    def set_scheme(self, scheme):
        self.scheme = scheme

    def get_scheme(self):
        return self.scheme

    def get_timeout(self):
        return self.timeout

    def get_sb_ip(self):
        return self.sb_ip

    def get_sb_port(self):
        return self.sb_port

    def get_url(self):
        return self.job_url

    def get_headers(self):
        header_txt = ""
        for header in self.headers:
            header_txt += "%s: %s\r\n" % (header, self.headers[header])
        return header_txt

    def fin_conn(self, status, errmsg, headers, body):
        #sys.stderr.write("Got status:\n%s\n" % status)
        #sys.stderr.write("Got errmsg:\n%s\n" % errmsg)
        #sys.stderr.write("Got headers:\n%s\n" % headers)
        #sys.stderr.write("Got body:\n%s\n" % body)
        if int(status) == 201:
            json_job = json.loads("[%s]" % body)


        #sys.stderr.write("Got body:\n%s\n" % json.dumps(json_body, indent=4))
