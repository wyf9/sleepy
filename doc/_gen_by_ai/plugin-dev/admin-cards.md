# 插件管理后台卡片功能

本文档详细介绍 sleepy 的插件管理后台卡片功能，允许插件在管理后台添加自定义卡片。

## 管理后台卡片基础

管理后台卡片允许插件在系统管理后台页面添加自定义内容区域，可用于展示信息、提供设置界面或其他管理功能。

### 注册管理后台卡片

使用 `@admin_card` 装饰器注册管理后台卡片：

```python
from plugin import admin_card

@admin_card("系统信息", order=10)
def system_info_card(config):
    """
    系统信息卡片
    
    :param config: 插件配置对象
    :return: 卡片内容
    """
    # 构建卡片内容
    content = "<div>这是一个系统信息卡片</div>"
    return content
```

### 卡片函数参数

`@admin_card` 装饰器接受以下参数：

- `title`：卡片标题，显示在卡片顶部
- `order`：卡片排序顺序，数字越小越靠前（默认为 100）

被装饰的函数必须接受一个 `config` 参数，这是插件的配置对象，可用于获取插件配置。

### 卡片内容

卡片函数应返回一个字符串，表示卡片的 HTML 内容。这个内容将直接插入到管理后台页面中。

卡片内容可以包含：

- HTML 标记
- CSS 样式（建议使用内联样式或 `<style>` 标签）
- JavaScript 代码（使用 `<script>` 标签）

## 卡片内容示例

### 简单信息卡片

```python
@admin_card("系统信息", order=10)
def system_info_card(config):
    import platform
    
    # 获取系统信息
    system_info = {
        "系统": platform.system(),
        "版本": platform.version(),
        "Python版本": platform.python_version()
    }
    
    # 构建卡片内容
    content = "<div class='system-info'>"
    for key, value in system_info.items():
        content += f"<div><strong>{key}:</strong> {value}</div>"
    content += "</div>"
    
    # 添加一些样式
    content += """
    <style>
    .system-info {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
        padding: 15px;
    }
    </style>
    """
    
    return content
```

### 交互式设置卡片

```python
@admin_card("插件设置", order=20)
def settings_card(config):
    # 获取当前设置
    message = config.getconf('settings.message')
    enabled = config.getconf('settings.enabled')
    
    # 构建卡片内容
    content = f"""
    <div class="settings-form">
        <div class="form-group">
            <label for="message">消息:</label>
            <input type="text" id="message" value="{message}" />
        </div>
        <div class="form-group">
            <label for="enabled">启用:</label>
            <input type="checkbox" id="enabled" {"checked" if enabled else ""} />
        </div>
        <div class="form-actions">
            <button id="save-settings" class="btn btn-primary">保存设置</button>
        </div>
    </div>
    
    <script>
    document.getElementById('save-settings').addEventListener('click', async function() {{
        const message = document.getElementById('message').value;
        const enabled = document.getElementById('enabled').checked;
        
        try {{
            const response = await fetch('/plugin/my_plugin/settings', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    message,
                    enabled
                }})
            }});
            
            const data = await response.json();
            
            if (data.success) {{
                alert('设置已保存');
            }} else {{
                alert('保存失败: ' + data.message);
            }}
        }} catch (error) {{
            alert('保存失败: ' + error.message);
        }}
    }});
    </script>
    """
    
    return content
```

## 与 API 路由结合

管理后台卡片通常需要与插件的 API 路由结合使用，以实现数据交互。例如，上面的设置卡片示例需要一个保存设置的 API 路由：

```python
@route('/settings', methods=['POST'])
def save_settings():
    from flask import request
    import yaml
    
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 更新配置文件
        # ...
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}
```

## 样式指南

为了保持管理后台的一致性，建议遵循以下样式指南：

1. 使用 `.plugin-card` 类提供的样式，如表单元素样式
2. 使用半透明背景色（`rgba(255, 255, 255, 0.5)`）
3. 使用圆角边框（`border-radius: 8px`）
4. 使用适当的内边距（`padding: 15px`）
5. 使用系统提供的按钮样式（`.btn`, `.btn-primary`, `.btn-secondary`）

## 注意事项

1. **安全性**：管理后台卡片中的代码只应在用户已通过身份验证的情况下执行
2. **性能**：避免在卡片中加载过多资源或执行复杂计算
3. **错误处理**：添加适当的错误处理，避免卡片内容影响整个管理后台
4. **响应式设计**：确保卡片在不同屏幕尺寸下都能正常显示

## 完整示例

请参考 `plugin/admin_card_example` 插件，它演示了如何在管理后台添加卡片，包括系统信息卡片和设置卡片。
