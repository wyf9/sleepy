# coding: utf-8

import os
import importlib
import yaml

from config import Config
from utils import Utils
from _utils import get_path, SleepyException


class PluginConfig:
    '''
    将传递给插件的配置
    '''
    name: str
    example_config: dict
    user_config: dict

    def __init__(self, name: str, example_config: dict, user_config: dict):
        '''
        初始化一项插件的配置
        :param namespace: 插件 id
        :param example: (插件的) 示例配置
        :param config: (插件的) 用户配置
        '''
        self.name = name
        self.example_config = example_config
        self.user_config = user_config
        print(f'plugin init name: {name}, example: {example_config}, config: {user_config}')

    def getkey(self, *key: str):
        '''
        通过键获取插件的配置项
        - 顺序: 用户配置 -> 插件 plugin.yaml
        '''
        # 1. from user config
        try:
            value = self.user_config
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
        '''
        return {**self.example_config, **self.user_config}


class Plugin:
    # [id, frontend, backend, config]
    plugins: list[tuple[str, str, object, PluginConfig]] = []

    def __init__(self, config: Config):
        '''
        初始化插件功能，包括验证插件可用性

        :param config: 用户配置
        '''
        self.c = config
        self.u = Utils(config=config)
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
            # 加载前端代码 (index.html)
            if plugin.get('frontend', False):
                with open(get_path(f'plugin/{i}/index.html'), 'r', encoding='utf-8') as ff:
                    plugin_frontend = ff.read()
                    ff.close()
            else:
                plugin_frontend = ''
            # 加载后端代码 (__init__.py)
            if plugin.get('backend', False):
                plugin_backend = importlib.import_module(f'plugin.{i}')
            else:
                plugin_backend = None
            # 加载配置
            plugin_config = PluginConfig(
                name=i,
                example_config=plugin.get('config', {}),
                user_config=self.c.plugin.get(i, {})
            )
            # 保存此项
            self.plugins.append((i, plugin_frontend, plugin_backend, plugin_config))
        self.u.debug(f'plugins enabled: {", ".join(self.c.plugin_enabled)}')
