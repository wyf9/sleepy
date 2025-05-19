# 插件后端功能

本文档详细介绍 sleepy 的插件后端功能，包括自定义路由、事件系统和插件生命周期。

## 插件后端基础

要创建一个后端插件，需要在插件的 `plugin.yaml` 文件中设置 `backend: true`，并创建 `__init__.py` 文件作为插件的入口点。

### 插件初始化

每个后端插件都可以定义一个 `init_plugin` 函数，该函数在插件加载时被调用：

```python
def init_plugin(config):
    """
    插件初始化函数

    :param config: 插件配置对象，包含用户配置和系统工具
    :return: 布尔值，表示初始化是否成功
    """
    # 获取插件配置
    message = config.getconf('message')

    # 访问系统工具
    config.u.info(f'[my_plugin] 插件初始化成功，消息: {message}')

    return True
```

### 配置对象

插件初始化函数接收一个配置对象，该对象提供以下功能：

- `getconf(key, default=None)`: 获取插件配置项
- `u`: 工具对象，提供日志记录等功能
  - `u.info(message)`: 记录信息日志
  - `u.error(message)`: 记录错误日志
  - `u.debug(message)`: 记录调试日志
  - `u.exception(message)`: 记录异常并抛出
- `d`: 数据对象，提供对系统数据的访问

## 自定义路由

插件可以添加自定义路由，这些路由会自动注册到 Flask 应用中。有两种类型的路由：

1. **命名空间路由**：路径前缀为 `/plugin/{plugin_name}`，适用于插件特定的功能
2. **全局路由**：无前缀，直接使用定义的路径，适用于需要简洁 URL 的功能

> 注意：关于全局路由的详细信息，请参阅 [global-routes.md](global-routes.md) 文档。

### 定义命名空间路由

使用 `@route` 装饰器定义命名空间路由：

```python
from plugin import route

@route('/hello')
def hello():
    """
    简单的 GET 路由
    访问路径: /plugin/my_plugin/hello
    """
    return {
        'message': 'Hello from my plugin!'
    }

@route('/data', methods=['GET', 'POST'])
def handle_data():
    """
    支持多种 HTTP 方法的路由
    访问路径: /plugin/my_plugin/data
    """
    from flask import request

    if request.method == 'POST':
        data = request.get_json()
        # 处理数据...
        return {
            'success': True,
            'message': 'Data received'
        }
    else:
        # 返回数据...
        return {
            'data': [1, 2, 3]
        }
```

### 路由参数

路由可以包含参数，遵循 Flask 的路由规则：

```python
@route('/user/<user_id>')
def get_user(user_id):
    """
    带参数的路由
    访问路径: /plugin/my_plugin/user/123
    """
    return {
        'user_id': user_id,
        'name': f'User {user_id}'
    }
```

### 返回值处理

路由函数的返回值会自动转换为 JSON 响应：

- 字典会被转换为 JSON 对象
- 列表会被转换为 JSON 数组
- 基本类型（字符串、数字、布尔值）会被转换为相应的 JSON 值

如果需要更复杂的响应处理，可以直接返回 Flask 的 Response 对象：

```python
from flask import Response

@route('/custom-response')
def custom_response():
    return Response('Hello, world!', mimetype='text/plain')
```

## 事件系统

插件可以注册事件处理器，响应系统中的各种事件。

### 注册事件处理器

使用 `@on_event` 装饰器注册事件处理器：

```python
from plugin import on_event

@on_event('app_started')
def on_app_started(plugin_manager):
    """
    应用启动事件处理器

    :param plugin_manager: 插件管理器实例
    """
    print('应用已启动')
    return True

@on_event('status_updated')
def on_status_updated(old_status, new_status):
    """
    状态更新事件处理器

    :param old_status: 旧状态
    :param new_status: 新状态
    """
    print(f'状态已更新: {old_status} -> {new_status}')
    return True
```

### 支持的事件

系统支持以下事件：

1. `app_started`: 应用启动时触发
2. `status_updated`: 状态更新时触发
3. `device_updated`: 设备更新时触发
4. `device_removed`: 设备删除时触发
5. `devices_cleared`: 设备清除时触发
6. `data_saved`: 数据保存时触发
7. `private_mode_changed`: 隐私模式变更时触发

### 定义全局路由

使用 `@global_route` 装饰器定义全局路由：

```python
from plugin import global_route

@global_route('/hello')
def global_hello():
    """
    全局路由
    访问路径: /hello
    """
    return {
        'message': 'Hello from global route!'
    }
```

## 完整示例

以下是一个完整的后端插件示例：

```python
# plugin/my_plugin/__init__.py
from plugin import route, global_route, on_event

# 存储计数器
counter = 0

def init_plugin(config):
    """插件初始化函数"""
    global counter
    counter = config.getconf('initial_count', 0)
    config.u.info(f'[my_plugin] 插件初始化成功，初始计数: {counter}')
    return True

@route('/count')
def get_count():
    """获取当前计数"""
    return {'count': counter}

@route('/increment', methods=['POST'])
def increment_count():
    """增加计数"""
    global counter
    counter += 1
    return {'count': counter}

@global_route('/api/counter')
def global_counter():
    """全局路由示例"""
    return {'count': counter, 'type': 'global'}

@on_event('status_updated')
def on_status_updated(old_status, new_status):
    """状态更新事件处理器"""
    global counter
    counter += 1
    print(f'状态已更新: {old_status} -> {new_status}, 新计数: {counter}')
    return True
```

对应的 `plugin.yaml` 文件：

```yaml
backend: true
frontend: true
config:
  initial_count: 0
```

对应的 `index.html` 文件：

```html
<h3>我的插件</h3>
<p>当前计数: <span id="counter">加载中...</span></p>
<button id="increment-btn">增加计数</button>

<script>
    // 获取计数
    async function getCount() {
        const response = await fetch('/plugin/my_plugin/count');
        const data = await response.json();
        document.getElementById('counter').textContent = data.count;
    }

    // 增加计数
    async function incrementCount() {
        const response = await fetch('/plugin/my_plugin/increment', {
            method: 'POST'
        });
        const data = await response.json();
        document.getElementById('counter').textContent = data.count;
    }

    // 页面加载完成后获取计数
    document.addEventListener('DOMContentLoaded', function() {
        getCount();

        // 绑定按钮点击事件
        document.getElementById('increment-btn').addEventListener('click', incrementCount);
    });
</script>
```
