#!/usr/bin/python3
# coding: utf-8
import os
import time
c = 0
server = os.path.join(os.path.dirname(sys.argv[0]), 'server.py')
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
