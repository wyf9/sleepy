import os
import importlib
import typing as t
from logging import getLogger
from functools import wraps
from contextlib import contextmanager
from uuid import uuid4 as uuid

import flask

from models import ConfigModel
from data import Data
import utils as u

l = getLogger(__name__)

# region plugin-api


class Plugin:
    '''
    Sleepy 插件接口
    '''
    name: str
    '''插件名称'''
    config: t.Any
    '''插件配置 (如传入 Model 则为对应 Model 实例, 否则为字典)'''
    _registry: dict[str, t.Any] = {}
    '''存放插件实例'''
    _routes = []
    '''插件注册的路由'''

    def __init__(self, name: str, config: t.Any = {}, data: dict = {}):
        '''
        初始化插件

        :param name: 插件名称 (通常为 `__name__`)
        :param config: *(Model / dict)* 插件默认配置 (可选)
        :param data: 插件默认数据 (可选)
        '''
        # 初始化 & 注册插件
        self.name = name.split('.')[-1]
        Plugin._registry[self.name] = self

        # 加载配置
        if not config:
            # 1. None -> raw
            self.config = PluginInit.instance.c.plugin.get(self.name, {})
        elif isinstance(config, dict):
            # 2. dict -> default + raw -> dict
            config_dict = u.deep_merge_dict(config, PluginInit.instance.c.plugin.get(self.name, {}))
            self.config = config_dict
        else:
            # 3. model -> default model + raw -> model
            config_dict = PluginInit.instance.c.plugin.get(self.name, {})
            self.config = config.model_validate(config_dict)

        self.data = u.deep_merge_dict(data, self.data)

    # region plugin-api-meta

    @property
    def data(self):
        '''
        插件数据存储
        '''
        return PluginInit.instance.d.get_plugin_data(self.name)

    @data.setter
    def data(self, value: dict):
        PluginInit.instance.d.set_plugin_data(id=self.name, data=value)

    @contextmanager
    def data_context(self):
        '''
        数据上下文 (在退出时自动保存)

        ```
        with plugin.data_context() as data:
            data['calls'] = data.get('calls', 0) + 1
        ```
        '''
        data = self.data
        yield data
        if data != self.data:
            self.data = data

    def set_data(self, key, value):
        '''
        设置数据值
        '''
        data = self.data
        data[key] = value
        self.data = data

    def get_data(self, key, default=None):
        '''
        获取数据值
        '''
        return self.data.get(key, default)

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
    def _app(self) -> flask.Flask:
        '''
        直接访问 flask.Flask 实例 (不建议使用)
        '''
        return PluginInit.instance.app

    # endregion plugin-api-meta

    # region plugin-api-route

    def add_route(self, func: t.Callable, rule: str, _wrapper: t.Callable | None = None, **options: t.Any):
        '''
        注册插件路由 **(访问: `/plugin/<name>/<rule>`)**

        :param func: 处理路由的视图函数
        :param rule: 路由规则 (路径)
        :param options: 其他传递给 Flask 的参数 *(`_wrapper` 除外)*
        '''
        endpoint = options.pop('endpoint', func.__name__)
        full_rule = f'/plugin/{self.name}{"" if rule.startswith("/") else "/"}{rule}'

        self._routes.append({
            'rule': full_rule,
            'endpoint': f"plugin.{self.name}.{endpoint}",
            'view_func': _wrapper or func,
            'options': options
        })

    def route(self, rule: str, **options: t.Any):
        '''
        **[装饰器]** 注册插件路由 **(访问: `/plugin/<name>/<rule>`)**

        :param rule: 路由规则 (路径)
        :param options: 其他传递给 Flask 的参数
        ```
        @plugin.route('/endpoint')
        def handler():
            return 'Hello from plugin!'
        ```
        '''
        def decorator(f):

            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            self.add_route(
                func=f,
                rule=rule,
                _wrapper=wrapper,
                **options
            )
            return wrapper
        return decorator

    def add_global_route(self, func: t.Callable, rule: str, _wrapper: t.Callable | None = None, **options: t.Any):
        '''
        注册全局插件路由 **(访问: `/<rule>`)**

        :param func: 处理路由的视图函数
        :param rule: 路由规则 (路径)
        :param options: 其他传递给 Flask 的参数
        '''
        endpoint = options.pop('endpoint', func.__name__)
        full_rule = f'{"" if rule.startswith("/") else "/"}{rule}'

        self._routes.append({
            'rule': full_rule,
            'endpoint': f"plugin_global.{self.name}.{endpoint}",
            'view_func': _wrapper or func,
            'options': options
        })

    def global_route(self, rule: str, **options: t.Any):
        '''
        [装饰器] 注册全局插件路由 **(访问: `/<rule>`)**

        :param rule: 路由规则 (路径)
        :param options: 其他传递给 Flask 的参数
        ```
        @plugin.route('/global-endpoint')
        def handler():
            return "Hello from plugin"
        ```
        '''
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            self.add_global_route(
                func=f,
                rule=rule,
                _wrapper=wrapper,
                **options
            )
            return wrapper
        return decorator

    # endregion plugin-api-route

    # region plugin-api-cards

    def add_index_card(self, card_id: str, content: str | t.Callable):
        '''
        注册 index.html 卡片 (如已有则追加到末尾)

        :param card_id: 用于区分不同卡片
        :param content: 卡片 HTML 内容
        '''
        stored = PluginInit.instance._index_cards.get(card_id, [])
        stored.append(content)
        PluginInit.instance._index_cards[card_id] = stored

    def index_card(self, card_id: str):
        '''
        [装饰器] 注册 index.html 卡片 (如已有则追加到末尾)

        :param card_id: 用于区分不同卡片
        '''
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            self.add_index_card(
                card_id=card_id,
                content=wrapper
            )
            return wrapper
        return decorator

    # endregion plugin-api-cards

    # region plugin-api-injects

    # endregion plugin-api-injects

    def init(self):
        '''
        初始化时将执行此函数 (可覆盖)
        '''

