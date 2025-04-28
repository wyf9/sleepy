# ENV 文件说明

本文档详细介绍了 `.env` 文件中可配置的环境变量及其作用。`.env` 文件允许您自定义 Sleepy 应用的各项行为和显示效果。

**重要提示:**
*   **创建 `.env` 文件:** 如果您是手动部署，需要在项目的根目录下（与 `server.py` 同级）手动创建一个名为 `.env` 的文件。您可以复制 `.env.example` 文件并将其重命名为 `.env` 作为起点。
*   **文件编码:** Windows 用户请特别注意，务必确保 `.env` 文件使用 **UTF-8** 编码保存，否则可能导致读取配置出错或中文乱码。
*   **重启生效:** 修改 `.env` 文件后，通常需要**重新启动 Sleepy 服务**才能让新的配置生效。
*   **优先级:** 直接设置的环境变量（例如在系统环境变量中设置或通过 Docker/Vercel 等平台设置）的优先级**高于** `.env` 文件中的配置。
*   **平台配置:** 对于 Huggingface 和 Vercel 等平台部署，这些变量需要在平台的“Settings”或“Environment Variables”区域进行配置，而不是通过 `.env` 文件。具体请参考 [部署文档](./deploy.md) 和 [更新文档](./update.md)。

---

## (main) 系统基本配置

这部分配置控制着 Sleepy 服务运行的基础设置。

| 环境变量                      | 类型    | 默认值          | 说明与提示                                       |
| ----------------------------- | ------- | --------------- | ------------------------------------------ |
| `sleepy_main_host`            | `str`   | `"0.0.0.0"`     | **监听地址:**<br/> - `"0.0.0.0"` (或 IPv6 的 `"::"`) 表示允许**任何** IP 地址访问您的 Sleepy 页面，这在服务器或 Docker 环境中很常用。<br/> - 如果只想本机访问，可以设置为 `"127.0.0.1"` 或 `"localhost"`。<br/> - **注意:** 请确保您的防火墙允许所选地址和端口的入站连接。 |
| `sleepy_main_port`            | `int`   | `9010`          | **监听端口:** Sleepy 服务监听的网络端口号。<br/> - **提示:** 如果 `9010` 端口已被其他程序占用，您需要修改为其他未被占用的端口（例如 `9011`）。 |
| `sleepy_main_debug`           | `bool`  | `false`         | **调试模式:**<br/> - `true`: 启用 Flask 的调试模式。这会在代码更改时自动重载服务，并在出错时显示详细的错误信息，方便开发调试。<br/> - `false`: 关闭调试模式，这是**生产环境**的推荐设置，更安全、性能更好。<br/> - **警告:** **切勿**在公开访问的生产环境中启用调试模式，这可能带来安全风险。 |
| `sleepy_main_timezone`        | `str`   | `"Asia/Shanghai"` | **时区设置:** 控制网页上显示的时间（例如“最后更新于”）以及 API 返回的时间所使用的时区。<br/> - **提示:** 请根据您所在的地理位置或偏好设置合适的时区，例如 `"America/New_York"` 或 `"Europe/London"`。有效的时区名称列表可以在网上找到（搜索 "tz database time zones"）。 |
| `sleepy_main_checkdata_interval` | `int`   | `30`            | **数据文件检查间隔 (秒):** Sleepy 会定期检查 `data.json` 文件是否有手动修改。这里设置检查的频率。<br/> - **提示:** 如果您不经常手动编辑 `data.json`，可以适当增大此值以减少不必要的检查。如果设置为 `0` 或负数，则禁用自动检查。 |
| `SLEEPY_SECRET`               | `str`   | `""`            | **API 鉴权密钥:** 用于保护需要身份验证的 API 接口（例如 `/api/status` 的 POST 请求）。<br/> - **重要:** 如果您启用了需要鉴权的客户端（如 `win_device.py` 的某些功能），**必须**设置一个**复杂且随机**的密钥，并确保客户端和服务端的密钥一致。<br/> - **提示:** 留空表示禁用 API 鉴权。 |

---

## (page) 页面内容配置

这部分配置控制着 Sleepy 状态展示页面的外观和内容。

