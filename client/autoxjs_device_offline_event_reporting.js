/*
autoxjs_device_offline_event_reporting.js
使用 Autox.js 编写的安卓自动更新状态脚本
by wyf9. all rights reserved. (?)

@NyaOH-Nahida 二改
新增捕捉退出事件，将退出脚本状态上报到服务器。
*/

// config start
const API_URL = 'https://example.com/device/set'; // 你的完整 API 地址，以 `/device/set` 结尾
const SECRET = '绝对猜不出来的密钥'; // 你的 secret
const ID = '设备ID'; // 你的设备 id
const SHOW_NAME = '设备名称'; // 你的设备名称
const CHECK_INTERVAL = '2000'; // 检查间隔 (毫秒)
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
    // 设备充电状态
    if (device.isCharging()){
        var retname =`[正在充电:${battery}%] ${app_name}`;
    } else {
        var retname = `[电量:${battery}%] ${app_name}`;
    }
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
    console.info(`应用状态: ${app_name}`)
    // toast(`应用状态: ${app_name}`)
    r = http.postJson(API_URL, {
        'secret': SECRET,
        'id': ID,
        'show_name': SHOW_NAME,
        'using': using,
        'app_name': app_name
    });
    log(`response: ${r.body.string()}`);
}

function exit_status_send() {
    // POST 到接口
    var using = false
    var app_name = "";
    log(`POST ${API_URL}`);
    try {
        r = http.postJson(API_URL, {
            'secret': SECRET,
            'id': ID,
            'show_name': SHOW_NAME,
            'using': using,
            'app_name': app_name
        });
        log(`响应: ${r.body.string()}`);
        toast("上报成功！已停止运行。");
    } catch (e) {
        console.error(`错误: ${e}`)
        toast(`上报失败! ${e}`)
    }
}

// 程序退出后上报停止事件
events.on("exit", function () {
    console.log("脚本已停止，正在上报停止事件");
    toast("脚本已停止，正在上报停止事件");
    exit_status_send();
});

while (true) {
    log('---------- Run\n');
    try {
        send_status();
    } catch (e) {
        error(`ERROR sending status: ${e}`);
    }
    sleep(CHECK_INTERVAL);
}
