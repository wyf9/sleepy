# coding: utf-8

from typing import Any

from pydantic import BaseModel, PositiveInt

# --- config


class _StatusItemModel(BaseModel):
    '''
    状态列表设置 (`status.status_list`) 中的项
    '''

    id: int = -1
    '''
    状态索引 (id)
    - *应由 `config.Config.__init__()` 动态设置*
    '''

    name: str
    '''
    状态名称
    '''

    desc: str
    '''
    状态描述
    '''

    color: str = 'awake'
    '''
    状态颜色 \n
    对应 `static/style.css` 中的 `.sleeping` `.awake` 等类 (可自行前往修改)
    '''


class _MainConfigModel(BaseModel):
    '''
    系统基本配置 (`main`)
    '''

    host: str = '0.0.0.0'
    '''
    监听地址
    - ipv4: `0.0.0.0` 表示监听所有接口
    - ipv6: `::` 表示监听所有接口
    '''

    port: PositiveInt = 9010
    '''
    服务监听端口 \n
    默认为 `9010`
    '''

    debug: bool = False
    '''
    是否启用 Flask 调试模式 \n
    (普通用户无需更改)
    '''

    log_file: str = ''
    '''
    保存日志文件目录 (留空禁用) \n
    如: `data/running.log` \n
    **注意: 不会自动切割日志**
    '''

    timezone: str = 'Asia/Shanghai'
    '''
    控制网页 / API 返回中时间的时区 \n
    默认: `Asia/Shanghai` (北京时间)
    '''

    checkdata_interval: PositiveInt = 120
    '''
    多久检查一次数据是否有更改 (秒)
    - *建议设置为 2 ~ 5 分钟 (120s ~ 300s)*
    '''

    secret: str = ''
    '''
    密钥, 更新状态时需要 \n
    **请勿泄露, 相当于密码!!!**
    '''

    cache_age: PositiveInt = 600
    '''
    静态资源缓存时间 (秒)
    - *建议设置为 10 分钟 (60s)*
    '''


class _PageConfigModel(BaseModel):
    '''
    页面内容配置 (`page`)
    '''

    name: str = 'User'
    '''
    你的名字
    - 将显示在网页中 `[User]'s Status:`
    '''

    title: str = 'User Alive?'
    '''
    页面标题 (`<title>`)
    '''

    desc: str = 'User \'s Online Status Page'
    '''
    页面详情 (用于 SEO, 或许吧)
    - *`<meta name="description">`*
    '''
    favicon: str = '/static/favicon.ico'
    '''
    页面图标 (favicon) url, 默认为 /static/favicon.ico
    - *可为绝对路径 / 相对路径 url*
    '''

    background: str = 'https://imgapi.siiway.top/image'
    '''
    背景图片 url / api
    - *默认为 imgapi.siiway.top (https://github.com/siiway/imgapi)*
    '''

    learn_more_text: str = 'GitHub Repo'
    '''
    更多信息链接的提示
    - *默认为 `GitHub Repo`*
    '''

    learn_more_link: str = 'https://github.com/sleepy-project/sleepy'
    '''
    更多信息链接的目标, 默认为本仓库链接
    '''

    more_text: str = ''
    '''
    内容将在状态页底部 learn_more 上方插入 (不转义)
    - *你可以在此中插入 统计代码 / 备案号 等信息*
    '''

    theme: str = 'default'
    '''
    设置页面的默认主题
    - 主题名即为 `theme/` 下的文件夹名
    '''


class _StatusConfigModel(BaseModel):
    '''
    状态配置 (`status`)
    '''

    device_slice: PositiveInt = 50
    '''
    设备状态从开头截取多少文字显示 (防止窗口标题过长影响页面显示)
    - *设置为 0 禁用*
    '''

    refresh_interval: PositiveInt = 5000
    '''
    网页多久刷新一次状态 (毫秒) \n
    *仅在回退到原始轮询方式后使用*
    '''

    not_using: str = '未在使用'
    '''
    锁定设备未在使用时的提示 *(如为空则使用设备提交值)*
    '''

    sorted: bool = False
    '''
    控制是否对设备进行排序 *(A-Z, 0-9)*
    '''

    using_first: bool = False
    '''
    控制是否优先显示正在使用设备
    '''

    status_list: list[_StatusItemModel] = []
    '''
    手动设置的状态列表
    - *见 `_StatusItemModel`*
    '''


