# coding: utf-8
'''
win_device.py
在 Windows 上获取窗口名称
by: @wyf9, @pwnint, @kmizmal
依赖: pywin32, requests
'''

# ----- Part: Import

import sys
import io
from time import sleep
import time  # 改用 time 模块以获取更精确的时间
from datetime import datetime
from requests import post
import threading
import win32api  # type: ignore - 勿删，用于强忽略非 windows 系统上 vscode 找不到模块的警告
import win32con  # type: ignore
import win32gui  # type: ignore
from pywintypes import error as pywinerror # type: ignore

# ----- Part: Config

# --- config start
# 服务地址, 末尾同样不带 /
SERVER: str = 'http://localhost:9010'
# 密钥
SECRET: str = 'wyf9test'
# 设备标识符，唯一 (它也会被包含在 api 返回中, 不要包含敏感数据)
DEVICE_ID: str = 'device-1'
# 前台显示名称
DEVICE_SHOW_NAME: str = 'MyDevice1'
# 检查间隔，以秒为单位
CHECK_INTERVAL: int = 2
# 是否忽略重复请求，即窗口未改变时不发送请求
BYPASS_SAME_REQUEST: bool = True
# 控制台输出所用编码，避免编码出错，可选 utf-8 或 gb18030
ENCODING: str = 'gb18030'
# 当窗口标题为其中任意一项时将不更新
SKIPPED_NAMES: list = ['', '系统托盘溢出窗口。', '新通知', '任务切换', '快速设置', '通知中心', '搜索', 'Flow.Launcher', '任务视图', '任务切换', 'Snipper - Snipaste']
# 当窗口标题为其中任意一项时视为未在使用
NOT_USING_NAMES: list = ['我们喜欢这张图片，因此我们将它与你共享。', '启动']
# 是否反转窗口标题，以此让应用名显示在最前 (以 ` - ` 分隔)
REVERSE_APP_NAME: bool = False
# 鼠标静止判定时间 (分钟)
MOUSE_IDLE_TIME: int = 15
# 鼠标移动检测的最小距离 (像素)
MOUSE_MOVE_THRESHOLD: int = 10
# 控制日志是否显示更多信息
DEBUG: bool = True
# 代理地址 (<http/socks>://host:port), 设置为空字符串禁用
PROXY: str = ''
# --- 媒体信息配置
# 是否启用媒体信息获取
MEDIA_INFO_ENABLED: bool = True
# 媒体信息显示模式: 'prefix' - 作为前缀添加到当前窗口名称, 'standalone' - 使用独立设备, 'both' - 都启用
MEDIA_INFO_MODE: str = 'prefix'
# 独立设备模式下的设备ID (仅当 MEDIA_INFO_MODE = 'standalone' 时有效)
MEDIA_DEVICE_ID: str = 'media-device'
# 独立设备模式下的显示名称
MEDIA_DEVICE_SHOW_NAME: str = '正在播放'
# 媒体信息前缀最大长度（超出部分将被截断）
MEDIA_PREFIX_MAX_LENGTH: int = 20
# --- config end

# ----- Part: Functions

# stdout = TextIOWrapper(stdout.buffer, encoding=ENCODING)  # https://stackoverflow.com/a/3218048/28091753
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_print_ = print


