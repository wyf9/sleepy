# coding: utf-8
'''
win_device.py
在 Windows 上获取窗口名称
by: @wyf9
依赖: pywin32, requests
'''
import win32gui  # type: ignore
import requests
import time

# --- config start
SERVER = 'http://localhost:9010'
SECRET = 'wyf9test'
CHECK_INTERVAL = 2
BYPASS_SAME_REQUEST = True
DEVICE_ID = 'device-1'
DEVICE_SHOW_NAME = 'MyDevice1'
# --- config end


def main():
    url = f'{SERVER}/device/set'
    last_window = ''
    while True:
        window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        print(f'--- Window: {window}')
        if (BYPASS_SAME_REQUEST and window != last_window) or (not BYPASS_SAME_REQUEST):
            print(f'POST {url}')
            try:
                resp = requests.post(url=url, json={
                    'secret': SECRET,
                    'id': DEVICE_ID,
                    'show_name': DEVICE_SHOW_NAME,
                    'using': True,
                    'app_name': window
                }, headers={
                    'Content-Type': 'application/json'
                })
                print(f'Response: {resp.status_code} - {resp.text}')
            except Exception as e:
                print(f'Error: {e}')
            last_window = window
        else:
            print('window not change, bypass')
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
