# coding: utf-8
from datetime import datetime
import json
from flask import make_response, Response

from config import Config
import _utils

class Utils:
    '''
    实用工具
    '''

    def __init__(self, config: Config):
        '''
        :param config: 用户配置对象
        '''
        self.c = config

    def info(self, *log):
        print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ℹ️  [Info]", *log)

    def infon(self, *log):
        print(f"\n{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ℹ️  [Info]", *log)

    def warning(self, *log):
        print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ⚠️  [Warning]", *log)

    def error(self, *log):
        print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ❌ [Error]", *log)

    def debug(self, *log):
        if self.c.main.debug:
            print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} ⚙️  [Debug]", *log)

    def format_dict(self, dic: dict | list) -> Response:
        '''
        字典 -> Response (内容为格式化后的 json 文本) \n
        @param dic: 字典
        '''
        response = make_response(
            json.dumps(dic, indent=4, ensure_ascii=False, sort_keys=False, separators=(', ', ': '))
        )
        response.mimetype = 'application/json'
        return response

    def reterr(self, code: str, message: str) -> Response:
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
        self.error(f'Response: {code} - {message}')
        return self.format_dict(ret)

    def show_404(self) -> tuple[str, int]:
        return '<!DOCTYPE HTML>\n<html lang=en>\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>', 404

    def exception(self, msg: str) -> _utils.SleepyException:
        '''
        抛出 SleepyException

        :param msg: 错误描述
        '''
        raise _utils.SleepyException(msg)
