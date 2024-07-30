# sleepy

Are you sleeping?

灵感由 Bilibili UP @ [WinMEMZ](https://space.bilibili.com/417031122) 而来: [site here](https://maao.cc/sleepy/), 并部分借鉴了代码。

如有 Bug / 建议 请 [issue](https://github.com/wyf9/sleepy/issues/new)

# 部署

理论上全平台通用, 安装了 Python 即可 *(开发环境: Debian linux)*

1. Clone 本仓库 (建议先 Fork)

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
# 也可自行安装: pip install -r requirements.txt
```

3. 编辑配置文件

先启动一遍程序:

```shell
python3 server.py
```

如果不出意外，会提示: `[Warning] [YYYY-MM-DD hh:mm:ss] data.json not exist, creating`，同时目录下出现 `data.json` 文件，编辑该文件中的配置 (实例请 [查看 `example.jsonc`](./example.jsonc) )

1. 启动程序即可

```shell
python3 server.py
```
<!--
> 如是在家庭内网等环境部署，可以试试 Cloudflare Tunnel (演示站使用的方案) ~~仅是觉得稳定推荐，勿喷~~
> 速度过慢可尝试 [优选ip](https://github.com/XIU2/CloudflareSpeedTest)
-->