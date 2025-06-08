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


class PluginClass:
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
        self.name = name
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


class _PluginClassForLint:
    '''
    *只是为了代码自动补全*
    '''
    class Plugin(PluginClass):
        def init(self) -> None:
            pass


class Plugin:
    '''
    Plugin System for Sleepy
    '''
    c: Config
    d: Data
    app: flask.Flask
    _plugins: list[PluginClass] = []  # 已启用的插件类 (PluginClass) 列表
    _index_cards: list[str] = []  # 前端 (index.html) 卡片列表
    _webui_cards: list[str] = []  # 管理面板 (/webui/panel) 卡片列表
    _routes: dict[str, t.Callable] = []  # 插件路由列表
    _event_handlers: dict[str, list[t.Callable]] = []  # 事件处理器列表

    def __init__(self, config: Config, data: Data, app: flask.Flask):
        '''
        初始化插件功能
        '''
        self.c = config
        self.d = data
        self.app = app

        # 加载插件
        for i in self.c.plugin_enabled:
            # 检查是否存在
            if not os.path.isdir(u.get_path(f'plugin/{i}')) or os.path.isfile(u.get_path(f'plugin/{i}.py')):
                l.error(f'Error initing plugin {i}: Not exist')
                continue
            try:
                # 加载 class
                plugin_file: _PluginClassForLint = importlib.import_module(f'plugin.{i}')
                plugin_class: PluginClass = plugin_file.Plugin(
                    name=i,
                    user_config=self.c,
                    data=self.d
                )
                # 执行 init (如存在)
                if hasattr(plugin_class, 'init'):
                    plugin_class.init()
                self._plugins.append(plugin_class)
            except Exception as e:
                l.error(f'Error initing plugin {i}: {e}')
    
    def trigger_event(event, *args, **kwargs):
        pass


def require_secret(view_func):
    '''
    require_secret 修饰器, 用于指定函数需要 secret 鉴权
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
