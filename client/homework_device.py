# coding: utf-8

import requests

# --- config start
SERVER = 'https://sleepy.example.com' # 部署地址，末尾不带 `/`
SECRET = '11111111-4444-5555-1111-444444444444'
# --- config end

# ----- api request


def device_set(id, show_name, msg):
    '''
    /device/set using POST
    '''
    resp = requests.post(url=f'{SERVER}/device/set', json={
        'secret': SECRET,
        'id': id,
        'show_name': show_name,
        'using': True,
        'app_name': msg
    }, headers={
        'Content-Type': 'application/json'
    })
    print(f'[/device/set] Response: {resp.status_code} - {resp.json()}')


def device_remove(id):
    '''
    /device/remove using GET
    '''
    resp = requests.get(url=f'{SERVER}/device/remove?secret={SECRET}&id={id}')
    print(f'[/device/remove] Response: {resp.status_code} - {resp.json()}')

# ----- functions


def left(num: int):
    '''
    set how much homework left
    '''
    if num == 0:
        device_remove(id='homework-left')
    else:
        device_set(
            id='homework-left',
            show_name='Homework left',
            msg=f'{num}'
        )


def writing(name: str):
    '''
    set what homework you're writing
    '''
    if name == '':
        device_remove(id='homework-name')
    else:
        device_set(
            id='homework-name',
            show_name='Homework writing',
            msg=name
        )


if __name__ == '__main__':
    try:
        while True:
            i = input('in  < ')
            try:
                o = eval(i)
                print(f'out > {o}')
            except Exception as e:
                print(f'err - {e}')
    except Exception as e:
        print(f'Exiting: {e}')
        exit(0)
