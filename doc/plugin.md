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
    - plugin.yaml # 插件定义文件
  - hitokoto/
```

### 用户配置

统一存储在用户的 `config.yaml` 中的 `plugin` 部分

```yaml
plugin:
  test: # 插件 id
    content: 'this is content' # 插件的配置项
```

配置的模板存放在上文的 `plugin.yaml`

## 启用插件

在 `config.yaml` 中:

```yaml
plugin_enabled: # 启动的插件列表，注入顺序为从上到下
  - test # 插件 id
  # - ...
```

## 插件组成

### 插件定义 (plugin.yaml)

包含插件的一些必要元数据 **(必须有本文件，否则将视为插件不存在)**

```yaml
frontend: true # 是否为前端插件 (为是才会尝试加载 index.html)
backend: true # 是否为后端插件 (为是才会尝试加载 __main__.py)
config: # 配置项定义 (即默认值)
  name: value
```

### 前端代码 (index.html)

将按照插件启用的顺序注入到主 index.html 中

可以使用 Flask 模板语言，另有如下变量 / 方法可用:

```html
<!-- 读取键为 name 的配置项 -->
{{ c.name }}

<!-- 读取键为 desc 的配置项，且允许渲染其中的 HTML 代码 -->
{{ c.desc | safe }}


```