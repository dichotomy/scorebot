#!/usr/bin/env python3

'''

@autor:  dichotomy@riseup.net

scorebot.py is the main script of the scorebot program.  It is run from the command prompt of a Linux box for game time, taking in all options from the command line and config files, instanciating and running classes from all modules.

Copyright (C) 2017 Dichotomy

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
import urllib.request
import json
import time
import sys


class ScoreMachine(object):

    def __init__(self):
        self.url = "http://10.200.100.110/api/scoreboard/7/"
        f = urllib.request.urlopen(self.url)
        self.this_check = self.proc_json(f.read().decode('utf-8'))
        self.last_check = None

    def proc_json(self, json_str):
        json_obj = json.loads(json_str)
        this_check = {}
        for team in json_obj["teams"]:
            team_name = team["name"]
            this_check[team_name] = {}
            for host in team["hosts"]:
                hostname = host["name"]
                this_check[team_name][hostname] = {}
                this_check[team_name][hostname]["online"] = host["online"]
                this_check[team_name][hostname]["services"] = {}
                for service in host["services"]:
                    protocol = service["protocol"]
                    port = service["port"]
                    service_name = "%s_%s" % (protocol, port)
                    status = service["status"]
                    this_check[team_name][hostname]["services"][service_name] = status
        return this_check

    def get_json(self):
        f = urllib.request.urlopen(self.url)
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.last_check = self.this_check
        self.this_check = self.proc_json(f.read().decode('utf-8'))
        for team in self.this_check:
            for host in self.this_check[team]:
                old_online = self.last_check[team][host]["online"]
                new_online = self.this_check[team][host]["online"]
                if old_online != new_online:
                    sys.stdout.write("INFO     %s changed: old %s | new %s | %s %s online state \n" %
                                        (now, old_online, new_online, team, host))
                for service_name in self.this_check[team][host]["services"]:
                    old_status = self.last_check[team][host]["services"][service_name]
                    new_status = self.this_check[team][host]["services"][service_name]
                    if old_status != new_status:
                        sys.stdout.write("INFO     %s changed: old %s | new %s | %s %s service %s \n" %
                                         (now, old_status, new_status, team, host, service_name ))

if __name__ == "__main__":
    sm = ScoreMachine()
    while True:
        sm.get_json()
