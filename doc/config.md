# 配置项说明

有三种方式修改配置:

1. `data/config.yaml` 或 `data/config.toml` 文件 **(优先级最高)**
2. 环境变量
3. `.env` 文件 _(不建议使用)_

> [!IMPORTANT] > _(特别是 Windows 用户)_ 请确保所有配置文件 **使用 `UTF-8` 编码保存**，否则会导致 **错误读入注释 / 中文乱码** 等异常情况 <br/>
> Huggingface / Vercel 等容器平台部署需将环境变量放在 **`Environment Variables`** _(见 [部署文档](./deploy.md))_ <br/> > _修改配置后需重启服务生效_

<details>
<summary>配置文件格式与环境变量的转换</summary>

在 `data/config.yaml` 中，`main.host` _(str)_, `main.port` _(int)_, `main.debug` _(bool)_ 可以这样配置:

```yaml
main:
    host: '0.0.0.0'
    port: 9010
    debug: false
```

也可以这样配置:

```yaml
main.host: '0.0.0.0'
main.port: 9010
main.debug: false
```

在 `data/config.toml` 中，相同的配置是这样的:

```toml
[main]
host = "0.0.0.0"
port = 9010
debug = false
```

转换到环境变量和 `.env` 就是这样配置:

```ini
sleepy_main_host = "0.0.0.0"
sleepy_main_port = 9010
sleepy_main_debug = false
```

</details>

---

> **配置类型** <br/>
>
> -   `str`: 字符串
> -   `int`: 整数
> -   `bool`: 布尔值，可选 `true` **(是)** / `false` **(否)**
> -   `list`: 列表 **_(只能在配置文件里配置)_**
> -   `dict`: 字典 **_(只能在配置文件里配置)_**

> 配置的默认值见 [`config.default.yaml`](../config.default.yaml)

## (main) 系统基本配置

| 名称                      | 类型 | 说明                                                                                                          |
| ------------------------- | ---- | ------------------------------------------------------------------------------------------------------------- |
| `main.host`               | str  | 服务的监听地址，如需同时监听 IPv6 地址需改为 `::`                                                             |
| `main.port`               | int  | 服务的监听端口 _(0-65535)_                                                                                    |
| `main.debug`              | bool | 控制是否开启 Flask 的调试模式 (一般无需开启) _(开启后可自动重载代码)_                                         |
| `main.log_file`           | str  | 日志文件路径 (建议: `./data/running.log`), 留空禁用保存日志 **(注意: 不会切割日志, 请注意日志文件大小!)**                                  |
| `main.timezone`           | str  | 控制 **API 返回中 / 网页上**显示时间的时区，一般无需更改 _(`Asia/Shanghai` 或 `Asia/Chongqing` 均为北京时间)_ |
| `main.checkdata_interval` | int  | 控制多久检查一次状态数据的更新 **(秒)** (_检测到更新后会写入 `data.json`，供下次启动时恢复状态_)              |
| `main.secret`             | str  | 密钥 (相当于密码，用于防止未授权设置状态)，**客户端须使用相同的密钥**                                         |

---

## (page) 页面内容配置

| 名称                   | 类型 | 说明                                                                                                         |
| ---------------------- | ---- | ------------------------------------------------------------------------------------------------------------ |
| `page.name`            | str  | 网页顶部 `(名字)'s Status` 中的名字                                                                          |
| `page.title`           | str  | 标题栏中显示的网页标题                                                                                       |
| `page.desc`            | str  | 网页描述 _(主要用于 SEO)_                                                                                    |
| `page.favicon`         | str  | 网页的图标 (`.png` 或 `.ico` 图片) 路径，可以为绝对路径或相对路径                                            |
| `page.background`      | str  | 背景图片地址，可以使用网上的图片 API 或单张图片 _(默认为 [siiway/imgapi](https://github.com/siiway/imgapi))_ |
| `page.learn_more_text` | str  | 网页底部链接的**显示文字**                                                                                   |
| `page.learn_more_link` | str  | 网页底部链接的**目标** _(默认为本 repo 地址)_                                                                |
| `page.more_text`       | str  | 网页底部链接上方插入的文字 (**支持 HTML**，可以插入 统计代码 / 备案号 等)                                    |

<!-- | `page.hitokoto`        | bool | 在插入文字上方显示随机 [一言](https://hitokoto.cn)                                                           |
| `page.canvas`          | bool | 是否启用粒子效果 *(如影响性能可关闭)*                                                                        |
| `page.moonlight`       | bool | 在卡片左上角 / 右上角显示**切换暗色模式**和**卡片透明度**的按钮                                              |
| `page.lantern`         | bool | 在网页顶部显示节日灯笼 *(默认文字为 `欢度新春`)*                                                             |
| `page.mplayer`         | bool | 在网页左下角显示**音乐播放器**                                                                               |
| `page.zhixue`          | bool | 显示智学网分数 (详见 **[对应客户端设置](../client/README.md#zhixuewang)**)                                   | -->

## (status) 页面状态显示配置

| 名称                  | 类型 | 说明                                                                 |
| --------------------- | ---- | -------------------------------------------------------------------- |
| `status.device_slice` | int  | 网页中设备状态文本的最大长度，超过此长度会被截断 _(设置为 `0` 禁用)_ |
| `status.not_using`    | str  | 设备未在使用时显示的状态文本 _(如为空则使用设备上报值)_              |
| `status.sorted`       | bool | 是否按字母顺序排序设备列表                                           |
| `status.using_first`  | bool | 是否设置使用中设备优先显示                                           |
| `status.status_list`  | list | 手动设置状态的预设列表 _(`status` 即为索引)_                         |

<!-- ## (util) 可选功能

| 环境变量                      | 类型 | 说明与提示                                                                               |
| ----------------------------- | ---- | ---------------------------------------------------------------------------------------- |
| `util.metrics`                | bool | 控制是否启用内置的访问计数功能，并启用 `/metrics` 接口                                   |
| `util.auto_switch_status`     | bool | 是否启用自动切换状态 *(当状态为 `0` (活着) 且所有设备都未在使用时自动切换为 `1` (似了))* |
| `util.steam_enabled`          | bool | 是否启用新版 Steam 状态 *(iframe 卡片显示，需配置 `util_steam_ids`)*                     |
| `util.steam_ids`              | str  | 你的 Steam 账号 ID *(应为一串数字)*                                                      |
| `util.steam_refresh_interval` | int  | 刷新 Steam 状态的频率 (**毫秒**，*建议至少设置为 10000ms，过低可能触发速率限制*)         | --> |

## (metrics) 访问统计

| 名称                 | 类型 | 说明                                         |
| -------------------- | ---- | -------------------------------------------- |
| `metrics.enabled`    | bool | 是否启用 metrics 功能 (用于统计接口调用次数) |
| `metrics.allow_list` | list | 只有访问此列表中的路径才会计入统计           |
