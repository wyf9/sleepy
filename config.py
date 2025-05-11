# coding: utf-8
import os

from dotenv import load_dotenv
import yaml

from _utils import tobool, get_path, SleepyException, list_dir

# ===== prepare env =====

load_dotenv(dotenv_path=get_path('.env'))


def getenv(key: str, typeobj) -> ...:
    '''
    获取环境变量
    - 请使用 `get()` 获取配置项，并由 `get()` 调用此函数

    :param key: 键
    :param typeobj: 类型对象 (str / int / bool)
    '''
    got_value = os.getenv(key)
    if got_value is None:
        raise KeyError
    else:
        if typeobj == bool:
            return tobool(got_value, throw=True)
        else:
            return typeobj(got_value)


# ===== prepare yaml =====

if os.path.exists(get_path('config.yaml')):
    # load user config
    with open(get_path('config.yaml'), 'r', encoding='utf-8') as f:
        user_config = yaml.safe_load(f)
        f.close()
else:
    user_config = {}
# load example config
with open(get_path('config.example.yaml'), 'r', encoding='utf-8') as f:
    example_config = yaml.safe_load(f)
    f.close()


def get(_type, *key: str) -> ...:
    '''
    获取配置项 
    - 顺序: `config.yaml` -> 环境变量 -> `.env` -> `config.example.yaml`

    :param _type: 配置项的类型
    :param *key: 配置项名
    :param load_env: 是否允许从 .env 加载 (列表 / 字典需设置为否)
    '''
    # 1. from user config
    try:
        value = user_config
        for k in key:
            value = value[k]
        assert isinstance(value, _type), SleepyException(f'Invaild config {".".join(key)} from config.yaml, it should be a(n) {_type.__name__} object.')  # verify config type
        return value
    except KeyError:
        pass

    # 2. from user env
    envname = f'sleepy_{"_".join(key)}'
    try:
        if _type in (str, int, float, bool):
            value = getenv(envname, typeobj=_type)
            return value
    except KeyError:
        pass
    except ValueError:
        raise SleepyException(f'Invaild config {envname} from environment or .env, it should be a(n) {_type.__name__} object.')

    # 3. from example config
    try:
        value = example_config
        for k in key:
            value = value[k]
        return value
    except KeyError:
        raise SleepyException(f'Config {envname} (should be a(n) {_type.__name__}) not found in config.example.yaml!')

# ===== system config =====


class Config:
    '''
    用户配置
    '''

    class _main:
        '''
        (main) 系统基本配置
        '''
        _ = 'main'
        host: str = get(str, _, 'host')
        port: int = get(int, _, 'port')
        debug: bool = get(bool, _, 'debug')
        timezone: str = get(str, _, 'timezone')
        checkdata_interval: int = get(int, _, 'checkdata_interval')
        secret: str = get(str, _, 'secret')

    class _page:
        '''
        (page) 页面内容配置
        '''
        _ = 'page'
        name: str = get(str, _, 'name')
        title: str = get(str, _, 'title')
        desc: str = get(str, _, 'desc')
        favicon: str = get(str, _, 'favicon')
        background: str = get(str, _, 'background')
        learn_more_text: str = get(str, _, 'learn_more_text')
        learn_more_link: str = get(str, _, 'learn_more_link')
        more_text: str = get(str, _, 'more_text')

        # to plugins
        # hitokoto: bool = getenv('sleepy_page_hitokoto', True, bool)
        # canvas: bool = getenv('sleepy_page_canvas', True, bool)
        # moonlight: bool = getenv('sleepy_page_moonlight', True, bool)
        # lantern: bool = getenv('sleepy_page_lantern', False, bool)
        # mplayer: bool = getenv('sleepy_page_mplayer', False, bool)
        # zhixue: bool = getenv('sleepy_page_zhixue', False, bool)

    class _status:
        '''
        (status) 页面状态显示配置
        '''
        _ = 'status'
        device_slice: int = get(int, _, 'device_slice')
        refresh_interval: int = get(int, _, 'refresh_interval')
        not_using: str = get(str, _, 'not_using')
        sorted: bool = get(bool, _, 'sorted')
        using_first: bool = get(bool, _, 'using_first')
        status_list: list[dict] = get(list, _, 'status_list')

    class _metrics:
        '''
        (metrics) 调用统计
        '''
        _ = 'metrics'
        enabled: bool = get(bool, _, 'enabled')
        allow_list: list[str] = get(list, _, 'allow_list')

        # to plugins
        # auto_switch_status: bool = getenv('sleepy_util_auto_switch_status', True, bool)
        # steam_enabled: bool = getenv('sleepy_util_steam_enabled', False, bool)
        # steam_ids: str = getenv('sleepy_util_steam_ids', '', str)
        # steam_refresh_interval: int = getenv('sleepy_util_steam_refresh_interval', 20000, int)

    main = _main()
    page = _page()
    status = _status()
    metrics = _metrics()

    # status_list 中自动补全 id
    for i in range(len(status.status_list)):
        status.status_list[i]['id'] = i

    # metrics_list 中 [static] 处理
    if '[static]' in metrics.allow_list:
        metrics.allow_list.remove('[static]')
        static_list = list_dir(get_path('static/'))
        metrics.allow_list.extend(['/static/' + i for i in static_list])

    # ===== plugin config =====

    plugin_enabled: list[str] = get(list, 'plugin_enabled')
    plugin: dict[str, dict] = get(dict, 'plugin')
