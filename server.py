#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response
from markupsafe import escape
from datetime import datetime
import pytz

import utils as u
from config import config as config_init
from data import data as data_init

c = config_init()
d = data_init()
app = Flask(__name__)
timezone = 'Asia/Shanghai'


# --- Functions


def showip(req: request, msg): # type: ignore
    '''
    在日志中显示 ip

    :param req: `flask.request` 对象, 用于取 ip
    :param msg: 信息
    '''
    ip1 = req.remote_addr
    try:
        ip2 = req.headers['X-Forwarded-For']
        u.infon(f'- Request: {ip1} / {ip2} : {msg}')
    except:
        ip2 = None
        u.infon(f'- Request: {ip1} : {msg}')


# --- Templates


@app.route('/')
def index():
    '''
    根目录返回 html
    - Method: **GET**
    '''
    showip(request, '/')
    ot = c.config['other']
    try:
        stat = c.config['status_list'][d.data['status']]
    except:
        stat = {
            'name': '未知',
            'desc': '未知的标识符，可能是配置问题。',
            'color': 'error'
        }
    return render_template(
        'index.html',
        user=ot['user'],
        learn_more=ot['learn_more'],
        repo=ot['repo'],
        status_name=stat['name'],
        status_desc=stat['desc'],
        status_color=stat['color'],
        more_text=ot['more_text'],
        last_updated=d.data['last_updated']
    )


@app.route('/get.js')
def get_js():
    '''
    /get.js
    - Method: **GET**
    '''
    return render_template(
        'get.js',
        interval=c.config['refresh']
    )


@app.route('/style.css')
def style_css():
    '''
    /style.css
    - Method: **GET**
    '''
    response = make_response(render_template(
        'style.css',
        bg=c.config['other']['background'],
        alpha=c.config['other']['alpha']
    ))
    response.mimetype = 'text/css'
    return response


# --- Status API


@app.route('/query')
def query():
    '''
    获取当前状态
    - 无需鉴权
    - Method: **GET**
    '''
    showip(request, '/query')
    st = d.data['status']
    try:
        stinfo = c.config['status_list'][st]
    except:
        stinfo = {
            'id': -1,
            'name': '未知',
            'desc': '未知的标识符，可能是配置问题。',
            'color': 'error'
        }
    ret = {
        'time': datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S'),
        'success': True,
        'status': st,
        'info': stinfo,
        'device': d.data['device_status'],
        'device_status_slice': c.config['other']['device_status_slice'],
        'last_updated': d.data['last_updated'],
        'refresh': c.config['refresh']
    }
    return u.format_dict(ret)


@app.route('/get/status_list')  # 兼容旧版
@app.route('/status_list')
def get_status_list():
    '''
    获取 `status_list`
    - 无需鉴权
    - Method: **GET**
    '''
    showip(request, '/status_list')
    stlst = c.get('status_list')
    return u.format_dict(stlst)


@app.route('/set')
def set_normal():
    '''
    普通的 set 设置状态
    - http[s]://<your-domain>[:your-port]/set?secret=<your-secret>&status=<a-number>
    - Method: **GET**
    '''
    showip(request, '/set')
    status = escape(request.args.get('status'))
    try:
        status = int(status)
    except:
        return u.reterr(
            code='bad request',
            message="argument 'status' must be a number"
        )
    secret = escape(request.args.get('secret'))
    secret_real = c.get('secret')
    if secret == secret_real:
        d.dset('status', status)
        return u.format_dict({
            'success': True,
            'code': 'OK',
            'set_to': status
        })
    else:
        return u.reterr(
            code='not authorized',
            message='invaild secret'
        )


@app.route('/set/<secret>/<int:status>')
def set_path(secret, status):
    '''
    set 设置状态, 但参数直接写路径里
    - http[s]://<your-domain>[:your-port]/set/<your-secret>/<a-number>
    - Method: **GET**
    '''
    showip(request, '/set/<secret>/<status>')
    secret = escape(secret)
    secret_real = c.get('secret')
    if secret == secret_real:
        d.dset('status', status)
        ret = {
            'success': True,
            'code': 'OK',
            'set_to': status
        }
        return u.format_dict(ret)
    else:
        return u.reterr(
            code='not authorized',
            message='invaild secret'
        )


