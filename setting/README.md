# setting

这里存储一些用户可自定义的设置哦

> [!TIP]
> 文件夹中 json 使用标准 `json` 库解析，所以**不允许注释**

## [`status_list.json`](./status_list.json)

> 用于自定义手动设置的 status

格式:

```jsonc
[
    { // status: 0
        "id": 0, // 与索引相同，非必须，仅为方便查看 (建议加上)
        "name": "活着", // 状态名称
        "desc": "目前在线，可以通过任何可用的联系方式联系本人。", // 状态描述
        "color": "awake" // 状态颜色, 对应 static/style.css 中的 .sleeping .awake 等类, 可自行前往修改
    },
    { // status: 1
        "id": 1,
        "name": "似了",
        "desc": "睡似了或其他原因不在线，紧急情况请使用电话联系。",
        "color": "sleeping"
    }
    // 还可添加更多自定义状态，但不要删除现有的两个状态
]
```

## [`metrics_list.json`](./metrics_list.json)

> 用于自定义访问统计的路径列表 (只有启用 metrics 功能, **且访问的路径在列表中**才会被计数)

格式:

```jsonc
[
    "/",
    "/steam",
    "/style.css",
    "/query",
    "/status_list",
    "/set",
    "/device/set",
    "/device/remove",
    "/device/clear",
    "/device/private_mode",
    "/save_data",
    "/events",
    "/metrics",
    "/robots.txt",
    "[static]", // 特殊值, 匹配 static 目录中的所有文件
    "/custom_route" // 还可添加更多
]
```