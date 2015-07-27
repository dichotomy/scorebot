'''
Created on Dec 18, 2011

@author:  dichotomy@riseup.net

Inject.py is a module in the scorebot program.  It's purpose is to manage and deliver Injects during a CTF competition.

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
import time
import smtplib
import globalvars
from Scores import Scores

class Inject(object):
    '''
    classdocs
    '''


    def __init__(self, name, value, duration, category, ticket=False):
        '''
        Constructor
        '''
        self.name = name
        self.value = int(value)
        self.category = category
        self.duration = int(duration) * 60
        self.challenge = ""
        self.response = ""
        self.end_time = None
        self.delivery = "\r\n\r\nThis task is to be completed by %s today."
        self.subject = ""
        self.scores = Scores()
        self.ticket = ticket

    def add_line(self, line):
        self.challenge += line

    def set_subject(self, subject):
        self.subject = subject

    def schedule(self, start_time):
        self.end_time = int(start_time) + self.duration
        end_time_lt = time.localtime(self.end_time)
        end_time_str = time.strftime("%a, %d %b %Y at %H:%M", end_time_lt)
        self.delivery = self.delivery % end_time_str

    def get_text(self):
        message = self.challenge
        message += self.delivery
        return message

    def get_subject(self):
        return self.subject

    def get_category(self):
        return self.category
