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

                                device_app = `<a
    class="awake" 
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
                        // update last update time (last-updated)
                        document.getElementById('last-updated').textContent = `最后更新: ${data.last_updated}`;
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

update();
