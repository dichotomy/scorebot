#!/usr/bin/env python
'''
Created on Dec 18, 2011

@author: dichtomy@riseup.net

Scores.py is a module in the scorebot program.  It's purpose is to track scores for a given team or Redcell player

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

class Scores(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.latest_round = 1
        self.rounds = {}
        self.itteration = 1


    def new_score(self, value):
        self.latest_round += 1
        self.rounds[self.latest_round] = int(value)

    def total(self):
        total = 0
        for this_round in self.rounds:
            total += self.rounds[this_round]
        return total

    def get_score(self, this_round=None):
        which_round = self.latest_round
        score = 0
        if this_round:
            which_round = int(this_round)
        if which_round in self.rounds:
            score = self.rounds[which_round]
        return score

    def set_score(self, this_round, value):
        self.rounds[int(this_round)] = int(value)
        self.latest_round += 1

    def dump(self):
        print self.rounds

    def __iter__(self):
          return self

    def next(self):
        if self.itteration < self.latest_round:
            score = self.rounds[self.itteration]
            self.itteration += 1
            return self.itteration-1, score
        else:
            self.itteration = 1
            raise StopIteration

if __name__ == "__main__":
    import random
    score_obj = Scores()
    for n in range(1,10):
        score = int(random.random()*100)
        score_obj.set_score(n, score)
        print "Round %s; Score %s" % (n, score)
    round = 0
    for round, score in score_obj:
        print "Round %s; Score %s" % (round, score)
    for round, score in score_obj:
        print "Round %s; Score %s" % (round, score)

