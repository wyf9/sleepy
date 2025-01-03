/*
autoxjs_device.js
使用 Autox.js 编写的安卓自动更新状态脚本
by wyf9. all rights reserved. (?)
*/

// config start
const API_URL = 'https://sleepy.wyf9.top/device/set'; // 你的完整 API 地址，以 `/device/set` 结尾
const SECRET = '绝对猜不出来的密码'; // 你的 secret
const ID = 'a-device'; // 你的设备 id
const SHOW_NAME = '一个设备'; // 你的设备名称
const CHECK_INTERVAL = '3000'; // 检查间隔 (毫秒)
// config end

auto.waitFor(); // 等待无障碍

// 替换了 secret 的日志
function log(msg) {
    try {
        console.log(msg.replace(SECRET, '[REPLACED]'));
    } catch (e) {
        console.log(msg);
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

function check_status() {
    /*
    检查状态并返回 app_name (如未在使用则返回空)
    */
    log(`[check] screen status: ${device.isScreenOn()}`);
    if (!device.isScreenOn()) {
        return ('');
    }
    var app_package = currentPackage(); // 应用包名
    log(`[check] app_package: '${app_package}'`);
    var app_name = app.getAppName(app_package); // 应用名称
    log(`[check] app_name: '${app_name}'`);
    var battery = device.getBattery(); // 电池百分比
    log(`[check] battery: ${battery}%`);
    var retname = `[${battery}%] ${app_name}`; // 返回
    if (!app_name) {
        retname = '';
    }
    return (retname);
}
function send_status() {
    /*
    发送 check_status() 的返回
    */
    var app_name = check_status();
    log(`ret app_name: '${app_name}'`);

    // 判断是否与上次相同
    if (app_name == last_status) {
        log('same as last status, bypass request');
        return;
    }
    last_status = app_name;
    // 判断 using
    if (app_name == '') {
        log('using: false');
        var using = false;
    } else {
        log('using: true');
        var using = true;
    }

    // POST to api
    log(`POST ${API_URL}`);
    r = http.postJson(API_URL, {
        'secret': SECRET,
        'id': ID,
        'show_name': SHOW_NAME,
        'using': using,
        'app_name': app_name
    });
    log(`response: ${r.body.string()}`);
}
while (true) {
    log('---------- Run\n');
    try {
        send_status();
    } catch (e) {
        error(`ERROR sending status: ${e}`);
    }
    sleep(CHECK_INTERVAL);
}
