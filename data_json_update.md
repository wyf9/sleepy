# data.json update

## `version` 字段的说明

格式为 `yyyy.mm.dd.n`
- `yyyy`: 年
- `mm`: 月
- `dd`: 日
- `n`: 本日第 `n` 次提交

# 2024.12.14.1

```json
    // ...
    "status": 0,
    "device_status": {}, // (1) [New]
    "status_list": [
    // ...
```

- **(1)**
  * Name: `device_status`
  * Upper: None
  * Type: Dict
  * Desc: 存储各个设备的状态 (见下)

```json
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

```json
// ...

    // ...
    ],
    "refresh": 5, // (1) [New]
    "other": {
    // ...
```

- **(1)**
  * Name: `refresh`
  * Upper: None
  * Type: Number
  * Desc: 控制网页自动刷新时间 (毫秒), `0` 为不刷新