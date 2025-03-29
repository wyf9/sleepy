# Tools

存放一些开发中使用的小工具

## [`test-request.py`](./test-request.py)

此脚本可以用来测试 api 请求哦

用法也很简单:

<details>
<summary>点击展开示例</summary>

```shell
[02:02:44 wyf9@SRserver /sync/dev/wyf9/sleepy]$ cd "/sync/dev/wyf9/sleepy/" && python req.test.py
I < p /device/set {"id": "device-1", "show_name": "MyDevice2", "using": true, "app_name": "VSCode"}
O > GET http://[::]:9011/device/set 200
{
    "success": true, 
    "code": "OK"
}
I < post /device/set {"id": "device-1", "show_name": "MyDevice2", "using": true, "app_name": "aaaaaaaaa"}
O > GET http://[::]:9011/device/set 200
{
    "success": true, 
    "code": "OK"
}
I < g /device/remove?name=device=2
O > GET http://[::]:9011/device/remove?name=device=2 200
{
    "success": false, 
    "code": "not found", 
    "message": "cannot find item"
}
I < get /device/remove?id=device-2
O > GET http://[::]:9011/device/remove?id=device-2 200
{
    "success": true, 
    "code": "OK"
}
I < g /query
O > GET http://[::]:9011/query 200
{
    "time": "2025-03-30 02:26:50", 
    "timezone": "Asia/Shanghai", 
    "success": true, 
    "status": 0, 
    "info": {
        "id": 0, 
        "name": "活着", 
        "desc": "目前在线，可以通过任何可用的联系方式联系本人。", 
        "color": "awake"
    }, 
    "device": {
        "device-2": {
            "show_name": "MyDevice1", 
            "using": false, 
            "app_name": "CustomNotUsing"
        }, 
        "device-1": {
            "show_name": "MyDevice2", 
            "using": true, 
            "app_name": "啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊"
        }, 
        "device-3": {
            "show_name": "MyDevice4", 
            "using": true, 
            "app_name": "阿米诺斯"
        }
    }, 
    "device_status_slice": 40, 
    "last_updated": "2025-03-17 17:36:32", 
    "refresh": 6000
}
I < ^C[02:26:59 wyf9@SRserver /sync/dev/wyf9/sleepy/tools]$ 
```

</details>

> *不需要自己设置 `BASE` 和 `SECRET`，会自动从 `../env.py` 获取*