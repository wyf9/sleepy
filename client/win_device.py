# coding: utf-8
'''
win_device.py
在 Windows 上获取窗口名称
by: @wyf9
依赖: pywin32, requests
'''
from win32gui import GetWindowText, GetForegroundWindow  # type: ignore
from requests import post
from datetime import datetime
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
# 是否反转窗口标题，以此让应用名显示在最前
REVERSE_APP_NAME = False
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
    msg = msg.replace('\u200b', '')
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
    print(lst)
    new = []
    for i in lst:
        print(i)
        new = [i] + new
    return ' - '.join(new)


Url = f'{SERVER}/device/set'
last_window = ''


def do_update():
    global last_window
    window = GetWindowText(GetForegroundWindow())  # type: ignore
    print(f'--- Window: `{window}`')

    # 检测重复名称
    if (BYPASS_SAME_REQUEST and window == last_window):
        print('window not change, bypass')
        return

    # 检查跳过名称
    for i in SKIPPED_NAMES:
        if i == window:
            print(f'* skipped: `{i}`')
            return

    # 判断是否在使用
    using = True
    for i in NOT_USING_NAMES:
        if i == window:
            print(f'* not using: `{i}`')
            using = False

    # 反转名称
    if REVERSE_APP_NAME:
        window = reverse_app_name(window)
        print(f'Reversed: `{i}`')

    # POST to api
    print(f'POST {Url}')
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
    except Exception as e:
        print(f'Error: {e}')
    last_window = window


def main():
    while True:
        do_update()
        sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        # 如果中断则发送未在使用
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
