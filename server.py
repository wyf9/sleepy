#!/usr/bin/python3
# coding: utf-8
import utils as u
from data import data as data_init
from flask import Flask, render_template, request, make_response
# from flask import Flask, render_template, request, url_for, redirect, flash, make_response
from markupsafe import escape
# import json

d = data_init()
app = Flask(__name__)

# --- Functions


def reterr(code: int, message: str) -> str:
    '''
    返回错误信息 json

    :param code: 代码
    :param message: 消息
    '''
    ret = {
        'success': False,
        'code': code,
        'message': message
    }
    u.error(f'{code} - {message}')
    return u.format_dict(ret)


def showip(req, msg):
    '''
    在日志中显示 ip

    :param req: `Request` 对象, 用于取 ip
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
    '''
    d.load()
    showip(request, '/')
    ot = d.data['other']
    try:
        stat = d.data['status_list'][d.data['status']]
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
        more_text=ot['more_text']
    )


@app.route('/get.js')
def get_js():
    '''
    /get.js
    '''
    return render_template(
        'get.js',
        interval=d.data['refresh']
    )


@app.route('/style.css')
def style_css():
    '''
    /style.css
    '''
    response = make_response(render_template(
        'style.css',
        bg=d.data['other']['background'],
        alpha=d.data['other']['alpha']
    ))
    response.mimetype = 'text/css'
    return response

# --- API


@app.route('/query')
def query():
    '''
    获取当前状态
    - 无需鉴权
    '''
    d.load()
    showip(request, '/query')
    st = d.data['status']
    # stlst = d.data['status_list']
    try:
        stinfo = d.data['status_list'][st]
    except:
        stinfo = {
            'id': -1,
            'name': '未知',
            'desc': '未知的标识符，可能是配置问题。',
            'color': 'error'
        }
    ret = {
        'success': True,
        'status': st,
        'info': stinfo,
        'refresh': d.data['refresh']
    }
    return u.format_dict(ret)


@app.route('/get/status_list')
def get_status_list():
    '''
    获取 `status_list`
    - 无需鉴权
    '''
    showip(request, '/get/status_list')
    stlst = d.dget('status_list')
    return u.format_dict(stlst)


@app.route('/set')
def set_normal():
    '''
    普通的 set 设置状态
    - http[s]://<your-domain>[:your-port]/set?secret=<your-secret>&status=<a-number>
    '''
    showip(request, '/set')
    status = escape(request.args.get("status"))
    try:
        status = int(status)
    except:
        return reterr(
            code='bad request',
            message="argument 'status' must be a number"
        )
    secret = escape(request.args.get("secret"))
    u.info(f'status: {status}, secret: "{secret}"')
    secret_real = d.dget('secret')
    if secret == secret_real:
        d.dset('status', status)
        u.info('set success')
        ret = {
            'success': True,
            'code': 'OK',
            'set_to': status
        }
        return u.format_dict(ret)
    else:
        return reterr(
            code='not authorized',
            message='invaild secret'
        )


@app.route('/set/<secret>/<int:status>')
def set_path(secret, status):
    '''
    set 设置状态, 但参数直接写路径里
    - http[s]://<your-domain>[:your-port]/set/<your-secret>/<a-number>
    '''
    showip(request, f'/set/{secret}/{status}')
    secret = escape(secret)
    u.info(f'status: {status}, secret: "{secret}"')
    secret_real = d.dget('secret')
    if secret == secret_real:
        d.dset('status', status)
        u.info('set success')
        ret = {
            'success': True,
            'code': 'OK',
            'set_to': status
        }
        return u.format_dict(ret)
    else:
        return reterr(
            code='not authorized',
            message='invaild secret'
        )


if __name__ == '__main__':
    d.load()
    app.run(  # 启↗动↘
        host=d.data['host'],
        port=d.data['port'],
        debug=d.data['debug']
    )
