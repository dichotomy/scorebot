'''
Created on Aug 24, 2012

@author:  dichotomy@riseup.net

FlagStore.py is a module in the scorebot program.  It's purpose is to manage flags during a competition.

Copyright (C) 2012  Dichotomy

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
from Flag import Flag
from pymongo import MongoClient
web_dir = "/var/www"

class FlagStore(threading.Thread):

   def __init__(self, logger, queue, dbname):
      threading.Thread.__init__(self)
      self.logger = logger
      self.queue_obj = queue
      self.flags = {}
      self.teams = {}
      self.theft = {}
      self.bogus = {}
      self.bandits = {}
      self.integrity = {}
      self.conn = MongoClient()
      self.db = self.conn[dbname]

   def run(self):
      while True:
         flag = None
         try:
            message = self.queue_obj.get(True, 1)
            msg_type = message[0]
            match_obj = message[1]
            if msg_type == 0:
               (thief, flag) = match_obj.groups()
               self.logger.out("Got %s:%s\n" % (thief, flag))
               name = self.find(flag)
               # Is this a real flag?
               if name:
                  print "recieved %s from %s" % (thief, flag)
                  team = self.flags[name].get_team()
                  # Is this a real team?
                  if self.teams.has_key(team):
                     if self.teams[team].has_key(name):
                        self.teams[team][name].append(thief)
                     else:
                        self.teams[team][name] = [thief]
                     if self.theft.has_key(thief):
                        self.theft[thief].append(name)
                     else:
                        self.theft[thief] = [name]
                     if self.bandits.has_key(thief):
                        self.bandits[thief].append(name)
                        self.db.bandits.update({"bandit_name": thief},
                                               {"$push": {"stolen": name}})
                     else:
                        pass #do nothing, because bandits need to reg
                  else:
                     msg = "Flag %s has a bad team value:%s\n"
                     self.logger.err(msg % (flag, team))
               else:
                  self.logger.out("Didn't find a team for %s:%s\n" %
                                  (thief, name))
                  if self.bogus.has_key(thief):
                     self.bogus[thief].append(flag)
                  else:
                     self.bogus[thief] = [flag]
            elif msg_type == 1:
               (label, bandit) = match_obj.groups()
               if self.bandits.has_key(bandit):
                  msg = "\t%s already registered once, ignoring...\n"
                  self.logger.out(msg)
               else:
                  self.bandits[bandit] = []
                  self.db.bandits.insert({"bandit_name": bandit, "stolen: []})
                  self.logger.out("%s registered\n" % bandit)
            elif msg_type == 2:
               (team, flag) = match_obj.groups()
               self.logger.out("Got integrity sumbission %s:%s\n" % (team,flag))
               name = self.find(flag)
               # Is this a real flag?
                  if name:
                     self.logger.out("Received %s from %s\n" % (flag, team))

                  if self.integrity.has_key(team):
                     self.integrity[team].append(name)
                  else:
                     self.integrity[team] = []
                     self.integrity[team].append(name)
               else:
                  msg = "Flag %s from team %s does not exist\n"
                  self.logger.err(msg % (flag, team))
            else:
               self.logger.out("Unrecognized code %s\n" % msg_type)
         except Queue.Empty, err:
            time.sleep(1)
            pass
         except:
            my_traceback = traceback.format_exc()
            err = sys.exc_info()[0]
            self.logger.out("Had a problem: %s\n%s\n" % (err, my_traceback))


   def score(self, team, round):
      stolen = 0
      lost = 0
      # find out how l33t they are
      self.logger.out("Team %s, round %s:\n" % (team, round))
      if self.theft.has_key(team):
         #on the board, not bad, but how much?...
         for name in self.theft[team]:
            stolen += self.flags[name].get_score()
         stolen = len(self.theft[team])
         self.logger.out("\tStole %s\n" % (",".join(self.theft[team])))
      else:
         # lame...get on with it!
         pass
      # We take points for lost flags - did they lose any???
      if self.teams.has_key(team):
         # Let's see.....
         lost_flags = len(self.teams[team].keys())
         if lost_flags:
            # uhoh....
            for name in self.teams[team].keys():
               score = self.flags[name].get_score()
               lost += (len(self.teams[team][name]) * score)
            self.logger.out("\tLost %s\n" %
                              (",".join(self.teams[team].keys())))
         else:
            # skillz!  (or...no worthy opponents... ;-)
            pass
      if self.integrity.has_key(team):
         integrity_score = len(self.integrity[team])
         self.logger.out("\tIntegrity %s\n" %
                              (",".join(self.integrity[team])))
      # do the math...
      if globalvars.binjitsu:
         flag_score = stolen - (lost * .5) + integrity_score
      else:
         flag_score = lost - integrity_score
      return flag_score

   def add(self, team, name, value, score=None):
      #initialize our score-keeping variables as new team names come in
      if self.teams.has_key(team):
         pass
      else:
         self.teams[team] = {}
      if self.theft.has_key(team):
         pass
      else:
         self.theft[team] = []
      if self.integrity.has_key(team):
         pass
      else:
         self.integrity[team] = []
      flag_name = "%s_%s" % (team, name)
      self.logger.out("Adding %s:%s:%s\n\tfor team %s\n" %
                        (flag_name,value,score,team))
      this_flag = Flag(team, flag_name, value, score)
      flag_team = this_flag.get_team()
      flag_name = this_flag.get_name()
      flag_value = this_flag.get_value()
      self.logger.out("Set    %s:%s\n\tfor team %s\n" % \
                         (flag_name,flag_value,flag_team))
      if self.flags.has_key(name):
         old_value = self.flags[flag_name].get_value()
         self.logger.out("Clobbering team %s flag %s:%s with %s:%s\n" %
                         (team, name, old_value, flag_name, value))
      self.flags[flag_name] = this_flag

   def get(self, name):
      return self.flags[name].get_value()

   def rem(self, name):
      if self.flags.has_key(name):
         value = self.flags[name].get_value()
         del self.flags[name]
         return value
      else:
         return None

   def find(self, value):
      for name in self.flags.keys():
         this_value = self.flags[name].get_value()
         if this_value == value:
            return name
      return None

   def get_lost(self, team):
      flags_by_name = []
      if self.teams.has_key(team):
         for name in self.teams[team].keys():
            flag_only = name.replace(team+"_", "")
            flags_by_name.append(flag_only)
      return flags_by_name

   def get_integrity(self, team):
      flags_by_name = []
      if self.integrity.has_key(team):
         for name in self.integrity[team]:
            flag_only = name.replace(team+"_", "")
            flags_by_name.append(flag_only)
      return flags_by_name

   def get_stolen(self, team):
      flags_by_name = []
      if self.theft.has_key(team):
         for name in self.theft[team]:
            flags_by_name.append(name)
      return flags_by_name

   def get_bogus(self, team):
      raw_flags = []
      if self.bogus.has_key(team):
         for flag in self.bogus[team].keys():
            raw_flags.append(flag)
      return raw_flags

   def get_bandits(self):
      return self.bandits


def getnum(min, max):
   number = 0
   while (min >= number) or (number > max):
      number = int(random.random()*(max+1))
   return number

def main():
   from Logger import Logger
   import Queue
   import random
   msg_re = re.compile("(\S+),(\S+)")
   queue = Queue.Queue()
   logger = Logger("Flagstest")
   flagstore_obj = FlagStore(logger, queue)
   flagstore_obj.start()
   # set up a pretend CTF
   teams = ["alpha", "beta", "gamma"]
   flags = {}
   for team in teams:
      max_flag = 20
      for count in range(max_flag):
         flag = int(random.random()*100000000000)
         name = "%s_%d" % (team, flag)
         flagstore_obj.add(team, name, flag)
         if flags.has_key(team):
            flags[team].append(flag)
         else:
            flags[team] = [flag]
         print "Team %s got flag %s:%s" % (team, name, flag)
   # Simulate a game (LOL!  ;)
   rounds = getnum(5, 10)
   print "we're going for %d rounds!" % rounds
   for round in range(rounds):
      # what's the score?
      for team in teams:
         score = flagstore_obj.score(team)
         print "Team %s received %s points in round %s" % (team, score, round)
      # How many things happen?
      action_num = getnum(1,5)
      print "Round %d, going for %d actions!" % (round, action_num)
      # What happens?
      for action in range(action_num):
         #action = getnum(1,4)
         action = 1
         thief = None
         flag = None
         if action == 1:   #Uhoh, someone stole a flag!
            thief_index = getnum(0, (len(teams)-1))
            thief = teams[thief_index]
            victim_index = thief_index
            while victim_index==thief_index:
               victim_index = getnum(0, (len(teams)-1))
               victim = teams[victim_index]
            flag_index = getnum(0, (len(flags[victim])-1))
            flag = flags[victim][flag_index]
            print "Team %s stole %s from team %s" % (thief, flag, victim)
         elif action == 2:  #hehe, someone faked a flag!!
            thief_index = getnum(0, (len(teams)-1))
            thief = teams[thief_index]
            flag = random.random()*100000000
            print "Team %s faked %s!" % (thief, flag)
         elif action == 3: #someone faked a team!  WTF?
            team = int(random.random()*100000000)
            victim_index = getnum(0, (len(teams)-1))
            victim = teams[victim_index]
            flag_index = getnum(0, (len(flags[victim])-1))
            flag = flags[victim][flag_index]
            print "Fake team %s stole %s from team %s" % (team, flag, victim)
         elif action == 4:  #well now you're just making shit up
            thief = int(random.random() * 1000000)
            flag = int(random.random()*100000000)
            print "Fake team %s faked %s!" % (thief, flag)
         # Make it so!
         msg = "%s,%s" % (thief, flag)
         queue_msg = msg_re.match(msg)
         queue.put(queue_msg)
      time.sleep(10)

if __name__ == "__main__":
   main()
