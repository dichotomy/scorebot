'''

Global variables for Scorebot

Copyright (C) 2011  Dichotomy

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

verbose = False
quick = False
debug = False
binjitsu = False
dns = "172.16.33.3"
sep = "=" * 80
message_ip = [ '127.0.0.1', '172.16.33.25'] # IPs allowed to change the banner message on the scoreboard.root@git-work:~/fun#
ctfnet_re_ip = "172"  #Host.py# First octet of your ip range.  Ex. 192.168.1.1 wouth be 192
web_port = 8090  #BottleServer.py# Port to listen on for the scoreboard webserver
goldcell_mail_svr = "172.16.33.5" #Injects.py# Goldcell's mail server
goldcell_email = '"Gold Team" <admin@goldteam.net>' #Injects.py# the From address of goldcell's email.