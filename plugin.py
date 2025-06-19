import os
import importlib
import typing as t
from logging import getLogger
from functools import wraps

import flask
from pydantic import BaseModel

from models import ConfigModel
from data import Data
import utils as u

l = getLogger(__name__)


class PluginConfig(BaseModel):
    '''
    插件默认配置 (使用 pydantic 解析)
    '''


class Plugin:
    '''
    Sleepy 插件接口
    '''
    _registry = {}
    _routes = []

    def __init__(self, name: str, config: type[PluginConfig] = PluginConfig):
        """
        初始化插件

        :param name: 插件名称 (通常为 `__name__`)
        :param config: 插件默认配置 (可选)
        """
        # 初始化 & 注册插件
        self.name = name.split('.')[-1]
        Plugin._registry[self.name] = self

        # 加载配置
        
        l.debug(f'[plugin] {self.name} registered')

    @property
    def global_config(self) -> ConfigModel:
        '''
        全局配置 (`config.Config()`)
        '''
        return PluginInit.instance.c

    @property
    def global_data(self) -> Data:
        '''
        全局数据 (`data.Data().data`)
        '''
        return PluginInit.instance.d

    @property
    def app(self) -> flask.Flask:
        """访问 flask.Flask 应用实例"""
        return PluginInit.instance.app

    def route(self, rule: str, **options: t.Any):
        '''
        注册插件路由 (访问: `/plugin/<name>/<rule>`)

        :param rule: 路由规则 (路径)
        ```
        @plugin.route('/endpoint')
        def handler():
            return "Hello from plugin"
        ```
        '''
        def decorator(f):
            endpoint = options.pop('endpoint', f.__name__)
            full_rule = f'/plugin/{self.name}{"" if rule.startswith("/") else "/"}{rule}'

            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            # 临时存储理由信息
            self._routes.append({
                'rule': full_rule,
                'endpoint': f"plugin.{self.name}.{endpoint}",
                'view_func': wrapper,
                'options': options
            })
            return wrapper
        return decorator

    def global_route(self, rule: str, **options: t.Any):
        '''
        注册全局插件路由 (访问: `/<rule>`)

        :param rule: 路由规则 (路径)
        ```
        @plugin.route('/global-endpoint')
        def handler():
            return "Hello from plugin"
        ```
        '''
        def decorator(f):
            endpoint = options.pop('endpoint', f.__name__)
            full_rule = f'{"" if rule.startswith("/") else "/"}{rule}'

            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            # 临时存储理由信息
            self._routes.append({
                'rule': full_rule,
                'endpoint': f"plugin._global_.{endpoint}",
                'view_func': wrapper,
                'options': options
            })
            return wrapper
        return decorator

    def init(self):
        '''
        默认初始化函数 (可重写)
        '''


class PluginInit:
    '''
    Plugin System Init
    '''
    c: ConfigModel
    d: Data
    app: flask.Flask

    def __init__(self, config: ConfigModel, data: Data, app: flask.Flask):
        self.c = config
        self.d = data
        self.app = app
        PluginInit.instance = self
        self._loaded_plugins = {}

    def load_plugins(self):
        '''
        加载插件
        '''
        for plugin_name in self.c.plugins_enabled:
            try:
                if not os.path.isfile(u.get_path(f'plugins/{plugin_name}/__init__.py')):
                    l.warning(f'[plugin] Invaild plugin {plugin_name}! it doesn\'t exist!')
                    break

                perf = u.perf_counter()
                module = importlib.import_module(f'plugins.{plugin_name}')

                # 查找 & 初始化插件实例
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, Plugin) and obj.name == plugin_name:
                        obj.init()
                        self._register_routes(obj)
                        self._loaded_plugins[plugin_name] = obj
                        l.debug(f'[plugin] init plugin {plugin_name} took {perf()}ms')
                        break
                else:
                    l.warning(f'[plugin] Invaild plugin {plugin_name}! it doesn\'t have a plugin instance')

            except Exception as e:
                l.warning(f'[plugin] Error when loading plugin {plugin_name}: {e}')

    def _register_routes(self, plugin: Plugin):
        '''
        注册插件所有路由

        :param plugin: 插件接口实例
        '''
        for route in plugin._routes:
            self.app.add_url_rule(
                route['rule'],
                endpoint=route['endpoint'],
                view_func=route['view_func'],
                **route['options']
            )
            l.debug(f"Registered Route: {route['rule']} -> {route['endpoint']}")

    def get_plugin(self, name: str) -> t.Optional[Plugin]:
        '''
        获取已加载插件实例
        '''
        return self._loaded_plugins.get(name)
