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
import os
import time
import threading
import rrdtool
import globalvars
from Logger import Logger

dupe_round_err = "Serious problem: dupe round %s for team %s\n"

web_dir = "/var/www"
score_filename = "latest_scores.html"
graph_filename = "graphs.html"
flags_filename = "flags.html"
scoreboard_filename = "ctf_scoreboard.html"

style = '''
<style type="text/css">
body
{
        background-color:#000000;
}
h1
{
        color:orange;
        text-align:center;
        color:#00aa00;
}
p
{
        font-family:"Courier";
        font-size:18px;
        color:#00aa00;
}
</style>
'''

header = "<html><head>%s</head>" % style

ccdc_scoreboard_html = '''
<html>
   <head>
      <title>Wilmington University Cyber Wildcats CTF Current Score</title>
      <meta http-equiv="refresh" content="10">
   </head>
   <frameset cols="40%%,*">
      <frameset rows="30%%,70%%">
         <frame src="%s">
         <frame src="%s">
      </frameset> <frameset rows="50%%,50%%">
         <frameset rows="50%%,50%%">
            <frame src="bt1injects.html">
            <frame src="bt1pwnage.html">
         </frameset>
         <frameset rows="50%%,50%%">
            <frame src="bt2injects.html">
            <frame src="bt2pwnage.html">
         </frameset>
      </frameset>
   </frameset>
</html>
''' % (score_filename, graph_filename)

binjitsu_scoreboard_html = '''
<html>
   <head>
      <title>Wilmington University Cyber Wildcats CTF Current Score</title>
      <meta http-equiv="refresh" content="10">
   </head>
   <frameset cols="40%%,*">
      <frameset rows="30%%,70%%">
         <frame src="%s">
         <frame src="flags.html">
      </frameset>
      <frame src="%s">
   </frameset>
</html>
''' % (score_filename, graph_filename)

#if globalvars.binjitsu:
scoreboard_html = binjitsu_scoreboard_html
#else:
#   scoreboard_html = ccdc_scoreboard_html

score_html = header + "<body><H1>%s</H1></body></html>" 

graph_html = header + "<body>%s</body></html>"

flags_html = header + "<body>%s</body></html>"

flags_team_section = '''
<H2>%s</H2>%s
'''

flags_sub_section = '''
<H3>%s</H3><p>%s
'''

score_line = "<br>Round %s Team %s Grand Total %s\n"
graph_line = "<img src=\"%s\">"



class Scoreboard(threading.Thread):

   def __init__(self, teams, flag_store):
      threading.Thread.__init__(self)
      self.logger = Logger("Scoreboard")
      self.teams = teams
      self.rounds = {}
      self.latest_scores = {}
      self.rrdfilename = "ctf.rrd"
      self.made_rrd = []
      for team in self.teams.keys():
         self.rounds[team] = []
         self.latest_scores[team] = score_line
      self.flag_store = flag_store

   def run(self):
      while True:
         score_file = open("%s/%s" % (web_dir, score_filename), "w")
         scores = ""
         graphs = ""
         flag_text = ""
         for team in self.teams.keys():
            # render the graphs
            round_score = self.teams[team].tally()
            this_round = round_score[0]
            score = round_score[1]
            scores += self.latest_scores[team] % (this_round, team, score)
            self.rrd_update(team, score)
            self.rrd_graph(team)
            team_imgfilename = "%s.png" % team
            graphs += graph_line % team_imgfilename
            # Get flag info and text
            flags = self.flag_store.get_stolen(team)
            flag_subtext = flags_sub_section % \
                             ("<p>Flags Stolen", ", ".join(flags))
            flags = self.flag_store.get_lost(team)
            flag_subtext += flags_sub_section % \
                             ("<p>Flags Lost", ", ".join(flags))
            flag_text += flags_team_section % \
                            (team, flag_subtext)
         bandits = self.flag_store.get_bandits()
         flag_final_txt = ""
         for bandit in bandits.keys():
            flags = ", ".join(bandits[bandit])
            flag_subtext = flags_sub_section % \
                          (("<p>Flags Stolen by %s" % bandit), flags)
            flag_final_txt += flag_subtext
         flag_text += flags_team_section % \
                            ("<p>Redcell", flag_final_txt)
         # write the flags file
         flags_file = open("%s/%s" % (web_dir, flags_filename), "w")
         flags_file.write(flags_html % flag_text)
         flags_file.close()
         #finish writing the score file
         score_file.write(score_html % scores)
         score_file.close()
         # write the scoreboard
         scoreboard = open("%s/%s" % (web_dir, scoreboard_filename), "w")
         scoreboard.write(scoreboard_html)
         scoreboard.close()
         # write the graph html file
         graph_file = open("%s/%s" % (web_dir, graph_filename), "w")
         graph_file.write(graph_html % graphs)
         graph_file.close()
         time.sleep(10)

   def rrd_update(self, team, score):
      rrdfilename = "%s.rrd" % team
      if os.path.exists(rrdfilename):
         pass
      else:
         rrdtool.create(rrdfilename,"-s", "300",\
               "DS:GrandTotal:GAUGE:600:-1250000:12500003",\
               "RRA:LAST:0.5:1:50")
      self.logger.out("Updating RRD for team %s with score %s" % \
            (team, score))   
      rrdtool.update(rrdfilename, "-t", "GrandTotal", "N:%s" % score)

   def rrd_graph(self, team):
      rrdfilename = "%s.rrd" % team
      imgfilename = "%s/%s.png" % (web_dir, team)
      rrdtool.graph(imgfilename, \
            "-s", "-14h",\
            "-t", "Total score for %s" % team, \
            "--lazy", \
            "-h", "300", "-w", "500", \
            "-l 0", "-a", "PNG", \
            "-v Points", \
            "DEF:GrandTotal=%s:GrandTotal:LAST" % rrdfilename,
            "AREA:GrandTotal#AA0000:Points",\
            "LINE1:GrandTotal#FF0000",\
            "GPRINT:GrandTotal:MAX:  Max\\: %5.1lf %s",\
            "GPRINT:GrandTotal:LAST: Current\\: %5.1lf %Spoints\\n",\
            "HRULE:0#000000")
