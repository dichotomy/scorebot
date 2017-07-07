#!/usr/bin/python

import os
import sys
import time
import django
import importlib
import threading
import importlib.util

from datetime import datetime, timedelta

SCOREBOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.chdir(SCOREBOT_DIR)
sys.path.insert(0, SCOREBOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scorebot.settings")
os.environ['DJANGO_SETTINGS_MODULE'] = 'scorebot.settings'

from django.conf import settings
# TODO: Fix logging to journalctl to loggin via daemon is separate file than http daemon
#from scorebot.utils import logger


class DaemonEntry:
    """
    Scorebot v3: DaemonEntry

    Stores the state of the SBE Daemon threads.
    """

    def __init__(self, name, trigger, method, timeout=0):
        if name is None:
            raise ValueError('Parameter "name" cannot be None!')
        if not isinstance(trigger, int) or int(trigger) <= 0:
            raise ValueError('Parameter "trigger" must be a positive "integer" object type!')
        if not callable(method):
            raise ValueError('Parameter "method" must be a "callable" object type!')
        self.end = None
        self.next = None
        self.name = name
        self.thread = None
        self.method = method
        self.running = False
        self.trigger = trigger
        self.timeout = timeout

    def stop(self):
        self.running = False
        self.thread.stop()
        self.thread = None

    def start(self):
        if self.timeout > 0:
            self.end = datetime.now() + timedelta(seconds=self.timeout)
        else:
            self.end = None
        self.next = datetime.now() + timedelta(seconds=self.trigger)
        self.running = True
        self.thread = DaemonThread(self)
        self.thread.start()

    def _stop(self):
        self.thread = None
        self.running = False

    def __bool__(self):
        return self.running and self.thread is not None

    def is_ready(self, now):
        if self.running or self.thread is not None:
            return False
        if self.next is None:
            return True
        if (now - self.next).seconds <= 0:
            return True
        return False

    def is_timeout(self, now):
        if self.end is None:
            return False
        if (now - self.end).seconds <= 0:
            return True
        return False


class Daemon(threading.Thread):
    """
    Scorebot v3: Daemon

    The main thread that runs outside of the mod_wsgi and preforms time based events.  This thread calls other threads
    to do work and is responsible for watching the other threads.
    """

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.running = False
        self.daemons = list()

    def run(self):
        self.running = True
        while self.running:
            now = datetime.now()
            for daemon in self.daemons:
                if daemon.__bool__():
                    if daemon.is_timeout(now):
                        print('Killing Daemon "%s".' % daemon.name)
                        #logger.debug('SBE-DAEMON', 'Killing Daemon "%s".' % daemon.name)
                        daemon.stop()
                else:
                    if daemon.is_ready(now):
                        daemon.start()
            time.sleep(1)

    def stop(self):
        for daemon in self.daemons:
            if daemon.__bool__():
                daemon.stop()
        self.running = False

    def load_daemons(self, daemon_dir):
        if not os.path.isdir(daemon_dir):
            return
        daemon_list = os.listdir(daemon_dir)
        if len(daemon_list) > 0:
            for daemon_file in daemon_list:
                if '.py' in daemon_file and not (' ' in daemon_file or '-' in daemon_file or '-' in daemon_file):
                    try:
                        daemon_loader = importlib.util.spec_from_file_location(daemon_file.replace('.py', ''),
                                                                               os.path.join(daemon_dir, daemon_file))
                        if daemon_loader is None:
                            continue
                        daemon_class = importlib.util.module_from_spec(daemon_loader)
                        if daemon_class is None:
                            continue
                        daemon_loader.loader.exec_module(daemon_class)
                        try:
                            daemon_class_def = getattr(daemon_class, 'init_daemon')
                            if daemon_class_def is not None and callable(daemon_class_def):
                                daemon_entry = daemon_class_def()
                                if daemon_entry is not None:
                                    self.daemons.append(daemon_entry)
                                    print('Loaded Daemon "%s".' % daemon_class.__name__)
                                    #logger.debug('SBE-DAEMON', 'Loaded Daemon "%s".' % daemon_class.__name__)
                            del daemon_class
                            del daemon_loader
                        except AttributeError:
                            print('Class "%s" does not have the "init_daemon" method!' % daemon_class.__name__)
                            #logger.warning('SBE-DAEMON', 'Class "%s" does not have the "init_daemon" method!' %
                            #               daemon_class.__name__)
                    except Exception as loadError:
                        print('Exception occurred when loading Daemon "%s"! %s' % (daemon_file, str(loadError)))
                        #logger.debug('SBE-DAEMON', 'Exception occurred when loading Daemon "%s"! %s' %
                        #             (daemon_file, str(loadError)))
        del daemon_list


class DaemonThread(threading.Thread):
    """
    Scorebot v3: DaemonThread

    This is the worker thread for each triggered Daemon call.  This ensures that work is not done on the main thread.
    """

    def __init__(self, daemon_entry):
        threading.Thread.__init__(self, daemon=True)
        self.running = False
        self.entry = daemon_entry

    def run(self):
        self.running = True
        print('Starting Daemon "%s".' % self.entry.name)
        #logger.debug('SBE-DAEMON', 'Starting Daemon "%s".' % self.entry.name)
        try:
            self.entry.method()
        except Exception as threadError:
            print('Daemon "%s" threw an Exception when called! %s.' % (self.entry.name, str(threadError)))
            #logger.debug('SBE-DAEMON', 'Daemon "%s" threw an Exception when called! %s.' %
            #             (self.entry.name, str(threadError)))
        print('Daemon "%s" Finished.' % self.entry.name)
        #logger.debug('SBE-DAEMON', 'Daemon "%s" Finished.' % self.entry.name)
        self.running = False
        self.entry._stop()

    def stop(self):
        # TODO: Not much we can do here to stop a running process
        self.running = False


if __name__ == '__main__':
    django.setup()
    print('Starting SBE Daemon process..')
    #logger.info('SBE-DAEMON', 'Starting SBE Daemon process..')
    daemon = Daemon()
    daemon.load_daemons(os.path.join(SCOREBOT_DIR, settings.DAEMON_DIR))
    print('Loading "%s" daemons..' % len(daemon.daemons))
    #logger.debug('SBE-DAEMON', 'Loading "%s" daemons..' % len(daemon.daemons))
    try:
        daemon.start()
        while daemon.running:
            pass
    except KeyboardInterrupt:
        daemon.stop()
        print('Stopping SBE Daemon process..')
        #logger.info('SBE-DAEMON', 'Stopping SBE Daemon process..')
        sys.exit(0)
