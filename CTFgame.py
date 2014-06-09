#!/usr/bin/env python
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

__author__ = 'dichotomy'

import Queue
import threading
from Logger import Logger
from FlagStore import FlagStore
from FlagServer import FlagServer
from Scoreboard import Scoreboard
from JsonConfig import JsonConfig
from MessageStore import MessageStore


class CTFgame(object):

    def __init__(self, cfg_file):
        self.flag_queue_obj = Queue.Queue()
        self.message_queue_obj = Queue.Queue()
        self.logger_obj = Logger("scorebot")
        self.flag_store = FlagStore(self.logger_obj, self.flag_queue_obj)
        self.json_cfg_obj = JsonConfig(cfg_file, self.flag_store)
        (self.blue_teams, self.injects) = self.json_cfg_obj.process()
        self.message_store = MessageStore(self.logger_obj, self.message_queue_obj)
        self.flag_server = FlagServer(self.logger_obj, self.flag_queue_obj, self.message_queue_obj)
        self.myscoreboard = Scoreboard(self.blue_teams, self.flag_store, self.message_store)
        for team in self.blue_teams.keys():
            self.blue_teams[team].add_queue(self.flag_queue_obj)

    def start_game(self):
        t = threading.Thread(target=self.flag_server.serve_forever)
        t.start()
        # Get this party started!
        self.myscoreboard.start()
        for team in self.blue_teams.keys():
            self.blue_teams[team].start()
        self.flag_store.start()
        self.message_store.start()
        self.injects.start()

