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
import sys
import traceback
import SocketServer
import globalvars
import socket
import re

class FlagHandler(SocketServer.BaseRequestHandler):

   def __init__(self, request, client_address, server):
      self.msg_re = re.compile("(\S+),(.+)")
      self.reg_re = re.compile("(register:)(.+)")
      SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

   def handle(self):
      # self.request is the client connection
      data = self.request.recv(1024)  # clip input at 1Kb
      if data:
         clean_data = data.strip()
         if self.msg_re.match(clean_data):
            reply = self.msg_re.match(clean_data)
            self.server.logger.out("%s:%d sent |%s|\n" % 
                         (self.client_address[0], self.client_address[1], 
                          data.strip()))
            if reply:
               self.server.queue.put([0, reply])
               self.request.send(data)
            else:
               self.request.send("What are you trying to pull?!?")
         elif self.reg_re.match(clean_data):
            reply = self.reg_re.match(clean_data)
            (label, bandit) = reply.groups()
            self.server.logger.out("%s:%d sent |%s|\n" % 
                         (self.client_address[0], self.client_address[1], 
                          data.strip()))
            if reply:
               self.server.queue.put([1, reply])
               self.request.send("Registration for %s acknowledged" %
                               bandit)
            else:
               self.request.send("What are you trying to pull?!?")
      else:
         self.server.logger.out("%s:%d sent null message\n" % 
                         (self.client_address[0], self.client_address[1]))
      self.request.close()


class FlagServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
   '''
   classdocs
   '''

   def __init__(self, logger, queue, port=50007, handler=FlagHandler):
      '''
      Constructor
      '''
      self.logger = logger
      self.queue = queue
      SocketServer.TCPServer.__init__(self, ('', port), handler)
      return

   def server_activate(self):
      self.logger.out("Flag Server started\n")
      SocketServer.TCPServer.server_activate(self)
      return 

   def serve_forever(self):
      self.logger.out("Waiting for request\n")
      while True:
         self.handle_request()
      return

   def verify_request(self, request, client_addr):
      self.logger.out("%s:%d connected\n" % client_addr)
      return SocketServer.TCPServer.verify_request(self, request, client_addr)

   def shutdown_request(self, request):
      client_addr = request.getsockname()
      self.logger.out("%s:%d closing connection\n" % (client_addr))
      return SocketServer.TCPServer.shutdown_request(self, request)


def main():
   '''
   unit tests for classes and their functions
   '''
   import threading
   import time
   import Queue
   from Logger import Logger

   globalvars.verbose = True
   globalvars.quick = True
   queue_obj = Queue.Queue()
   mylog = Logger("flagserver_py_test")
   server = FlagServer(mylog, queue_obj)
   t = threading.Thread(target=server.serve_forever)
   #t.setDaemon(True)
   t.start()


if __name__ == "__main__":
   main()
