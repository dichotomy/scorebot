import logging
import logging.config

LOG_HANDLES = dict()


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
    logger_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'default_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'standard',
                'filename': log_file,
                'maxBytes': 10485760,
                'backupCount': 20,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {
                'handlers': ['default', 'default_file'],
                'level': log_level,
                'propagate': True
            }
        }
    }
    init_logger(logger_config)
