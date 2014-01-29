#!/usr/bin/python

import getopt
import json
import Queue
import time
import re
import sys
import globalvars
import threading
import traceback
from FlagServer import FlagServer
from MessageStore import MessageStore
from Scoreboard import Scoreboard
from Injects import Injects
from BlueTeam import BlueTeam
from FlagStore import FlagStore
from Logger import Logger
import pymongo
# from pprint import pprint

shortargs = "hbc:rvdqn"
longargs = ["help", "verbose", "debug", "quick", "binjitsu", "config=",
            "nomovie", "resume"]

globalvars.verbose = False
globalvars.binjitsu = False
globalvars.nomovie = False
usage_str = """
   Usage:  %s [options]

   Options:
      --help
      --quick
      --binjitsu
      --verbose
      --debug
      --config=<filename>
"""

filename = "scorebotcfg.json"
config = open(filename)
blueteams_cfg, injects_cfg = config.read().split("\n\n\n")
inject_header_re = re.compile("INJECT (\S+):(\d+):(\d+) HEAD")
inject_subject_re = re.compile("INJECT SUBJECT: (.*)$")
inject_footer_re = re.compile("INJECT FOOTER")

injects = Injects()

dbname = "scorebot-%s-%s".replace(" ", "") % (time.strftime("%X"),
                                              time.strftime("%x").replace("/", ""))

def make_start_time():
    rightnow = time.time()
    rightnow_lt = time.localtime(rightnow)
    ones = rightnow_lt.tm_min % 10
    tens = rightnow_lt.tm_min - ones
    if ones < 5:
        next_tens = tens + 5
    else:
        next_tens = tens + 10
    time_tuple = (rightnow_lt.tm_year, rightnow_lt.tm_mon,
                  rightnow_lt.tm_mday, rightnow_lt.tm_hour, next_tens,
                  rightnow_lt.tm_sec, rightnow_lt.tm_wday, rightnow_lt.tm_yday,
                  rightnow_lt.tm_isdst)
    # Return the time when the clock starts
    return time.mktime(time_tuple)


def usage():
    sys.stdout.write(usage_str % sys.argv[0])
    sys.exit(2)


def get_blueTeams(config, flag_store):
    conn = pymongo.MongoClient()
    db = conn[dbname]
    blues = {}
    start_time = make_start_time()
    this_team = None
    raw_blueteams = config.split(",\n\n")
    for b in raw_blueteams:
        blueteam_json = json.loads(b)
        team_doc_id = db.game.insert(blueteam_json)
        this_team = str(blueteam_json['name'])
        blues[this_team] = BlueTeam(this_team, start_time, flag_store, team_doc_id, db.game)
        blues[this_team].add_dns(str(blueteam_json['dns']))
        for host in blueteam_json['hosts'].keys():
            host_dict = blueteam_json['hosts'][host]
            hostname = str(host_dict['hostname'])
            score = str(host_dict['score'])
            services = host_dict['services']
            blues[this_team].add_host(hostname, score)
            for service in services:
                try:
                    content = str(service['content'])
                except:
                    content = None
                try:
                    uri = str(service['uri'])
                except:
                    uri = None
                try:
                    password = str(service['password'])
                except:
                    password = None
                try:
                    username = str(service['username'])
                except:
                    username = None
                port = str(service['port'])
                protocol = str(service['protocol'])
                service_score = str(service['service_score'])
                blues[this_team].add_service(hostname, port, protocol,
                                             service_score, uri, content,
                                             username, password)
        flags = blueteam_json['flags']
        for flagname in blueteam_json['flags'].keys():
            flagvalue = str(flags[flagname])
            blues[this_team].add_flag(str(flagname), flagvalue)
    return blues


