#!/usr/bin/python2.7
######################################################################
#     dia2sql_xml.py - Parses an xml file produced by Dia for a UML diagram.
#
#     Copyright (C) 2003  Eric I. Arnoth    <earnoth@comcast.net>
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#     Change log
#        2003-02-08: initial release
# 
#        2008-07-06: updated code to handle new 'comment' fields in DIA UML
#
"""
    Author:     Eric I. Arnoth

    First Release Date:        February 8, 2003

    Latest Version:    0.3

    Parses an XML output file produced by Dia for a UML diagram.  The UML
    diagram should use classes to represent tables and constraints to represent
    foreign key relationships.  Currently, only simple schemas are supported
    (single column keys, etc).  Some minor database type differences between
    mySQL and PostgreSQL are also supported.

    Further development will occur as I find the need and/or the time.  Code
    contributions would be most welcome.

    Requires at least PyXML-0.7.1 (http://sourceforge.net/projects/pyxml)

    UPDATE:  2008-07-06 (release 0.3)
    In the five years since I last touched this, it seems that Dia has added
    a 'comments' field to the class object in their UML docs.  So, I added
    support for this (particularly since it broke my script.  ;)

    Oh, I also added a metric tonne of comments.  Enjoy.

"""
from xml.sax import make_parser, SAXException
import sys
from xml.sax.handler import ContentHandler
import re
import fileinput
import os
import binascii
import types
import os.path
import string
import traceback
import pprint

# SQL comments
table_header = "/*============================================================================*/"
table_header = string.join((table_header, "/* Table:                                                                                          */",table_header), "\n")

sequence_header = "/*============================================================================*/"
sequence_header = string.join((sequence_header, "/* Sequence:                                                                                      */",sequence_header), "\n")

foriegn_header = "/*============================================================================*/"
foriegn_header = string.join((foriegn_header, "/* New Foriegn Key Constraint:                                                              */",foriegn_header), "\n")

def fill_header(header, text):
    """
    This function takes two text strings (header, text) and merges them.  The
    first string's trailing whitespace is replaced with the second string.
    This is only done for aestetics (but probably won't work very well if text
    > header... ;)
    """
    text_len = len(text)
    empty_space = ''
    for char in range(text_len):
        empty_space += " "
    this_header = string.replace(header, empty_space, " "+text, 1)
    return this_header

# Element names specific to the dia XML document
dia_diagram = 'dia:diagram'
dia_attribute = 'dia:attribute'
dia_composite = 'dia:composite'
dia_object = 'dia:object'
dia_string = 'dia:string'
dia_connections = 'dia:connections'
dia_connection = 'dia:connection'

verbose = False
drop = False

# Attribute Names specific to the dia XML document
xmlns_dia = 'xmls:dia'
name = 'name'
val = 'val'
value = 'value'
comment = 'comment'
type_ = 'type'
version = 'version'
id = 'id'
handle = 'handle'
to = 'to'
connection = 'connection'
sterotype = 'stereotype'
constraint = 'constraint'

#XML names for the UML structure in the dia document
UMLclass = 'UML - Class'
UMLdep = 'UML - Dependency'
UMLconstraint = 'UML - Constraint'
umlattr = 'umlattribute'
stereotype = 'stereotype'

class column:
    """
    This class represents a simple column in a database.  It only has
    attributes, no methods.

    """

    def __init__(self, hook1, columnname):
        """
        The hook1 and hook2 variables are necessary due to the nuances of the
        way Dia records the physical diagram in the XML.  Hook1 represents the
        left side anchor of the row containing the attribute while hook2
        represents the right.  These are referenced by constraints.

        All other attributes in this class map directly to their database
        counterparts.

        """
        self.hook1 = hook1
        self.hook2 = hook1 + 1
        self.datatype = None
        self.constraint = None
        self.comment = None
        self.value = None
        self.columnname = columnname
        if verbose:
            print "Created %s with %s and %s" % (columnname, self.hook1, self.hook2)


