from plugin import route, get_logger, get_current_plugin, get_plugin_config

l = get_logger(__name__)

# 可选：保留类用于配置定义


class PluginConfig:
    example_config = {
        'a': 1,
        'test': '114514aaa'
    }

# 初始化函数


def init_plugin():
    l.debug('test Init!')
    config = get_plugin_config('test')
    l.debug(f'test: {config.get("test")}')

# 路由处理函数


@route('/abc')
def route_abc():
    plugin = get_current_plugin()
    config = get_plugin_config('test')
    data = plugin.data if plugin else None

    return f'''
test: {config.get('test')}
username: {plugin.user_config.page.name if plugin else 'N/A'}
status: {data.data.get('status') if data else 'N/A'}
'''
