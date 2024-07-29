#!/usr/bin/python3
# coding: utf-8
import utils as u
from data import data as data_init
from flask import Flask as flask
import json
from flask import request, url_for, redirect, flash
from markupsafe import escape
DEBUG = True
d = data_init()
app = flask(__name__)


@app.route('/hello')
def hello():
    return 'Hello world'


@app.route('/query')
def query():
    d.load()
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


def reterr(code, message):
    ret = {
        'success': False,
        'code': code,
        'message': message
    }
    u.error(f'{code} - {message}')
    return u.format_dict(ret)


@app.route('/set', methods=['GET', 'POST'])
def set():
    print()
    if request.method == "GET":
        status = escape(request.args.get("status"))
        try:
            status = int(status)
        except:
            return reterr(
                code = 'bad request',
                message = "argument 'status' must be a number"
            )
        secret = escape(request.args.get("secret"))
        u.info(f'req: status: {status}, secret: "{secret}"')
        secret_real = d.dget('secret')
        if secret == secret_real:
            d.dset('status', status)
            u.info('set success')
            ret = {
                'success': True,
                'code': 'OK',
            }
            return u.format_dict(ret)
        else:
            return reterr(
                code = 'not authorized',
                message = 'invaild secret'
            )
    else:
        return reterr(
            code = 'bad request',
            message = 'only support GET request now'
        )
    


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=3010,
        debug=DEBUG
    )
