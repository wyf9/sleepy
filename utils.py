# coding: utf-8
import os
import time
from datetime import datetime
from pathlib import Path
from logging import Formatter, getLogger, DEBUG
from functools import wraps

import flask
from colorama import Fore, Style

l = getLogger(__name__)


class CustomFormatter(Formatter):
    '''
    自定义的 logging formatter
    '''
    symbols = {
        'DEBUG': '⚙️ ',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }
    replaces = {
        'DEBUG': f'[DEBUG]',
        'INFO': f'[INFO] ',
        'WARNING': f'[WARN] ',
        'ERROR': f'[ERROR]',
        'CRITICAL': f'[CRIT] '
    }
    replaces_colorful = {
        'DEBUG': f'{Fore.BLUE}[DEBUG]{Style.RESET_ALL}',
        'INFO': f'{Fore.GREEN}[INFO]{Style.RESET_ALL} ',
        'WARNING': f'{Fore.YELLOW}[WARN]{Style.RESET_ALL} ',
        'ERROR': f'{Fore.RED}[ERROR]{Style.RESET_ALL}',
        'CRITICAL': f'{Fore.MAGENTA}[CRIT]{Style.RESET_ALL} '
    }
    default_symbol = '📢'
    colorful: bool

    def __init__(self, colorful: bool = True):
        super().__init__()
        self.colorful = colorful

    def format(self, record):
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        message = super().format(record)
        symbol = f' {self.symbols.get(record.levelname, self.default_symbol)}' if self.colorful else ''
        level = self.replaces_colorful.get(record.levelname, f'[{record.levelname}]') if self.colorful else self.replaces.get(record.levelname, f'[{record.levelname}]')
        file = relative_path(record.pathname)
        # func = '__main__' if record.funcName == '<module>' else record.funcName
        # formatted_message = f"{timestamp}{symbol} {level} | {file}:{record.lineno} @{func} | {message}"
        formatted_message = f"{timestamp}{symbol} {level} | {file}:{record.lineno} | {message}"
        return formatted_message


def cache_response(*args):
    '''
    给返回添加缓存标头
    '''
    resp = flask.make_response(*args)
    resp.headers['Cache-Control'] = 'max-age=86400, must-revalidate'
    resp.headers['Expires'] = '86400'
    return resp


def no_cache_response(*args):
    '''
    给返回添加阻止缓存标头
    '''
    resp = flask.make_response(*args)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


def require_secret(view_func):
    '''
    (装饰器) require_secret, 用于指定函数需要 secret 鉴权
    - ***请确保修饰器紧跟函数定义，如:***
    ```
    @app.route('/set')
    @u.require_secret
    def set_normal(): ...
    ```
    '''
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # 1. body
        # -> {"secret": "my-secret"}
        body: dict = flask.request.get_json(silent=True) or {}
        if body and body.get('secret') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Body')
            return view_func(*args, **kwargs)

        # 2. param
        # -> ?secret=my-secret
        elif flask.request.args.get('secret') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Param')
            return view_func(*args, **kwargs)

        # 3. header (Sleepy-Secret)
        # -> Sleepy-Secret: my-secret
        elif flask.request.headers.get('Sleepy-Secret') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Header (Sleepy-Secret)')
            return view_func(*args, **kwargs)

        # 4. header (Authorization)
        # -> Authorization: Bearer my-secret
        elif flask.request.headers.get('Authorization', '')[7:] == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Header (Authorization)')
            return view_func(*args, **kwargs)

        # 5. cookie (sleepy-token)
        # -> Cookie: sleepy-token=my-secret
        elif flask.request.cookies.get('sleepy-token') == flask.g.secret:
            l.debug('[Auth] Verify secret Success from Cookie (sleepy-token)')
            return view_func(*args, **kwargs)

        # -1. no any secret
        else:
            l.debug('[Auth] Verify secret Failed')
            return {
                'success': False,
                'code': 'not authorized',
                'message': 'wrong secret'
            }, 401
    return wrapped_view


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


def tobool(string, throw: bool = False) -> bool | None:
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
        'x': False,
        'none': False
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


def relative_path(path: str) -> str:
    '''
    绝对路径 -> 相对路径
    '''
    return os.path.relpath(path)


def perf_counter():
    '''
    获取一个性能计数器, 执行返回函数来结束计时, 并返回保留两位小数的毫秒值
    '''
    start = time.perf_counter()
    return lambda: round((time.perf_counter() - start)*1000, 2)


def process_env_split(keys: list[str], value: str) -> dict:
    '''
    处理环境变量配置项分割
    - `page_name=wyf9` -> `['page', 'name'], 'wyf9'` -> `{'page': {'name': 'wyf9'}, 'page_name': 'wyf9'}`
    '''
    if len(keys) == 1:
        return {keys[0]: value}
    else:
        sub_dict = process_env_split(keys[1:], value)
        result = {
            keys[0]: sub_dict,
            '_'.join(keys): value,
            keys[0] + '_' + keys[1]: sub_dict[keys[1]]
        }
        return result


def deep_merge_dict(*dicts: dict) -> dict:
    '''
    递归合并多个嵌套字典 (先后顺序) \n
    例:
    ```
    >>> dict1 = {'a': {'x': 1}, 'b': 2, 'n': 1}
    >>> dict2 = {'a': {'y': 3}, 'c': 4, 'n': 2}
    >>> dict3 = {'a': {'z': 5}, 'd': 6, 'n': 3}
    >>> print(deep_merge_dict(dict1, dict2, dict3))
    {'a': {'z': 5, 'x': 1, 'y': 3}, 'b': 2, 'n': 3, 'c': 4, 'd': 6}
    ```
    '''
    if not dicts:
        return {}

    # 创建基础字典的深拷贝（避免修改原始输入）
    base = {}
    for d in dicts:
        if d:  # 跳过空字典
            base.update(d.copy())

    # 递归合并所有字典
    for d in dicts:
        for key, value in d.items():
            # 如果当前键存在于基础字典且双方值都是字典，则递归合并
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # 递归合并嵌套字典
                base[key] = deep_merge_dict(base[key], value)
            else:
                # 直接赋值（覆盖原有值）
                base[key] = value

    return base
