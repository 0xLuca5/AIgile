# Hermes + DIAL

使用 Docker 通过 LiteLLM 将 Hermes 连接到 DIAL。

## 配置

复制 `.env.example` 为 `.env`，填写：

```dotenv
DIAL_API_KEY=你的DIAL密钥
LITELLM_MASTER_KEY=随机长字符串
GITHUB_WEBHOOK_SECRET=随机长字符串
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=强密码
HERMES_DASHBOARD_BASIC_AUTH_SECRET=随机长字符串
```

默认模型是 `dial-gpt-5`，可在 [litellm-config.yaml](litellm-config.yaml) 修改。

## 启动

```sh
docker compose --profile hermes up -d --build
docker compose --profile hermes ps
```

`litellm-proxy` 和 `hermes` 应为运行状态；`hermes-init` 显示 `Exited (0)` 即正常。

## 使用

打开 Hermes 终端：

```sh
docker compose --profile hermes exec hermes hermes
```

验证 DIAL 连接：

```sh
docker compose --profile hermes exec hermes hermes chat -q "Reply with exactly: DIAL connection successful"
```

## Dashboard / Kanban

访问 http://localhost:9119 ，使用 `.env` 中的 Dashboard 用户名和密码登录，再打开 **Kanban**。

| 服务 | 本机地址 |
| --- | --- |
| LiteLLM | http://localhost:4000 |
| Dashboard / Kanban | http://localhost:9119 |
| GitHub Webhook | http://localhost:8644 |

修改 `.env` 的 Dashboard 用户名或密码后，重新生成配置：

```powershell
docker compose --profile hermes down
Remove-Item "$env:USERPROFILE\.hermes-dial\.dial-litellm-initialized" -ErrorAction SilentlyContinue
docker compose --profile hermes up -d
```

如果使用 `HERMES_DATA_DIR`，请改为删除该目录中的 `.dial-litellm-initialized`。

## GitHub Webhook（可选）

在 [hermes-config.yaml](hermes-config.yaml) 修改路由和 Prompt：

- `github-pr`：输出 PR 审查摘要到 Hermes 日志。
- `github-issue`：为新建或重新打开的 Issue 创建 Kanban 任务。

修改后按上一节的方式重新生成配置。不要将密钥写入配置文件。

GitHub 需要通过 HTTPS 隧道访问本机 `8644`。Webhook URL 使用：

```text
https://你的域名/webhooks/github-pr
https://你的域名/webhooks/github-issue
```

GitHub 的 Webhook Secret 必须等于 `.env` 中的 `GITHUB_WEBHOOK_SECRET`。

## 排查与停止

```sh
# 日志
docker compose --profile hermes logs --tail 100 hermes
docker compose --profile hermes logs --tail 100 hermes-init
docker compose logs --tail 100 litellm-proxy

# 停止
docker compose --profile hermes down
```

Hermes 运行时数据默认保存在 `%USERPROFILE%\.hermes-dial`，不会提交到仓库。
