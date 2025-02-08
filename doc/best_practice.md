# Best Practice

## 添加访问量统计

> [!TIP]
> 请确保你启用了 metrics 功能，否则无法正常使用

很简单，只需要在 `config.json` 的 `other.more_text` 中添加特殊的占位符:
- `{visit_today}`: 今日的访问量 (即 `/` 的访问次数)
- `{visit_month}`: 本月的访问量
- `{visit_year}`: 本年的访问量
- `{visit_total}`: 总访问量

示例:

```jsonc
// config.jsonc
    // ...
    "other": {
        // ...
        "more_text": "其他文本<br/>今日已被视奸 {visit_today} 次",
        // ...
    }
}
```

将会渲染为:

```text
其他文本
今日已被视奸 114 次
```


## 添加访问量统计 (Legacy)

> [!WARNING]
> 此统计站点会被刷访问量，不一定准确，故不推荐此方法

主页: https://finicounter.eu.org/

在 `config.jsonc` 的 `other.more_text` 中添加以下内容:

```html
<br/>本站访问次数: <span id='finicount_views'></span><script async src='https://finicounter.eu.org/finicounter.js'></script>
```

修改后应该是这样的:

```jsonc
// config.jsonc
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