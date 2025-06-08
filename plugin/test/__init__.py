from plugin import PluginClass
from logging import getLogger

l = getLogger(f'plugin.{__name__}')


class Plugin(PluginClass):
    example_config = {
        'a': 1,
        'test': '114514aaa'
    }

    def init(self):
        l.debug('test Init!')
        l.debug(f'test: {self.get_config("test")}')