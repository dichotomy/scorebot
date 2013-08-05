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
import re
import os
import time
import random
import rrdtool
import threading
import globalvars
import subprocess
from Logger import Logger

dupe_round_err = "Serious problem: dupe round %s for team %s\n"

web_dir = "/var/www"
score_filename = "latest_scores.html"
scores_filename = "scores.html"
graph_filename = "graphs.html"
health_filename = "health.html"
flags_filename = "flags.html"
scoreboard_filename = "ctf_scoreboard.html"

movie_html = '''<HTML><HEAD>
      <TITLE>Movie Frame</TITLE>
      <script type="text/javascript" src="/jwplayer/jwplayer.js"></script>
      <meta http-equiv="refresh" content="%s">
</HEAD>

<BODY bgcolor="000000"> 
   <div id="myElement">Loading the player...</div>

   <script type="text/javascript">
      jwplayer("myElement").setup({
        file: "%s",
        autostart: true,
        width:  "100%%",
        height:  "100%%"
      });
   </script>
</BODY></HTML> '''

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

marquee
{
        font-family:"Courier";
        font-size:48px;
        color:#00aa00;
}

p
{
        font-family:"Courier";
        font-size:18px;
        color:#00aa00;
}

th
{
        font-family:"Courier";
        font-size:24px;
        color:#FF9900;
}

td
{
        font-family:"Courier";
        font-size:24px;
        color:#00aa00;
}       

td.green
{
        font-family:"Courier";
        font-size:24px;
        color:#ffffff;
        background-color:#00aa00;
}       

td.yellow
{
        font-family:"Courier";
        font-size:24px;
        color:#000000;
        background-color:#ffff00;
}       

td.red
{
        font-family:"Courier";
        font-size:24px;
        color:#000000;
        background-color:#ff0000;
}       


</style>
'''

header = "<html><head>%s</head>" % style

ccdc_scoreboard_html = '''
<html>
   <head>
      <title>CTF Current Score</title>
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
      <title>CTF Current Score</title>
      <meta http-equiv="refresh" content="10">
   </head>
   <frameset rows="5%%,*">
      <frame src="marquee.html">
      <frameset cols="30%%,*">
         <frameset rows="30%%,70%%">
            <frame src="%s">
            <frame src="flags.html">
         </frameset>
         <frame src="%s">
      </frameset>
   </frameset>
