# coding: utf-8

import json
import json5

import utils as u


class setting:
    '''
    setting 类 \n
    加载指定 json 文件内容到 `self.content`
    '''
    config: dict

    def __init__(self, name: str):
        try:
            # load user setting
            self.load(u.get_path(f'setting/{name}.json'))
        except:
            self.load(u.get_path(f'setting/{name}.default.jsonc'))

    def load(self, filename: str):
        '''
        加载配置
        '''
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.content = json5.load(file)
        except Exception as e:
            u.exception(f'[setting] Error loading {filename}: {e}')


status_list: list = setting('status_list').content
metrics_list: list = setting('metrics_list').content

# status_list 中自动补全 id
for i in range(len(status_list)):
    status_list[i]['id'] = i

# metrics_list 中 [static] 处理
if '[static]' in metrics_list:
    metrics_list.remove('[static]')
    static_list = u.list_dir(u.get_path('static/'))
    metrics_list.extend(['/static/' + i for i in static_list])
