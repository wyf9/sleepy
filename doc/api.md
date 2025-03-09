# API

1. [只读接口](#read-only)
2. [Status 接口](#status)
3. [Device status 接口](#device)
4. [Storage 接口](#storage)

## Read-only

[Back to # api](#api)

|                      | 路径           | 方法  | 作用             |
| -------------------- | -------------- | ----- | ---------------- |
|                      | `/`            | `GET` | 显示主页         |
| [Jump](#query)       | `/query`       | `GET` | 获取状态         |
| [Jump](#status-list) | `/status_list` | `GET` | 获取可用状态列表 |
| [Jump](#metrics)     | `/metrics`     | `GET` | 获取统计信息     |

### query

[Back to ## read-only](#read-only)

> `/query`

获取当前的状态

* Method: GET
* 无需鉴权

#### Response

```jsonc
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
            "app_name": "bilibili" // 应用名 (如 using == false 则不使用)
        }
    },
    "last_updated": "2024-12-20 23:51:34", // 信息上次更新的时间
    "refresh": 5000, // 刷新时间 (ms)
    "device_status_slice": 20 // 设备状态截取文字数
}
```

> 其中日期/时间的时区默认为 `Asia/Shanghai`, 可在 config.jsonc 中修改

### status-list

[Back to ## read-only](#read-only)

> `/status_list`

获取可用状态的列表

* Method: GET
* 无需鉴权
* Alias: `/get/status_list` *(兼容旧版本)*

#### Response

```jsonc
[
    {
        "id": 0, // 索引，取决于配置文件中的有无
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

> 就是返回 `config.jsonc` 中的 `status_list` 列表

### metrics

[Back to ## read-only](#read-only)

> `/metrics`

获取统计信息

* Method: GET
* 无需鉴权

> [!TIP]
> 本接口较特殊: 如服务器关闭了统计 *(`config.jsonc` 中的 `metrics` 为 `false`)*, 则 **`/metrics` 路由将不会被创建**, 体现为访问显示 404 页面而不是返回结果 <br/>
> ~~*我也不知道自己怎么想的*~~

#### Response

```jsonc
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

## Status

[Back to # api](#api)

|                     | 路径                                   | 方法  | 作用     |
| ------------------- | -------------------------------------- | ----- | -------- |
| [Jump](#status-set) | `/set?secret=<secret>&status=<status>` | `GET` | 设置状态 |

> 已移除旧的 `/set/<secret>/<status>` 接口

### status-set

[Back to ## status](#status)

> `/set?secret=<secret>&status=<status>`

设置当前状态

* Method: GET

#### Params

- `<secret>`: 在 `config.jsonc` 中配置的 `secret`
- `<status>`: 状态码 *(`int`)*

#### Response

```jsonc
// 成功
{
    "success": true, // 请求是否成功
    "code": "OK", // 返回代码
    "set_to": 0 // 设置到的状态码
}

// 失败 - 密钥错误
{
    "success": false, // 请求是否成功
    "code": "not authorized", // 返回代码
    "message": "invaild secret" // 详细信息
}

// 失败 - 请求无效
{
    "success": false, // 请求是否成功
    "code": "bad request", // 返回代码
    "message": "argument 'status' must be a number" // 详细信息
}
```

## Device

[Back to # api](#api)

|                              | 路径                                                                                          | 方法   | 作用                          |
| ---------------------------- | --------------------------------------------------------------------------------------------- | ------ | ----------------------------- |
| [Jump](#device-set)          | `/device/set`                                                                                 | `POST` | 设置单个设备的状态 (打开应用) |
|                              | `/device/set?secret=<secret>&id=<id>&show_name=<show_name>&using=<using>&app_name=<app_name>` | `GET`  | -                             |
| [Jump](#device-remove)       | `/device/remove?secret=<secret>&name=<device_name>`                                           | `GET`  | 移除单个设备的状态            |
| [Jump](#device-clear)        | `/device/clear?secret=<secret>`                                                               | `GET`  | 清除所有设备的状态            |
| [Jump](#device-private-mode) | `/device/private_mode?secret=<secret>&private=<isprivate>`                                    | `GET`  | 设置隐私模式                  |

### device-set

[Back to ## device](#device)

> `/device/set`

设置单个设备的状态

* Method: GET / POST

#### Params (GET)

> [!WARNING]
> 使用 url params 传递参数在某些情况下 *(如内容包含特殊符号)* 可能导致非预期行为, 此处更建议使用 POST

> `/device/set?secret=<secret>&id=<id>&show_name=<show_name>&using=<using>&app_name=<app_name>`

- `<secret>`: 在 `config.jsonc` 中配置的 `secret`
- `<id>`: 设备标识符
- `<show_name>`: 显示名称
- `<using>`: 是否正在使用
- `<app_name>`: 正在使用应用的名称

#### Body (POST)

> `/device/set`

```jsonc
{
    "secret": "MySecretCannotGuess", // 密钥
    "id": "device-1", // 设备标识符
    "show_name": "MyDevice1", // 显示名称
    "using": true, // 是否正在使用
    "app_name": "VSCode" // 正在使用应用的名称
}
```

#### Response

```jsonc
// 成功
{
  "success": true,
  "code": "OK"
}

// 失败 - 密钥错误
{
    "success": false,
    "code": "not authorized",
    "message": "invaild secret"
}

// 失败 - 缺少参数
{
    "success": false,
    "code": "bad request",
    "message": "missing param"
}
```

### device-remove

[Back to ## device](#device)

> `/device/remove?secret=<secret>&id=<device_id>`

移除单个设备的状态

* Method: GET

#### Params

- `<secret>`: 在 `config.jsonc` 中配置的 `secret`
- `<device_id>`: 设备标识符

#### Response

```jsonc
// 成功
{
    "success": true,
    "code": "OK"
}

// 失败 - 不存在 (也不算失败了?)
{
    "success": false,
    "code": "not found",
    "message": "cannot find item"
}

// 失败 - 密钥错误
{
    "success": false,
    "code": "not authorized",
    "message": "invaild secret"
}
```

### device-clear

[Back to ## device](#device)

> `/device/clear?secret=<secret>`

清除所有设备的状态

* Method: GET

#### Params

- `<secret>`: 在 `config.jsonc` 中配置的 `secret`

#### Response

```jsonc
// 成功
{
    "success": true,
    "code": "OK"
}

// 失败 - 密钥错误
{
    "success": false,
    "code": "not authorized",
    "message": "invaild secret"
}
```

### device-private-mode

[Back to ## device](#device)

> `/device/private_mode?secret=<secret>&private=<isprivate>`

设置隐私模式 *(即在 [`/query`](#query) 的返回中设置 `device` 项为空 (`{}`))*

* Method: GET

#### Params

- `<secret>`: 在 `config.jsonc` 中配置的 `secret`
- `<isprivate>`: bool (仅接受 `true` / `false`), 开关状态

#### Response

```jsonc
// 成功
{
    "success": true,
    "code": "OK"
}

// 失败 - 密钥错误
{
    "success": false,
    "code": "not authorized",
    "message": "invaild secret"
}

// 失败 - 请求无效
{
    "success": false,
    "code": "invaild request",
    "message": "\"private\" arg only supports boolean type"
}
```

## Storage

[Back to # api](#api)

|                            | 路径                         | 方法  | 作用                 |
| -------------------------- | ---------------------------- | ----- | -------------------- |
| [Jump](#storage-save-data) | `/save_data?secret=<secret>` | `GET` | 保存内存中的状态信息 |

> 已移除 `/reload_config` 接口, 现在需要重启服务以重载配置

### storage-save-data

[Back to ## storage](#storage)

> `/save_data?secret=<secret>`

保存内存中的状态信息到 `data.json`

* Method: GET

#### Params

- `<secret>`: 在 `config.jsonc` 中配置的 `secret`

#### Response

```jsonc
// 成功
{
    "success": true,
    "code": "OK",
    "data": { // data.json 内容
        "status": 0,
        "device_status": {},
        "last_updated": "2024-12-21 13:58:38"
    }
}

// 失败 - 密钥错误
{
    "success": false,
    "code": "not authorized",
    "message": "invaild secret"
}

// 失败 - 保存出错
{
    "success": false,
    "code": "exception",
    "message": "..." // 报错内容
}
```
