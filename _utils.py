# coding: utf-8
# 存放 utils.py 和 config.py 都使用到的函数

from pathlib import Path
import os


class SleepyException(Exception):
    '''
    Custom Exception for sleepy
    '''

    def __init__(self, msg: str | None = None):
        if msg:
            self.msg = msg

    def __str__(self):
        return self.msg


def tobool(string: str, throw: bool = False) -> bool | None:
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
            raise ValueError
        else:
            ret = None
    return ret


def current_dir() -> str:
    '''
    获取当前主程序所在目录
    '''
    return str(Path(__file__).parent)


def get_path(path: str) -> str:
    '''
    相对路径 (基于主程序目录) -> 绝对路径
    '''
    if current_dir().startswith('/var/task') and path == 'data.json':
        # 适配 Vercel 部署 (调整 data.json 路径为可写的 /tmp/)
        return '/tmp/sleepy_data.json'
    else:
        return str(Path(__file__).parent.joinpath(path))


def list_dir(path: str | Path, include_subfolder: bool = True, strict_exist: bool = False, ext: str = '') -> list:
    '''
    列出目录下的**文件**

    :param path: 目录路径
    :param include_subfolder: 是否包括子目录的文件 *(递归查找)*
    :param strict_exist: 目标目录不存在时是否抛出错误 *(为否则返回空列表)*
    :param ext: 指定文件扩展名 *(只有文件以此结尾才会计入)*
    '''

    try:
        filelst = os.listdir(path)
        for i in filelst:
            fullname_i = Path(path).joinpath(i)
            if os.path.isdir(fullname_i):
                # 为文件夹
                filelst.remove(i)
                if include_subfolder:
                    filelst.extend([
                        i + n if i.endswith('/') or i.endswith('\\') else i + '/' + n
                        for n in list_dir(
                            fullname_i,
                            include_subfolder=include_subfolder,
                            strict_exist=strict_exist,
                            ext=ext
                        )
                    ])
    except FileNotFoundError:
        # 找不到目标文件夹
        if strict_exist:
            raise
        else:
            return []
    else:
        if ext:
            newlst = []
            for i in filelst:
                if i.endswith(ext):
                    newlst.append(i)
            return newlst
        else:
            return filelst
