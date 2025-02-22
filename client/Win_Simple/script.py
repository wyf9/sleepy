# coding: utf-8
import os
import sys
import configparser
import requests
import logging
import threading
import win32gui,win32con,win32api # type: ignore
from time import time, sleep

#cd client/Win_Simple
#pyinstaller -F -n Win_Simple.exe --icon=zmal.ico --hidden-import=win32gui --hidden-import=win32con --hidden-import=win32api --hidden-import=requests script.py

# --------------------------
# 配置管理类
# --------------------------
class AppConfig:
    """应用程序配置管理"""
    _DEFAULT_CONFIG = """\
    [settings]
    SERVER = http://localhost:9010
    SECRET = wyf9test
    DEVICE_ID = Win_Simple
    DEVICE_SHOW_NAME = MyComputer
    CHECK_INTERVAL = 2
    ENCODING = utf-8
    SKIPPED_NAMES = | 系统托盘溢出窗口。| 新通知| 任务切换| 快速设置| 通知中心| 搜索| Flow.Launcher| 任务视图| 任务栏| 示例窗口1| 示例窗口2
    NOT_USING_NAMES = 我们喜欢这张图片，因此我们将它与你共享。| 示例窗口1| 示例窗口2
    REVERSE_APP_NAME = False
    MOUSE_IDLE_TIME = 15
    MOUSE_MOVE_THRESHOLD = 3
    LOGLEVEL = INFO
    LOG_FILE = False
    """
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.ini")
        self._ensure_config_exists()
        self._load_config()
    
    def _ensure_config_exists(self):
        """创建默认配置文件"""
        if not os.path.exists(self.config_path):
            logging.warning("⚠️ 配置文件不存在，正在创建默认 config.ini...")
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write(self._DEFAULT_CONFIG)
            sys.exit(f"✅ 默认配置文件已创建: {self.config_path}, 请编辑后重新运行程序")
    
    def _load_config(self):
        """加载并验证配置"""
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path, encoding='utf-8')
        
        try:
            # 基本配置
            self.server = self.config.get('settings', 'SERVER')
            self.secret = self.config.get('settings', 'SECRET')
            self.device_id = self.config.get('settings', 'DEVICE_ID')
            self.device_show_name = self.config.get('settings', 'DEVICE_SHOW_NAME')
            self.check_interval = self.config.getint('settings', 'CHECK_INTERVAL')
            
            # 窗口处理配置
            self.skipped_names = self._parse_list('SKIPPED_NAMES')
            self.not_using_names = self._parse_list('NOT_USING_NAMES')
            self.reverse_app_name = self.config.getboolean('settings', 'REVERSE_APP_NAME')
            
            # 鼠标配置
            self.mouse_idle_time = self.config.getint('settings', 'MOUSE_IDLE_TIME')
            self.mouse_move_threshold = self.config.getint('settings', 'MOUSE_MOVE_THRESHOLD')
            
            # 日志配置
            self.log_level = self._get_log_level()
            self.log_file = self.config.getboolean('settings', 'LOG_FILE')
            
        except Exception as e:
            logging.error(f'配置文件读取失败: {e}')
            sys.exit(1)
    
    def _parse_list(self, key: str) -> list:
        """解析竖线分隔的配置项"""
        return [item.strip() for item in self.config.get('settings', key).split('|') if item.strip()]
    
    def _get_log_level(self):
        """获取日志等级"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        return level_map.get(self.config.get('settings', 'LOGLEVEL'), logging.INFO)

# --------------------------
# 设备状态管理
# --------------------------
class DeviceState:
    """设备状态跟踪管理"""
    def __init__(self, config: AppConfig):
        self.config = config
        self.last_window = ''
        self.cached_window = ''
        self.last_mouse_pos = win32api.GetCursorPos()
        self.last_mouse_time = time()
        self.is_mouse_idle = False

    def check_mouse_idle(self) -> bool:
        """检测鼠标空闲状态"""
        current_pos = win32api.GetCursorPos()
        current_time = time()
        
        # 计算移动距离
        dx = abs(current_pos[0] - self.last_mouse_pos[0])
        dy = abs(current_pos[1] - self.last_mouse_pos[1])
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # 超过阈值视为活动
        if distance > self.config.mouse_move_threshold:
            self.last_mouse_pos = current_pos
            self.last_mouse_time = current_time
            if self.is_mouse_idle:
                logging.debug('鼠标恢复活动')
                self.is_mouse_idle = False
            return False
        
        # 检测空闲超时
        if (current_time - self.last_mouse_time) > (self.config.mouse_idle_time * 60):
            if not self.is_mouse_idle:
                logging.debug('鼠标进入空闲状态')
                self.is_mouse_idle = True
            return True
        return self.is_mouse_idle

    def process_window_title(self, raw_title: str) -> str:
        """处理窗口标题格式"""
        title = raw_title.strip()
        if self.config.reverse_app_name:
            parts = title.split(' - ')
            return ' - '.join(reversed(parts)) if len(parts) > 1 else title
        return title

# --------------------------
# 设备监控核心逻辑
# --------------------------
class DeviceMonitor:
    """设备状态监控器"""
    def __init__(self, config: AppConfig, state: DeviceState):
        self.config = config
        self.state = state
        self._setup_logging()
    
    def _setup_logging(self):
        """初始化日志配置"""
        handlers = [logging.StreamHandler()]
        if self.config.log_file:
            handlers.append(logging.FileHandler('mirror.log', encoding='utf-8'))
            
        logging.basicConfig(
            level=self.config.log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=handlers
        )
    
    def send_state(self, using: bool, window: str):
        """发送状态到服务器"""
        try:
            resp = requests.post(
                url=f'{self.config.server}/device/set',
                json={
                    'secret': self.config.secret,
                    'id': self.config.device_id,
                    'show_name': self.config.device_show_name,
                    'using': using,
                    'app_name': window
                },
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            resp.raise_for_status()
            self.state.last_window = window
        except requests.RequestException as e:
            logging.warning(f'状态发送失败: {e}')
    
    def _should_update(self, new_window: str, mouse_idle: bool) -> bool:
        """判断是否需要更新状态"""
        return (mouse_idle != self.state.is_mouse_idle) or (new_window != self.state.last_window)
    
    def _handle_skipped_window(self, window: str) -> str:
        """处理需要跳过的窗口"""
        if window not in self.config.skipped_names:
            return window
        
        logging.debug(f'跳过窗口: {window}')
        # 使用上次有效窗口
        fallback = self.state.last_window if self.state.last_window not in self.config.skipped_names else ''
        return fallback if fallback else None
    
    def update_state(self):
        """执行状态检测和更新"""
        try:
            # 获取当前窗口
            raw_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            current_window = self.state.process_window_title(raw_window)
            mouse_idle = self.state.check_mouse_idle()
            
            # 处理跳过窗口
            processed_window = self._handle_skipped_window(current_window)
            if not processed_window:
                return
            
            # 判断使用状态
            using = not (processed_window in self.config.not_using_names or mouse_idle)
            
            # 发送更新
            if self._should_update(processed_window, mouse_idle):
                logging.info(f'状态更新: using={using}, app={processed_window}, idle={mouse_idle}')
                self.send_state(using, processed_window)
        except Exception as e:
            logging.error(f'状态更新异常: {e}')

# --------------------------
# 系统功能模块
# --------------------------
def check_network():
    """检测网络连接"""
    try:
        response = requests.get('http://baidu.com', timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def message_loop():
    """(需异步执行) 窗口消息循环"""
    def create_window():
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = on_shutdown
        wc.lpszClassName = "LoggingWindow"
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, "状态监控", win32con.WS_OVERLAPPEDWINDOW,
                                     100, 100, 600, 400, 0, 0, wc.hInstance, None)
    
    def on_shutdown(hwnd, msg, wparam, lparam):
        """关机事件处理"""
        if msg == win32con.WM_QUERYENDSESSION:
            logging.info("系统正在关机或注销...")
            return True
        return 0
    
    hwnd = create_window()
    logging.info("窗口消息循环已启动")
    win32gui.PumpMessages()

# --------------------------
# 主程序入口
# --------------------------
def main():
    config = AppConfig()
    state = DeviceState(config)
    monitor = DeviceMonitor(config, state)
    
    # 启动消息循环线程
    threading.Thread(target=message_loop, daemon=True).start()
    
    # 等待网络连接
    while not check_network():
        logging.warning('网络连接失败，5秒后重试...')
        sleep(5)
    
    # 主监控循环
    while True:
        try:
            monitor.update_state()
            sleep(config.check_interval)
        except KeyboardInterrupt:
            monitor.send_state(False, "用户中断")
            sys.exit(0)
        except Exception as e:
            logging.error(f'主循环异常: {e}')
            sleep(10)

if __name__ == '__main__':
    main()