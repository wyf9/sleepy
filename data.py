# coding: utf-8

import json
import os
import threading
from time import sleep
from datetime import datetime
import pytz

import utils as u
from jsonc_parser.parser import JsoncParser
import config as config_module


class data:
    '''
    data 类，存储当前/设备状态
    可用 `.data['xxx']` 直接调取数据 (加载后) *(?)*

    :param config: config class
    '''
    data: dict
    preload_data: dict
    data_check_interval: int = 60
    c: config_module.config

    def __init__(self, config: config_module.config):
        self.c = config
        self.preload_data = JsoncParser.parse_file('data.example.jsonc', encoding='utf-8')
        if os.path.exists('data.json'):
            try:
                self.load()
            except Exception as e:
                u.warning(f'Error when loading data: {e}, try re-create')
                os.remove('data.json')
                self.data = self.preload_data
                self.save()
                self.load()
        else:
            u.info('Could not find data.json, creating.')
            try:
                self.data = self.preload_data
                self.save()
            except:
                u.error('Create data.json failed')
                raise

    # --- Storage functions

    def load(self, ret: bool = False, preload: dict = {}, error_count: int = 5) -> dict:
        '''
        加载状态

        :param ret: 是否返回加载后的 dict (为否则设置 self.data)
        :param preload: 将会将 data.json 的内容追加到此后
        '''
        if preload == {}:
            preload = self.preload_data
        try:
            if not os.path.exists('data.json'):
                u.warning('data.json not exist, try re-create')
                self.data = self.preload_data
                self.save()
            with open('data.json', 'r', encoding='utf-8') as file:
                Data = json.load(file)
                DATA: dict = {**preload, **Data}
                if ret:
                    return DATA
                else:
                    self.data = DATA
        except Exception as e:
            if error_count > 0:
                u.warning(f'Load data error: {e}, retrying')
                self.load(error_count=error_count-1)
            else:
                u.error(f'Load data error: {e}, reached max retry count!')
                raise

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

    def get_metrics_resp(self, json_only: bool = False):
        now = datetime.now(pytz.timezone(self.c.config['timezone']))
        if json_only:
            # 仅用于调试
            return {
                'time': f'{now}',
                'timezone': self.c.config['timezone'],
                'today_is': self.data['metrics']['today_is'],
                'month_is': self.data['metrics']['month_is'],
                'year_is': self.data['metrics']['year_is'],
                'today': self.data['metrics']['today'],
                'month': self.data['metrics']['month'],
                'year': self.data['metrics']['year'],
                'total': self.data['metrics']['total']
            }
        else:
            return u.format_dict({
                'time': f'{now}',
                'timezone': self.c.config['timezone'],
                'today_is': self.data['metrics']['today_is'],
                'month_is': self.data['metrics']['month_is'],
                'year_is': self.data['metrics']['year_is'],
                'today': self.data['metrics']['today'],
                'month': self.data['metrics']['month'],
                'year': self.data['metrics']['year'],
                'total': self.data['metrics']['total']
            })

    def record_metrics(self, path: str = None) -> None:
        '''
        记录调用

        :param path: 访问的路径
        '''
        if not path:
            return

        # get time now
        now = datetime.now(pytz.timezone(self.c.config['timezone']))
        year_is = str(now.year)
        month_is = f'{now.year}-{now.month}'
        today_is = f'{now.year}-{now.month}-{now.day}'

        # 调试使用, 请勿取消注释!!!
        # year_is = '2025'
        # month_is = '2025-1'
        # today_is = '2025-1-18'
        # if now.minute > 31 and now.second > 40:
        #     print('ok')
        #     today_is = '2025-1-19'
        # else:
        #     print('no')

        # - check time
        if self.data['metrics']['today_is'] != today_is:
            u.info(f'[metrics] today_is changed: {self.data["metrics"]["today_is"]} -> {today_is}')
            self.data['metrics']['today_is'] = today_is
            self.data['metrics']['today'] = {}
        # this month
        if self.data['metrics']['month_is'] != month_is:
            u.info(f'[metrics] month_is changed: {self.data["metrics"]["month_is"]} -> {month_is}')
            self.data['metrics']['month_is'] = month_is
            self.data['metrics']['month'] = {}
        # this year
        if self.data['metrics']['year_is'] != year_is:
            u.info(f'[metrics] year_is changed: {self.data["metrics"]["year_is"]} -> {year_is}')
            self.data['metrics']['year_is'] = year_is
            self.data['metrics']['year'] = {}

        # - record num
        today = self.data['metrics'].setdefault('today', {})
        month = self.data['metrics'].setdefault('month', {})
        year = self.data['metrics'].setdefault('year', {})
        total = self.data['metrics'].setdefault('total', {})

        today[path] = today.get(path, 0) + 1
        month[path] = month.get(path, 0) + 1
        year[path] = year.get(path, 0) + 1
        total[path] = total.get(path, 0) + 1

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
        u.info(f'[timer_check] started, interval: {self.data_check_interval} seconds.')
        while True:
            sleep(self.data_check_interval)
            try:
                try:
                    file_data = self.load(ret=True)
                except Exception as e:
                    file_data = {}
                if file_data != self.data:
                    self.save()
            except Exception as e:
                u.warning(f'[timer_check] Error: {e}, retrying.')

    # --- check device heartbeat
    # TODO
