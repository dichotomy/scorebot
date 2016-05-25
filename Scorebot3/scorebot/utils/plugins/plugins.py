import scorebot.utils.log as logger

from django.http import HttpResponse

LOADED_PLUGINS = dict()


def add_plugin(plugin_module):
    try:
        plugin_name = plugin_module.name
    except AttributeError:
        try:
            plugin_name = plugin_module.get_name()
        except AttributeError:
            logger.error('')


class Plugin:
    name = None
    version = None
    form_request = None
    save_request = None

    def __init__(self, plugin_module):
        self.__test_module(plugin_module)
        self.module = plugin_module

    def get_name(self):
        return self.name

    def get_version(self):
        return self.version

    def handle_startup(self):
        try:
            self.module.startup()
        except AttributeError:
            try:
                self.module.on_startup()
            except AttributeError:
                logger.warning(__name__, 'Module "%s" does not have a startup method!' % self.get_name())
            except Exception:
                logger.get_logger(__name__).error('Module "%s" threw an Exception on startup!' % self.get_name(),
                                                  exec_info=True)
        except Exception:
            logger.get_logger(__name__).error('Module "%s" threw an Exception on startup!' % self.get_name(),
                                              exec_info=True)

    def handle_request(self, request):
        try:
            pass
        except TypeError:
            logger.error(__name__, 'Module "%s" does not support the correct parameters!')
        except Exception:
            logger.get_logger(__name__).error('Module "%s" threw an Exception on request!' % self.get_name(),
                                              exec_info=True)
        return HttpResponse('The requested plugin has encountered an error.<br/><br/>Please alert the developers '
                            'of this problem.', status=500)

    def __test_module(self, plugin_module):
        try:
            self.name = plugin_module.name
        except AttributeError:
            try:
                self.name = plugin_module.get_name()
            except AttributeError:
                raise Exception('Module does not have a name parameter!')
        try:
            self.version = plugin_module.version
        except AttributeError:
            try:
                self.name = plugin_module.get_version()
            except AttributeError:
                raise Exception('Module does not have a version parameter!')
        try:
            self.request = plugin_module.request
        except AttributeError:
            try:
                self.request = plugin_module.do_request
            except AttributeError:
                try:
                    self.request = plugin_module.handle_request
                except AttributeError:
                    raise Exception('Module does not have a request parameter!')