</html>
''' % (scores_filename, health_filename)

#if globalvars.binjitsu:
scoreboard_html = binjitsu_scoreboard_html
#else:
#   scoreboard_html = ccdc_scoreboard_html

score_html = header + "<body><H1>%s</H1></body></html>" 

marquee_html = header + "<body><marquee behavior=\"scroll\" direction=\"left\" scrollamount=\"20\">%s</marquee></body></html>" 

scores_html = header + "<body><h1>Score</h><br>%s</body></html>" 

graph_html = header + "<body>%s</body></html>"

flags_html = header + "<body><h1>Flags</h1>%s</body></html>"

health_html = header + "<body><h1>Current Blueteam Scored System Health</h><br>%s<br><h1>Equipment and facilities for the CTF environment are provided by<a href=\"http://www.wilmu.edu/index.aspx\"><img src=\"http://www.wilmu.edu/images/logos/logo_large.jpg\"></a></p></body></html>"

flags_team_section = '''
<H2>%s</H2>%s
'''

health_team_section = '''
<H2>%s</H2>%s
'''


flags_sub_section = '''
<H3>%s</H3><p>%s
'''

table = '<table border="1" style="float: left;">\n%s\n</table>\n'
nowrap_table = '<table border="1"">\n%s\n</table>\n'
table_row = '\t<tr>\n%s\t</tr>\n'
table_header = '\t\t<th>%s</th>\n'
table_cell = '\t\t\t<td>%s</td>\n'
table_cell_green = '\t\t\t<td class="green">%s</td>\n'
table_cell_yellow = '\t\t\t<td class="yellow">%s</td>\n'
table_cell_red = '\t\t\t<td class="red">%s</td>\n'

score_line = "<br>Round %s Team %s Score %s\n"
graph_line = "<img src=\"%s\">"



class Scoreboard(threading.Thread):

   def __init__(self, teams, flag_store, message_store):
      threading.Thread.__init__(self)
      self.logger = Logger("Scoreboard")
      self.teams = teams
      self.latest_scores = {}
      self.rrdfilename = "ctf.rrd"
      self.made_rrd = []
      for team in self.teams.keys():
         self.latest_scores[team] = score_line
      self.flag_store = flag_store
      self.message_store = message_store
      self.team_scores = {}
      self.current_round = 0
      self.all_flags_found = []
      self.new_flag = False
      self.movie_dir = "/var/www/movies/"
      self.duration_re =re.compile("Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})")
      self.marquee="This is Scorebot v 1.0"

   def write_marquee(self):
      self.marquee = self.message_store.get_message()
      marquee_file = open("%s/%s" % (web_dir, "marquee.html"), "w")
      marquee_file.write(marquee_html % self.marquee)
      marquee_file.close()

   def calc_scores(self):
      num_teams = len(self.teams.keys())
      for team in self.teams.keys():
         #this round
         (this_round, this_score) = self.teams[team].get_score()
         if self.team_scores.has_key(this_round):
            self.team_scores[this_round][team] = this_score
         else:
            self.team_scores[this_round] = {}
            self.team_scores[this_round][team] = this_score
      for this_round in sorted(self.team_scores.keys(), reverse=True):
         #The first round with all teams is the current round
         if (len(self.team_scores[this_round].keys()) == num_teams):
            self.current_round = this_round
            break
         else:
            pass

   def write_scores(self):
      this_table = table_header % "Round"
      for team in self.teams.keys():
         this_table += table_header % team
      this_table = table_row % this_table
      rounds = range(self.current_round - 4, self.current_round + 1)
      for this_round in sorted(rounds, reverse=True):
         this_row = table_cell % this_round
         if this_round <= 0:
            break
         for team in sorted(self.team_scores[this_round].keys(), key=str.lower):
            this_row += table_cell % str(self.team_scores[this_round][team])
         this_row = table_row % this_row
         this_table += this_row
      this_table = table % this_table
      # write the scoreboard
      scores = open("%s/%s" % (web_dir, scores_filename), "w")
      scores.write(scores_html % this_table)
      scores.close()

   def write_health(self):
      health_content = ""
      for team in sorted(self.teams.keys()):
         team_name = team
         host_hash = self.teams[team].get_health()
         #this_table_header = table_header % "Host"
         this_table_header = table_header % team
         services = {}
         for host in sorted(host_hash.keys()):
            for service in sorted(host_hash[host].keys()):
               if services.has_key(service):
                  pass
               else:
                  services[service] = {}
         for service in sorted(services.keys()):
            this_table_header += table_header % service
         this_table = table_row % this_table_header
         for host in sorted(host_hash.keys()):
            this_row = table_cell % host
            for service in sorted(services.keys()):
               if host_hash[host].has_key(service):
                  health = host_hash[host][service]
                  if health == 0:
                     this_row += table_cell_red % health
                  elif health == 1:
                     this_row += table_cell_yellow % health
                  elif health == 2:
                     this_row += table_cell_green % health
                  else:
                     self.logger.err("Unknown health status %s for %s\n" % \
                           (health, host+service))
               else:
                  this_row += table_cell % ""
            this_row = table_row % this_row
            this_table += this_row
         this_table = table % this_table
         #health_content += health_team_section % (team_name, this_table)
         health_content += this_table
      health = open("%s/%s" % (web_dir, health_filename), "w")
      health.write(health_html % health_content)
      health.close()

   def find_flags(self):
      flag_text = ""
      this_table = table_header % "Flags"
      for team in self.teams.keys():
         this_table += table_header % team
      this_table = table_row % this_table
      # Stolen flags
      if globalvars.binjitsu:
         this_row = table_cell % "Stolen"
         for team in self.teams.keys():
            flags = self.flag_store.get_stolen(team)
            this_row += table_cell % "\n".join(flags)
         this_row = table_row % this_row
         this_table += this_row
      # Lost flags
      this_row = table_cell % "Lost"
      for team in self.teams.keys():
         flags = self.flag_store.get_lost(team)
         this_row += table_cell % "\n".join(flags)
         for flag in flags:
            if flag in self.all_flags_found:
               next
            else:
               self.all_flags_found.append(flag)
               self.new_flag = True
      this_row = table_row % this_row
      this_table += this_row
      this_table = nowrap_table % this_table
      flag_text += this_table
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

   def run(self):
      while True:
         self.write_marquee()
         self.calc_scores()
         self.write_scores()
         self.find_flags()
         self.write_health()
         score_file = open("%s/%s" % (web_dir, score_filename), "w")
         scores = ""
         graphs = ""
         for team in self.teams.keys():
            # render the graphs
            round_score = self.teams[team].get_score()
            this_round = round_score[0]
            score = round_score[1]
            scores += self.latest_scores[team] % (this_round, team, score)
            self.rrd_update(team, score)
            self.rrd_graph(team)
            team_imgfilename = "%s.png" % team
            graphs += graph_line % team_imgfilename
         #finish writing the score file
         score_file.write(score_html % scores)
         score_file.close()
         # write the scoreboard
         scoreboard = open("%s/%s" % (web_dir, scoreboard_filename), "w")
         if self.new_flag and not globalvars.nomovie:
            (movie_time, movie) = self.pick_movie()
            movie_name = "movies/%s" % movie
            self.logger.out("picked movie %s, length %s" % \
                     (movie_name, movie_time))
            if movie_name:
               scoreboard.write(movie_html % (movie_time, movie_name))
               self.new_flag = False
            else:
               scoreboard.write(scoreboard_html)
         else:
            scoreboard.write(scoreboard_html)
         scoreboard.close()
         # write the graph html file
         graph_file = open("%s/%s" % (web_dir, graph_filename), "w")
         graph_file.write(graph_html % graphs)
         graph_file.close()
         time.sleep(10)

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
            next
         (hrs, mins, secs, dec) = match_obj.groups()
         if hrs > 0:
            next
         time = secs + str(int(mins) * 60) 
         movies[filename] = time
      if len(movies) > 0:
         options = movies.keys()
         index = random.randrange(0,len(options))
         movie_name = options[index]
         movie_time = movies[movie_name]
         return (movie_time, movie_name)
      else:
         return False

   def rrd_update(self, team, score):
      rrdfilename = "%s.rrd" % team
      if os.path.exists(rrdfilename):
         pass
      else:
         rrdtool.create(rrdfilename,"-s", "300",\
               "DS:GrandTotal:GAUGE:600:-1250000:12500003",\
               "RRA:LAST:0.5:1:50")
      self.logger.out("Updating RRD for team %s with score %s\n" % \
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
