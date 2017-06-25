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
import csv
import re

class Table(object):

    def __init__(self, select_query, host="10.150.100.153", user="scorebot", passwd="password", db="sts"):
        self.sets = []
        self.select_query = select_query
        self.db = _mysql.connect(host=host, user=user, passwd=passwd,db=db)
        table_name_re = re.compile("from (\w+)")
        self.name = table_name_re.search(self.select_query).group(1)
        self.current_index = 0
        self.max_index = 0
        self.current_set = None
        self.current_set_index = None

    def __iter__(self):
        return self

    def next(self): # Python 3: def __next__(self)
        if self.current_set:
            pass
        else:
            self.reset_iter()
            raise StopIteration
        if self.current_index > self.max_index:
            self.reset_iter()
            raise StopIteration
        else:
            self.current_index += 1
            return self.current_set[self.current_index-1]

    def reset_iter(self):
        self.current_index = 0

    def get_row(self, row, set=None):
        if not set:
            set = len(self.sets) - 1
        return self.sets[set][row]

    def check_indexes(self, idx1, idx2):
        if not idx1 and not idx2:
            idx2 = len(self.sets) - 1
            idx1 = idx2 - 1
        elif idx1 and not idx2:
            idx2 = idx1+1
        elif idx2 and not idx1:
            idx1 = idx2 - 1
        else:
            pass
        if len(self.sets) - 1 > idx2:
            raise Exception("Set index2 %s is too big for table %s" % (idx2, self.name))
        return idx1, idx2

    def find_diff(self, idx1=None, idx2=None):
        try:
            idx1, idx2 = self.check_indexes(idx1, idx2)
        except:
            return None
        rownum = 0
        diff_list = []
        row_num = 0
        idx1rows = len(self.sets[idx1])
        idx2rows = len(self.sets[idx2])
        if idx1rows < idx2rows:
            for n in range(idx1rows, idx2rows):
                diff_list.append(n)
        for row in self.sets[idx1]:
            if rownum <= idx2rows:
                pass
            else:
                break
            if row == self.sets[idx2][row_num]:
                pass
            else:
                diff_list.append(row_num)
            row_num += 1
        return diff_list

    def diff_rows(self, rownum, idx1=None, idx2=None):
        idx1, idx2 = self.check_indexes(idx1, idx2)
        rows = {}
        if rownum in self.sets[idx1]:
            pass
        else:
            return None
        rows[idx1] = self.sets[idx1][rownum]
        rows[idx2] = self.sets[idx2][rownum]
        diff = {}
        if len(rows[idx1]) == len(rows[idx2]):
            pass
        else:
            raise Exception ("Rows do not have an equal number of columns!")
        colnum = 0
        for element in rows[idx1]:
            if element == rows[idx2][colnum]:
                pass
            else:
                diff[colnum] = [element, rows[idx2][colnum]]
            colnum += 1
        return diff

    def get_new_rows(self, idx1=None, idx2=None):
        try:
            idx1, idx2 = self.check_indexes(idx1, idx2)
        except:
            return None
        set2len = len(self.sets[idx2]) - 1
        if idx1 == -1:
            #This is our first round:
            return range(0, set2len)
        else:
            set1len = len(self.sets[idx1]) - 1
            return range(set1len, set2len)

    def get_current(self):
        return self.sets[len(self.sets)-1]

    def get_current_set_index(self):
        return len(self.sets) - 1

    def update(self):
        rows = self.get_set()
        # Is this our first time?
        if self.current_set_index > 0:
            if self.find_diff():
                # We only write a diff if this is different than the last set
                self.write_csv(rows)
        else:
            self.write_csv(rows)

    def get_set(self):
        results = self.query(self.select_query)
        #print "Got %s rows" % len(results)
        self.sets.append(results)
        self.current_set_index = len(self.sets) - 1
        if self.current_set_index > 5:
            # We only keep 5 sets on hand
            self.sets.reverse()
            self.sets.pop()
            self.sets.reverse()
            self.current_set_index -= 1
        self.current_set = self.sets[self.current_set_index]
        self.max_index = len(self.current_set) - 1
        return results

    def write_csv(self, rows):
        filename = "%s_%s.csv" % (self.name, time.strftime('%Y-%m-%d_%H%M%S', time.localtime(time.time())))
        with open(filename, 'wb') as csvfile:
            table_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                table_writer.writerow(row)

    def query(self, query):
        results = []
        self.db.query(query)
        r = self.db.store_result()
        new_row = r.fetch_row()
        while new_row:
            results.append(new_row[0])
            new_row = r.fetch_row()
        return results

if __name__=="__main__":
    import sys
    get_tickets_query = "select * from tickets order by id;"
    tickets_table = Table(get_tickets_query)
    get_tickets_log_query = "select * from tickets_log order by id;"
    tickets_log_table = Table(get_tickets_log_query)
    users_query = "select * from users order by id;"
    users_table = Table(users_query)
    tickets_table.update()
    print "Iterating through tickets table"
    for ticket in tickets_table:
        print ticket
    indexes = raw_input('Change a ticket and hit ENTER ')
    tickets_table.update()
    for ticket in tickets_table:
        print ticket[0]
    index = 0
    print "Got %s sets" % len(tickets_table.sets)
    #for row in tickets_table.sets[1]:
    #print "%s: %s" % (index, row[0])
    #index += 1
    #indexes = raw_input('Enter two ticket IDs: ')
    #(i1, i2) = indexes.split(",")
    difflist = tickets_table.find_diff(0,1)
    print difflist
    for diff in difflist:
        diffed = tickets_table.diff_rows(0,1, diff)
        print diffed
        for item in diffed:
            print tickets_table.get_row(diff, 0)[item]
            print tickets_table.get_row(diff, 1)[item]
