# AIgile

[English](README.md)

AIgile 是可运行的 Agentic SDLC 基础设施，通过 LiteLLM 将 Hermes 接入 DIAL，并提供 GitHub Webhook 自动化、Dashboard 与 Kanban，支持人工监督。

```text
GitHub Issue / PR → Hermes → LiteLLM → DIAL
                            ↓
                 Dashboard / Kanban（人工监督）
```

完整部署说明请参阅 [deploy/README-zh.md](deploy/README-zh.md)。

## 项目结构

```text
AIgile/
├── deploy/                         # Docker 部署、运行时脚本与部署文档
│   ├── docker-compose.yml           # LiteLLM、Hermes 和 Cloudflared 服务定义
│   ├── Dockerfile                   # LiteLLM Proxy 镜像
│   ├── bootstrap-hermes.py          # 渲染 Hermes 运行时配置
│   ├── README.md                    # English 部署文档
│   ├── README-zh.md                 # 中文部署文档
│   └── skills/                      # 挂载给 Hermes 的项目 Skills
├── prompts/                         # GitHub Webhook 路由 Prompt 正文
│   ├── github-pr.md
│   └── github-issue.md
├── settings/                        # 用户可维护的配置与环境变量
│   ├── .env.example                 # 环境变量模板；复制为 .env
│   ├── hermes-config.yaml           # Hermes、Kanban 和 Webhook 配置源
│   ├── litellm-config.yaml          # 默认 LiteLLM 模型路由
│   └── litellm-config.copilot.yaml  # 可选的 GitHub Copilot 模型路由
├── skills/                          # 共享 Skill 文档与模板
│   ├── README.md
│   └── README-zh.md
├── README.md                        # 本英文说明
└── README-zh.md                     # 本中文说明
```

## 快速开始

1. 将 [settings/.env.example](settings/.env.example) 复制为 `settings/.env`，并填写所需凭据。
2. 按照 [deploy/README-zh.md](deploy/README-zh.md) 启动 Hermes 服务。
3. 在浏览器打开 http://localhost:9119 访问 Dashboard。

运行时配置与 OAuth Token 默认保存到仓库外的 `%USERPROFILE%\.hermes-dial`。
