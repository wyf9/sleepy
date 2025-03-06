const MLswitch = document.getElementById('moonlight');

// 保存主题偏好
function saveThemePreference(isDark) {
    localStorage.setItem('themePref', isDark ? 'dark' : 'light');
}

// 获取主题偏好
function getThemePreference() {
    return localStorage.getItem('themePref') || 'auto';
}

// 应用主题
function applyTheme(theme) {
    document.querySelectorAll('.light, .dark').forEach(el => {
        if (theme === 'dark' && el.classList.contains('light')) {
            el.classList.replace('light', 'dark');
        } else if (theme === 'light' && el.classList.contains('dark')) {
            el.classList.replace('dark', 'light');
        }
    });
}

// 增加不透明度控制
function adjustOpacity(increase) {
    document.querySelectorAll('.card').forEach(card => {
        let opacity = parseFloat(getComputedStyle(card).opacity);
        opacity = increase ? Math.min(1, opacity + 0.1) : Math.max(0.3, opacity - 0.1);
        card.style.opacity = opacity;
        localStorage.setItem('cardOpacity', opacity);
    });
}

// 应用保存的不透明度
function applySavedOpacity() {
    const savedOpacity = localStorage.getItem('cardOpacity');
    if (savedOpacity) {
        document.querySelectorAll('.card').forEach(card => {
            card.style.opacity = savedOpacity;
        });
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 应用保存的主题
    const savedTheme = getThemePreference();
    if (savedTheme !== 'auto') {
        applyTheme(savedTheme);
    }

    // 应用保存的不透明度
    applySavedOpacity();

    // 添加控制面板
    const controlPanel = document.createElement('div');
    controlPanel.className = 'theme-controls';
    controlPanel.innerHTML = `
        <div class="opacity-controls">
            <button id="decrease-opacity">-</button>
            <span>不透明度</span>
            <button id="increase-opacity">+</button>
        </div>
    `;
    document.body.appendChild(controlPanel);

    // 添加事件监听
    document.getElementById('decrease-opacity').addEventListener('click', () => adjustOpacity(false));
    document.getElementById('increase-opacity').addEventListener('click', () => adjustOpacity(true));
});

// 原有的主题切换功能
MLswitch.onclick = function () {
    document.querySelectorAll('.light, .dark').forEach(el => {
        if (el.classList.contains('light')) {
            el.classList.replace('light', 'dark');
            saveThemePreference(true);
        } else {
            el.classList.replace('dark', 'light');
            saveThemePreference(false);
        }
    });
};

