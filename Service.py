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
import ftplib
import socket
import traceback
import globalvars
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

class Service(object):
    '''
    classdocs
    '''

    def __init__(self, port, protocol, value, logger, uri="index.html", \
                            content=None, username=None, password=None):
        '''
        Constructor
        '''
        self.logger = logger
        self.port = int(port)
        self.protocol = protocol
        self.value = float(value)
        self.scores = Scores()
        self.uri = "GET /%s\r\n\r\n" % uri
        self.up = False
        self.functional = False
        self.content = content
        if self.content:
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
        self.mail_re = re.compile("220")

    def check(self, this_round, ipaddress, timeout):
        service_name = "%s/%s" % (self.port, self.protocol)
        myscore = self.value
        if tcp_80_re.match(service_name):
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol))
                addrport = [ipaddress, self.port]
                mysock = socket.create_connection(addrport, timeout)
                mysock.settimeout(timeout)
                if globalvars.verbose:
                    self.logger.err("connected!\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * 1
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\t\tTrying to fetch %s..." % self.uri)
                mysock.send(self.uri)
                if globalvars.verbose:
                    self.logger.err("requested...\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem:\n")
                myscore = self.value * .75
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\t\tGetting data...")
                data = mysock.recv(4098)
                if globalvars.verbose:
                    self.logger.err("fetched\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * .50
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            if globalvars.verbose:
                self.logger.err("\t\t\tChecking data...")
            if self.content_re:
                if self.content_re.search(data):
                    if globalvars.verbose:
                        self.logger.err("good\n")
                    self.set_score(this_round, self.value * 0)
                    return myscore
                else:
                    if globalvars.verbose:
                        self.logger.err("bad: %s\n" % data)
                    self.set_score(this_round, self.value * .25)
                    return myscore
            elif score_str_re.search(data):
                if globalvars.verbose:
                    self.logger.err("good\n")
                self.set_score(this_round, self.value * 0)
                return myscore
            elif html1_str_re.search(data):
                if globalvars.verbose:
                    self.logger.err("good\n")
                self.set_score(this_round, self.value * 0)
                return myscore
            elif html2_str_re.search(data):
                if globalvars.verbose:
                    self.logger.err("good\n")
                self.set_score(this_round, self.value * 0)
                return myscore
            elif html3_str_re.search(data):
                if globalvars.verbose:
                    self.logger.err("good\n")
                self.set_score(this_round, self.value * 0)
                return myscore
            elif html4_str_re.search(data):
                if globalvars.verbose:
                    self.logger.err("good\n")
                self.set_score(this_round, self.value * 0)
                return myscore
            else:
                if globalvars.verbose:
                    self.logger.err("bad: %s\n" % data)
                self.set_score(this_round, self.value * .25)
                return myscore
        elif tcp_21_re.match(service_name):
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol))
                myftp = ftplib.FTP(timeout=timeout)
                myftp.connect(ipaddress, self.port)
                if globalvars.verbose:
                    self.logger.err("connected!\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * 1
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\t\tTrying to login with %s and %s..." % \
                                            (self.username, self.password))
                myftp.login(self.username, self.password)
                if globalvars.verbose:
                    self.logger.err("success!\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * 0.75
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\t\tTrying to fetch %s..." % self.uri)
                filename = "%s.%s" % (ipaddress, self.port)
                file_obj = open(filename, "w")
                myftp.set_pasv(False)
                myftp.retrbinary("RETR scoring_file.txt", file_obj.write)
                if globalvars.verbose:
                    self.logger.err("requested...\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * 0.50
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\t\tChecking data...")
                file_obj = open(filename)
                for line in file_obj:
                    if score_str_re.match(line):
                        myscore = self.value * 0
                        if globalvars.verbose:
                            self.logger.err("good\n")
                    else:
                        myscore = self.value * 0.25
                    self.set_score(this_round, myscore)
                    return myscore
            except:
                if globalvars.verbose:
                    self.logger.err("bad: %s\n" % data)
                myscore = self.value * 0.333
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
        elif tcp_25_re.match(service_name):
            #self.set_score(this_round, 0)
            #self.logger.err("NEED TO IMPLEMENT 25/TCP SCORE CHECKING!!\n")
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol))
                addrport = [ipaddress, self.port]
                mysock = socket.create_connection(addrport, timeout)
                mysock.settimeout(timeout)
                if globalvars.verbose:
                    self.logger.err("connected!\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * 1
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\tSending HELO..." )
                mysock.send("HELO mail")
                if globalvars.verbose:
                    self.logger.err("sent...\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem:\n")
                myscore = self.value * .75
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            try:
                if globalvars.verbose:
                    self.logger.err("\t\t\tGetting data...")
                data = mysock.recv(1024)
                if globalvars.verbose:
                    self.logger.err("fetched\n")
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * .50
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            ############################################
            if globalvars.verbose:
                self.logger.err("\t\t\tChecking data...")
            if self.mail_re.search(data):
                if globalvars.verbose:
                    self.logger.err("good\n")
                self.set_score(this_round, self.value * 0)
                return myscore
            else:
                if globalvars.verbose:
                    self.logger.err("bad: %s\n" % data)
                self.set_score(this_round, self.value * .25)
                return myscore
            ############################################
        else:
            try:
                if globalvars.verbose:
                    self.logger.err("\t\tChecking for service %s/%s..." \
                        % (self.port, self.protocol))
                addrport = [ipaddress, self.port]
                mysock = socket.create_connection(addrport, timeout)
                mysock.settimeout(timeout)
                if globalvars.verbose:
                    self.logger.err("connected!\n")
                myscore = self.value * 0
                self.set_score(this_round, myscore)
                return myscore
            except:
                if globalvars.verbose:
                    self.logger.err("there was a problem...\n")
                myscore = self.value * 1
                traceback.print_exc(file=self.logger)
                self.set_score(this_round, myscore)
                return myscore
            service_name = "%s/%s" % (str(self.port), str(self.protocol))
            self.set_score(this_round, myscore)


    def get_score(self, this_round):
        return self.scores.get_score(this_round)

    def set_score(self, this_round, value=None):
        if value == None:
            value = self.value
        service_name = "%s/%s" % (str(self.port), str(self.protocol))
        if (value == self.value):
            self.up = False
            self.functional = False
        elif (value > 0):
            self.up = True
            self.functional = False
        else:
            self.up = True
            self.functional = True
        if globalvars.binjitsu:
            this_value = self.value - value
        else:
            this_value = value
        self.logger.out("Round %s service %s score %s\n" % \
                    (this_round, service_name, this_value))
        self.logger.err("Round %s service %s score %s\n" % \
                    (this_round, service_name, this_value))
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
