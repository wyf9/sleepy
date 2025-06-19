# 插件全局路由功能

本文档详细介绍 sleepy 的插件全局路由功能，允许插件注册和覆盖全局路径。

## 全局路由基础

全局路由允许插件注册不带插件命名空间前缀的路由，例如 `/hello` 而不是 `/plugin/my_plugin/hello`。这使得插件可以提供更简洁的 API 路径，或者覆盖系统默认路由。

### 注册全局路由

使用 `@global_route` 装饰器注册全局路由：

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

### 全局路由与命名空间路由的区别

1. **路径前缀**：
   - 命名空间路由：`/plugin/{plugin_name}{rule}`
   - 全局路由：`{rule}`

2. **使用场景**：
   - 命名空间路由适用于插件特定的功能，避免与其他插件冲突
   - 全局路由适用于需要简洁 URL 的功能，或需要覆盖系统路由的场景

### 路由参数和HTTP方法

全局路由支持与命名空间路由相同的功能，包括路由参数和多种 HTTP 方法：

```python
@global_route('/greet/<name>')
def global_greet(name):
    """
    带参数的全局路由
    访问路径: /greet/{name}
    """
    return {
        'message': f'Hello, {name}!'
    }

@global_route('/api/data', methods=['GET', 'POST'])
def global_data():
    """
    支持多种HTTP方法的全局路由
    访问路径: /api/data
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

## 注意事项

### 路由冲突

全局路由可能与系统路由或其他插件的全局路由冲突。在这种情况下，后注册的路由会覆盖先注册的路由。请谨慎使用全局路由，避免不必要的冲突。

### 安全考虑

全局路由可能会影响系统的核心功能。在使用全局路由时，请确保：

1. 不要覆盖关键系统路由，如 `/`, `/set`, `/query` 等
2. 为路由添加适当的权限控制，避免未授权访问（例如：使用 `@u.require_secret` 修饰器）
3. 在插件配置中提供禁用全局路由的选项

## 完整示例

以下是一个完整的全局路由插件示例。
这个示例插件名为 `global_route_example`，演示了如何使用全局路由功能。可以在 `plugin/global_route_example` 目录下找到。

```python
# plugin/global_route_example/__init__.py
from flask import request
from plugin import route, global_route

# 存储访问计数
_counters = {
    'namespace_route': 0,
    'global_route': 0
}

def init_plugin(config):
    """插件初始化函数"""
    message = config.getconf('message')
    routes_enabled = config.getconf('routes_enabled')

    config.u.info(f'[global_route_example] 插件初始化成功，消息: {message}')
    config.u.info(f'[global_route_example] 路由启用状态: {routes_enabled}')

    return True

# 插件命名空间下的路由
@route('/hello')
def plugin_hello():
    _counters['namespace_route'] += 1
    return {
        'message': 'Hello from plugin namespace route!',
        'counter': _counters['namespace_route']
    }

# 全局路由
@global_route('/hello')
def global_hello():
    _counters['global_route'] += 1
    return {
        'message': 'Hello from global route!',
        'counter': _counters['global_route']
    }

# 带参数的全局路由
@global_route('/greet/<name>')
def global_greet(name):
    return {
        'message': f'Hello, {name}!',
        'from': 'global_route_example plugin'
    }
```

对应的 `plugin.yaml` 文件：

```yaml
frontend: true
backend: true
config:
  message: "这是一个全局路由示例插件"
  routes_enabled: true
```