# endregion plugin-api

# region plugin-init


class PluginInit:
    '''
    Plugin System Init
    '''
    c: ConfigModel
    d: Data
    app: flask.Flask
    plugins_loaded: list[Plugin] = []
    '''已加载的插件'''
    _routes = []
    '''插件注册的路由'''
    _index_cards: dict[str, list[str | t.Callable]] = {}
    '''主页卡片'''
    _index_injects = []
    '''主页注入'''
    _webui_cards = []
    '''管理面板卡片'''
    _webui_injects = []
    '''管理面板注入'''
    _global_injects = []
    '''前端全局注入'''

    def __init__(self, config: ConfigModel, data: Data, app: flask.Flask):
        self.c = config
        self.d = data
        self.app = app
        PluginInit.instance = self

    def load_plugins(self):
        '''
        加载插件
        '''
        # 加载系统自带的卡片
        self._index_cards['main'] = []

        for plugin_name in self.c.plugins_enabled:
            # 加载单个插件
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
                        self.plugins_loaded.append(obj)
                        l.debug(f'[plugin] init plugin {plugin_name} took {perf()}ms')
                        break
                else:
                    l.warning(f'[plugin] Invaild plugin {plugin_name}! it doesn\'t have a plugin instance!')

            except Exception as e:
                l.warning(f'[plugin] Error when loading plugin {plugin_name}: {e}')
                if self.c.main.debug:
                    raise

        loaded_count = len(self.plugins_loaded)
        loaded_names = ", ".join([n.name for n in self.plugins_loaded])
        l.info(f'{loaded_count} plugin{"s" if loaded_count > 1 else ""} enabled: {loaded_names}' if loaded_count > 0 else f'No plugins enabled.')
        l.debug(f'index cards: {self._index_cards}')

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
            l.debug(f'Registered Route: {route["rule"]} -> {route["endpoint"]}')

# endregion plugin-init
