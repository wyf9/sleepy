# Sleepy 插件开发文档

欢迎使用 Sleepy 插件开发文档！本文档将帮助您了解如何开发 Sleepy 插件，扩展系统功能。

## 插件系统概述

Sleepy 的插件系统允许开发者通过插件扩展系统功能，而无需修改核心代码。插件可以：

- 添加新的前端界面元素
- 提供新的后端 API
- 响应系统事件
- 注册全局路由
- 与其他服务集成

## 插件类型

Sleepy 支持两种类型的插件：

1. **前端插件**：提供用户界面元素，显示在主页上
2. **后端插件**：提供 API 和事件处理功能，可以与前端插件配合使用

插件可以同时包含前端和后端功能，也可以只包含其中一种。

## 插件结构

一个典型的插件目录结构如下：

```text
plugin/
  my_plugin/                # 插件目录
    plugin.yaml             # 插件定义文件
    __init__.py             # 后端入口点
    index.html              # 前端入口点
    static/                 # 静态资源目录
      style.css             # CSS 样式
      script.js             # JavaScript 脚本
```

### 插件定义文件

每个插件都需要一个 `plugin.yaml` 文件，定义插件的基本信息和配置：

```yaml
frontend: true              # 是否包含前端功能
backend: true               # 是否包含后端功能
frontend-card: true         # 是否创建卡片 (为是则将 index.html 内容插入到卡片中，为否则插入到网页底部)
config:                     # 插件配置
  # FIXME
  # title: "我的插件"          # 插件标题
  # description: "这是一个示例插件" # 插件描述
  # 其他配置项...
```

## 开发文档索引

### 基础文档

- [前端插件开发](frontend.md) - 学习如何开发插件的前端部分
- [后端插件开发](backend.md) - 学习如何开发插件的后端部分

### 高级功能

- [全局路由](global-routes.md) - 学习如何使用插件注册全局路由
- [管理后台卡片](admin-cards.md) - 学习如何在管理后台添加自定义卡片

## 快速入门

### 1. 创建插件目录

在 `plugin` 目录下创建一个新的目录，命名为您的插件名称：

```bash
mkdir -p plugin/my_plugin
```

### 2. 创建插件定义文件

创建 `plugin.yaml` 文件：

```yaml
frontend: true
backend: true
config:
  title: "我的第一个插件"
  description: "这是一个示例插件"
```

### 3. 创建前端入口点

创建 `index.html` 文件：

```html
<h3>{{ c.title }}</h3>
<p>{{ c.description }}</p>
<div id="my-plugin-content">
  <p>这是我的第一个插件！</p>
</div>
```

### 4. 创建后端入口点

创建 `__init__.py` 文件：

```python
from plugin import route, on_event

def init_plugin(config):
    """插件初始化函数"""
    config.u.info(f'[my_plugin] 插件初始化成功')
    return True

@route('/hello')
def hello():
    """简单的 API 路由"""
    return {
        'message': 'Hello from my plugin!'
    }

@on_event('app_started')
def on_app_started(plugin_manager):
    """应用启动事件处理器"""
    print('应用已启动，我的插件已加载')
    return True
```

### 5. 启用插件

在 `data/config.yaml` 或 `data/config.toml` 文件中启用您的插件：

```yaml
plugin_enabled:
  - my_plugin
```

## 最佳实践

1. **命名空间隔离**：使用唯一的类名或 ID 前缀，避免与其他插件冲突
2. **模块化代码**：将代码分割为小的、可维护的模块
3. **错误处理**：添加适当的错误处理，提高用户体验
4. **文档**：为您的插件提供清晰的文档，说明如何安装和使用
5. **配置选项**：提供合理的配置选项，允许用户自定义插件行为

## 示例插件

Sleepy 提供了几个示例插件，您可以参考它们来学习插件开发：

1. **test** - 一个简单的测试插件，展示基本功能
2. **custom_html** - 允许用户在页面上显示自定义 HTML 内容
3. **global_route_example** - 演示全局路由功能的示例插件
4. **admin_card_example** - 演示管理后台卡片功能的示例插件

## 获取帮助

如果您在开发插件时遇到问题，可以：

1. 查阅详细的开发文档
2. 参考示例插件的代码
3. 在 GitHub 上提交 Issue

祝您开发愉快！
