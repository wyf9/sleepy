# coding: utf-8

import json
import threading
from time import sleep, time
from datetime import datetime, timezone
from logging import getLogger

import pytz
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import safe_join

import utils as u
from models import ConfigModel

l = getLogger(__name__)

db = SQLAlchemy()


class DeviceStatus(db.Model):
    """设备状态表"""
    __tablename__ = 'device_status'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    show_name: Mapped[str] = mapped_column(String(255), nullable=False)
    using: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    app_name: Mapped[str] = mapped_column(Text, default='', nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=u.gettime(), onupdate=u.gettime())



class AppData(db.Model):
    """应用主数据表"""
    __tablename__ = 'app_data'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    private_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=u.utc_timestamp(), onupdate=u.utc_timestamp())


class PluginData(db.Model):
    """插件数据表"""
    __tablename__ = 'plugin_data'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plugin_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=u.utc_timestamp(), onupdate=u.utc_timestamp())


class Data:
    """
    数据库版本的 Data 类，使用 Flask-SQLAlchemy 存储数据
    
    :param app: Flask 应用实例
    :param config: 用户配置对象
    """
    
    _cache: dict[str, tuple[float, str]] = {}
    _data_check_interval: int = 60
    _plugins_enabled: list = []
    _c: ConfigModel
    app: Flask

    def __init__(self, app: Flask, config: ConfigModel):
        perf = u.perf_counter()
        self.app = app
        self._c = config
        app.config['SQLALCHEMY_DATABASE_URI'] = self._c.main.database
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # 初始化数据库
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            self._initialize_data()
            
        l.debug(f'[database_data] init took {perf()}ms')

    def _initialize_data(self):
        """初始化默认数据"""
        # 确保有主数据记录
        app_data = AppData.query.first()
        if not app_data:
            app_data = AppData()
            db.session.add(app_data)
            
        db.session.commit()

    # --- 属性访问器
    
    @property
    def status(self) -> int:
        """获取当前状态"""
        with self.app.app_context():
            app_data = AppData.query.first()
            return app_data.status if app_data else 0
    
    @status.setter
    def status(self, value: int):
        """设置当前状态"""
        with self.app.app_context():
            app_data = AppData.query.first()
            if not app_data:
                app_data = AppData()
                db.session.add(app_data)
            app_data.status = value
            db.session.commit()

    @property
    def private_mode(self) -> bool:
        """获取隐私模式状态"""
        with self.app.app_context():
            app_data = AppData.query.first()
            return app_data.private_mode if app_data else False
    
    @private_mode.setter
    def private_mode(self, value: bool):
        """设置隐私模式状态"""
        with self.app.app_context():
            app_data = AppData.query.first()
            if not app_data:
                app_data = AppData()
                db.session.add(app_data)
            app_data.private_mode = value
            db.session.commit()

    @property
    def last_updated(self) -> str:
        """获取最后更新时间"""
        with self.app.app_context():
            app_data = AppData.query.first()
            if app_data and app_data.last_update:
                return app_data.last_update.strftime('%Y-%m-%d %H:%M:%S')
            return '1970-01-01 08:00:00'

    # --- 设备状态管理

    def get_device_status(self) -> dict:
        """获取所有设备状态"""
        with self.app.app_context():
            devices = DeviceStatus.query.all()
            return {
                device.device_id: {
                    'show_name': device.show_name,
                    'using': device.using,
                    'app_name': device.app_name
                }
                for device in devices
            }

    def set_device_status(self, device_id: str, show_name: str, using: bool, app_name: str = ''):
        """设置设备状态"""
        with self.app.app_context():
            device = DeviceStatus.query.filter_by(device_id=device_id).first()
            if not device:
                device = DeviceStatus()
                device.device_id = device_id
                db.session.add(device)
            
            device.show_name = show_name
            device.using = using
            device.app_name = app_name
            db.session.commit()

    def remove_device(self, device_id: str):
        """移除设备"""
        with self.app.app_context():
            device = DeviceStatus.query.filter_by(device_id=device_id).first()
            if device:
                db.session.delete(device)
                db.session.commit()

    def clear_devices(self):
        """清除所有设备"""
        with self.app.app_context():
            DeviceStatus.query.delete()
            db.session.commit()

    # --- 统计数据管理

    def get_metrics_data(self):
        """获取统计数据（空实现，保持兼容性）"""
        now = datetime.now(pytz.timezone(self._c.main.timezone))
        return {
            'time': f'{now}',
            'timezone': self._c.main.timezone,
            'today_is': '0000-00-00',
            'month_is': '0000-00',
            'year_is': '0000',
            'today': {},
            'month': {},
            'year': {},
            'total': {}
        }

    def record_metrics(self, path: str | None = None) -> None:
        """记录访问统计（空实现，保持兼容性）"""
        pass

    # --- 插件数据管理

    def get_plugin_data(self, plugin_name: str) -> dict:
        """获取插件数据"""
        with self.app.app_context():
            plugin = PluginData.query.filter_by(plugin_name=plugin_name).first()
            return plugin.data if plugin else {}

    def set_plugin_data(self, plugin_name: str, data: dict):
        """设置插件数据"""
        with self.app.app_context():
            plugin = PluginData.query.filter_by(plugin_name=plugin_name).first()
            if not plugin:
                plugin = PluginData()
                plugin.plugin_name = plugin_name
                db.session.add(plugin)
            
            plugin.data = data
            db.session.commit()

    # --- 定时检查功能    def check_metrics_time(self) -> None:
        """检查时间跨度并重置统计数据（空实现，保持兼容性）"""
        pass

    def check_device_status(self):
        """检查设备状态并自动切换"""
        with self.app.app_context():
            current_status = self.status
            auto_switch_enabled: bool = False  # 等待插件支持

            if auto_switch_enabled and current_status in [0, 1]:
                devices = DeviceStatus.query.all()
                any_using = any(device.using for device in devices)
                
                new_status = 0 if any_using else 1
                if current_status != new_status:
                    self.status = new_status
                    l.debug(f'[check_device_status] switched status ({current_status} -> {new_status}).')

    def clean_cache(self):
        """清理过期缓存"""
        if self._c.main.debug:
            return
            
        now = time()
        for key in list(self._cache.keys()):
            if now - self._cache[key][0] > self._c.main.cache_age:
                del self._cache[key]

    def save(self):
        """保存插件数据到数据库"""
        try:
            with self.app.app_context():
                for plugin in self._plugins_enabled:
                    self.set_plugin_data(plugin.name, plugin.data)
        except Exception as e:
            l.error(f'Failed to save plugin data: {e}')

    def _data_check_timer(self):
        """定时检查数据变化"""
        l.info(f'[timer_check] started, interval: {self._data_check_interval} seconds.')
        while True:
            t = u.perf_counter()
            l.debug('[timer_check] running...')
            try:
                self.check_device_status()
                self.clean_cache()
                # 注意：数据库版本不需要 _auto_save，因为所有操作都是实时提交的
            except Exception as e:
                l.warning(f'[timer_check] error: {e}')
            l.debug(f'[timer_check] finished in {t()}ms.')
            sleep(self._data_check_interval)

    def start_timer_check(self, data_check_interval: int = 60, plugins_enabled: list = []):
        """启动定时检查线程"""
        self._data_check_interval = data_check_interval
        self._plugins_enabled = plugins_enabled
        self.timer_thread = threading.Thread(target=self._data_check_timer, daemon=True)
        self.timer_thread.start()

    # --- 缓存系统

    def get_cached(self, filename: str) -> str | None:
        """加载文本文件（经过缓存）"""
        filepath = safe_join(u.current_dir(), filename)
        if not filepath:
            return None
            
        try:
            if self._c.main.debug:
                # 调试模式直接加载
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 检查缓存
                now = time()
                cached = self._cache.get(filename)
                if cached and now - cached[0] < self._c.main.cache_age:
                    return cached[1]
                else:
                    # 加载并缓存
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self._cache[filename] = (now, content)
                    return content
        except (FileNotFoundError, IsADirectoryError):
            return None

    # --- 兼容性方法，用于与原始 data.py 接口保持一致

    @property
    def device_status(self) -> dict:
        """获取设备状态（兼容性属性）"""
        return self.get_device_status()

    @property
    def metrics(self) -> dict:
        """获取统计数据（兼容性属性，返回空数据）"""
        return {
            'today_is': '0000-00-00',
            'month_is': '0000-00',
            'year_is': '0000',
            'today': {},
            'month': {},
            'year': {},
            'total': {}
        }

    @property
    def plugin(self) -> dict:
        """获取所有插件数据（兼容性属性）"""
        with self.app.app_context():
            plugins = PluginData.query.all()
            return {plugin.plugin_name: plugin.data for plugin in plugins}
