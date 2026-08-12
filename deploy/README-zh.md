# AIgile

[English](README.md)

这是 [Agentic SDLC](../../../README-zh.md) 的可运行基础设施：通过 Docker 将 Hermes 接入 DIAL，并提供 GitHub Webhook、Dashboard 与 Kanban。业务愿景与人机分工见项目根目录 README；本页仅说明部署与操作。

```text
GitHub Issue / PR → Hermes → LiteLLM → DIAL
			    ↓
		    Dashboard / Kanban（人工监督）
```

## 配置

用户需要修改的文件都在 [settings](settings) 目录：

| 文件 | 用途 |
| --- | --- |
| [settings/.env.example](settings/.env.example) | 密钥和 Dashboard 登录信息模板。复制为 `settings/.env` 后填写。 |
| [settings/litellm-config.yaml](settings/litellm-config.yaml) | DIAL 模型设置。 |
| [settings/litellm-config.copilot.yaml](../settings/litellm-config.copilot.yaml) | 可选的 DIAL 和 GitHub Copilot 模型设置。 |
| [settings/hermes-config.yaml](settings/hermes-config.yaml) | Hermes、Kanban、Webhook 路由和 Prompt。 |
| [prompts](../prompts) | GitHub Webhook 路由使用的 Prompt 正文。 |
| [skills](skills) | 提供给 Hermes 的自定义 Skills；每个 Skill 使用独立目录和 `SKILL.md`。 |

安装和容器运行相关文件都在 [deploy](deploy) 目录，不需要日常修改。

复制 `settings/.env.example` 为 `settings/.env`，填写：

```dotenv
DIAL_API_KEY=你的DIAL密钥
LITELLM_MASTER_KEY=随机长字符串
GITHUB_WEBHOOK_SECRET=随机长字符串
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=强密码
HERMES_DASHBOARD_BASIC_AUTH_SECRET=随机长字符串
```

默认模型是 `dial-gpt-5`，可在 [settings/litellm-config.yaml](settings/litellm-config.yaml) 修改。

## 组件与端口

| 服务 | 运行方式 | 作用 |
| --- | --- | --- |
| `litellm-proxy` | 始终运行 | 提供 OpenAI 兼容 API，并将 Hermes 请求转发到 DIAL。 |
| `hermes-init` | 一次性运行 | 生成 Hermes 运行时配置与 Dashboard 密码哈希；`Exited (0)` 表示成功。 |
| `hermes` | 持续运行 | 运行 Hermes Gateway、Webhook、Dashboard 和 Kanban。 |
| `cloudflared` | 可选 | 为本机 Webhook 提供临时公网 HTTPS 地址。 |
| `copilot-login` | 按需运行 | 在当前终端显示 GitHub Copilot 设备授权信息。 |

### 模型配置

默认使用 [settings/litellm-config.yaml](../settings/litellm-config.yaml)。你可以复制该文件并按需要维护自己的 LiteLLM `model_list`，例如添加 DIAL、GitHub Copilot 或其他 LiteLLM 支持的模型路由。

通过 `settings/.env` 中的 `LITELLM_CONFIG_PATH` 选择要挂载到 LiteLLM 容器的配置文件。路径相对于 [deploy/docker-compose.yml](docker-compose.yml) 所在目录：

```dotenv
# 默认值；不设置时也会使用此文件
LITELLM_CONFIG_PATH=../settings/litellm-config.yaml

# GitHub Copilot 示例配置
# LITELLM_CONFIG_PATH=../settings/litellm-config.copilot.yaml

# 自定义配置示例
# LITELLM_CONFIG_PATH=../settings/litellm-config.my-models.yaml

# Hermes 要请求的 model_name；必须存在于所选配置的 model_list 中
HERMES_DEFAULT_MODEL=dial-gpt-5
```

`LITELLM_CONFIG_PATH` 只决定 LiteLLM 加载哪些路由，不会自动更改 Hermes 当前使用的模型。通过 `HERMES_DEFAULT_MODEL` 选择其中一个 `model_name`；例如 Copilot 配置可设置为 `github-copilot-gpt-5.4`。

修改 `LITELLM_CONFIG_PATH`、`HERMES_DEFAULT_MODEL` 或配置文件内容后，重新生成 Hermes 配置并重新创建服务：

```powershell
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes down
Remove-Item "$env:USERPROFILE\.hermes-dial\.dial-litellm-initialized" -ErrorAction SilentlyContinue
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes up -d
```

#### GitHub Copilot 设备授权

