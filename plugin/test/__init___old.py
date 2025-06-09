from plugin import PluginConfig, get_logger, route

l = get_logger(__name__)


class Plugin(PluginConfig):
    example_config = {
        'a': 1,
        'test': '114514aaa'
    }

    def init(self):
        l.debug('test Init!')
        l.debug(f'test: {self.get_config("test")}')

    @route('/abc')
    def route_abc(self):
        return f'''
test: {self.get_config('test')}
username: {self.user_config.page.name}
status: {self.data.data.get('status')}
last updated: {self.data.data.get('last_updated')}
'''
