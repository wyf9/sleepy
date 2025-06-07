# Plugin / 插件

本文档介绍如何使用 sleepy 的插件功能，适合普通用户阅读。

> 注意：如果您是插件开发者，请参阅 [plugin-dev/README.md](plugin-dev/README.md) 获取开发相关信息。

## 什么是插件？

插件是扩展 sleepy 功能的小型模块，可以添加新的显示内容、功能或与其他服务集成。插件可以显示在主页上，为您提供额外的信息或交互功能。

## 可用的插件

sleepy 默认包含以下插件。默认情况下，所有插件都是禁用的，您需要在 `data/config.yaml` 中启用它们。

1. **test** - 一个简单的测试插件，显示自定义内容
2. **custom_html** - 允许您在页面上显示自定义 HTML 内容
3. **example_backend** - 一个示例后端插件，展示事件日志，用于开发者参考

您可以在社区中找到更多插件，或者如果您有开发经验，也可以创建自己的插件。

## 启用插件

要启用插件，您需要编辑 `data/config.yaml` 文件，将插件名称添加到 `plugin_enabled` 列表中：

```yaml
plugin_enabled:
  - test
  - custom_html
  - example_backend
```

插件会按照列表中的顺序加载和显示。

## 配置插件

每个插件可能有自己的配置选项，您可以在 `data/config.yaml` 文件的 `plugin` 部分进行设置：

```yaml
plugin:
  test:
    content: "这是自定义的测试内容"

  custom_html:
    content: |
      <b>这是自定义HTML内容</b><br/>
      <p style="color: blue;">这是蓝色文字</p>
      <a href="https://github.com/sleepy-project/sleepy">项目链接</a>

  example_backend:
    message: "这是一个自定义的后端插件示例"
    log_events: true
```

每个插件的配置选项不同，请参考插件的说明文档了解具体的配置项。

## 插件示例

### Test 插件

这是一个简单的测试插件，可以显示自定义内容：

```yaml
plugin:
  test:
    content: "这是自定义的测试内容"
```

### Custom HTML 插件

这个插件允许您在页面上显示自定义 HTML 内容：

```yaml
plugin:
  custom_html:
    content: |
      <h3>自定义 HTML</h3>
      <p>您可以在这里添加任何 HTML 内容</p>
      <ul>
        <li>支持列表</li>
        <li>支持链接 <a href="https://example.com">示例</a></li>
        <li>支持样式 <span style="color: red;">红色文字</span></li>
      </ul>
```

### Example Backend 插件

这是一个示例后端插件，展示系统事件日志。
默认情况下，它是禁用的，只用于演示插件的开发。
如果您想启用它，请在 `data/config.yaml` 中添加以下内容：

```yaml
plugin:
  example_backend:
    message: "这是一个后端插件示例"
    log_events: true
    api_enabled: true
```

## 禁用插件

如果您想禁用某个插件，只需从 `plugin_enabled` 列表中删除该插件的名称即可：

```yaml
plugin_enabled:
  - test
  # - custom_html  # 注释掉或删除这一行来禁用插件
  - example_backend
```

## 插件排序

插件会按照 `plugin_enabled` 列表中的顺序在页面上显示。如果您想调整插件的显示顺序，只需调整列表中的顺序即可：

```yaml
plugin_enabled:
  - example_backend  # 现在这个插件会显示在最上面
  - test
  - custom_html
```
