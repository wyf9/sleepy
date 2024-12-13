function update() {
    fetch('http://localhost:9010/query') // 请替换为实际的API地址
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const statusElement = document.getElementById('status');
                statusElement.textContent = data.info.name;
                document.getElementById('additional-info').textContent = data.info.desc;
                statusElement.classList.add(data.info.color);
            }
        })
        .catch(error => console.error('Error:', error));
    }

update(); // 首次获取数据

// 每5秒更新一次数据
setInterval(update, 5000);