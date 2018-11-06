#!/usr/bin/env python2.7

class Parameters(object):
    def __init__(self):
        self.debug = False
        self.timeout = 90
        # TODO read this from a file so its not exposed in repository
        self.sbe_auth = "124dd9b2-b89c-444b-9b15-30dc7bdd83bf"
        self.sb_ip = "10.150.100.81"
        self.sb_port = 80
        self.url = "/api/job"
        self.headers = {
            "Connection" : "keep-alive",
            "Accept-Encoding" : "gzip, deflate",
            "User-Agent" : "Scorebot Monitor/3.0.0",
            "SBE-AUTH" : self.sbe_auth,
            "ACCEPT" : "*/*"
        }
        self.scheme = "http"

