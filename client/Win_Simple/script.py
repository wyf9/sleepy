# coding: utf-8
import os
import sys
import configparser
from win32gui import GetWindowText, GetForegroundWindow
from win32api import GetCursorPos
from requests import post
from datetime import datetime
from time import time, sleep
import io
#pyinstaller -F -n Win_Simple.exe --icon=zmal.ico --hidden-import=win32gui --hidden-import=win32api --hidden-import=requests script.py

import logging

# 读取 ini 配置文件
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")
# 创建默认配置
DEFAULT_CONFIG = """\
[settings]
# 服务地址, 末尾不带 /
SERVER = http://localhost:9010
# 密钥
SECRET = wyf9test
# 设备标识符，唯一 (它也会被包含在 api 返回中, 不要包含敏感数据)
DEVICE_ID = Win_Simple
# 前台显示名称
DEVICE_SHOW_NAME = MyComputer
# 检查间隔，以秒为单位
CHECK_INTERVAL = 2
# 是否忽略重复请求，即窗口未改变时不发送请求
BYPASS_SAME_REQUEST = True
# 控制台输出所用编码，避免编码出错，可选 utf-8 或 gb18030
ENCODING = utf-8
# 当窗口标题为其中任意一项时将不更新（|分隔）
SKIPPED_NAMES = | 系统托盘溢出窗口。| 新通知| 任务切换| 快速设置| 通知中心| 搜索| Flow.Launcher| 任务视图| 任务栏| 示例窗口1| 示例窗口2
# 当窗口标题为其中任意一项时视为未在使用
NOT_USING_NAMES = 我们喜欢这张图片，因此我们将它与你共享。| 示例窗口1| 示例窗口2
# 是否反转窗口标题，以此让应用名显示在最前 (以 ` - ` 分隔)
REVERSE_APP_NAME = False
# 鼠标静止判定时间(分钟)
MOUSE_IDLE_TIME = 15
# 鼠标移动检测的最小距离（像素）
MOUSE_MOVE_THRESHOLD = 3
#日志等级(DEBUG,INFO,WARNING,ERROR)DEBUG->ERROR日志依次减少
LOGLEVEL = INFO
#日志记录文件
LOG_FILE = False
"""
def ensure_config_exists():
    """如果 config.ini 不存在，则创建默认配置"""
    if not os.path.exists(CONFIG_PATH):
        logging.warning("⚠️ 配置文件不存在，正在创建默认 config.ini...")
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG)
        sys.exit(f"✅ 默认配置文件已创建: {CONFIG_PATH}, 请编辑后重新运行程序")
        pass

def parse_list(value: str):
    return [item.strip() for item in value.split('|') if item.strip()]
# 确保配置文件存在
ensure_config_exists()
# 读取配置
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding='utf-8')
try:

    # if not config.sections():
    #     raise ValueError('配置文件为空或无效')

    SERVER = config.get('settings', 'SERVER')
    SECRET = config.get('settings', 'SECRET')
    DEVICE_ID = config.get('settings', 'DEVICE_ID')
    DEVICE_SHOW_NAME = config.get('settings', 'DEVICE_SHOW_NAME')
    CHECK_INTERVAL = config.getint('settings', 'CHECK_INTERVAL')
    BYPASS_SAME_REQUEST = config.getboolean('settings', 'BYPASS_SAME_REQUEST')
    ENCODING = config.get('settings', 'ENCODING')

    SKIPPED_NAMES = parse_list(config.get('settings', 'SKIPPED_NAMES'))
    NOT_USING_NAMES = parse_list(config.get('settings', 'NOT_USING_NAMES'))
    
    REVERSE_APP_NAME = config.getboolean('settings', 'REVERSE_APP_NAME')
    MOUSE_IDLE_TIME = config.getint('settings', 'MOUSE_IDLE_TIME')
    MOUSE_MOVE_THRESHOLD = config.getint('settings', 'MOUSE_MOVE_THRESHOLD')
    LogLevel = config.get('settings', 'LOGLEVEL')
    LOG_FILE = config.getboolean('settings', 'LOG_FILE')

except Exception as e:
    logging.error(f'配置文件读取失败: {e}')
    sys.exit(1)
    
if LogLevel=='DEBUG':
    log_level = logging.DEBUG
elif LogLevel=='INFO':
    log_level = logging.INFO
elif LogLevel=='WARNING':
    log_level = logging.WARNING
elif LogLevel=='ERROR':
    log_level = logging.ERROR
      
if LOG_FILE:
    Log_handler = [logging.FileHandler('mirror.log', encoding='utf-8'), logging.StreamHandler()]
else:
    Log_handler = [logging.StreamHandler()]

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=Log_handler
)

