# sleepy

一个查看个人在线状态 (并视奸正在使用软件) 的 Flask 网站，让他人能知道你不在而不是故意吊他/她

[**功能**](#功能) / [**TODO**](#todo) / [**演示**](#preview-功能) / [**部署**](#部署) / [**使用**](#使用) / [**关于**](#关于)

## 功能

- 自行设置在线状态
- 实时更新设备打开应用(名称) *(未完成)*
- 美观的展示页面 [见 [Preview](#preview)]

### TODO

- [x] 网页使用 api 请求，并实现定时刷新
- [ ] 设备使用状态 (仅完成 api)
- [ ] 更好的客户端示例
- [x] **修改数据保存方法** (https://github.com/wyf9/sleepy/issues/3)
  - 拆分 `config.json` (只读) 和 `data.json`
  - 定时写入 `data.json`

> [!TIP]
> 正在加急更新中 (请看 [dev-2024-12-2](https://github.com/wyf9/sleepy/tree/dev-2024-12-2) 分支) <br/>
> 因上学原因, 可能放缓更新 <br/>
> **最新开发进度/完整 TODOs 见: [Discord Server](https://discord.gg/DyBY6gwkeg)**

### Preview

演示站 (稳定): [sleepy.wyf9.top](https://sleepy.wyf9.top)

开发预览 (*不保证可用*): [sleepy-preview.wyf9.top](https://sleepy-preview.wyf9.top)

## 部署

> 从旧版本更新? 请看 [config.json 更新记录](./config_json_update.md) <br/>
> *配置文件已从 `data.json` 更名为 `config.json`*

理论上全平台通用, 安装了 Python >= **3.6** 即可 (建议: **3.10+**)

1. Clone 本仓库 (建议先 Fork / Use this template)

```shell
git clone https://github.com/wyf9/sleepy.git
```

2. 安装依赖

```shell
pip install flask pytz
```

3. 编辑配置文件

先启动一遍程序:

```shell
python3 server.py
```

如果不出意外，会提示: `config.json not exist, creating`，同时目录下出现 `config.json` 文件，编辑该文件中的配置后重新运行即可 (示例请 [查看 `example.jsonc`](./example.jsonc) )

## 使用

有两种启动方式:

```shell
python3 server.py # 直接启动
python3 start.py # 简易启动器
```

默认服务 http 端口: `9010` *(可在 `config.json` 中修改)*

## API

> 斜体项表示无需传入任何参数

|     | 路径                                                                                          | 方法   | 作用                          |
| --- | --------------------------------------------------------------------------------------------- | ------ | ----------------------------- |
| 0   | *`/`*                                                                                         | `GET`  | *显示主页*                    |
| 1   | *`/query`*                                                                                    | `GET`  | *获取状态*                    |
| 2   | *`/status_list`*                                                                              | `GET`  | *获取可用状态列表*            |
| 3   | `/set?secret=<secret>&status=<status>`                                                        | `GET`  | 设置状态                      |
|     | `/set/<secret>/<status>`                                                                      | `GET`  | -                             |
| 4   | `/device/set`                                                                                 | `POST` | 设置单个设备的状态 (打开应用) |
|     | `/device/set?secret=<secret>&id=<id>&show_name=<show_name>&using=<using>&app_name=<app_name>` | `GET`  | -                             |
| 5   | `/device/remove?secret=<secret>&name=<device_name>`                                           | `GET`  | 移除单个设备的状态            |
| 6   | `/device/clear?secret=<secret>`                                                               | `GET`  | 清除所有设备的状态            |
| 7   | `/reload_config?secret=<secret>`                                                              | `GET`  | *[new]* 重载配置              |
| 8   | `/save_data?secret=<secret>`                                                                  | `GET`  | *[new]* 保存内存中的状态信息  |

### 1. `/query`

获取当前的状态

* Method: GET
* 无需鉴权

#### Response

```jsonc
{
    "success": true, // 请求是否成功
    "status": 0, // 获取到的状态码
    "info": { // 对应状态码的信息
        "name": "活着", // 状态名称
        "desc": "目前在线，可以通过任何可用的联系方式联系本人。", // 状态描述
        "color": "awake"// 状态颜色, 对应 static/style.css 中的 .sleeping .awake 等类
    },
    "refresh": 5000 // 刷新时间 (ms)
}
```

### 2. `/status_list`

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

> 就是返回 `config.json` 中的 `status_list` 列表

### 3. `/set?secret=<secret>&status=<status>`

设置当前状态

* Method: GET
* Alias: `/set/<secret>/<status>` (path param)

#### Params

- `<secret>`: 在 `config.json` 中配置的 `secret`
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


### 4. `/device/set`

设置单个设备的状态

* Method: GET / POST

#### Params (GET)

> [!WARNING]
> 使用 url params 传递参数在某些情况下 *(如内容包含特殊符号)* 可能导致非预期行为, 此处更建议使用 POST

> `/device/set?secret=<secret>&id=<id>&show_name=<show_name>&using=<using>&app_name=<app_name>`

- `<secret>`: 在 `config.json` 中配置的 `secret`
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

### 5. `/device/remove?secret=<secret>&id=<device_id>`

移除单个设备的状态

* Method: GET

#### Params

- `<secret>`: 在 `config.json` 中配置的 `secret`
- `<device_id>`: 设备标识符

### Response

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

### 6. `/device/clear?secret=<secret>`

清除所有设备的状态

* Method: GET

#### Params

- `<secret>`: 在 `config.json` 中配置的 `secret`

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

### 7. `/reload_config?secret=<secret>`

重新从 `config.json` 加载配置

* Method: GET

#### Params

- `<secret>`: 在 `config.json` 中配置的 `secret`

#### Response

```jsonc
// 成功
{
    "success": true,
    "code": "OK",
    "config": { // 你的 config.json 内容
        "version": "2024.12.20.1",
        "debug": true,
        "host": "::",
        "port": 9010,
        // ...
    }
}

// 失败 - 密钥错误
{
    "success": false,
    "code": "not authorized",
    "message": "invaild secret"
}
```

### 8. `/save_data?secret=<secret>`

保存内存中的状态信息到 `data.json`

* Method: GET

#### Params

- `<secret>`: 在 `config.json` 中配置的 `secret`

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
```

## 客户端示例

在 `_example/` 目录下, 可参考

## 关于

本项目灵感由 Bilibili UP [@WinMEMZ](https://space.bilibili.com/417031122) 而来: [site](https://maao.cc/sleepy/) / [blog](https://www.maodream.com/archives/192/), 并~~部分借鉴~~使用了前端代码, 在此十分感谢。

感谢 [@1812z](https://github.com/1812z) 的 B 站视频推广~ ([BV1LjB9YjEi3](https://www.bilibili.com/video/BV1LjB9YjEi3))

如有 Bug / 建议, 请 [issue](https://github.com/wyf9/sleepy/issues/new) 或 [More contact](https://wyf9.top/#/contact) *(注明来意)*.