# --- Device API


@app.route('/device/set', methods=['GET', 'POST'])
def device_set():
    '''
    设置单个设备的信息/打开应用
    - Method: **GET / POST**
    - **GET 可能出现 using 参数无效的情况，建议使用 POST**
    '''
    showip(request, '/device_set')
    if request.method == 'GET':
        try:
            device_id = escape(request.args.get('id'))
            device_show_name = escape(request.args.get('show_name'))
            device_using = bool(escape(request.args.get('using')))
            app_name = escape(request.args.get('app_name'))
        except:
            return u.reterr(
                code='bad request',
                message='missing param or wrong param type'
            )
        secret = escape(request.args.get('secret'))
        secret_real = c.get('secret')
        if secret == secret_real:
            devices: dict = d.dget('device_status')
            devices[device_id] = {
                'show_name': device_show_name,
                'using': device_using,
                'app_name': app_name
            }
            d.data['last_updated'] = datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return u.reterr(
                code='not authorized',
                message='invaild secret'
            )
    elif request.method == 'POST':
        req = request.get_json()
        try:
            secret = req['secret']
            device_id = req['id']
            device_show_name = req['show_name']
            device_using = bool(req['using'])
            app_name = req['app_name']
        except:
            return u.reterr(
                code='bad request',
                message='missing param'
            )
        secret_real = c.get('secret')
        if secret == secret_real:
            devices: dict = d.dget('device_status')
            devices[device_id] = {
                'show_name': device_show_name,
                'using': device_using,
                'app_name': app_name
            }
            d.data['last_updated'] = datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return u.reterr(
                code='not authorized',
                message='invaild secret'
            )
    else:
        return u.reterr(
            code='invaild request',
            message='only supports GET and POST method!'
        )
    return u.format_dict({
        'success': True,
        'code': 'OK'
    })


@app.route('/device/remove')
def remove_device():
    '''
    移除单个设备的状态
    - Method: **GET**
    '''
    showip(request, '/device/remove')
    device_id = escape(request.args.get('id'))
    secret = escape(request.args.get('secret'))
    secret_real = c.get('secret')
    if secret == secret_real:
        try:
            del d.data['device_status'][device_id]
            d.data['last_updated'] = datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S')
        except KeyError:
            return u.reterr(
                code='not found',
                message='cannot find item'
            )
    else:
        return u.reterr(
            code='not authorized',
            message='invaild secret'
        )
    return u.format_dict({
        'success': True,
        'code': 'OK'
    })


@app.route('/device/clear')
def clear_device():
    '''
    清除所有设备状态
    - Method: **GET**
    '''
    showip(request, '/device/clear')
    secret = escape(request.args.get('secret'))
    secret_real = c.get('secret')
    if secret == secret_real:
        d.data['device_status'] = {}
        d.data['last_updated'] = datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return u.reterr(
            code='not authorized',
            message='invaild secret'
        )
    return u.format_dict({
        'success': True,
        'code': 'OK'
    })


# --- Storage API

@app.route('/reload_config')
def reload_config():
    '''
    从 `config.json` 重载配置
    - Method: **GET**
    '''
    showip(request, '/reload_config')
    secret = escape(request.args.get('secret'))
    secret_real = c.get('secret')
    if secret == secret_real:
        c.load()
        return u.format_dict({
            'success': True,
            'code': 'OK',
        })
    else:
        return u.reterr(
            code='not authorized',
            message='invaild secret'
        )


@app.route('/save_data')
def save_data():
    '''
    保存内存中的状态信息到 `data.json`
    - Method: **GET**
    '''
    showip(request, '/save_data')
    secret = escape(request.args.get('secret'))
    secret_real = c.get('secret')
    if secret == secret_real:
        d.save()
        return u.format_dict({
            'success': True,
            'code': 'OK',
            'data': d.data
        })
    else:
        return u.reterr(
            code='not authorized',
            message='invaild secret'
        )


# --- End
if __name__ == '__main__':
    c.load()
    d.load()
    d.start_timer_check(data_check_interval=c.config['data_check_interval'])  # 启动定时保存
    app.run(  # 启↗动↘
        host=c.config['host'],
        port=c.config['port'],
        debug=c.config['debug']
    )