class reference:

    """
    This class represents a simple reference from a foriegn key to a primary
    key.

    """
    def __init__(self, name):
        self.name = name
        self.local_column = ""
        self.table = ""
        self.foreign_column = ""


class dbtable:

    """
    This class represents a database table instance as depicted in the UML
    reference.  It is basically a crude bundle of columns and references found
    for a given table, most methods providing either a thin wrapper for the
    internal variables or simple functionality for the processing of the XMl
    file.

    """
    def __init__(self):
        self.counter = 8
        self.name = ''
        self.__columns = {}
        self.__references = {}

    def local_ref(self, id, name, colname):
        self.__references[id] = reference(name)
        self.__references[id].local_column = colname

    def remote_ref(self, id, table, colname):
        self.__references[id].table = table
        self.__references[id].foreign_column = colname

    def get_refs(self):
        return self.__references.keys()

    def get_ref_name(self, id):
        return self.__references[id].name

    def get_ref_relations(self, id):
        if id in self.__references:
            return self.__references[id].local_column, \
                    self.__references[id].table, self.__references[id].foreign_column
        else:
            return None

    def get_ref_table(self, id):
        return self.__references[id].table

    def get_ref_local(self, id):
        return self.__references[id].local_column

    def get_ref_foriegn(self, id):
        return self.__references[id].foreign_column

    def add_column(self, columnname):
        self.__columns[columnname] = column(self.counter, columnname)
        self.counter += 2

    def set_col_type(self, columnname, type_):
        if self.__columns.has_key(columnname):
            self.__columns[columnname].datatype = type_
            return 1
        else:
            return 0

    def set_col_comm(self, colname, comment):
        if self.__columns.has_key(colname):
            self.__columns[colname].comment = comment
            return 1
        else:
            return 0

    def set_col_value(self, colname, thisvalue):
        if self.__columns.has_key(colname):
            self.__columns[colname].value = thisvalue
            return 1
        else:
            return 0

    def set_column_constraint(self, columnname, constraint):
        if self.__columns.has_key(columnname):
            self.columns[columnname].constraint = constraint
            return 1
        else:
            return 0

    def get_columns(self):
        return self.__columns.keys()

    def get_col_value(self, colname):
        return self.__columns[colname].value

    def get_col_comm(self, colname):
        return self.__columns[colname].comment

    def get_col_type(self, colname):
        return self.__columns[colname].datatype

    def get_col_refs(self, colname):
        col_list = self.__columns.keys()
        #for column in col_list:


    def get_hooks(self, colname):
        return self.__columns[colname].hook1, self.__columns[colname].hook2

    def hook_col(self, hook):
        """
        We want to know what column the given Dia diagram anchor corresponds to.
        Look through the hash of column objects to find the right one (hook
        could be n or n+1).

        """
        col_list = self.__columns.keys()
        for column in col_list:
            if self.__columns[column].hook1==int(hook):
                return column
            elif self.__columns[column].hook2==int(hook):
                return column


