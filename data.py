# coding: utf-8

import json
import os
import threading

# --- Add ---
import time
from datetime import datetime

# --- End Add ---
from time import sleep

import pytz

import env as env
import utils as u
from setting import metrics_list


class data:
    '''
    data 类，存储当前/设备状态
    可用 `.data['xxx']` 直接调取数据 (加载后) *(?)*
    '''
    data: dict
    preload_data: dict
    data_check_interval: int = 60

    def __init__(self):
        with open(u.get_path('data.template.json'), 'r', encoding='utf-8') as file:
            self.preload_data = json.load(file)
        if os.path.exists(u.get_path('data.json')):
            try:
                self.load()
            except Exception as e:
                u.warning(f'Error when loading data: {e}, try re-create')
                os.remove(u.get_path('data.json'))
                self.data = self.preload_data
                self.save()
                self.load()
        else:
            u.info('Could not find data.json, creating.')
            try:
                self.data = self.preload_data
                self.save()
            except Exception as e:
                u.exception(f'Create data.json failed: {e}')

    # --- Storage functions

    def load(self, ret: bool = False, preload: dict = {}, error_count: int = 5) -> dict:
        '''
        加载状态

        :param ret: 是否返回加载后的 dict (为否则设置 self.data)
        :param preload: 将会将 data.json 的内容追加到此后
        '''
        if not preload:
            preload = self.preload_data
        attempts = error_count

        while attempts > 0:
            try:
                if not os.path.exists(u.get_path('data.json')):
                    u.warning('data.json not exist, try re-create')
                    self.data = self.preload_data
                    self.save()
                with open(u.get_path('data.json'), 'r', encoding='utf-8') as file:
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
                    u.warning(f'Load data error: {e}, retrying ({attempts} attempts left)')
                else:
                    u.error(f'Load data error: {e}, reached max retry count!')
                    raise

    def save(self):
        '''
        保存配置
        '''
        try:
            with open(u.get_path('data.json'), 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            u.error(f'Failed to save data.json: {e}')

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
            self.data['metrics']
        except KeyError:
            u.debug('[metrics] Metrics data init')
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
        now = datetime.now(pytz.timezone(env.main.timezone))
        '''
        if json_only:
            # 仅用于调试
            return {
                'time': f'{now}',
                'timezone': env.main.timezone,
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
            'timezone': env.main.timezone,
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
        if not env.util.metrics:
            return

        # get time now
        now = datetime.now(pytz.timezone(env.main.timezone))
        year_is = str(now.year)
        month_is = f'{now.year}-{now.month}'
        today_is = f'{now.year}-{now.month}-{now.day}'

        # - check time
        if self.data['metrics']['today_is'] != today_is:
            u.debug(f'[metrics] today_is changed: {self.data["metrics"]["today_is"]} -> {today_is}')
            self.data['metrics']['today_is'] = today_is
            self.data['metrics']['today'] = {}
        # this month
        if self.data['metrics']['month_is'] != month_is:
            u.debug(f'[metrics] month_is changed: {self.data["metrics"]["month_is"]} -> {month_is}')
            self.data['metrics']['month_is'] = month_is
            self.data['metrics']['month'] = {}
        # this year
        if self.data['metrics']['year_is'] != year_is:
            u.debug(f'[metrics] year_is changed: {self.data["metrics"]["year_is"]} -> {year_is}')
            self.data['metrics']['year_is'] = year_is
            self.data['metrics']['year'] = {}

    def record_metrics(self, path: str = None) -> None:
        '''
        记录调用

        :param path: 访问的路径
        '''

        # check metrics list
        if path not in metrics_list:
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

    def check_device_status(self, trigged_by_timer: bool = False):
        '''
        按情况自动切换状态

        :param trigged_by_timer: 是否由计时器触发 (为 True 将不记录日志)
        '''
        device_status: dict = self.data.get('device_status', {})
        current_status: int = self.data.get('status', 0)  # 获取当前 status，默认为 0
        auto_switch_enabled: bool = env.util.auto_switch_status

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
                    u.debug(f'[check_device_status] 已自动切换状态 ({last_status} -> {self.data["status"]}).')
                elif not trigged_by_timer:
                    u.debug(f'[check_device_status] 当前状态已为 {current_status}, 无需切换.')
            elif not trigged_by_timer:
                u.debug(f'[check_device_status] 当前状态为 {current_status}, 不适用自动切换.')

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
                # --- Add: Heartbeat Check ---
                now = time.time()
                offline_timeout = env.status.device_offline_timeout
                devices_changed = False
                if "device_status" in self.data:
                    # 使用 list() 复制字典的 items，允许在迭代期间修改原始字典
                    for device_id, device_info in list(self.data["device_status"].items()):
                        last_heartbeat = device_info.get("last_heartbeat", 0)
                        # 检查是否超时
                        if now - last_heartbeat > offline_timeout:
                            # 仅当设备当前状态不是 [Offline] 时才标记并记录日志
                            if device_info.get("using", False) or device_info.get("app_name") != "[Offline]":
                                u.info(
                                    f"[timer_check] Device {device_id} timed out ({now - last_heartbeat:.0f}s > {offline_timeout}s). Marking as offline."
                                )
                                device_info["using"] = False
                                device_info["app_name"] = "[Offline]"
                                # 更新主状态的 last_updated 时间戳
                                self.data["last_updated"] = datetime.now(pytz.timezone(env.main.timezone)).strftime("%Y-%m-%d %H:%M:%S")
                                devices_changed = True
                # --- End Add ---

                self.check_metrics_time()  # 检测是否跨日
                self.check_device_status(trigged_by_timer=True)  # 检测设备状态并更新 status

                # --- Modify: Save if data changed OR devices timed out ---
                file_data = self.load(ret=True)
                # 比较相关部分，如果仅发生超时，则排除可能不同的时间戳
                current_data_comparable = {k: v for k, v in self.data.items() if k != "metrics"}  # 指标可能会频繁更改
                file_data_comparable = {k: v for k, v in file_data.items() if k != "metrics"}

                if file_data_comparable != current_data_comparable or devices_changed:
                    u.debug("[timer_check] Data changed, saving...")
                    self.save()
                # --- End Modify ---
            except Exception as e:
                u.warning(f'[timer_check] Error: {e}, retrying.')

    # --- check device heartbeat
