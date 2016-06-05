import importlib
import scorebot.utils.log as logger

"""
    SBE Init Loader

    Add full class paths to this file to add modules to be ran at runtime.
    Every loaded module must have a 'def init()' staticmethod and cannot block

"""

MODULES_TO_LOAD = [
    'scorebot.utils.plugins.pluginscanner',
]


def load_init():
    for iloader in MODULES_TO_LOAD:
        try:
            imod = importlib.import_module(iloader)
            if imod:
                try:
                    imod.init()
                    logger.debug(__name__, 'Module "%s" loaded successfully!' % iloader)
                except AttributeError:
                    logger.error(__name__, 'Module "%s" does not have an "init" method!' % iloader)
                except Exception:
                    logger.get_logger(__name__).error('Module "%s" threw an exception on load!' % iloader,
                                                      exec_info=True)
        except ImportError:
            logger.error(__name__, 'Module "%s" failed to load! (Does it exist?)' % iloader)
