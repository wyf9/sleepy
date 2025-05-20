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
    import os

    # 获取插件配置
    db_path = config.getconf('db_path')

    # 确保使用 /data/ 目录存储数据
    if not db_path.startswith('/data/'):
        # 如果配置的路径不是以 /data/ 开头，则修改为使用 /data/ 目录
        db_filename = os.path.basename(db_path)
        db_path = f'/data/{db_filename}'
        config.u.info(f'[app-chart] 数据库路径已调整为使用 /data/ 目录: {db_path}')

    # 确保数据库路径是绝对路径
    _db_path = _utils.get_path(db_path)

    # 确保 /data/ 目录存在
    data_dir = os.path.dirname(_db_path)
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            config.u.info(f'[app-chart] 创建数据目录: {data_dir}')
        except Exception as e:
            config.u.error(f'[app-chart] 创建数据目录失败: {e}')
            return False

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
            config.u.error(f"[app-chart] 获取模式列表失败: {e}")

        return True
    except Exception as e:
        config.u.error(f'[app-chart] 插件初始化失败: {e}')
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
    :return: 匹配后的应用名称，如果应该忽略则返回 None
    """
    conn = _get_db()
    cursor = conn.cursor()

    try:
        # 获取应用名称模式
        cursor.execute('SELECT pattern, replacement FROM app_name_patterns WHERE enabled = 1')
        patterns = cursor.fetchall()

        # 应用模式匹配
        for pattern in patterns:
            pattern_str = pattern['pattern']
            replacement = pattern['replacement']

            # 检查是否匹配
            is_match = False

            # 处理前缀通配符 (*xxx)
            if pattern_str.startswith('*') and len(pattern_str) > 1:
                suffix = pattern_str[1:]
                if app_name.endswith(suffix):
                    is_match = True

            # 处理后缀通配符 (xxx*)
            elif pattern_str.endswith('*') and len(pattern_str) > 1:
                prefix = pattern_str[:-1]
                if app_name.startswith(prefix):
                    is_match = True

            # 处理包含通配符 (*xxx*)
            elif pattern_str.startswith('*') and pattern_str.endswith('*') and len(pattern_str) > 2:
                substring = pattern_str[1:-1]
                if substring in app_name:
                    is_match = True

            # 精确匹配
            elif pattern_str == app_name:
                is_match = True

            # 如果匹配成功
            if is_match:
                # 特殊处理：如果替换值为 "IGNORE"，返回 None 表示忽略此应用
                if replacement.upper() == "IGNORE":
                    return None
                else:
                    return replacement
    except Exception as e:
        # 如果出错，记录错误并返回原始应用名称
        print(f"Error in _apply_app_name_patterns: {e}")
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

        # 如果应用名称被标记为忽略（返回None），则不记录统计
        if mapped_app_name is None:
            return

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

                # 检查应用是否应该被忽略
                mapped_last_app = _apply_app_name_patterns(last_app)

                # 如果上一个应用不应该被忽略
                if mapped_last_app is not None:
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
    import os

    # 获取当前设置
    db_path = config.getconf('db_path')
    max_apps = config.getconf('max_apps')
    default_days = config.getconf('default_days')
    chart_height = config.getconf('chart_height')
    colors = config.getconf('colors')

    # 颜色列表转为字符串
    colors_str = '\n'.join(colors) if colors else ''

    # 读取外部文件
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    # 读取HTML模板
    html_path = os.path.join(plugin_dir, 'settings.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 读取CSS
    css_path = os.path.join(plugin_dir, 'settings.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # 读取JavaScript
    js_path = os.path.join(plugin_dir, 'settings.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 构建卡片内容
    content = f"""
    {html_content}

    <style>
    {css_content}
    </style>

    <script>
    {js_content}
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

    :param _: 插件配置对象（未使用）
    :return: 卡片内容
    """
    import os

    # 读取外部文件
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    # 读取HTML模板
    html_path = os.path.join(plugin_dir, 'data-management.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 读取CSS
    css_path = os.path.join(plugin_dir, 'data-management.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # 读取JavaScript
    js_path = os.path.join(plugin_dir, 'data-management.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 构建卡片内容
    content = f"""
    {html_content}

    <style>
    {css_content}
    </style>

    <script>
    {js_content}
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

        # 确保使用 /data/ 目录
        import os
        if not db_path.startswith('/data/'):
            db_filename = os.path.basename(db_path)
            db_path = f'/data/{db_filename}'

        if max_apps < 1 or max_apps > 50:
            return {'success': False, 'message': '最大应用数量必须在1-50之间'}

        if default_days not in [7, 14, 30]:
            return {'success': False, 'message': '默认显示天数必须是7、14或30'}

        if chart_height < 100 or chart_height > 800:
            return {'success': False, 'message': '图表高度必须在100-800之间'}

        if not colors or len(colors) < 1:
            return {'success': False, 'message': '至少需要一种颜色'}

        # 更新配置文件
        config_path = _utils.get_path('data/config.yaml')

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
            return {'success': False, 'message': f'保存配置失败: {e}'}
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
    import os

    # 读取外部文件
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    # 读取HTML模板
    html_path = os.path.join(plugin_dir, 'patterns.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 读取CSS
    css_path = os.path.join(plugin_dir, 'patterns.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # 读取JavaScript
    js_path = os.path.join(plugin_dir, 'patterns.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 构建卡片内容
    content = f"""
    {html_content}

    <style>
    {css_content}
    </style>

    <script>
    {js_content}
    </script>
    """

    return content

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

@route('/import-db', methods=['POST'])
def import_database():
    """
    导入数据库文件

    :return: 操作结果
    """
    try:
        from flask import request
        import os
        import shutil
        import tempfile

        # 检查是否有文件上传
        if 'db_file' not in request.files:
            return {
                'success': False,
                'message': '没有上传文件'
            }

        file = request.files['db_file']
        if file.filename == '':
            return {
                'success': False,
                'message': '没有选择文件'
            }

        # 检查文件扩展名
        if not file.filename.endswith('.db'):
            return {
                'success': False,
                'message': '请上传有效的 SQLite 数据库文件 (.db)'
            }

        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_db_path = os.path.join(temp_dir, 'temp_import.db')

        # 保存上传的文件到临时位置
        file.save(temp_db_path)

        # 验证文件是否为有效的 SQLite 数据库
        try:
            import sqlite3
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()

            # 检查必要的表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='app_usage' OR name='daily_stats' OR name='app_name_patterns')")
            tables = cursor.fetchall()

            if len(tables) < 2:  # 至少应该有 app_usage 和 daily_stats 表
                conn.close()
                return {
                    'success': False,
                    'message': '无效的数据库文件，缺少必要的表'
                }

            conn.close()
        except Exception as e:
            return {
                'success': False,
                'message': f'无效的 SQLite 数据库文件: {str(e)}'
            }

        # 使用线程锁确保在替换过程中没有其他线程访问数据库
        with _db_lock:
            # 备份当前数据库
            backup_dir = tempfile.mkdtemp()
            backup_db_path = os.path.join(backup_dir, 'app_chart_backup.db')

            if os.path.exists(_db_path):
                shutil.copy2(_db_path, backup_db_path)

            try:
                # 替换数据库文件
                shutil.copy2(temp_db_path, _db_path)
            except Exception as e:
                # 如果替换失败，恢复备份
                if os.path.exists(backup_db_path):
                    shutil.copy2(backup_db_path, _db_path)
                raise e

        return {
            'success': True,
            'message': '数据库导入成功'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

@route('/import-json', methods=['POST'])
def import_json_data():
    """
    导入 JSON 数据

    :return: 操作结果
    """
    try:
        from flask import request

        # 获取请求数据
        data = request.get_json()

        if not data or 'data' not in data:
            return {
                'success': False,
                'message': '无效的请求数据'
            }

        json_data = data['data']
        clear_before_import = data.get('clear_before_import', False)

        # 验证 JSON 数据结构
        if 'daily_stats' not in json_data or 'app_usage' not in json_data:
            return {
                'success': False,
                'message': '无效的数据格式，缺少必要的数据字段'
            }

        daily_stats = json_data['daily_stats']
        app_usage = json_data['app_usage']

        if not isinstance(daily_stats, list) or not isinstance(app_usage, list):
            return {
                'success': False,
                'message': '无效的数据格式，数据字段必须是数组'
            }

        # 使用线程锁确保在导入过程中没有其他线程访问数据库
        with _db_lock:
            conn = _get_db()
            cursor = conn.cursor()

            try:
                # 如果需要，清除现有数据
                if clear_before_import:
                    cursor.execute('DELETE FROM app_usage')
                    cursor.execute('DELETE FROM daily_stats')
                    cursor.execute('DELETE FROM sqlite_sequence WHERE name="app_usage" OR name="daily_stats"')

                # 导入每日统计数据
                daily_count = 0
                for record in daily_stats:
                    if 'date' in record and 'app_name' in record and 'total_duration' in record:
                        cursor.execute('''
                        INSERT INTO daily_stats (date, app_name, total_duration)
                        VALUES (?, ?, ?)
                        ON CONFLICT(date, app_name) DO UPDATE SET
                        total_duration = total_duration + ?
                        ''', (record['date'], record['app_name'], record['total_duration'], record['total_duration']))
                        daily_count += 1

                # 导入应用使用记录
                usage_count = 0
                for record in app_usage:
                    if 'device_id' in record and 'device_name' in record and 'app_name' in record:
                        start_time = record.get('start_time')
                        end_time = record.get('end_time')
                        duration = record.get('duration', 0)

                        cursor.execute('''
                        INSERT INTO app_usage (device_id, device_name, app_name, start_time, end_time, duration)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (record['device_id'], record['device_name'], record['app_name'], start_time, end_time, duration))
                        usage_count += 1

                conn.commit()

                return {
                    'success': True,
                    'message': '数据导入成功',
                    'stats': {
                        'daily_count': daily_count,
                        'usage_count': usage_count
                    }
                }
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

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
