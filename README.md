# sleepy

一个用于 ~~*视奸*~~ 查看个人在线状态 (以及正在使用软件) 的 Flask 应用，让他人能知道你不在而不是故意吊他/她

[**功能**](#功能) / [**演示**](#preview) / [**部署**](#部署--更新) / [**Client**](#client) / [**API**](#api) / [**关于**](#关于)

## 功能

- [x] 自行设置在线状态 *(活着 / 似了 等, 也可自定义状态)*
- [x] 实时更新设备使用状态 *(包括 是否正在使用 / 打开的应用名, 通过 **[客户端](./client/README.md)** 主动推送)*
- [x] 美观的展示页面 [见 **[Preview](#preview)**]
- [x] 开放的 状态 / 统计 **[API](./doc/api.md)**

> [!TIP]
> **最新 开发进度 / TODOs 见: [Discord][link-dc]** / [Telegram][link-tg] / [QQ][link-qq]<br/>
> 如有 Bug / 建议, 可发 issue (**[Bug][link-issue-bug]** / **[Feature][link-issue-feature]**) 或选择上面的联系方式 *(注明来意)*.

### Preview

演示站: [sleepy.wyf9.top](https://sleepy.wyf9.top)

<details>

<summary>展开更多</summary>

**开放预览站**: [sleepy-preview.wyf9.top](https://sleepy-preview.wyf9.top)  
**HuggingFace** 部署预览: [wyf9-sleepy.hf.space](https://wyf9-sleepy.hf.space)  
**Vercel** 部署预览: [sleepy-vercel.wyf9.top](https://sleepy-vercel.wyf9.top)  
**开发服务器**: [请在 Discord 服务器获取](link-dc)

你可以在开发预览站测试最新功能和API, 但不保证稳定性 / 安全性.

</details>

## 部署 / 更新

请移步 **[部署教程](./doc/deploy.md)** 或 **[更新教程](./doc/update.md)** *(多图警告)*

## Client

如果你想直接开始使用，可在 **[`/client`](./client/README.md)** 找到客户端 (用于**手动更新状态**/**自动更新设备打开应用**)

## API

详细的 API 文档见 [doc/api.md](./doc/api.md).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=wyf9/sleepy&type=Date)](https://star-history.com/#wyf9/sleepy&Date)

## 关于

本项目灵感由 Bilibili UP [@WinMEMZ](https://space.bilibili.com/417031122) 而来: **[site](https://maao.cc/sleepy/)** / **[blog](https://www.maodream.com/archives/192/)** / **[repo: `maoawa/sleepy`](https://github.com/maoawa/sleepy)**, 并~~部分借鉴~~使用了前端代码, 在此十分感谢。

[`templates/steam-iframe.html`](./templates/steam-iframe.html) 来自 repo **[gamer2810/steam-miniprofile](https://github.com/gamer2810/steam-miniprofile).**

---

对智能家居 / Home Assistant 感兴趣的朋友，一定要看看 WinMEMZ 的 [sleepy 重生版](https://maao.cc/project-sleepy/): **[maoawa/project-sleepy](https://github.com/maoawa/project-sleepy)!**

感谢 [@1812z](https://github.com/1812z) 的 B 站视频推广~ **([BV1LjB9YjEi3](https://www.bilibili.com/video/BV1LjB9YjEi3))**

[link-dc]: https://wyf9.top/t/sleepy/dc
[link-tg]: https://wyf9.top/t/sleepy/tg
[link-qq]: https://wyf9.top/t/sleepy/qq
[link-issue-bug]: https://wyf9.top/t/sleepy/bug
[link-issue-feature]: https://wyf9.top/t/sleepy/feature
