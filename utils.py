from datetime import datetime
import json
from flask import make_response, Response
from pathlib import Path


def info(log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ℹ️  [Info] {log}")


def infon(log):
    print(f"\n{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ℹ️  [Info] {log}")


def warning(log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ⚠️  [Warning] {log}")


def error(log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ❌  [Error] {log}")


def debug(log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ⚙️  [Debug] {log}")


def format_dict(dic) -> Response:
    '''
    字典 -> Response (内容为格式化后的 json 文本)
    @param dic: 字典
    '''
    response = make_response(
        json.dumps(dic, indent=4, ensure_ascii=False, sort_keys=False, separators=(', ', ': '))
    )
    response.mimetype = 'application/json'
    return response


def reterr(code: int, message: str) -> str:
    '''
    返回错误信息 json

    :param code: 代码
    :param message: 消息
    '''
    ret = {
        'success': False,
        'code': code,
        'message': message
    }
    error(f'{code} - {message}')
    return format_dict(ret)


def tobool(string: str, throw: bool = False) -> bool:
    '''
    将形似 `true`, `1`, `t`, `yes`, `y` 之类的内容转换为布尔值

    :param throw: 控制无匹配项时是否直接抛出错误
    :return: `True` or `False` or `None` (如果不在 `booldict` 内)
    '''
    booldict = {
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
        'active': True,
        'inactive': False,
        'positive': True,
        'negative': False
    }
    try:
        ret = booldict[str(string).lower()]
    except KeyError:
        if throw:
            raise
        else:
            ret = None
    return ret


@property
def show_404() -> str:
    return '<!DOCTYPE HTML>\n<html lang=en>\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>', 404


class SleepyException(Exception):
    '''
    Custom Exception
    '''

    def __init__(self, msg=None):
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


def current_dir() -> str:
    '''
    获取当前主程序所在目录
    '''
    return str(Path(__file__).parent)


def get_path(path: str) -> Path:
    '''
    相对路径 (基于主程序目录) -> 绝对路径
    '''
    if current_dir().startswith('/var/task') and path == 'data.json':
        # 适配 Vercel 部署 (调整 data.json 路径为可写的 /tmp/)
        return '/tmp/sleepy_data.json'
    else:
        return str(Path(__file__).parent.joinpath(path))