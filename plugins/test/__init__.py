# coding: utf-8
from logging import getLogger

from plugin import Plugin
from pydantic import BaseModel

l = getLogger(__name__)


class Config(BaseModel):
    test: str = 'default'
    info: str = 'default'
    debug: bool = False


# Config Way 1: 定义插件类并使用
p = Plugin(
    __name__,
    config=Config,
    data={'calls': 0}
)
c: Config = p.config


@p.route('/hello')
def hello():
    with p.data_context() as d:
        d['calls'] += 1
        return {
            'message': f'Hello from {p.name} plugin',
            'username': p.global_config.page.name,  # Config Way 2: 直接读取全局配置
            'test': c.test,
            'debug': c.debug,
            'calls': d['calls']
        }

def hello2():
    return 'test2'

p.add_route(hello2, '/hello2')
# p.add_route(hello2, 'hello3')

@p.global_route('/testplugin')
def globaltest():
    return 'Hello World!'

# p.add_global_route(globaltest, '/testplugin2')
# p.add_global_route(globaltest, '/testplugin3')

# @plugin.route('/utils')
# def utils_demo():
#     return {
#         "utility_function": plugin.utils.some_utility()
#     }


def init():
    # 对于插件来说直接访问 app context 不好
    # plugin.app.logger.info(f"插件 '{plugin.name}' 自定义初始化完成")
    if c.debug:
        l.info(f'test plugin load ok, calls now: {p.data["calls"]}')


# 设置插件初始化函数
p.init = init

p.add_index_card('test-1', 'contenttest')

@p.index_card('test-2')
def testcard():
    return 'testtest'