# 插件前端功能

本文档详细介绍 sleepy 的插件前端功能，包括模板系统、静态资源管理和与后端的交互。

## 插件前端基础

要创建一个前端插件，需要在插件的 `plugin.yaml` 文件中设置 `frontend: true`，并创建 `index.html` 文件作为插件的前端入口点。

### 目录结构

一个典型的前端插件目录结构如下：

```
plugin/
  my_plugin/
    plugin.yaml      # 插件定义文件
    index.html       # 前端入口点
    static/          # 静态资源目录
      style.css      # CSS 样式
      script.js      # JavaScript 脚本
      images/        # 图片资源
        logo.png
```

### 插件定义

在 `plugin.yaml` 文件中，需要设置 `frontend: true` 来启用前端功能：

```yaml
frontend: true
frontend-card: true  # 是否创建卡片 (为是则将 index.html 内容插入到卡片中，为否则插入到网页底部)
config:
  title: "我的插件"
  description: "这是一个示例插件"
```

## 模板系统

插件的 `index.html` 文件使用 Flask 的 Jinja2 模板系统，可以访问插件的配置和系统数据。

### 基本语法

```html
<div class="my-plugin">
  <h3>{{ c.title }}</h3>
  <p>{{ c.description }}</p>
  
  {% if c.show_details %}
    <div class="details">
      <!-- 条件内容 -->
    </div>
  {% endif %}
  
  <ul>
    {% for item in c.items %}
      <li>{{ item }}</li>
    {% endfor %}
  </ul>
</div>
```

### 可用变量

在插件的模板中，可以访问以下变量：

- `c`: 插件配置对象，包含 `plugin.yaml` 中定义的配置项和用户在 `data/config.yaml` 中设置的值
  - 例如：`{{ c.title }}`, `{{ c.description }}`
- `status`: 系统状态信息
  - `status.name`: 当前状态名称
  - `status.desc`: 当前状态描述
  - `status.color`: 当前状态颜色
- `last_updated`: 最后更新时间
- `current_theme`: 当前主题名称
- `available_themes`: 可用主题列表

### 过滤器

模板系统支持多种过滤器，用于转换和格式化数据：

```html
<!-- 允许 HTML 内容 -->
{{ c.html_content | safe }}

<!-- 格式化日期 -->
{{ timestamp | datetime }}

<!-- 转换为大写 -->
{{ text | upper }}
```

## 静态资源

插件可以包含自己的静态资源，如 CSS、JavaScript 和图片文件。

### 引用静态资源

在模板中引用静态资源时，使用 `url_for` 函数：

```html
<!-- 引用 CSS 文件 -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

<!-- 引用 JavaScript 文件 -->
<script src="{{ url_for('static', filename='script.js') }}"></script>

<!-- 引用图片 -->
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```

### 主题回退机制

系统使用主题回退机制来查找静态资源。当引用一个静态资源时，系统会按以下顺序查找：

1. 当前插件的 `static` 目录
2. 当前主题的 `static` 目录
3. 默认主题的 `static` 目录

这意味着插件可以使用主题提供的公共资源，也可以提供自己的特定资源。

## 与后端交互

前端插件可以通过 API 与后端交互，包括系统 API 和插件自定义 API。

### 使用系统 API

```javascript
// 获取系统状态
async function getStatus() {
  const response = await fetch('/query');
  const data = await response.json();
  console.log('当前状态:', data.status);
}

// 获取设备信息
async function getDevices() {
  const response = await fetch('/device');
  const data = await response.json();
  if (data.success) {
    console.log('设备列表:', data.data);
  }
}
```

### 使用插件 API

如果插件有后端组件（`backend: true`），前端可以调用插件定义的 API：

```javascript
// 调用插件 API
async function callPluginApi() {
  const response = await fetch('/plugin/my_plugin/data');
  const data = await response.json();
  console.log('插件数据:', data);
}

// 发送数据到插件 API
async function sendDataToPlugin(userData) {
  const response = await fetch('/plugin/my_plugin/data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  const result = await response.json();
  console.log('响应结果:', result);
}
```

## 事件处理

插件可以监听和响应页面事件，实现动态交互。

### 页面加载事件

```javascript
document.addEventListener('DOMContentLoaded', function() {
  console.log('插件已加载');
  // 初始化插件
  initPlugin();
});
```

### 用户交互事件

```javascript
// 按钮点击事件
document.getElementById('my-button').addEventListener('click', function() {
  console.log('按钮被点击');
  // 处理点击事件
  handleButtonClick();
});

// 表单提交事件
document.getElementById('my-form').addEventListener('submit', function(event) {
  event.preventDefault();
  console.log('表单提交');
  // 处理表单提交
  handleFormSubmit(this);
});
```

## 完整示例

以下是一个完整的前端插件示例：

### plugin.yaml

```yaml
frontend: true
backend: true
config:
  title: "计数器插件"
  initial_count: 0
```

### index.html

```html
<div class="counter-plugin">
  <h3>{{ c.title }}</h3>
  <p>当前计数: <span id="counter">加载中...</span></p>
  <button id="increment-btn">增加计数</button>
</div>

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

### static/style.css

```css
.counter-plugin {
  border: 1px solid #ddd;
  padding: 15px;
  margin: 10px 0;
  border-radius: 5px;
}

.counter-plugin h3 {
  margin-top: 0;
  color: #333;
}

#counter {
  font-weight: bold;
  color: #007bff;
}

#increment-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
}

#increment-btn:hover {
  background-color: #0056b3;
}
```

## 最佳实践

### 1. 命名空间

为避免与其他插件或主页面冲突，使用唯一的类名或 ID 前缀：

```html
<div class="my-plugin-container">
  <div class="my-plugin-header">...</div>
  <div class="my-plugin-content">...</div>
</div>
```

### 2. 模块化 JavaScript

将 JavaScript 代码模块化，避免全局变量污染：

```javascript
(function() {
  // 插件的私有变量和函数
  let counter = 0;
  
  function increment() {
    counter++;
    updateDisplay();
  }
  
  function updateDisplay() {
    document.getElementById('my-plugin-counter').textContent = counter;
  }
  
  // 初始化函数
  function init() {
    document.getElementById('my-plugin-button').addEventListener('click', increment);
    updateDisplay();
  }
  
  // 页面加载时初始化
  document.addEventListener('DOMContentLoaded', init);
})();
```

### 3. 响应式设计

确保插件在不同屏幕尺寸下都能正常显示：

```css
.my-plugin-container {
  max-width: 100%;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .my-plugin-container {
    padding: 10px;
  }
  
  .my-plugin-header {
    font-size: 16px;
  }
}
```

### 4. 错误处理

添加适当的错误处理，提高用户体验：

```javascript
async function fetchData() {
  try {
    const response = await fetch('/plugin/my_plugin/data');
    if (!response.ok) {
      throw new Error('API 请求失败');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取数据失败:', error);
    document.getElementById('my-plugin-error').textContent = '加载数据失败，请刷新页面重试';
    return null;
  }
}
```
