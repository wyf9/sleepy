// 保存设置
document.getElementById('save-settings').addEventListener('click', async function() {
    const db_path = document.getElementById('db_path').value;
    const max_apps = parseInt(document.getElementById('max_apps').value);
    const default_days = parseInt(document.getElementById('default_days').value);
    const chart_height = parseInt(document.getElementById('chart_height').value);
    const colors_str = document.getElementById('colors').value;

    // 解析颜色列表
    const colors = colors_str.split('\n')
        .map(color => color.trim())
        .filter(color => color.length > 0);

    try {
        const response = await fetch('/plugin/app-chart/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                db_path,
                max_apps,
                default_days,
                chart_height,
                colors
            })
        });

        const data = await response.json();
        const messageEl = document.getElementById('settings-message');

        if (data.success) {
            messageEl.textContent = '设置已保存，重启服务后生效';
            messageEl.className = 'settings-message success';
            messageEl.style.display = 'block';
        } else {
            messageEl.textContent = '保存失败: ' + data.message;
            messageEl.className = 'settings-message error';
            messageEl.style.display = 'block';
        }

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        const messageEl = document.getElementById('settings-message');
        messageEl.textContent = '保存失败: ' + error.message;
        messageEl.className = 'settings-message error';
        messageEl.style.display = 'block';
    }
});

// 重置设置
document.getElementById('reset-settings').addEventListener('click', function() {
    document.getElementById('db_path').value = '{{ db_path }}';
    document.getElementById('max_apps').value = '{{ max_apps }}';
    document.getElementById('default_days').value = '{{ default_days }}';
    document.getElementById('chart_height').value = '{{ chart_height }}';
    document.getElementById('colors').value = '{{ colors_str }}';
});
