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
import globalvars
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


    def __init__(self, basename, path="logs"):
        threading.Thread.__init__(self)
        self.basename = basename
        self.oqueue = QueueP()
        self.equeue = QueueP()
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        self.outfilename = "%s/%s.out" % (path, self.basename)
        self.errfilename = "%s/%s.err" % (path, self.basename)
        self.outfile = open(self.outfilename, "a")
        self.errfile = open(self.errfilename, "a")

    def get_oqueue(self):
        return self.oqueue

    def get_equeue(self):
        return self.equeue

    def run(self):
        while True:
            try:
                if globalvars.verbose:
                    eqsze = self.equeue.qsize()
                    oqsze = self.oqueue.qsize()
                    if eqsze > 0:
                        print "B Log %s equeue has %s logs" % (self.basename, eqsze)
                    if oqsze > 0:
                        print "B Log %s oqueue has %s logs" % (self.basename, oqsze)
                e_item = self.equeue.get(False)
                if e_item:
                    self.put_err(e_item)
                o_item = self.oqueue.get(False)
                if o_item:
                    self.put_out(o_item)
                if globalvars.verbose:
                    eqsze = self.equeue.qsize()
                    oqsze = self.oqueue.qsize()
                    if eqsze > 0:
                        print "B Log %s equeue has %s logs" % (self.basename, eqsze)
                    if oqsze > 0:
                        print "B Log %s oqueue has %s logs" % (self.basename, oqsze)
            except Queue.Empty:
                time.sleep(0.01)
                pass

    def put_out(self, message):
        now = time.strftime('%X %x %Z')
        self.outfile.write("%s|%s" % (now, message))
        self.outfile.flush()

    def write(self, message):
        self.err(message)

    def put_err(self, message):
        now = time.strftime('%X %x %Z')
        self.errfile.write("%s|%s" % (now, message))
        self.errfile.flush()

    def get_err_file(self):
        return self.errfile

    def get_out_file(self):
        return self.outfile
