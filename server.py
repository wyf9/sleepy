#!/usr/bin/python3
# coding: utf-8
import utils as u
from data import data as data_init
from flask import Flask, render_template, request, url_for, redirect, flash
from markupsafe import escape
import json

d = data_init()
app = Flask(__name__)


@app.route('/')
def index():
    d.load()
    ot = d.data['other']
    stat = d.data['status_list'][d.data['status']]
    return render_template('index.html',
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
                code='bad request',
                message="argument 'status' must be a number"
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
                code='not authorized',
                message='invaild secret'
            )
    else:
        return reterr(
            code='bad request',
            message='only support GET request now'
        )


if __name__ == '__main__':
    d.load()
    app.run(
        host=d.data['host'],
        port=d.data['port'],
        debug=d.data['debug']
    )