def process_window_title(title: str) -> str:
    """处理窗口标题（反转应用名+跳过检查）"""
    logging.debug(f'Window: {title}')
    # 反转应用名称
    if REVERSE_APP_NAME:
        title = reverse_app_name(title)
    else:
        title = title.strip()
    return title

def reverse_app_name(name: str) -> str:
    '''反转应用名称 (将末尾的应用名提前)'''
    return ' - '.join(reversed(name.split(' - ')))

# 鼠标状态相关变量
last_mouse_pos = GetCursorPos()
last_mouse_move_time = time()
is_mouse_idle = False
cached_window_title = ''  # 缓存窗口标题,用于恢复

def check_mouse_idle() -> bool:
    '''检查鼠标是否静止'''
    global last_mouse_pos, last_mouse_move_time, is_mouse_idle
    
    current_pos = GetCursorPos()
    current_time = time()
    dx, dy = abs(current_pos[0] - last_mouse_pos[0]), abs(current_pos[1] - last_mouse_pos[1])
    distance = (dx ** 2 + dy ** 2) ** 0.5

    logging.debug(f'Mouse: {current_pos}, last={last_mouse_pos}, distance={distance:.1f}px')

    if distance > MOUSE_MOVE_THRESHOLD:  # 只在鼠标真正移动时更新
        last_mouse_pos, last_mouse_move_time = current_pos, current_time
        if is_mouse_idle:
            is_mouse_idle = False
            logging.debug(f'Mouse wake up: moved {distance:.1f}px')
        return False

    idle_time = current_time - last_mouse_move_time
    if idle_time > MOUSE_IDLE_TIME * 60:
        if not is_mouse_idle:
            is_mouse_idle = True
            logging.debug(f'Mouse entered idle state after {idle_time/60:.1f} minutes')
        return True
    return is_mouse_idle

Url = f'{SERVER}/device/set'
last_window = ''

def do_update():
    global last_window, cached_window_title, is_mouse_idle
    
    # 获取当前窗口标题
    raw_window = GetWindowText(GetForegroundWindow())
    current_window = process_window_title(raw_window)
    mouse_idle = check_mouse_idle()
    logging.debug(f'--- Window: `{current_window}`')
    
    # 始终保持同步的状态变量
    window = current_window
    using = True
    
    # 鼠标空闲状态处理（优先级最高）
    if mouse_idle:
        # 缓存非空闲时的窗口标题
        if not is_mouse_idle:
            cached_window_title = current_window
            logging.debug('Caching window title before idle')
        # 设置空闲状态
        using = False
        window = ''
        is_mouse_idle = True
    else:
        # 从空闲恢复
        if is_mouse_idle:
            window = cached_window_title
            using = True
            is_mouse_idle = False
            logging.info('Restoring window title from idle')
        # 正常窗口状态检查
        else:
            for name in NOT_USING_NAMES:
                if current_window == name:
                    using = False
                    logging.debug(f'* not using: `{name}`')
                    break
    
    # 是否需要发送更新
    should_update = (
        (mouse_idle != is_mouse_idle or  # 鼠标状态改变
        window != last_window) and    # 窗口改变
        window not in SKIPPED_NAMES  # 不在跳过列表中
    )
    
    if should_update:
        logging.info(f'Sending update: using={using}, app_name="{window}", idle={mouse_idle}')
        try:
            resp = post(url=Url, json={
                'secret': SECRET,
                'id': DEVICE_ID,
                'show_name': DEVICE_SHOW_NAME,
                'using': using,
                'app_name': window
            }, headers={
                'Content-Type': 'application/json'
            })
            logging.debug(f'Response: {resp.status_code} - {resp.json()}')
            if resp.status_code!=200:
                logging.warning(f'出现异常，Response: {resp.status_code} - {resp.json()}')
            last_window = window
        except Exception as e:
            logging.warning(f'Error: {e}')
    else:
        logging.debug('No state change, skipping update')

def main():
    while True:
        try:
            do_update()
            sleep(CHECK_INTERVAL)  # 使用配置的间隔
        except Exception as e:
            logging.error(f'主循环异常: {e}')
            sleep(1)  # 防止错误循环

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        # 如果中断或被taskkill则发送未在使用
        logging.warning(f'Interrupt: {e}')
        try:
            resp = post(url=Url, json={
                'secret': SECRET,
                'id': DEVICE_ID,
                'show_name': DEVICE_SHOW_NAME,
                'using': False,
                'app_name': f'{e}'
            }, headers={
                'Content-Type': 'application/json'
            })
            logging.debug(f'Response: {resp.status_code} - {resp.json()}')
            if resp.status_code!=200:
                logging.warning(f'出现异常，Response: {resp.status_code} - {resp.json()}')
        except Exception as e:
            logging.error(f'Exception: {e}')