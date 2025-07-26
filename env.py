# coding: utf-8
import os
from typing import Any, Callable

from dotenv import load_dotenv

from _utils import tobool, get_path

load_dotenv(dotenv_path=get_path('.env'))


def getenv(key: str, default: Any, typeobj: Callable) -> Any:
    '''
    获取环境变量

    :param key: 键
    :param default: 默认值 (未读取到此项配置时使用)
    :param typeobj: 类型对象 (str / int / bool)
    '''
    got_value = os.getenv(key.lower()) or os.getenv(key.upper()) # 全大写 / 全小写皆可
    if got_value is None:
        return default
    else:
        if typeobj == bool:
            return tobool(got_value)
        ret = typeobj(got_value)
        return ret


class _main:
    '''
    (main) 系统基本配置
    '''
    host: str = getenv('sleepy_main_host', '0.0.0.0', str)
    port: int = getenv('sleepy_main_port', 9010, int)
    debug: bool = getenv('sleepy_main_debug', False, bool)
    timezone: str = getenv('sleepy_main_timezone', 'Asia/Shanghai', str)
    checkdata_interval: int = getenv('sleepy_main_checkdata_interval', 30, int)
    secret: str = getenv('sleepy_secret', '', str)
    https_enabled: bool = getenv('sleepy_main_https_enabled', False, bool)
    ssl_cert: str = getenv('sleepy_main_ssl_cert', 'cert.pem', str)
    ssl_key: str = getenv('sleepy_main_ssl_key', 'key.pem', str)


class _page:
    '''
    (page) 页面内容配置
    '''
    user: str = getenv('sleepy_page_user', 'User', str)
    title: str = getenv('sleepy_page_title', f'{user} Alive?', str)
    desc: str = getenv('sleepy_page_desc', f'{user}\'s Online Status Page', str)
    favicon: str = getenv('sleepy_page_favicon', './static/favicon.ico', str)
    background: str = getenv('sleepy_page_background', 'https://imgapi.siiway.top/image', str)
    learn_more: str = getenv('sleepy_page_learn_more', 'GitHub Repo', str)
    repo: str = getenv('sleepy_page_repo', 'https://github.com/sleepy-project/sleepy', str)
    more_text: str = getenv('sleepy_page_more_text', '', str)
    sorted: bool = getenv('sleepy_page_sorted', False, bool)
    using_first: bool = getenv('sleepy_page_using_first', False, bool)
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
    steam_enabled: bool = getenv('sleepy_util_steam_enabled', False, bool)
    steam_api_url: str = getenv('sleepy_util_steam_api_url', 'https://steam-miniprofile-proxy.wyf9.top/miniprofile/', str)
    steam_ids: str = getenv('sleepy_util_steam_ids', '', str)
    steam_refresh_interval: int = getenv('sleepy_util_steam_refresh_interval', 20000, int)


main = _main()
page = _page()
status = _status()
util = _util()
