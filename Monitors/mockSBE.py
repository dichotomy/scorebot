#!/usr/bin/python2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import random
import cgi
import sys
import json
import time

PORT_NUMBER = 8080

# This class will handles any incoming request from
# the browser
class myHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    infile = open("test_jobs.txt")
    json_objs = json.load(infile)
    jsons = []
    for job in json_objs:
        jsons.append(json.dumps(job))
    #json_str1 = '{"pk": 120, "model": "scorebot.job", "fields": {"job_dns": ["10.100.101.60"], "job_host": {"host_services": [{"service_protocol": "tcp", "service_port": 80, "service_connect": "ERROR", "service_content": {}}], "host_ping_ratio": 50, "host_fqdn": "www.alpha.net"}}, "status": "job"}'
    #json_str2 = '{"pk": 120, "model": "scorebot.job", "fields": {"job_dns": ["10.100.103.60"], "job_host": {"host_services": [{"service_protocol": "tcp", "service_port": 80, "service_connect": "ERROR", "service_content": {}}], "host_ping_ratio": 50, "host_fqdn": "www.gamma.net"}}, "status": "job"}'
    #jsons = []
    #jsons.append(json_str1)
    #jsons.append(json_str2)

    def do_GET(self):
        if self.path == "/job/":
            try:
                # Check the file extension required and
                # set the right mime type

                # Open the static file requested and send it
                self.send_response(200)
                self.end_headers()
                which = random.randrange(len(self.jsons))
                self.wfile.write(self.jsons[which])
                print "GET REQUEST FOR %s" % self.path
                print "SENT %s" % self.jsons[which]
                #self.send_header('Content-type', mimetype)
                #self.end_headers()
                return
            except:
                self.send_error(500, 'We had a problem: %s' % sys.exc_info()[0])
        else:
            self.send_error(300, 'Incorrect request: %s' % self.path)

    # Handler for the POST requests
    def do_POST(self):
        if self.path == "/job":
            print "POST DATA FOR %s" % self.path
            data = self.rfile.read()
            print "RECEIVED %s" % data
            self.send_response(200)
            self.end_headers()
            return
        elif self.path == "/send":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                         })

            print ("Your name is: %s" % form["your_name"].value)
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Thanks %s !" % form["your_name"].value)
            return


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ', PORT_NUMBER)

    # Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
