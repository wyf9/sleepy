#!/usr/bin/python3
# coding: utf-8

import os
import sys
import time

c = 0  # count
selfn = sys.argv[0]  # self
dirn = os.path.dirname(selfn)  # self dir
server = os.path.join(dirn, 'server.py')  # server.py path
print(f'Server path: {server}')
while True:
    # loop
    c += 1
    print(f'Starting server #{c}')
    if os.name == 'nt':
        # Windows
        r = os.system(f'python {server}')
    else:
        # Others
        r = os.system(f'python3 {server}')
    print(f'#{c} exited with code {r}\nwaiting 5s')
    time.sleep(5)
