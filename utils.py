# coding: utf-8
from datetime import datetime
import json
from flask import make_response, Response

from _utils import *
from config import main as maincfg


def info(*log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ℹ️  [Info]", *log)


def infon(*log):
    print(f"\n{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ℹ️  [Info]", *log)


def warning(*log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ⚠️  [Warning]", *log)


def error(*log):
    print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ❌ [Error]", *log)


def debug(*log):
    if maincfg.debug:
        print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ⚙️  [Debug]", *log)


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
    返回错误信息 json

    :param code: 代码
    :param message: 消息
    '''
    ret = {
        'success': False,
        'code': code,
        'message': message
    }
    error(f'Response: {code} - {message}')
    return format_dict(ret)


def show_404() -> tuple[str, int]:
    return '<!DOCTYPE HTML>\n<html lang=en>\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>', 404


def exception(msg: str) -> SleepyException:
    '''
    抛出 SleepyException

    :param msg: 错误描述
    '''
    raise SleepyException(msg)
