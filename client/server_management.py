#!/usr/bin/python3
# coding:utf-8

'''
一个 python 服务器设备，个人状态管理器
依赖: requests
by @gongfuture&Claude-3.7
'''

import requests
import json
import sys
from typing import Dict, List, Union, Any, Optional

# --- config start
# 密钥
SECRET = 'YourSecretCannotGuess'
# 服务地址, 末尾不加 `/`
SERVER = 'https://example.com'
# 请求重试次数
RETRY = 3
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


class CommandLineInterface:
    """命令行界面，管理用户交互"""
    
    def __init__(self):
        """初始化 CLI"""
        self.manager = SleepyManager(SERVER, SECRET, RETRY)
        self.commands = {
            "help": self.show_help,
            "query": self.query,
            "status_list": self.status_list,
            "metrics": self.metrics,
            "set_status": self.set_status,
            "device_set": self.device_set,
            "device_remove": self.device_remove,
            "device_clear": self.device_clear,
            "private_mode": self.private_mode,
            "reload_config": self.reload_config,
            "save_data": self.save_data,
            "exit": self.exit
        }
    
    def show_help(self, *args) -> None:
        """显示帮助信息"""
        print("\n=== Sleepy 服务管理工具 ===")
        print("可用命令:")
        print("  help                             - 显示此帮助")
        print("  query                            - 获取当前状态")
        print("  status_list                      - 获取可用状态列表")
        print("  metrics                          - 获取统计信息")
        print("  set_status <状态ID>               - 设置当前状态")
        print("  device_set <设备ID> <显示名> <是否使用> <应用名>  - 设置设备状态")
        print("  device_remove <设备ID>            - 移除设备")
        print("  device_clear                     - 清除所有设备")
        print("  private_mode <true/false>        - 设置隐私模式")
        print("  reload_config                    - 重新加载配置")
        print("  save_data                        - 保存数据")
        print("  exit                             - 退出程序")
    
    def pretty_print(self, data: Any) -> None:
        """美化输出 JSON 数据"""
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def query(self, *args) -> None:
        """获取当前状态"""
        try:
            result = self.manager.query()
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def status_list(self, *args) -> None:
        """获取可用状态列表"""
        try:
            result = self.manager.status_list()
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def metrics(self, *args) -> None:
        """获取统计信息"""
        try:
            result = self.manager.metrics()
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def set_status(self, *args) -> None:
        """设置当前状态"""
        if not args or not args[0].isdigit():
            print("错误: 需要提供有效的状态 ID（数字）")
            return
            
        try:
            result = self.manager.set_status(int(args[0]))
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def device_set(self, *args) -> None:
        """设置设备状态"""
        if len(args) < 4:
            print("错误: 需要提供设备ID、显示名称、是否使用和应用名称")
            return
            
        device_id = args[0]
        show_name = args[1]
        
        # 解析布尔值
        using_str = args[2].lower()
        if using_str in ('true', 't', 'yes', 'y', '1'):
            using = True
        elif using_str in ('false', 'f', 'no', 'n', '0'):
            using = False
        else:
            print("错误: 使用状态必须是布尔值")
            return
            
        app_name = args[3]
        
        try:
            result = self.manager.device_set(device_id, show_name, using, app_name)
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def device_remove(self, *args) -> None:
        """移除设备"""
        if not args:
            print("错误: 需要提供设备 ID")
            return
            
        try:
            result = self.manager.device_remove(args[0])
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def device_clear(self, *args) -> None:
        """清除所有设备"""
        try:
            result = self.manager.device_clear()
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def private_mode(self, *args) -> None:
        """设置隐私模式"""
        if not args:
            print("错误: 需要提供隐私模式状态 (true/false)")
            return
            
        private_str = args[0].lower()
        if private_str in ('true', 't', 'yes', 'y', '1'):
            is_private = True
        elif private_str in ('false', 'f', 'no', 'n', '0'):
            is_private = False
        else:
            print("错误: 隐私状态必须是布尔值")
            return
            
        try:
            result = self.manager.device_private_mode(is_private)
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def reload_config(self, *args) -> None:
        """重新加载配置"""
        try:
            result = self.manager.reload_config()
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def save_data(self, *args) -> None:
        """保存数据"""
        try:
            result = self.manager.save_data()
            self.pretty_print(result)
        except Exception as e:
            print(f"错误: {e}")
    
    def exit(self, *args) -> None:
        """退出程序"""
        print("再见！")
        sys.exit(0)
    
    def run(self) -> None:
        """运行命令行界面"""
        print("欢迎使用 Sleepy 服务管理工具")
        print(f"服务器: {SERVER}")
        print("输入 'help' 获取帮助，输入 'exit' 退出")
        
        while True:
            try:
                cmd_line = input("\n> ").strip()
                if not cmd_line:
                    continue
                
                parts = cmd_line.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd in self.commands:
                    self.commands[cmd](*args)
                else:
                    print(f"未知命令: {cmd}")
                    self.show_help()
            except KeyboardInterrupt:
                print("\n已中断")
                break
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    cli = CommandLineInterface()
    cli.run()