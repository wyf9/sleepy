# coding: utf-8

import os
import threading
from time import sleep, time
from datetime import datetime
from logging import getLogger
import json

import pytz
from werkzeug.security import safe_join
from pydantic import ValidationError
from flask import Flask

import utils as u
from models import DataModel, ConfigModel

l = getLogger(__name__)


class Data:
    '''
    data 类，存储当前/设备状态 <br/>
    可用 `data.data.xxx` 调取数据 (加载后)

    :param config: 用户配置对象
    '''
    data: DataModel
    _cache: dict[str, tuple[float, str]] = {}
    _data_check_interval: int = 60
    _plugins_enabled: list = []
    _c: ConfigModel

    def __init__(self, config: ConfigModel):
        perf = u.perf_counter()
        # --- init
        self._c = config

        if os.path.exists(u.get_path('data/data.json')):
            try:
                self.load()
            except Exception as e:
                l.warning(f'Error when loading data: {e}, try re-create')
                os.remove(u.get_path('data/data.json'))
                self.data = DataModel()
                self.save()
        else:
            l.info('Could not find data/data.json, creating.')
            try:
                self.data = DataModel()
                self.save()
            except Exception as e:
                raise u.SleepyException(f'Create data/data.json failed: {e}')
        # --- load
        self.load()
        l.debug(f'[data] init took {perf()}ms')

    # --- Storage functions

    def load(self, ret: bool = False, error_count: int = 5) -> DataModel | None:
        '''
        加载状态

        :param ret: 是否直接返回加载后的 data (为否则设置 self.data 为加载后数据)
        :param preload: 将会将 data/data.json 的内容追加到此后
        '''

        while error_count > 0:
            try:
                if not os.path.exists(u.get_path('data/data.json')):
                    l.warning('data/data.json not exist, creating a new one')
                    self.data = DataModel()
                    self.save()
                with open(u.get_path('data/data.json'), 'r', encoding='utf-8') as file:
                    data_file_loaded = json.load(file)
                    data_model = DataModel(**data_file_loaded)
                    if ret:
                        return data_model
                    else:
                        self.data = data_model
                break  # 成功加载数据后跳出循环
            except ValidationError as e:
                raise
            except Exception as e:
                error_count -= 1
                if error_count > 0:
                    l.warning(f'Load data error: {e}, retrying ({error_count} attempts left)')
                else:
                    l.error(f'Load data error: {e}, reached max retry count!')
                    raise

    def save(self):
        '''
        保存配置
        '''
        try:
            for i in self._plugins_enabled:
                self.data.plugin[i.name] = i.data
            with open(u.get_path('data/data.json'), 'w', encoding='utf-8') as file:
                json.dump(self.data.model_dump(), file, indent=4, ensure_ascii=False)
        except Exception as e:
            l.error(f'Failed to save data/data.json: {e}')

    # --- Metrics

    def get_metrics_data(self):
        now = datetime.now(pytz.timezone(self._c.main.timezone))
        return {
            'time': f'{now}',
            'timezone': self._c.main.timezone,
            'today_is': self.data.metrics.today_is,
            'month_is': self.data.metrics.month_is,
            'year_is': self.data.metrics.year_is,
            'today': self.data.metrics.today,
            'month': self.data.metrics.month,
            'year': self.data.metrics.year,
            'total': self.data.metrics.total
        }

    def record_metrics(self, path: str | None = None) -> None:
        '''
        记录调用

        :param path: 访问的路径
        '''

        # check metrics list
        if not path in self._c.metrics.allow_list:
            return

        self.check_metrics_time()

        # - record num
        self.data.metrics.today[path] = self.data.metrics.today.get(path, 0) + 1
        self.data.metrics.month[path] = self.data.metrics.month.get(path, 0) + 1
        self.data.metrics.year[path] = self.data.metrics.year.get(path, 0) + 1
        self.data.metrics.total[path] = self.data.metrics.total.get(path, 0) + 1

    # --- Timer check
    # - check metrics time
    # - check device status
    # - check cache expire
    # - auto save data

    def check_metrics_time(self) -> None:
        '''
        跨 日 / 月 / 年 检测
        '''
        if not self._c.metrics.enabled:
            return

        # get time now
        now = datetime.now(pytz.timezone(self._c.main.timezone))
        year_is = str(now.year)
        month_is = f'{now.year}-{now.month}'
        today_is = f'{now.year}-{now.month}-{now.day}'

        # - check time
        if self.data.metrics.today_is != today_is:
            l.debug(f'[metrics] today_is changed: {self.data.metrics.today_is} -> {today_is}')
            self.data.metrics.today_is = today_is
            self.data.metrics.today = {}
        # this month
        if self.data.metrics.month_is != month_is:
            l.debug(f'[metrics] month_is changed: {self.data.metrics.month_is} -> {month_is}')
            self.data.metrics.month_is = month_is
            self.data.metrics.month = {}
        # this year
        if self.data.metrics.year_is != year_is:
            l.debug(f'[metrics] year_is changed: {self.data.metrics.year_is} -> {year_is}')
            self.data.metrics.year_is = year_is
            self.data.metrics.year = {}

    def check_device_status(self):
        '''
        按情况自动切换状态
        '''
        device_status = self.data.device_status
        current_status = self.data.status
        auto_switch_enabled: bool = False  # c.util.auto_switch_status - wait for plugin

        # 检查是否启用自动切换功能，并且当前 status 为 0 或 1
        last_status = self.data.status
        if auto_switch_enabled:
            if current_status in [0, 1]:
                any_using = any(device.using for device in device_status.values())
                if any_using:
                    self.data.status = 0
                else:
                    self.data.status = 1
                if last_status != self.data.status:
                    l.debug(f'[check_device_status] switched status ({last_status} -> {self.data.status}).')
                else:
                    l.debug(f'[check_device_status] current status is {current_status} already.')
            else:
                l.debug(f'[check_device_status] curent status: {current_status}, can\'t switch automatically.')

    def clean_cache(self):
        '''
        清理缓存中的过期项
        '''
        if self._c.main.debug:
            # 不用检查了, 直接返回
            return
        now = time()
        for i in list(self._cache.keys()):
            if now - self._cache[i][0] > self._c.main.cache_age:
                del self._cache[i]

    def _auto_save(self):
        try:

            file_data = self.load(ret=True)
            if file_data != self.data:
                self.save()
                self.load()
                l.info('[auto_save] data changed, saved to disk.')
        except Exception as e:
            l.warning(f'[auto_save] saving error: {e}')

    def _data_check_timer(self):
        '''
        定时检查更改并自动保存
        * 根据 `data_check_interval` 参数调整 sleep() 的秒数
        * 需要使用 threading 启动新线程运行
        '''
        l.info(f'[timer_check] started, interval: {self._data_check_interval} seconds.')
        while True:
            t = u.perf_counter()
            l.debug('[timer_check] running...')
            try:
                self.check_metrics_time()
                self.check_device_status()
                self.clean_cache()
                self._auto_save()
            except Exception as e:
                l.warning(f'[timer_check] error: {e}')
            l.debug(f'[timer_check] finished in {t()}ms.')
            sleep(self._data_check_interval)

    def start_timer_check(self, data_check_interval: int = 60, plugins_enabled: list = []):
        '''
        使用 threading 启动下面的 `timer_check()`

        :param data_check_interval: 检查间隔 *(秒)*
        '''
        self._data_check_interval = data_check_interval
        self._plugins_enabled = plugins_enabled
        self.timer_thread = threading.Thread(target=self._data_check_timer, daemon=True)
        self.timer_thread.start()

    # --- simple cache system

    def get_cached(self, filename: str) -> str | None:
        '''
        加载文本文件 (经过缓存)

        :param filename: 文件名
        :return str: (加载成功) 文件内容
        :return None: (加载失败) 空
        '''
        filepath = safe_join(u.current_dir(), filename)
        if not filepath:
            # unsafe -> none
            return None
        try:
            if self._c.main.debug:
                # debug -> load directly
                with open(filepath, 'r', encoding='utf-8') as f:
                    ret = f.read()
                    f.close()
                return ret
            else:
                # check cache & expire
                now = time()
                cached = self._cache.get(filename)
                if cached and now - cached[0] < self._c.main.cache_age:
                    # has cache, and not expired
                    return cached[1]
                else:
                    # no cache, or expired
                    with open(filepath, 'r', encoding='utf-8') as f:
                        ret = f.read()
                        f.close()
                    self._cache[filename] = (now, ret)
                    return ret
        except FileNotFoundError or IsADirectoryError:
            # not found / isn't file -> none
            return None
