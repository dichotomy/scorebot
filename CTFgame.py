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

import time
import Queue
import pprint
import threading
import traceback
import jaraco.modb
import globalvars
from bson.objectid import ObjectId
from decoder import *
from Logger import Logger, ThreadedLogger, QueueP
from FlagStore import FlagStore
from FlagServer import FlagServer
from JsonConfig import JsonConfig
from MessageStore import MessageStore
from BottleServer import BottleServer
from Movies import Movies


class CTFgame(threading.Thread):

    def __init__(self, db_col, cfg_file="scorebotcfg.json", obj_id=None):
        threading.Thread.__init__(self)
        self.col = db_col
        self.flag_queue = Queue.Queue()
        self.flag_answer_queue = Queue.Queue()
        self.msg_queue = Queue.Queue()
        self.logger_obj = Logger("scorebot")
        self.oqueue = Queue.Queue()
        self.equeue = Queue.Queue()
        self.logger = ThreadedLogger("ctfgame.log", self.oqueue, self.equeue)
        self.logger.start()
        self.pp = pprint.PrettyPrinter(indent=2)
        self.blues_queues = {}
        self.teams_rounds = {}
        # todo - fix why this isn't actually the first round!
        self.this_round = 1
        self.interval = 120
        self.inround = False
        self.go_time = time.time()
        self.save_time = time.time()
        self.save_interval = 10
        if obj_id:
            bson_id = ObjectId(obj_id)
            self.obj_id = bson_id
            json_obj = self.col.find_one(self.obj_id)
            if globalvars.debug:
                self.pp.pprint(json_obj)
            game = jaraco.modb.decode(decode_dict(json_obj))
            if "config" in game:
                self.flag_store = FlagStore(self.logger_obj, self.flag_queue, self.flag_answer_queue)
                self.json_cfg_obj = JsonConfig(cfg_file, self.flag_store)
                (self.blue_teams, self.injects) = self.json_cfg_obj.process(game["config"])
            else:
                raise Exception("No config section in restore object!")
            self.message_store = MessageStore(self.logger_obj, self.msg_queue)
            self.flag_server = FlagServer(self.logger_obj, self.flag_queue, self.flag_answer_queue, self.msg_queue)
            for team in self.blue_teams.keys():
                self.blue_teams[team].add_queue(self.flag_queue)
            if "scores" in game:
                scores = game["scores"]
                if "blueteams" in scores:
                    for team in self.blue_teams:
                        if team in scores["blueteams"]:
                            blue_score = scores["blueteams"][team]
                            self.blue_teams[team].set_scores(blue_score)
                        else:
                            raise Exception("Missing scores for team %s in restore object!" % team)
                else:
                    raise Exception("Missing blueteams score block in restore object!" % team)
            else:
                raise Exception("Missing scores block in restore object!" % team)
            if "flags" in game:
                all_flags = game["flags"]
                self.flag_store.restore(all_flags)
        else:
            self.obj_id = obj_id
            self.flag_store = FlagStore(self.logger_obj, self.flag_queue, self.flag_answer_queue)
            self.json_cfg_obj = JsonConfig(cfg_file, self.flag_store)
            (self.blue_teams, self.injects) = self.json_cfg_obj.process()
            self.message_store = MessageStore(self.logger_obj, self.msg_queue)
            self.flag_server = FlagServer(self.logger_obj, self.flag_queue, self.flag_answer_queue, self.msg_queue)
            for team in self.blue_teams.keys():
                self.blue_teams[team].add_queue(self.flag_queue)
                blue_queue = Queue.Queue()
                self.blues_queues[team] = blue_queue
                self.blue_teams[team].set_queue(blue_queue)
                self.teams_rounds[team] = True
        self.movies = Movies(self.logger_obj)
        #self.movies.set_movie()
        self.bottle_server = BottleServer(self.blue_teams, self.flag_store, self.message_store, self.movies, '0.0.0.0', 8090)

    def run(self):
        pp = pprint.PrettyPrinter(indent=2)
        self.inround = False
        while True:
            now = time.time()
            if self.save_time <= now:
                json_obj = self.build_json()
                if self.obj_id:
                    json_obj["_id"] = self.obj_id
                if globalvars.debug:
                    pp.pprint(json_obj)
                self.obj_id = self.col.save(json_obj)
                self.oqueue.put("Saved Game ID %s" % self.obj_id)
                self.save_time += self.save_interval
            for team in self.blues_queues:
                try:
                    item = self.blues_queues[team].get(False)
                    if item == "Done":
                        #process the host message
                        if team in self.teams_rounds:
                            #print "Found message from team %s" % team
                            self.teams_rounds[team] = True
                        else:
                            raise Exception("Unknown team %s\n" % team)
                    else:
                        self.blues_queues[team].put(item)
                except Queue.Empty:
                    pass
                except:
                    traceback.print_exc(file=self.logger_obj)
            score_round = True
            # Check to see if all hosts have finished the last round
            donemsg = ""
            finished = []
            not_finished = []
            for team in self.teams_rounds:
                if self.teams_rounds[team]:
                    donemsg += "%s, " % team
                    finished.append(team)
                else:
                    score_round = False
                    not_finished.append(team)
            if donemsg:
                failmsg = "Failed: "
                for team in self.teams_rounds:
                    if not self.teams_rounds[team]:
                        failmsg += team
                #sys.stdout.write("Done: %s\n" % donemsg)
                #sys.stdout.write(failmsg)
            if score_round:
                self.inround = False
                for team in self.teams_rounds:
                    self.teams_rounds[team] = False
            now = time.time()
            statfile = open("status/scorebot.status", "w")
            statfile.write("Round %s, teams %s not finished\n" % (self.this_round, ",".join(not_finished)))
            statfile.write("Round %s, teams %s finished\n" % (self.this_round, ", ".join(finished)))
            statfile.write("Go time:   %s\nNow time:  %s\n" % (self.go_time, now))
            statfile.close()
            if self.go_time <= now and not self.inround:
                try:
                    # Report times so that we know whether or not the last round ran too long
                    for team in self.blues_queues:
                        self.oqueue.put("Starting Service check for Blueteam %s.  Go time was %s, now is %s." % (team, self.go_time, now))
                        self.blues_queues[team].put(["Go", self.this_round], 1)
                    self.this_round += 1
                    self.go_time += self.interval
                    self.oqueue.put("New go time is %s" % self.go_time)
                    self.inround = True
                except:
                    traceback.print_exc(file=self.logger_obj)
            else:
                time.sleep(1)

    def build_json(self):
        # master hash for the whole thing
        game = {}
        # Get the config json
        json_config = self.json_cfg_obj.get_json()
        game["config"] = json_config
        # build the hash for the service scores
        scores = {}
        blueteam_scores = {}
        for blueteam in self.blue_teams:
            blue_score = self.blue_teams[blueteam].get_scores()
            if blue_score:
                blueteam_scores[blueteam] = blue_score
        scores["blueteams"] = blueteam_scores
        # Add the scores json to the game level json
        game["scores"] = scores
        # Get the flags json
        flags = self.flag_store.get_all_flags()
        #Add the flags to the game hash
        game["flags"] = flags
        #Convert the master hash to json
        json_obj = jaraco.modb.encode(game)
        return json_obj

    def start_game(self):
        t = threading.Thread(target=self.flag_server.serve_forever)
        t.start()
        # Get this party started!
        #self.myscoreboard.start()
        for team in self.blue_teams.keys():
            self.blue_teams[team].start()
        self.flag_store.start()
        self.message_store.start()
        self.injects.start()
        self.bottle_server.start()
