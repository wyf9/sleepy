const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay)); // 自定义 sleep (只能在 async 中加 await 使用)

function sliceText(text, maxLength) {
    /*
    截取一段文本的置顶长度
    */
    if (maxLength == 0) { // disabled
        return text;
    } else if (text.length <= maxLength) { // shorter than maxLength
        return text;
    }
    return text.slice(0, maxLength) + '...';
}

function escapeHtml(str) {
    /*
    escape some chars for HTML
    */
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function escapeJs(str) {
    /*
    escape some chars for JS
    */
    return String(str)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, '\\\'')
        .replace(/"/g, '\\"')
        .replace(/\r/g, '\\r')
        .replace(/\n/g, '\\n')
        .replace(/\t/g, '\\t')
        .replace(/\f/g, '\\f')
        .replace(/</g, '\\x3c')
        .replace(/>/g, '\\x3e');
}

function getFormattedDate(date) {
    /*
    convert data object to str like:
    1145-01-14 19:19:08
    */
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

document.addEventListener('DOMContentLoaded', function () {
    // 检查浏览器是否支持 SSE
    if (typeof (EventSource) !== "undefined") {
        const statusElement = document.getElementById('status');

        // 设置正在连接的状态
        document.getElementById('last-updated').innerHTML = `正在连接服务器... <a href="javascript:location.reload();" target="_self" style="color: rgb(0, 255, 0);">刷新页面</a>`;

        // 创建 EventSource
        const evtSource = new EventSource('/events');

        evtSource.onopen = function () {
            console.log('SSE连接已建立');
        };

        evtSource.onerror = function (e) {
            console.error('SSE 错误', e);
            document.getElementById('last-updated').innerHTML = `连接服务器失败，尝试重新连接... <a href="javascript:location.reload();" target="_self" style="color: rgb(0, 255, 0);">刷新页面</a>`;
            statusElement.textContent = '[!错误!]';
            document.getElementById('additional-info').textContent = '无法连接到服务器，请稍后再试';
            let last_status = statusElement.classList.item(0);
            statusElement.classList.remove(last_status);
            statusElement.classList.add('error');
        };

        evtSource.onmessage = function (event) {
            if (document.visibilityState == 'visible') {
                console.log('收到数据更新');
                const data = JSON.parse(event.data);

                if (data.success) {
                    // 更新状态 (status, additional-info)
                    statusElement.textContent = data.info.name;
                    document.getElementById('additional-info').innerHTML = data.info.desc;
                    let last_status = statusElement.classList.item(0);
                    statusElement.classList.remove(last_status);
                    statusElement.classList.add(data.info.color);

                    // 更新设备状态 (device-status)
                    var deviceStatus = '<hr/>';
                    const devices = Object.values(data.device);

                    for (let device of devices) {
                        let device_app;
                        if (device.using) {
                            const escapedAppName = escapeHtml(device.app_name);
                            const jsShowName = escapeJs(device.show_name);
                            const jsAppName = escapeJs(device.app_name);
                            const jsCode = `alert('${jsShowName}: \\n${jsAppName}')`;
                            const escapedJsCode = escapeHtml(jsCode);

                            device_app = `
<a class="awake" 
    title="${escapedAppName}" 
    href="javascript:${escapedJsCode}">
${sliceText(escapedAppName, data.device_status_slice)}
</a>`;
                        } else {
                            device_app = '<a class="sleeping">未在使用</a>';
                        }
                        deviceStatus += `${escapeHtml(device.show_name)}: ${device_app} <br/>`;
                    }

                    if (deviceStatus == '<hr/>') {
                        deviceStatus = '';
                    }
                    document.getElementById('device-status').innerHTML = deviceStatus;

                    // 更新最后更新时间 (last-updated)
                    timenow = getFormattedDate(new Date());
                    document.getElementById('last-updated').innerHTML = `
最后更新:
<a class="awake" 
title="服务器时区: ${data.timezone}" 
href="javascript:alert('浏览器最后更新时间: ${timenow}\\n数据最后更新时间 (基于服务器时区): ${data.last_updated}\\n服务端时区: ${data.timezone}')">
${data.last_updated}
</a>`;
                } else {
                    statusElement.textContent = '[!错误!]';
                    document.getElementById('additional-info').textContent = data.info || '未知错误';
                    let last_status = statusElement.classList.item(0);
                    statusElement.classList.remove(last_status);
                    statusElement.classList.add('error');
                }
            } else {
                console.log('tab not visible, skip update');
            }
        };
    } else {
        // 浏览器不支持SSE，回退到原来的轮询方案
        console.log('Browser does not support SSE, falling back to polling');
        update();
    }
});

// 保留原来的update函数作为后备方案
async function update() {
    let refresh_time = 5000;
    let routerIndex = window.location.href.indexOf('?');
    let url = window.location.href.slice(0, routerIndex > 0 ? routerIndex : window.location.href.length);
    while (true) {
        if (document.visibilityState == 'visible') {
            console.log('tab visible, updating...');
            let success_flag = true;
            let errorinfo = '';
            const statusElement = document.getElementById('status');
            // --- show updating
            document.getElementById('last-updated').innerHTML = `正在更新状态, 请稍候... <a href="javascript:location.reload();" target="_self" style="color: rgb(0, 255, 0);">刷新页面</a>`;
            // fetch data
            fetch(url + 'query', { timeout: 10000 })
                .then(response => response.json())
                .then(async (data) => {
                    console.log(data);
                    if (data.success) {
                        // update status (status, additional-info)
                        statusElement.textContent = data.info.name;
                        document.getElementById('additional-info').innerHTML = data.info.desc;
                        last_status = statusElement.classList.item(0);
                        statusElement.classList.remove(last_status);
                        statusElement.classList.add(data.info.color);
                        // update device status (device-status)
                        var deviceStatus = '<hr/>';
                        const devices = Object.values(data.device);

                        for (let device of devices) {
                            let device_app;
                            if (device.using) {

                                const escapedAppName = escapeHtml(device.app_name);

                                const jsShowName = escapeJs(device.show_name);
                                const jsAppName = escapeJs(device.app_name);

                                const jsCode = `alert('${jsShowName}: \\n${jsAppName}')`;
                                const escapedJsCode = escapeHtml(jsCode);

                                device_app = `
<a class="awake" 
    title="${escapedAppName}" 
    href="javascript:${escapedJsCode}">
${sliceText(escapedAppName, data.device_status_slice)}
</a>
`;
                            } else {
                                device_app = '<a class="sleeping">未在使用</a>';
                            }
                            deviceStatus += `${escapeHtml(device.show_name)}: ${device_app} <br/>`;
                        }
                        if (deviceStatus == '<hr/>') {
                            deviceStatus = '';
                        }
                        document.getElementById('device-status').innerHTML = deviceStatus;
                        // update last update time (last-updated)
                        timenow = getFormattedDate(new Date());
                        document.getElementById('last-updated').innerHTML = `
最后更新:
<a
class="awake" 
title="服务器时区: ${data.timezone}" 
href="javascript:alert('
浏览器最后更新时间: ${timenow}\\n
数据最后更新时间 (基于服务器时区): ${data.last_updated}\\n
服务端时区: ${data.timezone}
')">
${data.last_updated}
</a>
`;
                        // update refresh time
                        refresh_time = data.refresh;
                    } else {
                        errorinfo = data.info;
                        success_flag = false;
                    }
                })
                .catch(error => {
                    errorinfo = error;
                    success_flag = false;
                });
            // 出错时显示
            if (!success_flag) {
                statusElement.textContent = '[!错误!]';
                document.getElementById('additional-info').textContent = errorinfo;
                last_status = statusElement.classList.item(0);
                statusElement.classList.remove(last_status);
                statusElement.classList.add('error');
            }
        } else {
            console.log('tab not visible, skip update');
        }

        await sleep(refresh_time);
    }
}
