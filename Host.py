'''
Created on Dec 18, 2011

@author: dichotomy@riseup.net

Copyright (C) 2011  Dichotomy

Host.py is a module in the scorebot program.  It's purpose is to manage Host information during a competition.

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
import Queue
import traceback
import threading
import DNS
import Ping
import globalvars
import jsonpickle
from Scores import Scores
from Logger import Logger
from Service import Service

ctfnet_re = re.compile("^10")
score_str = "Round %s host %s scored %s\n"
DNS.ParseResolvConf()

class Host(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self, teamname, hostname, value, logger, dns_servers, msgqueue, timeout=300):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.dns_servers = dns_servers
        basename = "%s-%s" % (teamname, hostname)
        self.logger = Logger(basename)
        self.ipaddress = None
        self.compromised = False
        self.services = {}
        self.service_queues = {}
        self.service_rounds = {}
        self.value = value
        self.scores = Scores()
        self.timeout = timeout
        self.msgqueue = msgqueue

    def add_dns(self, dnssvr):
        if dnssvr in self.dns_servers:
            pass
        else:
            self.dns_servers.append(dnssvr)

    def del_dns(self, dnssvr):
        if dnssvr in self.dns_servers:
            index = self.dns.nameservers.index(dnssvr)
            self.dns_servers.pop(index)
        else:
            pass

    def lookup(self, record="A"):
        if globalvars.verbose:
            mydns = ", ".join(self.dns_servers)
            self.logger.err("Looking up %s with %s\n" % (self.hostname, mydns))
        try:
            for svr in self.dns_servers:
                # We set a short timeout because life moves too fast...so does the game!
                r = DNS.DnsRequest(self.hostname, qtype="A", server=[svr], protocol='udp', timeout=60)
                res = r.req()
                for answer in res.answers:
                    if answer["data"]:
                        ipaddress = answer["data"]
                        break
                    else:
                        self.logger.err("Failed to get DNS!")
            if ctfnet_re.search(ipaddress):
                if globalvars.verbose:
                    self.logger.err("got %s\n" % self.ipaddress)
                self.ipaddress = ipaddress
                return True
            else:
                self.logger.err("Got non RFC1918: %s\n" % ipaddress)
                return False
        except:
            traceback.print_exc(file=self.logger)
            self.ipaddress = None
            return False

    def add_service(self, teamname, port, proto, value, uri=None, content=None, \
                                username=None, password=None):
        service_name = "%s/%s" % (port, proto)
        if self.services.has_key(service_name):
            pass
        this_queue = Queue.Queue()
        self.services[service_name] = Service(port, proto, value, \
                    teamname , this_queue, self.hostname, uri, content, username, password)
        self.service_rounds[service_name] = False
        self.service_queues[service_name] = this_queue

    def run(self):
        for service in self.services:
            self.services[service].start()
        while True:
            # Check to see if we have any messages from our services
            for service in self.service_queues:
                try:
                    item = self.service_queues[service].get(False)
                    if item == "Done":
                        # process the service message
                        if service in self.service_rounds:
                            self.service_rounds[service] = True
                        else:
                            raise Exception("Unknown service %s" % service)
                    else:
                        self.service_queues[service].put(item)
                except Queue.Empty:
                    pass
                except:
                    traceback.print_exc(file=self.logger)
            score_round = True
            # Check to see if all our services have finished the last round
            for service in self.service_rounds:
                if self.service_rounds[service]:
                    #sys.stdout.write("Host %s service %s done\n" % (self.hostname, service))
                    continue
                else:
                    score_round = False
                    break
            if score_round:
                for service in self.service_rounds:
                    self.service_rounds[service] = False
                self.msgqueue.put("score")
            # Check to see if we have any messages from our team object
            item = None
            try:
                item = self.msgqueue.get(False)
            except Queue.Empty:
                continue
            # Evaluate the result
            if len(item) == 2:
                #print "Found ", item
                # The round has begun!
                if item[0] == "Go":
                    this_round = item[1]
                else:
                    raise Exception("Unknown queue message %s!" % item[0])
                score = int(self.value)
                try:
                    if self.lookup():
                        if globalvars.verbose:
                            self.logger.err("Checking for %s(%s) with ping...\n" \
                                    % (self.hostname, self.ipaddress))
                        myping = Ping.Ping()
                        results = myping.quiet_ping(self.ipaddress)
                        percent_failed = int(results[0])
                        if percent_failed < 100:
                            # The host seems up, check the services
                            self.check_services(this_round)
                        else:
                            self.fail_services(this_round)
                        if globalvars.binjitsu:
                            score = int(self.value) - (int(self.value)*percent_failed/100)
                        else:
                            score = int(self.value) * percent_failed / 100
                        if globalvars.verbose:
                            if score:
                                self.logger.err("%s failed: %s\n" % (self.hostname,score))
                            else:
                                self.logger.err("%s scored: %s\n" % (self.hostname,score))
                        else:
                            pass
                    else:
                        self.fail_services(this_round)
                except:
                    traceback.print_exc(file=self.logger)
                self.set_score(this_round, score)
            elif item:
                # This isn't for me...
                self.msgqueue.put(item)
            else:
                # Didn't get back anything!  Naptime...
                time.sleep(0.1)

    def check_services(self, this_round):
        if globalvars.verbose:
            self.logger.err("Checking services for %s:\n" % self.hostname)
        for service_name in self.service_queues:
            if globalvars.verbose:
                self.logger.err("\tHost %s queueing Service Check %s\n" % (self.name, service_name))
            self.service_queues[service_name].put([this_round, self.ipaddress, self.timeout])

    def set_score(self, this_round, value=None):
        if value == None:
            this_value = self.value
        else:
            this_value = value
        this_time = time.strftime('%X %x %Z')
        self.logger.out("%s Round %s host %s score %s\n" % \
                    (this_time, this_round, self.hostname, this_value))
        self.logger.err("Round %s host %s score %s\n" % \
                    (this_round, self.hostname, this_value))
        self.scores.set_score(this_round, this_value)

    def fail_services(self, this_round):
        if globalvars.verbose:
            self.logger.err("Failing service scores for %s:\n" % self.hostname)
        services = self.services.keys()
        for service in services:
            if globalvars.verbose:
                self.logger.err("\tFailing for %s:" % service)
            self.services[service].set_score(this_round)
            self.service_rounds[service] = True

    def get_score(self, this_round):
        try:
            score = 0
            score += self.scores.get_score(this_round)
            services = self.services.keys()
            for service in services:
                score += self.services[service].get_score(this_round)
            return score
        except:
            self.logger.err("Had a problem with host %s:\n" % self.hostname)
            traceback.print_exc(file=self.logger)
            return False

    def get_health(self):
        service_hash = {}
        for service in self.services:
            name = "%s/%s" % (self.services[service].port, \
                        self.services[service].protocol)
            state = self.services[service].get_state()
            if service_hash.has_key(name):
                self.logger.err("Found duplicate service %s" % name)
            else:
                service_hash[name] = state
        return service_hash

    def get_scores(self):
        services_scores = {}
        for service in self.services:
            services_scores[service] = self.services[service].get_scores()
        host_total_scores = {"host":self.scores, "services": services_scores}
        return host_total_scores

    def set_scores(self, host_total_scores):
        """  Function to import and process the json object exported by get_scores()
        """
        if "host" in host_total_scores:
            self.scores = host_total_scores["host"]
        else:
            json_obj = jsonpickle.encode(host_total_scores)
            raise Exception ("Invalid team_scores hash, missing host score! \n%s\n" % json_obj)
        if "services" in host_total_scores:
            for service in self.services:
                if service in host_total_scores["services"]:
                    self.services[service].set_scores(host_total_scores["services"][service])
                else:
                    json_obj = jsonpickle.encode(host_total_scores)
                    raise Exception ("Invalid service score hash in scores! \n%s\n" % json_obj)
        else:
            json_obj = jsonpickle.encode(host_total_scores)
            raise Exception ("Invalid team_scores hash, missing services scores! \n%s\n" % json_obj)



def main():
    '''
    unit tests for classes and their functions
    '''
    globalvars.verbose = True
    mylog = Logger("host_py_test")
    hostobj = Host("atlas1.arnothde.net", 100, mylog, dnssvr="10.0.1.50")
    hostobj.del_dns("8.8.8.8")
    hostobj.lookup()
    sys.stdout.write("Found: %s\n" % hostobj.ipaddress)
    score = hostobj.check(1)
    sys.stdout.write("Score returned %s:  %s\n" % (hostobj.ipaddress, score))
    score = hostobj.get_score(1)
    print score



if __name__ == "__main__":
    main()
