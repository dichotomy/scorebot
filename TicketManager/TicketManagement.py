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

import _mysql
import time
import re
import sys
import json
import requests
from threading import Thread
from Table import Table
from Tickets import Ticket
import logging

class TicketManager(Thread):

    def __init__(self, logfilename, start_time=None,
                    host="10.150.100.153", user="scorebot", passwd="password", db="sts"):
        Thread.__init__(self)
        now = time.time()
        if start_time:
            self.start_time = start_time
        else:
            self.start_time = int(now)
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=log_format, filename=logfilename, level=logging.DEBUG)
        logging.info("Starting Ticketmanger" )
        self.get_tickets_query = "select * from tickets order by id;"
        self.get_tickets_log_query = "select * from tickets_log;"
        self.get_tickets_log_query_by_ticket = "select * from tickets_log where ticket_id = %s;"
        self.users_query = "select * from users order by id;"
        self.get_users_query = "select id, ln from users;"
        self.tickets_log_table = Table(self.get_tickets_log_query, host, user, passwd, db)
        self.tickets_table = Table(self.get_tickets_query, host, user, passwd, db)
        self.users_table = Table(self.users_query, host, user, passwd, db)
        self.tickets = {}
        self.ticket_logs = []
        self.db = _mysql.connect(host=host, user=user, passwd=passwd,db=db)
        self.ticket_closed_re = re.compile("Ticket Closed.")
        self.ticket_opened_re = re.compile("Ticket Opened.")
        self.user_changed_re = re.compile("End User Changed: (\S+)")
        self.location_changed_re = re.compile("Location changed to: (\S+)")
        self.category_changed_re = re.compile("Category changed to: (\S+)")
        self.set_next_time(now)
        self.users = {}
        self.users_by_id = {}
        self.round_scores = {}
        self.get_users()
        self.url = "http://10.200.100.110/api/tickets/"
        self.req = requests.session()
        self.req.headers['SBE-AUTH'] = "bf086697-5373-496e-b2f0-8464d2b162eb"
        self.team_apis = {
             "ALPHA": "bab14508-f15a-4de0-9e02-3a019902f3a7",
             "Gamma": "0980aef1-a13e-4aa9-9910-4c3fdf7769ed",
             "Delta": "18bff393-895d-4aa6-8440-92e2f001f5d4",
             "Epsilon": "3f303b60-730b-45bd-9d9a-0ef5dad35707"
        }

    def run(self):
        """
        1. Get a list of all tickets from the database
        2. For already existing tickets, look for
           A. Closure History (from tickets_log table)
           B. Current Open/Closed state (state column in tickets table)
           C. Changes of ownership (from tickets_log table)
        3. For new tickets
           _. Created By vs. Assigned To
           A. Closure History (from tickets_log table)
           B. Current Open/Closed state (state column in tickets table)
           C. Changes of ownership (from tickets_log table)
        4. Assess penalty points
           A. Category Base value x 5 minute intervals starting after 15 minutes
           B. Assess reopening penalties for each reopening
              1. Add 100 point base penalty
              2. Base value x 1.5 x 5 minute intervals starting after 15 minutes
        """
        while True:
            # Grab a copy of each table every minute and save it
            # Rather than do SQL queries for each data type, we do all the work in memory with Python
            # Why?  Because we can't trust the database, so we take these snapshots and work with those
            self.users_table.update()
            self.audit_table(self.users_table, "users")
            self.tickets_table.update()
            self.audit_table(self.tickets_table, "tickets")
            self.tickets_log_table.update()
            self.audit_table(self.tickets_log_table, "tickets_log")
            for ticket_row in self.tickets_table:
                ticket_id = ticket_row[0]
                if ticket_id in self.tickets:
                    #Look for changes we care about
                    self.audit_ticket(ticket_id, ticket_row)
                else:
                    self.tickets[ticket_id] = Ticket(ticket_row)
                    owner_id = self.tickets[ticket_id].get_eu_uid()
                    owner_name = self.users_by_id[owner_id]
                    opened_id = self.tickets[ticket_id].get_created_uid()
                    opened_name = self.users_by_id[opened_id]
                    category = self.tickets[ticket_id].get_category()
                    logging.info("Found new ticket number %s of type %s for team %s opened by %s " %
                                 (ticket_id, category, owner_name, opened_name))
            new_rows = self.tickets_log_table.get_new_rows()
            print "Found %s new rows for tickets log" % new_rows
            if new_rows:
                for row_num in new_rows:
                    row = self.tickets_log_table.get_row(row_num)
                    ticket_id = row[0]
                    if ticket_id in self.tickets:
                        logging.info("Added ticket log '%s' to ticket %s" % ("|".join(row), ticket_id))
                        self.tickets[ticket_id].add_log(row)
                    else:
                        logging.error("Ticket log '%s' does not have a ticket" % "|".join(row) )
                    #todo - evaluate each log row to ensure the time is always ascending.
            # Every five minutes, we score
            now = time.time()
            #if self.check_time(now):
            if True:
                # Time to do a scoring run!
                # Look for new tickets
                for ticket in self.tickets_table:
                    ticket_id = ticket[0]
                    score = self.tickets[ticket_id].score(now)
                    owner_id = self.tickets[ticket_id].get_assigned_uid()
                    username = self.users_by_id[owner_id]
                    if username in self.round_scores:
                        self.round_scores[username] += score
                    else:
                        self.round_scores[username] = score
            if self.round_scores:
                sys.stdout.write("Round scores: ")
                print self.round_scores
                scores = {}
                for team in self.round_scores:
                    if team == "BETA":
                        continue
                    uid = self.team_apis[team]
                    scores[uid] = self.round_scores[team]
                self.submit(json.dumps(scores))
                self.round_scores = {}
            # Take a break, you earned it!
            time.sleep(1)

    def submit(self, data):
        sys.stderr.write("Posting to %s: %s" % (self.url, data))
        b = self.req.post(self.url, data=data)
        r = b.content.decode('utf-8')
        print r
        #filename = "%s.log" % time.time()
        #outfile = open(filename, "w")
        #outfile.write(r)
        sys.stderr.write("Received status code: " + str(b.status_code))
        #if r.status_code == 200:

    def get_users(self):
        results = self.query(self.get_users_query)
        for result in results:
            user_name = result[1]
            user_id = result[0]
            self.users[user_name] = user_id
            self.users_by_id[user_id] = user_name
        return self.users

    def audit_ticket(self, ticket_id, ticket_row):
        # Audit for ticket changes.
        ticket = self.tickets[ticket_id]
        # Look for cheating - raise alerts
        new_created_uid = ticket_row[5]
        old_created_uid = ticket.get_created_uid()
        if new_created_uid != old_created_uid:
            logging.error("ALERT!  Ticket %s created UID was changed! from %s to %s" %
                        (ticket_id, old_created_uid, new_created_uid))
        new_created_time = ticket_row[7]
        old_created_time = ticket.get_created_time()
        if new_created_time != old_created_time:
            logging.error("ALERT!  Ticket %s created time was changed! from %s to %s" %
                        (ticket_id, old_created_time, new_created_time))
        new_created_date = ticket_row[6]
        old_created_date = ticket.get_created_date()
        if new_created_date != old_created_date:
            logging.error("ALERT!  Ticket %s created date was changed! from %s to %s" %
                        (ticket_id, old_created_date, new_created_date))
        # Look for expected changes
        new_state_id = ticket_row[14]
        old_state_id = ticket.get_state_id()
        if new_state_id != old_state_id:
            ticket.set_state_id(new_state_id)
            logging.info("Ticket %s state_id change from %s to %s" % (ticket_id, old_state_id, new_state_id))
        new_resolved_uid = ticket_row[15]
        old_resolved_uid = ticket.get_resolved_uid()
        if new_resolved_uid != old_resolved_uid:
            ticket.set_resolved_uid(new_resolved_uid)
            logging.info("Ticket %s resolved uid change from %s to %s" %
                         (ticket_id, old_resolved_uid, new_resolved_uid))
        new_resolved_date = ticket_row[16]
        old_resolved_date = ticket.get_resolved_date()
        if new_resolved_date != old_resolved_date:
            ticket.set_resolved_date(new_resolved_date)
            logging.info("Ticket %s resolved date change from %s to %s" %
                         (ticket_id, old_resolved_date, new_resolved_date))
        new_resolved_time = ticket_row[17]
        old_resolved_time = ticket.get_resolved_time()
        if new_resolved_time != old_resolved_time:
            ticket.set_resolved_time(new_resolved_time)
            logging.info("Ticket %s resolved time change from %s to %s" %
                         (ticket_id, old_resolved_time, new_resolved_time))


    def audit_table(self, table, name):
        # Monitor and log all observed changes to tables.
        # TODO - add intelligence per table to alert on sensitive columns.  This could get noisy as is.
        difflist = table.find_diff()
        if difflist:
            for diff in difflist:
                set2 = table.get_current_set_index()
                set1 = set2 - 1
                logging.info("Difference observed at row %s between table %s versions %s and %s" %
                                  (diff, name, set1, set2))
                col_diffs = table.diff_rows(diff)
                if col_diffs:
                    for colnum in col_diffs:
                        logging.info("Column %s changed from %s to %s" %
                                          (colnum, col_diffs[colnum][0], col_diffs[colnum][1]))

    def check_time(self, now):
        # This DOES NOT WORK when crossing from one day to the next.
        now_t = time.localtime(now)
        now_h = now_t[3]
        now_m = now_t[4]
        if now_h >= self.next_time[0]:
            if now_m >= self.next_time[1]:
                self.set_next_time(now)
                return True
            else:
                return False
        else:
            return False

    def set_next_time(self, this_time):
        this_time_t = time.localtime(this_time)
        this_time_h = this_time_t[3]
        this_time_m = this_time_t[4]
        if 0 <= this_time_m < 55:
            next_go_m = this_time_m + 5 - (this_time_m % 5)
            self.next_time = [this_time_h, next_go_m]
        else:
            next_go_m = this_time_m + 5 - (this_time_m % 5)
            self.next_time = [this_time_h + 1, next_go_m]

    def query(self, query):
        results = []
        self.db.query(query)
        r = self.db.store_result()
        new_row = r.fetch_row()
        while new_row:
            results.append(new_row[0])
            new_row = r.fetch_row()
        return results

if __name__ == "__main__":
    tmanager = TicketManager("tm_testing.log")
    tmanager.start()
