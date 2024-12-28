// ==UserScript==
// @name         页面标题上报脚本
// @namespace    https://github.com/nuym
// @version      1.0
// @description  获取页面标题并上报到指定API（包括浏览器名称）
// @author       nuym
// @match        *://*/*
// @grant        GM_xmlhttpRequest
// @connect      在这里写入你的API_URL
// ==/UserScript==

(function () {
    'use strict';

    // 配置 API 参数

    // 请在@connect 这一行写入你的API_URL
    // 请在@connect 这一行写入你的API_URL
    // 请在@connect 这一行写入你的API_URL
    // 请在@connect 这一行写入你的API_URL
    // 请在@connect 这一行写入你的API_URL

    const API_URL = 'http://你的网站/device/set'; //你的API
    const SECRET = '你的secret'; // 你的 secret
    const ID = '114514';              // 你的设备 id
    const SHOW_NAME = '设备名称'; // 替换为你的设备名称

    // 获取浏览器名称
    function getBrowserName() {
        const userAgent = navigator.userAgent;

        if (userAgent.includes("Edg")) {
            return "Microsoft Edge";
        } else if (userAgent.includes("Chrome") && !userAgent.includes("Edg")) {
            return "Google Chrome";
        } else if (userAgent.includes("Firefox")) {
            return "Mozilla Firefox";
        } else if (userAgent.includes("Safari") && !userAgent.includes("Chrome")) {
            return "Apple Safari";
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

        // 使用 GM_xmlhttpRequest 发送请求
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
