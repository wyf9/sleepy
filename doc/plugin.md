# Plugin / 插件

本文档介绍 sleepy 的插件设计及规范

## 存储位置

### 主程序文件

```yaml
- plugin/ # 插件总文件夹
  - steam/ # 插件 id
    - index.html # 将注入的 HTML 代码
    - static/ # 插件所需静态资源 (css / js / img / ...)
      - steam.css
    - __init__.py # 插件后端入口
    - config.plugin.yaml # 插件配置模板
  - hitokoto/
```

### 用户配置

统一存储在用户的 `config.yaml` 中的 `plugin` 部分

```yaml
plugin:
  test: # 插件 id
    content: 'this is content' # 插件的配置项
```

配置的模板存放在上文的 `config.yaml`

## 启用插件

在 `config.yaml` 中:

```yaml
plugin_enabled: # 启动的插件列表，注入顺序为从上到下
  - test # 插件 id
  # - ...
```

## 运作方式

### 前端代码 (index.html)

将按照插件启用的顺序注入到主 index.html 中