# custom_html

一个非常简单的纯前端小插件，用于展示自定义的 HTML 卡片

配置项:

- `content`: str，指定卡片的内容

比如:

```yaml
plugin:
  custom_html:
    content: |
    <b>我是粗体</b> <br/>
    我换<br/>行了 <br/>
    我没
    换行 <br/>
    <p color=red>我是红色的</p>
```
