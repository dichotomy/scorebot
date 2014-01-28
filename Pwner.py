'''
Created on Dec 18, 2011

@author: dichotomy@riseup.net

Pwner.py is a module in the scorebot program.  It's purpose is to track pwnerships.

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

class Pwner(object):
	'''
	classdocs
	'''


	def __init__(self, name):
		'''
		Constructor
		'''
		self.name = name
		self.scores = Scores()
