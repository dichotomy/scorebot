'''
Created on Aug 23, 2012

@author:  dichotomy@riseup.net

FlagServer.py is a module in the scorebot program.  It's purpose is to manage submissions of flags during a competition.

Copyright (C) 2012 Dichotomy

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

__author__ = 'dichotomy'

import random

class Host(object):

    def __init__(self, name):
        self.name = name
        self.website = False
        self.database = False

    def set_database(self):
        self.database = True

    def set_website(self):
        self.website = True

    def make_flag(self):
        return hex(int(random.random()*1000000000))

