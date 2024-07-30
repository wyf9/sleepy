# coding: utf-8

import json
import os
import utils as u
from jsonc_parser.parser import JsoncParser as jsonp


def initJson():
    try:
        jsonData = jsonp.parse_file('example.jsonc', encoding='utf-8')
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
