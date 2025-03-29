# coding: utf-8
import requests as r
import json
import sys

sys.path.append('../')
if True:
    import env

BASE = f'http://{f"[{env.main.host}]" if ":" in env.main.host else env.main.host}:{env.main.port}'
SECRET = env.main.secret


def get(path: str):
    reqpath = f'{BASE}{path if path.startswith("/") else "/" + path}'
    req = r.get(
        reqpath,
        headers={
            'Sleepy-Secret': SECRET
        }
    )
    return f'GET {reqpath} {req.status_code}\n{req.text}'.replace(SECRET, '[SECRET]')


def post(path: str, data: dict):
    if type(data) == str:
        data = json.loads(data)
    reqpath = f'{BASE}{path if path.startswith("/") else "/" + path}'
    req = r.post(
        reqpath,
        headers={
            'Sleepy-Secret': SECRET
        },
        json=data
    )
    return f'GET {reqpath} {req.status_code}\n{req.text}'.replace(SECRET, '[SECRET]')


if __name__ == '__main__':
    while True:
        try:
            inp = input('I < ')
            if inp.startswith('get '):
                out = get(inp[4:])
            elif inp.startswith('g '):
                out = get(inp[2:])
            elif inp.startswith('post '):
                out = post(*inp[5:].split(' ', 1))
            elif inp.startswith('p '):
                out = post(*inp[2:].split(' ', 1))
            else:
                out = eval(inp)
            print(f'O > {out}')
        except Exception as e:
            print(f'E - {e}')
        except KeyboardInterrupt:
            exit(0)
