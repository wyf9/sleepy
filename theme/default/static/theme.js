// 处理主题设置
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const urlTheme = urlParams.get('theme');
    const currentTheme = document.body.getAttribute('data-theme');

    // 如果 URL 中有主题参数，则将其保存到 localStorage
    if (urlTheme) {
        localStorage.setItem('sleepy_theme', urlTheme);
    } else {
        // 如果 URL 中没有主题参数，检查 localStorage
        const savedTheme = localStorage.getItem('sleepy_theme');

        // 如果保存的主题是 default-light，将其更改为 default
        if (savedTheme === 'default-light') {
            localStorage.setItem('sleepy_theme', 'default');
        }

        // 如果有保存的主题且与当前主题不同，则切换到保存的主题
        if (savedTheme && savedTheme !== currentTheme) {
            // 构建带有主题参数的 URL
            const url = new URL(window.location.href);
            url.searchParams.set('theme', savedTheme);
            window.location.href = url.toString();
        }
    }
});

// 切换主题
function switchTheme(theme) {
    // 保存主题选择到 localStorage
    localStorage.setItem('sleepy_theme', theme);

    // 保存当前的 URL 参数
    const urlParams = new URLSearchParams(window.location.search);
    // 设置新的主题
    urlParams.set('theme', theme);
    
    // 获取密钥（如果存在）
    const secret = localStorage.getItem('sleepy_secret');
    // 确保 secret 参数存在（如果在管理面板中）
    if (window.location.pathname.includes('/webui/') && !urlParams.has('secret') && secret) {
        urlParams.set('secret', secret);
    }
    
    // 重定向到新的 URL
    window.location.href = window.location.pathname + '?' + urlParams.toString();
}
