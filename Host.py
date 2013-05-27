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
import traceback
import dns.resolver
import dns.exception
import Ping
import globalvars
from Scores import Scores
from Logger import Logger
from Service import Service

ctfnet_re = re.compile("^10")
score_str = "Round %s host %s scored %s\n" 

class Host:
   '''
   classdocs
   '''

   def __init__(self, hostname, value, logger, dns=None, timeout=300):
      '''
      Constructor
      '''
      self.hostname = hostname
      if dns:
         self.dns = dns
      else:   
         self.dns = dns.resolver.Resolver()
      self.logger = logger
      self.dns.lifetime = 3
      self.ipaddress = None
      self.compromised = False
      self.services = {}
      self.value = value
      self.scores = Scores()
      self.timeout = timeout

   def add_dns(self, dnssvr):
      if self.dns.nameservers.count(dnssvr):
         pass
      else:
         self.dns.nameservers.append(dnssvr)

   def del_dns(self, dnssvr):
      if self.dns.nameservers.count(dnssvr):
         index = self.dns.nameservers.index(dnssvr)
         self.dns.nameservers.pop(index)
      else:
         pass

   def lookup(self, record="A"):
      if globalvars.verbose:
         mydns= ""
         mydns = mydns.join(self.dns.nameservers)
         self.logger.err("Looking up %s with %s\n" % (self.hostname, mydns))
      try:
         answer = self.dns.query(self.hostname, record)
         ipaddress = answer[0].address
         if ctfnet_re.search(ipaddress):
            if globalvars.verbose:
               self.logger.err("got %s\n" % self.ipaddress)
            self.ipaddress = ipaddress
            return True
         else:
            self.logger.err("Got non RFC1918: %s\n" % ipaddress)
            return False
      except dns.exception.Timeout:
         if globalvars.verbose:
            self.logger.err("Request timed out\n")
         self.ipaddress = None
         return False
      except:
         traceback.print_exc(file=self.logger)
         return False

   def add_service(self, port, proto, app, value):
      service_name = "%s/%s" % (port, proto)
      if self.services.has_key(service_name):
         pass
      else:
         self.services[service_name] = Service(port, proto, app, value, \
               self.logger)

   def check(self, this_round):
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
               self.check_services(this_round)
            else:
               self.max_services(this_round)
            if globalvars.binjitsu:
               score = int(self.value) - (int(self.value)*percent_failed/100)
            else:
               score = int(self.value) * percent_failed / 100
            if globalvars.verbose:
               if score:
                  self.logger.err("%s failed: %s\n" % (self.hostname,score))
               else:
                  self.logger.err("%s scored: %s\n" % (self.hostname,score))
               pass
         else:
            self.max_services(this_round)
      except:
         traceback.print_exc(file=self.logger)
      self.set_score(this_round, score)
      return score

   def check_services(self, this_round):   
      if globalvars.verbose:
         self.logger.err("Checking services for %s:\n" % self.hostname)
      services = self.services.keys()
      for service in services:
         if globalvars.verbose:
            self.logger.err("\tChecking %s\n" % service)
         self.services[service].check(this_round, \
               self.ipaddress, self.timeout)

   def set_score(self, this_round, value=None):      
      if value == None:
         this_value = self.value
      else:
         this_value = value
      self.logger.out("Round %s host %s score %s\n" % \
               (this_round, self.hostname, this_value))
      self.logger.err("Round %s host %s score %s\n" % \
               (this_round, self.hostname, this_value))
      self.scores.set_score(this_round, this_value)

   def max_services(self, this_round):   
      if globalvars.verbose:
         self.logger.err("Maxing service scores for %s:\n" % self.hostname)
      services = self.services.keys()
      for service in services:
         if globalvars.verbose:
            self.logger.err("\tMaxing for %s:" % service)
         self.services[service].set_score(this_round)

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
