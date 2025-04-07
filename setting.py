# coding: utf-8

import json
import utils as u


class setting:
    '''
    setting 类 \n
    加载指定 json 文件内容到 `self.content`
    '''
    config: dict

    def __init__(self, filename: str):
        self.load(filename)

    def load(self, filename: str):
        '''
        加载配置
        '''
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.content = json.load(file)
        except Exception as e:
            u.exception(f'[setting] Error loading {filename}: {e}')


status_list: list = setting(u.get_path('setting/status_list.json')).content
metrics_list: list = setting(u.get_path('setting/metrics_list.json')).content

# metrics_list 中 [static] 处理
if '[static]' in metrics_list:
    metrics_list.remove('[static]')
    static_list = u.list_dir(u.get_path('static/'))
    metrics_list.extend(['/static/' + i for i in static_list])
