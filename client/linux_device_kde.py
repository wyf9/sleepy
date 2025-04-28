# coding: utf-8
'''
linux_device_kde.py
在 Linux (KDE) 上获取窗口名称
by: @RikkaNaa
依赖: kdotool, requests
'''

import subprocess
from datetime import datetime
from io import TextIOWrapper
from sys import stdout
from time import sleep, time

from requests import post

# --- config start
SERVER = 'http://localhost:9010'  # 服务地址, 末尾还是不带 /
SECRET = 'wyf9test'  # 密钥
DEVICE_ID = 'device-1'  # 设备标识符
DEVICE_SHOW_NAME = 'MyDevice1'  # 前台显示名称
STATUS_CHECK_INTERVAL = 2  # 状态检查间隔 (秒)
HEARTBEAT_INTERVAL = 60  # 心跳发送间隔 (秒)
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
last_send_time = 0  # 上次发送时间戳 (秒)


def do_update(force_send=False):
    """
    进行更新
    :param force_send: 是否强制发送 (用于心跳)
    """
    global last_window, last_send_time
    window = get_active_window_title()
    print(f"--- Checked Window: `{window}`")

    # 检查跳过名称
    is_skipped = False
    for i in SKIPPED_NAMES:
        if i == window:
            print(f"* skipping: `{i}`")
            is_skipped = True
            break

    # 如果被跳过，且与上次状态相同，则不处理
    if is_skipped and window == last_window:
        print("Skipped and unchanged, doing nothing.")
        return
    # 如果被跳过，但与上次状态不同，则更新 last_window 但不发送 (除非是心跳强制发送)
    if is_skipped and window != last_window and not force_send:
        print("Skipped but changed, updating last_window only.")
        last_window = window  # 更新状态以便下次比较
        # 注意：这里不更新 last_send_time，允许心跳机制触发
        return

    # 判断是否在使用
    using = True
    for i in NOT_USING_NAMES:
        if i == window:
            print(f'* not using: `{i}`')
            using = False
            break

    # 检查状态是否变化 或 是否到达心跳时间
    status_changed = window != last_window
    should_send_heartbeat = time() - last_send_time >= HEARTBEAT_INTERVAL

    if status_changed:
        print(f"Status changed: '{last_window}' -> '{window}', using={using}")
    elif should_send_heartbeat:
        print("Heartbeat interval reached, sending status.")
    else:
        # 状态未变且未到心跳时间，不发送
        print("Status unchanged and heartbeat interval not reached, skipping send.")
        return

    # POST to api
    print(f"POST {Url}")
    try:
        resp = post(
            url=Url,
            json={"secret": SECRET, "id": DEVICE_ID, "show_name": DEVICE_SHOW_NAME, "using": using, "app_name": window},
            headers={"Content-Type": "application/json"},
        )
        print(f"Response: {resp.status_code} - {resp.json()}")
        # 仅在成功发送后更新 last_window 和 last_send_time
        last_window = window
        last_send_time = time()
    except Exception as e:
        print(f"Error: {e}")
        # 发送失败时不更新，以便下次重试或触发心跳


def main():
    '''
    主循环
    '''
    global last_send_time  # 确保可以在循环中访问
    while True:
        print("---------- Run Check")
        try:
            # 检查状态并根据需要发送
            do_update()

            # 额外检查是否需要强制发送心跳 (处理跳过状态的心跳)
            if time() - last_send_time >= HEARTBEAT_INTERVAL:
                print("Heartbeat interval reached for potentially skipped status, forcing send.")
                do_update(force_send=True)  # 强制发送当前状态作为心跳

        except Exception as e:
            print(f"ERROR in main loop: {e}")

        sleep(STATUS_CHECK_INTERVAL)  # 使用较短的检查间隔


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(f'Interrupt: {e}. Server will detect offline via heartbeat timeout.')
