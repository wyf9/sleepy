// 加载数据统计
async function loadDataStats() {
    const statsEl = document.querySelector('.data-stats');
    statsEl.innerHTML = '<div class="loading">加载数据统计中...</div>';

    try {
        const response = await fetch('/plugin/app-chart/data-stats');
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '加载数据失败');
        }

        statsEl.innerHTML = `
            <h4>数据统计</h4>
            <div class="data-stat-item">
                <span class="data-stat-label">应用使用记录数:</span>
                <span>${data.stats.usage_count}</span>
            </div>
            <div class="data-stat-item">
                <span class="data-stat-label">每日统计记录数:</span>
                <span>${data.stats.daily_count}</span>
            </div>
            <div class="data-stat-item">
                <span class="data-stat-label">追踪的应用数:</span>
                <span>${data.stats.app_count}</span>
            </div>
            <div class="data-stat-item">
                <span class="data-stat-label">数据库大小:</span>
                <span>${data.stats.db_size}</span>
            </div>
            <div class="data-stat-item">
                <span class="data-stat-label">最早记录日期:</span>
                <span>${data.stats.first_date || '无数据'}</span>
            </div>
            <div class="data-stat-item">
                <span class="data-stat-label">最新记录日期:</span>
                <span>${data.stats.last_date || '无数据'}</span>
            </div>
        `;
    } catch (error) {
        console.error('Error loading data stats:', error);
        statsEl.innerHTML = `<div class="error-message">加载数据统计失败: ${error.message}</div>`;
    }
}

// 清除所有数据
async function clearAllData() {
    if (!confirm('确定要清除所有应用使用时间数据吗？此操作不可恢复！')) {
        return;
    }

    const messageEl = document.getElementById('data-message');

    try {
        const response = await fetch('/plugin/app-chart/clear-data', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            messageEl.textContent = '所有数据已清除';
            messageEl.className = 'data-message success';
            messageEl.style.display = 'block';

            // 重新加载统计
            loadDataStats();
        } else {
            messageEl.textContent = '清除数据失败: ' + data.message;
            messageEl.className = 'data-message error';
            messageEl.style.display = 'block';
        }

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        messageEl.textContent = '清除数据失败: ' + error.message;
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
    }
}

// 导出数据
async function exportData() {
    try {
        const response = await fetch('/plugin/app-chart/export-data');
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '导出数据失败');
        }

        // 创建下载链接
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data.data, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "app_usage_data.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();

        const messageEl = document.getElementById('data-message');
        messageEl.textContent = '数据导出成功';
        messageEl.className = 'data-message success';
        messageEl.style.display = 'block';

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        const messageEl = document.getElementById('data-message');
        messageEl.textContent = '导出数据失败: ' + error.message;
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
    }
}

// 下载数据库
async function downloadDatabase() {
    try {
        const messageEl = document.getElementById('data-message');
        messageEl.textContent = '准备下载数据库...';
        messageEl.className = 'data-message success';
        messageEl.style.display = 'block';

        // 创建下载链接
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", '/plugin/app-chart/download-db');
        downloadAnchorNode.setAttribute("download", "app_chart.db");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();

        messageEl.textContent = '数据库下载已开始';

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        const messageEl = document.getElementById('data-message');
        messageEl.textContent = '下载数据库失败: ' + error.message;
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
    }
}

// 导入数据库文件
async function importDatabase() {
    const fileInput = document.getElementById('db-file');
    const messageEl = document.getElementById('data-message');

    if (!fileInput.files || fileInput.files.length === 0) {
        messageEl.textContent = '请选择数据库文件';
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
        return;
    }

    const file = fileInput.files[0];
    if (!file.name.endsWith('.db')) {
        messageEl.textContent = '请选择有效的 SQLite 数据库文件 (.db)';
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
        return;
    }

    if (!confirm('导入数据库将替换当前所有数据，确定要继续吗？')) {
        return;
    }

    const formData = new FormData();
    formData.append('db_file', file);

    try {
        messageEl.textContent = '正在导入数据库...';
        messageEl.className = 'data-message info';
        messageEl.style.display = 'block';

        const response = await fetch('/plugin/app-chart/import-db', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            messageEl.textContent = '数据库导入成功';
            messageEl.className = 'data-message success';

            // 清空文件输入
            fileInput.value = '';

            // 重新加载统计
            loadDataStats();
        } else {
            messageEl.textContent = '导入失败: ' + data.message;
            messageEl.className = 'data-message error';
        }
    } catch (error) {
        messageEl.textContent = '导入失败: ' + error.message;
        messageEl.className = 'data-message error';
    }

    // 3秒后隐藏消息
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

// 导入 JSON 数据
async function importJsonData() {
    const fileInput = document.getElementById('json-file');
    const clearBeforeImport = document.getElementById('clear-before-import').checked;
    const messageEl = document.getElementById('data-message');

    if (!fileInput.files || fileInput.files.length === 0) {
        messageEl.textContent = '请选择 JSON 数据文件';
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
        return;
    }

    const file = fileInput.files[0];
    if (!file.name.endsWith('.json')) {
        messageEl.textContent = '请选择有效的 JSON 文件 (.json)';
        messageEl.className = 'data-message error';
        messageEl.style.display = 'block';
        return;
    }

    if (clearBeforeImport && !confirm('导入前将清除所有现有数据，确定要继续吗？')) {
        return;
    }

    try {
        // 读取文件内容
        const fileContent = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });

        // 解析 JSON
        let jsonData;
        try {
            jsonData = JSON.parse(fileContent);
        } catch (e) {
            throw new Error('无效的 JSON 格式');
        }

        // 验证 JSON 结构
        if (!jsonData.daily_stats || !jsonData.app_usage) {
            throw new Error('无效的数据格式，缺少必要的数据字段');
        }

        messageEl.textContent = '正在导入数据...';
        messageEl.className = 'data-message info';
        messageEl.style.display = 'block';

        // 发送数据到服务器
        const response = await fetch('/plugin/app-chart/import-json', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: jsonData,
                clear_before_import: clearBeforeImport
            })
        });

        const data = await response.json();

        if (data.success) {
            messageEl.textContent = `数据导入成功: ${data.stats.daily_count} 条每日记录, ${data.stats.usage_count} 条使用记录`;
            messageEl.className = 'data-message success';

            // 清空文件输入
            fileInput.value = '';

            // 重新加载统计
            loadDataStats();
        } else {
            messageEl.textContent = '导入失败: ' + data.message;
            messageEl.className = 'data-message error';
        }
    } catch (error) {
        messageEl.textContent = '导入失败: ' + error.message;
        messageEl.className = 'data-message error';
    }

    // 3秒后隐藏消息
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载初始数据
    loadDataStats();

    // 绑定事件
    document.getElementById('refresh-stats').addEventListener('click', loadDataStats);
    document.getElementById('clear-data').addEventListener('click', clearAllData);
    document.getElementById('export-data').addEventListener('click', exportData);
    document.getElementById('download-db').addEventListener('click', downloadDatabase);

    // 绑定导入功能事件
    document.getElementById('import-db-btn').addEventListener('click', importDatabase);
    document.getElementById('import-json-btn').addEventListener('click', importJsonData);
});
