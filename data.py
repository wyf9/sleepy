# coding: utf-8

import json
import os
import utils as u

# 检测是否存在
def initJson():
    try:
        jsonData = {
            'version': 1,
            'debug': False,
            'host': '0.0.0.0',
            'port': 9010,
            'secret': '',
            'status': 0,
            'status_list': [
                {
                    'name': '活着',
                    'desc': '目前在线，可以通过任何可用的联系方式联系本人。',
                    'color': 'awake'
                },
                {
                    'name': '似了',
                    'desc': '睡似了或其他原因不在线，紧急情况请使用电话联系。',
                    'color': 'sleeping'
                }
            ],
            'other': {
                'user': 'User',
                'learn_more': 'GitHub Repo',
                'repo': 'https://github.com/wyf9/sleepy',
                'more_text': ''
            }
        }

        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(jsonData, file, indent=4, ensure_ascii=False)
    except:
        u.error('Create data.json failed')
        raise



class data:
    def __init__(self):
        if not os.path.exists('data.json'):
            u.warning('data.json not exist, creating')
            initJson()
        with open('data.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)
    def load(self):
        with open('data.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)
    def save(self):
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
    def dset(self, name, value):
        self.data[name] = value
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
    def dget(self, name):
        with open('data.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)
            try:
                gotdata = self.data[name]
            except:
                gotdata = None
            return gotdata