class DiaContentHandler(ContentHandler):
    """
    Subclass of ContentHandler, its methods are over-written as needed to
    process the XML file.  Currently only handles the SQL-specific fields of
    the UML diagram, ignoring everything else.

    """
    def __init__(self, filename):
        """
        Just initialize everything to zero.

        """
        self.__tables = {}
        self.__dependencies = {}
        self.intable = None
        self.buffer = ''
        self.column = 0
        self.column_name = 0
        self.column_type = 0
        self.invalue = 0
        self.intable = 0
        self.table_name = 0
        self.comment = 0
        self.tableid = 0
        self.dep_name = 0
        self.indep =0
        self.system = None
        parser = make_parser()
        parser.setContentHandler(self)
        try:
            parser.parse(open(filename))
        except:
            print '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
            print 'Failure in XML parsing!'
            print 'Did you remember to save the Dia file without compression...?'
            print '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
            traceback.print_exc()



    def startElement(self, xmlname, attrs):
        """
        Called when the parser encounters the opening of an xml tag.  This
        method evaluates the xml namespace encountered, looking for known
        values.  When one is found, it sets the proper boolean values to start
        processing of subsequent lines to capture the needed data.

        Typically, the UMLclass is encountered first.  Afterwards, we will find
        attributes (which correspond to database columns), within which we will
        find strings.

        Connections are seperate from Attributes, and have only the relationship
        data within them (depicting which two attributes [columns] from two
        different classes [tables] are linked.

        """
        if xmlname == dia_object:
            if attrs.get(type_) == UMLclass:
                table_id = attrs.get(id)
                self.__tables[table_id] = dbtable()
                self.intable = table_id
            elif attrs.get(type_) == UMLconstraint:
                self.indep = attrs.get(id)
        elif xmlname == dia_string:
            self.buffer = ''
        elif xmlname == dia_composite:
            if attrs.get(type_) == umlattr:
                self.column = 1
        elif xmlname == dia_attribute:
            if attrs.get(name) == name:
                if self.column:
                    self.column_name = 1
                if not self.column:
                    self.table_name = 1
            elif attrs.get(name) == type_:
                self.column_type = 1
            elif attrs.get(name) == value and self.column:
                self.invalue = 1
            elif attrs.get(name) == comment and self.column:
                self.comment = 1
        elif xmlname == dia_connection:
            if self.indep:
                # THERE IS A BUG HERE!!!
                # If the XML file is not laid out correctly, a key error
                # will occur if a connection is processed before both tables are
                # processed.  A workaround is to move both tables before the
                # connection in the XML file.
                #
                # A better fix would be to rewrite this code and remove the bug.
                #
                # So, someday I should get to that. ;)
                #
                if not self.tableid:
                    self.tableid = attrs.get(to)
                    colid = attrs.get(connection)
                    colname = self.__tables[self.tableid].hook_col(colid)
                    self.__tables[self.tableid].local_ref(self.indep, self.dep_name,\
                              colname)
                    if verbose:
                        print "Found reference:", self.tableid, colid, \
                                self.dep_name, colname
                elif self.tableid:
                    tableid = attrs.get(to)
                    colid = attrs.get(connection)
                    colname = self.__tables[tableid].hook_col(colid)
                    self.__tables[self.tableid].remote_ref(self.indep, tableid, \
                              colname)
                    if verbose:
                        print "Found reference:", tableid, colid, \
                              self.dep_name, colname
                    self.indep = 0
                    self.tableid = 0


    def endElement(self, xmlname):
        """
        Called upon entry of a closing tag.  The combination of variables
        indicate our state.  Reading the Dia XMl sample doc enclosed will help
        make sense of this.

        One thing we're doing here is borrowing the ID elements of the XML file
        to create hashes for our tables, columns, and relationships.  Since
        they're already unique, it's handy (and is actually necessary for the
        relationships depicted by the Constratints anyway).

        Before leaving here, we need to ensure we reset the proper variables
        when we're done, or things get buggered.

        """
        if xmlname==dia_string:
            if self.intable:
                if verbose:
                    print self.buffer
                if self.table_name:
                    table_name = string.replace(self.buffer.strip(), "#", "")
                    self.__tables[self.intable].name = table_name
                    self.table_name = 0
                elif self.column and self.column_name and not self.column_type and \
                            not self.invalue and not self.comment:
                    columnname = string.replace(self.buffer.strip(), "#", "")
                    if verbose:
                        print "Found column", columnname
                    self.__tables[self.intable].add_column(columnname)
                    self.column_name = columnname
                elif self.column and self.column_name and self.column_type and \
                            not self.invalue and not self.comment:
                    columntype = string.replace(self.buffer.strip(), "#", "")
                    if verbose:
                        print "Found column type", columntype
                    self.__tables[self.intable].set_col_type(self.column_name,\
                              columntype)
                    self.column_type = 0
                elif self.column and self.column_name and not self.column_type and \
                            self.invalue and not self.comment:
                    thisvalue = string.replace(self.buffer.strip(), "#", "")
                    if verbose:
                        print "Found column value", thisvalue
                    self.__tables[self.intable].set_col_value(self.column_name, \
                              thisvalue)
                    self.invalue = 0
                elif self.column and self.column_name and not self.column_type and \
                            not self.invalue and self.comment:
                    comment = string.replace(self.buffer.strip(), "#", "")
                    if verbose:
                        print "Found column comment", comment
                    self.__tables[self.intable].set_col_comm(self.column_name, \
                              comment)
                    self.comment = 0
            if self.indep:
                self.dep_name = string.replace(self.buffer.strip(), "#", "")
        if xmlname == dia_object:
            if self.intable:
                self.intable = 0
        if xmlname == dia_composite:
            self.column = 0
            self.column_name = 0

    def characters(self, chars):
        """
        Gather data.  This function is called upon entering data between XML
        tags.  In the Dia structure, for our purposes, we only really care about
        the <strings> tag.

        """
        self.buffer += chars

    def get_data(self):
        return self.__tables

    def get_last_index(self):
        return self.index

