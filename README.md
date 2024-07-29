# sleepy

Are you online/sleeping? / 个人在线状态监测

灵感由 Bilibili UP @ [WinMEMZ](https://space.bilibili.com/417031122) 而来: [site here](https://maao.cc/sleepy/), 并部分借鉴了代码。

> 文档尚未完成

如有 Bug / 建议 请 [issue](https://github.com/wyf9/sleepy/issues/new)

# 部署

理论上全平台通用, 安装了 Python 即可 *(开发环境: Debian linux)*

1. Clone 本仓库

```shell
git clone https://github.com/wyf9/sleepy.git
# or:
git clone git@github.com:wyf9/sleepy.git
```

2. 安装依赖

```shell
cd sleepy
./install_lib.sh
# or:
.\install_lib.bat
# 也可自行安装: See requirements.txt
```

3. 编辑配置文件

先启动一遍程序:

```shell
python3 server.py
```

确定无报错后使用 Ctrl+C 退出, 并编辑目录下生成的 `data.json` 文件:

```json

```