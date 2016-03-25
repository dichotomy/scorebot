'''
Created on Dec 29, 2011

@author: dichotomy@riseup.net

Scoreboard.py is a module in the scorebot program.  It produces the scorebaord HTML pages.

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

import os
import re
import subprocess
import traceback
import random


class Movies(object):

    def __init__(self, logger):
        self.logger = logger
        self.movie_dir = "movies/"
        self.play_movie = True
        self.duration_re =re.compile("Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})")

    def set_movie(self):
        self.play_movie = True

    def check_movie(self):
        if self.play_movie:
            self.play_movie = False
            movie = self.pick_movie()
            if movie:
                print "Sending movie %s at length %s" % (movie["name"], movie["length"])
                return {"movie": movie}
            else:
                return {}

    def pick_movie(self):
        movies = {}
        for filename in os.listdir(self.movie_dir):
            full_filename = os.path.join(self.movie_dir, filename)
            try:
                p = subprocess.Popen(["ffmpeg", "-i", full_filename], \
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
            except:
                self.logger.err("Error processing movie:\n%s\n" % full_filename)
                traceback.print_exc(file=self.logger)
            if "Duration" in err:
                match_obj = self.duration_re.search(err)
            else:
                self.logger.err("Error processing movie:%s\n%s\n" % \
                                            (full_filename, err))
                continue
            (hrs, mins, secs, dec) = match_obj.groups()
            if int(hrs) > 0:
                continue
            time = secs + str(int(mins) * 60000)
            uri = "movies/%s" % filename
            movies[uri] = time
        if len(movies) > 0:
            options = movies.keys()
            index = random.randrange(0,len(options))
            movie_hash = {}
            movie_name = options[index]
            movie_hash["name"] = movie_name
            movie_hash["length"] = movies[movie_name]
            return movie_hash
        else:
            return False


