# sleepy

Are you sleeping?

一个查看个人在线状态的 Flask 网站，让他人能知道你不在而不是故意吊他/她

[演示站](https://sleepy.wyf9.top) / [部署](#部署) / [使用](#使用) / [关于](#关于)

## 部署

理论上全平台通用, 安装了 Python 即可 *(开发环境: Debian linux)*

1. Clone 本仓库 (建议先 Fork)

```shell
git clone https://github.com/wyf9/sleepy.git
# or ssh:
git clone git@github.com:wyf9/sleepy.git
```

2. 安装依赖

```shell
cd sleepy
./install_lib.sh
# or windows:
.\install_lib.bat
# 也可自行安装: pip install -r requirements.txt
```

3. 编辑配置文件

先启动一遍程序:

```shell
python3 server.py
```

如果不出意外，会提示: `[Warning] [YYYY-MM-DD hh:mm:ss] data.json not exist, creating`，同时目录下出现 `data.json` 文件，编辑该文件中的配置即可 (示例请 [查看 `example.jsonc`](./example.jsonc) )

## 使用

有两种启动方式:

- 直接启动

```shell
python3 server.py
```

- 简易启动器

```shell
python3 start.py
```

相比直接启动, 启动器可实现在服务器退出后自动重启

<details>
<summary>点击展开</summary>

```shell

```

</details>


默认服务 http 端口: `9010`

| 路径                                   | 作用                |
| -------------------------------------- | ------------------- |
| `/`                                    | 显示主页            |
| `/query`                               | 获取状态            |
| `/get/status_list`                     | 获取可用状态列表    |
| `/set?secret=<secret>&status=<status>` | 设置状态 (url 参数) |
| `/set/<secret>/<status>`               | 设置状态 (路径)     |

> 以下是 4 个接口的解释

1. `/query`:

获取当前的状态 (无需鉴权)

返回 json:

```jsonc
{
    "success": true, // 请求是否成功
    "status": 0, // 获取到的状态码
    "info": { // 对应状态码的信息
        "name": "活着", // 状态名称
        "desc": "目前在线，可以通过任何可用的联系方式联系本人。", // 状态描述
        "color": "awake"// 状态颜色, 对应 static/style.css 中的 .sleeping .awake 等类
    }
}
```

2. `/get/status_list`

获取可用状态的列表 (无需鉴权)

返回 json:

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

> 就是返回 `data.json` 中的 `status_list` 字段

3. `/set?secret=<secret>&status=<status>`

设置当前状态

- `<secret>`: 在 `data.json` 中配置的 `secret`
- `<status>`: 状态码 *(`int`)*

返回 json:

```jsonc
// 1. 设置成功
{
    "success": true, // 请求是否成功
    "code": "OK", // 返回代码
    "set_to": 0 // 设置到的状态码
}

// 2. 失败 - 未验证
{
    "success": false, // 请求是否成功
    "code": "not authorized", // 返回代码
    "message": "invaild secret" // 详细信息
}

// 3. 失败 - 请求无效
{
    "success": false, // 请求是否成功
    "code": "bad request", // 返回代码
    "message": "argument 'status' must be a number" // 详细信息
}
```

4. `/set/<secret>/<status>`

同上 `2.`, 唯一的不同是 url 格式

### 个性化

Fork 后可自行更改代码以实现更多功能

- 站点图标: `static/favicon.ico`
- 背景图: `static/style.css` 注释处

## 关于

本项目灵感由 Bilibili UP @ [WinMEMZ](https://space.bilibili.com/417031122) 而来: [site](https://maao.cc/sleepy/) / [blog](https://www.maodream.com/archives/192/), 并部分借鉴了前端代码。

如有 Bug / 建议, 请 [issue](https://github.com/wyf9/sleepy/issues/new).