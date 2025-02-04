#!/system/bin/sh

# ========== 基础配置 ==========
URL="https://asfag654-j.hf.space/device/set"
SECRET="你猜"
LOG_NAME="focus_monitor.log"

ARRAY="com.tencent.tmgp.speedmobile com.miHoYo.Yuanshen com.tencent.tmgp.sgame com.tencent.tmgp.supercell.clashofclans com.netease.sky.m4399"

# ========== 判断是否为游戏 ==========
is_game() {
  for item in $ARRAY; do
    if [ "$item" = "$1" ]; then
      log "在玩 $1，延长监测时间"
      echo 600
      break
    else
      continue
    fi
  done
echo 30

}

# ========== 日志系统 ==========
LOG_PATH="${0%/*}/${LOG_NAME}"
log() {
  local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$message" | tee -a "$LOG_PATH"
}

# ========== 核心逻辑 ==========
LAST_PACKAGE=""
echo "" > "$LOG_PATH"
log "===== 服务启动 ====="
device=$(getprop ro.product.model)
log "设备信息：$device Android $(getprop ro.build.version.release) 等待一分钟"

sleep 60
log "开始监测"

while true; do
  CURRENT_FOCUS=$(dumpsys window | grep mCurrentFocus)
  PACKAGE_NAME=$(echo "$CURRENT_FOCUS" | awk -F '[ /}]' '{print $5}' | tr -d '[:space:]')

  if [ "$PACKAGE_NAME" != "$LAST_PACKAGE" ]; then
    log "状态变化: ${LAST_PACKAGE:-none} → ${PACKAGE_NAME:-none}"


# 定义缓存路径
CACHE="${0%/*}/cache.txt"
# 如果不是锁屏状态
if [ "$PACKAGE_NAME" != "NotificationShade" ]; then
    # 先检查缓存
    if [ -f "$CACHE" ]; then
       # 文件存在且是文件
        ApkName=$(awk -F '=' -v pkg="$PACKAGE_NAME" '$1 == pkg {print $2; exit}' "$CACHE")
    fi

    # 如果缓存未命中，则进行网络请求
    if [ -z "$ApkName" ]; then
        #字符串长度为0
        if ! curl --silent --show-error --fail -A "Mozilla/5.0" -o temp.html "https://app.mi.com/details?id=$PACKAGE_NAME"; then
            log "网页请求失败，回退到包名 $PACKAGE_NAME"
            ApkName="$PACKAGE_NAME"
        else
            # 解析网页获取 App 名称
            ApkName=$(sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' temp.html)
            rm -f temp.html  # 清理临时文件

            # 解析失败则回退到包名
            if [ -z "$ApkName" ]; then
                log "网页解析失败，回退到包名 $PACKAGE_NAME"
                ApkName="$PACKAGE_NAME"
            else
                echo "$PACKAGE_NAME=$ApkName" >> "$CACHE"
                log "缓存已更新: $PACKAGE_NAME=$ApkName"              
            fi
        fi
    else
        log "缓存命中: $PACKAGE_NAME=$ApkName"
    fi
else
    ApkName="锁屏了"
fi


    HTTP_CODE=$(curl -G -s --connect-timeout 35 --max-time 100 -w "%{http_code}" -o /tmp/curl_body "$URL" \
      --data-urlencode "secret=$SECRET" \
      --data-urlencode "id=0" \
      --data-urlencode "show_name=OnePlus ACE3" \
      --data-urlencode "using=true" \
      --data-urlencode "app_name=$(echo "$ApkName" | sed 's/-[^-]*$//')")

    if [ "$HTTP_CODE" -ne 200 ]; then
      log "警告：请求失败，状态码 $HTTP_CODE，响应内容：$(cat /tmp/curl_body)"
    fi

    LAST_PACKAGE=$PACKAGE_NAME
  fi

  sleep_time=$(is_game "$PACKAGE_NAME")
  sleep "$sleep_time"
done




