// Simple theme - minimal JavaScript for device status updates

// 获取设备状态
async function getDeviceStatus() {
    try {
        const response = await fetch('/device');
        const data = await response.json();
        
        if (data.success) {
            updateDeviceStatus(data.data);
        }
    } catch (error) {
        console.error('获取设备状态失败:', error);
    }
}

// 更新设备状态显示
function updateDeviceStatus(devices) {
    const deviceStatusElement = document.getElementById('device-status');
    if (!deviceStatusElement) return;
    
    if (Object.keys(devices).length === 0) {
        deviceStatusElement.textContent = '[无设备数据]';
        return;
    }
    
    let deviceList = '';
    for (const [deviceId, device] of Object.entries(devices)) {
        deviceList += `${device.show_name}: ${device.using ? '使用中' : '未使用'}\n`;
    }
    
    deviceStatusElement.textContent = deviceList.trim();
}

// 页面加载完成后开始获取设备状态
document.addEventListener('DOMContentLoaded', function() {
    getDeviceStatus();
    
    // 定期更新设备状态
    setInterval(getDeviceStatus, 10000); // 每10秒更新一次
});
