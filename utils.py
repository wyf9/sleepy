# coding: utf-8
import os
from datetime import datetime
from pathlib import Path
import json
from logging import Formatter, getLogger, DEBUG

from flask import make_response, Response

l = getLogger(__name__)


class CustomFormatter(Formatter):
    symbols = {
        'DEBUG': '⚙️ ',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }
    default_symbol = '📢'
    show_symbol: bool

    def __init__(self, show_symbol: bool = True):
        super().__init__()
        self.show_symbol = show_symbol

    def format(self, record):
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        message = super().format(record)
        symbol = f' {self.symbols.get(record.levelname, self.default_symbol)}' if self.show_symbol else ''
        formatted_message = f"{timestamp}{symbol} [{record.levelname}] {message}"
        return formatted_message


def format_dict(dic: dict | list) -> Response:
    '''
    字典 -> Response (内容为格式化后的 json 文本) \n
    @param dic: 字典
    '''
    response = make_response(
        json.dumps(dic, indent=4, ensure_ascii=False, sort_keys=False, separators=(', ', ': '))
    )
    response.mimetype = 'application/json'
    return response


def reterr(code: str, message: str) -> Response:
    '''
    返回错误信息 ~~json~~ response

    :param code: 代码
    :param message: 消息
    '''
    ret = {
        'success': False,
        'code': code,
        'message': message
    }
    return format_dict(ret)


def cache_response(*args):
    '''
    给返回添加缓存标头
    '''
    resp = make_response(*args)
    resp.headers['Cache-Control'] = 'max-age=86400, must-revalidate'
    resp.headers['Expires'] = '86400'
    return resp

def no_cache_response(*args):
    '''
    给返回添加阻止缓存标头
    '''
    resp = make_response(*args)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


class SleepyException(Exception):
    '''
    Custom Exception for sleepy
    '''

    def __init__(self, msg: str | None = None):
        '''
        SleepyException

        :param msg: 错误信息
        '''
        if msg:
            self.msg = msg

    def __str__(self):
        return self.msg


def exception(msg: str) -> SleepyException:
    '''
    抛出 SleepyException

    :param msg: 错误描述
    '''
    raise SleepyException(msg)


def list_files(path: str, include_subfolder: bool = False, name_only: bool = False, strict_exist: bool = False, ext: str = '') -> list:
    '''
    列出目录下的**文件**列表

    :param path: 目录路径
    :param include_subfolder: 是否包括子目录的文件 *(递归查找)*
    :param name_only: 是否仅返回文件名
    :param strict_exist: 目标目录不存在时是否抛出错误 *(为否则返回空列表)*
    :param ext: 指定文件扩展名 *(只有文件以此结尾才会计入)*
    '''

    try:
        rawlst = os.listdir(path)
        endlist: list[str] = []
        for i in rawlst:
            fullname_i = str(Path(path).joinpath(i))
            if os.path.isdir(fullname_i) and include_subfolder:
                # 如为目录，且包含子目录 -> 递归
                endlist.extend([
                    n if name_only else str(Path(i).joinpath(n))
                    for n in list_files(
                        path=fullname_i,
                        include_subfolder=include_subfolder,
                        name_only=name_only,
                        strict_exist=strict_exist,
                        ext=ext
                    )
                ])
            # 否则为文件 -> 添加
            endlist.append(i if name_only else fullname_i)
    except FileNotFoundError:
        # 找不到目标文件夹
        if strict_exist:
            raise
        else:
            return []
    else:
        if ext:
            newlst = []
            for i in endlist:
                if i.endswith(ext):
                    newlst.append(i)
            return newlst
        else:
            return endlist


def list_dirs(path: str, strict_exist: bool = False, name_only: bool = False) -> list:
    '''
    列出目录下的**目录**列表

    :param path: 目录路径
    :param strict_exist: 目标目录不存在时是否抛出错误 *(为否则返回空列表)*
    :param name_only: 是否仅返回目录名
    '''

    try:
        rawlst = os.listdir(path)
        endlist: list[str] = []
        for i in rawlst:
            fullname_i = str(Path(path).joinpath(i))
            if os.path.isdir(fullname_i) and (not '__pycache__' in fullname_i):
                # 如为目录 -> 追加
                endlist.append(i if name_only else fullname_i)
        return endlist
    except FileNotFoundError:
        # 找不到目标文件夹
        if strict_exist:
            raise
        else:
            return []


_themes_available_cache = sorted(list_dirs('theme', name_only=True))


def themes_available() -> list[str]:
    if l.level == DEBUG:
        return sorted(list_dirs('theme', name_only=True))
    else:
        return _themes_available_cache


def tobool(string: str, throw: bool = False) -> bool | None:
    '''
    将形似 `true`, `1`, `yes` 之类的内容转换为布尔值

    :param throw: 控制无匹配项时是否直接抛出错误 (为否则返回 None)
    :return: `True` or `False` or `None` (如果不在 `booldict` 内)
    '''
    booldict = {
        # 此列表中的项 (强制小写) 会转换为对应的布尔值
        'true': True,
        'false': False,
        '1': True,
        '0': False,
        't': True,
        'f': False,
        'yes': True,
        'no': False,
        'y': True,
        'n': False,
        'on': True,
        'off': False,
        'enable': True,
        'disable': False,
        'v': True,
        'x': False
    }
    ret = booldict.get(str(string).lower(), None)
    assert ret or (not throw), ValueError
    return ret


def current_dir() -> str:
    '''
    获取当前主程序所在目录
    '''
    return str(Path(__file__).parent)


def get_path(path: str, create_dirs: bool = True, is_dir: bool = False) -> str:
    '''
    相对路径 (基于主程序目录) -> 绝对路径

    :param path: 相对路径
    :param create_dirs: 是否自动创建目录（如果不存在）
    :param is_dir: 目标是否为目录
    :return: 绝对路径
    '''
    if current_dir().startswith('/var/task') and path == '/data/data.json':
        # 适配 Vercel 部署 (调整 data/data.json 路径为可写的 /tmp/)
        full_path = '/tmp/sleepy/data/data.json'
    else:
        full_path = str(Path(__file__).parent.joinpath(path))
        if create_dirs:
            # 自动创建目录
            if is_dir:
                os.makedirs(full_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path
