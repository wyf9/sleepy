# coding: utf-8

import json
import os
import threading
from time import sleep
from datetime import datetime

import utils as u


def initJson():
    '''
    初始化 (创建 data.json 文件)
    '''
    try:
        jsonData = {  # 初始 data.json 数据
            'status': 0,
            'device_status': {},
            'private_mode': False,
            'last_updated': '1970-01-01 08:00:00'
        }
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(jsonData, file, indent=4, ensure_ascii=False)
    except:
        u.error('Create data.json failed')
        raise


class data:
    '''
    data 类，存储当前/设备状态
    可用 `.data['xxx']` 直接调取数据 (加载后) *(?)*
    '''
    data: dict
    data_check_interval: int

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

    # --- Storage functions

    def load(self, ret: bool = False) -> dict:
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

    def dget(self, name, default=None):
        '''
        读取一个值
        '''
        try:
            gotdata = self.data[name]
        except KeyError:
            gotdata = default
        return gotdata

    # --- Metrics

    def metrics_init(self):
        try:
            metrics = self.data['metrics']
        except KeyError:
            u.info('Metrics data init')
            self.data['metrics'] = {
                'today_is': '',
                'month_is': '',
                'year_is': '',
                'today': {},
                'month': {},
                'year': {},
                'total': {}
            }
            self.record_metrics()

    def get_metrics_resp(self):
        return u.format_dict({
            'today_is': self.data['metrics']['today_is'],
            'month_is': self.data['metrics']['month_is'],
            'year_is': self.data['metrics']['year_is'],
            'today': self.data['metrics']['today'],
            'month': self.data['metrics']['month'],
            'year': self.data['metrics']['year'],
            'total': self.data['metrics']['total']
        })

    def record_metrics(self, path: str = None):
        '''
        记录调用

        :param path: 访问的路径
        '''
        # - get time now
        now = datetime.now()
        year_is = str(now.year)
        month_is = f'{now.year}-{now.month}'
        today_is = f'{now.year}-{now.month}-{now.day}'
        # - check time
        # today
        if self.data['metrics']['today_is'] != today_is:
            self.data['metrics']['today_is'] = today_is
            self.data['metrics']['today'] = {}
        # this month
        if self.data['metrics']['month_is'] != month_is:
            self.data['metrics']['month_is'] = month_is
            self.data['metrics']['month'] = {}
        # this year
        if self.data['metrics']['year_is'] != year_is:
            self.data['metrics']['year_is'] = year_is
            self.data['metrics']['year'] = {}
        # - record num
        if not path:
            return 0
        # today
        try:
            self.data['metrics']['today'][path] += 1
        except KeyError:
            self.data['metrics']['today'][path] = 1
        # this month
        try:
            self.data['metrics']['month'][path] += 1
        except KeyError:
            self.data['metrics']['month'][path] = 1
        # this year
        try:
            self.data['metrics']['year'][path] += 1
        except KeyError:
            self.data['metrics']['year'][path] = 1
        # total
        try:
            self.data['metrics']['total'][path] += 1
        except KeyError:
            self.data['metrics']['total'][path] = 1

    # --- Timer check - save data

    def start_timer_check(self, data_check_interval: int = 60):
        '''
        使用 threading 启动下面的 `timer_check()`

        :param data_check_interval: 检查间隔 *(秒)*
        '''
        self.data_check_interval = data_check_interval
        self.timer_thread = threading.Thread(target=self.timer_check, daemon=True)
        self.timer_thread.start()

    def timer_check(self):
        '''
        定时检查更改并自动保存
        * 根据 `data_check_interval` 参数调整 sleep() 的秒数
        * 需要使用 threading 启动新线程运行
        '''
        while True:
            sleep(self.data_check_interval)
            file_data = self.load(ret=True)
            if file_data != self.data:
                self.save()

    # --- check device heartbeat
    # TODO
