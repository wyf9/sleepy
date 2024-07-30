from datetime import datetime
import json
import os


def info(log):
    print(f"[Info] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def infon(log):
    print(f"\n[Info] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def warning(log):
    print(f"[Warning] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def error(log):
    print(f"[Error] {datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} " + log)


def format_dict(dic):
    '''
    列表 -> 格式化 json
    @param dic: 列表
    '''
    return json.dumps(dic, indent=4, ensure_ascii=False, sort_keys=False, separators=(', ', ': '))
