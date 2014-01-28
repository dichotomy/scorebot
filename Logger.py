'''
Created on Dec 27, 2011

@author:  dichotomy@riseup.net

Logger.py is a module in the scorebot program.	It's purpose is to write logs for all other modules.

Copyright (C) 2011	Dichotomy

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA	02110-1301, USA.
'''

class Logger:


	def __init__(self, basename):

		self.basename = basename
		self.outfilename = self.basename + ".out"
		self.errfilename = self.basename + ".err"
		self.outfile = open(self.outfilename, "a")
		self.errfile = open(self.errfilename, "a")

	def out(self, message):
		self.outfile.write(message)
		self.outfile.flush()

	def write(self, message):
		self.err(message)

	def err(self, message):
		self.errfile.write(message)
		self.errfile.flush()

	def get_err_file(self):
		return self.errfile

	def get_out_file(self):
		return self.outfile
