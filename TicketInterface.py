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

import _mysql
import time

class TicketInterface(object):


    def __init__(self, host="10.150.100.153", user="scorebot", passwd="password", db="sts"):
        self.locations = {}
        self.users = {}
        self.users_by_id = {}
        self.categories = {}
        self.all_tickets = {}
        self.closed_tickets = {}
        self.sqlhost = host
        self.sqluser = user
        self.sqlpass = passwd
        self.dbname = db
        # Database stuff
        # Insert a ticket
        self.insert_ticket_query = """INSERT INTO tickets (
                                      subject,  issue,  preview,
                                      created_uid, created_date, created_time,
                                      location_id, state_id, eu_uid, category_id, assigned_uid)
                                      VALUES ("%s", "%s", "%s", %s, %s, %s, %s, %s, %s, %s, %s);"""
        # Queries
        # count all tickets by owner
        self.group_tickets_by_owner_query = """select users.id, count(*) from tickets, users where users.id = tickets.eu_uid and tickets.created_uid = 1 group by users.id;"""
        self.tickets_by_owner_query = """select count(*) from tickets where tickets.created_uid = 1 and tickets.eu_uid = %s;"""
        # count closed tickets by owner
        self.group_closed_by_owner_query = """select users.id, count(*) from tickets, users where users.id = tickets.eu_uid and tickets.created_uid = 1 and tickets.state_id = 2 group by users.id;"""
        self.closed_by_owner_query = """select count(*) from tickets where  tickets.created_uid = 1 and tickets.state_id = 2 and tickets.eu_uid = %s;"""
        # get users
        self.get_users_query = """select id, ln from users;"""
        # get locations
        self.get_locations_query = """select id, name from locations;"""
        # get categories
        self.get_categories_query = """select * from categories;"""
        # populate static data
        self.get_users()
        self.get_categories()
        self.get_locations()

    def insert_ticket(self, subject, issue, preview, loc_id, user_id, cat_id):
        now = time.time()
        #c_id = creation_id
        c_id = 1
        #cdate = creation date
        cdate = now
        #ctime = creation time
        ctime = now
        #loc_id = lcoation id
        #s_id = state id
        s_id = 1
        #a_uid = assigned_uid
        eu_uid = user_id
        a_uid = user_id
        db = _mysql.connect(host=self.sqlhost, user=self.sqluser, passwd=self.sqlpass,db=self.dbname);
        db.query(self.insert_ticket_query %
                       (subject, issue, preview, c_id, cdate, ctime, loc_id, s_id, eu_uid, cat_id, a_uid))
        db.close()

    def get_categories(self):
        results = self.query(self.get_categories_query)
        for result in results:
            category = result[1]
            category_id = result[0]
            self.categories[category] = category_id

    def get_users(self):
        results = self.query(self.get_users_query)
        for result in results:
            user_name = result[1]
            user_id = result[0]
            self.users[user_name] = user_id
            self.users_by_id[user_id] = user_name

    def get_locations(self):
        results = self.query(self.get_locations_query)
        for result in results:
            loc_name = result[1]
            locat_id = result[0]
            self.locations[loc_name] = locat_id

    def get_team_closed(self, team):
        if team in self.users:
            team_id = self.users[team]
        else:
            users = ", ".join(self.users.keys())
            raise Exception("Invalid team %s, not in %s!" % (team, users))
        results = self.query(self.closed_by_owner_query % team_id)
        return results[0][0]

    def get_team_tickets(self, team):
        if team in self.users:
            team_id = self.users[team]
        else:
            users = ", ".join(self.users.keys())
            raise Exception("Invalid team %s, not in %s!" % (team, users))
        results = self.query(self.tickets_by_owner_query % team_id)
        return results[0][0]

    def get_closed(self):
        results = self.query(self.group_closed_by_owner_query)
        for result in results:
            user_id = result[0]
            if user_id in self.users_by_id:
                team = self.users_by_id[user_id]
            else:
                raise Exception("User ID %s not found!" % user_id)
            count = result[1]
            self.closed_tickets[team] = count

    def get_tickets(self):
        results = self.query(self.group_tickets_by_owner_query)
        for result in results:
            user_id = result[0]
            if user_id in self.users_by_id:
                team = self.users_by_id[user_id]
            else:
                raise Exception("User ID %s not found!" % user_id)
            count = result[1]
            self.all_tickets[team] = count

    def query(self, query):
        results = []
        db = _mysql.connect(host=self.sqlhost, user=self.sqluser, passwd=self.sqlpass,db=self.dbname);
        db.query(query)
        r = db.store_result()
        new_row = r.fetch_row()
        while new_row:
            results.append(new_row[0])
            new_row = r.fetch_row()
        db.close()
        return results

if __name__=="__main__":
    ticket_obj = TicketInterface()
    print ticket_obj.categories
    print ticket_obj.users
    print ticket_obj.locations
    loc_id = ticket_obj.locations["beta.net"]
    user_id = ticket_obj.users["BETA"]
    cat_id = ticket_obj.categories["service request"]
    ticket_obj.insert_ticket("Yet another ticket", "IT SUCKS", "IT SU...", loc_id, user_id, cat_id)
    ticket_obj.get_closed()
    print ticket_obj.closed_tickets
    ticket_obj.get_tickets()
    print ticket_obj.all_tickets
    print "ALPHA tickets: %s" % ticket_obj.get_team_tickets("ALPHA")
    print "BETA tickets: %s" % ticket_obj.get_team_tickets("BETA")
    print "ALPHA tickets closed: %s" % ticket_obj.get_team_closed("ALPHA")
    print "BETA tickets closed: %s" % ticket_obj.get_team_closed("BETA")