class AlchemyMaker(object):
    """
    This class takes the objects instanciated through the XML parsing in
    DiaContentHandler and processes it, creating SQL statements for building
    the database drawn.
    """

    def __init__(self, tables, indent=4):
        """
        Zero out all the text strings we'll use to build the SQL statement.
        """
        self.tables = tables
        self.sql_create = ''
        self.sqla_header = """#!/usr/bin/env python
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgresql://scorebot:password@localhost/scorebot", echo=True)

Base = declarative_base()

"""
        self.sqlaf_header = """#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://scorebot:password@localhost/scorebot"
db = SQLAlchemy(app)


"""
        self.sql_header = self.sqlaf_header

        self.sql_tables = {}
        self.sql_references = {}
        self.sql_delete = ''
        self.sql_create_seq = ''
        self.sql_constraint = ''
        self.additional_constraints = ''
        self.pp = pprint.PrettyPrinter(indent=4)
        if type(indent) == type(int()):
            self.indent = " " * indent
        else:
            self.indent = " " * 4

    def affect_table(self, table_id, operation):
        """
        Create a table from the hash ID given, return the Python text.  Only gives
        the first line, more is done in other methods.
        """
        table_name = self.tables[table_id].name
        self.sql_tables[table_id] = ["", ""]
        if operation == "CREATE":
            self.sql_tables[table_id][0] = table_name
            #self.sql_tables[table_id][1] += "class %s(Base):\n" % table_name
            self.sql_tables[table_id][1] += "class %s(db.Model):\n" % table_name
            self.sql_tables[table_id][1] += "    __tablename__ = '%s'\n" % table_name.lower()
        else:
            raise NameError, 'Invalid SQL command %s' % operation

    def create_columns(self, table_id):
        """
        Create the columns for the table in question.
        """
        col_list = self.tables[table_id].get_columns()
        references = self.tables[table_id].get_refs()
        table_name = self.tables[table_id].name
        num_cols = len(col_list)
        if verbose:
            print "Found %s columns" % num_cols
        for index in range(num_cols):
            # Get the name of the column
            colname = col_list[index]
            # Get and fix the column type
            coltype = self.tables[table_id].get_col_type(colname)
            coltype = self.fix_datatype(coltype)
            # Deal with any default value
            colvalue = self.tables[table_id].get_col_value(colname)
            # Get the comment for the column
            colcomm = self.tables[table_id].get_col_comm(colname)
            if colcomm:
                colcomm.strip()
                self.sql_create += "\n\t/* %s */\n" % colname
            # Make the column statement
            col_statement = self.fix_value(table_id, table_name, index, colname, coltype, colvalue, references)
            # Add the column to the create statmement for the table
            if index < num_cols-1:
                self.sql_tables[table_id][1] += col_statement
            else:
                self.sql_tables[table_id][1] += col_statement

    def fix_datatype(self, coltype):
        """
        Stub to be over-ridden by the sub class.
        """
        if "varchar" in coltype:
            #return coltype.replace("varchar", "String")
            return coltype.replace("varchar", "db.String")
        elif "int" in coltype:
            #return "Integer"
            return "db.Integer"
        elif "datetime" in coltype:
            #return "DateTime"
            return "db.DateTime"
        elif "boolean" in coltype:
            #return "Boolean"
            return "db.Boolean"
        else:
            return coltype

    def fix_value(self, table_id, table_name, col_id, colname, coltype, colvalue, references):
        """
        """
        print table_name, colname, coltype, colvalue
        # See if the column has a relationship to another table
        foreign_key = None
        for ref in references:
            relation = self.tables[table_id].get_ref_relations(ref)
            if relation:
                (local_col, foreign_table_id, foreign_col) = relation
                print "%s:%s:%s" % (local_col, foreign_table_id, foreign_col)
                if local_col == colname:
                    foreign_table = self.tables[foreign_table_id].name.lower()
                    foreign_key = "db.ForeignKey(\"%s.%s\")" % (foreign_table, foreign_col)
                    if table_id in self.sql_references:
                        self.sql_references[table_id].append([foreign_table_id, foreign_col])
                    else:
                        self.sql_references[table_id] = [[foreign_table_id, foreign_col]]
        if colvalue == 'identity':
            seq_name = "%s_seq" % colname
            col_statement = "%s%s = db.Column(%s, db.Sequence('%s'), primary_key=True)\n" % \
                            (self.indent, colname, coltype, seq_name)
        elif colvalue == 'not null':
            if foreign_key:
                col_statement = "%s%s = db.Column(%s, %s, nullable=False)\n" % \
                                (self.indent, colname, coltype, foreign_key)
            else:
                col_statement = "%s%s = db.Column(%s, nullable=False)\n" % (self.indent, colname, coltype)
        elif colvalue == 'unique':
            col_statement = "%s%s = db.Column(%s, unique=True)\n" % (self.indent, colname, coltype)
        else:
            if foreign_key:
                col_statement = "%s%s = db.Column(%s, %s)\n" % (self.indent, colname, coltype, foreign_key)
            else:
                col_statement = "%s%s = db.Column(%s)\n" % (self.indent, colname, coltype)
        return col_statement

    def create_references(self, table_id):
        """
        Is this needed?
        """
        pass

    def make_database(self):
        """
        The function that starts it all.  From here, we build the statements to
        create tables, populate them with columns, link key references, and
        such.
        """
        table_list = sorted(self.tables.keys())
        for table_id in table_list:
            # need to write the logic here
            self.additional_constraints = ''
            self.affect_table(table_id, "CREATE")
            self.create_columns(table_id)
            if self.additional_constraints:
                self.sql_tables[table_id][1] += self.additional_constraints + "\n"
            self.create_references(table_id)
        hold = []
        sequence = {}
        seqno = 0
        while sorted(sequence.values()) != sorted(self.sql_tables.keys()):
            sys.stdout.write("db.Sequence:  ")
            print sorted(sequence.values())
            sys.stdout.write("SQLtables: ")
            print sorted(self.sql_tables.keys())
            sys.stdout.write("References: ")
            self.pp.pprint(self.sql_references)
            for table_id in self.sql_tables:
                skip = False
                sys.stdout.write("Checking table %s\n" % table_id)
                if table_id in sequence.values():
                    continue
                elif table_id in self.sql_references:
                    for reference in self.sql_references[table_id]:
                        sys.stdout.write("\tChecking reference:\n\t")
                        print reference
                        foreign_table = reference[0]
                        if not foreign_table in sequence.values():
                            # A dependent table is not processed yet, we need to wait
                            print "%s has dependent table %s which is not in sequence yet" % \
                                        (table_id, foreign_table)
                            skip = True
                            break
                        else:
                            # Need to process all references!
                            pass
                    if skip:
                        continue
                    else:
                        sequence[seqno] = table_id
                        seqno += 1
                else:
                    sequence[seqno] = table_id
                    seqno += 1
        self.sql_create = self.sql_header
        self.sql_create += self.sql_create_seq
        for seqno in sorted(sequence):
            table_id = sequence[seqno]
            print self.sql_tables[table_id]
            self.sql_create += self.sql_tables[table_id][1]
            self.sql_create += "\n"
        self.sql_create += self.sql_constraint

    def print_raw_data(self):
        """
        Raw data dump.  Useful for debugging.

        """
        print '========================='
        table_list = self.tables.keys()
        for table_id in table_list:
            print table_id
            print self.tables[table_id].name
            columns = self.tables[table_id].get_columns()
            for colname in columns:
                print colname, self.tables[table_id].get_col_type(colname), \
                    self.tables[table_id].get_hooks(colname), \
                    self.tables[table_id].get_col_value(colname)
            references = self.tables[table_id].get_refs()
            for ref in references:
                print ref, self.tables[table_id].get_ref_name(ref), \
                    self.tables[table_id].get_ref_relations(ref)
            print '-------------------------'
        print '========================='

