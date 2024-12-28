'''
passenger_wsgi.py
方便 Serv00 WWW 使用
'''
import sys
import os
sys.path.append(os.getcwd())

from application import app as application # type: ignore