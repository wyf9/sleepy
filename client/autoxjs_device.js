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

console.log(device.getBattery());
console.log(device.isScreenOn());
console.log(currentPackage());
console.log(getAppName(currentPackage()));