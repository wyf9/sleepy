# coding: utf-8
'''
win_device.py
在 Windows 上获取窗口名称
by: @wyf9
依赖: pywin32, requests
'''
'''
modification by pwnint
- Added `SystemExit` case when the script is interrupted
- Added mouse idle detection
  :-) GLHF
'''
from win32gui import GetWindowText, GetForegroundWindow  # type: ignore
from win32api import GetCursorPos  # 添加鼠标位置获取
from requests import post
from datetime import datetime
import time  # 改用 time 模块以获取更精确的时间
from time import sleep
import sys
import io

# --- config start
# 服务地址, 末尾同样不带 /
SERVER = 'http://localhost:9010'
# 密钥
SECRET = 'wyf9test'
# 设备标识符，唯一 (它也会被包含在 api 返回中, 不要包含敏感数据)
DEVICE_ID = 'device-1'
# 前台显示名称
DEVICE_SHOW_NAME = 'MyDevice1'
# 检查间隔，以秒为单位
CHECK_INTERVAL = 2
# 是否忽略重复请求，即窗口未改变时不发送请求
BYPASS_SAME_REQUEST = True
# 控制台输出所用编码，避免编码出错，可选 utf-8 或 gb18030
ENCODING = 'gb18030'
# 当窗口标题为其中任意一项时将不更新
SKIPPED_NAMES = ['', '系统托盘溢出窗口。', '新通知', '任务切换', '快速设置', '通知中心', '搜索', 'Flow.Launcher']
# 当窗口标题为其中任意一项时视为未在使用
NOT_USING_NAMES = ['我们喜欢这张图片，因此我们将它与你共享。']
# 是否反转窗口标题，以此让应用名显示在最前 (以 ` - ` 分隔)
REVERSE_APP_NAME = False
# 鼠标静止判定时间(分钟)
MOUSE_IDLE_TIME = 15
# 鼠标移动检测的最小距离（像素）
MOUSE_MOVE_THRESHOLD = 3
# --- config end

# buffer = stdout.buffer  # backup
# stdout = TextIOWrapper(stdout.buffer, encoding=ENCODING)  # https://stackoverflow.com/a/3218048/28091753
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_print_ = print


def print(msg: str, **kwargs):
    '''
    修改后的 `print()` 函数，解决不刷新日志的问题
    原: `_print_()`
    '''
    msg = str(msg).replace('\u200b', '')
    try:
        _print_(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}', flush=True, **kwargs)
    except Exception as e:
        _print_(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Log Error: {e}', flush=True)


def reverse_app_name(name: str) -> str:
    '''
    反转应用名称 (将末尾的应用名提前)
    如 Before: win_device.py - dev - Visual Studio Code
    After: Visual Studio Code - dev - win_device.py
    '''
    lst = name.split(' - ')
    new = []
    for i in lst:
        new = [i] + new
    return ' - '.join(new)


# 鼠标状态相关变量
last_mouse_pos = GetCursorPos()
last_mouse_move_time = time.time()
is_mouse_idle = False
cached_window_title = ''  # 缓存窗口标题,用于恢复

def check_mouse_idle() -> bool:
    '''
    检查鼠标是否静止
    返回 True 表示鼠标静止超时
    '''
    global last_mouse_pos, last_mouse_move_time, is_mouse_idle
    
    current_pos = GetCursorPos()
    current_time = time.time()
    
    # 计算鼠标移动距离
    dx = abs(current_pos[0] - last_mouse_pos[0])
    dy = abs(current_pos[1] - last_mouse_pos[1])
    distance = (dx * dx + dy * dy) ** 0.5
    
    # 打印详细的鼠标状态信息
    print(f'Mouse: current={current_pos}, last={last_mouse_pos}, distance={distance:.1f}px')
    
    # 如果移动距离超过阈值
    if distance > MOUSE_MOVE_THRESHOLD:
        last_mouse_pos = current_pos
        last_mouse_move_time = current_time
        if is_mouse_idle:
            is_mouse_idle = False
            print(f'Mouse wake up: moved {distance:.1f}px')
        else:
            print(f'Mouse moving: {distance:.1f}px')
        return False
    
    # 检查是否超过静止时间
    idle_time = current_time - last_mouse_move_time
    print(f'Idle time: {idle_time:.1f}s / {MOUSE_IDLE_TIME*60:.1f}s')
    
    if idle_time > MOUSE_IDLE_TIME * 60:
        if not is_mouse_idle:
            is_mouse_idle = True
            print(f'Mouse entered idle state after {idle_time/60:.1f} minutes')
        return True
    
    return is_mouse_idle  # 保持当前状态

Url = f'{SERVER}/device/set'
last_window = ''


def do_update():
    global last_window, cached_window_title, is_mouse_idle
    
    # 获取当前窗口标题和鼠标状态
    current_window = GetWindowText(GetForegroundWindow())
    mouse_idle = check_mouse_idle()
    
    print(f'--- Window: `{current_window}`')
    
    # 始终保持同步的状态变量
    window = current_window
    using = True
    
    # 鼠标空闲状态处理（优先级最高）
    if mouse_idle:
        # 缓存非空闲时的窗口标题
        if not is_mouse_idle:
            cached_window_title = current_window
            print('Caching window title before idle')
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
            print('Restoring window title from idle')
        # 正常窗口状态检查
        else:
            for name in NOT_USING_NAMES:
                if current_window == name:
                    using = False
                    print(f'* not using: `{name}`')
                    break
    
    # 是否需要发送更新
    should_update = (
        mouse_idle != is_mouse_idle or  # 鼠标状态改变
        window != last_window or  # 窗口改变
        not BYPASS_SAME_REQUEST  # 强制更新模式
    )
    
    if should_update:
        print(f'Sending update: using={using}, app_name="{window}", idle={mouse_idle}')
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
            print(f'Response: {resp.status_code} - {resp.json()}')
            last_window = window
        except Exception as e:
            print(f'Error: {e}')
    else:
        print('No state change, skipping update')


def main():
    while True:
        do_update()
        sleep(1)  # 改为1秒检查一次，提高响应度


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        # 如果中断或被taskkill则发送未在使用
        print(f'Interrupt: {e}')
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
            print(f'Response: {resp.status_code} - {resp.json()}')
        except Exception as e:
            print(f'Exception: {e}')
