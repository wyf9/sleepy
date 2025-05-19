# coding: utf-8

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import request
from plugin import route, on_event, admin_card
import _utils

# 数据库连接
_db_path = None
_db_lock = None

def init_plugin(config):
    """
    插件初始化函数

    :param config: 插件配置对象
    """
    global _db_path, _db_lock
    import threading

    # 获取插件配置
    db_path = config.getconf('db_path')

    # 确保数据库路径是绝对路径
    _db_path = _utils.get_path(db_path)

    # 初始化线程锁
    _db_lock = threading.Lock()

    # 初始化数据库
    try:
        _init_database()
        config.u.info(f'[app-chart] 插件初始化成功，数据库路径: {_db_path}')

        # 在服务器启动时输出模式列表
        try:
            conn = _get_db()
            cursor = conn.cursor()

            try:
                # 获取所有模式
                cursor.execute('SELECT id, pattern, replacement, description, enabled FROM app_name_patterns ORDER BY id')
                patterns = [dict(row) for row in cursor.fetchall()]

                # 输出模式列表
                config.u.debug("===== 应用名称模式列表 =====")
                if patterns:
                    for pattern in patterns:
                        config.u.debug(f"ID: {pattern['id']}, 模式: {pattern['pattern']}, 替换为: {pattern['replacement']}, 描述: {pattern.get('description', '')}")
                else:
                    config.u.debug("暂无模式")
                config.u.debug("========================================")
            finally:
                conn.close()
        except Exception as e:
            config.u.error(f"[app-chart] 获取模式列表失败: {str(e)}")

        return True
    except Exception as e:
        config.u.error(f'[app-chart] 插件初始化失败: {str(e)}')
        return False

def _get_db():
    """获取数据库连接"""
    global _db_path

    # 每次请求创建新的连接，确保线程安全
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问

    return conn

def _init_database():
    """初始化数据库表结构"""
    conn = _get_db()
    cursor = conn.cursor()

    try:
        # 创建应用使用记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            device_name TEXT NOT NULL,
            app_name TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration INTEGER DEFAULT 0
        )
        ''')

        # 创建每日统计表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            app_name TEXT NOT NULL,
            total_duration INTEGER DEFAULT 0,
            UNIQUE(date, app_name)
        )
        ''')

        # 创建应用名称模式表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_name_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL UNIQUE,
            replacement TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            description TEXT
        )
        ''')

        conn.commit()
    finally:
        conn.close()

def _record_app_usage(device_id, device_name, app_name, start_time=None, end_time=None, duration=0):
    """
    记录应用使用情况

    :param device_id: 设备ID
    :param device_name: 设备名称
    :param app_name: 应用名称
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param duration: 使用时长（秒）
    """
    conn = _get_db()
    cursor = conn.cursor()

    try:
        if start_time is None:
            start_time = datetime.now()

        # 插入记录
        cursor.execute('''
        INSERT INTO app_usage (device_id, device_name, app_name, start_time, end_time, duration)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_id, device_name, app_name, start_time, end_time, duration))

        conn.commit()
    finally:
        conn.close()

def _apply_app_name_patterns(app_name):
    """
    应用应用名称模式匹配

    :param app_name: 原始应用名称
    :return: 匹配后的应用名称
    """
    conn = _get_db()
    cursor = conn.cursor()

    try:
        # 获取应用名称模式
        cursor.execute('SELECT pattern, replacement FROM app_name_patterns')
        patterns = cursor.fetchall()

        # 应用模式匹配
        for pattern in patterns:
            pattern_str = pattern['pattern']
            replacement = pattern['replacement']

            # 处理前缀通配符 (*xxx)
            if pattern_str.startswith('*') and len(pattern_str) > 1:
                suffix = pattern_str[1:]
                if app_name.endswith(suffix):
                    return replacement

            # 处理后缀通配符 (xxx*)
            elif pattern_str.endswith('*') and len(pattern_str) > 1:
                prefix = pattern_str[:-1]
                if app_name.startswith(prefix):
                    return replacement

            # 处理包含通配符 (*xxx*)
            elif pattern_str.startswith('*') and pattern_str.endswith('*') and len(pattern_str) > 2:
                substring = pattern_str[1:-1]
                if substring in app_name:
                    return replacement

            # 精确匹配
            elif pattern_str == app_name:
                return replacement
    except:
        # 如果出错，返回原始应用名称
        pass
    finally:
        conn.close()

    return app_name

