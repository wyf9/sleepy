# coding: utf-8
# 存放 utils.py 和 env.py 都使用到的函数

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
