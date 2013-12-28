#!/usr/bin/python

import json
from BlueTeam import BlueTeam
from FlagStore import FlagStore
from Logger import Logger
import Queue
import time
#import pymongo
# from pprint import pprint

filename = "scorebotcfg.json"
config = open(filename)
blueteams_cfg, injects_cfg = config.read().split("\n\n\n")


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


def get_blueTeams(config, flag_store):
    blues = {}
    start_time = make_start_time()
    this_team = None
    raw_blueteams = config.split(",\n\n")
    for b in raw_blueteams:
        blueteam_json = json.loads(b)
        this_team = blueteam_json['name']
        blues[this_team] = BlueTeam(this_team, start_time, flag_store)
        blues[this_team].add_dns(blueteam_json['dns'])
        for host in blueteam_json['hosts'].keys():
            host_dict = blueteam_json['hosts'][host]
            hostname = host_dict['hostname']
            score = host_dict['score']
            services = host_dict['services']
            blues[this_team].add_host(hostname, score)
            for service in services:
                try:
                    content = service['content']
                except:
                    content = None
                try:
                    uri = service['uri']
                except:
                    uri = None
                try:
                    password = service['password']
                except:
                    password = None
                try:
                    username = service['username']
                except:
                    username = None
                port = service['port']
                protocol = service['protocol']
                service_score = service['service_score']
                blues[this_team].add_service(hostname, port, protocol,
                                             service_score, uri, content,
                                             username, password)
        flags = blueteam_json['flags']
        for flagname in blueteam_json['flags'].keys():
            flagvalue = flags[flagname]
            blues[this_team].add_flag(flagname, flagvalue)
    return blues

# config.close()

if __name__ == '__main__':
    flag_queue_obj = Queue.Queue()
    logger_obj = Logger("scorebot_test")
    flag_store = FlagStore(logger_obj, flag_queue_obj)
    blue_teams = get_blueTeams(blueteams_cfg, flag_store)
