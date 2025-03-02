# coding: utf-8

import os
import json5
import shutil
import utils as u

class config:
    '''
    config 类, 负责配置调用
    可用 `.config['xxx']` 直接调取数据 (加载后)
    '''
    config: dict

    def __init__(self):
        # jsonData = JsoncParser.parse_file('config.example.jsonc', encoding='utf-8')
        jsonData= json5.load(open('config.example.jsonc', encoding='utf-8'))
        if not os.path.exists('config.jsonc'):
            u.warning('config.jsonc not exist, creating')
            try:
                shutil.copy('config.example.jsonc', 'config.jsonc')
                u.exception('Generated new config file (config.jsonc), please edit it and re-run this program.')
            except Exception as e:
                u.error(f'Create config.jsonc failed: {e}')
                raise
        self.load()
        if self.config['version'] != jsonData['version']:
            u.exception(f'Config fotmat updated ({self.config["version"]} -> {jsonData["version"]}), please change your config.jsonc\nSee: config.example.json and doc/config_update.md')

    def load(self):
        '''
        加载配置
        '''
        try:
            self.config = json5.load(open('config.jsonc', encoding='utf-8'))
        except Exception as e:
            u.error(f'Error loading config.jsonc: {e}')
            raise

    def get(self, name):
        '''
        读取一个值
        '''
        try:
            gotdata = self.config[name]
        except:
            gotdata = None
        return gotdata
