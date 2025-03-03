const MLswitch = document.getElementById('moonlight');

MLswitch.onclick = function () {
    document.querySelectorAll('.light, .dark').forEach(el => {
        if (el.classList.contains('light')) {
            el.classList.replace('light', 'dark');
        } else {
            el.classList.replace('dark', 'light');
        }
    });
};

