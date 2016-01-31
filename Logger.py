'''
Created on Dec 27, 2011

@author:  dichotomy@riseup.net

Logger.py is a module in the scorebot program.  It's purpose is to write logs for all other modules.

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

import os
import os.path
import time
import Queue
import threading

class Logger(object):


    def __init__(self, basename, path="logs"):

        self.basename = basename
        if os.path.exists(path):
             pass
        else:
             os.mkdir(path)
        self.outfilename = "%s/%s.out" % (path, self.basename)
        self.errfilename = "%s/%s.err" % (path, self.basename)
        self.outfile = open(self.outfilename, "a")
        self.errfile = open(self.errfilename, "a")

    def out(self, message):
        now = time.strftime('%X %x %Z')
        self.outfile.write("%s|%s" % (now, message))
        self.outfile.flush()

    def write(self, message):
        self.err(message)

    def err(self, message):
        now = time.strftime('%X %x %Z')
        self.errfile.write("%s|%s" % (now, message))
        self.errfile.flush()

    def get_err_file(self):
        return self.errfile

    def get_out_file(self):
        return self.outfile

class QueueP(Queue.Queue):

    def __init__(self):
        Queue.Queue.__init__(self, "QueueP")

    def write(self, msg):
        self.put(msg)

class ThreadedLogger(threading.Thread):


    def __init__(self, basename, oqueue, equeue, path="logs"):
        threading.Thread.__init__(self)
        self.basename = basename
        self.oqueue = oqueue
        self.equeue = equeue
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        self.outfilename = "%s/%s.out" % (path, self.basename)
        self.errfilename = "%s/%s.err" % (path, self.basename)
        self.outfile = open(self.outfilename, "a")
        self.errfile = open(self.errfilename, "a")

    def run(self):
        while True:
            try:
                e_item = self.equeue.get(False)
                if e_item:
                    self.err(e_item)
                o_item = self.oqueue.get(False)
                if o_item:
                    self.out(o_item)
            except Queue.Empty:
                time.sleep(0.01)
                pass

    def out(self, message):
        now = time.strftime('%X %x %Z')
        self.outfile.write("%s|%s" % (now, message))
        self.outfile.flush()

    def write(self, message):
        self.err(message)

    def err(self, message):
        now = time.strftime('%X %x %Z')
        self.errfile.write("%s|%s" % (now, message))
        self.errfile.flush()

    def get_err_file(self):
        return self.errfile

    def get_out_file(self):
        return self.outfile
