#!/usr/bin/env python
__author__ = 'dichotomy'
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

from bottle import *
import sys
import logging
import threading
import traceback
import globalvars
from Logger import Logger


class BottleServer(threading.Thread):

    def __init__(self, teams, flag_store, message_store, movies, host, port):
        threading.Thread.__init__(self)
        self._host = host
        self._port = port
        self._app = Bottle()
        self._route()
        self.logger = Logger("BottleServer")
        self.teams = teams
        self.movies = movies
        self.flag_store = flag_store
        self.message_store = message_store
        self.whitelist = ["scoreboard.html", "movie.html", "scoreboard2.html"]
        self.all_flags_found = []

    def _route(self):
        self._app.route('/<filename>', method="GET", callback=self._index)
        self._app.route('/css/<filename>', method="GET", callback=self._css)
        self._app.route('/jscript/<filename>', method="GET", callback=self._jscript)
        self._app.route('/jwplayer/<filename>', method="GET", callback=self._jwplayer)
        self._app.route('/movies/<filename>', method="GET", callback=self._movies)
        self._app.route('/images/<filename>', method="GET", callback=self._images)
        self._app.route('/scores', callback=self._scores)
        self._app.route('/scores2', callback=self._scores2)
        self._app.route('/health', callback=self._health)
        self._app.route('/marquee', callback=self._marquee)
        self._app.route('/movie', callback=self._movie)
        self._app.route('/flags', callback=self._flags)
        self._app.route('/flags2', callback=self._flags2)
        self._app.route('/beacons', callback=self._beacons)
        self._app.route('/tickets', callback=self._tickets)
        self._app.route('/redcell', callback=self._redcell)
        self._app.route('/teamnames', callback=self._teamnames)

    def run(self):
        self._app.run(host=self._host, port=self._port, server="paste")

    def _teamnames(self):
        teamnames = {"teamnames":[]}
        for team in self.teams:
            teamnames["teamnames"].append(team)
        return teamnames

    def _css(self, filename):
        return static_file(filename, root="css")

    def _jscript(self, filename):
        return static_file(filename, root="jscript")

    def _jwplayer(self, filename):
        return static_file(filename, root="jwplayer")

    def _movies(self, filename):
        return static_file(filename, root="movies")

    def _images(self, filename):
        return static_file(filename, root="images")

    def _index(self, filename="scoreboard.html"):
        if filename in self.whitelist:
            return static_file(filename, root="")
        else:
            return template("Forbidden!")

    def _redcell(self):
        bandits = self.flag_store.get_bandits()
        redcell = {}
        for bandit in bandits:
            redcell[bandit] = {"flags": bandits[bandit]}
        beaconlist = self.flag_store.get_beacons()
        for bandit in beaconlist:
            if bandit in redcell:
                redcell[bandit]["beacons"] = {}
            else:
                redcell[bandit] = {"beacons"}
                redcell[bandit]["beacons"] = {}
            for pwned in beaconlist[bandit]:
                for team in self.teams:
                    if self.teams[team].has_ip(pwned):
                        if team in redcell[bandit]:
                            redcell[bandit]["beacons"][team] += 1
                        else:
                            redcell[bandit]["beacons"][team] = 1
        return redcell

    def _beacons(self):
        beaconlist = self.flag_store.get_beacons()
        beacons = {}
        for bandit in beaconlist:
            beacons[bandit] = {}
            for pwned in beaconlist[bandit]:
                for team in self.teams:
                    if self.teams[team].has_ip(pwned):
                        if team in beacons[bandit]:
                            beacons[bandit][team] += 1
                        else:
                            beacons[bandit][team] = 1
        return beacons

    def _tickets(self):
        team_tickets = {}
        for team in self.teams.keys():
            team_tickets[team] = self.teams[team].get_tickets()
        return team_tickets

    def _scores(self):
        team_scores = {}
        for team in self.teams.keys():
            team_scores[team] = self.teams[team].get_score()
        return team_scores

    def _scores2(self):
        team_scores = {}
        for team in self.teams.keys():
            team_scores[team] = self.teams[team].get_score_detail()
        return team_scores

    def _health(self):
        team_health = {}
        for team in self.teams.keys():
            team_health[team] = self.teams[team].get_health()
        return team_health

    def _marquee(self):
        return {"marquee": self.message_store.get_message()}

    def _movie(self):
        return self.movies.check_movie()

    def _flags(self):
        flags = {}
        flags["lost"] = {}
        flags["integrity"] = {}
        flags["bandits"] = self.flag_store.get_bandits()
        if globalvars.binjitsu:
            flags["stolen"] = {}
            for team in self.teams.keys():
                stolen_flags = self.flag_store.get_stolen(team)
                flags["stolen"][team] = stolen_flags
        # Lost flags
        for team in self.teams.keys():
            lost_flags = self.flag_store.get_lost(team)
            flags["lost"][team] = lost_flags
            for flag in lost_flags:
                if flag in self.all_flags_found:
                    continue
                else:
                    self.all_flags_found.append(flag)
                    flags["newflag"] = 1
        for team in self.teams.keys():
            flags["integrity"][team] = self.flag_store.get_integrity(team)
        return flags

    def _flags2(self):
        flags = {}
        flags["teams"] = {}
        flags["bandits"] = self.flag_store.get_bandits()
        if globalvars.binjitsu:
            flags["binjitsu"] = {}
            for team in self.teams.keys():
                stolen_flags = self.flag_store.get_stolen(team)
                flags["binjitsu"][team] = stolen_flags
        # Lost flags
        for team in self.teams.keys():
            flags["teams"][team] = {}
            lost_flags = self.flag_store.get_lost(team)
            flags["teams"][team]["lost"] = lost_flags
            for flag in lost_flags:
                if flag in self.all_flags_found:
                    continue
                else:
                    self.all_flags_found.append(flag)
                    flags["newflag"] = 1
        for team in self.teams.keys():
            flags["teams"][team]["integrity"] = self.flag_store.get_integrity(team)
        return flags

if __name__=="__main__":
    server = BottleServer(host='localhost', port=8090)
    server.start()
