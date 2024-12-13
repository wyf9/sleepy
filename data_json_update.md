# data.json update

## `version` 字段的说明

格式为 `yyyy.mm.dd.n`
- `yyyy`: 年
- `mm`: 月
- `dd`: 日
- `n`: 本日第 `n` 次提交

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
  * Desc: 控制网页自动刷新时间 (秒), `0` 为不刷新