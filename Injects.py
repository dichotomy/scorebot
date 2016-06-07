'''
Created on Jan 7, 2012

@author:  dichotomy@riseup.net

Injects.py is a module in the scorebot program.  It's purpose is to manage and deliver Injects during a CTF competition.

Copyright (C) 2012  Dichotomy

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

    def __init__(self, smtp_ip=globalvars.goldcell_mail_svr):
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
        self.to_addresses = {}
        self.from_address = globalvars.goldcell_email
        self.teams = []
        self.did_time = None
        self.ticket_objs = {}

    def add_email(self, name, email):
        full_email = '"%s" <%s>' % (name, email)
        if name in self.to_addresses:
            pass
        else:
            self.to_addresses[name] = full_email

    def add_ticketobj(self, name, ticketobj):
        if name in self.ticket_objs:
            sys.stderr.write("Warning, overwriting ticket obj for %s" % name)
        self.ticket_objs[name] = ticketobj

    def run(self):
        #wait until an hour after gametime
        self.logger.out("Starting inject engine\n")
        interval = 60 * 30
        for name in self.injects.keys():
            go_time = time.time()
            self.injects[name].schedule(go_time)
            self.inject(name)
            time.sleep(interval)

    def add_inject(self, name, value, duration, category, set_ticket=False):
        if self.injects.has_key(name):
            self.logger.err("warning, clobbering inject %s" % name)
        else:
            self.logger.out("Adding inject %s\n" % name)
        self.injects[name] = Inject(name, value, duration, category, set_ticket)
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
        category = self.injects[name].get_category()
        if globalvars.verbose:
            self.logger.out("injecting %s...\n" % name)
        for team in self.to_addresses:
            self.logger.out("Sending to team %s" % team)
            to = self.to_addresses[team]
            self.mail(to, self.from_address, subject, message)
            if team in self.ticket_objs:
                self.ticket_objs[team].new_ticket(subject, message, category)

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

