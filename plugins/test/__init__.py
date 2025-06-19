# coding: utf-8
from logging import getLogger

from plugin import Plugin, PluginConfig

l = getLogger(__name__)


class Config(PluginConfig):
    info: str = 'default'


plugin = Plugin(__name__, Config)


@plugin.route('/hello')
def hello():
    return {
        "message": f"Hello from {plugin.name} plugin",
        "username": plugin.global_config.page.name,
        "today_visits": plugin.global_data.data.metrics.today.get('/', 0)
    }


@plugin.global_route('/testplugin')
def globaltest():
    return 'Hello World!'

# @plugin.route('/utils')
# def utils_demo():
#     return {
#         "utility_function": plugin.utils.some_utility()
#     }


def init():
    # 对于插件来说直接访问 data 不好

    # 访问应用上下文
    # plugin.app.logger.info(f"插件 '{plugin.name}' 自定义初始化完成")
    l.info('test plugin load ok')


# 设置插件初始化函数
plugin.init = init
