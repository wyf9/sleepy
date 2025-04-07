# coding: utf-8
import os
from pathlib import Path
from dotenv import load_dotenv

from _utils import tobool

dotenv_filename = str(Path(__file__).parent.joinpath('.env'))
load_dotenv(dotenv_path=dotenv_filename)


def getenv(key: str, default, typeobj: object = str) -> any:
    '''
    获取环境变量

    :param key: 键
    :param typeobj: 类型对象 (str / int / bool)
    :param default: 默认值 (未读取到此项配置时使用)
    '''
    got_value = os.getenv(key)
    if got_value is None:
        return default
    else:
        if typeobj == bool:
            return tobool(got_value)
        return typeobj(got_value)


class _main:
    '''
    (main) 系统基本配置
    '''
    host: str = getenv('sleepy_main_host', '0.0.0.0', str)
    port: int = getenv('sleepy_main_port', 9010, int)
    debug: bool = getenv('sleepy_main_debug', False, bool)
    timezone: str = getenv('sleepy_main_timezone', 'Asia/Shanghai', str)
    checkdata_interval: int = getenv('sleepy_main_checkdata_interval', 30, int)
    secret: str = getenv('SLEEPY_SECRET', '', str)


class _page:
    '''
    (page) 页面内容配置
    '''
    title: str = getenv('sleepy_page_title', 'User Alive?', str)
    desc: str = getenv('sleepy_page_desc', 'User\'s Online Status Page', str)
    favicon: str = getenv('sleepy_page_favicon', '', str)
    user: str = getenv('sleepy_page_user', 'User', str)
    background: str = getenv('sleepy_page_background', 'https://imgapi.siiway.top/image', str)
    learn_more: str = getenv('sleepy_page_learn_more', 'GitHub Repo', str)
    repo: str = getenv('sleepy_page_repo', 'https://github.com/wyf9/sleepy', str)
    more_text: str = getenv('sleepy_page_more_text', '', str)
    hitokoto: bool = getenv('sleepy_page_hitokoto', True, bool)
    canvas: bool = getenv('sleepy_page_canvas', True, bool)
    moonlight: bool = getenv('sleepy_page_moonlight', True, bool)
    lantern: bool = getenv('sleepy_page_lantern', False, bool)
    mplayer: bool = getenv('sleepy_page_mplayer', False, bool)
    zhixue: bool = getenv('sleepy_page_zhixue', False, bool)


class _status:
    '''
    (status) 页面状态显示配置
    '''
    device_slice: int = getenv('sleepy_status_device_slice', 30, int)
    show_loading: bool = getenv('sleepy_status_show_loading', True, bool)
    refresh_interval: int = getenv('sleepy_status_refresh_interval', 5000, int)
    not_using: str = getenv('sleepy_status_not_using', '', str)


class _util:
    '''
    (util) 可选功能
    '''
    metrics: bool = getenv('sleepy_util_metrics', True, bool)
    auto_switch_status: bool = getenv('sleepy_util_auto_switch_status', True, bool)
    steam_legacy_enabled: bool = getenv('sleepy_util_steam_legacy_enabled', False, bool)
    steam_enabled: bool = getenv('sleepy_util_steam_enabled', False, bool)
    steam_key: str = getenv('sleepy_util_steam_key', '', str)
    steam_ids: str = getenv('sleepy_util_steam_ids', '', str)


main = _main()
page = _page()
status = _status()
util = _util()
