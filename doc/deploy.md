# 部署

- [部署](#部署)
  - [手动部署](#手动部署)
    - [安装](#安装)
    - [启动](#启动)
  - [Huggingface 部署](#huggingface-部署)
    - [我承认你的代码写的确实很nb，但对我来说还是太吃操作了](#我承认你的代码写的确实很nb但对我来说还是太吃操作了)
  - [Vercel 部署](#vercel-部署)

## 手动部署

本方式理论上全平台通用, 安装了 Python >= **3.6** 即可 (建议: **3.10+**)

> 优点: 数据文件 (`data.json`) 可持久化，不会因为重启而被删除

### 安装

1. Clone 本仓库 (建议先 Fork / Use this template)

```shell
git clone --depth=1 -b main https://github.com/wyf9/sleepy.git
```

2. 安装依赖

```shell
pip install -r requirements.txt
```

3. 编辑配置文件

> *配置文件变化史: `data.json` -> `config.json` -> `config.jsonc` -> `.env`*

在目录下新建 `.env` 文件 (参考 [`.env.example`](../.env.example) 填写), *也可以直接设置相应的环境变量*

> [!IMPORTANT]
> **[配置示例](../.env.example)** <br/>
> **Windows 用户请确保 `.env` 文件以 UTF-8 编码而非 GBK 编码保存，否则读取可能出现问题!** *(如**错误读入行尾注释**)* <br/>
> *注意: 环境变量的优先级**高于** `.env` 文件* <br/>

### 启动

> **使用宝塔面板 (uwsgi) 等部署时，请确定只为本程序分配了 1 个进程, 如设置多个服务进程可能导致数据不同步!!!**

有两种启动方式:

```shell
# 直接启动
python3 server.py
# 简易启动器
python3 start.py
```
默认服务 http 端口: **`9010`**

## Huggingface 部署

> 适合没有服务器部署的同学使用 <br/>
> *~~有服务器也推荐，不怕被打~~* <br/>
> *唯一的缺点: **不能使用自定义域名***

只需三步:

1. 复制 Space `wyf9/sleepy` (**[点击直达](https://huggingface.co/spaces/wyf9/sleepy?duplicate=true&visibility=public)**)
2. 在复制页面设置 secret 和页面信息等环境变量 *[**[配置示例](../.env.example)**]*
3. 点击部署，等待完成后点击右上角三点 -> `Embed this space`，即可获得你的部署地址 *(类似于: <https://wyf9-sleepy.hf.space>)*

> [!IMPORTANT]
> **在创建时请务必选择 Space 类型为公开 (`Public`)，否则无法获取部署地址 (他人无法访问)!** <br/>
> *Hugging Face Space 如 48h 未访问将会休眠，建议使用定时请求平台 (如 `cron-job.org`, `Uptime Kuma` 等) 定时请求 Space `/none`*

### 我承认你的代码写的确实很nb，但对我来说还是太吃操作了

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
![链接](https://ghimg.siiway.top/sleepy/deploy/huggingface-1.1.png)
就可以复制你的`URL`，填入你选择的 **[`/client`](./client/README.md)** 对应的url配置中即可快速开始

</details>

## Vercel 部署

> 可以使用自定义域名，但限制较多 **(如无法使用 SSE)** <br/>
> *当前端检测到为 Vercel 部署时会回退到轮询方式更新*

1. Fork 本项目
2. 打开 [`vercel.com/new`](https://vercel.com/new)，并按照提示授权访问 GitHub *(如未注册则注册)*
3. 选择你的 Fork，点击 `Import`

![vercel-1](https://ghimg.siiway.top/sleepy/deploy/vercel-1.1.png)

4. 在导入界面设置环境变量 (其他配置保持默认)，点击 `Deploy` 部署 *[**[配置示例](../.env.example)**]*

![vercel-2](https://ghimg.siiway.top/sleepy/deploy/vercel-2.1.png)

即可完成部署，默认分配 `vercel.app` 域名

5. ***[可选]*** 绑定自定义域名: `Settings` -> `Domains`

![vercel-3](https://ghimg.siiway.top/sleepy/deploy/vercel-3.1.png)

6. ***[可选]*** 添加更多环境变量: `Settings` -> `Environment Variables`

![vercel-4](https://ghimg.siiway.top/sleepy/deploy/vercel-4.1.png)

> 修改环境变量后需重新部署
