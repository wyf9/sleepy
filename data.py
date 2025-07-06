# coding: utf-8

import os
from datetime import datetime
from logging import getLogger
from threading import Thread
from time import sleep, time
from typing import Any

from werkzeug.security import safe_join
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from objtyping import to_primitive
import pytz
import schedule

import utils as u
from models import ConfigModel

l = getLogger(__name__)

db = SQLAlchemy()
LIMIT = 1024

# -----


class _MainData(db.Model):
    '''
    主程序数据
    '''
    __tablename__ = 'main'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=0)
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    '''当前状态 id *(即 status_list 中的列表索引)*'''
    private_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    '''是否开启隐私模式 *(启用时 /query 返回中的 `device` 替换为空字典)*'''
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=u.nowutc, onupdate=u.nowutc)
    '''数据最后更新时间 (utc)'''


class _DeviceStatusData(db.Model):
    '''
    设备状态
    '''
    __tablename__ = 'device_status'
    id: Mapped[str] = mapped_column(String(LIMIT), primary_key=True, unique=True, nullable=False)
    '''[必选] 设备唯一 id'''
    show_name: Mapped[str] = mapped_column(String(LIMIT), nullable=False)
    '''[必选] 设备显示名称'''
    # desc: Mapped[str] = mapped_column(String(LIMIT), nullable=True)
    # '''[可选] 设备描述'''
    # online: Mapped[bool] = mapped_column(Boolean, nullable=True)
    # '''[可选] 设备是否在线'''
    using: Mapped[bool] = mapped_column(Boolean, nullable=True)
    '''[可选] 设备是否正在使用'''
    status: Mapped[str] = mapped_column(Text, nullable=True)
    '''[可选] 设备状态文本 (如打开的应用名)'''
    # playing: Mapped[str] = mapped_column(Text, nullable=True)
    # '''[可选] 设备正在播放的媒体名'''
    # battery: Mapped[int] = mapped_column(Integer, nullable=True)
    # '''[可选] 设备电量 (0~100)'''
    # is_charging: Mapped[bool] = mapped_column(Boolean, nullable=True)
    # '''[可选] 设备是否正在充电'''
    fields: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    '''[可选] 设备的扩展字段'''
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=u.nowutc, onupdate=u.nowutc)
    '''(本设备) 数据最后更新时间 (UTC)'''


class _MetricsMetaData(db.Model):
    '''
    访问统计元数据
    '''
    __tablename__ = 'metrics_meta'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=0)
    today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    week: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    year: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class _MetricsData(db.Model):
    '''
    访问统计数据
    '''
    __tablename__ = 'metrics'
    path: Mapped[str] = mapped_column(String(LIMIT), primary_key=True, unique=True, nullable=False)
    daily: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weekly: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    yearly: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class _PluginData(db.Model):
    '''
    插件数据
    '''
    __tablename__ = 'plugin'
    id: Mapped[str] = mapped_column(String(LIMIT), primary_key=True, unique=True, nullable=False)
    '''插件 id'''
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    '''插件数据'''


# -----


