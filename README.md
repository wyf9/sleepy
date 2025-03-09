# 稳定使用版本
更多文档参考 https://github.com/wyf9/sleepy
# 开始使用
## 安装必要的运行环境
```
apt-get update && apt-get install -y git python3 python3-pip tzdata
```
## 克隆仓库
```
git clone -b use --depth=1 https://github.com/kmizmal/sleepy.git
cd sleepy
pip install --no-cache-dir -r requirements.txt
python3 server.py
```
