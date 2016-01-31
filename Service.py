'''
Created on Dec 18, 2011

@author: dichotomy@riseup.net

Service.py is a module in the scorebot program.  It's purpose is to provide scoring for a given service.

Copyright (C) 2011 Dichotomy

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''
import re
import sys
import time
import ftplib
import socket
import traceback
import threading
import globalvars
import random
import requests
from Logger import Logger
from Scores import Scores

score_str_re = re.compile("Gold Team scoring file, do not touch")
html1_str_re = re.compile("It works")
html2_str_re = re.compile("IIS")
html3_str_re = re.compile("lamp")
html4_str_re = re.compile("Wordpress")

tcp_80_re = re.compile("80/tcp")
tcp_21_re = re.compile("21/tcp")
tcp_25_re = re.compile("25/tcp")
udp_53_re = re.compile("53/udp")

class Service(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self, port, protocol, value, teamname, queue, hostname, \
                        oqueue, equeue, BToqueue, BTequeue, \
                        uri="index.html", content=None, username=None, password=None):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.hostname = hostname
        basename = "%s-%s:%s_%s" % (teamname, hostname, port, protocol)
        #self.logger = Logger(basename)
        self.oqueue = oqueue
        self.equeue = equeue
        self.BToqueue = BToqueue
        self.BTequeue = BTequeue
        self.olog = ""
        self.elog = ""
        self.port = int(port)
        self.protocol = protocol
        self.value = float(value)
        self.scores = Scores()
        self.uri = "GET /%s\r\n\r\n" % uri
        self.up = False
        self.functional = False
        self.content = content
        if self.content:
            if self.port != 80:
                self.content_re = re.compile(str(self.content))
        else:
            self.content_re = None
        if password:
            self.password = password
        else:
            self.password = "abcd1234"
        if username:
            self.username = username
        else:
            self.username = "blueteam"
        if isinstance(content, dict):
            self.loginpage = content.get("loginpage")
            self.user_param = content.get("user_param")
            self.pwd_param = content.get("pwd_param")
            self.pages = content.get("pages")
        self.mail_re = re.compile("220")
        self.msg_queue = queue

    def run(self):
        while True:
            item = self.msg_queue.get()
            if len(item) == 3:
                this_round = item[0]
                ipaddress = item[1]
                timeout = item[2]
                self.check(this_round, ipaddress, timeout)
                #print "Putting done for %s:%s/%s" % (self.hostname, self.port, self.protocol)
                self.msg_queue.put("Done")
            else:
                self.msg_queue.put(item)
            time.sleep(0.1)

    def check(self, this_round, ipaddress, timeout):
        service_name = "%s/%s" % (self.port, self.protocol)
        penalty = self.value
        data = ""
        if tcp_80_re.match(service_name):
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol)
                addrport = [ipaddress, self.port]
                mysock = socket.create_connection(addrport, timeout)
                mysock.settimeout(timeout)
                if globalvars.verbose:
                    self.elog += "connected!\n"
                    self.elog += "good\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * 1
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            try:
                pageindex = random.randint(0, len(self.pages)-1)
                current_page = self.pages[pageindex]
                if globalvars.verbose:
                    self.elog += "\t\t\tTrying to fetch %s..." % self.uri
                web_session = requests.Session()
                if self.loginpage:
                    payload = {
                        self.user_param: self.username,
                        self.pwd_param: self.password
                    }
                    web_session.post(
                        "http://{}{}".format(ipaddress, self.loginpage),
                        data=payload, timeout=timeout
                    )
                url = "http://{}{}".format(ipaddress, current_page.get("url"))
                result = web_session.get(url, timeout=timeout)
                try:
                    content_length = int(result.headers.get('content_length'))
                except:
                    content_length = len(result.text)
                content_min = current_page.get("size") - 100
                content_max = current_page.get("size") + 100
                if content_length >= content_min or content_length <= content_max:
                    if globalvars.verbose:
                        self.elog += "content length matched!\n"
                        self.elog += "good\n"
                else:
                    self.elog += "Content-length: {} did not current_page size: {}.\n".format(content_length, current_page.get("size"))
                    raise Exception('Content-length did not match size')
                if "keywords" in current_page.keys():
                    for keyword in current_page.get("keywords"):
                        if keyword not in result.text:
                            raise Exception(
                                'Keywords {} not matched'.format(keyword)
                            )
                self.set_score(this_round, self.value * 0)
            except Exception as e:
                if globalvars.verbose:
                    self.elog += "there was a problem...{}\n".format(e)
                penalty = self.value * 0.25
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
        elif tcp_21_re.match(service_name):
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol)
                myftp = ftplib.FTP(timeout=timeout)
                myftp.connect(ipaddress, self.port)
                if globalvars.verbose:
                    self.elog += "connected!\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * 1
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\t\tTrying to login with %s and %s..." % \
                                            (self.username, self.password)
                myftp.login(self.username, self.password)
                if globalvars.verbose:
                    self.elog += "success!\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * 0.75
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\t\tTrying to fetch %s..." % self.uri
                filename = "%s.%s" % (ipaddress, self.port)
                file_obj = open(filename, "w")
                myftp.set_pasv(False)
                myftp.retrbinary("RETR scoring_file.txt", file_obj.write)
                if globalvars.verbose:
                    self.elog += "requested...\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * 0.50
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\t\tChecking data..."
                file_obj = open(filename)
                for line in file_obj:
                    if score_str_re.match(line):
                        penalty = self.value * 0
                        if globalvars.verbose:
                            self.elog += "good\n"
                    else:
                        penalty = self.value * 0.25
                    self.set_score(this_round, penalty)
            except:
                if globalvars.verbose:
                    self.elog += "bad: %s\n" % data
                penalty = self.value * 0.333
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
        elif tcp_25_re.match(service_name):
            #self.set_score(this_round, 0)
            #self.elog += "NEED TO IMPLEMENT 25/TCP SCORE CHECKING!!\n"
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol)
                addrport = [ipaddress, self.port]
                mysock = socket.create_connection(addrport, timeout)
                mysock.settimeout(timeout)
                if globalvars.verbose:
                    self.elog += "connected!\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * 1
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\tSending HELO..."
                mysock.send("HELO mail")
                if globalvars.verbose:
                    self.elog += "sent...\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem:\n"
                penalty = self.value * .75
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
            try:
                if globalvars.verbose:
                    self.elog += "\t\t\tGetting data..."
                data = mysock.recv(1024)
                if globalvars.verbose:
                    self.elog += "fetched\n"
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * .50
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            ############################################
            if globalvars.verbose:
                self.elog += "\t\t\tChecking data..."
            if self.mail_re.search(data):
                if globalvars.verbose:
                    self.elog += "good\n"
                self.set_score(this_round, self.value * 0)
            else:
                if globalvars.verbose:
                    self.elog += "bad: %s\n" % data
                self.set_score(this_round, self.value * .25)
                return
            ############################################
        else:
            try:
                if globalvars.verbose:
                    self.elog += "\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol)
                addrport = [ipaddress, self.port]
                mysock = socket.create_connection(addrport, timeout)
                mysock.settimeout(timeout)
                if globalvars.verbose:
                    self.elog += "connected!\n"
                penalty = self.value * 0
                self.set_score(this_round, penalty)
            except:
                if globalvars.verbose:
                    self.elog += "there was a problem...\n"
                penalty = self.value * 1
                self.elog += traceback.format_exc()
                self.set_score(this_round, penalty)
                return
            service_name = "%s/%s" % (str(self.port), str(self.protocol))
            self.set_score(this_round, penalty)


    def get_score(self, this_round):
        return self.scores.get_score(this_round)

    def set_score(self, this_round, penalty=None):
        if penalty == None:
            penalty = self.value
        service_name = "%s/%s" % (str(self.port), str(self.protocol))
        if (penalty == self.value):
            self.up = False
            self.functional = False
        elif (penalty > 0):
            self.up = True
            self.functional = False
        else:
            self.up = True
            self.functional = True
        this_penalty = penalty
        this_value = self.value - this_penalty
        this_time = time.strftime('%X %x %Z')
        self.equeue.put(self.elog)
        self.oqueue.put(self.olog)
        msg = "%s Round %s host %s service %s score %s\n" % \
                    (this_time, this_round, self.hostname, service_name, this_value)
        print msg
        self.BToqueue.put(msg)
        self.scores.set_score(this_round, this_value)

    def get_state(self):
        # Returns 2 if up and functional
        # Returns 1 if up but not functional
        # Returns 0 if down
        return self.up + self.functional

    def get_scores(self):
        return self.scores

    def set_scores(self, scores):
        if isinstance(scores, Scores):
            self.scores = scores
        else:
            raise Exception("Invalid score object given!")

def main():
    myservice = Service(80, "tcp", "HTTP", 500)
    result = myservice.check("10.0.1.28", 3)
    print "Got %s " % result


if __name__ == "__main__":
    main()
