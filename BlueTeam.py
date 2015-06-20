#!/usr/bin/env python
'''
Created on Dec 18, 2011

@author: dichotomy@riseup.net

Blueteam.py is a module in the scorebot program.  It's purpose is to manage Blue Team assets and run scoring for services.

Copyright (C) 2011  Dichotomy

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

import sys
import traceback
import threading
import time
import Queue
import pprint
import globalvars
import jsonpickle
import re
from Host import Host
from Logger import Logger
from Scores import Scores
from FlagStore import FlagStore

del_host_blue_str = "Blueteam %s:  Deleting host %s\n"
del_host_blue_err_str = "Blueteam %s: No such host %s to delete\n"
add_host_blue_str = "Blueteam %s:  Adding host %s\n"
add_srvc_blue_str = "Blueteam %s:  Adding service %s/%s with value %s to host %s\n"
add_srvc_blue_err_str = "Blueteam %s:  Failed adding service %s/%s with value %s to host %s\n"
clobber_host_blue_str = "Blueteam %s:  clobbering host %s!\n"
host_re = re.compile("(\w+).*$")

class BlueTeam(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self, teamname, start_time, flags, this_round=1, current_score=0, id=None, db=None, queue=None, interval=300):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.id = id
        self.db = db
        self.queue_obj = queue
        now = time.strftime("%Y %b %d %H:%M:%S", time.localtime(time.time()))
        self.dns_servers = []
        self.teamname = teamname
        self.logger = Logger(self.teamname)
        self.logger.err("\n" + globalvars.sep + "\n")
        self.logger.err("| Starting run for Blueteam %s\n" % self.teamname)
        self.logger.err("| Start time: %s\n" % now)
        self.logger.out(globalvars.sep + "\n")
        self.logger.out("| Starting run for Blueteam %s\n" % self.teamname)
        self.logger.out("| Start time: %s\n" % now)
        self.hosts = {}
        self.hosts_rounds = {}
        self.host_queues = {}
        self.scores = Scores()
        self.start_time = start_time
        self.go_time = self.start_time
        self.interval = interval
        self.did_time = None
        # Number of rounds finished
        self.this_round = this_round
        self.flag_store = flags
        self.current_score = current_score
        self.last_flag_score = 0
        self.last_ticket_score = 0
        self.nets = []
        self.pp = pprint.PrettyPrinter(indent=2)
        self.email = ""
        self.ticket_obj = None
        self.inround = False

    def set_ticket_interface(self, ticket_obj):
        self.ticket_obj = ticket_obj

    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email

    def get_teamname(self):
         return self.teamname

    def add_flag(self, name, value, score=1, answer=""):
        self.flag_store.add(self.teamname, name, value, score, answer)

    def add_net(self, net):
        if net in self.nets:
            pass
        else:
            self.nets.append(net)

    def has_ip(self, ip):
        for net in self.nets:
            if net in ip:
                return True
        return False


    def run(self):
        print "Firing up Blueteam %s, go time is %s" % \
                        (self.teamname, self.go_time)
        if globalvars.quick:
            self.go_time = time.time() + 5
        for host in self.hosts:
            self.hosts[host].start()
        self.inround = False
        while True:
            # Check to see if we have any messages from our hosts
            for host in self.host_queues:
                try:
                    item = self.host_queues[host].get(False)
                    if item == "score":
                        #process the host message
                        if host in self.hosts_rounds:
                            print "Found message from host %s" % host
                            self.hosts_rounds[host] = True
                        else:
                            raise Exception("Unknown host %s\n" % host)
                    else:
                        self.host_queues[host].put(item)
                except Queue.Empty:
                    pass
                except:
                    traceback.print_exc(file=self.logger)
            score_round = True
            # Check to see if all hosts have finished the last round
            for host in self.hosts_rounds:
                if self.hosts_rounds[host]:
                    print "Host %s is ready" % host
                    continue
                else:
                    score_round = False
                    break
            if score_round:
                self.inround = False
                for host in self.hosts_rounds:
                    self.hosts_rounds[host] = False
                self.set_score()
                self.this_round += 1
            now = time.time()
            # Check to see if it's tme to start the new round, but only if the last is done
            if self.go_time <= now and not self.inround:
                try:
                    # Report times so that we know whether or not the last round ran too long
                    print "Starting Service check for Blueteam %s.  Go time was %s, now is %s." % \
                          (self.teamname, self.go_time, now)
                    for host in self.host_queues:
                        self.host_queues[host].put(["Go", self.this_round], 1)
                    new_go = self.go_time + self.interval
                    if new_go < now:
                        self.go_time = now + 60
                    else:
                        self.go_time = new_go
                    print "New go time is %s" % self.go_time
                    self.inround = True
                except:
                    traceback.print_exc(file=self.logger)
            else:
                time.sleep(0.1)

    def add_dns(self, dnssvr):
        if dnssvr in self.dns_servers:
            pass
        else:
            self.logger.out("Adding DNS %s to %s\n" % (dnssvr, self.teamname))
            self.dns_servers.append(dnssvr)
        for host in self.hosts:
            self.hosts[host].add_dns(dnssvr)

    def del_dns(self, dnssvr):
        if dnssvr in self.dns_servers:
            index = self.dns_servers.index(dnssvr)
            self.dns_servers.pop(index)
        else:
            pass
        for host in self.hosts:
            self.hosts[host].del_dns(dnssvr)

    def add_queue(self, queue):
        self.queue_obj = queue

    def add_host(self, hostname, value):
        # Have to strip "." because MongoDB doesn't like them for key names
        clean_hostname = hostname.replace(".", "___")
        if self.hosts.has_key(clean_hostname):
            self.logger.err(clobber_host_blue_str % (self.teamname, hostname))
        else:
            self.logger.err(add_host_blue_str % (self.teamname, hostname))
        this_queue = Queue.Queue()
        self.hosts[clean_hostname] = Host(hostname, value, self.logger, self.dns_servers, this_queue)
        self.hosts_rounds[clean_hostname] = False
        self.host_queues[clean_hostname] = this_queue

    def del_host(self, hostname):
        # Have to strip "." because MongoDB doesn't like them for key names
        clean_hostname = hostname.replace(".", "___")
        if self.hosts.has_key(clean_hostname):
            self.logger.err(del_host_blue_str % (self.teamname, hostname))
            del(self.hosts[clean_hostname])
        else:
            self.logger.err(del_host_blue_err_str % (self.teamname, hostname))

    def add_service(self, hostname, port, proto, value, uri=None, content=None,
                                username=None, password=None):
        # Have to strip "." because MongoDB doesn't like them for key names
        clean_hostname = hostname.replace(".", "___")
        if self.hosts.has_key(clean_hostname):
            self.logger.err(add_srvc_blue_str % \
                    (self.teamname, port, proto, value, hostname))
            self.hosts[clean_hostname].add_service(port, proto, value, uri, content, \
                                username, password)
        else:
            self.logger.err(add_srvc_blue_err_str % \
                    (self.teamname, port, proto, hostname))

    def del_service(self, hostname, port, proto):
        # Have to strip "." because MongoDB doesn't like them for key names
        clean_hostname = hostname.replace(".", "___")
        if self.hosts.has_key(clean_hostname):
            self.logger.err(add_srvc_blue_str % \
                    (self.teamname, port, proto, hostname))
            self.hosts[clean_hostname].del_service(port, proto, app, value)
        else:
            self.logger.err(add_srvc_blue_err_str % \
                    (self.teamname, port, proto, hostname))

    def get_score(self, this_round=None):
        if not this_round:
            this_round = self.this_round - 1
        #this_score = self.scores.get_score(this_round)
        this_score = self.scores.total()
        return [this_round, this_score]

    def get_all_rounds(self):
        scores = {}
        for round, score in self.scores:
            scores[round] = score
        return scores

    def get_scores(self):
        team_scores = {}
        team_scores["hosts"] = {}
        team_scores["teamscore"] = self.scores
        for host in self.hosts:
            host_score = self.hosts[host].get_scores()
            team_scores["hosts"][host] = host_score
        team_scores["round"] = self.this_round
        return team_scores

    def set_scores(self, team_scores):
        """  Function to import and process the json object exported by get_scores()
        """
        if "teamscore" in team_scores:
            self.scores = team_scores["teamscore"]
            if globalvars.debug:
                print "Set team score for %s to %s" % (self.teamname, self.scores)
                json_obj = jsonpickle.encode(self.scores)
                self.pp.pprint(json_obj)
        else:
            json_obj = jsonpickle.encode(team_scores)
            raise Exception ("Invalid team_scores hash, missing team score! \n%s\n" % json_obj)
        if "round" in team_scores:
            self.this_round = team_scores["round"]
            if globalvars.debug:
                print "Set round for %s to %s" % (self.teamname, self.this_round)
        else:
            json_obj = jsonpickle.encode(team_scores)
            raise Exception ("Invalid team_scores hash, missing round! \n%s\n" % json_obj)
        if "hosts" in team_scores:
            for host in self.hosts:
                if host in team_scores["hosts"]:
                    self.hosts[host].set_scores(team_scores["hosts"][host])
                else:
                    json_obj = jsonpickle.encode(team_scores)
                    raise Exception ("Invalid team_scores hash! \n%s\n" % json_obj)
        else:
            json_obj = jsonpickle.encode(team_scores)
            raise Exception ("Invalid team_scores hash, missing hosts! \n%s\n" % json_obj)

    def set_score(self, this_round=None, value=None):
        if this_round and value:
            this_round = self.this_round
            self.scores.set_score(this_round, value)
            return
        service_score = 0
        for host in self.hosts:
            service_score += self.hosts[host].get_score(self.this_round)
        (all_tickets, closed_tickets) = self.get_tickets()
        ticket_score = int(closed_tickets) * 1000
        if ticket_score == self.last_ticket_score:
            ticket_score = 0
        else:
            self.last_ticket_score = ticket_score
        if int(all_tickets) < int(closed_tickets):
            self.logger.err("There are more closed tickets than all for %s!" % self.teamname)
        if globalvars.binjitsu:
            flag_score = self.flag_store.score(self.teamname, self.this_round)
            if flag_score != self.last_flag_score:
                this_flag_score = flag_score - self.last_flag_score
                self.last_flag_score = flag_score * 1000
            else:
                this_flag_score = 0
            round_score = (this_flag_score - service_score )
        else:
            flag_score = self.flag_store.score(self.teamname, self.this_round)
            if flag_score != self.last_flag_score:
                this_flag_score = flag_score - self.last_flag_score
                round_score = (service_score + (this_flag_score * 1000))
                self.last_flag_score = flag_score
            else:
                round_score = service_score
        round_score += ticket_score
        self.scores.set_score(self.this_round, round_score)
        total = self.scores.total()
        print "Blueteam %s round %s scored %s for a new total of %s\n" % \
                  (self.teamname, self.this_round, round_score, total)
        print "Blueteam %s tally: %s\n" % (self.teamname, self.get_score())
        self.this_round += 1

    def get_health(self):
        host_hash = {}
        for host in self.hosts:
            name = self.hosts[host].hostname
            clean_name = host_re.match(name).groups()[0]
            service_hash = self.hosts[host].get_health()
            if host_hash.has_key(clean_name):
                self.logger.err("Found duplicate host %s" % name)
            else:
                host_hash[clean_name] = service_hash
        return host_hash

    def get_tickets(self):
        all_tickets = self.ticket_obj.get_team_tickets(self.teamname)
        closed_tickets = self.ticket_obj.get_team_closed(self.teamname)
        return all_tickets, closed_tickets



def main():
    '''
    unit tests for classes and their functions
    '''
    globalvars.verbose = True
    globalvars.quick = True
    queue_obj = Queue.Queue()
    hostname = "atlas.arnothde.net"
    score = 100
    mylog = Logger("blueteam_py_test")
    rightnow = time.time()+5
    blueteam = BlueTeam("Test", rightnow, interval=120)
    blueteam.add_host(hostname, score)
    blueteam.add_service(hostname, 80, "tcp", score)
    blueteam.add_queue(queue_obj)
    blueteam.start()



if __name__ == "__main__":
    main()
