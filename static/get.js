const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay)); // custom sleep func (only can use in async with await)

async function update() {
    let refresh_time = 5000;
    let routerIndex = window.location.href.indexOf('?');
    let url = window.location.href.slice(0, routerIndex > 0 ? routerIndex : window.location.href.length);
    while (true) {
        let success_flag = true;
        let errorinfo = '';
        const statusElement = document.getElementById('status');
        // --- show updating
        statusElement.textContent = '[更新中...]';
        document.getElementById('additional-info').textContent = '正在更新状态, 请稍候...';
        last_status = statusElement.classList.item(0);
        statusElement.classList.remove(last_status);
        statusElement.classList.add('sleeping');
        // fetch data
        fetch(url + 'query')
            .then(response => response.json())
            .then(async (data) => {
                console.log(data);
                if (data.success) {
                    // update status
                    statusElement.textContent = data.info.name;
                    document.getElementById('additional-info').textContent = data.info.desc;
                    last_status = statusElement.classList.item(0);
                    statusElement.classList.remove(last_status);
                    statusElement.classList.add(data.info.color);
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
        // update error
        if (!success_flag) {
            statusElement.textContent = '[!错误!]';
            document.getElementById('additional-info').textContent = errorinfo;
            last_status = statusElement.classList.item(0);
            statusElement.classList.remove(last_status);
            statusElement.classList.add('error');
        }
        await sleep(refresh_time);
    }
}

update();