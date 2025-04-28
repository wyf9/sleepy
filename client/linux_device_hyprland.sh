#!/usr/bin/env bash

# --- config start
API_URL="https://sleepy.wyf9.top/device/set" # 你的完整 API 地址，以 `/device/set` 结尾
SECRET="绝对猜不出来的密码"                # 你的 secret
ID="hyprland-device"                      # 你的设备 id, 唯一
SHOW_NAME="Hyprland PC"                   # 你的设备名称, 将显示在网页上
CHECK_INTERVAL=5                          # 心跳检查间隔 (秒)
HEARTBEAT_INTERVAL=60                     # 心跳发送间隔 (秒)
# --- config end

# --- check dependencies
for cmd in socat hyprctl jq curl; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: command not found: $cmd"
        exit 1
    fi
done

# --- logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [hyprland_device] $1" | sed "s/$SECRET/[REPLACED]/g"
}

# --- state variables
last_app_name=""
last_using=false
last_send_time=0

# --- send status function
send_status() {
    local using=$1
    local app_name=$2
    local force_send=${3:-false} # Optional third argument to force send (for heartbeat)
    local current_time=$(date +%s)

    # Determine if status changed or heartbeat interval reached
    local status_changed=false
    if [[ "$using" != "$last_using" ]] || [[ "$app_name" != "$last_app_name" ]]; then
        status_changed=true
    fi

    local should_send_heartbeat=false
    # Ensure last_send_time is initialized
    if [[ -z "$last_send_time" ]]; then
        last_send_time=0
    fi
    if (( current_time - last_send_time >= HEARTBEAT_INTERVAL )); then
        should_send_heartbeat=true
    fi

    if [[ "$force_send" == "true" ]]; then
      log "Heartbeat forced send."
      should_send_heartbeat=true # Ensure heartbeat flag is true if forced
    elif ! $status_changed && ! $should_send_heartbeat; then
        # log "Status unchanged and heartbeat interval not reached, skipping send."
        return
    fi

    if $status_changed; then
         log "Status changed: using=$using, app_name='$app_name'"
    elif $should_send_heartbeat; then
         log "Heartbeat interval reached, sending status."
    fi

    log "Sending status to $API_URL"
    local payload
    # Ensure using is 'true' or 'false' string for jq
    local using_str=$( [[ "$using" == "true" ]] && echo "true" || echo "false" )
    payload=$(jq -n --arg secret "$SECRET" --arg id "$ID" --arg show_name "$SHOW_NAME" --argjson using "$using_str" --arg app_name "$app_name" \
        '{secret: $secret, id: $id, show_name: $show_name, using: $using, app_name: $app_name}')

    # Use curl to send POST request and capture HTTP status code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        --data "$payload" --connect-timeout 5 --max-time 10)

    curl_exit_code=$?
    if [[ $curl_exit_code -ne 0 ]]; then
        log "Error: curl command failed with exit code $curl_exit_code."
        # Don't update last state on failure
        return 1
    elif [[ $http_code -ne 200 ]]; then
        log "Error: API request failed with HTTP status code $http_code."
        # Don't update last state on failure
        return 1
    else
        log "Status sent successfully (HTTP $http_code)."
        # Update last state only on success
        last_app_name="$app_name"
        last_using=$using # Store as boolean 'true' or 'false'
        last_send_time=$current_time
    fi
}

# --- heartbeat check loop (run in background)
heartbeat_check() {
    while true; do
        sleep $CHECK_INTERVAL
        local current_time=$(date +%s)
        # Ensure last_send_time is initialized
        if [[ -z "$last_send_time" ]]; then
            last_send_time=0
        fi
        if (( current_time - last_send_time >= HEARTBEAT_INTERVAL )); then
            log "Heartbeat interval reached, triggering send."
            # Send current known state as heartbeat, force send
            send_status "$last_using" "$last_app_name" true
        fi
    done
}

# --- cleanup function on exit
cleanup() {
    log "Script exiting. Sending 'using: false' status."
    # Send final status, force it even if interval not reached
    # Use a generic app_name like 'Offline' or keep last_app_name? Keep last for now.
    send_status false "$last_app_name" true
    log "Killing heartbeat process $heartbeat_pid"
    # Check if PID exists before killing
    if [[ -n "$heartbeat_pid" ]] && ps -p $heartbeat_pid > /dev/null; then
        kill $heartbeat_pid
    fi
    log "Cleanup finished."
    # exit 0 # Trap handler should not exit itself unless necessary
}

# --- main logic
main() {
    # Set trap for cleanup on exit signals
    trap cleanup INT TERM EXIT

    # Start heartbeat check in the background
    heartbeat_check &
    heartbeat_pid=$!
    log "Heartbeat check started with PID $heartbeat_pid"

    # Initial send: Assume not using initially until first window event
    send_status false "" true

    # Listen to Hyprland socket events
    # Ensure HYPRLAND_INSTANCE_SIGNATURE is set
    if [[ -z "$HYPRLAND_INSTANCE_SIGNATURE" ]]; then
        log "Error: HYPRLAND_INSTANCE_SIGNATURE environment variable not set."
        exit 1
    fi
    local socket_path="/tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock"
    if [[ ! -S "$socket_path" ]]; then
         log "Error: Hyprland socket not found at $socket_path"
         exit 1
    fi

    socat -U - "UNIX-CONNECT:$socket_path" | while read -r line; do
        # log "Received line: $line" # Debugging line
        if [[ $line == activewindow>>* ]]; then
            # Extract window class after "activewindow>>"
            local window_info=${line#*>>}
            # Sometimes it's class,instance - take the first part
            local window_class=$(echo "$window_info" | cut -d',' -f1)

            if [[ -n "$window_class" ]]; then
                 # log "Active window class: $window_class" # Debugging line
                 send_status true "$window_class"
            else
                 # If class is empty, maybe the window closed or switched to empty workspace?
                 # Send using: false with a generic name or empty string
                 log "Active window event, but no class found. Sending 'using: false'."
                 send_status false ""
            fi
        # Consider adding other events if needed for more accuracy
        # elif [[ $line == closewindow>>* ]]; then ...
        # elif [[ $line == workspace>>* ]]; then ...
        fi
    done

    # If socat exits unexpectedly (e.g., Hyprland restarts), the script might end here.
    log "socat listener finished or failed."
}

# --- start main function
main
