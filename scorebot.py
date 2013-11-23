#!/usr/bin/python
'''

@autor:  dichotomy@riseup.net

scorebot.py is the main script of the scorebot program.  It is run from the command prompt of a Linux box for game time, taking in all options from the command line and config files, instanciating and running classes from all modules.

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

import getopt
import sys
import re
import os
import time
import Queue
import traceback

import threading
import globalvars
from Logger import Logger
from Inject import Inject
from Injects import Injects
from BlueTeam import BlueTeam
from FlagStore import FlagStore
from FlagServer import FlagServer
from Scoreboard import Scoreboard
from MessageStore import MessageStore

shortargs = "hbc:vdqn"
longargs = ["help", "verbose", "debug", "quick", "binjitsu", "config=", \
            "nomovie"]
team_header_re = re.compile("BLUETEAM (\S+)")
inject_header_re = re.compile("INJECT (\S+):(\d+):(\d+) HEAD")
inject_subject_re = re.compile("INJECT SUBJECT: (.*)$")
inject_footer_re = re.compile("INJECT FOOTER")
comment_re = re.compile("^#")
comma_re = re.compile(",")
dns_re = re.compile("DNS=")
flag_re = re.compile("FLAG=(\S+),(.+)")
uri_re = re.compile("uri:(.+)")
password_re = re.compile("password:(.+)")
username_re = re.compile("username:(.+)")
content_re = re.compile("content:(.+)")
host_configline_re = re.compile(".+:\d+=\d+/\w+-\d+")
globalvars.verbose = False
globalvars.binjitsu = False
globalvars.nomovie = False
usage_str = """
   Usage:  %s [options]
   
   Options:
      --help 
      --quick
      --binjitsu
      --verbose
      --debug
      --config=<filename>
"""
injects = Injects()

def make_start_time():
   rightnow = time.time()
   rightnow_lt = time.localtime(rightnow)
   # Let's start at the next 5 minute interval
   ones = rightnow_lt.tm_min % 10
   tens = rightnow_lt.tm_min - ones
   if ones < 5:
      next_tens = tens + 5
   else:   
      next_tens = tens + 10
   time_tuple = (rightnow_lt.tm_year, rightnow_lt.tm_mon, \
         rightnow_lt.tm_mday, rightnow_lt.tm_hour, next_tens, \
         rightnow_lt.tm_sec, rightnow_lt.tm_wday, rightnow_lt.tm_yday, \
         rightnow_lt.tm_isdst)
   # Return the time when the clock starts
   return time.mktime(time_tuple)

def usage():
   sys.stdout.write(usage_str % sys.argv[0])
   sys.exit(2)

def read_config(cfg_file, flag_store):
   blues = {}
   file_obj = open(cfg_file)
   this_team = None
   start_time = make_start_time()
   in_inject = False
   inject_name = None
   dns = None
   for line in file_obj:
      line = line.rstrip('\r\n')
      # Logging statement
      if globalvars.verbose:
         sys.stderr.write("Read:  %s\n" % line)
      else:
         pass
      # match lines
      if team_header_re.match(line):
         if in_inject:
            sys.stderr.write("Premature match on team_header_re:%s" % line)
         else:
            pass
         team_header_re_obj = team_header_re.match(line)
         this_team = team_header_re_obj.groups()[0]
         blues[this_team] = BlueTeam(this_team, start_time, flag_store)
      elif comment_re.search(line):
         continue
      elif inject_header_re.match(line):
         inject_header_re_obj = inject_header_re.match(line)
         (inject_name, value, duration) = inject_header_re_obj.groups()
         injects.add_inject(inject_name, value, duration)
         in_inject = True
      elif inject_footer_re.match(line):
         inject_name = None
         in_inject = False
      elif inject_subject_re.match(line):
         inject_subject_re_obj = inject_subject_re.match(line)
         subject = inject_subject_re_obj.groups()[0] 
         injects.set_subject(inject_name, subject)
      elif host_configline_re.search(line):
         if in_inject:
            sys.stderr.write("Premature match on host_config_re:%s" % line)
         else:
            pass
         (hostname_value, services_values_str) = line.split("=")
         (hostname, value) = hostname_value.split(":")
         this_host = blues[this_team].add_host(hostname, value)
         services_values = services_values_str.split(",")
         services = []
         for service_value in services_values:
            parts = service_value.split("-")
            (service, value) = parts[0:2]
            remaining_parts = parts[2:]
            content = None
            uri = None
            password = None
            username = None
            for part in remaining_parts:
               if content_re.match(part):
                  (content,) = content_re.match(part).groups()
               elif uri_re.match(part):
                  (uri,) = uri_re.match(part).groups()
               elif password_re.match(part):
                  (password,) = password_re.match(part).groups()
               elif username_re.match(part):
                  (username,) = username_re.match(part).groups()
               else:
                  sys.stderr.write("Bad config line: \n\t%s\n" % line)
                  sys.stderr.write("Failure to parse service %s\n" % \
                                    service_value)
            (port, proto) = service.split("/")
            blues[this_team].add_service(hostname, port, proto, value, \
                                             uri, content, username, password)
      elif in_inject:
         injects.add_line(inject_name, line)
      elif dns_re.match(line):
         (garbage, dns) = dns_re.split(line)
         blues[this_team].add_dns(dns)
         dns = None
      elif flag_re.match(line):
         flag_match_obj = flag_re.match(line)
         parts = flag_match_obj.groups()
         if len(parts) == 2:
            (name, value) = parts
            blues[this_team].add_flag(name, value)
         elif len(parts) == 3:
            (name, score, value) = parts
            blues[this_team].add_flag(name, value, score)
      else:
         sys.stderr.write("Warning, bad config line:\n\t%s\n" % line)
   for team in blues.keys():
      injects.add_team(team)
   return blues
   
def main():
   try:
      opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
   except getopt.GetoptError, err:
      sys.stderr.write("Had a problem: %s" % err)
      traceback.print_exc(file=sys.stderr)
   output = None
   cfg_file = "scorebot.cfg"
   for o, a in opts:
      if o in ("-h", "--help"):
         usage()
         sys.exit()
      elif o in ("-c", "--config"):
         cfg_file = a
      elif o in ("-b", "--binjitsu"):
         globalvars.binjitsu = True
      elif o in ("-v", "--verbose"):
         globalvars.verbose = True
      elif o in ("-q", "--quick"):
         globalvars.quick = True
      elif o in ("-q", "--quick"):
         globalvars.quick = True
      elif o in ("-n", "--nomovie"):
         globalvars.nomovie = True
      else:
         assert False, "unhandled option"
   flag_queue_obj = Queue.Queue()
   message_queue_obj = Queue.Queue()
   logger_obj = Logger("scorebot")
   flag_store = FlagStore(logger_obj, flag_queue_obj)
   message_store = MessageStore(logger_obj, message_queue_obj)
   flag_server = FlagServer(logger_obj, flag_queue_obj, message_queue_obj)
   t = threading.Thread(target=flag_server.serve_forever)
   t.start()
   blue_teams = read_config(cfg_file, flag_store)      
   myscoreboard = Scoreboard(blue_teams, flag_store, message_store)
   myscoreboard.start()
   for team in blue_teams.keys():
      blue_teams[team].add_queue(flag_queue_obj)
      blue_teams[team].start()
   flag_store.start()
   message_store.start()
   injects.start()   

if __name__ == "__main__":
   main()
