#!/usr/bin/env python2
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

import re
import time
import json

def time_range(self, offset=0):
    # Offset will be subtracted so that we can get time windows from the past.
    # Naturally, passing a negative offset will look at time windows in the future.
    now = time.time()
    now_t = time.localtime(now)
    now_a = []
    for n in range(9):
        now_a.append(now_t[n])
    m = now_a[4] - offset
    min =  m - m % 5
    min_a = now_a
    min_a[4] = min
    min_epoch = time.mktime(min_a)
    max = m + 5 - m % 5
    max_a = now_a
    max_a[4] = max
    max_epoch = time.mktime(max_a)
    return [min_epoch, max_epoch]

class TicketLog(object):

    def __init__(self, log):
        self.log = {}
        self.log["ticket_id"] = log[0]
        self.log["user_id"] = log[1]
        self.log["data"] = log[2]
        self.log["date"] = log[3]
        self.log["time"] = log[4]

    def get_json(self):
        return json.dumps(self.log)

    def get_ticket_id(self):
        return self.log["ticket_id"]

    def set_ticket_id(self, ticket_id):
        self.log["ticket_id"] = ticket_id

    def get_user_id(self):
        return self.log["user_id"]

    def set_user_id(self, user_id):
        self.log["user_id"] = user_id

    def get_data(self):
        return self.log["data"]

    def set_data(self, data):
        self.log["data"] = data

    def get_date(self):
        return self.log["date"]

    def set_date(self, date):
        self.log["date"] = date

    def get_time(self):
        return self.log["time"]

    def set_time(self, time):
        self.log["time"] = time

