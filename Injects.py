'''
Created on Jan 7, 2012

@author:  dichotomy@riseup.net

Injects.py is a module in the scorebot program.  It's purpose is to manage and deliver Injects during a CTF competition.

Copyright (C) 2012   Dichotomy

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
import time
import random
import smtplib
import traceback
import threading
from Inject import Inject
from Logger import Logger
import globalvars

class Injects(threading.Thread):
   '''
   classdocs
   '''

   def __init__(self, smtp_ip="10.150.100.70"):
      '''
      Constructor
      '''
      threading.Thread.__init__(self)
      self.logger = Logger("Injects")
      self.injects = {}
      self.schedule = {}
      self.durations = {}
      self.smtp_ip = smtp_ip
      self.smtpserver = smtplib.SMTP()
      self.start_time = time.time()
      self.to_addresses = ['"Alpha" <alpha@alpha.net>', \
                      '"Beta" <beta@beta.net>', \
                      '"Gamma" <gamma@gamma.net>', \
                      '"Delta" <delta@delta.net>', \
                      '"Epsilon" <epsilon@epsilon.net>'
                      ]
      self.from_address = '"Gold Team" <admin@goldteam.net>'
      self.teams = []
      self.did_time = None

   def run(self):
      #wait until an hour after gametime
      self.logger.out("Starting inject engine\n")
      interval = 10 * 60
      for name in self.injects.keys():
         go_time = time.time()
         self.injects[name].schedule(go_time)
         self.inject(name)
         time.sleep(interval)

      #go_time = self.start + 3600
      #durations_list = self.durations.keys()
      #durations_list.sort(reverse=True)
      #for duration in durations_list:
      #  name = self.durations[duration].name
      #  if globalvars.verbose:
      #     self.logger.out("Setting go time %s for %s\n" % (go_time, name))
      #  self.injects[name].schedule(go_time)
      #  self.schedule[go_time] = name
      #  go_time += int(random.random()*60)
      #go_times = self.schedule.keys()
      #go_times.sort()
      #for go_time in go_times:
      #  notdone = True
      #  while notdone:
      #     name = self.schedule[go_time]
      #     go_time_lt = time.localtime(go_time)
      #     if self.did_time:
      #       did_time_lt = time.localtime(self.did_time)
      #       if go_time_lt.tm_min == did_time_lt.tm_min:
      #         continue
      #       else:
      #         pass
      #     else:
      #       pass
      #     rightnow = time.time()
      #     rightnow_lt = time.localtime(rightnow)
      #     if go_time_lt.tm_mday == rightnow_lt.tm_mday:
      #       if go_time_lt.tm_hour == rightnow_lt.tm_hour:
      #         if go_time_lt.tm_min == rightnow_lt.tm_min:
      #           try:
      #              self.did_time = go_time
      #              self.inject(name)
      #              notdone = True
      #           except:
      #              traceback.print_exc(file=self.logger)
      #         elif go_time_lt.tm_min == (rightnow_lt.tm_min + 1):
      #           print "Counting down for %s: %s to %s..." % \
      #                (name, go_time, rightnow)
      #           time.sleep(1)
      #         else:
      #           print "Counting down for %s: %s to %s..." % \
      #                (name, go_time, rightnow)
      #           time.sleep(60)
      #       else:
      #         print "Counting down for %s: %s to %s..." % \
      #              (name, go_time, rightnow)
      #         time.sleep(60)
      #     else:
      #       time.sleep(60)

   def add_inject(self, name, value, duration):
      if self.injects.has_key(name):
         self.logger.err("warning, clobbering inject %s" % name)
      else:
         self.logger.out("Adding inject %s\n" % name)
      self.injects[name] = Inject(name, value, duration)
      self.durations[duration] = self.injects[name]

   def set_subject(self, name, subject):
      if self.injects.has_key(name):
         self.logger.out("Setting inject %s subject to %s\n" % \
              (name, subject))
         self.injects[name].set_subject(subject)
      else:
         self.logger.err("No such inject %s!\n" % name)

   def add_line(self, name, line):
      self.injects[name].add_line(line)

   def inject(self, name):
      message = self.injects[name].get_text()
      subject = self.injects[name].get_subject()
      if globalvars.verbose:
         self.logger.out("injecting %s...\n" % name)
      for to in self.to_addresses:
         self.mail(to, self.from_address, subject, message)

   def add_team(self, team):
      self.teams.append(team)

   def mail(self, to_addr, from_addr, subject, message):
      msg_header = "To:%s\r\nFrom:%s\r\nSubject:%s\r\n" % \
           (to_addr, from_addr, subject)
      full_email = "%s%s\r\n\r\n" % (msg_header, message)
      if globalvars.verbose:
         self.smtpserver.set_debuglevel(1)
      else:
         pass
      self.smtpserver.connect(self.smtp_ip)
      self.smtpserver.ehlo()
      self.smtpserver.sendmail(from_addr, to_addr, full_email)
      self.smtpserver.quit()

def main():
   '''
   unit tests for classes and their functions
   '''
   globalvars.verbose = True
   globalvars.quick = True
   injects = Injects()
   injects.add_inject("test", 100, 120)
   injects.set_subject("test", "this is a test inject")
   injects.add_line("test", "Do this inject or else!")
   injects.add_inject("test2", 100, 120)
   injects.set_subject("test2", "this is another test inject")
   injects.add_line("test2", "Do this inject or else, DUH!")
   injects.run()

if __name__ == "__main__":
   main()
