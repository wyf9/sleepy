# coding: utf-8
'''
win_device.py
在 Windows 上获取窗口名称
by: @wyf9, @pwnint, @kmizmal, @gongfuture
基础依赖: pywin32, requests
媒体信息依赖:
 - Python≤3.9: winrt
 - Python≥3.10: winrt.windows.media.control, winrt.windows.foundation
 * (如果你嫌麻烦并且不在乎几十m的包占用, 也可以直接装winsdk :)
'''

# ----- Part: Import

import io
import sys
import threading
import time  # 改用 time 模块以获取更精确的时间
from datetime import datetime
from time import sleep

import win32api  # type: ignore - 勿删，用于强忽略非 windows 系统上 vscode 找不到模块的警告
import win32con  # type: ignore
import win32gui  # type: ignore
from pywintypes import error as pywinerror  # type: ignore
from requests import post

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
# 状态检查间隔 (秒)
STATUS_CHECK_INTERVAL: int = 5
# 心跳发送间隔 (秒)
HEARTBEAT_INTERVAL: int = 60
# 当窗口标题为其中任意一项时将不更新 (检查原始标题)
SKIPPED_NAMES: list = [
    '',  # 空字符串
    '系统托盘溢出窗口。', '新通知', '任务切换', '快速设置', '通知中心', '操作中心', '日期和时间信息', '网络连接', '电池信息', '搜索', '任务视图', '任务切换', 'Program Manager',  # 桌面组件
    'Flow.Launcher', 'Snipper - Snipaste', 'Paster - Snipaste'  # 其他程序
]
# 当窗口标题为其中任意一项时视为未在使用 (检查原始标题)
NOT_USING_NAMES: list = [
    '启动', '「开始」菜单',  # 开始菜单
    '我们喜欢这张图片，因此我们将它与你共享。', '就像你看到的图像一样？选择以下选项', '喜欢这张图片吗?'  # 锁屏界面
]
# 是否反转窗口标题，以此让应用名显示在最前 (以 ` - ` 分隔)
REVERSE_APP_NAME: bool = False
# 鼠标静止判定时间 (分钟)
MOUSE_IDLE_TIME: int = 15
# 鼠标移动检测的最小距离 (像素)
MOUSE_MOVE_THRESHOLD: int = 10
# 控制日志是否显示更多信息
DEBUG: bool = False
# 代理地址 (<http/socks>://host:port), 设置为空字符串禁用
PROXY: str = ''
# 是否启用媒体信息获取
MEDIA_INFO_ENABLED: bool = True
# 媒体信息显示模式: 'prefix' - 作为前缀添加到当前窗口名称, 'standalone' - 使用独立设备
MEDIA_INFO_MODE: str = 'prefix'
# 独立设备模式下的设备ID (仅当 MEDIA_INFO_MODE = 'standalone' 时有效)
MEDIA_DEVICE_ID: str = 'media-device'
# 独立设备模式下的显示名称 (仅当 MEDIA_INFO_MODE = 'standalone' 时有效)
MEDIA_DEVICE_SHOW_NAME: str = '正在播放'
# --- config end

# ----- Part: Functions

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # 统一使用 utf-8
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


# 导入拎出来优化性能 (?)
if MEDIA_INFO_ENABLED:
    try:
        from asyncio import run  # type: ignore

        import winrt.windows.media.control as media  # type: ignore
    except ImportError:
        # 如果上面的导入失败 (例如旧版 winrt)，尝试备用导入 (虽然通常是一样的)
        # 注意：如果基础的 winrt 包都装不上，这里还是会失败
        from asyncio import run  # type: ignore

        import winrt.windows.media.control as media  # type: ignore


def get_media_info():
    '''
    使用 pywinrt 获取 Windows SMTC 媒体信息 (正在播放的音乐等)
    Returns:
        tuple: (是否正在播放, 标题, 艺术家, 专辑)
    '''
    # 首先尝试使用 pywinrt
    try:
        # 以异步方式获取媒体会话管理器
        async def get_media_session():
            # 获取媒体会话管理器
            manager = await media.GlobalSystemMediaTransportControlsSessionManager.request_async()
            return manager.get_current_session()

        # 使用异步函数包装整个操作
        async def get_media_info_async():
            session = await get_media_session()
            # 如果没有活动的媒体会话，直接返回
            if not session:
                return False, '', '', ''

            # 获取播放状态
            info = session.get_playback_info()
            # 检查 info 是否有效 (某些情况下可能为 None)
            if not info:
                return False, "", "", ""
            is_playing = info.playback_status == media.GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING

            # 获取媒体属性
            props = await session.try_get_media_properties_async()
            # 检查 props 是否有效
            if not props:
                # 如果获取属性失败，但仍在播放，至少返回播放状态
                return is_playing, "", "", ""

            title = props.title or ''
            artist = props.artist or ''
            album = props.album_title or ''

            if album == '<未知专辑名>':
                album = ''

            return is_playing, title, artist, album

        # 运行异步函数
        return run(get_media_info_async())

    # 捕获所有可能的异常 (winrt 可能抛出各种 COM 或其他错误)
    except Exception as primary_error:
        debug(f"主要媒体信息获取方式失败: {primary_error}")
        return False, "", "", ""

