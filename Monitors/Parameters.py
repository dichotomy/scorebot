#!/usr/bin/env python2.7

import sys
import json

class Parameters(object):
    # TODO Document methods and attributes
    def __init__(self):
        self.debug = False
        self.timeout = 90
        # TODO read this from a file so its not exposed in repository
        # IDEA - configuration file??
        self.sbe_auth = "2863e4ad-fcc5-4b35-8d31-42112c1c7b5b"
        self.sb_ip = "10.150.100.81"
        self.sb_port = 80
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

    # TODO figure out if there is a real reason for these methods rather than
    # just referring to the attributes directly.
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

