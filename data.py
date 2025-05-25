# coding: utf-8

import os
import threading
from time import sleep
from datetime import datetime
from logging import getLogger

import pytz
import json
import json5

import utils as u
from config import Config

l = getLogger(__name__)


class Data:
    '''
    data 类，存储当前/设备状态
    可用 `.data['xxx']` 直接调取数据 (加载后) *(?)*

    :param config: 用户配置对象
    '''
    data: dict
    preload_data: dict
    data_check_interval: int = 60
    c: Config

    def __init__(self, config: Config):
        self.c = config

        with open(u.get_path('data.example.jsonc'), 'r', encoding='utf-8') as file:
            self.preload_data = json5.load(file)
        if os.path.exists(u.get_path('data/data.json')):
            try:
                self.load()
            except Exception as e:
                l.warning(f'Error when loading data: {e}, try re-create')
                os.remove(u.get_path('data/data.json'))
                self.data = self.preload_data
                self.save()
                self.load()
        else:
            l.info('Could not find data/data.json, creating.')
            try:
                self.data = self.preload_data
                self.save()
            except Exception as e:
                u.exception(f'Create data/data.json failed: {e}')

    # --- Storage functions

    def load(self, ret: bool = False, preload: dict = {}, error_count: int = 5) -> dict | None:
        '''
        加载状态

        :param ret: 是否返回加载后的 dict (为否则设置 self.data)
        :param preload: 将会将 data/data.json 的内容追加到此后
        '''
        if not preload:
            preload = self.preload_data
        attempts = error_count

        while attempts > 0:
            try:
                if not os.path.exists(u.get_path('data/data.json')):
                    l.warning('data/data.json not exist, try re-create')
                    self.data = self.preload_data
                    self.save()
                with open(u.get_path('data/data.json'), 'r', encoding='utf-8') as file:
                    Data = json.load(file)
                    DATA: dict = {**preload, **Data}
                    if ret:
                        return DATA
                    else:
                        self.data = DATA
                break  # 成功加载数据后跳出循环
            except Exception as e:
                attempts -= 1
                if attempts > 0:
                    l.warning(f'Load data error: {e}, retrying ({attempts} attempts left)')
                else:
                    l.error(f'Load data error: {e}, reached max retry count!')
                    raise

    def save(self):
        '''
        保存配置
        '''
        try:
            with open(u.get_path('data/data.json'), 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            l.error(f'Failed to save data/data.json: {e}')

    # --- Metrics

    def metrics_init(self):
        try:
            self.data['metrics']
        except KeyError:
            l.debug('[metrics] Metrics data init')
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
        now = datetime.now(pytz.timezone(self.c.main.timezone))
        '''
        if json_only:
            # 仅用于调试
            return {
                'time': f'{now}',
                'timezone': c.main.timezone,
                'today_is': self.data['metrics']['today_is'],
                'month_is': self.data['metrics']['month_is'],
                'year_is': self.data['metrics']['year_is'],
                'today': self.data['metrics']['today'],
                'month': self.data['metrics']['month'],
                'year': self.data['metrics']['year'],
                'total': self.data['metrics']['total']
            }
        else:
        '''
        return u.format_dict({
            'time': f'{now}',
            'timezone': self.c.main.timezone,
            'today_is': self.data['metrics']['today_is'],
            'month_is': self.data['metrics']['month_is'],
            'year_is': self.data['metrics']['year_is'],
            'today': self.data['metrics']['today'],
            'month': self.data['metrics']['month'],
            'year': self.data['metrics']['year'],
            'total': self.data['metrics']['total']
        })

    def check_metrics_time(self) -> None:
        '''
        跨 日 / 月 / 年 检测
        '''
        if not self.c.metrics.enabled:
            return

        # get time now
        now = datetime.now(pytz.timezone(self.c.main.timezone))
        year_is = str(now.year)
        month_is = f'{now.year}-{now.month}'
        today_is = f'{now.year}-{now.month}-{now.day}'

        # - check time
        if self.data['metrics']['today_is'] != today_is:
            l.debug(f'[metrics] today_is changed: {self.data["metrics"]["today_is"]} -> {today_is}')
            self.data['metrics']['today_is'] = today_is
            self.data['metrics']['today'] = {}
        # this month
        if self.data['metrics']['month_is'] != month_is:
            l.debug(f'[metrics] month_is changed: {self.data["metrics"]["month_is"]} -> {month_is}')
            self.data['metrics']['month_is'] = month_is
            self.data['metrics']['month'] = {}
        # this year
        if self.data['metrics']['year_is'] != year_is:
            l.debug(f'[metrics] year_is changed: {self.data["metrics"]["year_is"]} -> {year_is}')
            self.data['metrics']['year_is'] = year_is
            self.data['metrics']['year'] = {}

    def record_metrics(self, path: str | None = None) -> None:
        '''
        记录调用

        :param path: 访问的路径
        '''

        # check metrics list
        if not path in self.c.metrics.allow_list:
            return

        self.check_metrics_time()

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

    def check_device_status(self):
        '''
        按情况自动切换状态
        '''
        device_status: dict = self.data.get('device_status', {})
        current_status: int = self.data.get('status', 0)  # 获取当前 status，默认为 0
        auto_switch_enabled: bool = False  # c.util.auto_switch_status

        # 检查是否启用自动切换功能，并且当前 status 为 0 或 1
        last_status = self.data['status']
        if auto_switch_enabled:
            if current_status in [0, 1]:
                any_using = any(device.get('using', False) for device in device_status.values())
                if any_using:
                    self.data['status'] = 0
                else:
                    self.data['status'] = 1
                if last_status != self.data['status']:
                    l.debug(f'[check_device_status] 已自动切换状态 ({last_status} -> {self.data["status"]}).')
                else:
                    l.debug(f'[check_device_status] 当前状态已为 {current_status}, 无需切换.')
            else:
                l.debug(f'[check_device_status] 当前状态为 {current_status}, 不适用自动切换.')

    def timer_check(self):
        '''
        定时检查更改并自动保存
        * 根据 `data_check_interval` 参数调整 sleep() 的秒数
        * 需要使用 threading 启动新线程运行
        '''
        l.info(f'[timer_check] started, interval: {self.data_check_interval} seconds.')
        while True:
            sleep(self.data_check_interval)
            try:
                self.check_metrics_time()  # 检测是否跨日
                self.check_device_status()  # 检测设备状态并更新 status
                file_data = self.load(ret=True)
                if file_data == self.data:
                    l.debug('[timer_check] data not changed, skip saving.')
                else:
                    self.save()
                    l.debug('[timer_check] data changed, saved to disk.')
            except Exception as e:
                l.warning(f'[timer_check] saving error: {e}, retrying.')

    # --- check device heartbeat
    # TODO
