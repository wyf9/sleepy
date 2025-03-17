// 实用函数
const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

function sliceText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.slice(0, maxLength - 3) + '...';
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function escapeJs(str) {
    return String(str)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}

function getFormattedDate(date) {
    const pad = (num) => (num < 10 ? '0' + num : num);
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

// 全局变量 - 重要：保证所有函数可访问
let evtSource = null;
let reconnectInProgress = false;
let countdownInterval = null;
let connectionCheckTimer = null;
let lastEventTime = Date.now();
let connectionAttempts = 0;
const maxReconnectDelay = 30000; // 最大重连延迟时间为30秒

// 重连函数
function reconnectWithDelay(delay) {
    if (reconnectInProgress) {
        console.log('已经在重连过程中，忽略此次请求');
        return;
    }

    reconnectInProgress = true;
    console.log(`安排在${delay / 1000}秒后重连`);

    // 清除可能存在的倒计时
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }

    // 更新UI状态
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.textContent = '[!错误!]';
        document.getElementById('additional-info').textContent = '与服务器的连接已断开，正在尝试重新连接...';
        let last_status = statusElement.classList.item(0);
        statusElement.classList.remove(last_status);
        statusElement.classList.add('error');
    }

    // 添加倒计时更新
    let remainingSeconds = Math.floor(delay / 1000);
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.innerHTML = `连接服务器失败，${remainingSeconds}秒后重新连接... <a href="javascript:location.reload();" target="_self" style="color: rgb(0, 255, 0);">刷新页面</a>`;
    }

    countdownInterval = setInterval(() => {
        remainingSeconds--;
        if (remainingSeconds > 0 && lastUpdatedElement) {
            lastUpdatedElement.innerHTML = `连接服务器失败，${remainingSeconds}秒后重新连接... <a href="javascript:location.reload();" target="_self" style="color: rgb(0, 255, 0);">刷新页面</a>`;
        } else if (remainingSeconds <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);

    setTimeout(() => {
        console.log('开始重连...');
        clearInterval(countdownInterval); // 清除倒计时
        setupEventSource();
        reconnectInProgress = false;
    }, delay);
}

// 建立SSE连接
function setupEventSource() {
    // 重置重连状态
    reconnectInProgress = false;

    // 清除可能存在的倒计时
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }

    // 清除旧的定时器
    if (connectionCheckTimer) {
        clearTimeout(connectionCheckTimer);
        connectionCheckTimer = null;
    }

    // 更新UI状态
    const statusElement = document.getElementById('status');
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.innerHTML = `正在连接服务器... <a href="javascript:location.reload();" target="_self" style="color: rgb(0, 255, 0);">刷新页面</a>`;
    }

    // 关闭旧连接
    if (evtSource) {
        evtSource.close();
    }

    // 创建新连接
    evtSource = new EventSource('/events');

    // 监听连接打开事件
    evtSource.onopen = function () {
        console.log('SSE连接已建立');
        connectionAttempts = 0; // 重置重连计数
        lastEventTime = Date.now(); // 初始化最后事件时间

        // 更新连接状态UI (如果有)
        const connectionStatus = document.getElementById('connection-status');
        if (connectionStatus) {
            connectionStatus.textContent = '连接正常';
            connectionStatus.style.color = '#00ff00';
        }
    };

    // 监听更新事件
    evtSource.addEventListener('update', function (event) {
        lastEventTime = Date.now(); // 更新最后收到消息的时间

        console.log('收到数据更新');
        const data = JSON.parse(event.data);

        // 处理更新数据
        if (data.success) {
            // 更新状态
            if (statusElement) {
                statusElement.textContent = data.info.name;
                document.getElementById('additional-info').innerHTML = data.info.desc;
                let last_status = statusElement.classList.item(0);
                statusElement.classList.remove(last_status);
                statusElement.classList.add(data.info.color);
            }

            // 更新设备状态
            var deviceStatus = '<hr/><b><p id="device-status"><i>Device</i> Status</p></b>';
            const devices = Object.values(data.device);

            for (let device of devices) {
                let device_app;
                const escapedAppName = escapeHtml(device.app_name);
                if (device.using) {
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
                    device_app = `
<a class="sleeping">
${sliceText(escapedAppName, data.device_status_slice)}
</a>`
                }
                deviceStatus += `${escapeHtml(device.show_name)}: ${device_app} <br/>`;
            }

            if (deviceStatus == '<hr/><b><p id="device-status"><i>Device</i> Status</p></b>') {
                deviceStatus = '';
            }

            const deviceStatusElement = document.getElementById('device-status');
            if (deviceStatusElement) {
                deviceStatusElement.innerHTML = deviceStatus;
            }

            // 更新最后更新时间
            const timenow = getFormattedDate(new Date());
            if (lastUpdatedElement) {
                lastUpdatedElement.innerHTML = `
最后更新:
<a class="awake" 
title="服务器时区: ${data.timezone}" 
href="javascript:alert('浏览器最后更新时间: ${timenow}\\n数据最后更新时间 (基于服务器时区): ${data.last_updated}\\n服务端时区: ${data.timezone}')">
${data.last_updated}
</a>`;
            }
        } else {
            if (statusElement) {
                statusElement.textContent = '[!错误!]';
                document.getElementById('additional-info').textContent = data.info || '未知错误';
                let last_status = statusElement.classList.item(0);
                statusElement.classList.remove(last_status);
                statusElement.classList.add('error');
            }
        }
    });

    // 监听心跳事件
    evtSource.addEventListener('heartbeat', function (event) {
        console.log('收到心跳:', event.data);
        lastEventTime = Date.now(); // 更新最后收到消息的时间

        // 更新连接状态UI (如果有)
        const connectionStatus = document.getElementById('connection-status');
        if (connectionStatus) {
            connectionStatus.textContent = '连接正常';
            connectionStatus.style.color = '#00ff00';
        }
    });

    // 错误处理 - 立即开始重连
    evtSource.onerror = function (e) {
        console.error('SSE 错误', e);
        evtSource.close();

        // 计算重连延迟时间 (指数退避)
        const reconnectDelay = Math.min(1000 * Math.pow(2, connectionAttempts), maxReconnectDelay);
        connectionAttempts++;

        // 使用统一重连函数
        reconnectWithDelay(reconnectDelay);
    };

    // 设置长时间未收到消息的检测
    function checkConnectionStatus() {
        const currentTime = Date.now();
        const elapsedTime = currentTime - lastEventTime;

        // 只有在连接正常但长时间未收到消息时才触发重连
        if (elapsedTime > 60000 && !reconnectInProgress) {
            console.warn('长时间未收到服务器消息，正在重新连接...');
            evtSource.close();

            // 使用与onerror相同的重连逻辑
            const reconnectDelay = Math.min(1000 * Math.pow(2, connectionAttempts), maxReconnectDelay);
            connectionAttempts++;
            reconnectWithDelay(reconnectDelay);
        }

        // 仅当没有正在进行的重连时才设置下一次检查
        if (!reconnectInProgress) {
            connectionCheckTimer = setTimeout(checkConnectionStatus, 10000);
        }
    }

    // 启动连接状态检查
    connectionCheckTimer = setTimeout(checkConnectionStatus, 10000);

    // 在页面卸载时关闭连接
    window.addEventListener('beforeunload', function () {
        if (evtSource) {
            evtSource.close();
        }
    });
}

// 初始化SSE连接或回退到轮询
document.addEventListener('DOMContentLoaded', function () {
    // 初始化变量
    lastEventTime = Date.now();
    connectionAttempts = 0;

    // 检查浏览器是否支持SSE
    if (typeof (EventSource) !== "undefined") {
        console.log('浏览器支持SSE，开始建立连接...');
        // 初始建立连接
        setupEventSource();
    } else {
        // 浏览器不支持SSE，回退到轮询方案
        console.log('浏览器不支持SSE，回退到轮询方案');
        update();
    }
});

// 原始轮询函数 (仅作为后备方案)
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
                        var deviceStatus = '<hr/><b><p id="device-status"><i>Device</i> Status</p></b>';
                        const devices = Object.values(data.device);

                        for (let device of devices) {
                            let device_app;
                            const escapedAppName = escapeHtml(device.app_name);
                            if (device.using) {
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
                                device_app = `
<a class="sleeping">
${sliceText(escapedAppName, data.device_status_slice)}
</a>`
                            }
                            deviceStatus += `${escapeHtml(device.show_name)}: ${device_app} <br/>`;
                        }
                        if (deviceStatus == '<hr/><b><p id="device-status"><i>Device</i> Status</p></b>') {
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