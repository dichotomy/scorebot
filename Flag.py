'''
Created on Aug 24, 2012

@author: dichotomy@riseup.net

Flag.py is a module in the scorebot program.  It's purpose is to track a flag's data in the program.

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


class Flag:

    def __init__(self, team, name, value, score=None):
        self.team = str(team)
        self.name = str(name)
        self.value = str(value)
        if score:
            self.score = int(score)
        else:
            self.score = 1

    def get_team(self):
        return self.team

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_score(self):
        return self.score

    def set_team(self, team):
        self.team = str(team)

    def set_name(self, name):
        self.name = str(name)

    def set_value(self, value):
        self.value = str(value)

    def set_score(self, score):
        self.score = int(score)
