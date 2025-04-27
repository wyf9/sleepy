# 贡献指南

## 一般步骤

1. 首先要 Fork 本仓库，否则无法推送更改哦
2. Clone 你的仓库到本地
3. 进行功能修改 (包括写代码和测试)
4. 提交并推送更改
5. 创建 pr (Pull Request)
6. 等待我们合并即可~

> [!TIP]
> 最好自己测试没有问题了再创建 pull request 哦 <br/>
> 也可以创建一个 draft *(草稿)* pull request，等功能写好再转成普通的 pr <br/>
> *开发过程中遇到任何问题可以 [联系我们](https://siiway.top/about/contact)~*

## 项目结构

> *以 `/` 结尾的为目录*，否则就是文件

```ini
### 根目录程序 ###
-> server.py # 服务主程序 (入口文件)
-> data.py # 运行中的状态存储 (就是管 data.json 的)
-> env.py # 读取 .env 和环境变量中的配置
-> setting.py # 读取 setting/ 下的配置 json
-> utils.py # 常用函数 / 小功能
-> _utils.py # utils.py 和 env.py 都用到的函数
-> start.py # 简易启动器
-> __init__.py # 我也不知道干嘛用的
-> install_lib.bat # 依赖安装脚本 (Windows)
-> install_lib.sh # 依赖安装脚本 (Unix-like)
```

```ini
### 子目录 ###
-> client/ # 客户端
-> doc/ # 文档 (部署 / 使用 / API)
# |-> plugin/ # 插件 - 还在构思(
-> templates/ # Flask 模板文件夹 (HTML)
-> static/ # Flask 静态文件 (CSS / JS, 可以用 /static/文件名 访问)
-> tools/ # 开发用的小工具 (实际上就一个)
```

```ini
### 用户可修改配置 / 模板 ###
-> .env.example # 环境变量 (配置) 的示例
-> setting/ # 独立于 .env 的设置? (一般是 json 文件存储的列表)
-> data.template.json # 状态文件模板
```

```ini
### 社区基础 (Community Standards) ###
-> README.md # 自述文件
-> LICENSE # 版权声明
-> CONTRIBUTING.md # 贡献指南 (本文件)
-> SECURITY.md # 安全准则
```

```ini
### 特定平台配置 ###
-> .github/ # GitHub 配置文件夹
  |-> ISSUE_TEMPLATE/ # Issue 模板
  |-> PULL_REQUEST_TEMPLATE # PR 模板
-> .vscode/ # VSCode 配置文件夹
-> .gitignore # Git 忽略文件
-> requirements.txt # Python 依赖列表
```

> [!IMPORTANT]
> **千万不要**将 `.env` 和 `data.json` 包含在提交中！ *(`.env` 有服务器 secret)*

## 代码风格

- 缩进: **4** 或 2 个空格 *(非强制)*
- 编码: UTF-8
- *是的，没了~*

> *[查看 Prettier 配置](./.prettierrc.json)*