# ----- Part: Send status


Url = f'{SERVER}/device/set'
last_window = ""  # 上次成功发送的窗口状态 (处理后)
last_send_time = 0  # 上次成功发送的时间戳 (秒)


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
        print("Received logout event. Server will detect offline via heartbeat timeout.")
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
        return is_mouse_idle
    current_time = time.time()

    # 计算鼠标移动距离的平方（避免开平方运算）
    dx = abs(current_pos[0] - last_mouse_pos[0])
    dy = abs(current_pos[1] - last_mouse_pos[1])
    distance_squared = dx * dx + dy * dy

    # 阈值的平方，用于比较
    threshold_squared = MOUSE_MOVE_THRESHOLD * MOUSE_MOVE_THRESHOLD

    # 打印详细的鼠标状态信息（为了保持日志一致性，仍然显示计算后的距离）
    distance = distance_squared ** 0.5 if DEBUG else 0  # 仅在需要打印日志时计算
    debug(
        f'Mouse: current={current_pos}, last={last_mouse_pos}, distance={distance:.1f}px')

    # 如果移动距离超过阈值（使用平方值比较）
    if distance_squared > threshold_squared:
        last_mouse_pos = current_pos
        last_mouse_move_time = current_time
        if is_mouse_idle:
            is_mouse_idle = False
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
last_media_content = ''  # 跟踪上一次的媒体内容


