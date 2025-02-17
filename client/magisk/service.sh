#!/system/bin/sh

# ========== 读取配置文件 ==========
SCRIPT_DIR=${0%/*}
CONFIG_FILE="${SCRIPT_DIR}/config.cfg"
source "$CONFIG_FILE"
# ========== 日志系统 ==========
LOG_PATH="${SCRIPT_DIR}/${LOG_NAME}"
log() {
  message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$message" >> "$LOG_PATH"
}

# ========== 判断是否为游戏 ==========
is_game() {
  pkg="$1"
  for game in $GAME_PACKAGES; do
    if [ "$game" = "$pkg" ]; then
      #log "检测到游戏进程: $pkg，延长监测间隔 600 秒"
      sleep 600
      return 0
    fi
  done
  #log "非游戏进程: $pkg，默认监测间隔 30 秒"
  sleep 30
}

# ========== 解析应用名称 ==========
get_app_name() {
  package_name="$1"

  # 如果是锁屏状态，直接返回
  if [ "$package_name" = "NotificationShade" ]; then
    echo "锁屏了"
    return
  fi

  cached_name=$(awk -F '=' -v pkg="$package_name" '$1 == pkg {print $2; exit}' "$CACHE")
  if [ -n "$cached_name" ]; then
    echo "$cached_name"
    #log "缓存命中: $package_name=$cached_name"
    return
  fi

  # 请求应用商店获取名称
  temp_file="${SCRIPT_DIR}/temp.html"
  if curl --silent --show-error --fail -A "Mozilla/5.0" -o "$temp_file" "https://app.mi.com/details?id=$package_name"; then
    app_name=$(sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' "$temp_file" | sed 's/-[^-]*$//')
    rm -f "$temp_file"

    if [ -n "$app_name" ]; then
      echo "$app_name"
      echo "$package_name=$app_name" >> "$CACHE"
      log "已写入缓存: $package_name=$app_name"
      return
    else
      echo "$package_name"
      log "网页解析失败，回退到包名: $package_name"
    fi
  else
    echo "$package_name"
    log "网页请求失败，回退到包名: $package_name"
  fi
}

# ========== 发送状态请求 ==========
send_status() {
  package_name="$1"
  app_name=$(get_app_name "$package_name")
  
  battery_level=$(dumpsys battery | grep 'level:' | awk '{print $2}')
  res_up="$app_name[${battery_level}%]"
  log "$res_up"
  
  http_code=$(curl -G -s --connect-timeout 35 --max-time 100 -w "%{http_code}" -o /tmp/curl_body "$URL" \
    --data-urlencode "secret=${SECRET}" \
    --data-urlencode "id=0" \
    --data-urlencode "show_name=${device_model}" \
    --data-urlencode "using=true" \
    --data-urlencode "app_name=$res_up")
    
  if [ "$http_code" -ne 200 ]; then
    log "警告：请求失败，状态码 $http_code，响应内容：$(cat /tmp/curl_body)"
  fi
}

# ========== 主流程 ==========
LAST_PACKAGE=""
> "$LOG_PATH"
log "===== 服务启动 ====="

# 获取设备信息
device_model=$(getprop ro.product.model)
android_version=$(getprop ro.build.version.release)
log "设备信息: ${device_model}, Android ${android_version}，等待一分钟"

# 如有需要，可在此处覆盖设备显示名称
device_model="OnePlus ACE3"

sleep 60
log "开！"

# ========== 核心逻辑 ==========
while true; do
  # 获取当前焦点窗口信息
  CURRENT_FOCUS=$(dumpsys window | grep mCurrentFocus)
  PACKAGE_NAME=$(echo "$CURRENT_FOCUS" | awk -F '[ /}]' '{print $5}' | tr -d '[:space:]')

  if [ "$PACKAGE_NAME" != "$LAST_PACKAGE" ] && [ -n "$PACKAGE_NAME" ]; then
    log "状态变化: ${LAST_PACKAGE:-none} → ${PACKAGE_NAME:-none}"
    send_status "$PACKAGE_NAME"
    LAST_PACKAGE="$PACKAGE_NAME"
  fi
  is_game "$PACKAGE_NAME"
done