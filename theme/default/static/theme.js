// Cookie 操作辅助函数
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/; samesite=Lax";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// 处理主题设置
document.addEventListener('DOMContentLoaded', function() {
    // 自动清除 localStorage 中存储的 secret 和 theme
    if (localStorage.getItem('sleepy_secret')) {
        localStorage.removeItem('sleepy_secret');
        console.log('已清除 localStorage 中存储的 secret');
    }

    // 清除旧的 localStorage 主题设置
    if (localStorage.getItem('sleepy_theme')) {
        const oldTheme = localStorage.getItem('sleepy_theme');
        localStorage.removeItem('sleepy_theme');
        console.log('已清除 localStorage 中存储的主题设置');

        // 如果没有 cookie 主题设置，则将旧的主题设置迁移到 cookie
        if (!getCookie('sleepy-theme')) {
            setCookie('sleepy-theme', oldTheme, 30); // 保存 30 天
            console.log('已将主题设置从 localStorage 迁移到 cookie');
        }
    }

    const urlParams = new URLSearchParams(window.location.search);
    const urlTheme = urlParams.get('theme');
    const currentTheme = document.body.getAttribute('data-theme');

    // 如果 URL 中有主题参数，则将其保存到 cookie
    if (urlTheme) {
        setCookie('sleepy-theme', urlTheme, 30); // 保存 30 天
    } else {
        // 如果 URL 中没有主题参数，检查 cookie
        const savedTheme = getCookie('sleepy-theme');

        // 如果保存的主题是 default-light，将其更改为 default
        if (savedTheme === 'default-light') {
            setCookie('sleepy-theme', 'default', 30);
        }

        // 如果有保存的主题且与当前主题不同，则直接应用主题
        // 但是为了防止无限刷新循环，我们需要检查URL中是否已经有theme参数
        if (savedTheme && savedTheme !== currentTheme && !urlTheme) {
            // 使用URL参数切换主题，而不是直接刷新
            const currentUrl = new URL(window.location.href);

            // 清除所有现有的查询参数
            Array.from(currentUrl.searchParams.keys()).forEach(key => {
                currentUrl.searchParams.delete(key);
            });

            // 添加主题参数
            currentUrl.searchParams.set('theme', savedTheme);

            // 重定向到新URL
            window.location.href = currentUrl.toString();
        }
    }
});

// 切换主题
function switchTheme(theme) {
    // 保存主题选择到 cookie
    setCookie('sleepy-theme', theme, 30); // 保存 30 天

    // 使用URL参数切换主题，而不是直接刷新
    const currentUrl = new URL(window.location.href);

    // 清除所有现有的查询参数
    Array.from(currentUrl.searchParams.keys()).forEach(key => {
        currentUrl.searchParams.delete(key);
    });

    // 添加主题参数
    currentUrl.searchParams.set('theme', theme);

    // 重定向到新URL
    window.location.href = currentUrl.toString();
}
