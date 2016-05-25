import importlib
import threading
import scorebot.settings
import scorebot.utils.log as logger

SCANNER = None


class PluginScanner(threading.Thread):
    def __init__(self):
        self.base_dir = scorebot.settings.PLUGIN_DIR
        threading.Thread.__init__(self)

    def run(self):
        # while True:
        pass


def init():
    pass
