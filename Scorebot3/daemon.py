#!/usr/bin/python

import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'scorebot.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scorebot.settings')

from scorebot.utils.daemons import DaemonEntry, start_daemon


if __name__ == '__main__':
    django.setup()
    start_daemon()
    sys.exit(0)