class SQLBuilder(object):
    """
    This class takes the objects instanciated through the XML parsing in
    DiaContentHandler and processes it, creating SQL statements for building
    the database drawn.

    """

    def __init__(self, tables):
        """
        Zero out all the text strings we'll use to build the SQL statement.

        """
        self.tables = tables
        self.sql_create = ''
        self.sql_delete = ''
        self.sql_create = ''
        self.sql_create_seq = ''
        self.sql_constraint = ''
        self.additional_constraints = ''

    def affect_table(self, table_id, operation):
        """
        Create a table from the hash ID given, return the SQL text.  Only gives
        the first line, more is done in other methods.

        """
        table_name = self.tables[table_id].name
        this_table_header = fill_header(table_header, table_name)
        self.sql_create = string.join((self.sql_create, this_table_header), \
                  "\n\n\n")
        if operation == "CREATE":
            self.sql_create = string.join((self.sql_create, "%s TABLE %s (" \
                % (operation, string.upper(table_name))), "\n")
        elif operation == "DROP":
            self.sql_create = string.join((self.sql_create, "%s TABLE %s cascade;"\
                % (operation, string.upper(table_name))), "\n")
        else:
            raise NameError, 'Invalid SQL command %s' % operation
        return table_name

    def create_columns(self, table_id):
        """
        Create the columns for the table in question.  We call fix_datatype to
        clean up anything PGSQL or MYSQL specific.  The function is to be
        overidden by the database-specific subclass in question.

        """
        col_list = self.tables[table_id].get_columns()
        table_name = self.tables[table_id].name
        num_cols = len(col_list)
        if verbose:
            print "Found %s columns" % num_cols
        for index in range(num_cols):
            colname = col_list[index]

            coltype = self.tables[table_id].get_col_type(colname)
            coltype = self.fix_datatype(coltype)

            colvalue = self.tables[table_id].get_col_value(colname)
            colcomm = self.tables[table_id].get_col_comm(colname)
            if colcomm:
                colcomm.strip()
                self.sql_create = string.join((self.sql_create, "\n\t/* ", \
                         colcomm, " */"), "")
            col_statement = self.fix_value(table_name, colname, coltype, colvalue)
            if index < num_cols-1:
                self.sql_create = string.join((self.sql_create, "\n\t", \
                            string.upper(col_statement)+","), "")
            else:
                self.sql_create = string.join((self.sql_create, "\n\t", \
                            string.upper(col_statement)), "")

    def fix_datatype(self, coltype):
        """
        Stub to be over-ridden by the sub class.

        """
        return

    def create_references(self, table_id):
        """
        Stub to be over-ridden by the sub class.

        """
        return

    def make_database(self):
        """
        The function that starts it all.  From here, we build the statements to
        create tables, populate them with columns, link key references, and
        such.

        """
        table_list = self.tables.keys()
        for table_id in table_list:
            self.additional_constraints = ''
            table_name = self.affect_table(table_id, "CREATE")

            self.create_columns(table_id)

            if self.additional_constraints:
                self.sql_create = \
                    string.join((self.sql_create, self.additional_constraints),",\n")

            self.create_references(table_id)

            self.sql_create = string.join((self.sql_create, ");"), "\n")

        self.sql_create = string.join((self.sql_create_seq, self.sql_create, \
                        self.sql_constraint), "")

    def print_raw_data(self):
        """
        Raw data dump.  Useful for debugging.

        """
        print '========================='
        table_list = self.tables.keys()
        for table_id in table_list:
            print table_id
            print self.tables[table_id].name
            columns = self.tables[table_id].get_columns()
            for colname in columns:
                print colname, self.tables[table_id].get_col_type(colname), \
                        self.tables[table_id].get_hooks(colname), \
                        self.tables[table_id].get_col_value(colname)
            references = self.tables[table_id].get_refs()
            for ref in references:
                print self.tables[table_id].get_ref_name(ref), \
                        self.tables[table_id].get_ref_relations(ref)
            print '-------------------------'
        print '========================='


