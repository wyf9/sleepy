# coding: utf-8

import os
import importlib
import functools
from typing import Dict, List, Callable, Any, Tuple
from logging import getLogger
from flask import Flask

import yaml

from config import Config
import utils as u
from data import Data

# 全局变量，用于存储插件注册的路由和事件处理器
l = getLogger(__name__)
_plugin_routes: Dict[str, Dict[str, Callable]] = {}  # 插件命名空间下的路由
_plugin_global_routes: Dict[str, Dict[str, Callable]] = {}  # 全局路由
_plugin_event_handlers: Dict[str, List[Tuple[str, Callable]]] = {}
_plugin_admin_cards: Dict[str, Dict[str, Any]] = {}  # 插件注册的管理后台卡片

# 插件装饰器

def route(rule: str, methods: List[str] = None):
    """
    装饰器：注册插件路由

    :param rule: 路由规则，例如 '/api/myplugin'
    :param methods: HTTP方法列表，例如 ['GET', 'POST']
    """
    if methods is None:
        methods = ['GET']

    def decorator(func):
        # 获取插件名称（从函数模块名称中提取）
        module_name = func.__module__
        plugin_name = module_name.split('.')[-1]

        # 初始化插件路由字典
        if plugin_name not in _plugin_routes:
            _plugin_routes[plugin_name] = {}

        # 注册路由
        _plugin_routes[plugin_name][rule] = {
            'func': func,
            'methods': methods
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def global_route(rule: str, methods: List[str] = None):
    """
    装饰器：注册全局路由（不带插件前缀）

    :param rule: 路由规则，例如 '/hello'
    :param methods: HTTP方法列表，例如 ['GET', 'POST']
    """
    if methods is None:
        methods = ['GET']

    def decorator(func):
        # 获取插件名称（从函数模块名称中提取）
        module_name = func.__module__
        plugin_name = module_name.split('.')[-1]

        # 初始化插件全局路由字典
        if plugin_name not in _plugin_global_routes:
            _plugin_global_routes[plugin_name] = {}

        # 注册全局路由
        _plugin_global_routes[plugin_name][rule] = {
            'func': func,
            'methods': methods
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def admin_card(title: str, order: int = 100):
    """
    装饰器：注册管理后台卡片

    :param title: 卡片标题
    :param order: 卡片排序顺序（数字越小越靠前）
    """
    def decorator(func):
        # 获取插件名称（从函数模块名称中提取）
        module_name = func.__module__
        plugin_name = module_name.split('.')[-1]

        # 初始化插件管理后台卡片字典
        if plugin_name not in _plugin_admin_cards:
            _plugin_admin_cards[plugin_name] = {}

        # 生成卡片ID
        card_id = f"{plugin_name}_{len(_plugin_admin_cards[plugin_name])}"

        # 注册管理后台卡片
        _plugin_admin_cards[plugin_name][card_id] = {
            'title': title,
            'order': order,
            'func': func
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def on_event(event_name: str):
    """
    装饰器：注册事件处理器

    :param event_name: 事件名称，例如 'data_updated', 'app_started'
    """
    def decorator(func):
        # 获取插件名称（从函数模块名称中提取）
        module_name = func.__module__
        plugin_name = module_name.split('.')[-1]

        # 初始化插件事件处理器列表
        if event_name not in _plugin_event_handlers:
            _plugin_event_handlers[event_name] = []

        # 注册事件处理器
        _plugin_event_handlers[event_name].append((plugin_name, func))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def trigger_event(event_name: str, *args, **kwargs):
    """
    触发事件，调用所有注册的事件处理器

    :param event_name: 事件名称
    :param args: 传递给事件处理器的位置参数
    :param kwargs: 传递给事件处理器的关键字参数
    :return: 所有事件处理器的返回值列表
    """
    results = []

    if event_name in _plugin_event_handlers:
        for plugin_name, handler in _plugin_event_handlers[event_name]:
            try:
                result = handler(*args, **kwargs)
                results.append((plugin_name, result))
            except Exception as e:
                print(f"Error in plugin {plugin_name} event handler for {event_name}: {e}")

    return results


class PluginClass:
    '''
    将传递给插件的配置
    '''
    name: str
    example_config: dict
    user_config: Config
    d: Data

    def __init__(self, name: str, example_config: dict, user_config: Config, data: Data):
        '''
        初始化一项插件的所需资源 (?)

        :param namespace: 插件 id
        :param example_config: **(插件的)** 示例配置
        :param user_config: **(全局的)** 用户配置
        :param data: 用户数据 (`data.Data`)
        '''
        self.name = name
        self.example_config = example_config
        self.user_config = user_config
        self.d = data

    def getconf(self, *key: str):
        '''
        通过键获取插件的配置项
        - 顺序: 用户配置 -> 插件 plugin.yaml
        '''
        # 1. from user config
        try:
            value = self.user_config.plugin.get(self.name, {})
            for k in key:
                value = value[k]
            return value
        except KeyError:
            pass

        # 2. from plugin.yaml
        try:
            value = self.example_config
            for k in key:
                value = value[k]
            return value
        except KeyError:
            raise u.SleepyException(f'Plugin config not found in plugin/{self.name}/plugin.yaml!')

    @property
    def config(self):
        '''
        获取插件的配置项 (example + user)
        - *一般在前端 html 中使用, 后端请用 `getconf()`*
        '''
        return {**self.example_config, **self.user_config.plugin.get(self.name, {})}

    def register_route(self, rule: str, func: Callable, methods: List[str] = None):
        """
        注册插件的路由

        :param rule: 路由规则，例如 '/api/endpoint'
        :param func: 处理函数
        :param methods: HTTP方法列表，例如 ['GET', 'POST']
        """
        if methods is None:
            methods = ['GET']

        # 获取插件名称
        if self.name not in _plugin_routes:
            _plugin_routes[self.name] = {}

        # 注册路由
        _plugin_routes[self.name][rule] = {
            'func': func,
            'methods': methods
        }

        l.debug(f"Route '{rule}' registered for plugin '{self.name}'")

    def register_event(self, event_name: str, handler: Callable):
        """
        注册事件处理器

        :param event_name: 事件名称
        :param handler: 处理函数
        """
        if event_name not in _plugin_event_handlers:
            _plugin_event_handlers[event_name] = []
            
        _plugin_event_handlers[event_name].append((self.name, handler))
        l.debug(f"Event handler registered for '{event_name}' in plugin '{self.name}'")


class Plugin:
    # [id, frontend, backend, ConfigClass]
    plugins: list[tuple[str, str, object, PluginClass]] = []
    # 存储已注册的插件路由
    registered_routes = {}
    # 存储已注册的管理后台卡片
    admin_cards = []

    c: Config
    d: Data
    app: Flask

    def __init__(self, config: Config, data: Data, app=None):
        '''
        初始化插件功能，包括验证插件可用性

        :param config: 用户配置 (`config.Config`)
        :param utils: 实用功能 (`utils.Utils`)
        :param data: 用户数据 (`data.Data`)
        :param app: Flask应用实例，用于注册路由
        '''
        self.c = config
        self.d = data
        self.app = app

        # 检查目录是否存在 (以及是否有插件定义 (plugin.yaml))
        if self.c.plugin_enabled:
            for i in self.c.plugin_enabled:
                plugin_path = u.get_path(f'plugin/{i}/plugin.yaml')
                if os.path.exists(plugin_path) and os.path.isfile(plugin_path):
                    pass
                else:
                    u.exception(f'Plugin not exist: {i}')

        # 检查插件是否为第一次运行
        for i in self.c.plugin_enabled:
            if not self.is_first_run(i):
                l.info(f'Plugin {i} is not first run.')
            else:
                l.info(f'Plugin {i} is first run, created mark file.')

        # 加载插件配置
        if self.c.plugin_enabled:
            for i in self.c.plugin_enabled:
                # 加载单个插件配置
                with open(u.get_path(f'plugin/{i}/plugin.yaml'), 'r', encoding='utf-8') as f:
                    plugin: dict = yaml.safe_load(f)
                    f.close()

                is_frontend = plugin.get('frontend', False)
                is_backend = plugin.get('backend', False)
                l.debug(f'initing plugin, name: {i}, frontend: {is_frontend}, backend: {is_backend}')

                # 加载前端代码 (index.html)
                plugin_frontend = ''
                if is_frontend:
                    html_path = u.get_path(f'plugin/{i}/index.html')
                    if not os.path.exists(html_path):
                        l.warning(f'Plugin {i} does not have index.html, skipping frontend loading.')
                    else:
                        try:
                            with open(html_path, 'r', encoding='utf-8') as ff:
                                plugin_frontend = ff.read()
                        except Exception as e:
                            l.error(f'Failed to load index.html for plugin {i}: {e}')
                else:
                    plugin_frontend = ''

                # 加载后端代码 (__init__.py)
                plugin_backend = None
                if is_backend:
                    try:
                        plugin_backend = importlib.import_module(f'plugin.{i}')

                        # 检查并调用插件的初始化函数
                        if hasattr(plugin_backend, 'init_plugin'):
                            plugin_config = PluginClass(
                                name=i,
                                example_config=plugin.get('config', {}),
                                user_config=self.c,
                                data=self.d
                            )

                            # 调用插件的初始化函数
                            try:
                                plugin_backend.init_plugin(plugin_config)
                                l.info(f"Plugin '{i}' initialized successfully")
                            except Exception as e:
                                l.error(f"Error initializing plugin '{i}': {e}")

                        # 注册插件路由
                        if self.app and i in _plugin_routes:
                            self._register_plugin_routes(i)

                    except Exception as e:
                        l.error(f"Error loading plugin '{i}': {e}")
                        plugin_backend = None

                # 加载配置
                plugin_config = PluginClass(
                    name=i,
                    example_config=plugin.get('config', {}),
                    user_config=self.c,
                    data=self.d
                )

                # 保存此项
                self.plugins.append((i, plugin_frontend, plugin_backend, plugin_config))

        # 注册管理后台卡片
        self._register_admin_cards()

        # 触发应用启动事件
        trigger_event('app_started', self)

        l.info(f'plugins enabled: {", ".join(self.c.plugin_enabled)}' if self.c.plugin_enabled else 'no plugin enabled.')

    def is_first_run(self, plugin_name: str) -> bool:
        """
        检查插件是否为第一次运行

        :param plugin_name: 插件名称
        :return: 如果是第一次运行返回 True，否则返回 False
        """
        
        # 如果存在 .mark 文件，表示不是第一次运行
        mark_file = u.get_path(f'plugin/{plugin_name}/.mark')
        if os.path.exists(mark_file):
            return False
        else:
            # 如果不存在 .mark 文件，表示是第一次运行
            # 创建 .mark 文件
            l.info(f'Plugin {plugin_name} is first run, creating mark file.')
            with open(mark_file, 'w', encoding='utf-8') as f:
                f.write('SPMF')
                f.close()
            # 安装依赖
            if os.path.exists(u.get_path(f'plugin/{plugin_name}/requirements.txt')):
                # 检查退出状态
                if os.system(f'pip install -r {u.get_path(f"plugin/{plugin_name}/requirements.txt")}') != 0:
                    l.error(f'Failed to install dependencies for plugin {plugin_name}. Please check requirements.txt.')
                else:
                    # 安装成功
                    l.info(f'Plugin {plugin_name} dependencies installed.')
            else:
                l.warning(f'Plugin {plugin_name} does not have requirements.txt, skipping dependency installation.')
            return True

    def _register_plugin_routes(self, plugin_name):
        """
        注册插件的路由

        :param plugin_name: 插件名称
        """
        # 注册插件命名空间下的路由
        if plugin_name in _plugin_routes:
            for rule, route_info in _plugin_routes[plugin_name].items():
                # 构建完整的路由规则
                full_rule = f'/plugin/{plugin_name}{rule}'

                # 注册路由
                self.app.route(full_rule, methods=route_info['methods'])(route_info['func'])

                # 记录已注册的路由
                if plugin_name not in self.registered_routes:
                    self.registered_routes[plugin_name] = []

                self.registered_routes[plugin_name].append({
                    'rule': full_rule,
                    'methods': route_info['methods'],
                    'type': 'namespace'
                })

                l.info(f"Registered route '{full_rule}' for plugin '{plugin_name}'")

        # 注册全局路由
        if plugin_name in _plugin_global_routes:
            for rule, route_info in _plugin_global_routes[plugin_name].items():
                # 全局路由直接使用规则，不添加前缀
                full_rule = rule

                # 注册路由
                self.app.route(full_rule, methods=route_info['methods'])(route_info['func'])

                # 记录已注册的路由
                if plugin_name not in self.registered_routes:
                    self.registered_routes[plugin_name] = []

                self.registered_routes[plugin_name].append({
                    'rule': full_rule,
                    'methods': route_info['methods'],
                    'type': 'global'
                })

                l.info(f"Registered global route '{full_rule}' for plugin '{plugin_name}'")

    def _register_admin_cards(self):
        """
        注册插件的管理后台卡片
        """
        # 清空已注册的卡片
        self.admin_cards = []

        # 如果没有启用的插件，直接返回
        if not self.c.plugin_enabled:
            return

        # 遍历所有启用的插件
        for plugin_name in self.c.plugin_enabled:
            # 检查插件是否注册了管理后台卡片
            if plugin_name in _plugin_admin_cards:
                for card_id, card_info in _plugin_admin_cards[plugin_name].items():
                    # 获取插件配置
                    plugin_config = None
                    for p in self.plugins:
                        if p[0] == plugin_name:
                            plugin_config = p[3]
                            break

                    if plugin_config:
                        try:
                            # 调用卡片函数获取内容
                            content = card_info['func'](plugin_config)

                            # 添加到已注册的卡片列表
                            self.admin_cards.append({
                                'id': card_id,
                                'plugin_name': plugin_name,
                                'title': card_info['title'],
                                'order': card_info['order'],
                                'content': content
                            })

                            l.info(f"Registered admin card '{card_info['title']}' for plugin '{plugin_name}'")
                        except Exception as e:
                            l.error(f"Error registering admin card for plugin '{plugin_name}': {e}")

        # 按顺序排序卡片
        if self.admin_cards:
            self.admin_cards.sort(key=lambda x: x['order'])

    def get_admin_cards(self):
        """
        获取所有注册的管理后台卡片

        :return: 卡片列表
        """
        return self.admin_cards

    def trigger_event(self, event_name, *args, **kwargs):
        """
        触发事件

        :param event_name: 事件名称
        :param args: 传递给事件处理器的位置参数
        :param kwargs: 传递给事件处理器的关键字参数
        :return: 所有事件处理器的返回值列表
        """
        return trigger_event(event_name, *args, **kwargs)
