# config.json update

> 在 [2024.12.14.2](#202412142) 中拆分 `data.json` 为 config 与 data 两部分

## `version` 字段的说明

格式为 `yyyy.mm.dd.n`
- `yyyy`: 年
- `mm`: 月
- `dd`: 日
- `n`: 本日第 `n` 次修改

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
  * Type: int
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
  * Type: int
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
  * Type: Dict
  * Desc: 存储各个设备的状态 (见下)

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
    "refresh": 5, // (1) [New]
    "other": {
    // ...
```

- **New** (1)
  * Name: `refresh`
  * Upper: None
  * Type: Number
  * Desc: 控制网页自动刷新时间 (毫秒), `0` 为不刷新
