import os
import logging
import logging.config

LOG_HANDLES = dict()

LOGGER_INSTANCE = None
LOGGER_DEFAULT_LEVEL = 'DEBUG'
LOGGER_DEFAULT_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'


class Logger(object):
    def __init__(self, log_directory):
        if log_directory is None:
            raise ValueError('Parameter "log_directory" cannot be None!')
        if not os.path.isdir(log_directory):
            if not os.path.exists(log_directory):
                try:
                    os.mkdir(log_directory)
                except OSError as osError:
                    raise OSError('Parameter "log_directory" is not a directory! (%s)' % str(osError))
            # TODO: Fix, causes issues for some reason
            #raise OSError('Parameter "log_directory" is not a directory!')
        self.log_handles = dict()
        self.log_dir = log_directory

    def info(self, log_name, log_message):
        if log_name not in self.log_handles:
            self.setup_log(log_name)
        self.log_handles[log_name].info(log_message)

    def error(self, log_name, log_message):
        if log_name not in self.log_handles:
            self.setup_log(log_name)
        self.log_handles[log_name].error(log_message)

    def debug(self, log_name, log_message):
        if log_name not in self.log_handles:
            self.setup_log(log_name)
        self.log_handles[log_name].debug(log_message)

    def warning(self, log_name, log_message):
        if log_name not in self.log_handles:
            self.setup_log(log_name)
        self.log_handles[log_name].warning(log_message)

    def setup_log(self, log_name, log_level=LOGGER_DEFAULT_LEVEL, log_format=LOGGER_DEFAULT_FORMAT):
        log_handler = logging.FileHandler(os.path.join(self.log_dir, '%s.log' % log_name.lower()))
        log_handler.setFormatter(logging.Formatter(log_format))
        log_logger = logging.getLogger(log_name)
        log_logger.setLevel(log_level)
        log_logger.addHandler(log_handler)
        self.log_handles[log_name] = log_logger

    def setup_log_stdout(self, log_name, log_level=LOGGER_DEFAULT_LEVEL, log_format=LOGGER_DEFAULT_FORMAT):
        if log_name not in self.log_handles:
            self.setup_log(log_name, log_level=log_level, log_format=log_format)
        log_stream = logging.StreamHandler()
        log_stream.setFormatter(logging.Formatter(log_format))
        self.log_handles[log_name].addHandler(log_stream)


def log_event(event_message):
    pass


def log_info(log_name, log_message):
    if LOGGER_INSTANCE is None:
        print('[!] Logger is not initialized yet! Please initialize it!\n[+] %s' % log_message)
    LOGGER_INSTANCE.info(log_name, log_message)


def log_error(log_name, log_message):
    if LOGGER_INSTANCE is None:
        print('[!] Logger is not initialized yet! Please initialize it!\n[+] %s' % log_message)
    LOGGER_INSTANCE.error(log_name, log_message)


def log_debug(log_name, log_message):
    if LOGGER_INSTANCE is None:
        print('[!] Logger is not initialized yet! Please initialize it!\n[+] %s' % log_message)
    LOGGER_INSTANCE.debug(log_name, log_message)


def log_warning(log_name, log_message):
    if LOGGER_INSTANCE is None:
        print('[!] Logger is not initialized yet! Please initialize it!\n[+] %s' % log_message)
    LOGGER_INSTANCE.warning(log_name, log_message)


def log_init(log_directory, log_default=None):
    global LOGGER_INSTANCE
    global LOGGER_DEFAULT_LEVEL
    if LOGGER_INSTANCE is None:
        LOGGER_INSTANCE = Logger(log_directory)
    if log_default is not None:
        LOGGER_DEFAULT_LEVEL = log_default


def log_score(score_event, message, score_object=None):
    pass


def log_stdout(log_name, log_level=LOGGER_DEFAULT_LEVEL, log_format=LOGGER_DEFAULT_FORMAT):
    if LOGGER_INSTANCE is not None:
        LOGGER_INSTANCE.setup_log_stdout(log_name, log_level, log_format)

# OLD

def init_logger(settings):
    logging.config.dictConfig(settings)


def get_logger(module_name):
    if module_name in LOG_HANDLES:
        return LOG_HANDLES[module_name]
    LOG_HANDLES[module_name] = logging.getLogger(module_name)
    return LOG_HANDLES[module_name]


def info(module_name, log_data):
    return get_logger(module_name).info(log_data)


def error(module_name, log_data):
    return get_logger(module_name).error(log_data)


def debug(module_name, log_data):
    return get_logger(module_name).debug(log_data)


def warning(module_name, log_data):
    return get_logger(module_name).warning(log_data)


def init_simple(log_file, log_level='INFO'):
    simple_config = {'version': 1, 'disable_existing_loggers': False,
                     'formatters': { 'standard': { 'format': LOGGER_DEFAULT_FORMAT},},
                     'handlers': {'default_file': {'class': 'logging.handlers.RotatingFileHandler', 'level': log_level,
                                                   'formatter': 'standard', 'filename': log_file, 'maxBytes': 10485760,
                                                   'backupCount': 20,'encoding': 'utf8'}},
                     'loggers': {'': {'handlers': ['default_file'], 'level': log_level, 'propagate': True}}}
    init_logger(simple_config)