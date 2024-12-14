# coding: utf-8

import json
import os

import utils as u
from jsonc_parser.parser import JsoncParser as jsonp


def initJson():
    '''
    初始化配置 (从 example.jsonc 加载)
    '''
    try:
        jsonData = jsonp.parse_file('example.jsonc', encoding='utf-8')
        with open('config.json', 'w+', encoding='utf-8') as file:
            json.dump(jsonData, file, indent=4, ensure_ascii=False)
        u.info('Generated new config file (config.json), please edit and re-run this program.')
        u.info('Example: example.jsonc / Online: https://github.com/wyf9/sleepy/blob/main/example.jsonc')
    except:
        u.error('Create config.json failed')
        raise


class config:
    '''
    config 类, 负责配置调用
    可用 `.config['xxx']` 直接调取数据 (加载后)
    '''

    def __init__(self):
        if not os.path.exists('config.json'):
            u.warning('config.json not exist, creating')
            initJson()
        self.load()

    def load(self):
        '''
        加载配置
        '''
        with open('config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)

    # def save(self):
    #     '''
    #     保存配置
    #     '''
    #     with open('config.json', 'w+', encoding='utf-8') as file:
    #         json.dump(self.data, file, indent=4, ensure_ascii=False)

    # def dset(self, name, value):
    #     '''
    #     设置一个值
    #     '''
    #     self.data[name] = value
    #     with open('config.json', 'w+', encoding='utf-8') as file:
    #         json.dump(self.data, file, indent=4, ensure_ascii=False)

    def get(self, name):
        '''
        读取一个值
        '''
        try:
            gotdata = self.config[name]
        except:
            gotdata = None
        return gotdata
