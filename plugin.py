# coding: utf-8

import os
import importlib
from logging import getLogger
import typing as t
from functools import wraps

import flask

from config import Config
from data import Data
import utils as u

l = getLogger(__name__)

# --- Plugin Class


class Plugin:
    '''
    Sleepy 插件接口
    '''
    name: str
    example_config: dict
    user_config: Config
    data: Data

    def __init__(self, name: str, user_config: Config, data: Data):
        '''
        初始化 PluginClass
        '''
        self.example_config = getattr(self, 'example_config') or {}
        self.name = name.split('.')[-1]
        self.user_config = user_config
        self.data = data

    def get_config(self, *key: str):
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
            raise u.SleepyException(f'Plugin config {".".join(key)} not found in plugin/{self.name}/plugin.yaml!')

    @property
    def config(self):
        '''
        获取插件的配置项字典
        '''
        return {**self.example_config, **self.user_config.plugin.get(self.name, {})}

# --- Globals


_plugins: list[Plugin] = []  # 已启用的插件类 (PluginClass) 列表 [plugin: PluginClass]
_index_cards: list[str] = []  # 前端 (index.html) 卡片列表 [content: str]
_webui_cards: list[str] = []  # 管理面板 (/webui/panel) 卡片列表 [content: str]
_routes: dict[str, tuple[str, tuple, dict, t.Callable]] = {}  # 插件路由列表 {rule: [str: by_plugin, *args, **kwargs, Callable]}
_event_handlers: dict[str, list[t.Callable]] = []  # 事件处理器列表 [event: str, Callable]
_current_plugin: t.Optional[str] = None
_plugin_instances: dict[str, Plugin] = {}

# --- Functions


def _get_plugin_name(func: t.Callable):
    '''
    (在修饰器中) 通过函数模块名获取插件名称
    '''
    return func.__module__.split('.')[-1]


def route(rule: str, *args, **kwargs):
    '''
    (装饰器) 注册插件路由 (带插件前缀)
    '''
    def decorator(func):
        # 使用全局变量 _current_plugin
        plugin_name = globals().get('_current_plugin') or _get_plugin_name(func)
        _rule = rule if rule.startswith('/') else f'/{rule}'
        full_rule = f'/{plugin_name}{_rule}'

        # 存储路由信息
        _routes[full_rule] = (plugin_name, args, kwargs, func)

        @wraps(func)
        def wrapper(*args_, **kwargs_):
            return func(*args_, **kwargs_)
        return wrapper
    return decorator


def trigger_event(event: str, *args, **kwargs):
    '''
    触发事件

    :param event: 事件名称
    '''


def require_secret(view_func):
    '''
    (装饰器) require_secret, 用于指定函数需要 secret 鉴权
    - ***请确保修饰器紧跟函数定义，如:***
    ```
    @app.route('/set')
    @require_secret
    def set_normal(): ...
    ```
    '''
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # 1. body
        # -> {"secret": "my-secret"}
        body: dict = flask.request.get_json(silent=True) or {}
        if body and body.get('secret') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Body')
            return view_func(*args, **kwargs)

        # 2. param
        # -> ?secret=my-secret
        elif flask.request.args.get('secret') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Param')
            return view_func(*args, **kwargs)

        # 3. header (Sleepy-Secret)
        # -> Sleepy-Secret: my-secret
        elif flask.request.headers.get('Sleepy-Secret') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Header (Sleepy-Secret)')
            return view_func(*args, **kwargs)

        # 4. header (Authorization)
        # -> Authorization: Bearer my-secret
        elif flask.request.headers.get('Authorization', '')[7:] == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Header (Authorization)')
            return view_func(*args, **kwargs)

        # 5. cookie (sleepy-token)
        # -> Cookie: sleepy-token=my-secret
        elif flask.request.cookies.get('sleepy-token') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Cookie (sleepy-token)')
            return view_func(*args, **kwargs)

        # -1. no any secret
        else:
            l.debug('[Auth] Verify secret Failed')
            return {
                'success': False,
                'code': 'not authorized',
                'message': 'wrong secret'
            }, 401
    return wrapped_view


# --- Plugin Init

def _register_routes(app: flask.Flask):
    '''
    注册路由
    '''
    for route, info in _routes.items():
        app.route(route, *info[1], **info[2])(info[3])
        l.debug(f'Registered route {route}' + f' by plugin {info[0]}' if info[0] else '')


class PluginInit:
    '''
    Plugin System for Sleepy
    '''
    c: Config
    d: Data
    app: flask.Flask

    def __init__(self, config: Config, data: Data, app: flask.Flask):
        '''
        初始化插件功能
        '''
        self.c = config
        self.d = data
        self.app = app

        # 加载插件
        for i in self.c.plugin_enabled:
            try:
                globals()['_current_plugin'] = i  # 当前插件名

                plugin_module = importlib.import_module(f'plugins.{i}')
                plugin_class = getattr(plugin_module, 'Plugin', None)
                if plugin_class and issubclass(plugin_class, Plugin):
                    instance = plugin_class(
                        name=i,
                        user_config=self.c,
                        data=self.d
                    )
                    _plugin_instances[i] = instance

                    # 执行 init (如存在)
                    if hasattr(instance, 'init'):
                        instance.init()

                # 重置插件名
                globals()['_current_plugin'] = None

            except Exception as e:
                l.error(f'Error loading plugin {i}: {e}')
                globals()['_current_plugin'] = None

        # 注册路由
        _register_routes(self.app)

