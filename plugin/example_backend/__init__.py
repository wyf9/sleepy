# coding: utf-8

from datetime import datetime
import pytz
from plugin import route, on_event

# 存储事件日志
_events = []
_max_events = 20  # 最多保存的事件数量

def init_plugin(config):
    """
    插件初始化函数
    
    :param config: 插件配置对象
    """
    # 获取插件配置
    message = config.getconf('message')
    log_events = config.getconf('log_events')
    
    # 记录初始化事件
    if log_events:
        _add_event('init', f'插件初始化成功，消息: {message}')
    
    # 打印调试信息
    config.u.info(f'[example_backend] 插件初始化成功，消息: {message}')
    
    return True

def _add_event(event_type, message):
    """
    添加事件到日志
    
    :param event_type: 事件类型
    :param message: 事件消息
    """
    global _events
    
    # 获取当前时间
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 添加事件
    _events.append({
        'time': now,
        'type': event_type,
        'message': message
    })
    
    # 限制事件数量
    if len(_events) > _max_events:
        _events = _events[-_max_events:]

# 路由处理函数
@route('/status')
def get_status():
    """
    获取插件状态
    """
    return {
        'success': True,
        'message': '插件正常运行中',
        'events': _events,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# 事件处理函数
@on_event('app_started')
def on_app_started(plugin_manager):
    """
    应用启动事件处理
    
    :param plugin_manager: 插件管理器实例
    """
    _add_event('app_started', '应用已启动')
    return True

@on_event('status_updated')
def on_status_updated(old_status, new_status):
    """
    状态更新事件处理
    
    :param old_status: 旧状态
    :param new_status: 新状态
    """
    _add_event('status_updated', f'状态已更新: {old_status} -> {new_status}')
    return True

@on_event('device_updated')
def on_device_updated(device_id, device_info):
    """
    设备更新事件处理
    
    :param device_id: 设备ID
    :param device_info: 设备信息
    """
    _add_event('device_updated', f'设备已更新: {device_id}, 应用: {device_info.get("app_name", "未知")}')
    return True

@on_event('device_removed')
def on_device_removed(device_id, device_info):
    """
    设备删除事件处理
    
    :param device_id: 设备ID
    :param device_info: 设备信息
    """
    _add_event('device_removed', f'设备已删除: {device_id}')
    return True

@on_event('devices_cleared')
def on_devices_cleared(old_devices):
    """
    设备清除事件处理
    
    :param old_devices: 旧设备列表
    """
    _add_event('devices_cleared', f'所有设备已清除，共 {len(old_devices)} 个设备')
    return True

@on_event('data_saved')
def on_data_saved(data):
    """
    数据保存事件处理
    
    :param data: 保存的数据
    """
    _add_event('data_saved', '数据已保存')
    return True

@on_event('private_mode_changed')
def on_private_mode_changed(old_mode, new_mode):
    """
    隐私模式变更事件处理
    
    :param old_mode: 旧模式
    :param new_mode: 新模式
    """
    _add_event('private_mode_changed', f'隐私模式已变更: {old_mode} -> {new_mode}')
    return True
