# coding: utf-8
from logging import getLogger

from plugin import Plugin
from pydantic import BaseModel

l = getLogger(__name__)


class Config(BaseModel):
    test: str = 'default'
    info: str = 'default'
    debug: bool = False


class DefaultData(BaseModel):
    calls: int = 0


# Config Way 1: 定义插件类并使用
p = Plugin(
    __name__,
    config=Config,
    data=DefaultData
)
c: Config = p.config
d: DefaultData = p.data

@p.route('/hello')
def hello():
    d.calls += 1
    return {
        'message': f'Hello from {p.name} plugin',
        'username': p.global_config.page.name,  # Config Way 2: 直接读取全局配置
        'today_visits': p.global_data.data.metrics.today.get('/', 0),
        'info': c.info,
        'test': c.test,
        'debug': c.debug,
        'calls': d.calls
    }


@p.global_route('/testplugin')
def globaltest():
    return 'Hello World!'

# @plugin.route('/utils')
# def utils_demo():
#     return {
#         "utility_function": plugin.utils.some_utility()
#     }


def init():
    # 对于插件来说直接访问 app context 不好
    # plugin.app.logger.info(f"插件 '{plugin.name}' 自定义初始化完成")
    if c.debug:
        l.info('test plugin load ok')


# 设置插件初始化函数
p.init = init
