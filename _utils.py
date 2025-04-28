# coding: utf-8
# 存放 utils.py 和 env.py 都使用到的函数

from pathlib import Path


def tobool(string: str, throw: bool = False) -> bool:
    '''
    将形似 `true`, `1`, `yes` 之类的内容转换为布尔值

    :param throw: 控制无匹配项时是否直接抛出错误
    :return: `True` or `False` or `None` (如果不在 `booldict` 内)
    '''
    booldict = {
        # 此列表中的项会转换为对应的布尔值
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
    try:
        ret = booldict[str(string).lower()]
    except KeyError:
        if throw:
            raise
        else:
            ret = None
    return ret


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
