# API

0. [鉴权说明](#一些说明)
1. [Status 接口](#status)
2. [Device 接口](#device)
3. [其他接口](#others)

## 一些说明

### 关于错误

所有 API 返回的错误都会通过 `utils.APIUnsuccessful` 格式化:

```jsonc
{
  "success": false, // 表示请求未成功
  "code": 500, // 数字 HTTP Code (如 404, 500, ...)
  "details": "Internal Server Error", // HTTP Code 描述 (如 Not Found, Internal Server Error, ...)
  "message": "..." // 附带的错误详情
}
```

### 关于鉴权

> 在接口列表中, 标记为斜体的即为需要鉴权

任何标记了需要鉴权的接口，都需要用下面三种方式的一种传入 **与服务端一致** 的 `secret` *(优先级从上到下)*:

1. 请求体 *(`Body`)* 的 `secret` *(仅适用于 POST 请求)*

```jsonc
{
  "secret": "MySecretCannotGuess",
  // ...
}
```

2. 请求参数 *(`Param`)* 的 `secret`

```url
?secret=MySecretCannotGuess
```

3. 请求头 *(`Header`)* 的 `Sleepy-Secret`

```http
Sleepy-Secret: MySecretCannotGuess
```

4. 请求头 *(`Header`)* 的 `Authorization` *(需要在 secret 前加 `Bearer `)*

```http
Authorization: Bearer MySecretCannotGuess
```

5. Cookie *(`Cookie`)* 的 `sleepy-token`

```
sleepy-token=MySecretCannotGuess
```

> 服务端的 `secret` 即为在环境变量中配置的 `SLEEPY_SECRET`

如 `secret` 错误，则会返回:

```jsonc
// 403 Forbidden
{
  "success": false, // 请求是否成功
  "code": "not authorized", // 返回代码
  "message": "wrong secret" // 详细信息
}
```

## Status

[Back to # api](#api)

|                      | 路径                              | 方法  | 作用             |
| -------------------- | --------------------------------- | ----- | ---------------- |
| [Jump](#query)       | `/api/status/query`               | `GET` | 获取状态         |
| [Jump](#status-set)  | `/api/status/set?status=<status>` | `GET` | 设置状态         |
| [Jump](#status-list) | `/api/status/list`                | `GET` | 获取可用状态列表 |
| [Jump](#metrics)     | `/api/metrics`             | `GET` | 获取统计信息     |

### query

[Back to ## status](#status)

> `/api/status/query`

获取当前的状态

* Method: GET
* 无需鉴权

#### Params

- `meta`: 是否同时请求元数据 *(bool)*
- `metrics`: 是否同时请求统计数据 *(bool)*

#### Response

```jsonc
// 200 OK
{
  "time": 1751074053.782428, // 服务端时间 (UTC 时间戳)
  "success": true, // 请求是否成功
  "status": { // 手动状态
    "color": "awake", // 状态颜色, 对应 static/style.css 中的 .sleeping .awake 等类
    "desc": "目前在线，可以通过任何可用的联系方式联系本人。", // 状态描述
    "id": 0, // 状态数字 id
    "name": "活着" // 状态名称
  },
  "device": {}, // 设备列表 (见下)
  "last_updated": 1750640868.938035 // 最后更新时间
}
```

#### Response (OLD)

> [!IMPORTANT]
> 作为兼容旧版选项提供, 需要加上参数请求: `/api/status/query?version=1`

<details>
<summary>点击展开</summary>

```jsonc
// 200 OK
{
  "time": "2024-12-28 00:21:24", // 服务端时间
  "timezone": "Asia/Shanghai", // 服务端配置的时区
  "success": true, // 请求是否成功
  "status": 0, // 获取到的状态码
  "info": { // 对应状态码的信息
    "name": "活着", // 状态名称
    "desc": "目前在线，可以通过任何可用的联系方式联系本人。", // 状态描述
    "color": "awake"// 状态颜色, 对应 static/style.css 中的 .sleeping .awake 等类
  },
  "device": { // 设备列表
    "device-1": { // 标识符，唯一
      "show_name": "MyDevice1", // 前台显示名称
      "using": "false", // 是否正在使用
      "app_name": "bilibili" // 应用名 (如 using == false 且设置了 status.not_using 则会被替换)
    }
  },
  "last_updated": "2024-12-20 23:51:34", // 信息上次更新的时间
  "refresh": 5000, // 刷新时间 (ms)
  "device_status_slice": 20 // 设备状态截取文字数
}
```

> 返回中 **日期/时间** 的时区默认为 **`Asia/Shanghai`** *(即北京时间)*, 可在配置中修改

</details>

### status-set

[Back to ## status](#status)

> `/api/status/set?status=<status>`

设置当前状态

* Method: GET
* **需要鉴权**

#### Params

- `<status>`: 状态码 *(`int`)*

#### Response

```jsonc
// 200 OK | 成功
{
  "success": true, // 请求是否成功
  "code": "OK", // 返回代码
  "set_to": 0 // 设置到的状态码
}

// 400 Bad Request | 失败 - 请求无效
{
  "success": false, // 请求是否成功
  "code": "bad request", // 返回代码
  "message": "argument 'status' must be a number" // 详细信息
}
```

### status-list

[Back to ## status](#status)

> `/api/status/list`

获取可用状态的列表

* Method: GET
* 无需鉴权

#### Response

```jsonc
// 200 OK
[
  {
    "id": 0, // 索引 (从 0 开始)
    "name": "活着", // 状态名称
    "desc": "目前在线，可以通过任何可用的联系方式联系本人。", // 状态描述
    "color": "awake" // 状态颜色, 对应 static/style.css 中的 .sleeping .awake 等类
  }, 
  {
    "id": 1, 
    "name": "似了", 
    "desc": "睡似了或其他原因不在线，紧急情况请使用电话联系。", 
    "color": "sleeping"
  }, 
  // 以此类推
]
```

### metrics

[Back to ## status](#status)

> `/api/metrics`

获取统计信息

* Method: GET
* 无需鉴权

> [!TIP]
> 本接口较特殊: 如服务器关闭了统计, 则 **`/api/metrics` 路由将不会被创建**, 体现为访问显示 404 页面而不是返回结果  
> ~~*我也不知道自己怎么想的*~~

#### Response

```jsonc
// 200 OK
{
  "time": "2025-01-22 08:40:48.564728+08:00", // 服务端时间
  "timezone": "Asia/Shanghai", // 时区
  "today_is": "2025-1-22", // 今日日期
  "month_is": "2025-1", // 今日月份
  "year_is": "2025", // 今日年份
  "today": { // 今天的数据
    "/device/set": 18,
    "/": 2,
    "/style.css": 1,
    "/query": 2
  }, 
  "month": { // 今月的数据
    "/device/set": 18,
    "/": 2,
    "/style.css": 1,
    "/query": 2
  }, 
  "year": { // 今年的数据
    "/device/set": 18,
    "/": 2,
    "/style.css": 1,
    "/query": 2
  }, 
  "total": { // 总统计数据，不清除
    "/device/set": 18,
    "/": 2,
    "/style.css": 1,
    "/query": 2
  }
}
```

## Device

[Back to # api](#api)

|                              | 路径                                                                              | 方法   | 作用                          |
| ---------------------------- | --------------------------------------------------------------------------------- | ------ | ----------------------------- |
| [Jump](#device-set)          | `/api/device/set`                                                                 | `POST` | 设置单个设备的状态 (打开应用) |
|                              | `/api/device/set?id=<id>&show_name=<show_name>&using=<using>&app_name=<app_name>` | `GET`  | -                             |
| [Jump](#device-remove)       | `/api/device/remove?name=<device_name>`                                           | `GET`  | 移除单个设备的状态            |
| [Jump](#device-clear)        | `/api/device/clear`                                                               | `GET`  | 清除所有设备的状态            |
| [Jump](#device-private-mode) | `/api/device/private_mode?private=<isprivate>`                                    | `GET`  | 设置隐私模式                  |

### device-set

[Back to ## device](#device)

> `/api/device/set`

设置单个设备的状态

* Method: GET / POST
* **需要鉴权**

#### Params (GET)

> [!WARNING]
> 使用 url params 传递参数在某些情况下 *(如内容包含特殊符号)* 可能导致非预期行为, 此处更建议使用 POST

> `/api/device/set?id=<id>&show_name=<show_name>&using=<using>&app_name=<app_name>`

- `<id>`: 设备标识符
- `<show_name>`: 显示名称
- `<using>`: 是否正在使用
- `<app_name>`: 正在使用应用的名称

#### Body (POST)

> `/api/device/set`

```jsonc
{
  "id": "device-1", // 设备标识符
  "show_name": "MyDevice1", // 显示名称
  "using": true, // 是否正在使用
  "app_name": "VSCode" // 正在使用应用的名称
}
```

#### Response

```jsonc
// 200 OK | 成功
{
  "success": true,
  "code": "OK"
}

// 400 Bad Request | 失败 - 缺少参数 / 参数类型错误
{
  "success": false,
  "code": "bad request",
  "message": "missing param or wrong param type"
}
```

### device-remove

[Back to ## device](#device)

> `/api/device/remove?id=<device_id>`

移除单个设备的状态

* Method: GET
* **需要鉴权**

#### Params

- `<device_id>`: 设备标识符

#### Response

```jsonc
// 200 OK | 成功
{
  "success": true,
  "code": "OK"
}

// 404 Not Found | 失败 - 不存在 (也不算失败了?)
{
  "success": false,
  "code": "not found",
  "message": "cannot find item"
}
```

### device-clear

[Back to ## device](#device)

> `/api/device/clear`

清除所有设备的状态

* Method: GET
* **需要鉴权**

#### Response

```jsonc
// 200 OK | 成功
{
  "success": true,
  "code": "OK"
}
```

### device-private-mode

[Back to ## device](#device)

> `/api/device/private_mode?private=<isprivate>`

设置隐私模式 *(即在 [`/api/status/query`](#query) 的返回中设置 `device` 项为空 (`{}`))*

* Method: GET
* **需要鉴权**

#### Params

- `<isprivate>`: bool, 开关状态

#### Response

```jsonc
// 200 OK | 成功
{
  "success": true,
  "code": "OK"
}

// 400 Bad Request | 失败 - 请求无效
{
  "success": false,
  "code": "invaild request",
  "message": "\"private\" arg must be boolean"
}
```

## Others

[Back to # api](#api)

|                              | 路径                                                                              | 方法   | 作用                          |
| ---------------------------- | --------------------------------------------------------------------------------- | ------ | ----------------------------- |
| [Jump](#device-set)          | `/api/meta`                                                                 | `POST` | 设置单个设备的状态 (打开应用) |