def _update_daily_stats(date, app_name, duration):
    """
    更新每日统计

    :param date: 日期（YYYY-MM-DD格式）
    :param app_name: 应用名称
    :param duration: 使用时长（秒）
    """
    conn = _get_db()
    cursor = conn.cursor()

    try:
        # 应用名称模式匹配
        mapped_app_name = _apply_app_name_patterns(app_name)

        # 尝试更新现有记录
        cursor.execute('''
        INSERT INTO daily_stats (date, app_name, total_duration)
        VALUES (?, ?, ?)
        ON CONFLICT(date, app_name) DO UPDATE SET
        total_duration = total_duration + ?
        ''', (date, mapped_app_name, duration, duration))

        conn.commit()
    finally:
        conn.close()

def _get_app_stats(days=7, limit=10):
    """
    获取应用使用统计

    :param days: 统计天数
    :param limit: 返回的应用数量限制
    :return: 统计数据
    """
    conn = _get_db()
    cursor = conn.cursor()

    try:
        # 计算起始日期
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)

        # 生成日期列表
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        # 获取总使用时间最多的应用
        cursor.execute('''
        SELECT app_name, SUM(total_duration) as total
        FROM daily_stats
        WHERE date >= ?
        GROUP BY app_name
        ORDER BY total DESC
        LIMIT ?
        ''', (start_date.strftime('%Y-%m-%d'), limit))

        top_apps = [dict(row) for row in cursor.fetchall()]

        # 获取每个应用每天的使用时间
        app_data = {}
        for app in top_apps:
            app_name = app['app_name']
            app_data[app_name] = {date: 0 for date in date_list}

            cursor.execute('''
            SELECT date, total_duration
            FROM daily_stats
            WHERE app_name = ? AND date >= ?
            ''', (app_name, start_date.strftime('%Y-%m-%d')))

            for row in cursor.fetchall():
                if row['date'] in app_data[app_name]:
                    app_data[app_name][row['date']] = row['total_duration']

        return {
            'dates': date_list,
            'apps': [app['app_name'] for app in top_apps],
            'data': app_data
        }
    finally:
        conn.close()

