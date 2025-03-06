import os
from dotenv import load_dotenv,find_dotenv
if not find_dotenv():
    print("⚠️ 未找到 .env 文件，将使用默认配置，部分功能可能失效！")

load_dotenv()

user = os.getenv("sleepyUser", "admin")  # 默认用户名
host = os.getenv("sleepyHost", "0.0.0.0")  # 默认主机名
port = int(os.getenv("sleepyPort", 7860))  # 默认端口
timezone = os.getenv("timezone", "Asia/Shanghai")  # 默认时区

metrics = os.getenv("metrics", "false").lower() in ['true', '1', 't', 'y', 'yes']  # 默认 false
show_loading = os.getenv("showLoading", "false").lower() in ['true', '1', 't', 'y', 'yes']  # 默认 false
hitokoto = os.getenv("hitokoto", "true").lower() in ['true', '1', 't', 'y', 'yes']  # 默认 hitokoto 启用
canvas = os.getenv("canvas", "true").lower() in ['true', '1', 't', 'y', 'yes']  # 默认 canvas 启用

title = os.getenv("sleepyTitle", "Sleepy App")  # 默认标题
sleepyDesc = os.getenv("sleepyDesc", "A simple status monitoring app.")  # 默认描述
background = os.getenv("sleepyBackground", "https://imgapi.siiway.top/image")  # 默认背景
learn_more = os.getenv("sleepyLearnMore", "")  # 默认了解更多链接
repo = os.getenv("sleepyRepo", "https://github.com/wyf9/sleepy")  # 默认仓库地址
more_text = os.getenv("sleepyMoreText", "More details available.")  # 默认更多信息文本

refresh = int(os.getenv("sleepyRefresh", 30))  # 默认刷新间隔 30 秒
device_status_slice = int(os.getenv("deviceStatusSlice", 30))  # 默认设备状态片段数
data_check_interval = int(os.getenv("dataCheckInterval", 60))  # 默认数据检查间隔 60 秒

secret = os.getenv("SLEEPY_SECRET", "")  # 默认密钥为空
steamkey = os.getenv("STEAMKEY", "")  # 默认 steamkey 为空
steamids = os.getenv("steamids", "")  # 默认 steamid 为空

# 打印配置检查
# print(f"Host: {host}, Port: {port}, Timezone: {timezone}, Metrics: {metrics}")
# print(f"Title: {title}, Description: {sleepyDesc}, User: {user}")
# print(f"Refresh Interval: {refresh}, Show Loading: {show_loading}, Canvas: {canvas}")

