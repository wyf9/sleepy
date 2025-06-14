from plugin import route, get_plugin_config, get_plugin_data, get_current_plugin, get_plugin_name
from logging import getLogger

l = getLogger(__name__)

# 初始化函数


def init_plugin():
    l.debug('test Init!')
    config = get_plugin_config('test')
    l.debug(f'test: {config.get("test")}, my name: {get_plugin_name()}')

# 路由处理函数


@route('/abc')
def route_abc():
    config = get_plugin_config('test')
    data = get_plugin_data('test')
    current_plugin = get_current_plugin()

    return f'''
test: {config.get('test')}
username: {current_plugin.user_config.page.name if current_plugin else 'N/A'}
status: {data.data.get('status') if data else 'N/A'}
'''
