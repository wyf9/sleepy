# /client

此目录存储客户端 (用于更新状态/设备状态)

- [/client](#client)
  - [CMDConsole](#cmdconsole)
  - [CmdConsoleMuiti](#cmdconsolemuiti)
  - [WinDevice](#windevice)
    - [Configure](#configure)
  - [AutoxjsScript](#autoxjsscript)
    - [Configure](#configure-1)
    - [Using](#using)
  - [BrowserScript](#browserscript)
    - [Configure](#configure-2)
  - [Homework](#homework)
    - [Configure](#configure-3)
    - [Using](#using-1)
  - [Other repos](#other-repos)

> [!TIP]
> 欢迎提交 Issue / PR 贡献自己的脚本！

## [CMDConsole](./cmd_console.py)

> by: [@wyf9](https://github.com/wyf9)

一个简单的命令行客户端，用于手动更新状态

依赖: `requests`

## [CmdConsoleMuiti](./cmd_console_muiti.py)

> by: [@wyf9](https://github.com/wyf9)

[CMDConsole](#cmdconsole) 的旧版本 (可选择多个服务)

## [WinDevice](./win_device.py)

> by: [@wyf9](https://github.com/wyf9)

在 Windows 上自动更新设备状态

依赖: `requests`, `pywin32`

### Configure

> 文件 [L12-L19](https://github.com/wyf9/sleepy/blob/main/client/win_device.py#L12-L19) 的配置如下：

```py
# --- config start
# 服务地址, 末尾同样不带 /
SERVER = 'http://localhost:9010'
# 密钥
SECRET = 'wyf9test'
# 设备标识符，唯一 (它也会被包含在 api 返回中, 不要包含敏感数据)
DEVICE_ID = 'device-1'
# 前台显示名称
DEVICE_SHOW_NAME = 'MyDevice1'
# 检查间隔，以秒为单位
CHECK_INTERVAL = 2
# 是否忽略重复请求，即窗口未改变时不发送请求
BYPASS_SAME_REQUEST = True
# 控制台输出所用编码，避免编码出错，可选 utf-8 或 gb18030
ENCODING = 'utf-8'
# 当窗口名为其中任意一项时将不更新
SPECIAL_NAMES = ['新通知']
# 当窗口名为其中任意一项时视为未在使用
NOT_USING_NAMES = ['', '搜索', '通知中心', '快速设置', '系统托盘溢出窗口。', '我们喜欢这张图片，因此我们将它与你共享。', 'Flow.Launcher']
# --- config end
```

> PM2 启动命令参考: `pm2 start python --name sleepywin -- -u win_device.py` **(不加 `-u` 参数会导致 `pm2 log` 命令没有输出)**

## [AutoxjsScript](./autoxjs_device.js)

> by: [@wyf9](https://github.com/wyf9) <br/>
> Co-authored-by: [@NyaOH-Nahida](https://github.com/NyaOH-Nahida)

使用 [Autox.js](https://github.com/kkevsekk1/AutoX) 编写的安卓自动更新状态脚本

在使用前，请确保**已安装** Autox.js *且*授予**无障碍权限**

### Configure

> 文件 [L7-L13](https://github.com/wyf9/sleepy/blob/main/client/autoxjs_device.py#L7-L13) 的配置如下：

```js
// config start
const API_URL = 'https://sleepy.wyf9.top/device/set'; // 你的完整 API 地址，以 `/device/set` 结尾
const SECRET = '绝对猜不出来的密码'; // 你的 secret
const ID = 'a-device'; // 你的设备 id, 唯一
const SHOW_NAME = '一个设备'; // 你的设备名称, 将显示在网页上
const CHECK_INTERVAL = '3000'; // 检查间隔 (毫秒, 1000ms=1s)
// config end
```

### Using

启动后可点击 Autox.js 右上角的日志图标查看日志

![image](https://files.catbox.moe/x93248.png)

- 当手机息屏 (应用名返回为空) 时视为未在使用
- *[+]* 当脚本退出时也会更新状态为未在使用 *(不包括 Autox.js 停止运行)*

## [BrowserScript](./页面标题上报脚本-2024.12.2.user.js)

> by: [@nuym](https://github.com/nuym)

在任何支持油猴脚本的浏览器均可使用，*据作者↑说是为了解决 Mac 无法获取窗口标题，遂退而求其次获取浏览器页面（有系统就有浏览器，即有用户脚本）*

- [点击安装 (GitHub raw)](https://raw.githubusercontent.com/wyf9/sleepy/main/client/页面标题上报脚本-2024.12.2.user.js)

- [点击安装 (ghp.ci)](https://ghp.ci/https://raw.githubusercontent.com/wyf9/sleepy/main/client/页面标题上报脚本-2024.12.2.user.js)

### Configure

> 文件 [L18-L25](https://github.com/wyf9/sleepy/blob/main/client/页面标题上报脚本-2024.12.2.user.js#L18-L25) 的配置如下:

```js
// 参数配置开始
const API_URL = 'https://sleepy.wyf9.top/device/set'; // 你的完整 API 地址，以 `/device/set` 结尾
const SECRET = '绝对猜不出来的密码'; // 你的 secret
const ID = '114514'; // 你的设备 id
const SHOW_NAME = '设备名称'; // 替换为你的设备名称
const NO_TITLE = 'url'; // 定义页面没有标题时的返回，url: 页面的完整 url 地址 / host: 域名 / 其他: 对应值
// [!!!] 请将第 10 行 `@connect` 处的域名改为你的服务域名，如此处就应为 sleepy.wyf9.top
// 参数配置结束
```

## [Homework](./homework_device.py)

> by: [@wyf9](https://github.com/wyf9)

一个手动设置设备状态的示例 *(用来展示你的作业进度)*

依赖: `requests`

### Configure

只有两个配置:

- `SERVER`: 服务器地址，末尾不带 `/`，如：`https://sleepy.wyf9.top`
- `SECRET`: 同名

### Using

脚本提供了两个函数:

- `left(num: int)`: 设置剩余作业的数量 (为 `0` 则移除)
- `writing(name: str)`: 设置正在写的作业 (名称为空字符串则移除)

那么，如何使用这两个函数呢？

1. 直接使用

使用 `python homework_device.py` 直接打开, 并用执行函数 *(`eval()`)* 的方式发送请求，

如：`left(114514)`

> 如何将多个调用写在一行？可用逗号分隔：`left(114513), writing('五 年 中 考 三 年 模 拟')`

2. 其他程序调用

```py
from time import sleep
from homework_device import left, writing # import

for i in range(114514, 1, -1):
    left(i)
    writing(f'My Homework #{i}')
    sleep(1145)
```

## Other repos

> 在功能 / API 实现上有不同，需要进行修改以与本分支适配 (见 [API #device-set](../doc/api.md#device-set))

- [1812z/sleepy] Android [Macrodroid](https://www.bing.com/search?q=Macrodroid%20download): [(main) `前台应用状态.macro`](https://github.com/1812z/sleepy/blob/main/%E5%89%8D%E5%8F%B0%E5%BA%94%E7%94%A8%E7%8A%B6%E6%80%81.macro)
- [HBWuChang/sleepy] Android Magisk: [(main) `_example/win.py`](https://github.com/HBWuChang/sleepy/blob/main/_example/win.py) *(详见脚本同目录下 `/magisk`)*
- [HBWuChang/sleepy] Windows Python: [(main) `_example/win.py`](https://github.com/HBWuChang/sleepy/blob/main/_example/win.py)