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


def exception(module_name, log_data):
    return get_logger(module_name).exception(log_data)
