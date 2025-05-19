# coding: utf-8

from plugin import route, admin_card
import json

def init_plugin(config):
    """
    插件初始化函数
    
    :param config: 插件配置对象
    """
    # 获取插件配置
    message = config.getconf('settings.message')
    count = config.getconf('settings.count')
    enabled = config.getconf('settings.enabled')
    
    # 打印调试信息
    config.u.info(f'[admin_card_example] 插件初始化成功')
    config.u.info(f'[admin_card_example] 配置: message={message}, count={count}, enabled={enabled}')
    
    return True

# 简单信息卡片
@admin_card("系统信息", order=10)
def system_info_card(config):
    """
    系统信息卡片
    
    :param config: 插件配置对象
    :return: 卡片内容
    """
    import platform
    import os
    
    # 获取系统信息
    system_info = {
        "系统": platform.system(),
        "版本": platform.version(),
        "Python版本": platform.python_version(),
        "处理器": platform.processor() or "未知",
        "主机名": platform.node(),
        "工作目录": os.getcwd()
    }
    
    # 构建卡片内容
    content = "<div class='system-info'>"
    for key, value in system_info.items():
        content += f"<div class='info-item'><span class='info-label'>{key}:</span> <span class='info-value'>{value}</span></div>"
    content += "</div>"
    
    # 添加一些样式
    content += """
    <style>
    .system-info {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
        padding: 15px;
    }
    .info-item {
        margin-bottom: 8px;
        display: flex;
    }
    .info-label {
        font-weight: bold;
        min-width: 120px;
    }
    .info-value {
        font-family: monospace;
    }
    </style>
    """
    
    return content

# 设置卡片
@admin_card("插件设置", order=20)
def settings_card(config):
    """
    插件设置卡片
    
    :param config: 插件配置对象
    :return: 卡片内容
    """
    # 获取当前设置
    message = config.getconf('settings.message')
    count = config.getconf('settings.count')
    enabled = config.getconf('settings.enabled')
    
    # 构建卡片内容
    content = """
    <div class="settings-form">
        <div class="form-group">
            <label for="message">消息:</label>
            <input type="text" id="message" value="{{ message }}" />
        </div>
        <div class="form-group">
            <label for="count">计数:</label>
            <input type="number" id="count" value="{{ count }}" min="1" max="100" />
        </div>
        <div class="form-group">
            <label for="enabled">启用:</label>
            <input type="checkbox" id="enabled" {% if enabled %}checked{% endif %} />
        </div>
        <div class="form-actions">
            <button id="save-settings" class="btn btn-primary">保存设置</button>
            <button id="reset-settings" class="btn btn-secondary">重置</button>
        </div>
    </div>
    
    <script>
    document.getElementById('save-settings').addEventListener('click', async function() {
        const message = document.getElementById('message').value;
        const count = parseInt(document.getElementById('count').value);
        const enabled = document.getElementById('enabled').checked;
        
        try {
            const response = await fetch('/plugin/admin_card_example/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    count,
                    enabled
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('设置已保存');
            } else {
                alert('保存失败: ' + data.message);
            }
        } catch (error) {
            alert('保存失败: ' + error.message);
        }
    });
    
    document.getElementById('reset-settings').addEventListener('click', function() {
        document.getElementById('message').value = '{{ message }}';
        document.getElementById('count').value = '{{ count }}';
        document.getElementById('enabled').checked = {{ 'true' if enabled else 'false' }};
    });
    </script>
    """
    
    # 渲染模板变量
    content = content.replace('{{ message }}', message)
    content = content.replace('{{ count }}', str(count))
    content = content.replace('{{ enabled }}', str(enabled).lower())
    content = content.replace("{{ 'true' if enabled else 'false' }}", 'true' if enabled else 'false')
    
    return content

# 设置保存路由
@route('/settings', methods=['POST'])
def save_settings():
    """
    保存插件设置
    
    :return: 操作结果
    """
    from flask import request
    import _utils
    
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return {'success': False, 'message': '无效的请求数据'}
        
        # 获取设置值
        message = data.get('message', '')
        count = int(data.get('count', 5))
        enabled = bool(data.get('enabled', True))
        
        # 验证设置值
        if not message:
            return {'success': False, 'message': '消息不能为空'}
        
        if count < 1 or count > 100:
            return {'success': False, 'message': '计数必须在1-100之间'}
        
        # 更新配置文件
        config_path = _utils.get_path('data/config.yaml')
        
        try:
            import yaml
            
            # 读取当前配置
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 确保插件配置存在
            if 'plugin' not in config:
                config['plugin'] = {}
            
            if 'admin_card_example' not in config['plugin']:
                config['plugin']['admin_card_example'] = {}
            
            if 'settings' not in config['plugin']['admin_card_example']:
                config['plugin']['admin_card_example']['settings'] = {}
            
            # 更新设置
            config['plugin']['admin_card_example']['settings']['message'] = message
            config['plugin']['admin_card_example']['settings']['count'] = count
            config['plugin']['admin_card_example']['settings']['enabled'] = enabled
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': f'保存配置失败: {e}'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
