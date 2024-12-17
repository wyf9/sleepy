# coding: utf-8

import json
import os
import threading
from time import sleep

import utils as u


def initJson():
    '''
    初始化 (创建 data.json 文件)
    '''
    try:
        jsonData = {  # 初始 data.json 数据
            'status': 0,
            'device_status': {},
            'last_updated': '1970-01-01 08:00:00'
        }
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(jsonData, file, indent=4, ensure_ascii=False)
    except:
        u.error('Create data.json failed')
        raise


class data:
    '''
    data 类，存储持久化状态
    可用 `.data['xxx']` 直接调取数据 (加载后) *(?)*
    '''

    def __init__(self):
        if not os.path.exists('data.json'):
            u.info('Could not find data.json, creating.')
            initJson()
        try:
            self.load()
        except Exception as e:
            u.warning(f'Error when loading data: {e}, try re-create')
            os.remove('data.json')
            initJson()
            self.load()
        self.timer_thread = threading.Thread(target=self.timer_check)
        self.timer_thread.start()

    def load(self, ret: bool = False) -> None | dict:
        '''
        加载状态

        :param ret: 是否返回加载后的 dict (为否则设置 self.data)
        '''
        with open('data.json', 'r', encoding='utf-8') as file:
            Data = json.load(file)
            if ret:
                return Data
            else:
                self.data = Data

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

    def dget(self, name):
        '''
        读取一个值
        '''
        gotdata = self.data[name]
        return gotdata

    def timer_check(self):
        '''
        定时检查更改并自动保存
        * 默认 3 分钟 (3 * 60s)
        * 需要使用 threading 启动新线程运行
        '''
        while True:
            sleep(5*60)
            file_data = self.load(ret=True)
            if file_data != self.data:
                u.info('Detected data change, saving.')
                self.save()
