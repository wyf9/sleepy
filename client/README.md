# /client

此目录存储客户端 (用于更新状态/设备状态)

- [/client](#client)
  - [CMDConsole](#cmdconsole)
  - [Configure](#configure)
  - [Using](#using)
  - [CmdConsoleMulti](#cmdconsolemulti)
  - [Configure](#configure-1)
  - [Using](#using-1)
  - [WinDevice](#windevice)
    - [Configure](#configure-2)
  - [AutoxjsScript](#autoxjsscript)
    - [Configure](#configure-3)
    - [Using](#using-2)
  - [BrowserScript](#browserscript)
    - [Configure](#configure-4)
  - [Homework](#homework)
    - [Configure](#configure-5)
    - [Using](#using-3)
  - [MinecraftScript](#minecraftscript)
    - [Minescript](#minescript)
    - [Configure](#configure-6)
    - [Using](#using-4)
    - [Autorun](#autorun)
  - [LinuxScriptKDE](#linuxscriptkde)
    - [Configure](#configure-7)
    - [Using](#using-5)
  - [LinuxScriptHyprland](#linuxscripthyprland)
    - [Configure](#configure-8)
    - [Using](#using-6)
  - [Other repos](#other-repos)

> [!TIP]
> 欢迎提交 Issue / PR 贡献自己的脚本！

## [CMDConsole](./cmd_console.py)

> by: [@wyf9](https://github.com/wyf9)

一个简单的命令行客户端，用于手动更新状态

依赖: `requests`

## Configure

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/cmd_console.py#L14-L21

## Using

启动脚本, 按照提示操作即可

## [CmdConsoleMulti](./cmd_console_multi.py)

> by: [@wyf9](https://github.com/wyf9)

[CMDConsole](#cmdconsole) 的旧版本 (可选择多个服务)

## Configure

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/cmd_console_multi.py#L14-L23

## Using

同上, 多了一步选择服务

## [WinDevice](./win_device.py)

> by: [@wyf9](https://github.com/wyf9)

在 Windows 上自动更新设备状态

依赖: `requests`, `pywin32`

### Configure

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/win_device.py#L15-L31

> PM2 启动命令参考: `pm2 start python --name sleepywin -- -u win_device.py` **(不加 `-u` 参数会导致 `pm2 log` 命令没有输出)** <br/>
> 如使用 PM2 出现乱码请手动设置编码环境变量 (自行搜索)

## [AutoxjsScript](./autoxjs_device.js)

> by: [@wyf9](https://github.com/wyf9) <br/>
> Co-authored-by: [@NyaOH-Nahida](https://github.com/NyaOH-Nahida)

使用 [(Archive) Autox.js](https://web.archive.org/*/https://github.com/kkevsekk1/AutoX) 编写的安卓自动更新状态脚本

> [!WARNING]
> Autox.js 已删库，RIP <br/>
> 可自行寻找 Auto.js 的其他分支 **(可能需要作一些修改以兼容其他分支的方法)**

在使用前，请确保**已安装** Autox.js *且*授予**无障碍权限**

### Configure

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/autoxjs_device.js#L8-L15

### Using

启动后可点击 Autox.js 右上角的日志图标查看日志

![image](https://files.catbox.moe/x93248.png)

- 当手机息屏 (应用名返回为空) 时视为未在使用
- 当脚本退出时也会更新状态为未在使用 *(不包括 Autox.js 直接停止运行)*

## [BrowserScript](./页面标题上报脚本-2024.12.2.user.js)

> by: [@nuym](https://github.com/nuym)

在任何支持油猴脚本的浏览器均可使用，*据作者↑说是为了解决 Mac 无法获取窗口标题，遂退而求其次获取浏览器页面（有系统就有浏览器，即有用户脚本）*

- [点击安装 (GitHub raw)](https://raw.githubusercontent.com/wyf9/sleepy/main/client/页面标题上报脚本-2024.12.2.user.js)

- [点击安装 (ghp.ci)](https://ghp.ci/https://raw.githubusercontent.com/wyf9/sleepy/main/client/页面标题上报脚本-2024.12.2.user.js)

### Configure

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/页面标题上报脚本-2024.12.2.user.js#L18-L26

## [Homework](./homework_device.py)

> by: [@wyf9](https://github.com/wyf9)

一个手动设置设备状态的示例 *(用来展示你的作业进度)*

依赖: `requests`

### Configure

只有两个配置:

- `SERVER`: 服务器地址，末尾不带 `/`，如：`https://sleepy.wyf9.top`
- `SECRET`: 同名

### Using

脚本提供了一些函数:

- `left(num: int)`: 设置剩余作业的数量 (为 `0` 则移除) *[device id: `homework-left`]*
- `writing(name: str)`: 设置正在写的作业 (名称为空字符串则移除) *[device id: `homework-name`]*

还有一些扩展函数, 可以调用大部分 API
- `query()`: 查看当前状态 *(未格式化输出)*
- `lst()`: 查看可用状态列表 *(未格式化输出)*
- `status(stat: int)`: 设置状态
- `device_set(id: str, show_name: str, msg: str, using: bool = True)`: 设备状态设置
- `device_remove(id: str)`: 移除设备状态
- `device_clear()`: 清除设备状态

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
    sleep(11.45)
```

## [MinecraftScript](./mc_script.py)

> by: [@wyf9](https://github.com/wyf9)

依赖: `requests`

一个使用 Minescript mod 在 Minecraft Java 版中上报游戏内信息的脚本

### Minescript

在使用前, 你需要下载 Minescript mod:

Links: [MCMod.cn](https://www.mcmod.cn/class/7594.html) / [Modrinth](https://modrinth.com/mod/minescript) / [Repo](https://github.com/maxuser0/minescript)

> 也可在各大启动器的 Modrinth 源中直接下载

在下载并启动一次后, 打开 `.minecraft/versions/你的版本/minescript/` 目录, 并进行两个操作:

1. 新建 `config.txt`, 内容:

```txt
# Lines starting with "#" are ignored.
# 替换为你的 Python 可执行程序路径
python="C:\Program Files\Python312\python.exe"
```

2. 将 [`mc_script.py`](./mc_script.py) 复制到此目录, 并改名为 `sleepy.py` (也可为其他名字)

### Configure

需要配置两处:

1. 基本服务

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/mc_script.py#L16-L24

2. `app_name` 格式

https://github.com/wyf9/sleepy/blob/e6b77af1e4333ad570983b5bf9ac397cb1d40d7b/client/mc_script.py#L116

### Using

配置完成后重启 Minecraft 进入游戏, 按 `T` *(默认键位, 可能不同)* 打开聊天栏, 并输入: `\sleepy` **(即上面重命名后的文件名去掉 `.py` 后缀)* 回车启动

停止: `\sleepy stop`

### Autorun

也可以配置自启, 只需在 `config.txt` 中新增一行:

```txt
autorun[*]=eval 'execute("\\sleepy")'
```

## [LinuxScriptKDE](./linux_device_kde.py)

> by: [@RikkaNaa](https://github.com/RikkaNaa)

适用于 Linux KDE 桌面环境，且需要系统安装 [kdotool](https://github.com/jinliu/kdotool)

如获取失败则视为未在使用，[变量计时参考](https://github.com/RikkaNaa/sleepy/commit/9d5b4fc2014b725df24304beaa9439a5eb07099b)

### Configure

https://github.com/wyf9/sleepy/blob/7fc21380a259247533db76f3a0443fa550fcffec/client/linux_device_kde.py#L18-L28

### Using

可自行配置本脚本的自启动

> 当进程接收到 `SIGTERM` 信号时将会发送未在使用请求

## [LinuxScriptHyprland](./linux_device_hyprland.sh)

> by: [@inoryxin](https://github.com/inoryxin)

适用于 Linux Hyprland 桌面环境，无需任何依赖，开箱即用

### Configure

https://github.com/wyf9/sleepy/blob/7fc21380a259247533db76f3a0443fa550fcffec/client/linux_device_hyprland.sh#L7-L12

### Using

直接启动即可

> 开机自启可自行在 `hyprland.conf` 中配置

## Other repos

> 在功能 / API 实现上有不同，需要进行修改以与本分支适配 (见 [API #device-set](../doc/api.md#device-set))

- [1812z/sleepy] Android [Macrodroid](https://www.bing.com/search?q=Macrodroid%20download): [(main) `前台应用状态.macro`](https://github.com/1812z/sleepy/blob/main/%E5%89%8D%E5%8F%B0%E5%BA%94%E7%94%A8%E7%8A%B6%E6%80%81.macro)
- [HBWuChang/sleepy] Android Magisk: [(main) `_example/win.py`](https://github.com/HBWuChang/sleepy/blob/main/_example/win.py) *(详见脚本同目录下 `/magisk`)*
- [HBWuChang/sleepy] Windows Python: [(main) `_example/win.py`](https://github.com/HBWuChang/sleepy/blob/main/_example/win.py)