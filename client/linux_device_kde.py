#!/usr/bin/env python3
# coding: utf-8
"""
linux_device_kde.py
在 Linux (KDE) 上获取窗口名称
by: @RikkaNaa
依赖: PyQt5, requests
"""

import atexit
import json
import sys
import time

import requests
from PyQt5.QtCore import QCoreApplication, QTimer, QVariant
from PyQt5.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage

# --- config start
API_URL = "https://sleepy.wyf9.top/device/set"  # 你的完整 API 地址，以 `/device/set` 结尾
SECRET = "绝对猜不出来的密码"  # 你的 secret
ID = "kde-device"  # 你的设备 id, 唯一
SHOW_NAME = "KDE PC"  # 你的设备名称, 将显示在网页上
CHECK_INTERVAL = 5000  # 心跳检查间隔 (毫秒)
HEARTBEAT_INTERVAL = 60000  # 心跳发送间隔 (毫秒)
# --- config end

# --- logging
def log(msg):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [kde_device] {str(msg).replace(SECRET, '[REPLACED]')}")
    except Exception:
        print(f"[{timestamp}] [kde_device] {msg}")  # Fallback if replace fails


# --- state variables
last_app_name = ""
last_using = False
last_send_time = 0  # Store as milliseconds


# --- send status function
def send_status(using: bool, app_name: str, force_send: bool = False):
    global last_app_name, last_using, last_send_time
    current_time = int(time.time() * 1000)  # Use milliseconds

    status_changed = (using != last_using) or (app_name != last_app_name)
    should_send_heartbeat = current_time - last_send_time >= HEARTBEAT_INTERVAL

    if force_send:
        log("Heartbeat forced send.")
        should_send_heartbeat = True  # Ensure heartbeat flag is true if forced
    elif not status_changed and not should_send_heartbeat:
        return

    if status_changed:
        log(f"Status changed: using={using}, app_name='{app_name}'")
    elif should_send_heartbeat:
        log("Heartbeat interval reached, sending status.")

    log(f"Sending status to {API_URL}")
    payload = {"secret": SECRET, "id": ID, "show_name": SHOW_NAME, "using": using, "app_name": app_name}

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        log(f"Status sent successfully (HTTP {response.status_code}).")
        # Update last state only on success
        last_app_name = app_name
        last_using = using
        last_send_time = current_time

    except requests.exceptions.RequestException as e:
        log(f"Error: API request failed: {e}")
    except Exception as e:
        log(f"Error: An unexpected error occurred during send: {e}")

# --- KDE D-Bus interaction
def get_active_window_info():
    try:
        bus = QDBusConnection.sessionBus()
        kwin_interface = QDBusInterface("org.kde.KWin", "/KWin", "org.kde.KWin", bus)

        # Get active window ID
        reply = kwin_interface.call("activeWindow")
        if reply.type() == QDBusMessage.ErrorMessage:
            log(f"Error calling activeWindow: {reply.errorMessage()}")
            return None
        window_id = reply.arguments()[0]

        if window_id <= 0:  # No active window or invalid ID
            log("No active window detected (ID <= 0).")
            return None  # Treat as not using

        # Get window info using the ID
        reply = kwin_interface.call("getWindowInfo", QVariant(window_id))  # Pass ID as QVariant
        if reply.type() == QDBusMessage.ErrorMessage:
            log(f"Error calling getWindowInfo for ID {window_id}: {reply.errorMessage()}")
            return None

        window_info_json = reply.arguments()[0]

        # Parse the JSON info
        try:
            window_info = json.loads(window_info_json)
            app_name = window_info.get("resourceClass", "") or window_info.get("caption", "")
            log(
                f"Active window info: class='{window_info.get('resourceClass', '')}', caption='{window_info.get('caption', '')}' -> Using: '{app_name}'"
            )
            return app_name if app_name else "[No Name]"
        except json.JSONDecodeError as e:
            log(f"Error decoding window info JSON: {e}")
            log(f"Raw JSON: {window_info_json}")
            return "[JSON Error]"
        except Exception as e:
            log(f"Unexpected error parsing window info: {e}")
            return "[Parse Error]"

    except Exception as e:
        log(f"Error interacting with D-Bus: {e}")
        return None

# --- D-Bus signal handler
def on_active_window_changed(window_id):
    log(f"Signal windowActivated received for ID: {window_id}")
    try:
        if window_id <= 0:
            log("Window activated signal for invalid ID <= 0. Sending 'using: false'.")
            send_status(False, "")
            return

        app_name = get_active_window_info()

        if app_name is not None:
            send_status(True, app_name)
        else:
            log("Failed to get info for newly activated window. Sending 'using: false'.")
            send_status(False, "")
    except Exception as e:
        log(f"Error in on_active_window_changed handler: {e}")


# --- Heartbeat check function
def heartbeat_check():
    current_time = int(time.time() * 1000)
    if current_time - last_send_time >= HEARTBEAT_INTERVAL:
        log("Heartbeat interval reached, triggering send.")
        send_status(last_using, last_app_name, force_send=True)


# --- Cleanup function on exit
def cleanup():
    log("Script exiting. Sending 'using: false' status.")
    send_status(False, last_app_name, force_send=True)
    log("Cleanup finished.")


# --- main logic
def main():
    app = QCoreApplication(sys.argv)

    if not QDBusConnection.sessionBus().isConnected():
        log("Error: Cannot connect to D-Bus session bus.")
        sys.exit(1)

    # Connect to KWin's windowActivated signal
    kwin_service = "org.kde.KWin"
    kwin_path = "/KWin"
    kwin_interface_name = "org.kde.KWin"

    bus = QDBusConnection.sessionBus()
    signal_connected = bus.connect(kwin_service, kwin_path, kwin_interface_name, "windowActivated", on_active_window_changed)

    if not signal_connected:
        log("Error: Failed to connect to KWin's windowActivated signal.")
        signal_connected_alt = bus.connect(kwin_service, kwin_path, kwin_interface_name, "activeWindowChanged", on_active_window_changed)
        if not signal_connected_alt:
            log("Error: Also failed to connect to KWin's activeWindowChanged signal.")
        else:
            log("Connected to KWin's activeWindowChanged signal instead.")
    else:
        log("Connected to KWin's windowActivated signal.")

    # Setup heartbeat timer
    timer = QTimer()
    timer.timeout.connect(heartbeat_check)
    timer.start(CHECK_INTERVAL)
    log(f"Heartbeat timer started ({CHECK_INTERVAL}ms interval).")

    # Register cleanup function
    atexit.register(cleanup)

    # Send initial status
    log("Sending initial status...")
    initial_app_name = get_active_window_info()
    if initial_app_name is not None:
        send_status(True, initial_app_name, force_send=True)
    else:
        send_status(False, "", force_send=True)

    log("Starting Qt event loop...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
