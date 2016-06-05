#!/usr/bin/env python2.7

import sys
import json

class Parameters(object):

    def __init__(self):
        self.debug = False
        self.timeout = 90
        self.sbe_auth = "0987654321"
        self.sb_ip = "10.200.100.50"
        self.sb_port = 80
        self.job_url = "/job/"
        self.headers = {}
        self.reason = ""
        self.headers["Connection"] = "keep-alive"
        self.headers["Host"] = self.sb_ip
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["User-Agent"] = "Scorebot Monitor/3.0.0"
        self.headers["SBE-AUTH"] = self.sbe_auth
        self.headers["Accept"] = "*/*"

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

    def fail_conn(self, status, reason, server_headers, conn_time, sent_bytes, recv_bytes):
        sys.stderr.write("="*80 + "\n")
        sys.stderr.write("clientConnectionLost\n")
        sys.stderr.write("given reason: %s\n" % reason)
        sys.stderr.write("Status: %s\n" % status)
        sys.stderr.write("self.reason: %s\n" % self.reason)
        sys.stderr.write("Received:\n")
        sys.stderr.write(server_headers)
        sys.stderr.write("Connection time: %s\n" % conn_time)
        sys.stderr.write("Bytes Sent: %s Bytes Recv: %s\n" % (sent_bytes, recv_bytes))
        sys.stderr.write( "="*80 + "\n")

    def fin_conn(self, status, errmsg, headers, body):
        #sys.stderr.write("Got status:\n%s\n" % status)
        #sys.stderr.write("Got errmsg:\n%s\n" % errmsg)
        #sys.stderr.write("Got headers:\n%s\n" % headers)
        #sys.stderr.write("Got body:\n%s\n" % body)
        if int(status) == 201:
            json_job = json.loads(body)


        #sys.stderr.write("Got body:\n%s\n" % json.dumps(json_body, indent=4))