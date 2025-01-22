# coding: utf-8

import json
import os

import utils as u
from jsonc_parser.parser import JsoncParser


class config:
    '''
    config 类, 负责配置调用
    可用 `.config['xxx']` 直接调取数据 (加载后)
    '''
    config: dict

    def __init__(self):
        jsonData = JsoncParser.parse_file('config.example.jsonc', encoding='utf-8')
        if not os.path.exists('config.json'):
            u.warning('config.json not exist, creating')
            try:
                with open('config.json', 'w+', encoding='utf-8') as file:
                    json.dump(jsonData, file, indent=4, ensure_ascii=False)
                u.exception('Generated new config file (config.json), please edit it and re-run this program.')
            except Exception as e:
                u.error(f'Create config.json failed: {e}')
                raise
        self.load()
        if self.config['version'] != jsonData['version']:
            u.exception(f'Config fotmat updated ({self.config["version"]} -> {jsonData["version"]}), please change your config.json\nExample see: config.example.json')

    def load(self):
        '''
        加载配置
        '''
        with open('config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)

    def get(self, name):
        '''
        读取一个值
        '''
        try:
            gotdata = self.config[name]
        except:
            gotdata = None
        return gotdata
