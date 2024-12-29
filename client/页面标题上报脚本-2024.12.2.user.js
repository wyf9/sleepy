// ==UserScript==
// @name         页面标题上报脚本
// @namespace    sleepy
// @version      2024.12.2
// @description  获取页面标题并上报到指定 API (包括浏览器名称) / 请在安装脚本后手动编辑下面的配置
// @author       nuym
// @author       wyf9
// @match        *://*/*
// @grant        GM_xmlhttpRequest
// @connect      *
// @homepage     https://github.com/wyf9/sleepy
// @source       https://github.com/wyf9/sleepy/blob/main/client/%E9%A1%B5%E9%9D%A2%E6%A0%87%E9%A2%98%E4%B8%8A%E6%8A%A5%E8%84%9A%E6%9C%AC-2024.12.2.user.js
// ==/UserScript==

(function () {
    'use strict';

    // 参数配置开始
    const API_URL = 'http://example.com/device/set'; // 你的完整 API 地址，以 `/device/set` 结尾
    const SECRET = '绝对猜不出来的密码'; // 你的 secret
    const ID = '114514'; // 你的设备 id
    const SHOW_NAME = '设备名称'; // 替换为你的设备名称
    // 参数配置结束

    // 获取浏览器名称
    function getBrowserName() {
        const userAgent = navigator.userAgent;

        if (userAgent.includes("Edg")) {
            return "Edge";
        } else if (userAgent.includes("Chrome") && !userAgent.includes("Edg")) {
            return "Chrome";
        } else if (userAgent.includes("Firefox")) {
            return "Firefox";
        } else if (userAgent.includes("Safari") && !userAgent.includes("Chrome")) {
            return "Safari";
        } else if (userAgent.includes("Opera") || userAgent.includes("OPR")) {
            return "Opera";
        } else {
            return "Unknown Browser";
        }
    }

    // 发送请求函数
    function sendRequest() {
        const browserName = getBrowserName(); // 获取浏览器名称
        const appName = `${browserName} - ${document.title}`; // 拼接浏览器名称和页面标题

        // 构造 API URL
        const apiUrl = `${API_URL}?secret=${encodeURIComponent(SECRET)}&id=${encodeURIComponent(ID)}&show_name=${encodeURIComponent(SHOW_NAME)}&using=true&app_name=${encodeURIComponent(appName)}`;

        // 使用 GM_xmlhttpRequest 发送请求 (还是先用 get 吧)
        GM_xmlhttpRequest({
            method: 'GET',
            url: apiUrl,
            onload: (response) => {
                if (response.status === 200) {
                    console.log(`API 请求成功: ${apiUrl}`);
                } else {
                    console.error(`API 请求失败: ${response.status} ${response.statusText}`);
                }
            },
            onerror: (error) => {
                console.error(`API 请求出错: ${error}`);
            }
        });
    }

    // 页面加载完成时发送请求
    window.addEventListener('DOMContentLoaded', () => {
        sendRequest();
    });

    // 监听页面聚焦事件发送请求
    window.addEventListener('focus', () => {
        sendRequest();
    });
})();