def resume_blueTeams(flag_store):
    conn = pymongo.MongoClient()
    db = conn[dbname]
    blues = {}
    start_time = make_start_time()
    this_team = None
    for b in db.game.find():
        blueteam_json = b
        team_doc_id = blueteam_json['_id']
        this_team = str(blueteam_json['name'])
        current_round = int(blueteam_json['current_round'])
        team_score = int(blueteam_json['team_score'])
        blues[this_team] = BlueTeam(this_team, start_time, flag_store, current_round, team_score, team_doc_id, db.game)
        blues[this_team].add_dns(str(blueteam_json['dns']))
        for host in blueteam_json['hosts'].keys():
            host_dict = blueteam_json['hosts'][host]
            hostname = str(host_dict['hostname'])
            score = str(host_dict['score'])
            services = host_dict['services']
            blues[this_team].add_host(hostname, score)
            for service in services:
                try:
                    content = str(service['content'])
                except:
                    content = None
                try:
                    uri = str(service['uri'])
                except:
                    uri = None
                try:
                    password = str(service['password'])
                except:
                    password = None
                try:
                    username = str(service['username'])
                except:
                    username = None
                port = str(service['port'])
                protocol = str(service['protocol'])
                service_score = str(service['service_score'])
                blues[this_team].add_service(hostname, port, protocol,
                                             service_score, uri, content,
                                             username, password)
        flags = blueteam_json['flags']
        for flagname in blueteam_json['flags'].keys():
            flagvalue = str(flags[flagname])
            blues[this_team].add_flag(str(flagname), flagvalue)
    return blues


def get_injects(inject_file, blues):
    in_inject = False
    inject_name = None
    for line in inject_file:
        line.rstrip('\r\n')
        if inject_header_re.match(line):
            inject_header_re_obj = inject_header_re.match(line)
            (inject_name, value, duration) = inject_header_re_obj.groups()
            injects.add_inject(inject_name, value, duration)
            in_inject = True
        elif inject_footer_re.match(line):
            inject_name = None
            in_inject = False
        elif inject_subject_re.match(line):
            inject_subject_re_obj = inject_subject_re.match(line)
            subject = inject_subject_re_obj.groups()[0]
            injects.set_subject(inject_name, subject)
        elif in_inject:
            injects.add_line(inject_name, line)
        else:
            sys.stderr.write("Waring, bad config line:\n\t%s\n" % line)
    for team in blues.keys():
        injects.add_team(team)


def main():
    resume = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
    except getopt.GetoptError, err:
        sys.stderr.write("Had a problem: %s" % err)
        traceback.print_exc(file=sys.stderr)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--config"):
            config = a
        elif o in ("-b", "--binjitsu"):
            globalvars.binjitsu = True
        elif o in ("-v", "--verbose"):
            globalvars.verbose = True
        elif o in ("-q", "--quick"):
            globalvars.quick = True
        elif o in ("-q", "--quick"):
            globalvars.quick = True
        elif o in ("-n", "--nomovie"):
            globalvars.nomovie = True
        elif o in ("-r", "--resume"):
            resume = True
        else:
            assert False, "unhandled option"
    if resume:
        filename = "scorebotcfg.json"
        config = open(filename)
        blueteams_cfg, injects_cfg = config.read().split("\n\n\n")
        flag_queue_obj = Queue.Queue()
        message_queue_obj = Queue.Queue()
        logger_obj = Logger("scorebot")
        flag_store = FlagStore(logger_obj, flag_queue_obj, dbname)
        message_store = MessageStore(logger_obj, message_queue_obj)
        flag_server = FlagServer(logger_obj, flag_queue_obj, message_queue_obj)
        t = threading.Thread(target=flag_server.serve_forever)
        t.start()
        blue_teams = resume_blueTeams(flag_store)
        get_injects(config, blue_teams)
        myscoreboard = Scoreboard(blue_teams, flag_store, message_store)
        myscoreboard.start()
        for team in blue_teams.keys():
            blue_teams[team].add_queue(flag_queue_obj)
            blue_teams[team].start()
        flag_store.start()
        message_store.start()
        injects.start()
    else:
        filename = "scorebotcfg.json"
        config = open(filename)
        blueteams_cfg, injects_cfg = config.read().split("\n\n\n")
        flag_queue_obj = Queue.Queue()
        message_queue_obj = Queue.Queue()
        logger_obj = Logger("scorebot")
        flag_store = FlagStore(logger_obj, flag_queue_obj, dbname)
        message_store = MessageStore(logger_obj, message_queue_obj)
        flag_server = FlagServer(logger_obj, flag_queue_obj, message_queue_obj)
        t = threading.Thread(target=flag_server.serve_forever)
        t.start()
        blue_teams = get_blueTeams(blueteams_cfg, flag_store)
        get_injects(config, blue_teams)
        myscoreboard = Scoreboard(blue_teams, flag_store, message_store)
        myscoreboard.start()
        for team in blue_teams.keys():
            blue_teams[team].add_queue(flag_queue_obj)
            blue_teams[team].start()
        flag_store.start()
        message_store.start()
        injects.start()

if __name__ == '__main__':
    main()
