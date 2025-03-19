# 更新

- [更新](#更新)
  - [手动部署](#手动部署)
  - [Huggingface 部署](#huggingface-部署)

## 手动部署

先运行这两行命令:

```bash
git pull # 拉取最新代码
pip install -r requirements.txt # 安装依赖 (如果有新的)
```

更新完成，启动即可.

> 如有自定义需求，可以 [在这](https://github.com/wyf9/sleepy/commits/main/.env.example) 查看 [`.env.example`](../.env.example) 更新记录，并相应修改 `.env`

## Huggingface 部署

1. `Settings` ==> `Variables and secrets` ==> **更改对应的新增配置项**
2. `Settings` ==> `Factory rebuild` ==> **完全重新部署**
