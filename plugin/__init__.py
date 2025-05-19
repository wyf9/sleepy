# coding: utf-8

import os
import importlib
import inspect
import yaml
import functools
from typing import Dict, List, Callable, Any, Optional, Union, Tuple

from config import Config
from utils import Utils
from data import Data
from _utils import get_path, SleepyException

# 全局变量，用于存储插件注册的路由和事件处理器
_plugin_routes: Dict[str, Dict[str, Callable]] = {}
_plugin_event_handlers: Dict[str, List[Tuple[str, Callable]]] = {}

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
                print(f"Error in plugin {plugin_name} event handler for {event_name}: {str(e)}")

    return results


class PluginClass:
    '''
    将传递给插件的配置
    '''
    name: str
    example_config: dict
    user_config: Config
    u: Utils
    d: Data

    def __init__(self, name: str, example_config: dict, user_config: Config, utils: Utils, data: Data):
        '''
        初始化一项插件的所需资源 (?)

        :param namespace: 插件 id
        :param example_config: **(插件的)** 示例配置
        :param user_config: **(全局的)** 用户配置
        :param utils: 实用功能 (`utils.Utils`)
        :param data: 用户数据 (`data.Data`)
        '''
        self.name = name
        self.example_config = example_config
        self.user_config = user_config
        self.u = utils
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
            raise SleepyException(f'Plugin config not found in plugin/{self.name}/plugin.yaml!')

    @property
    def config(self):
        '''
        获取插件的配置项 (example + user)
        - *一般在前端 html 中使用, 后端请用 `getconf()`*
        '''
        return {**self.example_config, **self.user_config.plugin.get(self.name, {})}


class Plugin:
    # [id, frontend, backend, ConfigClass]
    plugins: list[tuple[str, str, object, PluginClass]] = []
    # 存储已注册的插件路由
    registered_routes = {}

    def __init__(self, config: Config, utils: Utils, data: Data, app=None):
        '''
        初始化插件功能，包括验证插件可用性

        :param config: 用户配置 (`config.Config`)
        :param utils: 实用功能 (`utils.Utils`)
        :param data: 用户数据 (`data.Data`)
        :param app: Flask应用实例，用于注册路由
        '''
        self.c = config
        self.u = utils
        self.d = data
        self.app = app

        # 检查目录是否存在 (以及是否有插件定义 (plugin.yaml))
        for i in self.c.plugin_enabled:
            plugin_path = get_path(f'plugin/{i}/plugin.yaml')
            if os.path.exists(plugin_path) and os.path.isfile(plugin_path):
                pass
            else:
                self.u.exception(f'Plugin not exist: {i}')

        # 加载插件配置
        for i in self.c.plugin_enabled:
            # 加载单个插件配置
            with open(get_path(f'plugin/{i}/plugin.yaml'), 'r', encoding='utf-8') as f:
                plugin: dict = yaml.safe_load(f)
                f.close()

            is_frontend = plugin.get('frontend', False)
            is_backend = plugin.get('backend', False)
            self.u.debug(f'initing plugin, name: {i}, frontend: {is_frontend}, backend: {is_backend}')

            # 加载前端代码 (index.html)
            if is_frontend:
                with open(get_path(f'plugin/{i}/index.html'), 'r', encoding='utf-8') as ff:
                    plugin_frontend = ff.read()
                    ff.close()
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
                            utils=self.u,
                            data=self.d
                        )

                        # 调用插件的初始化函数
                        try:
                            plugin_backend.init_plugin(plugin_config)
                            self.u.info(f"Plugin '{i}' initialized successfully")
                        except Exception as e:
                            self.u.error(f"Error initializing plugin '{i}': {str(e)}")

                    # 注册插件路由
                    if self.app and i in _plugin_routes:
                        self._register_plugin_routes(i)

                except Exception as e:
                    self.u.error(f"Error loading plugin '{i}': {str(e)}")
                    plugin_backend = None

            # 加载配置
            plugin_config = PluginClass(
                name=i,
                example_config=plugin.get('config', {}),
                user_config=self.c,
                utils=self.u,
                data=self.d
            )

            # 保存此项
            self.plugins.append((i, plugin_frontend, plugin_backend, plugin_config))

        # 触发应用启动事件
        if self.c.plugin_enabled:
            trigger_event('app_started', self)

        self.u.info(f'plugins enabled: {", ".join(self.c.plugin_enabled)}' if self.c.plugin_enabled else 'no plugin enabled.')

    def _register_plugin_routes(self, plugin_name):
        """
        注册插件的路由

        :param plugin_name: 插件名称
        """
        if plugin_name not in _plugin_routes:
            return

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
                'methods': route_info['methods']
            })

            self.u.info(f"Registered route '{full_rule}' for plugin '{plugin_name}'")

    def trigger_event(self, event_name, *args, **kwargs):
        """
        触发事件

        :param event_name: 事件名称
        :param args: 传递给事件处理器的位置参数
        :param kwargs: 传递给事件处理器的关键字参数
        :return: 所有事件处理器的返回值列表
        """
        return trigger_event(event_name, *args, **kwargs)
