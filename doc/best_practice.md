# Best Practice

## 添加访问量统计

> [!TIP]
> 请确保你启用了 metrics 功能，否则无法正常使用 <br/>
> 更精确的访问量请使用专门的统计工具 (如 [umami](https://umami.is/))

很简单，只需要在 `sleepy_page_more_text` 环境变量中添加特殊的占位符:
- `{visit_today}`: 今日的访问量 (即 `/` 的访问次数)
- `{visit_month}`: 本月的访问量
- `{visit_year}`: 本年的访问量
- `{visit_total}`: 总访问量

示例:

```ini
# .env
sleepy_page_more_text = "其他文本<br/>今日已被视奸 {visit_today} 次"
```

将会渲染为:

```text
其他文本
今日已被视奸 114 次
```
