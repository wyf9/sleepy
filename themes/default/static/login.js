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

// 登录函数
async function login() {
    const secret = document.getElementById('secret').value;
    if (!secret) {
        document.getElementById('error-message').style.display = 'block';
        document.getElementById('error-message').textContent = '请输入密钥';
        return;
    }

    // 将密钥存储在 localStorage 中作为备份
    localStorage.setItem('sleepy_secret', secret);

    // 获取当前保存的主题
    const savedTheme = localStorage.getItem('sleepy_theme');

    // 检查是否支持现代API登录方式
    const useModernAuth = document.body.hasAttribute('data-use-modern-auth');

    if (useModernAuth) {
        try {
            // 现代方式：使用fetch API发送登录请求
            const response = await fetch('/webui/auth', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ secret: secret })
            });

            if (response.ok) {
                // 登录成功，重定向到管理面板
                let redirectUrl = '/webui/panel';
                if (savedTheme) {
                    redirectUrl += '?theme=' + encodeURIComponent(savedTheme);
                }
                window.location.href = redirectUrl;
            } else {
                // 登录失败
                const data = await response.json();
                document.getElementById('error-message').style.display = 'block';
                document.getElementById('error-message').textContent = data.message || '密钥错误，请重试';
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            document.getElementById('error-message').style.display = 'block';
            document.getElementById('error-message').textContent = '登录请求失败，请检查网络连接';
        }
    } else {
        // 传统方式：直接通过URL参数传递密钥
        let redirectUrl = '/webui/panel?secret=' + encodeURIComponent(secret);
        if (savedTheme) {
            redirectUrl += '&theme=' + encodeURIComponent(savedTheme);
        }
        window.location.href = redirectUrl;
    }
}

// 初始化事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 按下回车键时触发登录按钮
    document.getElementById('secret').addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            login();
        }
    });

    // 如果存在登录按钮，添加点击事件
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', login);
    }
});
