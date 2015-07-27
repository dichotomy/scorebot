#!/usr/bin/python
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
import json
from Injects import Injects
from BlueTeam import BlueTeam
from TicketInterface import *

class JsonConfig(object):

    def __init__(self, filename, flag_store, params=None):
        self.filename = filename
        self.config = None
        self.flag_store = flag_store
        self.start_time = self.make_start_time()
        self.params = params

    def get_json(self):
        return self.config

    def set_json(self, config):
        self.config = config

    def make_start_time(self):
        rightnow = time.time()
        rightnow_lt = time.localtime(rightnow)
        # Let's start at the next 5 minute interval
        ones = rightnow_lt.tm_min % 10
        tens = rightnow_lt.tm_min - ones
        if ones < 5:
            next_tens = tens + 5
        else:
            next_tens = tens + 10
        time_tuple = (rightnow_lt.tm_year, rightnow_lt.tm_mon, \
                      rightnow_lt.tm_mday, rightnow_lt.tm_hour, next_tens, \
                      rightnow_lt.tm_sec, rightnow_lt.tm_wday, rightnow_lt.tm_yday, \
                      rightnow_lt.tm_isdst)
        # Return the time when the clock starts
        return time.mktime(time_tuple)

    def process(self, config=None):
        if config:
            self.config = config
        else:
            jfile = open(self.filename)
            self.config = json.load(jfile)  #Should this stay Unicode, or convert?
        blue_teams = {}
        # todo - clean up this code, make sure it can handle unexpected situations
        first_pass = True
        if "game_name" in self.config:
            pass
        else:
            pass
        if "blueteams" in self.config:
            for blueteam in self.config["blueteams"]:
                blue_obj = self.proc_blueteam(blueteam)
                blue_teams[blue_obj.get_teamname()] = blue_obj
        else:
            raise Exception("No bluteams given!")
        if "injects" in self.config:
            injects = Injects()
            for team in blue_teams:
                teamname = blue_teams[team].get_teamname()
                email = blue_teams[team].get_email()
                location = email.split("@")[1]
                ticket_obj = TeamTicket(teamname, location)
                blue_teams[team].set_ticket_interface(ticket_obj)
                email = blue_teams[team].get_email()
                injects.add_email(team, email)
                injects.add_ticketobj(team, ticket_obj)
            for inject in self.config["injects"]:
                self.proc_injects(inject, injects)
        else:
            injects = None
        return (blue_teams, injects)

    def proc_blueteam(self, blueteam):
        if "name" in blueteam:
            this_team = str(blueteam["name"])
            blue_obj = BlueTeam(this_team, self.start_time, self.flag_store)
        else:
            raise Exception("No name given for blueteam!")
        if "email" in blueteam:
            email = str(blueteam["email"])
            blue_obj.set_email(email)
        else:
            raise Exception("No email given for blueteam %s!" % this_team)
        if "dns" in blueteam:
            dns = str(blueteam["dns"])
            blue_obj.add_dns(dns)
        else:
            raise Exception("No DNS given for blueteam %s!" % this_team)
        if "nets" in blueteam:
            for net in blueteam["nets"]:
                blue_obj.add_net(net)
        else:
            raise Exception("No Nets entry for blueteam %s!" % this_team)
        if "hosts" in blueteam:
            for host in blueteam["hosts"]:
                self.proc_hosts(blue_obj, host)
        else:
            raise Exception("No Hosts entry for blueteam %s!" % this_team)
        if "flags" in blueteam:
            for flag_name in blueteam["flags"]:
                this_flag = blueteam["flags"][flag_name]
                self.proc_flags(blue_obj, flag_name, this_flag)
        return blue_obj


    def proc_hosts(self, blue_obj, hosts):
        blueteam = blue_obj.get_teamname()
        if "hostname" in hosts:
            hostname = hosts["hostname"]
        else:
            raise Exception("No hostname for a host in blueteam %s" % blueteam)
        if "value" in hosts:
            value = hosts["value"]
            blue_obj.add_host(hostname, value)
        else:
            raise Exception("No score given for hostname %s in blueteam %s" % (hostname, blueteam))
        if "services" in hosts:
            for service in hosts["services"]:
                self.proc_services(blue_obj, hostname, service)
        else:
            raise Exception("No services given for hostname %s in blueteam %s" % (hostname, blueteam))

    def proc_services(self, blue_obj, hostname, services):
        blueteam = blue_obj.get_teamname()
        if "port" in services:
            port = services["port"]
        else:
            raise Exception("No port for host %s in blueteam %s" % (hostname, blueteam))
        if "protocol" in services:
            proto = services["protocol"]
        else:
            raise Exception("No protocol for host %s in blueteam %s" % (hostname, blueteam))
        if "value" in services:
            value = services["value"]
        else:
            raise Exception("No service score for host %s in blueteam %s" % (hostname, blueteam))
        if "uri" in services:
            uri = services["uri"]
        else:
            uri = None
        if "content" in services:
            content = services["content"]
        else:
            content = None
        if "username" in services:
            username = services["username"]
        else:
            username = None
        if "password" in services:
            password = services["password"]
        else:
            password = None
        blue_obj.add_service(hostname, port, proto, value, uri, content, username, password)

    def proc_injects(self, inject, injects):
        set_ticket = False
        if "inject_name" in inject:
            inject_name = inject["inject_name"]
        else:
            raise Exception("Inject without name: %s" % ":".join(inject.values()))
        if "inject_value" in inject:
            inject_value = inject["inject_value"]
        else:
            raise Exception("Inject without value: %s" % ":".join(inject.values()))
        if "category" in inject:
            category = inject["category"]
        else:
            raise Exception("Inject without category: %s" % join(inject.values()))
        if "inject_duration" in inject:
            inject_duration = inject["inject_duration"]
        else:
            raise Exception("Inject without duration: %s" % ":".join(inject.values()))
        if "set_ticket" in inject:
            if "True" in inject["set_ticket"]:
                set_ticket = True
            elif "False" in inject["set_ticket"]:
                set_ticket = False
            else:
                raise Exception("Invalid set_ticket value for inject %s" % inject_name)
        else:
            set_ticket = False
        injects.add_inject(inject_name, inject_value, inject_duration, category, set_ticket)
        if "inject_subject" in inject:
            inject_subject = inject["inject_subject"]
            injects.set_subject(inject_name, inject_subject)
        else:
            raise Exception("Inject without subject: %s" % ":".join(inject.values()))
        if "inject_body" in inject:
            for line in inject["inject_body"]:
                injects.add_line(inject_name, line)
        else:
            raise Exception("Inject without body: %s" % ":".join(inject.values()))


    def proc_flags(self, blue_obj, flag_name, flag):
        if "value" in flag:
            value = flag["value"]
        else:
            raise Exception("No value given for flag %s!" % flag_name)
        if "answer" in flag:
            this_answer = flag["answer"]
        else:
            raise Exception("No answer given for flag %s!" % flag_name)
        if "score" in flag:
            this_score = flag["score"]
            blue_obj.add_flag(flag_name, value, score=this_score, answer=this_answer)
        else:
            blue_obj.add_flag(flag_name, value, answer=this_answer)


if __name__ == "__main__":
    from FlagStore import FlagStore
    from Logger import Logger
    from Queue import Queue
    queue_obj = Queue()
    logger_obj = Logger("JsonConfigTesT")
    flag_store = FlagStore(logger_obj, queue_obj, "test")
    json_obj = JsonConfig("scorebotcfg.json", flag_store)
    (blueteams, injects) = json_obj.process()
    for blueteam in blueteams:
        print blueteam.get_teamname()