class Data:
    '''
    data 类, 定义 sql 数据表格式
    '''

    def __init__(self, config: ConfigModel, app: Flask):
        perf = u.perf_counter()
        self._app = app
        self._c = config
        # 配置数据库地址
        app.config['SQLALCHEMY_DATABASE_URI'] = self._c.main.database
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # 初始化数据库
        db.init_app(app)
        with app.app_context():
            db.create_all()
            main_data = _MainData.query.first()
            if not main_data:
                l.debug(f'[data] main_data not exist, creating a new one')
                main_data = _MainData()
                db.session.add(main_data)
                db.session.commit()

            metrics_metadata = _MetricsMetaData.query.first()
            if self._c.metrics.enabled and not metrics_metadata:
                l.debug(f'[data] metrics_metadata not exist, creating a new one')
                metrics_metadata = _MetricsMetaData()
                db.session.add(metrics_metadata)
                db.session.commit()

            # 启动 schedule loop
            self._schedule_loop_th = Thread(target=self._schedule_loop, daemon=True)
            self._schedule_loop_th.start()

        l.debug(f'[data] init took {perf()}ms')

    def _throw(self, e: SQLAlchemyError):
        '''
        简化抛出 sql call failed error
        '''
        l.error(f'SQL Call Failed: {e}')
        raise u.APIUnsuccessful(500, 'Database Error')

    def _schedule_loop(self):
        if self._c.metrics.enabled:
            # 先执行一次
            self._metrics_refresh()
            schedule.every().day.at('00:00:00', self._c.main.timezone).do(self._metrics_refresh)  # metrics check
        schedule.every(self._c.main.cache_age).seconds.do(self._clean_cache)  # cache

        while True:
            schedule.run_pending()
            sleep(1)

    # --- 主程序数据访问

    @property
    def status(self) -> int:
        '''
        当前的状态 id
        '''
        try:
            with self._app.app_context():
                maindata: _MainData = _MainData.query.first()  # type: ignore
                return maindata.status
        except SQLAlchemyError as e:
            self._throw(e)

    @status.setter
    def status(self, value: int):
        try:
            with self._app.app_context():
                maindata: _MainData = _MainData.query.first()  # type: ignore
                maindata.status = value
                db.session.commit()
        except SQLAlchemyError as e:
            self._throw(e)

    @property
    def private_mode(self) -> bool:
        '''
        是否开启隐私模式 (不返回设备状态)
        '''
        try:
            with self._app.app_context():
                maindata: _MainData = _MainData.query.first()  # type: ignore
                return maindata.private_mode
        except SQLAlchemyError as e:
            self._throw(e)

    @private_mode.setter
    def private_mode(self, value: bool):
        try:
            with self._app.app_context():
                maindata: _MainData = _MainData.query.first()  # type: ignore
                maindata.private_mode = value
                db.session.commit()
        except SQLAlchemyError as e:
            self._throw(e)

    @property
    def last_updated(self) -> datetime:
        '''
        数据最后更新时间 (utc)
        '''
        try:
            with self._app.app_context():
                maindata: _MainData = _MainData.query.first()  # type: ignore
                return maindata.last_updated
        except SQLAlchemyError as e:
            self._throw(e)

    @last_updated.setter
    def last_updated(self, value: datetime):
        try:
            with self._app.app_context():
                maindata: _MainData = _MainData.query.first()  # type: ignore
                maindata.last_updated = value
                db.session.commit()
        except SQLAlchemyError as e:
            self._throw(e)

    # --- 设备状态接口

    @property
    def _raw_device_list(self) -> dict[str, dict[str, str | int | float | bool]]:
        '''
        原始设备列表 (未排序)
        '''
        try:
            # 判断隐私模式
            if self.private_mode:
                return {}
            with self._app.app_context():
                devices: list[_DeviceStatusData] = _DeviceStatusData.query.all().copy()
                for d in devices:
                    d.last_updated = d.last_updated.timestamp()  # type: ignore
                ret = to_primitive({d.id: d for d in devices}, format_date_time=False)
                return ret  # type: ignore
        except SQLAlchemyError as e:
            self._throw(e)

    @property
    def device_list(self) -> dict[str, dict[str, Any]]:
        '''
        排序后设备列表
        '''
        try:
            if self.private_mode:
                # 隐私模式
                devicelst = {}
            elif self._c.status.using_first:
                # 使用中优先
                devicelst = {}  # devicelst = device_using
                device_not_using = {}
                device_unknown = {}
                for k, v in self._raw_device_list.items():
                    if v.get('using') == True:  # * 正在使用
                        devicelst[k] = v
                    elif v.get('using') == False:  # * 未在使用
                        if self._c.status.not_using:
                            v['status'] = self._c.status.not_using  # 如锁定了未在使用时状态名, 则替换
                        device_not_using[k] = v
                    else:  # * 未知
                        device_unknown[k] = v
                if self._c.status.sorted:
                    devicelst = dict(sorted(devicelst.items()))
                    device_not_using = dict(sorted(device_not_using.items()))
                    device_unknown = dict(sorted(device_unknown.items()))
                # 追加到末尾
                devicelst.update(device_not_using)
                devicelst.update(device_unknown)
            else:
                # 正常获取
                devicelst = self._raw_device_list
                # 如锁定了未在使用时状态名, 则替换
                if self._c.status.not_using:
                    for d in devicelst.keys():
                        if devicelst[d].get('using') == False:
                            devicelst[d]['status'] = self._c.status.not_using
                if self._c.status.sorted:
                    devicelst = dict(sorted(devicelst.items()))
            return devicelst
        except SQLAlchemyError as e:
            self._throw(e)

    def device_get(self, id: str) -> dict[str, str | int | float | bool] | None:
        '''
        获取指定设备状态

        :param id: 设备 id
        '''
        try:
            with self._app.app_context():
                device: _DeviceStatusData | None = _DeviceStatusData.query.filter_by(id=id).first()
                if device:
                    return to_primitive(device)  # type: ignore
                else:
                    return None
        except SQLAlchemyError as e:
            self._throw(e)

    def device_set(self, id: str | None = None,
                   show_name: str | None = None,
                   using: bool | None = None,
                   status: str | None = None,
                   fields: dict = {}
                   ):
        '''
        设备状态设置

        :param id: 设备唯一 id
        :param show_name: 设备显示名称
        :param using: 设备是否正在使用
        :param status: 设备状态文本
        :param fields: 扩展字段
        '''
        try:
            with self._app.app_context():
                device = _DeviceStatusData.query.filter_by(id=id).first()
                if not id:
                    # 验证设备 id 不为空
                    raise u.APIUnsuccessful(400, 'device id cannot be empty!')
                if not device:
                    # 在创建时验证必填字段 (显示名称不能为空)
                    if not show_name:
                        raise u.APIUnsuccessful(400, 'device show_name cannot be empty!')
                    device = _DeviceStatusData()
                    device.id = id
                    db.session.add(device)
                device.show_name = show_name or device.show_name
                device.using = using if using is not None else device.using
                device.status = status or device.status
                device.fields = u.deep_merge_dict(device.fields, fields)
                db.session.commit()
                self.last_updated = u.nowutc()
        except SQLAlchemyError as e:
            self._throw(e)

    def device_remove(self, id: str):
        '''
        移除单个设备

        :param id: 设备唯一 id
        '''
        try:
            with self._app.app_context():
                device: _DeviceStatusData | None = _DeviceStatusData.query.filter_by(id=id).first()
                if device:
                    db.session.delete(device)
                    db.session.commit()
                    self.last_updated = u.nowutc()
        except SQLAlchemyError as e:
            self._throw(e)

    def device_clear(self):
        '''
        清除设备状态
        '''
        try:
            with self._app.app_context():
                _DeviceStatusData.query.delete()
                db.session.commit()
                self.last_updated = u.nowutc()
        except SQLAlchemyError as e:
            self._throw(e)

    # --- 统计数据访问

    def record_metrics(self, path: str, count: int = 1, override: bool = False):
        '''
        记录 metrics 数据

        :param path: 路径
        :param count: 记录增加次数 (调试使用?)
        :param override: 是否直接替换值而不是增加
        '''
        if not path in self._c.metrics.allow_list:
            return
        try:
            with self._app.app_context():
                metric: _MetricsData | None = _MetricsData.query.filter_by(path=path).first()
                if not metric:
                    metric = _MetricsData()
                    metric.path = path
                    metric.daily = 0
                    metric.weekly = 0
                    metric.monthly = 0
                    metric.yearly = 0
                    metric.total = 0
                    db.session.add(metric)
                if override:
                    metric.daily = count
                    metric.weekly = count
                    metric.monthly = count
                    metric.yearly = count
                    metric.total = count
                else:
                    metric.daily += count
                    metric.weekly += count
                    metric.monthly += count
                    metric.yearly += count
                    metric.total += count
                db.session.commit()
        except SQLAlchemyError as e:
            self._throw(e)

    @property
    def metrics_data(self) -> list[dict[str, str]]:
        '''
        获取 metrics 数据

        :return: (今日, 全部)
        '''
        try:
            raw_metrics: list[_MetricsData] = _MetricsData.query.all()
            daily = {}
            weekly = {}
            monthly = {}
            yearly = {}
            total = {}
            for i in raw_metrics:
                daily[i.path] = i.daily
                weekly[i.path] = i.weekly
                monthly[i.path] = i.monthly
                yearly[i.path] = i.yearly
                total[i.path] = i.total
            return [daily, weekly, monthly, yearly, total]
        except SQLAlchemyError as e:
            self._throw(e)

    @property
    def metrics_resp(self) -> dict[str, Any]:
        '''
        获取 metrics 返回
        '''
        enabled = self._c.metrics.enabled
        if enabled:
            daily, weekly, monthly, yearly, total = self.metrics_data if enabled else ({}, {}, {}, {}, {})
            now = datetime.now(pytz.timezone(self._c.main.timezone))
            return {
                'enabled': True,
                'time': now.timestamp(),
                'time_local': now.strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': self._c.main.timezone,
                'daily': daily,
                'weekly': weekly,
                'monthly': monthly,
                'yearly': yearly,
                'total': total
            }
        else:
            return {
                'enabled': False
            }

    def _metrics_refresh(self):
        '''
        (在 每日 0 点 / 启动时 执行) 刷新 metrics 数据
        '''
        perf = u.perf_counter()
        try:
            with self._app.app_context():
                raw_metrics: list[_MetricsData] = _MetricsData.query.all()
                meta_metrics: _MetricsMetaData = _MetricsMetaData.query.first()  # type: ignore

                # get today
                now = datetime.now(pytz.timezone(self._c.main.timezone))
                today = now.day
                week = now.weekday()
                month = now.month
                year = now.year

                # compare
                if today != meta_metrics.today:
                    meta_metrics.today = today
                    for i in raw_metrics:
                        i.daily = 0

                if week != meta_metrics.week:
                    meta_metrics.week = week
                    for i in raw_metrics:
                        i.weekly = 0

                if month != meta_metrics.month:
                    meta_metrics.month = month
                    for i in raw_metrics:
                        i.monthly = 0

                if year != meta_metrics.year:
                    meta_metrics.year = year
                    for i in raw_metrics:
                        i.yearly = 0

                db.session.commit()
        except SQLAlchemyError as e:
            l.error(f'[_metrics_refresh] Error: {e}')
        l.debug(f'[_metrics_refresh] took {perf()}ms')

    # --- 插件数据访问

    def get_plugin_data(self, id: str) -> dict:
        '''
        获取插件数据 (没有则会创建)
        '''
        try:
            with self._app.app_context():
                plugin: _PluginData | None = _PluginData.query.filter_by(id=id).first()
                if plugin is None:
                    plugin = _PluginData()
                    plugin.id = id
                    db.session.add(plugin)
                    db.session.commit()
                return plugin.data
        except SQLAlchemyError as e:
            self._throw(e)

    def set_plugin_data(self, id: str, data: dict):
        '''
        设置插件数据
        '''
        try:
            with self._app.app_context():
                plugin: _PluginData | None = _PluginData.query.filter_by(id=id).first()
                if plugin is None:
                    plugin = _PluginData()
                    plugin.id = id
                    plugin.data = {}
                    db.session.add(plugin)
                plugin.data = data
                db.session.commit()
        except SQLAlchemyError as e:
            self._throw(e)

    # --- 缓存系统

    _cache: dict[str, tuple[float, str]] = {}

    def get_cached_file(self, dirname: str, filename: str) -> str | None:
        '''
        加载文本文件 (经过缓存)

        :param dirname: 路径
        :param filename: 文件名
        :return str: (加载成功) 文件内容
        :return None: (加载失败) 空
        '''
        filepath = safe_join(u.get_path(dirname), filename)
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
                cached = self._cache.get(f'file-{filename}')
                if cached and now - cached[0] < self._c.main.cache_age:
                    # has cache, and not expired
                    return cached[1]
                else:
                    # no cache, or expired
                    with open(filepath, 'r', encoding='utf-8') as f:
                        ret = f.read()
                        f.close()
                    self._cache[f'file-{filename}'] = (now, ret)
                    return ret
        except FileNotFoundError or IsADirectoryError:
            # not found / isn't file -> none
            return None

    def _clean_cache(self):
        '''
        清理过期缓存
        '''
        if self._c.main.debug:
            return
        now = time()
        for name in self._cache.keys():
            if now - self._cache.get(name, (now, ''))[0] > self._c.main.cache_age:
                self._cache.pop(name, None)
