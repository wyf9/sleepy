# Best Practice

## 添加访问量统计

主页: https://finicounter.eu.org/

在 `config.json` 的 `other.more_text` 中添加以下内容:

```html
<br/>本站访问次数: <span id='finicount_views'></span><script async src='https://finicounter.eu.org/finicounter.js'></script>
```

修改后应该是这样的:

```jsonc
// config.json
    // ...
    "data_check_interval": 30,
    "other": {
        // ...
        "repo": "https://github.com/wyf9/sleepy",
        "more_text": "其他文本<br/>已被视奸 <span id='finicount_views'>(未知)</span> 次<script async src='https://finicounter.eu.org/finicounter.js'></script>",
        "device_status_slice": 30
    }
}
```