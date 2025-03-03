# config.jsonc update

> [!IMPORTANT]
> 在 [2024.12.14.2](#202412142) 中拆分 `data.json` 为 config 与 data 两部分 <br/>
> **config 文件名为 `config.jsonc`，后缀为 `jsonc` 而非 `json`，*支持注释***

## `version` 字段的说明

格式为 `yyyy.mm.dd.n`
- `yyyy`: 年
- `mm`: 月
- `dd`: 日
- `n`: 本日第 `n` 次修改
- *不补 `0` (`1145.1.4`, not `1145.01.04`)*

# 2025-03

## 2025.3.2.1

```jsonc
  "other": {
    "page_title": "User Alive?", // (1) [NEW]
    "page_desc": "User's Online Status Page", // (1) [NEW]
    // ...
  }
```

- **New** (1)
  * Name: `page_title`
  * Upper: `other`
  * Type: `str`
  * Desc: 控制网页标题

- **New** (2)
  * Name: `page_desc`
  * Upper: `other`
  * Type: `str`
  * Desc: 控制网页的内容描述 *(`<meta name="description" content="">` 的内容)*

# 2025-02

## 2025.2.10.1
```jsonc
// ...
    "other": {
        // ...
        "hitokoto": true,
        "canvas": true // (1) [NEW]
    }
```

- **New** (1)
  * Name: `canvas`
  * Upper: `other`
  * Type: `bool`
  * Desc: 控制是否显示背景图中的 [`canvas` 粒子效果](../static/canvas.js)，使网站更美观 (?)

## 2025.2.8.1
```jsonc
// ...
    "other": {
        // ...
        "device_status_slice": 30,
        "hitokoto": true // (1) [NEW]
    }
```

- **New** (1)
  * Name: `hitokoto`
  * Upper: `other`
  * Type: `bool`
  * Desc: 控制是否显示一言 (powered by [hitokoto.cn](https://hitokoto.cn))

## 2025.2.2.1

```jsonc
// ...
    "other": {
        // ...
        "more_text": "",
        "refresh": 5000, // (1) [MOVED]
        "device_status_slice": 30
    }
```

- **Moved** (1)
  * Name: `refresh`
  * Upper *(Before)*: None
  * Upper *(After)*: `other`

# 2025-01

## 2025.1.18.1

```jsonc
// ...
    "port": 9010,
    "timezone": "Asia/Shanghai", // (1) [NEW]
    "metrics": true,
// ...
```

- **New** (1)
  * Name: `timezone`
  * Upper: None
  * Type: `str`
  * Desc: 控制时区 (用于网页 / API 返回中的日期时间和 metrics 跨日计算)
  * Desc: 北京时间即为 `Asia/Shanghai` 或 `Asia/Chongqing` (***不是 `Beijing`!!!***), 一般情况下无需更改

## 2025.1.16.1

```jsonc
// ...
    "port": 9010,
    "metrics": true, // (1) [NEW]
    "secret": "nope",
// ...
```

- **New** (1)
  * Name: `metrics`
  * Upper: None
  * Type: `bool`
  * Desc: 控制是否启用 metrics (统计页面访问 / API 调用次数)
  * Desc: ps: 如禁用, 则无法访问 `/metrics` *(404)*

# 2024-12

## 2024.12.31.1

```jsonc
    "other": {
        // ...
        "more_text": "",
        "device_status_slice": 30 // (1) [NEW]
    }
}
```

- **New** (1)
  * Name: `device_status_slice`
  * Upper: `other`
  * Type: `int`
  * Desc: 控制设备状态从开头截取多少文字显示 (防止窗口标题过长影响页面)
  * Desc: ps: 设置为 `0` 以禁用

## 2024.12.20.1

```jsonc
// ...
    "refresh": 5000,
    "data_check_interval": 60, // (1) [NEW]
    "other": {
// ...
```

- **New** (1)
  * Name: `data_check_interval`
  * Upper: None
  * Type: `int`
  * Desc: 控制多久 *(秒)* 检查一次状态是否与 `data.json` 中的内容有异, 如有则保存
  * Desc: ps: 设置为 `0` 以禁用保存状态 **(不建议)**

## 2024.12.14.2

```jsonc
// ...
    "secret": "xxx",
    "status": 0, // (1) [REMOVE]
    "device_status": { // (2) [REMOVE]
        "last_updated": "2024-12-14 21:10:55" // (2) [REMOVE]
    }, // (2) [REMOVE]
    "status_list": [
// ...
```

- **Remove** (1)
  * Name: `status`
  * Upper: None
- **Remove** (2)
  * Name: `device_status`
  * Upper: None

## 2024.12.14.1

```jsonc
    // ...
    "status": 0,
    "device_status": {}, // (1) [New]
    "status_list": [
    // ...
```

- **New** (1)
  * Name: `device_status`
  * Upper: None
  * Type: `dict`
  * Desc: 存储各个设备的状态 (见下)
  * *Desc: 不用看了，当天就删了*

```jsonc
// device_status example
"device_status": {
    "desktop-3ee05kd": { // 设备名称 (标识符)
        "show_name": "Computer", // 在页面上显示的设备名称
        "using": true, // 是否正在使用
        "app_name": "Visual Studio Code" // 应用名
    },
    "redmi": {
        "show_name": "Phone",
        "using": false,
        "app_name": "UnKnown"
    },
    "last_updated": "2024-12-14 11:45:14" // 标识符不能为 last_updated
}
```

## 2024.12.13.1

```jsonc
// ...

    // ...
    ],
    "refresh": 5000, // (1) [New]
    "other": {
    // ...
```

- **New** (1)
  * Name: `refresh`
  * Upper: None
  * Type: `int`
  * Desc: 控制网页自动刷新时间 (毫秒), `0` 为不刷新