class Ticket(object):

    def __init__(self, ticket):
        self.ticket = {}
        self.ticket["id"] = ticket[0]
        self.ticket["subject"] = ticket[1]
        self.ticket["issue"] = ticket[2]
        self.ticket["preview"] = ticket[3]
        self.ticket["resolution"] = ticket[4]
        self.ticket["created_uid"] = ticket[5]
        self.ticket["created_date"] = ticket[6]
        self.ticket["created_time"] = ticket[7]
        self.ticket["category_id"] = ticket[8]
        self.ticket["location_id"] = ticket[9]
        self.ticket["assigned_gid"] = ticket[10]
        self.ticket["assigned_uid"] = ticket[11]
        self.ticket["assigned_date"] = ticket[12]
        self.ticket["assigned_time"] = ticket[13]
        self.ticket["state_id"] = ticket[14]
        self.ticket["resolved_uid"] = ticket[15]
        self.ticket["resolved_date"] = ticket[16]
        self.ticket["resolved_time"] = ticket[17]
        self.ticket["eu_uid"] = ticket[18]
        self.resolved_time = self.ticket["resolved_time"]
        self.logs = []
        self.log_index = 0
        self.ticket_closed_re = re.compile("Ticket Closed.")
        self.ticket_opened_re = re.compile("Ticket Opened.")
        self.base_scores = {}
        self.base_scores["No Category"] = 10
        self.base_scores["outage"] = 50
        self.base_scores["service request"] = 25
        self.base_scores["change"] = 25
        self.base_scores["issue"] = 30
        self.base_scores["deliverable"] = 30
        self.categories = ["No Category", "outage", "service request", "change", "issue", "deliverable"]
        self.state = ["opened", "closed"]
        self.multiple = 1

    def get_category(self):
        index = int(self.get_category_id()) - 1
        if index < len(self.categories):
            category = self.categories[index]
            if category:
                return category
            else:
                raise Exception("Unknown category id %s for ticket %s" %  (index, self.get_id()))
        else:
            return False

    def get_closed_uid(self, resolved_time):
        for log in self.logs:
            if resolved_time == log.get_time():
                return log.get_user_id()
        raise Exception("Ticket %s: Cannot match resolved time with a tickets_log entry!" % self.get_id())


    def get_base_score(self):
        category = self.get_category()
        if category:
            return self.base_scores[category]

    def get_state(self):
        state_id = int(self.get_state_id()) - 1
        if state_id < len(self.state):
            return self.state[state_id]
        else:
            raise Exception("State id %s for ticket %s is too large!" % (state_id, self.get_id()))

    def get_state_bool(self):
        state_id = int(self.get_state_id())
        if state_id == 1:
            return False
        elif state_id == 2:
            return True
        else:
            raise Exception("State id %s for ticket %s is unknown!" % (state_id, self.get_id()))

    def get_json(self):
        return json.dumps(self.ticket)

    def __iter__(self):
        return self

    def next(self): # Python 3: def __next__(self)
        if self.log_index > len(self.logs) - 1:
            self.reset_iter()
            raise StopIteration
        else:
            self.log_index += 1
            return self.logs[self.log_index-1]

    def reset_iter(self):
        self.log_index = 0

    def score(self, now):
        # Each ticket is given a 15 minute grace time
        if int(self.get_created_time()) + (15*60) < now:
            return self.proc_history()
        else:
            return 0

    def proc_history(self):
        # We look back at the prior 5 minute interval
        min_epoch, max_epoch = time_range(5)
        opencloses = {}
        base_score = self.get_base_score()
        current_state = self.get_state()
        for tlog in self.logs:
            # Find ticket logs within this scoring interval
            if min_epoch < tlog.get_time() < max_epoch:
                data = tlog.get_data()
                this_time = tlog.get_time()
                # Look for ticket closures
                if self.ticket_closed_re.search(data):
                    print "Found closed for ticket %s" % self.get_id()
                    opencloses[this_time] = "closed"
                # Look for ticket openings
                elif self.ticket_opened_re.search(data):
                    print "Found opened for ticket %s" % self.get_id()
                    opencloses[this_time] = "opened"
                else:
                    pass
        closed_time = 0
        opened_time = 0
        opened_count = 0
        last_time = min_epoch
        last_state = None
        if opencloses:
            for this_time in opencloses:
                if opencloses[this_time] == "closed":
                    opened_time += this_time - last_time
                    last_state = "closed"
                elif opencloses[this_time] == "opened":
                    closed_time += this_time - last_time
                    opened_count += 1
                    last_state = "opened"
                last_time = this_time
            if last_state == "opened":
                opened_time += max_epoch - last_time
            elif last_state == "closed":
                closed_time += max_epoch - last_time
            opened_fraction = float(opened_time) / 600
            if self.multiple == 1:
                self.multiple = opened_count * 1.5
            else:
                self.multiple += opened_count * 1.5
        else:
            if current_state == "opened":
                opened_fraction = 1
            else:
                opened_fraction = 0
        return (base_score * opened_fraction * self.multiple) + (100 * opened_count)

    def add_log(self, log):
        self.logs.append(TicketLog(log))

    def get_log(self, index):
        if index < len(self.logs):
            return [index]
        else:
            raise Exception("Log index %s too big for ticket %s" % (index, self.ticket["id"]))

    def get_id(self):
        return self.ticket["id"]

    def set_id(self, id):
        self.ticket["id"] = id

    def get_subject(self):
        return self.ticket["subject"]

    def set_subject(self, subject):
        self.ticket["subject"] = subject

    def get_issue(self):
        return self.ticket["issue"]

    def set_issue(self, issue):
        self.ticket["issue"] = issue

    def get_preview(self):
        return self.ticket["preview"]

    def set_preview(self, preview):
        self.ticket["preview"] = preview

    def get_resolution(self):
        return self.ticket["resolution"]

    def set_resolution(self, resolution):
        self.ticket["resolution"] = resolution

    def get_created_uid(self):
        return self.ticket["created_uid"]

    def set_created_uid(self, uid):
        self.ticket["created_uid"] = uid

    def get_created_date(self):
        return self.ticket["created_date"]

    def set_created_date(self, created_date):
        self.ticket["created_date"] = created_date

    def get_created_time(self):
        return self.ticket["created_time"]

    def set_created_time(self, created_time):
        self.ticket["created_time"] = created_time

    def get_category_id(self):
        return self.ticket["category_id"]

    def set_category_id(self, id):
        self.ticket["category_id"] = id

    def get_location_id(self):
        return self.ticket["location_id"]

    def set_location_id(self, id):
        self.ticket["location_id"] = id

    def get_assigned_uid(self):
        return self.ticket["assigned_uid"]

    def set_assigned_uid(self, uid):
        self.ticket["assigned_uid"] = uid

    def get_assigned_gid(self):
        return self.ticket["assigned_gid"]

    def set_assigned_gid(self, gid):
        self.ticket["assigned_gid"] = gid

    def get_assigned_date(self):
        return self.ticket["assigned_date"]

    def set_assigned_date(self, date):
        self.ticket["assigned_date"] = date

    def get_assigned_time(self):
        return self.ticket["assigned_time"]

    def set_assigned_time(self, assigned_time):
        self.ticket["assigned_time"] = assigned_time

    def get_state_id(self):
        return self.ticket["state_id"]

    def set_state_id(self, state_id):
        self.ticket["state_id"] = state_id

    def get_resolved_uid(self):
        return self.ticket["resolved_uid"]

    def set_resolved_uid(self, resolved_uid):
        self.ticket["resolved_uid"] = resolved_uid

    def get_resolved_date(self):
        return self.ticket["resolved_date"]

    def set_resolved_date(self, resolved_date):
        self.ticket["resolved_date"] = resolved_date

    def get_resolved_time(self):
        return self.ticket["resolved_time"]

    def set_resolved_time(self, resolved_time):
        self.ticket["resolved_time"] = resolved_time

    def get_eu_uid(self):
        return self.ticket["eu_uid"]

    def set_eu_uid(self, eu_uid):
        self.ticket["eu_uid"] = eu_uid
