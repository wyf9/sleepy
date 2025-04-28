#!/usr/bin/python3
# coding:utf-8

'''
一个 python 命令行示例 (多服务版，也就是旧的 cmd_console.py)
依赖: requests
by @wyf9
'''

import json

import requests

# --- config start
# 密钥
SECRET = '11451419-1981-0114-5141-919810114514'
# 服务列表, 末尾不加 `/`
SERVER_LIST = ['https://sleepy.wyf9.top',
               'http://114.51.41.91:9010',
               'http://127.0.0.1:9010']
# 请求重试次数
RETRY = 3
# --- config end


def get(url):
    for t1 in range(RETRY):
        t = t1 + 1
        try:
            x = requests.get(url, timeout=10)  # Added timeout
            x.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return x.text
        except requests.exceptions.RequestException as e:  # Catch specific exceptions
            print(f"Request failed: {e}. Retrying... {t}/{RETRY}")
            if t >= RETRY:
                print("Max retry limit reached!")
                raise
            continue


def loadjson(url):
    raw = get(url)
    try:
        return json.loads(raw)
    except json.decoder.JSONDecodeError as e:
        print(f'Error decoding json: {e}\nRaw data:\n"""\n{raw}\n"""')
        raise
    except Exception as e:  # Catch other potential errors during loading
        print(f"Unexpected error loading JSON: {e}")
        raise


def main():
    print('\n---\nSelect Server:')
    # Use enumerate and f-string for cleaner list printing
    serverlst_show = "\n".join([f"    {i + 1}. {s}" for i, s in enumerate(SERVER_LIST)])
    print(f"""
    0. Quit
{serverlst_show}
""")
    server = None  # Initialize server variable
    while True:
        try:
            inp_str = input("> ")
            inp = int(inp_str)
            if inp == 0:
                return 0
            # Add range check for server selection
            elif 1 <= inp <= len(SERVER_LIST):
                server = SERVER_LIST[inp - 1]
                print(f'Selected server: {server}')
                break
            else:
                print(f"Invalid input. Please enter a number between 0 and {len(SERVER_LIST)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except IndexError:  # Should not happen with the check above, but good practice
            print("Invalid selection number.")

    if not server:
        print("No server selected. Exiting.")
        return 1

    print('\n---\nStatus now:')
    try:
        stnow = loadjson(f"{server}/query")
        # Use .get() for safer dictionary access
        success = stnow.get("success", "N/A")
        status = stnow.get("status", "N/A")
        info = stnow.get("info", {})
        info_name = info.get("name", "N/A")
        info_desc = info.get("desc", "N/A")
        info_color = info.get("color", "N/A")
        print(f"success: [{success}], status: [{status}], info_name: [{info_name}], info_desc: [{info_desc}], info_color: [{info_color}]")
    except Exception as e:
        print(f"Failed to get or parse current status: {e}")
        # Optionally print raw data if needed for debugging: print(f'RawData: {stnow}')

    print('\n---\nSelect status:')
    try:
        stlst = loadjson(f"{server}/status_list")
        # Use f-string and .get() for safer list printing
        status_options = [f"{n.get('id', '?')} - {n.get('name', 'Unknown')} - {n.get('desc', 'No description')}" for n in stlst]
        print("\n".join(status_options))
    except Exception as e:
        print(f"Failed to get or parse status list: {e}")
        return 1  # Exit if status list cannot be loaded

    st = input("\n> Status ID to set: ")
    try:
        ret = loadjson(f"{server}/set?secret={SECRET}&status={st}")
        # Use .get() for safer dictionary access
        success = ret.get("success", "N/A")
        code = ret.get("code", "N/A")
        set_to = ret.get("set_to", "N/A")
        message = ret.get("message", "")  # Get potential error message
        print(f"success: [{success}], code: [{code}], set_to: [{set_to}] {message}")
    except Exception as e:
        print(f"Failed to set status or parse response: {e}")
        # Optionally print raw data: print(f'RawData: {ret}')
    return 0


if __name__ == "__main__":
    exit_code = 1  # Default exit code to error
    try:
        exit_code = main()
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except Exception as e:
        print(f"Main ERROR! {e}")
    input('\n---\nPress Enter to exit.')
    exit(exit_code)  # Exit with the code from main() or 1 if error occurred