def do_update(force_send=False):
    """
    检查状态并根据需要发送更新或心跳
    :param force_send: 是否强制发送 (用于心跳)
    """
    # 全局变量
    global last_window, last_send_time, cached_window_title, is_mouse_idle, last_media_playing, last_media_content

    # --- 1. 获取原始状态 ---
    current_window_raw = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    mouse_idle = check_mouse_idle()
    debug(f"--- Raw state: Window=`{current_window_raw}`, mouse_idle={mouse_idle}")

    # --- 2. 处理状态 (媒体前缀, 反转, 空闲) ---
    window_processed = current_window_raw
    using = True

    # 获取媒体信息 (可能用于前缀或独立设备)
    prefix_media_info = None
    standalone_media_info = None
    media_is_playing = False
    if MEDIA_INFO_ENABLED:
        is_playing, title, artist, album = get_media_info()
        media_is_playing = is_playing  # 保存播放状态供 standalone 使用
        if is_playing and (title or artist):
            # 为 prefix 模式创建格式化后的媒体信息 [♪歌曲名]
            if title:
                prefix_media_info = f"[♪{title}]"
            else:
                prefix_media_info = "[♪]"
            # 为 standalone 模式创建格式化后的媒体信息 ♪歌曲名-歌手-专辑
            parts = []
            if title:
                parts.append(f"♪{title}")
            if (artist and artist != title):
                parts.append(artist)
            if (album and album != title and album != artist):
                parts.append(album)
            standalone_media_info = " - ".join(parts) if parts else "♪播放中"
            debug(f"Media detected - title: {title or ''} - artist: {artist or ''} - album: {album or ''}")

    # 应用反转
    if REVERSE_APP_NAME and " - " in window_processed:
        window_processed = reverse_app_name(window_processed)

    # 应用媒体前缀 (如果启用)
    if MEDIA_INFO_ENABLED and prefix_media_info and MEDIA_INFO_MODE == 'prefix':
        window_processed = f"{prefix_media_info} {window_processed}"

    # 应用鼠标空闲状态 (最高优先级)
    if mouse_idle:
        if not is_mouse_idle:  # 刚进入空闲
            cached_window_title = window_processed  # 缓存进入空闲前的状态
            print('Caching window title before idle')
        window_processed = ""  # 空闲时发送空状态
        using = False
        is_mouse_idle = True  # 确保状态被标记为空闲
    else:
        if is_mouse_idle:  # 刚从空闲恢复
            is_mouse_idle = False
            print("Mouse is active again")
        # 检查 NOT_USING_NAMES (仅在非空闲时检查)
        if current_window_raw in NOT_USING_NAMES:
            using = False
            debug(f"* not using (raw name): `{current_window_raw}`")

    debug(f"--- Processed state: Window=`{window_processed}`, using={using}")

    # --- 3. 决定是否发送主设备更新 ---
    is_skipped = current_window_raw in SKIPPED_NAMES  # 使用原始名称检查跳过
    status_changed = window_processed != last_window  # 比较处理后的名称
    should_send_heartbeat = time.time() - last_send_time >= HEARTBEAT_INTERVAL

    should_send_main = False
    reason = ""

    if is_skipped:
        if window_processed == last_window:
            reason = "Skipped and unchanged."
        elif not force_send:
            reason = "Skipped but changed, updating last_window only."
            last_window = window_processed  # 更新本地状态但不发送
        else:  # force_send is True
            reason = "Skipped, but forcing send for heartbeat."
            should_send_main = True
    elif status_changed:
        reason = f"Status changed: '{last_window}' -> '{window_processed}'"
        should_send_main = True
    elif should_send_heartbeat:
        reason = "Heartbeat interval reached."
        should_send_main = True
    else:
        reason = "Status unchanged and heartbeat interval not reached."

    debug(f"Send decision: {should_send_main}. Reason: {reason}")

    # --- 4. 发送主设备更新 (如果需要) ---
    if should_send_main:
        print(f'Sending main update: using={using}, app_name="{window_processed}"')
        try:
            resp = send_status(using=using, app_name=window_processed, id=DEVICE_ID, show_name=DEVICE_SHOW_NAME)
            debug(f"Main Response: {resp.status_code} - {resp.json()}")
            if resp.status_code == 200:
                last_window = window_processed  # 仅在成功发送时更新
                last_send_time = time.time()
            elif not DEBUG:
                print(f"Error! Main Response: {resp.status_code} - {resp.json()}")
        except Exception as e:
            print(f"Error sending main status: {e}")

    # --- 5. 处理媒体信息 (standalone 模式) ---
    if MEDIA_INFO_ENABLED and MEDIA_INFO_MODE == 'standalone':
        try:
            # 确定当前媒体状态
            current_media_playing = media_is_playing  # 使用之前获取的状态
            current_media_content = standalone_media_info if standalone_media_info else ''

            # 检测播放状态或歌曲内容是否变化
            media_changed = (current_media_playing != last_media_playing) or (current_media_playing and current_media_content != last_media_content)

            # standalone 模式也需要心跳。
            # 当前简化逻辑：只要正在播放，每次检查都发送更新 (充当心跳)。
            # 或者当播放状态/内容发生变化时发送更新。
            send_media_update = False
            media_app_name = "没有媒体播放"
            media_using = False

            if current_media_playing:
                media_app_name = current_media_content
                media_using = True
                if media_changed:
                    debug(
                        f"Media changed: status: {last_media_playing} -> {current_media_playing}, content changed: {current_media_content != last_media_content} - `{current_media_content}`"
                    )
                    send_media_update = True
                else:
                    # 如果正在播放且内容未变，每次检查都发送心跳
                    debug(f"Sending media heartbeat: `{current_media_content}`")
                    send_media_update = True  # 强制发送作为心跳
            elif last_media_playing:  # 从播放变为不播放
                debug(f"Media stopped: status: {last_media_playing} -> {current_media_playing}")
                send_media_update = True

            if send_media_update:
                media_resp = send_status(using=media_using, app_name=media_app_name, id=MEDIA_DEVICE_ID, show_name=MEDIA_DEVICE_SHOW_NAME)
                debug(f"Media Response: {media_resp.status_code}")
                # 更新上一次的媒体状态和内容 (仅在发送后更新，避免重复发送停止状态)
                if media_resp.status_code == 200:
                    last_media_playing = current_media_playing
                    last_media_content = current_media_content
                elif not DEBUG:
                    print(f"Error! Media Response: {media_resp.status_code} - {media_resp.json()}")

        except Exception as e:
            debug(f"Media Info Error (standalone): {e}")


if __name__ == '__main__':
    try:
        while True:
            print("---------- Run Check")
            try:
                # 检查状态并根据需要发送更新或心跳
                # do_update 内部已包含心跳逻辑
                do_update()

            except Exception as loop_error:
                print(f"ERROR in main loop: {loop_error}")

            sleep(STATUS_CHECK_INTERVAL)  # 使用较短的检查间隔
    except (KeyboardInterrupt, SystemExit) as e:
        debug(f"Interrupt: {e}. Server will detect offline via heartbeat timeout.")