def print(msg: str, print_only: bool = False, **kwargs):
    '''
    修改后的 `print()` 函数，解决不刷新日志的问题
    原: `_print_()`
    '''
    msg = str(msg).replace('\u200b', '')
    try:
        if print_only:
            _print_(msg, flush=True, **kwargs)
        else:
            _print_(
                f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}', flush=True, **kwargs)
    except Exception as e:
        _print_(
            f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Log Error: {e}', flush=True)


def debug(msg: str, **kwargs):
    '''
    显示调试消息
    '''
    if DEBUG:
        print(msg, **kwargs)


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


def get_media_info():
    '''
    使用 winrt 获取 Windows SMTC 媒体信息 (正在播放的音乐等)
    Returns:
        tuple: (是否正在播放, 标题, 艺术家, 专辑)
    '''
    # 首先尝试使用 winrt
    try:
        import winrt.windows.media.control as media
        from asyncio import run

        # 以异步方式获取媒体会话管理器
        async def get_media_session():
            # 获取媒体会话管理器
            manager = await media.GlobalSystemMediaTransportControlsSessionManager.request_async()
            return manager.get_current_session()

        # 使用异步函数包装整个操作
        async def get_media_info_async():
            session = await get_media_session()
            if not session:
                return False, "", "", ""

            # 获取播放状态
            info = session.get_playback_info()
            is_playing = info.playback_status == media.GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING

            # 获取媒体属性
            props = await session.try_get_media_properties_async()

            title = props.title or ""
            artist = props.artist or ""
            album = props.album_title or ""

            return is_playing, title, artist, album

        # 运行异步函数
        return run(get_media_info_async())

    except Exception as primary_error:
        debug(f"主要媒体信息获取方式失败: {primary_error}")
        return False, "", "", ""

# ----- Part: Send status


Url = f'{SERVER}/device/set'
last_window = ''


def send_status(using: bool = True, app_name: str = '', id: str = DEVICE_ID, show_name: str = DEVICE_SHOW_NAME, **kwargs):
    '''
    post 发送设备状态信息
    设置了 headers 和 proxies
    '''
    json_data = {
        'secret': SECRET,
        'id': id,
        'show_name': show_name,
        'using': using,
        'app_name': app_name
    }
    if PROXY:
        return post(
            url=Url,
            json=json_data,
            headers={
                'Content-Type': 'application/json'
            },
            proxies={
                'all': PROXY
            },
            **kwargs
        )
    else:
        return post(
            url=Url,
            json=json_data,
            headers={
                'Content-Type': 'application/json'
            },
            **kwargs
        )

# ----- Part: Shutdown handler


def on_shutdown(hwnd, msg, wparam, lparam):
    '''
    关机监听回调
    '''
    if msg == win32con.WM_QUERYENDSESSION:
        print("Received logout event, sending not using...")
        try:
            resp = send_status(
                using=False,
                app_name="要关机了喵",
                id=DEVICE_ID,
                show_name=DEVICE_SHOW_NAME
            )
            debug(f'Response: {resp.status_code} - {resp.json()}')
            if resp.status_code != 200:
                print(f'Error! Response: {resp.status_code} - {resp.json()}')
        except Exception as e:
            print(f'Exception: {e}')
        return True  # 允许关机或注销
    return 0  # 其他消息


# 注册窗口类
wc = win32gui.WNDCLASS()
wc.lpfnWndProc = on_shutdown  # 设置回调函数
wc.lpszClassName = "ShutdownListener"
wc.hInstance = win32api.GetModuleHandle(None)

# 创建窗口类并注册
class_atom = win32gui.RegisterClass(wc)

# 创建窗口
hwnd = win32gui.CreateWindow(
    class_atom,  # className
    "Sleepy Shutdown Listener",  # windowTitle
    0,  # style
    0,  # x
    0,  # y
    0,  # width
    0,  # height
    0,  # parent
    0,  # menu
    wc.hInstance,  # hinstance
    None  # reserved
)


def message_loop():
    '''
    (需异步执行) 用于在后台启动消息循环
    '''
    win32gui.PumpMessages()


# 创建并启动线程
message_thread = threading.Thread(target=message_loop, daemon=True)
message_thread.start()

# ----- Part: Mouse idle

# 鼠标状态相关变量
last_mouse_pos = win32api.GetCursorPos()
last_mouse_move_time = time.time()
is_mouse_idle = False
cached_window_title = ''  # 缓存窗口标题, 用于恢复


def check_mouse_idle() -> bool:
    '''
    检查鼠标是否静止
    返回 True 表示鼠标静止超时
    '''
    global last_mouse_pos, last_mouse_move_time, is_mouse_idle

    try:
        current_pos = win32api.GetCursorPos()
    except pywinerror as e:
        print(f'Check mouse pos error: {e}')
        return None
    current_time = time.time()

    # 计算鼠标移动距离
    dx = abs(current_pos[0] - last_mouse_pos[0])
    dy = abs(current_pos[1] - last_mouse_pos[1])
    distance = (dx * dx + dy * dy) ** 0.5

    # 打印详细的鼠标状态信息
    debug(
        f'Mouse: current={current_pos}, last={last_mouse_pos}, distance={distance:.1f}px')

    # 如果移动距离超过阈值
    if distance > MOUSE_MOVE_THRESHOLD:
        last_mouse_pos = current_pos
        last_mouse_move_time = current_time
        if is_mouse_idle:
            is_mouse_idle = False
            print(
                f'Mouse wake up: moved {distance:.1f}px > {MOUSE_MOVE_THRESHOLD}px')
        else:
            debug(f'Mouse moving: {distance:.1f}px > {MOUSE_MOVE_THRESHOLD}px')
        return False

    # 检查是否超过静止时间
    idle_time = current_time - last_mouse_move_time
    debug(f'Idle time: {idle_time:.1f}s / {MOUSE_IDLE_TIME*60:.1f}s')

    if idle_time > MOUSE_IDLE_TIME * 60:
        if not is_mouse_idle:
            is_mouse_idle = True
            print(f'Mouse entered idle state after {idle_time/60:.1f} minutes')
        return True

    return is_mouse_idle  # 保持当前状态

# ----- Part: Main interval check

last_media_playing = False  # 跟踪上一次的媒体播放状态
last_media_content = ""  # 跟踪上一次的媒体内容

def do_update():
    global last_window, cached_window_title, is_mouse_idle, last_media_playing, last_media_content

    # 获取当前窗口标题和鼠标状态
    current_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    # 如果启用了反转应用名称功能，则反转窗口标题
    if REVERSE_APP_NAME and ' - ' in current_window:
        current_window = reverse_app_name(current_window)
    mouse_idle = check_mouse_idle()
    debug(f'--- Window: `{current_window}`, mouse_idle: {mouse_idle}')

    # 始终保持同步的状态变量
    window = current_window
    using = True

        # 获取媒体信息
    prefix_media_info = None
    standalone_media_info = None

    if MEDIA_INFO_ENABLED:
        is_playing, title, artist, album = get_media_info()
        if is_playing and (title or artist):
            # 为 prefix 模式创建格式化后的媒体信息 [♪歌曲名]
            if title:
                # 如果标题太长，进行截断
                if len(title) > MEDIA_PREFIX_MAX_LENGTH - 4:  # 为[♪]和...留出空间
                    truncated_title = title[:MEDIA_PREFIX_MAX_LENGTH - 7] + "..."
                    prefix_media_info = f"[♪{truncated_title}]"
                else:
                    prefix_media_info = f"[♪{title}]"
            else:
                prefix_media_info = "[♪]"

            # 为 standalone 模式创建格式化后的媒体信息 ♪歌曲名-歌手-专辑
            parts = []
            if title:
                parts.append(f"♪{title}")
            if artist:
                parts.append(artist)
            if album:
                parts.append(album)

            standalone_media_info = "-".join(parts) if parts else "♪播放中"

            debug(f"检测到媒体: {title or ''} - {artist or ''} - {album or ''}")

    # 处理媒体信息 (prefix 模式)
    if MEDIA_INFO_ENABLED and prefix_media_info and (MEDIA_INFO_MODE == 'prefix' or MEDIA_INFO_MODE == 'both'):
        # 作为前缀添加到窗口名称
        window = f"{prefix_media_info} {window}"

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

    # 是否需要发送更新
    should_update = (
        mouse_idle != is_mouse_idle or  # 鼠标状态改变
        window != last_window or  # 窗口改变
        not BYPASS_SAME_REQUEST  # 强制更新模式
    )

    if should_update:
        # 窗口名称检查 (未使用列表)
        if current_window in NOT_USING_NAMES:
            using = False
            debug(f'* not using: `{current_window}`')

        # 窗口名称检测 (跳过列表)
        if current_window in SKIPPED_NAMES:
            debug(f'* in skip list: `{current_window}`, ', end='')
            if mouse_idle == is_mouse_idle:
                # 鼠标状态未改变 -> 直接跳过
                print('skipped', print_only=True)
                return
            else:
                # 鼠标状态改变 -> 将窗口名称设为上次 (非未在使用) 的名称
                print(
                    f'set app name to last window: `{last_window}`', print_only=True)
                window = last_window

        # 发送状态更新
        print(
            f'Sending update: using = {using}, app_name = "{window}", idle = {mouse_idle}')
        try:
            resp = send_status(
                using=using,
                app_name=window,
                id=DEVICE_ID,
                show_name=DEVICE_SHOW_NAME
            )
            debug(f'Response: {resp.status_code} - {resp.json()}')
            if resp.status_code != 200 and not DEBUG:
                print(f'Error! Response: {resp.status_code} - {resp.json()}')
            last_window = window
        except Exception as e:
            print(f'Error: {e}')
    else:
        debug('No state change, skipping update')
        return

    # 如果使用独立设备模式展示媒体信息
    if MEDIA_INFO_ENABLED and (MEDIA_INFO_MODE == 'standalone' or MEDIA_INFO_MODE == 'both'):
        try:
            # 确定当前媒体状态
            current_media_playing = bool(standalone_media_info)
            current_media_content = standalone_media_info if standalone_media_info else ""
            
            # 检测播放状态或歌曲内容是否变化
            media_changed = (current_media_playing != last_media_playing) or \
                           (current_media_playing and current_media_content != last_media_content)
            
            if media_changed:
                debug(f'Media changed: status {last_media_playing}->{current_media_playing}, content changed: {last_media_content != current_media_content}')
                
                if current_media_playing:
                    # 从不播放变为播放或歌曲内容变化
                    media_resp = send_status(
                        using=True,
                        app_name=standalone_media_info,
                        id=MEDIA_DEVICE_ID,
                        show_name=MEDIA_DEVICE_SHOW_NAME
                    )
                else:
                    # 从播放变为不播放
                    media_resp = send_status(
                        using=False,
                        app_name='No Media Playing',
                        id=MEDIA_DEVICE_ID,
                        show_name=MEDIA_DEVICE_SHOW_NAME
                    )
                debug(f'Media Response: {media_resp.status_code}')
                
                # 更新上一次的媒体状态和内容
                last_media_playing = current_media_playing
                last_media_content = current_media_content
        except Exception as e:
            debug(f'Media Info Error: {e}')


def main():
    while True:
        do_update()
        sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        # 如果中断或被 taskkill 则发送未在使用
        debug(f'Interrupt: {e}')
        try:
            resp = send_status(
                using=False,
                app_name=f'Client Exited: {e}',
                id=DEVICE_ID,             # 添加设备ID
                show_name=DEVICE_SHOW_NAME  # 添加显示名称
            )
            debug(f'Response: {resp.status_code} - {resp.json()}')

            # 如果启用了独立媒体设备，也发送该设备的退出状态
            if MEDIA_INFO_ENABLED and (MEDIA_INFO_MODE == 'standalone' or MEDIA_INFO_MODE == 'both'):
                media_resp = send_status(
                    using=False,
                    app_name='Media Client Exited',
                    id=MEDIA_DEVICE_ID,
                    show_name=MEDIA_DEVICE_SHOW_NAME
                )
                debug(f'Media Response: {media_resp.status_code}')

            if resp.status_code != 200:
                print(f'Error! Response: {resp.status_code} - {resp.json()}')
        except Exception as e:
            print(f'Exception: {e}')
