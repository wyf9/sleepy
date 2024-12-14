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
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(jsonData, file, indent=4, ensure_ascii=False)
        u.info('Generated new config file (data.json), please edit and re-run this program.')
        u.info('Example: example.jsonc / Online: https://github.com/wyf9/sleepy/blob/main/example.jsonc')
    except:
        u.error('Create data.json failed')
        raise


class data:
    '''
    data 类, 负责配置存储/调用
    可用 `.data['xxx']` 直接调取数据 (加载后)
    '''
    def __init__(self):
        if not os.path.exists('data.json'):
            u.warning('data.json not exist, creating')
            initJson()
        with open('data.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)

    def load(self):
        '''
        加载配置
        '''
        with open('data.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)

    def save(self):
        '''
        保存配置
        '''
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def dset(self, name, value):
        '''
        设置一个值
        '''
        self.data[name] = value
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def dget(self, name):
        '''
        读取一个值
        '''
        with open('data.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)
            try:
                gotdata = self.data[name]
            except:
                gotdata = None
            return gotdata
