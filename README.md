# sleepy

一个 ~~用于视奸~~ 查看个人在线状态 (以及正在使用软件) 的 Flask 网站，让他人能知道你不在而不是故意吊他/她

[**功能**](#功能) / [**TODO**](#todo) / [演示](#preview) / [**部署**](#部署) / [**使用**](#使用) / [**关于**](#关于)

## 功能

- 自行设置在线状态
- 实时更新设备打开应用 (名称)
- 美观的展示页面 [见 [Preview](#preview)]

### TODO

- [x] **拆分 `config.json` (只读) 和 `data.json`** (https://github.com/wyf9/sleepy/issues/3)
- [x] 网页使用 api 请求，并实现定时刷新
- [x] 设备使用状态
- [x] Windows 客户端 (Python)
- [x] Android 客户端 ([Autox.js](http://doc.autoxjs.com/))
- [ ] Metrics API (统计页面访问 / 接口调用次数)
- [ ] 设备状态尝试 Websocket (=↓)
- [ ] 设备状态 Heartbeat 机制
- [ ] 更多状态存储选项 (如 SQLite)

> [!TIP]
> 因上学原因 ***(临近期末)***, 可能放缓更新 <br/>
> **最新开发进度/ TODOs 见: [Discord Server](https://discord.gg/DyBY6gwkeg)** <br/>
> 如有 Bug / 建议, 可 [issue](https://github.com/wyf9/sleepy/issues/new) 或 [More contact](https://wyf9.top/#/contact) *(注明来意)*. <br/>

<!-- > 正在加急更新中 (请看 [dev-2025-1-1](https://github.com/wyf9/sleepy/tree/dev-2025-1-1) 分支) -->

### Preview

演示站 (稳定): [sleepy.wyf9.top](https://sleepy.wyf9.top)

开发预览 (*不保证可用*, 密钥 `wyf9test`): [sleepy-preview.wyf9.top](https://sleepy-preview.wyf9.top)

## 部署

> 从旧版本更新? 请看 [config.json 更新记录](./doc/config_json_update.md) <br/>
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

如果不出意外，会提示: `config.json not exist, creating`，同时目录下出现 `config.json` 文件，编辑该文件中的配置后重新运行即可

`>>` **[配置示例](./example.jsonc)** `<<` *(`config.json` 从此生成)*

## 使用

有两种启动方式:

```shell
# 直接启动
python3 server.py
# 简易启动器
python3 start.py
```

默认服务 http 端口: **`9010`** *(可在 `config.json` 中修改)*

## 客户端示例

如果你想直接开始使用，可在 **[`/client`](./client/README.md)** 找到客户端 (用于**手动更新状态**/**自动更新设备打开应用**)

## API

详细的 API 文档见 [doc/api.md](./doc/api.md).

## 关于

本项目灵感由 Bilibili UP [@WinMEMZ](https://space.bilibili.com/417031122) 而来: [site](https://maao.cc/sleepy/) / [blog](https://www.maodream.com/archives/192/), 并~~部分借鉴~~使用了前端代码, 在此十分感谢。

也欢迎参观 WinMEMZ *(GitHub: [maoawa](https://github.com/maoawa))* 的原版！[maoawa/sleepy](https://github.com/maoawa/sleepy)

感谢 [@1812z](https://github.com/1812z) 的 B 站视频推广~ ([BV1LjB9YjEi3](https://www.bilibili.com/video/BV1LjB9YjEi3))
