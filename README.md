scorebot 3.0
========

Scoring Engine for CTF competitions
https://github.com/dichotomy/scorebot

DESCRIPTION
Scorebot is a scoring engine for CTF competitions.  It is built upon a Blue Team / Red Team model, where Blue Teams defend flags against Red teams.  (Blue Teams may also attack other Blue Teams to steal flags).  Scoring is based upon flags stolen, scored service up time, and injects submitted (there is no scoring tracking for injects yet).

DEPENDENCIES
Scorebot depends upon dnspython (http://www.dnspython.org/).
Scorebot runs best in Linux, but should work in Windows (never tested, no promises).
Python 2.7 or greater is recommended.

To install all dependencies on Ubuntu, run:
   apt-get install python-dnspython python-rrdtool apache2 python-pymongo python-dns python-setuptools
   easy_install jaraco.modb

    easy_install sqlalchemy
    easy_install flask
    easy_install flask-sqlalchemy
    easy_install twisted



BUGS
Yes, there are bugs.  These will be documented later.  ;)

COPYRIGHT

Copyright (C) 2011  Dichotomy <dichotomy@riseup.net>

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
