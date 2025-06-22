# coding: utf-8

import os
from datetime import datetime
from logging import getLogger
import typing as t

from werkzeug.security import safe_join
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from objtyping import to_primitive

import utils as u
from models import ConfigModel

l = getLogger(__name__)

db = SQLAlchemy()
LIMIT = 255

# -----


class _DeviceStatusData(db.Model):
    '''
    设备状态
    '''
    __tablename__ = 'device_status_data'
    id: Mapped[str] = mapped_column(String(LIMIT), primary_key=True, unique=True, nullable=False)
    '''[必选] 设备唯一 id'''
    show_name: Mapped[str] = mapped_column(String(LIMIT), nullable=False)
    '''[必选] 设备显示名称'''
    desc: Mapped[str] = mapped_column(String(LIMIT), nullable=True)
    '''[可选] 设备描述'''
    online: Mapped[bool] = mapped_column(Boolean, nullable=True)
    '''[可选] 设备是否在线'''
    using: Mapped[bool] = mapped_column(Boolean, nullable=True)
    '''[可选] 设备是否正在使用'''
    app_name: Mapped[str] = mapped_column(Text, nullable=True)
    '''[可选] 设备打开的应用名'''
    playing: Mapped[str] = mapped_column(Text, nullable=True)
    '''[可选] 设备正在播放的媒体名'''
    battery: Mapped[int] = mapped_column(Integer, nullable=True)
    '''[可选] 设备电量 (0~100)'''
    is_charging: Mapped[bool] = mapped_column(Boolean, nullable=True)
    '''[可选] 设备是否正在充电'''
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=u.nowutc, onupdate=u.nowutc)
    '''(本设备) 数据最后更新时间 (UTC)'''


class _PluginData(db.Model):
    '''
    插件数据
    '''
    __tablename__ = 'plugin_data'
    name: Mapped[str] = mapped_column(String(LIMIT), primary_key=True, unique=True, nullable=False)
    '''插件名称 (== id?)'''
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    '''插件数据'''


class _MainData(db.Model):
    '''
    主数据
    '''
    __tablename__ = 'main_data'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=0)
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    '''当前的状态 id'''
    private_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    '''是否开启隐私模式 (不返回设备状态)'''
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=u.nowutc, onupdate=u.nowutc)
    '''数据最后更新时间 (utc)'''


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

            # 缓存最后更新时间
            self._last_updated_cache = main_data.last_updated

        l.debug(f'[data] init took {perf()}ms')

    def _throw(self, e: SQLAlchemyError):
        '''
        简化抛出 sql call failed error
        '''
        l.error(f'SQL Call Failed: {e}')
        raise u.APIUnsuccessful(500, 'Database Error')

    # --- _MainData 属性访问

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
                return to_primitive({d.id: d for d in devices}, format_date_time=False)  # type: ignore
        except SQLAlchemyError as e:
            self._throw(e)

    @property
    def device_list(self) -> dict[str, dict[str, str | int | float | bool]]:
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
                device_offline = {}
                device_unknown = {}
                for k, v in self._raw_device_list.items():
                    if v.get('online') == True:  # - 首先确保在线
                        if v.get('using') == True:  # * 正在使用
                            devicelst[k] = v
                        elif v.get('using') == False:  # * 未在使用
                            if self._c.status.not_using:
                                v['app_name'] = self._c.status.not_using  # 如锁定了未在使用时设备名, 则替换
                            device_not_using[k] = v
                    elif v.get('online') == False:  # - 不在线
                        if self._c.status.offline:
                            v['app_name'] = self._c.status.offline  # 如锁定了离线时设备名, 则替换
                        device_offline[k] = v
                    else:  # - 无此字段
                        device_unknown[k] = v
                if self._c.status.sorted:
                    devicelst = dict(sorted(devicelst.items()))
                    device_not_using = dict(sorted(device_not_using.items()))
                devicelst.update(device_not_using)  # append items to end
                devicelst.update(device_offline)
                devicelst.update(device_unknown)
            else:
                # 正常获取
                devicelst = self._raw_device_list
                # 如锁定了离线 / 未在使用时设备名, 则替换 (离线优先)
                for d in devicelst.keys():
                    if self._c.status.offline and devicelst[d].get('online') == False:  # 离线
                        devicelst[d]['app_name'] = self._c.status.offline
                    elif self._c.status.not_using and devicelst[d].get('using') == False:  # 未在使用
                        devicelst[d]['app_name'] = self._c.status.not_using
                if self._c.status.sorted:
                    devicelst = dict(sorted(devicelst.items()))
            return devicelst
        except SQLAlchemyError as e:
            self._throw(e)

    def device_get(self, id: str) -> dict[str, str | int | float | bool] | None:
        '''
        获取指定设备状态
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

    def device_set(self, id: str,
                   show_name: str | None = None,
                   desc: str | None = None,
                   online: bool | None = None,
                   using: bool | None = None,
                   app_name: str | None = None,
                   playing: str | None = None,
                   battery: int | None = None,
                   is_charging: bool | None = None
                   ):
        '''
        设备状态设置

        :param id: 设备唯一 id
        '''
        try:
            with self._app.app_context():
                device = _DeviceStatusData.query.filter_by(id=id).first()
                if not device:
                    # 验证必填字段 (显示名称不能为空)
                    if not show_name:
                        raise u.APIUnsuccessful(400, 'show_name cannot be empty!')
                    device = _DeviceStatusData()
                    device.id = id
                    db.session.add(device)
                update_fields = {
                    'show_name': show_name or device.show_name,
                    'desc': desc,
                    'online': online,
                    'using': using,
                    'app_name': app_name,
                    'playing': playing,
                    'battery': battery,
                    'is_charging': is_charging
                }
                for k, v in update_fields.items():
                    if v is not None:
                        # 验证特殊字段 (0 <= 电量 <= 100)
                        if k == 'battery' and not (0 <= v <= 100):
                            db.session.rollback()
                            raise u.APIUnsuccessful(400, 'Invaild battery value! it must be a number between 0 and 100.')
                    setattr(device, k, v)
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
