from pydantic import BaseModel, PositiveInt

# --- data


class _DeviceModel(BaseModel):
    '''
    单个设备状态
    '''
    show_name: str  # 显示的设备名称
    using: bool  # 是否正在使用
    app_name: str  # 设备正在使用的应用名


class _MetricsModel(BaseModel):
    '''
    metrics 统计信息
    '''
    today_is: str = ""
    month_is: str = ""
    year_is: str = ""
    today: dict[str, int] = {}
    month: dict[str, int] = {}
    year: dict[str, int] = {}
    total: dict[str, int] = {}


class DataModel(BaseModel):
    '''
    数据文件 (data/data.json)
    '''
    status: int = 0  # 当前状态 (status_list 的列表索引)
    device_status: dict[str, _DeviceModel] = {}  # 设备状态列表
    private_mode: bool = False  # 隐私模式 (启用时 device_status 返回空字典)
    last_updated: str = "1970-01-01 08:00:00"  # 最后更新
    metrics: _MetricsModel = _MetricsModel()  # metrics (访问统计) 信息
