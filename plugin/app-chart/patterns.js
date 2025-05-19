// 加载模式列表
async function loadPatterns() {
    const container = document.getElementById('patterns-container');
    if (!container) {
        console.error('Error: patterns-container element not found');
        return;
    }

    container.innerHTML = '<div class="loading">加载中...</div>';

    try {
        const response = await fetch('/plugin/app-chart/patterns/list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '加载模式失败');
        }

        if (data.patterns.length === 0) {
            container.innerHTML = '<div class="empty-message">暂无模式，请添加一个新模式</div>';
            const deleteAllBtn = document.getElementById('delete-all-patterns');
            if (deleteAllBtn) {
                deleteAllBtn.style.display = 'none';
            }
            return;
        }

        // 显示删除所有按钮
        const deleteAllBtn = document.getElementById('delete-all-patterns');
        if (deleteAllBtn) {
            deleteAllBtn.style.display = 'block';
        }

        container.innerHTML = '';

        data.patterns.forEach(pattern => {
            const patternItem = document.createElement('div');
            patternItem.className = 'pattern-item';

            const patternInfo = document.createElement('div');
            patternInfo.className = 'pattern-info';

            const patternText = document.createElement('div');
            patternText.innerHTML = `<span class="pattern-pattern">${pattern.pattern}</span> → <span class="pattern-replacement">${pattern.replacement}</span>`;

            const patternDescription = document.createElement('div');
            patternDescription.className = 'pattern-description';
            patternDescription.textContent = pattern.description || '';

            patternInfo.appendChild(patternText);
            if (pattern.description) {
                patternInfo.appendChild(patternDescription);
            }

            const patternActions = document.createElement('div');
            patternActions.className = 'pattern-actions';

            const deleteButton = document.createElement('button');
            deleteButton.className = 'btn btn-danger btn-sm';
            deleteButton.innerHTML = '<i class="fas fa-trash"></i> 删除';
            deleteButton.title = '删除此模式';
            deleteButton.onclick = () => deletePattern(pattern.id);

            patternActions.appendChild(deleteButton);

            patternItem.appendChild(patternInfo);
            patternItem.appendChild(patternActions);

            container.appendChild(patternItem);
        });
    } catch (error) {
        console.error('Error loading patterns:', error);
        container.innerHTML = `<div class="error-message">加载模式失败: ${error.message}</div>`;
    }
}

// 添加新模式
async function addPattern() {
    const pattern = document.getElementById('pattern').value.trim();
    const replacement = document.getElementById('replacement').value.trim();
    const description = document.getElementById('description').value.trim();
    const messageEl = document.getElementById('patterns-message');

    if (!pattern) {
        messageEl.textContent = '请输入模式';
        messageEl.className = 'patterns-message error';
        messageEl.style.display = 'block';
        return;
    }

    if (!replacement) {
        messageEl.textContent = '请输入替换名称';
        messageEl.className = 'patterns-message error';
        messageEl.style.display = 'block';
        return;
    }

    try {
        const response = await fetch('/plugin/app-chart/patterns', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pattern,
                replacement,
                description
            })
        });

        const data = await response.json();

        if (data.success) {
            messageEl.textContent = '模式添加成功';
            messageEl.className = 'patterns-message success';
            messageEl.style.display = 'block';

            // 清空表单
            document.getElementById('pattern').value = '';
            document.getElementById('replacement').value = '';
            document.getElementById('description').value = '';

            // 重新加载模式列表
            loadPatterns();
        } else {
            messageEl.textContent = '添加模式失败: ' + data.message;
            messageEl.className = 'patterns-message error';
            messageEl.style.display = 'block';
        }

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        messageEl.textContent = '添加模式失败: ' + error.message;
        messageEl.className = 'patterns-message error';
        messageEl.style.display = 'block';
    }
}

// 删除模式
async function deletePattern(id) {
    if (!confirm('确定要删除这个模式吗？')) {
        return;
    }

    const messageEl = document.getElementById('patterns-message');
    if (!messageEl) {
        console.error('Error: patterns-message element not found');
        return;
    }

    try {
        const response = await fetch(`/plugin/app-chart/patterns/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            messageEl.textContent = '模式删除成功';
            messageEl.className = 'patterns-message success';
            messageEl.style.display = 'block';

            // 重新加载模式列表
            loadPatterns();
        } else {
            messageEl.textContent = '删除模式失败: ' + data.message;
            messageEl.className = 'patterns-message error';
            messageEl.style.display = 'block';
        }

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        console.error('Error deleting pattern:', error);
        messageEl.textContent = '删除模式失败: ' + error.message;
        messageEl.className = 'patterns-message error';
        messageEl.style.display = 'block';
    }
}

// 删除所有模式
async function deleteAllPatterns() {
    if (!confirm('确定要删除所有模式吗？此操作不可恢复！')) {
        return;
    }

    const messageEl = document.getElementById('patterns-message');
    if (!messageEl) {
        console.error('Error: patterns-message element not found');
        return;
    }

    try {
        const response = await fetch('/plugin/app-chart/patterns/list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '获取模式列表失败');
        }

        if (!data.patterns || data.patterns.length === 0) {
            messageEl.textContent = '没有模式可删除';
            messageEl.className = 'patterns-message info';
            messageEl.style.display = 'block';
            return;
        }

        // 显示删除进度
        messageEl.textContent = '正在删除模式...';
        messageEl.className = 'patterns-message info';
        messageEl.style.display = 'block';

        // 逐个删除模式
        let successCount = 0;
        let failCount = 0;

        for (const pattern of data.patterns) {
            try {
                const deleteResponse = await fetch(`/plugin/app-chart/patterns/${pattern.id}`, {
                    method: 'DELETE'
                });

                if (!deleteResponse.ok) {
                    failCount++;
                    continue;
                }

                const deleteData = await deleteResponse.json();

                if (deleteData.success) {
                    successCount++;
                } else {
                    failCount++;
                }
            } catch (error) {
                console.error('Error deleting pattern:', error);
                failCount++;
            }
        }

        // 显示结果
        if (failCount === 0) {
            messageEl.textContent = `成功删除了 ${successCount} 个模式`;
            messageEl.className = 'patterns-message success';
        } else {
            messageEl.textContent = `删除了 ${successCount} 个模式，${failCount} 个模式删除失败`;
            messageEl.className = 'patterns-message warning';
        }

        // 重新加载模式列表
        loadPatterns();

        // 3秒后隐藏消息
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    } catch (error) {
        console.error('Error deleting all patterns:', error);
        messageEl.textContent = '删除所有模式失败: ' + error.message;
        messageEl.className = 'patterns-message error';
        messageEl.style.display = 'block';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 确保所有元素都存在
    const addPatternBtn = document.getElementById('add-pattern');
    const deleteAllPatternsBtn = document.getElementById('delete-all-patterns');

    // 加载初始数据
    loadPatterns();

    // 绑定事件（确保元素存在）
    if (addPatternBtn) {
        addPatternBtn.addEventListener('click', addPattern);
    }

    if (deleteAllPatternsBtn) {
        deleteAllPatternsBtn.addEventListener('click', deleteAllPatterns);
    }
});
