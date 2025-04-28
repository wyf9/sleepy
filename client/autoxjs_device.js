/*
autoxjs_device.js
使用 Autox.js 编写的安卓自动更新状态脚本
by wyf9;
Co-authored-by: NyaOH-Nahida - 新增捕捉退出事件，将退出脚本状态上报到服务器。
*/

// config start
const API_URL = 'https://sleepy.wyf9.top/device/set'; // 你的完整 API 地址，以 `/device/set` 结尾
const SECRET = '绝对猜不出来的密码'; // 你的 secret
const ID = 'a-device'; // 你的设备 id, 唯一
const SHOW_NAME = '一个设备'; // 你的设备名称, 将显示在网页上
const STATUS_CHECK_INTERVAL = 3000; // 状态检查间隔 (毫秒)
const HEARTBEAT_INTERVAL = 60000; // 心跳发送间隔 (毫秒)
const SKIPPED_NAMES = ['系统界面', '系统界面组件', '手机管家', '平板管家', 'System UI', 'Security tools'] // 获取到的软件名包含列表中之一时忽略
// config end

auto.waitFor(); // 等待无障碍

// 替换了 secret 的日志, 同时添加前缀
function log(msg) {
    try {
        console.log(`[sleepyc] ${msg.replace(SECRET, '[REPLACED]')}`);
    } catch (e) {
        console.log(`[sleepyc] ${msg}`);
    }
}
function error(msg) {
    try {
        console.error(msg.replace(SECRET, '[REPLACED]'));
    } catch (e) {
        console.error(msg);
    }
}

var last_status = '';
var last_send_time = 0; // 上次发送时间戳 (毫秒)

function check_status() {
    /*
    检查状态并返回 app_name (如 未亮屏/获取不到应用名 则返回空)
    [Tip] 如有调试需要可自行取消 log 注释
    */
    // log(`[check] screen status: ${device.isScreenOn()}`);
    if (!device.isScreenOn()) {
        return ('');
    }
    var app_package = currentPackage(); // 应用包名
    // log(`[check] app_package: '${app_package}'`);
    var app_name = app.getAppName(app_package); // 应用名称
    // log(`[check] app_name: '${app_name}'`);
    var battery = device.getBattery(); // 电池百分比
    // log(`[check] battery: ${battery}%`);
    // 判断设备充电状态
    if (device.isCharging()) {
        var retname = `[${battery}% +] ${app_name}`;
    } else {
        var retname = `[${battery}%] ${app_name}`;
    }
    if (!app_name) {
        retname = '';
    }
    return (retname);
}

function send_status() {
    /*
    检查并发送状态
    */
    var app_name = check_status();
    log(`Checked app_name: '${app_name}'`);

    // 判断是否在忽略列表中
    var is_skipped = false;
    for (let i = 0; i < SKIPPED_NAMES.length; i++) {
        if (app_name.includes(SKIPPED_NAMES[i])) {
            log(`Skipping because of: '${SKIPPED_NAMES[i]}'`);
            is_skipped = true;
            break;
        }
    }

    // 判断 using
    var using = true;
    if (app_name == '') {
        log('using: false');
        using = false;
    }

    // 检查状态是否变化 或 是否到达心跳时间
    var status_changed = (app_name !== last_status);
    var should_send_heartbeat = (Date.now() - last_send_time >= HEARTBEAT_INTERVAL);

    // 决定是否发送：状态改变 或 到达心跳时间
    if (status_changed || should_send_heartbeat) {
        if (status_changed) {
            log(`Status changed: '${last_status}' -> '${app_name}', using: ${using}`);
        } else { // Must be heartbeat
            log('Heartbeat interval reached, sending status.');
        }

        // 如果状态是被跳过的，并且不是因为心跳强制发送，则只更新 last_status
        // （心跳需要发送，即使是被跳过的状态）
        if (is_skipped && !should_send_heartbeat) {
             log('Skipped status changed, updating last_status only (not sending).');
             last_status = app_name; // 更新状态以便下次比较
             // 注意：这里不更新 last_send_time，允许心跳机制触发
             return;
        }

        // POST to api
        log(`POST ${API_URL}`);
        try {
            r = http.postJson(API_URL, {
                'secret': SECRET,
                'id': ID,
                'show_name': SHOW_NAME,
                'using': using,
                'app_name': app_name
            });
            log(`response: ${r.body.string()}`);
            // 仅在成功发送后更新 last_status 和 last_send_time
            last_status = app_name;
            last_send_time = Date.now();
        } catch (e) {
            error(`Error sending status: ${e}`);
            // 发送失败时不更新，以便下次重试或触发心跳
        }
    } else {
        // 状态未变且未到心跳时间，不发送
        log('Status unchanged and heartbeat interval not reached, skipping send.');
    }
}

// 程序退出后上报停止事件
events.on("exit", function () {
    log("Script exits. Server will detect offline via heartbeat timeout.");
    toast("[sleepy] 脚本已停止");
});

while (true) {
    log('---------- Run Check');
    try {
        // 检查状态并根据需要发送 (心跳逻辑已包含在内)
        send_status();
    } catch (e) {
        error(`ERROR in main loop: ${e}`);
    }
    sleep(STATUS_CHECK_INTERVAL); // 使用较短的检查间隔
}