# 路由处理函数
@route('/stats')
def get_stats():
    """获取应用使用统计数据"""
    try:
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 10))

        stats = _get_app_stats(days, limit)
        return {
            'success': True,
            'stats': stats
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@route('/summary')
def get_summary():
    """获取应用使用总结"""
    try:
        # 获取所有应用的总使用时间
        conn = _get_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT app_name, SUM(total_duration) as total
            FROM daily_stats
            GROUP BY app_name
            ORDER BY total DESC
            ''')

            apps = [dict(row) for row in cursor.fetchall()]

            # 如果没有数据，返回空结果
            if not apps:
                return {
                    'success': True,
                    'apps': [],
                    'total_time': 0
                }

            # 获取总使用时间
            total_time = sum(app.get('total', 0) for app in apps)

            # 计算百分比
            for app in apps:
                app['percentage'] = (app.get('total', 0) / total_time) * 100 if total_time > 0 else 0

            return {
                'success': True,
                'apps': apps,
                'total_time': total_time
            }
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

# 存储上次设备状态
_last_device_status = {}

# 事件处理函数
@on_event('device_updated')
def on_device_updated(device_id, device_info):
    """
    设备更新事件处理

    :param device_id: 设备ID
    :param device_info: 设备信息
    """
    global _last_device_status

    try:
        current_time = datetime.now()
        device_name = device_info.get('show_name', 'Unknown')
        app_name = device_info.get('app_name', 'Unknown')
        is_using = device_info.get('using', False)

        # 检查设备之前的状态
        if device_id in _last_device_status:
            last_status = _last_device_status[device_id]
            last_time = last_status.get('time')
            last_app = last_status.get('app_name')
            last_using = last_status.get('using', False)

            # 如果之前设备正在使用，计算使用时长并记录
            if last_using and last_time and last_app:
                # 计算时间差（秒）
                time_diff = (current_time - last_time).total_seconds()

                # 如果应用变更或状态变更为未使用，记录上一个应用的使用时间
                if not is_using or last_app != app_name:
                    _record_app_usage(
                        device_id=device_id,
                        device_name=device_name,
                        app_name=last_app,
                        start_time=last_time,
                        end_time=current_time,
                        duration=time_diff
                    )

                    # 更新每日统计
                    today = last_time.strftime('%Y-%m-%d')
                    _update_daily_stats(today, last_app, time_diff)
                # 如果应用没变但仍在使用，也更新统计（每次更新增加时间差）
                elif is_using and last_app == app_name:
                    # 更新每日统计
                    today = last_time.strftime('%Y-%m-%d')
                    _update_daily_stats(today, app_name, time_diff)

        # 更新设备状态
        _last_device_status[device_id] = {
            'time': current_time,
            'app_name': app_name,
            'using': is_using
        }

        return True
    except Exception as e:
        print(f"Error in device_updated event: {e}")
        return False

@on_event('app_started')
def on_app_started(_):
    """应用启动事件处理"""
    # 初始化设备状态
    global _last_device_status
    _last_device_status = {}
    return True

# 管理后台卡片
@admin_card("应用使用时间统计", order=30)
def app_chart_settings_card(config):
    """
    应用使用时间统计配置卡片

    :param config: 插件配置对象
    :return: 卡片内容
    """
    # 获取当前设置
    db_path = config.getconf('db_path')
    max_apps = config.getconf('max_apps')
    default_days = config.getconf('default_days')
    chart_height = config.getconf('chart_height')
    colors = config.getconf('colors')

    # 颜色列表转为字符串
    colors_str = '\n'.join(colors) if colors else ''

    # 构建卡片内容
    content = """
    <div class="app-chart-settings">
        <div class="form-group">
            <label for="db_path">数据库路径:</label>
            <input type="text" id="db_path" value="{{ db_path }}" />
            <small>数据库文件的路径，相对于应用根目录</small>
        </div>
        <div class="form-group">
            <label for="max_apps">最大应用数量:</label>
            <input type="number" id="max_apps" value="{{ max_apps }}" min="1" max="50" />
            <small>图表中显示的最大应用数量</small>
        </div>
        <div class="form-group">
            <label for="default_days">默认显示天数:</label>
            <select id="default_days">
                <option value="7" {% if default_days == 7 %}selected{% endif %}>7天</option>
                <option value="14" {% if default_days == 14 %}selected{% endif %}>14天</option>
                <option value="30" {% if default_days == 30 %}selected{% endif %}>30天</option>
            </select>
            <small>默认显示的时间范围</small>
        </div>
        <div class="form-group">
            <label for="chart_height">图表高度:</label>
            <input type="number" id="chart_height" value="{{ chart_height }}" min="100" max="800" step="10" />
            <small>图表的高度（像素）</small>
        </div>
        <div class="form-group">
            <label for="colors">图表颜色:</label>
            <textarea id="colors" rows="5">{{ colors_str }}</textarea>
            <small>每行一个颜色代码，例如 #4e79a7</small>
        </div>
        <div class="form-actions">
            <button id="save-settings" class="btn btn-primary">保存设置</button>
            <button id="reset-settings" class="btn btn-secondary">重置</button>
        </div>
        <div id="settings-message" class="settings-message" style="display: none;"></div>
    </div>

    <style>
    .app-chart-settings {
        max-width: 600px;
    }
    .app-chart-settings small {
        display: block;
        color: #666;
        margin-top: 2px;
        font-size: 12px;
    }
    .settings-message {
        margin-top: 15px;
        padding: 10px;
        border-radius: 4px;
    }
    .settings-message.success {
        background-color: rgba(46, 160, 67, 0.1);
        border: 1px solid rgba(46, 160, 67, 0.2);
        color: #2ea043;
    }
    .settings-message.error {
        background-color: rgba(248, 81, 73, 0.1);
        border: 1px solid rgba(248, 81, 73, 0.2);
        color: #f85149;
    }
    </style>

    <script>
    // 保存设置
    document.getElementById('save-settings').addEventListener('click', async function() {
        const db_path = document.getElementById('db_path').value;
        const max_apps = parseInt(document.getElementById('max_apps').value);
        const default_days = parseInt(document.getElementById('default_days').value);
        const chart_height = parseInt(document.getElementById('chart_height').value);
        const colors_str = document.getElementById('colors').value;

        // 解析颜色列表
        const colors = colors_str.split('\\n')
            .map(color => color.trim())
            .filter(color => color.length > 0);

        try {
            const response = await fetch('/plugin/app-chart/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    db_path,
                    max_apps,
                    default_days,
                    chart_height,
                    colors
                })
            });

            const data = await response.json();
            const messageEl = document.getElementById('settings-message');

            if (data.success) {
                messageEl.textContent = '设置已保存，重启服务后生效';
                messageEl.className = 'settings-message success';
                messageEl.style.display = 'block';
            } else {
                messageEl.textContent = '保存失败: ' + data.message;
                messageEl.className = 'settings-message error';
                messageEl.style.display = 'block';
            }

            // 3秒后隐藏消息
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 3000);
        } catch (error) {
            const messageEl = document.getElementById('settings-message');
            messageEl.textContent = '保存失败: ' + error.message;
            messageEl.className = 'settings-message error';
            messageEl.style.display = 'block';
        }
    });

    // 重置设置
    document.getElementById('reset-settings').addEventListener('click', function() {
        document.getElementById('db_path').value = '{{ db_path }}';
        document.getElementById('max_apps').value = '{{ max_apps }}';
        document.getElementById('default_days').value = '{{ default_days }}';
        document.getElementById('chart_height').value = '{{ chart_height }}';
        document.getElementById('colors').value = '{{ colors_str }}';
    });
    </script>
    """

    # 渲染模板变量
    content = content.replace('{{ db_path }}', db_path)
    content = content.replace('{{ max_apps }}', str(max_apps))
    content = content.replace('{{ default_days }}', str(default_days))
    content = content.replace('{{ chart_height }}', str(chart_height))
    content = content.replace('{{ colors_str }}', colors_str)

    # 处理条件语句
    if default_days == 7:
        content = content.replace('{% if default_days == 7 %}selected{% endif %}', 'selected')
    else:
        content = content.replace('{% if default_days == 7 %}selected{% endif %}', '')

    if default_days == 14:
        content = content.replace('{% if default_days == 14 %}selected{% endif %}', 'selected')
    else:
        content = content.replace('{% if default_days == 14 %}selected{% endif %}', '')

    if default_days == 30:
        content = content.replace('{% if default_days == 30 %}selected{% endif %}', 'selected')
    else:
        content = content.replace('{% if default_days == 30 %}selected{% endif %}', '')

    return content

@admin_card("应用使用数据管理", order=31)
def app_chart_data_card(_):
    """
    应用使用数据管理卡片

    :param config: 插件配置对象
    :return: 卡片内容
    """
    # 构建卡片内容
    content = """
    <div class="app-chart-data-management">
        <div class="data-stats">
            <div class="loading">加载数据统计中...</div>
        </div>

        <div class="data-actions">
            <button id="refresh-stats" class="btn btn-secondary">刷新统计</button>
            <button id="clear-data" class="btn btn-danger">清除所有数据</button>
            <button id="export-data" class="btn btn-primary">导出数据</button>
            <button id="download-db" class="btn btn-primary">下载数据库</button>
        </div>

        <div id="data-message" class="data-message" style="display: none;"></div>
    </div>

    <style>
    .app-chart-data-management {
        max-width: 600px;
    }
    .data-stats {
        margin-bottom: 20px;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
        padding: 15px;
    }
    .data-actions {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    .data-message {
        margin-top: 15px;
        padding: 10px;
        border-radius: 4px;
    }
    .data-message.success {
        background-color: rgba(46, 160, 67, 0.1);
        border: 1px solid rgba(46, 160, 67, 0.2);
        color: #2ea043;
    }
    .data-message.error {
        background-color: rgba(248, 81, 73, 0.1);
        border: 1px solid rgba(248, 81, 73, 0.2);
        color: #f85149;
    }
    .data-stat-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    }
    .data-stat-item:last-child {
        border-bottom: none;
    }
    .data-stat-label {
        font-weight: bold;
    }
    </style>

    <script>
    // 加载数据统计
    async function loadDataStats() {
        const statsEl = document.querySelector('.data-stats');
        statsEl.innerHTML = '<div class="loading">加载数据统计中...</div>';

        try {
            const response = await fetch('/plugin/app-chart/data-stats');
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || '加载数据失败');
            }

            statsEl.innerHTML = `
                <h4>数据统计</h4>
                <div class="data-stat-item">
                    <span class="data-stat-label">应用使用记录数:</span>
                    <span>${data.stats.usage_count}</span>
                </div>
                <div class="data-stat-item">
                    <span class="data-stat-label">每日统计记录数:</span>
                    <span>${data.stats.daily_count}</span>
                </div>
                <div class="data-stat-item">
                    <span class="data-stat-label">追踪的应用数:</span>
                    <span>${data.stats.app_count}</span>
                </div>
                <div class="data-stat-item">
                    <span class="data-stat-label">数据库大小:</span>
                    <span>${data.stats.db_size}</span>
                </div>
                <div class="data-stat-item">
                    <span class="data-stat-label">最早记录日期:</span>
                    <span>${data.stats.first_date || '无数据'}</span>
                </div>
                <div class="data-stat-item">
                    <span class="data-stat-label">最新记录日期:</span>
                    <span>${data.stats.last_date || '无数据'}</span>
                </div>
            `;
        } catch (error) {
            console.error('Error loading data stats:', error);
            statsEl.innerHTML = `<div class="error-message">加载数据统计失败: ${error.message}</div>`;
        }
    }

    // 清除所有数据
    async function clearAllData() {
        if (!confirm('确定要清除所有应用使用时间数据吗？此操作不可恢复！')) {
            return;
        }

        const messageEl = document.getElementById('data-message');

        try {
            const response = await fetch('/plugin/app-chart/clear-data', {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                messageEl.textContent = '所有数据已清除';
                messageEl.className = 'data-message success';
                messageEl.style.display = 'block';

                // 重新加载统计
                loadDataStats();
            } else {
                messageEl.textContent = '清除数据失败: ' + data.message;
                messageEl.className = 'data-message error';
                messageEl.style.display = 'block';
            }

            // 3秒后隐藏消息
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 3000);
        } catch (error) {
            messageEl.textContent = '清除数据失败: ' + error.message;
            messageEl.className = 'data-message error';
            messageEl.style.display = 'block';
        }
    }

    // 导出数据
    async function exportData() {
        try {
            const response = await fetch('/plugin/app-chart/export-data');
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || '导出数据失败');
            }

            // 创建下载链接
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data.data, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "app_usage_data.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();

            const messageEl = document.getElementById('data-message');
            messageEl.textContent = '数据导出成功';
            messageEl.className = 'data-message success';
            messageEl.style.display = 'block';

            // 3秒后隐藏消息
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 3000);
        } catch (error) {
            const messageEl = document.getElementById('data-message');
            messageEl.textContent = '导出数据失败: ' + error.message;
            messageEl.className = 'data-message error';
            messageEl.style.display = 'block';
        }
    }

    // 下载数据库
    async function downloadDatabase() {
        try {
            const messageEl = document.getElementById('data-message');
            messageEl.textContent = '准备下载数据库...';
            messageEl.className = 'data-message success';
            messageEl.style.display = 'block';

            // 创建下载链接
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", '/plugin/app-chart/download-db');
            downloadAnchorNode.setAttribute("download", "app_chart.db");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();

            messageEl.textContent = '数据库下载已开始';

            // 3秒后隐藏消息
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 3000);
        } catch (error) {
            const messageEl = document.getElementById('data-message');
            messageEl.textContent = '下载数据库失败: ' + error.message;
            messageEl.className = 'data-message error';
            messageEl.style.display = 'block';
        }
    }

    // 初始化
    document.addEventListener('DOMContentLoaded', function() {
        // 加载初始数据
        loadDataStats();

        // 绑定事件
        document.getElementById('refresh-stats').addEventListener('click', loadDataStats);
        document.getElementById('clear-data').addEventListener('click', clearAllData);
        document.getElementById('export-data').addEventListener('click', exportData);
        document.getElementById('download-db').addEventListener('click', downloadDatabase);
    });
    </script>
    """

    return content

@route('/settings', methods=['POST'])
def save_settings():
    """
    保存插件设置

    :return: 操作结果
    """
    try:
        # 获取请求数据
        data = request.get_json()

        if not data:
            return {'success': False, 'message': '无效的请求数据'}

        # 获取设置值
        db_path = data.get('db_path', 'app_chart.db')
        max_apps = int(data.get('max_apps', 10))
        default_days = int(data.get('default_days', 7))
        chart_height = int(data.get('chart_height', 300))
        colors = data.get('colors', [])

        # 验证设置值
        if not db_path:
            return {'success': False, 'message': '数据库路径不能为空'}

        if max_apps < 1 or max_apps > 50:
            return {'success': False, 'message': '最大应用数量必须在1-50之间'}

        if default_days not in [7, 14, 30]:
            return {'success': False, 'message': '默认显示天数必须是7、14或30'}

        if chart_height < 100 or chart_height > 800:
            return {'success': False, 'message': '图表高度必须在100-800之间'}

        if not colors or len(colors) < 1:
            return {'success': False, 'message': '至少需要一种颜色'}

        # 更新配置文件
        config_path = _utils.get_path('config/config.yaml')

        try:
            import yaml

            # 读取当前配置
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 确保插件配置存在
            if 'plugin' not in config:
                config['plugin'] = {}

            if 'app-chart' not in config['plugin']:
                config['plugin']['app-chart'] = {}

            # 更新设置
            config['plugin']['app-chart']['db_path'] = db_path
            config['plugin']['app-chart']['max_apps'] = max_apps
            config['plugin']['app-chart']['default_days'] = default_days
            config['plugin']['app-chart']['chart_height'] = chart_height
            config['plugin']['app-chart']['colors'] = colors

            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': f'保存配置失败: {str(e)}'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@route('/data-stats')
def get_data_stats():
    """
    获取数据库统计信息

    :return: 统计信息
    """
    try:
        conn = _get_db()
        cursor = conn.cursor()

        try:
            # 获取应用使用记录数
            cursor.execute('SELECT COUNT(*) FROM app_usage')
            usage_count = cursor.fetchone()[0]

            # 获取每日统计记录数
            cursor.execute('SELECT COUNT(*) FROM daily_stats')
            daily_count = cursor.fetchone()[0]

            # 获取应用数量
            cursor.execute('SELECT COUNT(DISTINCT app_name) FROM daily_stats')
            app_count = cursor.fetchone()[0]

            # 获取最早和最新记录日期
            cursor.execute('SELECT MIN(date), MAX(date) FROM daily_stats')
            date_row = cursor.fetchone()
            first_date = date_row[0] if date_row else None
            last_date = date_row[1] if date_row else None

            # 获取数据库文件大小
            db_size = "未知"
            try:
                import os
                if os.path.exists(_db_path):
                    size_bytes = os.path.getsize(_db_path)
                    if size_bytes < 1024:
                        db_size = f"{size_bytes} 字节"
                    elif size_bytes < 1024 * 1024:
                        db_size = f"{size_bytes / 1024:.2f} KB"
                    else:
                        db_size = f"{size_bytes / (1024 * 1024):.2f} MB"
            except:
                pass

            return {
                'success': True,
                'stats': {
                    'usage_count': usage_count,
                    'daily_count': daily_count,
                    'app_count': app_count,
                    'first_date': first_date,
                    'last_date': last_date,
                    'db_size': db_size
                }
            }
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@route('/clear-data', methods=['POST'])
def clear_data():
    """
    清除所有数据

    :return: 操作结果
    """
    try:
        conn = _get_db()
        cursor = conn.cursor()

        try:
            # 清空表
            cursor.execute('DELETE FROM app_usage')
            cursor.execute('DELETE FROM daily_stats')

            # 重置自增ID
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="app_usage" OR name="daily_stats"')

            conn.commit()

            return {
                'success': True,
                'message': '所有数据已清除'
            }
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@admin_card("应用名称模式", order=32)
def app_name_patterns_card(_):
    """
    应用名称模式卡片

    :param _: 插件配置对象（未使用）
    :return: 卡片内容
    """
    # 直接返回内联的 HTML、CSS 和 JavaScript，不需要导入模块
    return """
    <div class="app-name-patterns">
        <div class="patterns-description">
            <h4>应用名称模式</h4>
            <p>您可以创建应用名称模式来合并相似的应用名称。例如，将所有包含"Chrome"的应用名称显示为"Chrome浏览器"。</p>
            <p>支持的模式类型：</p>
            <ul>
                <li><code>*Chrome</code> - 匹配所有以"Chrome"结尾的名称</li>
                <li><code>Chrome*</code> - 匹配所有以"Chrome"开头的名称</li>
                <li><code>*Chrome*</code> - 匹配所有包含"Chrome"的名称</li>
                <li><code>Exact Name</code> - 精确匹配 "Exact Name"</li>
            </ul>
        </div>

        <div class="patterns-list">
            <div class="patterns-header">
                <h4>当前模式</h4>
                <button id="delete-all-patterns" class="btn btn-danger btn-sm" style="display: none;">
                    <i class="fas fa-trash-alt"></i> 删除所有模式
                </button>
            </div>
            <div id="patterns-container">
                <div class="loading">加载中...</div>
            </div>
        </div>

        <div class="patterns-form">
            <h4>添加新模式</h4>
            <div class="form-group">
                <label for="pattern">模式:</label>
                <input type="text" id="pattern" placeholder="例如: *Discord" />
                <small>使用 * 作为通配符</small>
            </div>
            <div class="form-group">
                <label for="replacement">替换为:</label>
                <input type="text" id="replacement" placeholder="例如: Discord" />
                <small>所有匹配的应用将显示为这个名称</small>
            </div>
            <div class="form-group">
                <label for="description">描述:</label>
                <input type="text" id="description" placeholder="可选描述" />
                <small>帮助您记住这个模式的用途</small>
            </div>
            <div class="form-actions">
                <button id="add-pattern" class="btn btn-primary">添加模式</button>
            </div>
        </div>

        <div id="patterns-message" class="patterns-message" style="display: none;"></div>
    </div>

    <style>
    .app-name-patterns {
        max-width: 600px;
    }
    .patterns-description {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .patterns-description code {
        background-color: rgba(0, 0, 0, 0.05);
        padding: 2px 4px;
        border-radius: 3px;
        font-family: monospace;
    }
    .patterns-list {
        margin-bottom: 20px;
    }
    .patterns-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .pattern-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        margin-bottom: 8px;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 4px;
    }
    .pattern-info {
        flex-grow: 1;
    }
    .pattern-actions {
        display: flex;
        gap: 5px;
    }
    .pattern-pattern {
        font-weight: bold;
        font-family: monospace;
    }
    .pattern-replacement {
        color: #2ea043;
        font-weight: bold;
    }
    .pattern-description {
        color: #666;
        font-size: 0.9em;
        margin-top: 3px;
    }
    .patterns-form {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .patterns-message {
        margin-top: 15px;
        padding: 10px;
        border-radius: 4px;
    }
    .patterns-message.success {
        background-color: rgba(46, 160, 67, 0.1);
        border: 1px solid rgba(46, 160, 67, 0.2);
        color: #2ea043;
    }
    .patterns-message.error {
        background-color: rgba(248, 81, 73, 0.1);
        border: 1px solid rgba(248, 81, 73, 0.2);
        color: #f85149;
    }
    .patterns-message.info {
        background-color: rgba(3, 102, 214, 0.1);
        border: 1px solid rgba(3, 102, 214, 0.2);
        color: #0366d6;
    }
    .patterns-message.warning {
        background-color: rgba(249, 197, 19, 0.1);
        border: 1px solid rgba(249, 197, 19, 0.2);
        color: #e36209;
    }
    .loading {
        text-align: center;
        padding: 20px;
        color: #666;
    }
    .empty-message {
        color: #888;
        text-align: center;
        padding: 20px;
    }
    .error-message {
        color: #e15759;
        text-align: center;
        padding: 20px;
    }
    </style>

    <script>
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
    </script>
    """

@route('/export-data')
def export_data():
    """
    导出数据

    :return: 导出的数据
    """
    try:
        conn = _get_db()
        cursor = conn.cursor()

        try:
            # 获取每日统计数据
            cursor.execute('SELECT * FROM daily_stats ORDER BY date')
            daily_stats = [dict(row) for row in cursor.fetchall()]

            # 获取应用使用记录
            cursor.execute('SELECT * FROM app_usage ORDER BY start_time')
            app_usage = [dict(row) for row in cursor.fetchall()]

            # 转换日期时间格式
            for record in app_usage:
                if 'start_time' in record and record['start_time']:
                    record['start_time'] = str(record['start_time'])
                if 'end_time' in record and record['end_time']:
                    record['end_time'] = str(record['end_time'])

            return {
                'success': True,
                'data': {
                    'daily_stats': daily_stats,
                    'app_usage': app_usage,
                    'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@route('/patterns/list', methods=['GET'])
def get_patterns():
    """
    获取应用名称模式列表

    :return: 模式列表
    """
    try:
        conn = _get_db()
        cursor = conn.cursor()

        try:
            # 获取所有模式
            cursor.execute('SELECT id, pattern, replacement, description, enabled FROM app_name_patterns ORDER BY id')
            patterns = [dict(row) for row in cursor.fetchall()]

            # 在后台输出模式列表
            print("\n===== 应用名称模式列表 =====")
            if patterns:
                for pattern in patterns:
                    print(f"ID: {pattern['id']}, 模式: {pattern['pattern']}, 替换为: {pattern['replacement']}, 描述: {pattern.get('description', '')}")
            else:
                print("暂无模式")
            print("===========================\n")

            return {
                'success': True,
                'patterns': patterns
            }
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@route('/patterns', methods=['POST'])
def add_pattern():
    """
    添加应用名称模式

    :return: 操作结果
    """
    try:
        # 获取请求数据
        data = request.get_json()

        if not data:
            return {'success': False, 'message': '无效的请求数据'}

        # 获取模式值
        pattern = data.get('pattern', '').strip()
        replacement = data.get('replacement', '').strip()
        description = data.get('description', '').strip()

        # 验证模式值
        if not pattern:
            return {'success': False, 'message': '模式不能为空'}

        if not replacement:
            return {'success': False, 'message': '替换名称不能为空'}

        # 添加模式
        conn = _get_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO app_name_patterns (pattern, replacement, description, enabled)
            VALUES (?, ?, ?, 1)
            ''', (pattern, replacement, description))

            conn.commit()

            # 在后台输出添加的模式
            new_id = cursor.lastrowid
            print("\n===== 添加新模式 =====")
            print(f"ID: {new_id}, 模式: {pattern}, 替换为: {replacement}, 描述: {description}")
            print("======================\n")

            return {'success': True, 'id': new_id}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': '模式已存在'}
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@route('/download-db')
def download_database():
    """
    下载数据库文件

    :return: 数据库文件
    """
    try:
        from flask import send_file
        import os
        import shutil
        import tempfile

        # 使用线程锁确保在复制过程中没有其他线程访问数据库
        with _db_lock:
            # 检查文件是否存在
            if not os.path.exists(_db_path):
                return {
                    'success': False,
                    'message': '数据库文件不存在'
                }, 404

            # 创建临时文件
            temp_dir = tempfile.mkdtemp()
            temp_db_path = os.path.join(temp_dir, 'app_chart.db')

            # 复制数据库文件到临时位置
            shutil.copy2(_db_path, temp_db_path)

        # 发送临时文件
        return send_file(
            temp_db_path,
            as_attachment=True,
            download_name='app_chart.db',
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }, 500

@route('/patterns/<int:pattern_id>', methods=['DELETE'])
def delete_pattern(pattern_id):
    """
    删除应用名称模式

    :param pattern_id: 模式ID
    :return: 操作结果
    """
    try:
        conn = _get_db()
        cursor = conn.cursor()

        try:
            # 检查模式是否存在
            cursor.execute('SELECT id FROM app_name_patterns WHERE id = ?', (pattern_id,))
            pattern = cursor.fetchone()

            if not pattern:
                return {'success': False, 'message': '模式不存在'}

            # 获取模式信息（用于日志）
            cursor.execute('SELECT pattern, replacement FROM app_name_patterns WHERE id = ?', (pattern_id,))
            pattern_info = cursor.fetchone()

            # 删除模式
            cursor.execute('DELETE FROM app_name_patterns WHERE id = ?', (pattern_id,))
            conn.commit()

            # 在后台输出删除的模式
            print("\n===== 删除模式 =====")
            if pattern_info:
                print(f"ID: {pattern_id}, 模式: {pattern_info['pattern']}, 替换为: {pattern_info['replacement']}")
            else:
                print(f"ID: {pattern_id}")
            print("===================\n")

            return {'success': True}
        finally:
            conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
