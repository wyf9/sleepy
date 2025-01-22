# coding: utf-8

import requests

# --- config start
SERVER = 'https://sleepy.example.com'  # 部署地址，末尾不带 `/`
SECRET = '11111111-4444-5555-1111-444444444444'
# --- config end

# ----- functions


def device_set(id: str, show_name: str, msg: str, using: bool = True):
    '''
    /device/set using POST
    '''
    resp = requests.post(url=f'{SERVER}/device/set', json={
        'secret': SECRET,
        'id': id,
        'show_name': show_name,
        'using': using,
        'app_name': msg
    }, headers={
        'Content-Type': 'application/json'
    })
    print(f'[/device/set] Response: {resp.status_code} - {resp.json()}')


def device_remove(id: str):
    '''
    /device/remove using GET
    '''
    resp = requests.get(url=f'{SERVER}/device/remove?secret={SECRET}&id={id}')
    print(f'[/device/remove] Response: {resp.status_code} - {resp.json()}')


def device_clear():
    '''
    /device/clear using GET
    '''
    resp = requests.get(url=f'{SERVER}/device/clear?secret={SECRET}')
    print(f'[/device/clear] Response: {resp.status_code} - {resp.json()}')


def private_mode(private: bool):
    '''
    /device/private_mode using GET
    '''
    if private:
        private = 'true'
    else:
        private = 'false'
    resp = requests.get(url=f'{SERVER}/device/private_mode?secret={SECRET}&private={private}')
    print(f'[/device/clear] Response: {resp.status_code} - {resp.json()}')

# ---


def left(num: int = 0):
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


def writing(name: str = ''):
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

# ---


def query():
    '''
    check status now
    '''
    resp = requests.get(url=f'{SERVER}/query')
    print(f'[/query] Response: {resp.status_code} - {resp.text}')


def lst():
    '''
    status list
    '''
    resp = requests.get(url=f'{SERVER}/status_list')
    print(f'[/status_list] Response: {resp.status_code} - {resp.text}')


def status(stat: int):
    '''
    set status
    '''
    resp = requests.get(url=f'{SERVER}/set?secret={SECRET}&status={stat}')
    print(f'[/set] Response: {resp.status_code} - {resp.json()}')

# ----- main loop


if __name__ == '__main__':
    try:
        while True:
            i = input('in  < ')
            try:
                o = eval(i)
                print(f'out > {o}')
            except Exception as e:
                print(f'err - {e}')
    except KeyboardInterrupt:
        print('Exiting: ^C')
    except Exception as e:
        print(f'Exiting: {e}')
    exit()