class PostgresBuilder(SQLBuilder):
    """
    Subclass to do stuff specific to PostgreSQL.  Namely, fix datatypes,
    build CREATE SEQUENCE statements and create foriegn-key constraint
    statements.

    """

    def __init__(self, tables):
        """
        Call the parent initialization.  Nothing special here.

        """
        SQLBuilder.__init__(self, tables)

    def make_database(self):
        if drop:
            table_list = self.tables.keys()
            for table_id in table_list:
                self.affect_table(table_id, "DROP")
        super(PostgresBuilder, self).make_database()


    def fix_datatype(self, coltype):
        """
        The only fix we have to do (so far) is change 'datetime' to 'timestamp'.

        """
        if coltype == 'datetime':
            return 'timestamp'
        else:
            return coltype

    def fix_value(self, table_name, colname, coltype, colvalue):
        """
        Autoincrementing primary keys in PGSQL requires a CREATE SEQUENCE
        statement for the column in question.
        """
        print table_name, colname, coltype, colvalue
        if colvalue == 'identity':
            seq_statement = "CREATE SEQUENCE %s\n" + \
                    "INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;"
            seq_name = string.join((table_name, colname, "req"), "_")
            seq_statement = string.upper(seq_statement % seq_name)
            self.sql_create_seq = string.join((self.sql_create_seq, \
                            fill_header(sequence_header, seq_name), \
                            seq_statement), "\n\n")
            self.additional_constraints = \
                            string.join((self.additional_constraints, \
                            "CONSTRAINT %s_PKEY PRIMARY KEY (%s)" % \
                            (string.upper(table_name), string.upper(colname))), \
                            "\n")
            col_statement = string.join((colname, coltype, \
                      "NOT NULL DEFAULT NEXTVAL('%s')" % seq_name), " ")
        else:
            col_statement = string.join((colname, coltype, colvalue), " ")
        return col_statement

    def create_references(self, table_id):
        """
        Here we build the foriegn key reference constraints.
        """
        references = self.tables[table_id].get_refs()
        table_name = self.tables[table_id].name
        for ref in references:
            refname = string.upper(self.tables[table_id].get_ref_name(ref))
            reflocal = string.upper(self.tables[table_id].get_ref_local(ref))
            reftable = string.upper(self.tables[table_id].get_ref_table(ref))
            reftablename = string.upper(self.tables[reftable].name)
            refforeign = \
                    string.upper(self.tables[table_id].get_ref_foriegn(ref))
            ref_statement = 'CONSTRAINT %s FOREIGN KEY(%s) REFERENCES %s (%s)'%\
                (str(refname), str(reflocal), str(reftablename), str(refforeign))
            ref_statement = "ALTER TABLE %s ADD %s;" % \
                    (string.upper(table_name), ref_statement)
            self.sql_constraint = string.join((self.sql_constraint, \
                            fill_header(foriegn_header, refname), \
                            ref_statement),"\n\n")