class _MetricsConfigModel(BaseModel):
    '''
    统计配置 (`metrics`)
    '''

    enabled: bool = True
    '''
    是否启用统计功能
    '''

    allow_list: list[str] = [
        '/',
        '/style.css',
        '/query',
        '/status_list',
        '/set',
        '/device/set',
        '/device/remove',
        '/device/clear',
        '/device/private_mode',
        '/save_data',
        '/events',
        '/metrics',
        '/robots.txt',
        '[static]'
    ]
    '''
    将计入统计的路径列表 \n
    *其中的 `[static]` 为特殊值, 匹配 static 目录中的所有文件*
    '''


class ConfigModel(BaseModel):
    '''
    用户配置文件 \n
    加载顺序:
    - `data/.env` & 环境变量
    - `data/config.yaml`
    - `data/config.toml`
    '''

    main: _MainConfigModel = _MainConfigModel()
    page: _PageConfigModel = _PageConfigModel()
    status: _StatusConfigModel = _StatusConfigModel()
    metrics: _MetricsConfigModel = _MetricsConfigModel()

    plugins_enabled: list[str] = []
    '''
    启用的插件列表，按从上到下的顺序加载
    '''

    plugin: dict[str, dict[str, Any]] = {}
    '''
    各个插件的配置
    - 键: 字符串, 插件 id *(即文件夹名)*
    - 值: 字典, 插件的配置
    '''

# --- data


class _DeviceModel(BaseModel):
    '''
    单个设备状态
    '''

    show_name: str
    '''
    显示的设备名称
    '''

    using: bool
    '''
    是否正在使用
    '''

    app_name: str
    '''
    设备正在使用的应用名
    '''


class _MetricsModel(BaseModel):
    '''
    metrics 统计信息
    '''

    today_is: str = '0000-00-00'
    '''
    今日日期
    - *`yyyy-mm-dd`*
    '''

    month_is: str = '0000-00'
    '''
    当前月份
    - *`yyyy-mm`*
    '''

    year_is: str = '0000'
    '''
    当前年份
    - *`yyyy`*
    '''

    today: dict[str, int] = {}
    '''
    今日统计数据 (在每日 0 点清除)
    - *`路径`: `计数`*
    '''

    month: dict[str, int] = {}
    '''
    本月统计数据 (在每月 1 日 0 点清除)
    - *`路径`: `计数`*
    '''

    year: dict[str, int] = {}
    '''
    本年统计数据 (在每年 1 月 1 日 0 点清除)
    - *`路径`: `计数`*
    '''

    total: dict[str, int] = {}
    '''
    总统计数据 (永不清除)
    - *`路径`: `计数`*
    '''


class DataModel(BaseModel):
    '''
    数据文件
    - `data/data.json`
    '''

    status: int = 0
    '''
    当前状态 *(即 status_list 中的列表索引)*
    '''

    device_status: dict[str, _DeviceModel] = {}
    '''
    设备状态列表
    - *键: 设备 id*
    - *值: `_DeviceModel`*
    '''

    private_mode: bool = False
    '''
    隐私模式 *(启用时 /query 返回中的 `device` 替换为空字典)*
    '''

    last_updated: str = '1970-01-01 08:00:00'
    '''
    (所有数据的) 最后更新时间
    - *`yyyy-mm-dd hh:mm:ss`*
    '''

    metrics: _MetricsModel = _MetricsModel()
    '''
    metrics (访问统计) 数据
    - *见 `_MetricsModel`*
    '''
