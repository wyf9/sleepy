#!/usr/bin/python3
# coding:utf-8

'''
一个 python 命令行示例
依赖: requests
by @wyf9
'''

import json

import requests

# --- config start
# 密钥
SECRET = 'YourSecretCannotGuess'
# 服务地址, 末尾不加 `/`
SERVER = 'https://example.com'
# 请求重试次数
RETRY = 3
# --- config end


def get(url):
    for t1 in range(RETRY):
        t = t1 + 1
        try:
            x = requests.get(url, timeout=10)  # Added timeout
            x.raise_for_status()  # Raise HTTPError for bad responses
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
    except Exception as e:  # Catch other potential errors
        print(f"Unexpected error loading JSON: {e}")
        raise


def main():
    print(f"Using server: {SERVER}")

    print('\n---\nStatus now:')
    try:
        stnow = loadjson(f"{SERVER}/query")
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

    print('\n---\nSelect status:')
    try:
        stlst = loadjson(f"{SERVER}/status_list")
        # Use f-string and .get() for safer list printing
        status_options = [f"{n.get('id', '?')} - {n.get('name', 'Unknown')} - {n.get('desc', 'No description')}" for n in stlst]
        print("\n".join(status_options))
    except Exception as e:
        print(f"Failed to get or parse status list: {e}")
        return 1  # Exit if status list cannot be loaded

    st = input("\n> Status ID to set: ")
    try:
        ret = loadjson(f"{SERVER}/set?secret={SECRET}&status={st}")
        # Use .get() for safer dictionary access
        success = ret.get("success", "N/A")
        code = ret.get("code", "N/A")
        set_to = ret.get("set_to", "N/A")
        message = ret.get("message", "")  # Get potential error message
        print(f"success: [{success}], code: [{code}], set_to: [{set_to}] {message}")
    except Exception as e:
        print(f"Failed to set status or parse response: {e}")
        return 1  # Indicate error on failure
    return 0


if __name__ == "__main__":
    exit_code = 1  # Default exit code to error
    try:
        exit_code = main()
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except Exception as e:
        print(f"Main ERROR! {e}")
    input("\n---\nPress Enter to exit.")  # Moved here
    exit(exit_code)  # Exit with the code from main() or 1 if error occurred
