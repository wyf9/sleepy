#!/usr/bin/python3
# coding: utf-8

import os
import sys
import time

c = 0
selfn = sys.argv[0]
dirn = os.path.dirname(selfn)
server = os.path.join(dirn, 'server.py')
if len(sys.argv) > 1:
    if sys.argv[1] == 'screen':
        st = os.system(f'cd {dirn} && screen -dmS sleepy {sys.argv[0]}')
        if st == 0:
            print(f'Started screen: cd {dirn} && screen -dmS sleepy {sys.argv[0]}')
            while True:
                time.sleep(114514)
            # exit(0)
        else:
            print(f'Start screen failed: cd {dirn} && screen -dmS sleepy {sys.argv[0]}')
            exit(1)
    else:
        print('Invaild arg.')
        exit(1)
print(f'Server path: {server}')
while True:
    c += 1
    print(f'Starting server #{c}')
    if os.name == 'nt':
        r = os.system(f'python {server}')
    else:
        r = os.system(f'python3 {server}')
    print(f'#{c} exited with code {r}\nwaiting 5s')
    time.sleep(5)
