import os
import time
import importlib
import threading
import importlib.util

from django.conf import settings
from django.utils import timezone
from scorebot.utils.logger import log_debug, log_error, log_info, log_warning, log_stdout


def start_daemon():
    log_stdout('DAEMON', 'DEBUG')
    log_info('DAEMON', 'Starting the Scorebot3 Daemon process..')
    daemon_thread = Daemon()
    daemon_thread.load_daemons(settings.DAEMON_DIR)
    log_debug('DAEMON', 'Loaded "%d" daemons, [%s]..' % (len(daemon_thread.daemons),
                                                         ', '.join([str(d.name) for d in daemon_thread.daemons])))
    try:
        daemon_thread.start()
        while daemon_thread.running:
            pass
    except KeyboardInterrupt:
        daemon_thread.stop()
        log_info('DAEMON', 'Stopping SBE Daemon process..')


class DaemonEntry(object):
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
        self.next = None
        self.name = name
        self.thread = None
        self.method = method
        self.running = False
        self.trigger = trigger
        self.timeout = timeout

    def stop(self):
        log_debug('DAEMON', 'Attempting to stop daemon "%s"..' % self.name)
        self.running = False
        self.thread.stop()
        log_debug('DAEMON', 'Stopped daemon "%s"..' % self.name)
        self.thread = None

    def start(self):
        log_debug('DAEMON', 'Attempting to start daemon "%s"..' % self.name)
        if self.timeout > 0:
            log_debug('DAEMON', 'Daemon "%s" has a set timeout of "%d" seconds..' % (self.name, self.timeout))
        self.next = timezone.now()
        self.running = True
        self.thread = DaemonThread(self)
        self.thread.start()
        log_debug('DAEMON', 'Started Daemon "%s"!' % self.name)

    def del_stop(self):
        self.thread = None
        self.running = False

    def __bool__(self):
        return self.running and self.thread is not None

    def is_ready(self, now):
        if self.running or self.thread is not None:
            return False
        if self.next is None:
            return True
        if (now - self.next).seconds >= self.trigger:
            return True
        return False

    def is_timeout(self, now):
        if self.timeout == 0:
            return False
        if (now - self.next).seconds > self.timeout:
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
            now = timezone.now()
            for daemon in self.daemons:
                if daemon.__bool__():
                    if daemon.is_timeout(now):
                        log_debug('DAEMON', 'killing Daemon "%s" due to timeout!' % self.name)
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
                                    log_debug('DAEMON', 'Loaded Daemon "%s"!' % daemon_class.__name__)
                            del daemon_class
                            del daemon_loader
                        except AttributeError:
                            log_warning('DAEMON',
                                        'Daemon class for "%s" does not have the "init_daemon" method, ignoring!' %
                                        daemon_class.__name__)
                    except Exception as loadError:
                        log_error('DAEMON', 'An error ocured when attempting to load Daemon "%s"! Exception: "%s' %
                                  (daemon_file, str(loadError)))
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
        log_info('DAEMON', 'Starting Daemon "%s"..' % self.entry.name)
        try:
            self.entry.method()
        except Exception as threadError:
            log_error('DAEMON', 'Daemon "%s" encountered an error when running! Exception: "%s"' %
                      (self.entry.name, str(threadError)))
        log_info('DAEMON', 'Daemon "%s" finished running.' % self.entry.name)
        self.running = False
        self.entry.del_stop()

    def stop(self):
        # TODO: Not much we can do here to stop a running process
        self.running = False