class MySQLBuilder(SQLBuilder):
    """
    Subclass for MySQL specific stuff.  Much less to do here, I'm not trying to
    do foreign key constraints yet.

    """

    def __init__(self, tables):
        """
        Call the parent initialization.  Nothing special here.

        """
        SQLBuilder.__init__(self, tables)

    def fix_datatype(self, coltype):
        """
        The only fix we have to do (so far) is change 'datetime' to 'timestamp'.

        """
        if coltype == 'timestamp':
            return 'datetime'
        else:
            return coltype

    def fix_value(self, table_name, colname, coltype, colvalue):
        """
        Do autoincrementing correctly for MySQL

        """
        if colvalue == 'identity':
            self.additional_constraints = \
                            string.join((self.additional_constraints, \
                            "PRIMARY KEY (%s)" %  string.upper(colname)), "\n")
            col_statement = string.join((colname, coltype, \
                      "NOT NULL AUTO_INCREMENT"), " ")
        else:
            col_statement = string.join((colname, coltype, colvalue), " ")
        return col_statement


if __name__=='__main__':
    """
    Main program body.  Process arguments given, instanciate the classes.
    Process the XML file and generate the SQL output(s) requested.

    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--filename", help="Filename for input",
            dest="filename")
    parser.add_option("-d", "--drop", help="Drop tables before creating",
            dest="drop", action="store_true")
    parser.add_option("-m", "--mysql", help="filename for mysql output",
            dest="mysql")
    parser.add_option("-p", "--postgresql",
            help="filename for postgresql output", dest="postgresql")
    parser.add_option("-a", "--alchemy",
                      help="filename for alchemy output", dest="alchemy")
    parser.add_option("-V", "--verbose", action="store_true",
            help="verbose output (debugging)", dest="verbose")
    (options, args) = parser.parse_args()

    verbose = options.verbose
    if options.filename:
        filename = options.filename
        if os.path.exists(filename):
            print "Processing", filename
            diaxml_obj = DiaContentHandler(filename)
            tables = diaxml_obj.get_data()
        else:
            parser.error("You must specify a valid file, cannot access".filename)
    else:
        parser.error("You must specify a filename")

    if options.postgresql:
        sql_builder_obj = PostgresBuilder(tables)
        sql_builder_obj.make_database()
        if verbose:
            sql_builder_obj.print_raw_data()
        outfile = open(options.postgresql, "w")
        outfile.write(sql_builder_obj.sql_create)
        outfile.flush()
    elif options.mysql:
        sql_builder_obj = MySQLBuilder(tables)
        sql_builder_obj.make_database()
        if verbose:
            sql_builder_obj.print_raw_data()
        outfile = open(options.mysql, "w")
        outfile.write(sql_builder_obj.sql_create)
        outfile.flush()
    elif options.alchemy:
        sql_builder_obj = AlchemyMaker(tables)
        sql_builder_obj.make_database()
        if verbose:
            sql_builder_obj.print_raw_data()
        outfile = open(options.alchemy, "w")
        outfile.write(sql_builder_obj.sql_create)
        outfile.flush()

