# coding: utf-8

import json
import utils as u


class setting:
    '''
    setting 类 \n
    加载指定 json 文件内容到 `self.content`
    '''
    config: dict

    def __init__(self, filename: str):
        self.load(filename)

    def load(self, filename: str):
        '''
        加载配置
        '''
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.content = json.load(file)
        except Exception as e:
            u.exception(f'[setting] Error loading {filename}: {e}')


status_list: list = setting('setting/status_list.json').content
metrics_list: list = setting('setting/metrics_list.json').content
