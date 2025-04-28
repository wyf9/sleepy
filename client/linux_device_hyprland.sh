#!/bin/bash

# linux_device_hyprland.sh
# 在 Linux (Hyprland) 上获取窗口名称\
# by: @inoryxin

# --- config start
URL="http://10.0.0.123:9010/device/set" # API 地址, 以 /device/set 结尾
SECRET="114514" # 密钥
DEVICE_ID="desktop" # 设备 id, 唯一
DEVICE_SHOW_NAME="祈歆的电脑" # 设备显示名称
# --- config end

LASTWINDOW=""
LAST_SEND_TIME=0 # 上次发送时间戳 (秒)
HEARTBEAT_INTERVAL=60 # 心跳间隔 (秒)

while true; do

    HYPRCTL_BIN=$(which hyprctl)

    PACKAGE_NAME=$($HYPRCTL_BIN activewindow | grep "title:" | sed 's/title://g' | sed 's/^[[:space:]]*//')

    echo "$PACKAGE_NAME"

    if [ "$PACKAGE_NAME" = "" ]; then
        STATUS=false
    else
        STATUS=true
    fi

    echo "$STATUS"

    json_data='{
    "secret": "'$SECRET'",
    "id": "'$DEVICE_ID'",
    "show_name": "'$DEVICE_SHOW_NAME'",
    "using": '$STATUS',
    "app_name": "'$PACKAGE_NAME'"
}'

    CURRENT_TIME=$(date +%s)

    if [ "$PACKAGE_NAME" = "$LASTWINDOW" ]; then
        echo "window not change, bypass"
        # --- 添加心跳检查 ---
        if [ $((CURRENT_TIME - LAST_SEND_TIME)) -ge $HEARTBEAT_INTERVAL ]; then
            echo "Heartbeat interval reached, sending current status: $PACKAGE_NAME"
            curl -X POST "$URL" -H "Content-Type: application/json" -d "$json_data"
            LAST_SEND_TIME=$CURRENT_TIME # 更新发送时间
        fi
        # --- 结束添加 ---
    else
        curl -X POST "$URL" -H "Content-Type: application/json" -d "$json_data"
        LAST_SEND_TIME=$CURRENT_TIME # 更新发送时间
    fi

    LASTWINDOW="$PACKAGE_NAME"

    sleep 10
done
