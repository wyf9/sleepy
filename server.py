#!/usr/bin/python3
# coding: utf-8
import utils as u
from data import data as data_init
from flask import Flask, render_template, request, url_for, redirect, flash
from markupsafe import escape
import json

d = data_init()
app = Flask(__name__)

# ---


def reterr(code, message):
    ret = {
        'success': False,
        'code': code,
        'message': message
    }
    u.error(f'{code} - {message}')
    return u.format_dict(ret)


def get_ip(req):
    ip1 = req.remote_addr
    try:
        ip2 = req.headers['X-Forwarded-For']
    except:
        ip2 = None
    return ip1, ip2


def showip(req, msg):
    ip1, ip2 = get_ip(req)
    u.infon(f'- Conn: {ip1} / {ip2} : {msg}')

# ---


@app.route('/')
def index():
    d.load()
    showip(request, '/')
    ot = d.data['other']
    stat = d.data['status_list'][d.data['status']]
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


@app.route('/query')
def query():
    d.load()
    showip(request, '/query')
    st = d.data['status']
    stlst = d.data['status_list']
    try:
        stinfo = d.data['status_list'][st]
    except:
        stinfo = {
            'status': st,
            'name': '未知'
        }
    ret = {
        'success': True,
        'status': st,
        'info': stinfo
    }
    return u.format_dict(ret)


@app.route('/set', methods=['GET', 'POST'])
def set():
    showip(request, '/set')
    if request.method == "GET":
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
    else:
        return reterr(
            code='bad request',
            message='only support GET request now'
        )


@app.route('/set/<secret>/<int:status>')
def set_path(secret, status):
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
    app.run(
        host=d.data['host'],
        port=d.data['port'],
        debug=d.data['debug']
    )
