'''
Created on Jul 31, 2013

@author:  dichotomy@riseup.net

FlagStore.py is a module in the scorebot program.  It's purpose is to manage flags during a competition.

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
import re
import sys
import time
import Queue
import random
import threading
import traceback
import globalvars

class MessageStore(threading.Thread):

   def __init__(self, logger, queue):
      threading.Thread.__init__(self)
      self.logger = logger
      self.queue_obj = queue
      self.messages = []
      self.current_message = "This is Scorebot v1.0"
      self.messages.append(self.current_message)

   def run(self):
      while True:
         message = None
         try:
            self.current_message = self.queue_obj.get(True, 1)
            self.messages.append(self.current_message)
         except Queue.Empty, err:
            time.sleep(1)
            pass
         except:
            my_traceback = traceback.format_exc()
            err = sys.exc_info()[0]
            self.logger.out("Had a problem: %s\n%s\n" % (err, my_traceback))

   def get_message(self):
      return self.current_message
