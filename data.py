# coding: utf-8

import os
import random
import pytz
import json
import threading
from time import sleep
from datetime import datetime

from orm import ColorGroupIndex, Event
import orm
import utils as u
import env as env
from setting import metrics_list

import sqlite3

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
        self.init_db()


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

    def record_metrics(self, path: str = None) -> None:
        '''
        记录调用

        :param path: 访问的路径
        '''

        # check metrics list
        if not path in metrics_list:
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
                self.check_metrics_time()  # 检测是否跨日
                self.check_device_status(trigged_by_timer=True)  # 检测设备状态并更新 status
                file_data = self.load(ret=True)
                if file_data != self.data:
                    self.save()
            except Exception as e:
                u.warning(f'[timer_check] Error: {e}, retrying.')

    def init_db(self):
        '''
        初始化数据库
        
        '''
        if env.util.save_to_db == 'sqlite':
            db_path = f'{env.util.sqlite_name}.db'
            if not os.path.exists(db_path):
                u.info('No existing sqlite database founded, will create one.')
            try:
                db = sqlite3.connect(db_path)
                cursor = db.cursor()
            except Exception as e:
                u.warning(f'Error when connecting sqlite {env.util.sqlite_name}: {e}')
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Events'")
            if cursor.fetchone()[0] == 0:
                u.info('No existing "Events" table, will create one.')
                try:
                    for command in u.get_sql(r'sql/sqlite_init.sql'):
                        cursor.execute(command)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    u.warning(f'Failed to execute SQL file: {str(e)}')
            cursor.close()
            db.close()
    
    
    def save_db(self, device_id:str = None):
        '''
        将设备使用数据存储至数据库
        
        支持只存储某个设备的数据
        
        :param id: 选择存储的设备
        '''
        db_path = f'{env.util.sqlite_name}.db'
        u.debug(f'[save_db] started, saving data to {env.util.save_to_db}.')
        if env.util.save_to_db == 'sqlite':
            ds_dict:dict = self.data["device_status"]
            device_dict:dict = ds_dict.get(device_id)
            if device_dict == None:
                u.warning(f'[save_db] Status of this device not detected, will not save.')        
                return
            
            sql_script = u.get_sql(r'sql/save.sql')[0]
            if device_id != None:
                db = orm.get_db()
                cursor = db.cursor()
                try:
                    cursor.execute(sql_script,(
                        device_id,
                        device_dict.get('show_name'),
                        device_dict.get('app_name'),
                        device_dict.get('using'),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    db.commit()
                    u.debug(f'[save_db] Successfully saving data to {env.util.save_to_db}.')
                except Exception as e:
                    db.rollback()
                    u.warning(f'[save_db] Error while inserting value into database: {e}')
                    
                
                if orm.get_color_orm().find_group_color(device_dict["app_name"]) == None:
                    
                    new_color_row = {
                        'group_name': device_dict["app_name"],
                        'color_hex': f'#{random.randint(0, 0xFFFFFF):06X}',
                        '[set]': 0
                    }
                    
                    orm.get_color_orm().append_row(new_color_row)
                cursor.close()
    
    def db_to_xml(self, device_id:str ,table:str='Events', start_from:datetime=None, end_to:datetime=None, ignore_sec=2) -> str:
        """将数据库中设备使用的信息转换为可被ManicTime接收的xml文件

        Args:
            device_id (str): 设备标识符
            start_from (datetime): 开始时间
            end_to (datetime): 结束时间
        """
            # ignore_sec (int): 忽略小于等于此时间秒数的事件
        # 注：table参数和ignore_sec参数相关逻辑未完成，暂时留置
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        # 定义 XML 结构
        timeline = ET.Element("Timeline")
        color = ET.SubElement(timeline, "Color")
        color.text = "#bacf9c" # #bacf9c
        activities = ET.SubElement(timeline, "Activities")
        groups_elem = ET.SubElement(timeline,"Groups")
        
        events = orm.get_orm().query(Event, 
            "SELECT * FROM Events WHERE device_id = ? AND start_time BETWEEN ? AND ?", 
            (device_id,    
                start_from.strftime('%Y-%m-%d %H:%M:%S'),
                end_to.strftime('%Y-%m-%d %H:%M:%S'))
            )
        
        events = sorted(events, key=lambda e: e.start_time, reverse=False) # False:升序，由旧到新
        
        if events:
            last_event = orm.get_orm().query(Event, '''SELECT * FROM Events WHERE device_id = ? AND id = ?''', (device_id, events[0].id - 1))
            if last_event is not None:
                events.insert(0, last_event[0])
        
        color_groups = orm.get_color_orm().find_matching_color_groups(events)
        color_groups_index = ColorGroupIndex(color_groups)
        
        for index, event in enumerate(events):

            color_group = color_groups_index.get_group_by_name(event.app_name)
            if color_group is None:
                u.warning(f'[db_to_xml] Generating group id: event exists but not found in group, will pass event:{event.app_name}')
                continue
                
            group_id = color_group.id
            
            activity_elem = ET.SubElement(activities, "Activity")
                    
            group_id_elem = ET.SubElement(activity_elem, "GroupId")
            group_id_elem.text = str(group_id)
                    
            display_name_elem = ET.SubElement(activity_elem, "DisplayName")
            display_name_elem.text = event.app_name
            
            start_time_elem = ET.SubElement(activity_elem, "StartTime")
            start_time_elem.text = event.start_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
            end_time_elem = ET.SubElement(activity_elem, "EndTime")
            if index == len(events) - 1:
                end_time_elem.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
            else:
                end_time_elem.text = events[index + 1].start_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
        for color_group in color_groups:
            
            group_elem = ET.SubElement(groups_elem, "Group")
            
            group_id_elem = ET.SubElement(group_elem, "GroupId")
            group_id_elem.text = str(color_group.id)
            
            color_elem = ET.SubElement(group_elem,"Color")
            color_elem.text = color_group.color_hex
            
            display_name_elem_g = ET.SubElement(group_elem, "DisplayName")
            display_name_elem_g.text = color_group.group_name

        xmlstr = minidom.parseString(ET.tostring(timeline)).toprettyxml(indent="  ")

        return xmlstr
        
    # --- check device heartbeat
    # TODO
