#!/usr/bin/python3
# coding:utf-8

'''
一个 python 服务器设备，个人状态管理器
依赖: requests, prettytable, argparse
by @gongfuture
'''

import requests
import json
import sys
import argparse
import shlex
from typing import Dict, List, Union, Any, Optional

# 尝试导入 PrettyTable，如果不可用则提供简易替代
try:
    from prettytable import PrettyTable
    PRETTYTABLE_AVAILABLE = True
except ImportError:
    PRETTYTABLE_AVAILABLE = False
    print("警告: PrettyTable 库未安装，将使用简易格式化输出。")
    print("您可以通过 'pip install prettytable' 安装该库以获得更好的显示效果。")

# --- config start
# 密钥
SECRET = ''
# 服务地址, 末尾不加 `/`
SERVER = 'http://127.0.0.1:9010'
# 请求重试次数
RETRY = 3
# 是否显示原始 JSON 响应
SHOW_RAW_JSON = False
# --- config end

class SleepyManager:
    """Sleepy API 管理类，封装了所有 API 调用"""
    
    def __init__(self, server: str, secret: str, retry: int = 3):
        """初始化 SleepyManager"""
        self.server = server.rstrip('/')
        self.secret = secret
        self.retry = retry
    
    def _request(self, method: str, path: str, params: Dict = None, json_data: Dict = None) -> Dict:
        """发送请求并处理重试逻辑"""
        url = f"{self.server}/{path.lstrip('/')}"
        
        # 如果是 GET 请求且没有 params，初始化一个空字典
        if method.upper() == 'GET' and params is None:
            params = {}
        
        # 如果需要身份验证且未在参数中指定密钥
        if params is not None and 'secret' not in params:
            params['secret'] = self.secret
        
        # 如果是 POST 请求且需要 JSON 数据
        if method.upper() == 'POST' and json_data is not None and 'secret' not in json_data:
            json_data['secret'] = self.secret
            
        for attempt in range(self.retry):
            try:
                response = requests.request(
                    method=method, 
                    url=url, 
                    params=params, 
                    json=json_data,
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if attempt == self.retry - 1:
                    print(f"请求失败 ({attempt + 1}/{self.retry}): {e}")
                    raise
                print(f"请求失败，正在重试 ({attempt + 1}/{self.retry}): {e}")
    
    # ------ Read-only APIs ------
    
    def query(self) -> Dict:
        """获取当前状态"""
        return self._request('GET', 'query')
    
    def status_list(self) -> List[Dict]:
        """获取可用状态列表"""
        return self._request('GET', 'status_list')
    
    def metrics(self) -> Dict:
        """获取统计信息"""
        return self._request('GET', 'metrics')
    
    # ------ Status APIs ------
    
    def set_status(self, status: int) -> Dict:
        """设置当前状态"""
        return self._request('GET', 'set', params={'status': status})
    
    # ------ Device APIs ------
    
    def device_set(self, id: str, show_name: str, using: bool, app_name: str) -> Dict:
        """设置单个设备的状态"""
        data = {
            'id': id,
            'show_name': show_name,
            'using': using,
            'app_name': app_name
        }
        return self._request('POST', 'device/set', json_data=data)
    
    def device_remove(self, device_id: str) -> Dict:
        """移除单个设备的状态"""
        return self._request('GET', 'device/remove', params={'id': device_id})
    
    def device_clear(self) -> Dict:
        """清除所有设备的状态"""
        return self._request('GET', 'device/clear')
    
    def device_private_mode(self, is_private: bool) -> Dict:
        """设置隐私模式"""
        return self._request('GET', 'device/private_mode', params={'private': str(is_private).lower()})
    
    # ------ Storage APIs ------
    
    def reload_config(self) -> Dict:
        """重新从 config.jsonc 加载配置"""
        return self._request('GET', 'reload_config')
    
    def save_data(self) -> Dict:
        """保存内存中的状态信息到 data.json"""
        return self._request('GET', 'save_data')


class SimplePrinter:
    """当无法使用 PrettyTable 时的简单格式化打印替代品"""
    
    @staticmethod
    def print_table(headers, rows, title=None):
        """打印简单的表格"""
        if title:
            print(f"\n=== {title} ===")
        
        # 计算每列的最大宽度
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # 打印表头
        header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        print(header_line)
        print("-" * len(header_line))
        
        # 打印数据行
        for row in rows:
            row_str = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            print(row_str)
    
    @staticmethod
    def print_dict(data, title=None):
        """打印字典数据"""
        if title:
            print(f"\n=== {title} ===")
        
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")


class SleepyManagerCLI:
    """改进的命令行界面，支持参数解析和表格显示"""
    
    def __init__(self):
        """初始化 CLI"""
        self.manager = SleepyManager(SERVER, SECRET, RETRY)
        self.parser = argparse.ArgumentParser(description='Sleepy 服务管理工具')
        self.setup_commands()
        
    def setup_commands(self):
        """设置命令行参数"""
        subparsers = self.parser.add_subparsers(dest='command', help='可用命令')
        
        # 查询当前状态
        subparsers.add_parser('query', help='获取当前状态')
        
        # 获取状态列表
        subparsers.add_parser('status_list', help='获取可用状态列表')
        
        # 获取统计信息
        subparsers.add_parser('metrics', help='获取统计信息')
        
        # 设置状态
        set_status_parser = subparsers.add_parser('set_status', help='设置当前状态')
        set_status_parser.add_argument('status_id', type=int, help='状态ID（数字）')
        
        # 设置设备
        device_set_parser = subparsers.add_parser('device_set', help='设置设备状态')
        device_set_parser.add_argument('device_id', help='设备ID')
        device_set_parser.add_argument('show_name', help='显示名称')
        device_set_parser.add_argument('using', choices=['true', 'false'], help='是否使用 (true/false)')
        device_set_parser.add_argument('app_name', help='应用名称')
        
        # 移除设备
        device_remove_parser = subparsers.add_parser('device_remove', help='移除设备')
        device_remove_parser.add_argument('device_id', help='设备ID')
        
        # 清除设备
        subparsers.add_parser('device_clear', help='清除所有设备')
        
        # 隐私模式
        private_parser = subparsers.add_parser('private_mode', help='设置隐私模式')
        private_parser.add_argument('status', choices=['true', 'false'], help='隐私模式状态 (true/false)')
        
        # 重载配置
        subparsers.add_parser('reload_config', help='重新加载配置文件')
        
        # 保存数据
        subparsers.add_parser('save_data', help='保存数据到文件')
        
        # 退出
        subparsers.add_parser('exit', help='退出程序')
    
    def handle_query(self, args):
        """处理 query 命令"""
        try:
            result = self.manager.query()
            
            # 显示原始 JSON（如果开启）
            if SHOW_RAW_JSON:
                print("\n=== 原始 JSON 响应 ===")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            
            print("\n=== 当前状态信息 ===")
            
            # 根据是否可用 PrettyTable 选择显示方式
            if PRETTYTABLE_AVAILABLE:
                # 状态信息表
                status_table = PrettyTable(["字段", "值"])
                status_table.align = "l"
                status_table.add_row(["状态ID", result['status']])
                status_table.add_row(["状态名称", result['info']['name']])
                status_table.add_row(["状态描述", result['info']['desc']])
                status_table.add_row(["状态颜色", result['info']['color']])
                status_table.add_row(["当前时间", result['time']])
                status_table.add_row(["时区", result['timezone']])
                status_table.add_row(["最后更新", result['last_updated']])
                print(status_table)
                
                # 设备信息表
                if result['device']:
                    print("\n=== 设备信息 ===")
                    device_table = PrettyTable(["设备ID", "显示名称", "状态", "应用名称"])
                    device_table.align = "l"
                    for device_id, device_info in result['device'].items():
                        device_table.add_row([
                            device_id,
                            device_info['show_name'],
                            "使用中" if device_info['using'] else "未使用",
                            device_info['app_name'] if device_info['using'] else "-"
                        ])
                    print(device_table)
                else:
                    print("\n没有设备信息")
            else:
                # 使用 SimplePrinter 替代 PrettyTable
                # 状态信息
                status_data = [
                    ["状态ID", result['status']],
                    ["状态名称", result['info']['name']],
                    ["状态描述", result['info']['desc']],
                    ["状态颜色", result['info']['color']],
                    ["当前时间", result['time']],
                    ["时区", result['timezone']],
                    ["最后更新", result['last_updated']]
                ]
                SimplePrinter.print_table(["字段", "值"], status_data)
                
                # 设备信息
                if result['device']:
                    print("\n=== 设备信息 ===")
                    device_rows = []
                    for device_id, device_info in result['device'].items():
                        device_rows.append([
                            device_id,
                            device_info['show_name'],
                            "使用中" if device_info['using'] else "未使用",
                            device_info['app_name'] if device_info['using'] else "-"
                        ])
                    SimplePrinter.print_table(["设备ID", "显示名称", "状态", "应用名称"], device_rows)
                else:
                    print("\n没有设备信息")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_status_list(self, args):
        """处理 status_list 命令"""
        try:
            result = self.manager.status_list()
            
            # 显示原始 JSON（如果开启）
            if SHOW_RAW_JSON:
                print("\n=== 原始 JSON 响应 ===")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            
            print("\n=== 可用状态列表 ===")
            
            if PRETTYTABLE_AVAILABLE:
                table = PrettyTable(["ID", "名称", "描述", "颜色"])
                table.align = "l"
                
                for status in result:
                    table.add_row([
                        status['id'],
                        status['name'],
                        status['desc'],
                        status['color']
                    ])
                print(table)
            else:
                # 使用 SimplePrinter
                rows = []
                for status in result:
                    rows.append([
                        status['id'],
                        status['name'],
                        status['desc'],
                        status['color']
                    ])
                SimplePrinter.print_table(["ID", "名称", "描述", "颜色"], rows)
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_metrics(self, args):
        """处理 metrics 命令"""
        try:
            result = self.manager.metrics()
            
            if not result:
                print("无统计数据")
                return
                
            print("\n=== 统计信息 ===")
            
            # 处理基本统计信息
            if 'basic' in result:
                if PRETTYTABLE_AVAILABLE:
                    basic_table = PrettyTable(["指标", "值"])
                    basic_table.align = "l"
                    for key, value in result['basic'].items():
                        basic_table.add_row([key, value])
                    print(basic_table)
                else:
                    SimplePrinter.print_dict(result['basic'], title="基本统计信息")
            
            # 处理详细统计信息
            if 'detailed' in result:
                print("\n=== 详细统计 ===")
                for category, items in result['detailed'].items():
                    print(f"\n-- {category} --")
                    if PRETTYTABLE_AVAILABLE:
                        detailed_table = PrettyTable(["项目", "计数"])
                        detailed_table.align = "l"
                        for key, value in items.items():
                            detailed_table.add_row([key, value])
                        print(detailed_table)
                    else:
                        rows = [[key, value] for key, value in items.items()]
                        SimplePrinter.print_table(["项目", "计数"], rows, title=category)
                    
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_set_status(self, args):
        """处理 set_status 命令"""
        try:
            result = self.manager.set_status(args.status_id)
            print(f"状态已更新为 ID: {args.status_id}")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_device_set(self, args):
        """处理 device_set 命令"""
        try:
            using = args.using.lower() in ('true', 't', 'yes', 'y', '1')
            result = self.manager.device_set(args.device_id, args.show_name, using, args.app_name)
            print(f"设备 {args.device_id} 状态已更新")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_device_remove(self, args):
        """处理 device_remove 命令"""
        try:
            result = self.manager.device_remove(args.device_id)
            print(f"设备 {args.device_id} 已移除")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_device_clear(self, args):
        """处理 device_clear 命令"""
        try:
            result = self.manager.device_clear()
            print("所有设备已清除")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_private_mode(self, args):
        """处理 private_mode 命令"""
        try:
            is_private = args.status.lower() in ('true', 't', 'yes', 'y', '1')
            result = self.manager.device_private_mode(is_private)
            status_text = "启用" if is_private else "禁用"
            print(f"隐私模式已{status_text}")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_reload_config(self, args):
        """处理 reload_config 命令"""
        try:
            result = self.manager.reload_config()
            print("配置已重新加载")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def handle_save_data(self, args):
        """处理 save_data 命令"""
        try:
            result = self.manager.save_data()
            print("数据已保存")
            print(f"响应: {result['success']} - {result['code']}")
        except Exception as e:
            print(f"错误: {e}")
    
    def run(self):
        """运行命令行界面"""
        print("欢迎使用 Sleepy 服务管理工具")
        print(f"服务器: {SERVER}")
        print("输入命令或 'help' 获取帮助，输入 'exit' 退出")
        
        while True:
            try:
                cmd_line = input("\n> ").strip()
                if not cmd_line:
                    continue
                    
                # 将用户输入拆分成参数列表，支持引号内的空格
                args = shlex.split(cmd_line)
                
                # 如果是退出命令，直接处理
                if args[0].lower() == 'exit':
                    print("再见!")
                    break
                    
                # 显示帮助
                if args[0].lower() == 'help':
                    self.parser.print_help()
                    continue
                    
                # 解析参数并执行对应的处理函数
                try:
                    parsed_args = self.parser.parse_args(args)
                    command = parsed_args.command
                    
                    # 调用对应的处理函数
                    handler_name = f"handle_{command}"
                    if hasattr(self, handler_name):
                        getattr(self, handler_name)(parsed_args)
                    else:
                        print(f"错误: 未知命令 '{command}'")
                        self.parser.print_help()
                except SystemExit:
                    # argparse 在遇到 -h/--help 或参数错误时会调用 sys.exit()
                    # 我们捕获这个异常以避免程序退出
                    pass
                    
            except KeyboardInterrupt:
                print("\n已中断")
                break
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    cli = SleepyManagerCLI()
    cli.run()