| 环境变量                 | 类型    | 默认值                          | 说明与提示                                                         |
| ------------------------ | ------- | ------------------------------- | ------------------------------------------------------------ |
| `sleepy_page_title`      | `str`   | `"User Alive?"`                 | **页面标题:** 显示在浏览器标签页上的文字。 |
| `sleepy_page_desc`       | `str`   | `"User's Online Status Page"`   | **页面描述:** 主要用于搜索引擎优化 (SEO)，帮助搜索引擎了解页面内容。 |
| `sleepy_page_favicon`    | `str`   | `"./static/favicon.ico"`        | **页面图标 (Favicon):** 显示在浏览器标签页标题旁边的小图标。<br/> - **提示:** 可以使用相对路径（相对于项目根目录）或完整的 URL。建议使用 `.ico`, `.png` 或 `.svg` 格式。 |
| `sleepy_page_user`       | `str`   | `"User"`                        | **显示的用户名:** 在页面顶部显示的用户名或昵称。 |
| `sleepy_page_background` | `str`   | `"https://imgapi.siiway.top/image"` | **背景图片 URL:**<br/> - **提示:** 您可以替换为您喜欢的任何图片 URL。建议使用加载速度快、分辨率合适的图片。如果 URL 失效或加载缓慢，会影响页面体验。也可以使用本地图片路径，例如 `"./static/my_background.jpg"` (需要将图片放入 `static` 文件夹)。 |
| `sleepy_page_learn_more` | `str`   | `"GitHub Repo"`                 | **“了解更多”链接文本:** 页面底部链接显示的文字。 |
| `sleepy_page_repo`       | `str`   | `"https://github.com/wyf9/sleepy"` | **“了解更多”链接目标 URL:** 点击上述链接后跳转的网址。 |
| `sleepy_page_more_text`  | `str`   | `""`                            | **额外页脚文本:** 在状态页底部“了解更多”链接上方插入的额外内容。<br/> - **提示:** 支持 HTML 代码。常用于添加网站访问量统计代码（如 [不蒜子](https://busuanzi.ibruce.info/)、Google Analytics 等），或其他版权信息、备案号等。具体用法可参考 [最佳实践文档](./best_practice.md#添加访问量统计)。 |
| `sleepy_page_sorted`     | `bool`  | `false`                         | **设备列表排序:**<br/> - `true`: 页面上显示的设备列表将按设备名称的字母顺序排序。<br/> - `false`: 按 `data.json` 文件中的原始顺序或更新顺序显示。 |
| `sleepy_page_hitokoto`   | `bool`  | `true`                          | **显示一言:**<br/> - `true`: 在页面顶部加载并显示一条来自 [hitokoto.cn](https://hitokoto.cn/) 的句子。 |
| `sleepy_page_canvas`     | `bool`  | `true`                          | **背景粒子效果:**<br/> - `true`: 加载并显示动态的背景粒子动画效果。<br/> - **提示:** 如果觉得影响性能或不喜欢，可以设置为 `false` 关闭。 |
| `sleepy_page_moonlight`  | `bool`  | `true`                          | **暗色模式与透明度:**<br/> - `true`: 在页面右下角启用一个控制按钮，允许用户切换页面的暗色/亮色模式，并调整卡片背景的透明度。 |
| `sleepy_page_lantern`    | `bool`  | `false`                         | **节日灯笼效果:**<br/> - `true`: 在页面两侧加载红灯笼挂饰效果，增添节日气氛（例如春节）。 |
| `sleepy_page_mplayer`    | `bool`  | `false`                         | **音乐播放器:**<br/> - `true`: 在页面底部加载一个简单的音乐播放器 (APlayer)。需要配合 `data.json` 中的 `mplayer` 配置项使用。 |
| `sleepy_page_zhixue`     | `bool`  | `false`                         | **智学网分数:**<br/> - `true`: 加载用于显示智学网考试分数的模块。需要配合 `data.json` 中的 `zhixue` 配置项和相应的客户端脚本使用。 |

---

## (status) 页面状态显示配置

这部分配置控制状态信息在页面上的具体展示方式。

| 环境变量                        | 类型    | 默认值       | 说明与提示                                                         |
| ------------------------------- | ------- | ------------ | ------------------------------------------------------------ |
| `sleepy_status_device_slice`    | `int`   | `30`         | **设备状态截断长度:** 设备状态信息（例如正在运行的应用名称）通常比较长，这里设置在页面上最多显示多少个字符。<br/> - **提示:** 设置为 `0` 表示不截断，显示完整的状态信息。根据您的设备状态信息长度和页面布局调整此值。 |
| `sleepy_status_show_loading`    | `bool`  | `true`       | **显示“更新中”提示:**<br/> - `true`: 当页面通过 SSE 或轮询请求新状态时，在状态区域短暂显示“更新中…”的提示，给用户明确的反馈。<br/> - `false`: 不显示此提示。 |
| `sleepy_status_refresh_interval`| `int`   | `5000`       | **状态自动刷新间隔 (毫秒):** 这个设置**仅**在浏览器不支持或无法建立 SSE (Server-Sent Events) 连接时生效。<br/> - **背景:** Sleepy 优先使用 SSE 技术实时推送状态更新。如果 SSE 不可用，页面会回退到传统的**轮询**方式，即每隔一段时间主动向服务器请求一次最新状态。这个变量就是设置轮询的时间间隔。<br/> - **提示:** `5000` 毫秒等于 5 秒。如果您的网络环境导致 SSE 经常失败，可以调整此值，但不建议设置得太小（例如小于 2000），以免对服务器造成不必要的压力。 |
| `sleepy_status_not_using`       | `str`   | `"未在使用"` | **强制“未使用”状态文本:** 当设备状态被判断为“未使用”（例如电脑锁屏、手机息屏）时，页面上强制显示的文本。<br/> - **提示:** 如果您希望显示设备端上报的原始“未使用”状态（例如“屏幕已锁定”），可以将此值设置为空字符串 `""`。 |
| `sleepy_status_device_offline_timeout` | `int` | `180` | **设备心跳超时时间 (秒):** 服务器判断设备是否离线的阈值。<br/> - **机制:** 客户端需要定期调用 `/device/set` 接口（即使状态不变）来发送心跳。如果服务器在指定秒数内没有收到来自某个设备的心跳，则会自动将该设备标记为离线 (`using=false`, `app_name='[Offline]'`)。<br/> - **提示:** 建议此值大于客户端的心跳间隔 (`HEARTBEAT_INTERVAL`)，例如客户端心跳为 60 秒，则此值可设为 180 秒 (3 倍心跳间隔)。 |

---

## (util) 可选功能

这部分配置启用或禁用 Sleepy 提供的一些额外功能。

| 环境变量                           | 类型    | 默认值   | 说明与提示                                                         |
| ---------------------------------- | ------- | -------- | ------------------------------------------------------------ |
| `sleepy_util_metrics`              | `bool`  | `true`   | **启用 Metrics 接口:**<br/> - `true`: 启用 `/metrics` 接口，该接口以 Prometheus 格式暴露一些基本的 API 调用统计信息，可用于监控。 |
| `sleepy_util_auto_switch_status`   | `bool`  | `true`   | **自动切换状态:**<br/> - `true`: 启用基于设备使用情况的自动状态切换逻辑。例如，当电脑长时间无操作或锁屏时，其状态可能会自动从“在线”切换为“离开”或“未使用”。<br/> - **提示:** 具体逻辑依赖于 `data.json` 中设备的 `auto_switch_status` 配置以及客户端上报的信息。 |
| `sleepy_util_steam_legacy_enabled` | `bool`  | `false`  | **启用旧版 Steam 状态 (文字模式):**<br/> - `true`: 在页面上显示指定 Steam 用户的在线状态和正在玩的游戏（纯文本显示）。<br/> - **依赖:** 需要同时配置 `sleepy_util_steam_key` 和 `sleepy_util_steam_ids`。<br/> - **注意:** 需要一个 Steam Web API 密钥。 |
| `sleepy_util_steam_enabled`        | `bool`  | `false`  | **启用新版 Steam 状态 (iframe 模式):**<br/> - `true`: 在页面上嵌入一个 Steam 官方提供的小部件 (iframe)，展示更丰富的 Steam 个人资料信息。<br/> - **依赖:** 只需要配置 `sleepy_util_steam_ids`。<br/> - **提示:** 这是**推荐**的 Steam 状态显示方式，不需要 API 密钥，展示效果更好。 |
| `sleepy_util_steam_key`            | `str`   | `""`     | **Steam Web API 密钥:** 用于**旧版** Steam 状态功能。<br/> - **获取:** 您可以从 [Steam 开发者社区](https://steamcommunity.com/dev/apikey) 申请一个 API 密钥。<br/> - **安全:** 请妥善保管您的 API 密钥，不要泄露。 |
| `sleepy_util_steam_ids`            | `str`   | `""`     | **Steam 用户 ID (64位):** 用于新版和旧版 Steam 状态功能。<br/> - **格式:** 填写您的 Steam 64位 ID (通常是一个很长的数字)。如果有多个用户，用英文逗号 `,` 分隔。<br/> - **查找:** 您可以通过 [SteamID Finder](https://steamid.io/) 等第三方网站，输入您的 Steam 个人资料链接来查找您的 64位 ID。 |
| `sleepy_util_steam_refresh_interval` | `int`   | `20000`  | **Steam 状态刷新间隔 (毫秒):** 从 Steam API 获取状态信息的频率。<br/> - **提示:** `20000` 毫秒等于 20 秒。过于频繁的请求可能会触发 Steam API 的速率限制。 |

---

**再次提醒:** 修改 `.env` 文件后，记得**重启 Sleepy 服务**以应用更改！
