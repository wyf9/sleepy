# sleepy

一个用于 ~~*视奸*~~ 查看个人在线状态 (以及正在使用软件) 的 Flask 应用，让他人能知道你不在而不是故意吊他/她

[**功能**](#功能) / [**TODO**](#todo) / [演示](#preview) / [**部署**](#部署) / [**使用**](#使用) / [**关于**](#关于)

## 功能

- 自行设置在线状态
- 实时更新设备打开应用 (名称)
- 美观的展示页面 [见 [Preview](#preview)]
- 开放的 Query / Metrics [接口](./doc/api.md), 方便统计

### 功能

- [x] **拆分 `config.jsonc` (只读) 和 `data.json`** (https://github.com/wyf9/sleepy/issues/3)
- [x] 网页使用 SSE *(Server Send Events)* 刷新状态
- [x] 网页使用 api 请求，并实现定时轮询刷新 *(备选方案)*
- [x] 设备使用状态 *(包括 是否正在使用 / 打开的应用名)*
- [x] Windows 客户端 (Python)
- [x] Android 客户端 ([Autox.js](https://github.com/aiselp/AutoX))
- [x] [查看更多客户端 (如浏览器脚本等)](./client/README.md)
- [x] Metrics API (统计页面访问 / 接口调用次数)
- [ ] **设备状态使用 Heartbeat 超时判定未在使用**
- [ ] ~~更多状态存储选项 (如 SQLite)~~

> [!TIP]
> **最新开发进度/ TODOs 见: [Discord Server](https://discord.gg/DyBY6gwkeg)** <br/>
> 如有 Bug / 建议, 可 [issue](https://github.com/wyf9/sleepy/issues/new) 或 [More contact](https://wyf9.top/#/contact) *(注明来意)*.

对智能家居 / Home Assistant 感兴趣的朋友，一定要看看 WinMEMZ 的 [sleepy 重生版](https://maao.cc/project-sleepy/): [maoawa/project-sleepy](https://github.com/maoawa/project-sleepy)!

### Preview

演示站 (*较*稳定): [sleepy.wyf9.top](https://sleepy.wyf9.top)

开发预览 (*不保证可用*): [sleepy-preview.wyf9.top](https://sleepy-preview.wyf9.top)

> 区别: 演示站为 wyf9 个人站点; 预览站允许测试 API，且直接运行开发版本 (**密钥 `wyf9test`**)

> [!WARNING]
> 不要拿演示站做坏事 (比如 js 注入，已由 DeepSeek 强力修复) ~~，没准哪天我会加访问日志~~

## 部署

理论上全平台通用, 安装了 Python >= **3.6** 即可 (建议: **3.10+**)

1. Clone 本仓库 (建议先 Fork / Use this template)

```shell
git clone --depth=1 -b main https://github.com/wyf9/sleepy.git
```

2. 安装依赖

```shell
pip install -r requirements.txt
```

3. 编辑配置文件

在目录下新建 `.env` 文件 (参考 `.env.example` 填写), 也可以直接设置相应的环境变量

> [!IMPORTANT]
> **[配置示例](./.env.example)** <br/>
> *注意: 环境变量的优先级**高于** `.env` 文件*

## 使用

> **使用宝塔面板 (uwsgi) 等部署时，请确定只为本程序分配了 1 个进程, 如设置多个服务进程可能导致数据不同步!!!**

有两种启动方式:

```shell
# 直接启动
python3 server.py
# 简易启动器
python3 start.py
```
默认服务 http 端口: **`9010`**

### 我承认你的代码写的确实很nb，但对我来说还是太吃操作了

> by [@kmizmal](https://github.com/kmizmal)

<details>

***<summary>点!此!展!开! (大图警告)</summary>***

有没有更简单无脑的方法推荐一下
**有的兄弟，有的！**
这样的方法有很多个，各个都是`GitHub` T<sub>0.5</sub>的操作
我怕教太多了你学不会，现在只要点
[这里](https://huggingface.co/spaces/sadg456/s?duplicate=true&visibility=public)  
然后自己去注册一个账号
参考`.env.example`在Setting==>Variables and secrets添加环境变量配置
然后在这里:
![链接](https://files.catbox.moe/svvdt6.png)
就可以复制你的`URL`，填入你选择的 **[`/client`](./client/README.md)** 对应的url配置中即可快速开始
</details>

## 客户端示例

如果你想直接开始使用，可在 **[`/client`](./client/README.md)** 找到客户端 (用于**手动更新状态**/**自动更新设备打开应用**)

## API

详细的 API 文档见 [doc/api.md](./doc/api.md).

## 优化站点

见 [Best Practice](./doc/best_practice.md).

> [!TIP]
> 想自定义你的状态列表 / metrics 统计白名单? **[见 Setting README](./setting/README.md)**

## 更新

```bash
git pull
pip install -r requirements.txt
```

> **Huggingface 更新** <br/>
> `Setting` ==> `Variables and secrets` ==> *更改对应的新增配置项* ==> **`Factory rebuild`**

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=wyf9/sleepy&type=Date)](https://star-history.com/#wyf9/sleepy&Date)

## 关于

本项目灵感由 Bilibili UP [@WinMEMZ](https://space.bilibili.com/417031122) 而来: [site](https://maao.cc/sleepy/) / [blog](https://www.maodream.com/archives/192/), 并~~部分借鉴~~使用了前端代码, 在此十分感谢。

[`templates/steam.html`](./templates/steam.html) 来自项目 [gamer2810/steam-miniprofile](https://github.com/gamer2810/steam-miniprofile).

**也欢迎参观 WinMEMZ *(GitHub: [maoawa](https://github.com/maoawa))* 的原版！[maoawa/sleepy](https://github.com/maoawa/sleepy)**

感谢 [@1812z](https://github.com/1812z) 的 B 站视频推广~ ([BV1LjB9YjEi3](https://www.bilibili.com/video/BV1LjB9YjEi3))
