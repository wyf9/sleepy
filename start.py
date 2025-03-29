#!/usr/bin/python3
# coding: utf-8

from os import name, path, system
from sys import argv
from time import sleep

Server_Path = 'server.py'  # server.py 相对路径
Sleep_Time = 5  # 等待时间 (s)

c = 0  # count
selfn = argv[0]  # self
dirn = path.dirname(selfn)  # self dir
server = path.join(dirn, Server_Path)  # server.py path
print(f'[Start] Server path: {server}')
while True:
    c += 1
    print(f'[Start] Starting server #{c}')
    if name == 'nt':
        # Windows
        r = system(f'python {server}')
    else:
        # not Windows
        r = system(f'python3 {server}')
    print(f'[Start] #{c} exited with code {r}\nwaiting {Sleep_Time}s')
    sleep(Sleep_Time)
