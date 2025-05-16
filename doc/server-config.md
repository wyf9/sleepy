# 服务器配置

> [!WARNING]
> 本文 100% 由 AI 编写，不保证以下内容的准确性

- [服务器配置](#服务器配置)
  - [配置文件](#配置文件)
  - [配置项说明](#配置项说明)
  - [Linux 服务管理](#linux-服务管理)
    - [自动注册为系统服务](#自动注册为系统服务)
    - [服务管理面板](#服务管理面板)
    - [配置管理](#配置管理)

## 配置文件

> *配置文件: `.env`*

在目录下新建 `.env` 文件 (参考 [`.env.example`](../.env.example) 填写), *也可以直接设置相应的环境变量*

> [!TIP]
> `scripts/install.sh` 脚本会自动创建 `.env` 文件并生成随机密钥，建议使用该脚本进行安装。
> 请勿将 `.env` 文件提交到版本控制系统中，如 Git，以保护您的敏感信息。

> [!IMPORTANT]
> **[配置示例](../.env.example)** <br/>
> **Windows 用户请确保 `.env` 文件以 UTF-8 编码而非 GBK 编码保存，否则读取可能出现问题!** *(如**错误读入行尾注释**)* <br/>
> *注意: 环境变量的优先级**高于** `.env` 文件* <br/>

## 配置项说明

以下内容不会更新。请查看 [ENV.MD](./env.md)。

以下是主要配置项的说明：

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| `SLEEPY_SECRET` | 用于客户端认证的密钥 | 必填 |
| `SLEEPY_PORT` | 服务器监听端口 | `9010` |
| `SLEEPY_HOST` | 服务器监听地址 | `0.0.0.0` |
| `SLEEPY_TITLE` | 页面标题 | `Sleepy` |
| `SLEEPY_SUBTITLE` | 页面副标题 | `Status Page` |
| `SLEEPY_DESCRIPTION` | 页面描述 | `A simple status page` |
| `SLEEPY_THEME` | 页面主题 | `auto` |
| `SLEEPY_LANG` | 页面语言 | `zh-CN` |
| `SLEEPY_TIMEZONE` | 时区 | `Asia/Shanghai` |
| `SLEEPY_DATA_FILE` | 数据文件路径 | `data.json` |
| `SLEEPY_LOG_LEVEL` | 日志级别 | `INFO` |
| `SLEEPY_HTTPS` | 是否启用 HTTPS | `false` |
| `SLEEPY_CERT_FILE` | SSL 证书文件路径 | - |
| `SLEEPY_KEY_FILE` | SSL 密钥文件路径 | - |

## Linux 服务管理

### 自动注册为系统服务

在 Linux 系统上，安装脚本现在支持将 Sleepy 自动注册为 systemd 服务，这样可以实现开机自启动和更方便的管理。

在运行 `scripts/install.sh` 时，脚本会询问是否要注册为系统服务：

```bash
Do you want to register Sleepy as a systemd service? (y/n):
```

选择 `y` 后，脚本会：

1. 创建 systemd 服务文件 `/etc/systemd/system/sleepy.service`
2. 启用服务自动启动
3. 创建管理面板脚本 `panel.sh`
4. 提供 `sleepy` 命令别名设置指南

### 服务管理面板

安装完成后，可以通过以下方式使用管理面板：

1. 设置别名：
   ```bash
   alias sleepy='/home/azureuser/sleepy/scripts/panel.sh'
   ```

   请将路径替换为您的实际安装路径。

2. 使用管理命令：
   ```bash
   sleepy start     # 启动服务
   sleepy stop      # 停止服务
   sleepy restart   # 重启服务
   sleepy status    # 查看服务状态
   sleepy logs      # 查看服务日志
   sleepy follow    # 实时查看日志
   sleepy enable    # 启用开机自启
   sleepy disable   # 禁用开机自启
   ```

3. 交互式管理界面：
   ```bash
   sleepy
   ```

   这将打开一个交互式菜单，可以通过数字选择各种管理选项。

### 配置管理

管理面板提供了配置文件管理功能，可以方便地查看和修改配置：

1. 查看配置：
   ```bash
   sleepy config       # 查看完整配置文件
   sleepy config-list  # 列出所有配置项
   sleepy secret       # 查看密钥
   ```

2. 修改配置：
   ```bash
   sleepy config-set KEY VALUE  # 设置配置值
   ```

   例如：
   ```bash
   sleepy config-set SLEEPY_TITLE "我的状态页"
   sleepy config-set SLEEPY_PORT 8080
   ```

3. 交互式配置编辑：

   在交互式菜单中选择"编辑配置"选项，可以通过菜单方式修改配置。
