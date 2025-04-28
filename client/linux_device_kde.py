# coding: utf-8
'''
linux_device_kde.py
在 Linux (KDE) 上获取窗口名称
by: @RikkaNaa
依赖: kdotool, requests
'''

from requests import post
from datetime import datetime
from time import sleep
from sys import stdout, exit
from io import TextIOWrapper
import subprocess
import signal


# --- config start
SERVER = 'http://localhost:9010'  # 服务地址, 末尾还是不带 /
SECRET = 'wyf9test'  # 密钥
DEVICE_ID = 'device-1'  # 设备标识符
DEVICE_SHOW_NAME = 'MyDevice1'  # 前台显示名称
CHECK_INTERVAL = 60  # 检查间隔，以秒为单位, 改为 60 秒
BYPASS_SAME_REQUEST = False  # 是否忽略重复请求, 改为 False
ENCODING = 'utf-8'  # 控制台输出所用编码，避免编码出错，可选 utf-8 或 gb18030
SKIPPED_NAMES = ['', 'plasmashell']  # 当窗口名为其中任意一项时将不更新
NOT_USING_NAMES = ['[FAILED]']  # 当窗口名为其中任意一项时视为未在使用
# --- config end

stdout = TextIOWrapper(stdout.buffer, encoding=ENCODING)  # https://stackoverflow.com/a/3218048/28091753
_print_ = print


def print(msg: str, **kwargs):
    '''
    修改后的 `print()` 函数，解决不刷新日志的问题
    原: `_print_()`
    '''
    _print_(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}', flush=True, **kwargs)


def get_active_window_title():
    '''
    获取窗口标题, 如检测失败则为 `[FAILED]`
    '''
    result = subprocess.run(["kdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True)
    if result.returncode == 0:
        window_name = result.stdout.replace("\n", "")
        return window_name
    else:
        print(f'Return code isn\'t 0: {result.returncode}!')
        return '[FAILED]'


Url = f'{SERVER}/device/set'
last_window = ''


def do_update():
    '''
    进行更新
    '''
    global last_window
    window = get_active_window_title()
    print(f'--- Window: `{window}`')

    # 检查跳过名称
    send_update = True
    for i in SKIPPED_NAMES:
        if i == window:
            print(f'* skipped: `{i}`')
            # 如果跳过且与上次相同，则不发送
            if window == last_window:
                print('skipped and unchanged, bypass send')
                send_update = False
            # 否则，更新 last_window 但不发送
            else:
                 last_window = window # 更新 last_window 以避免下次误判为变化
                 send_update = False
            break # 找到一个跳过项就足够了

    # 判断是否在使用
    using = True
    for i in NOT_USING_NAMES:
        if i == window:
            print(f'* not using: `{i}`')
            using = False
            break # 找到一个即可

    # POST to api (if not skipped)
    if send_update:
        # 仅在状态实际改变时记录日志，避免心跳刷屏
        if window != last_window:
             print(f'Status changed: '{last_window}' -> '{window}', using={using}')
        else:
             print('Sending heartbeat with unchanged status.')

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
            # 仅在成功发送后更新 last_window
            last_window = window
        except Exception as e:
            print(f'Error: {e}')
            # 发送失败时不更新 last_window


def main():
    '''
    主循环
    '''
    while True:
        do_update()
        sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(f'Interrupt: {e}. Server will detect offline via heartbeat timeout.')