如果选中的模型配置包含 `github_copilot/...` 路由，请先完成一次设备授权，避免 LiteLLM 健康检查等待登录而超时。链接和验证码会直接显示在当前终端：

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml run --rm copilot-login
```

打开终端显示的链接，输入验证码并完成 GitHub 授权。LiteLLM 显示已成功启动后，按 `Ctrl+C` 退出。OAuth Token 会保存到 `HERMES_DATA_DIR/litellm-copilot`，重建容器后仍可复用。

此命令特意不使用 `--build`：正常部署命令会构建同一个镜像。部分 Docker Desktop 版本会在镜像导出完成后，由 Buildx Bake 界面报出 `failed to execute bake: read |0: file already closed`。如确实需要重新构建，请在 PowerShell 中先执行以下命令，为当前终端会话关闭 Bake：

```powershell
$env:COMPOSE_BAKE = "false"
```

所有端口默认绑定到 `127.0.0.1`，只能从运行 Docker 的本机访问：

| 端口 | 用途 |
| --- | --- |
| `4000` | LiteLLM API：`http://localhost:4000/v1` |
| `8642` | Hermes Gateway API |
| `8644` | GitHub Webhook；健康检查：`http://localhost:8644/health` |
| `9119` | Dashboard / Kanban：`http://localhost:9119` |

`deploy` 中的 [docker-compose.yml](deploy/docker-compose.yml)、[Dockerfile](deploy/Dockerfile) 和 [bootstrap-hermes.py](deploy/bootstrap-hermes.py) 是运行文件；正常使用时无需修改。远程访问 Dashboard 推荐 SSH 或 Tailscale 隧道，而不是直接暴露 `9119`。

## 部署方式

### 本地部署

适用于本机聊天、Dashboard、Kanban，或已有其他公网反向代理的服务器。此方式**不会**为 GitHub 提供公网访问地址。

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes up -d
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes ps
```

`litellm-proxy` 和 `hermes` 应为运行状态；`hermes-init` 显示 `Exited (0)` 即正常。

如修改 [Dockerfile](Dockerfile) 后需要重建 LiteLLM 镜像，请在 PowerShell 中关闭 Bake 后单独构建，再不带 `--build` 启动服务：

```powershell
$env:COMPOSE_BAKE = "false"
docker compose --env-file settings/.env -f deploy/docker-compose.yml build litellm-proxy
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes up -d
```

### 配置 GitHub Webhook

如需让 GitHub 触发 PR 审查或创建 Issue Kanban 任务，必须在 GitHub 仓库 **Settings → Webhooks** 中创建 Webhook。Payload URL 必须是 GitHub 能访问的 HTTPS 公网地址：本机开发可使用下方可选的 Cloudflared；服务器部署可使用已有域名和反向代理。

```text
https://<随机名称>.trycloudflare.com/webhooks/github-pr
```

如需将 Issue 创建为 Kanban 任务，创建另一个 Webhook：

```text
https://<随机名称>.trycloudflare.com/webhooks/github-issue
```

两个 Webhook 的 Secret 都必须等于 `settings/.env` 中的 `GITHUB_WEBHOOK_SECRET`。

### 可选：启用 Cloudflared

仅在本机开发、且没有已有公网 HTTPS 地址时启用。Cloudflared 会创建临时 HTTPS 地址，并转发到 Hermes 的 `8644` 端口。

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes --profile tunnel up -d
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes --profile tunnel logs -f cloudflared
```

日志中会出现如下地址：

```text
Your quick Tunnel has been created!
https://<随机名称>.trycloudflare.com
```

将该地址替换上节 Webhook URL 中的 `<随机名称>.trycloudflare.com`。临时地址会在 Cloudflared 重启后改变，需要同步更新 GitHub Webhook。访问隧道根地址返回 `404` 是正常的；可通过 `https://<随机名称>.trycloudflare.com/health` 验证隧道。

只关闭 Cloudflared、不影响 Hermes：

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile tunnel stop cloudflared
```

## 使用

打开 Hermes 终端：

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes exec hermes hermes
```

## Dashboard / Kanban

访问 http://localhost:9119 ，使用 `.env` 中的 Dashboard 用户名和密码登录。

修改 `.env` 的 Dashboard 用户名或密码后，需要重新生成配置：

```powershell
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes down
Remove-Item "$env:USERPROFILE\.hermes-dial\.dial-litellm-initialized" -ErrorAction SilentlyContinue
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes up -d
```

如果使用 `HERMES_DATA_DIR`，请改为删除该目录中的 `.dial-litellm-initialized`。


## 排查与停止

```sh
# 日志
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes logs --tail 100 hermes
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes logs --tail 100 hermes-init
docker compose --env-file settings/.env -f deploy/docker-compose.yml logs --tail 100 litellm-proxy

# 停止
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes down
```

Hermes 运行时数据默认保存在 `%USERPROFILE%\.hermes-dial`，不会提交到仓库。

## 自定义 Skills

[skills](skills) 与 Compose 文件同级，会以只读方式挂载到 Hermes 容器的 `/opt/dial/skills`，并通过 `skills.external_dirs` 自动发现。新增 Skill 时使用如下结构：

```text
deploy/skills/
└── <skill-name>/
	└── SKILL.md
```

修改 `settings/hermes-config.yaml` 后，需要重新初始化运行时配置：先停止服务，删除 `HERMES_DATA_DIR` 中的 `.dial-litellm-initialized`，再重新启动。只新增或修改 [skills](skills) 中的文件时，重启 `hermes` 服务即可重新加载目录。
