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

import getopt
import sys
import time
import Queue
import traceback
import jaraco.modb
from pymongo import MongoClient
from bson.objectid import ObjectId

from decoder import *
import globalvars
from Logger import Logger
from CTFgame import CTFgame

shortargs = "hbc:vdqnr:d:"
longargs = ["help", "verbose", "debug", "quick", "binjitsu", "config=", \
                "nomovie", "resume=", "database="]

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
        --database=<db_name>
        --resume=<gameID>
        --config=<filename>
"""

def usage():
    sys.stdout.write(usage_str % sys.argv[0])
    sys.exit(2)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
    except getopt.GetoptError, err:
        sys.stderr.write("Had a problem: %s" % err)
        traceback.print_exc(file=sys.stderr)
    cfg_file = "scorebotcfg.json"
    database = "Scorebot"
    obj_id = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--config"):
            cfg_file = a
        elif o in ("-b", "--binjitsu"):
            globalvars.binjitsu = True
        elif o in ("-v", "--verbose"):
            globalvars.verbose = True
        elif o in ("-d", "--debug"):
            globalvars.debug = True
        elif o in ("-q", "--quick"):
            globalvars.quick = True
        elif o in ("-q", "--quick"):
            globalvars.quick = True
        elif o in ("-n", "--nomovie"):
            globalvars.nomovie = True
        elif o in ("-r", "--resume"):
            obj_id = a
        elif o in ("-d", "--database"):
            database = a
        else:
            assert False, "unhandled option"
    client = MongoClient()
    db = client[database]
    col = db["Games"]
    if obj_id:
        ctf_game_obj = CTFgame(col, cfg_file, obj_id)
        # Cannot use jaraco.modb - bugs prevent Scorebot's structure from being recovered
        # https://github.com/jsonpickle/jsonpickle/issues/74
        #obj_id = ObjectId(resume)
        #result = col.find_one(obj_id)
        #ctf_game_obj = jaraco.modb.decode(decode_dict(result))
    else:
        ctf_game_obj = CTFgame(col, cfg_file)
        # Cannot use jaraco.modb - bugs prevent Scorebot's structure from being recovered
        # https://github.com/jsonpickle/jsonpickle/issues/74
        #json_obj = jaraco.modb.encode(ctf_game_obj)
        #obj_id = col.save(json_obj)
        #sys.stdout.write("Your game ID is %s\n" % str(obj_id))
    ctf_game_obj.start_game()
    ctf_game_obj.start()
    while True:
        time.sleep(10)
        # Cannot use jaraco.modb - bugs prevent Scorebot's structure from being recovered
        # https://github.com/jsonpickle/jsonpickle/issues/74
        #json_obj = jaraco.modb.encode(ctf_game_obj)
        #json_obj["_id"] = obj_id
        #col.save(json_obj)
    sys.stdout.write("GAME OVER.\n")
    sys.stdout.write("Your game ID is %s\n" % str(obj_id))

if __name__ == "__main__":
    main()
