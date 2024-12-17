from datetime import datetime
import json
from flask import make_response, Response


def info(log):
    print(f"[Info] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def infon(log):
    print(f"\n[Info] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def warning(log):
    print(f"[Warning] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def error(log):
    print(f"[Error] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def format_dict(dic) -> Response:
    '''
    列表 -> 格式化 json
    @param dic: 列表
    '''
    # return jsonify(dic, ensure_ascii = False)
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
