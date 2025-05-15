# coding: utf-8

import os
import importlib
import yaml

from config import Config
from utils import Utils
from data import Data
from _utils import get_path, SleepyException


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

    def __init__(self, config: Config, utils: Utils, data: Data):
        '''
        初始化插件功能，包括验证插件可用性

        :param config: 用户配置 (`config.Config`)
        :param utils: 实用功能 (`utils.Utils`)
        :param data: 用户数据 (`data.Data`)
        '''
        self.c = config
        self.u = utils
        self.d = data
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
            if is_backend:
                plugin_backend = importlib.import_module(f'plugin.{i}')
            else:
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
        self.u.info(f'plugins enabled: {", ".join(self.c.plugin_enabled)}')
