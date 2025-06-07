# coding: utf-8

from flask import request, jsonify
from plugin import route, global_route, on_event

# 存储访问计数
_counters = {
    'namespace_route': 0,
    'global_route': 0
}

def init_plugin(config):
    """
    插件初始化函数
    
    :param config: 插件配置对象
    """
    # 获取插件配置
    message = config.getconf('message')
    routes_enabled = config.getconf('routes_enabled')
    
    # 打印调试信息
    config.u.info(f'[global_route_example] 插件初始化成功，消息: {message}')
    config.u.info(f'[global_route_example] 路由启用状态: {routes_enabled}')
    
    return True

# 插件命名空间下的路由
@route('/hello')
def plugin_hello():
    """
    插件命名空间下的路由
    访问路径: /plugin/global_route_example/hello
    """
    _counters['namespace_route'] += 1
    return {
        'message': 'Hello from plugin namespace route!',
        'counter': _counters['namespace_route']
    }

# 全局路由
@global_route('/hello')
def global_hello():
    """
    全局路由
    访问路径: /hello
    """
    _counters['global_route'] += 1
    return {
        'message': 'Hello from global route!',
        'counter': _counters['global_route']
    }

# 带参数的全局路由
@global_route('/greet/<name>')
def global_greet(name):
    """
    带参数的全局路由
    访问路径: /greet/{name}
    """
    return {
        'message': f'Hello, {name}!',
        'from': 'global_route_example plugin'
    }

# 支持多种HTTP方法的全局路由
@global_route('/api/data', methods=['GET', 'POST'])
def global_data():
    """
    支持多种HTTP方法的全局路由
    访问路径: /api/data
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        return {
            'success': True,
            'message': 'Data received',
            'data': data
        }
    else:
        return {
            'success': True,
            'message': 'GET request received',
            'counters': _counters
        }

# 事件处理函数
@on_event('app_started')
def on_app_started(plugin_manager):
    """
    应用启动事件处理
    """
    return True
