# AIgile

[中文文档](README-zh.md)

AIgile is runnable Agentic SDLC infrastructure that connects Hermes to DIAL through LiteLLM. It provides GitHub webhook automation, a Dashboard, and Kanban for human oversight.

```text
GitHub Issue / PR → Hermes → LiteLLM → DIAL
                            ↓
                 Dashboard / Kanban (human oversight)
```

For complete deployment instructions, see [deploy/README.md](deploy/README.md).

## Project Structure

```text
AIgile/
├── deploy/                         # Docker deployment, runtime scripts, and guides
│   ├── docker-compose.yml           # LiteLLM, Hermes, and Cloudflared services
│   ├── Dockerfile                   # LiteLLM Proxy image
│   ├── bootstrap-hermes.py          # Renders the Hermes runtime configuration
│   ├── README.md                    # English deployment guide
│   ├── README-zh.md                 # Chinese deployment guide
│   └── skills/                      # Project Skills mounted into Hermes
├── prompts/                         # GitHub webhook prompt bodies
│   ├── github-pr.md
│   └── github-issue.md
├── settings/                        # User-managed configuration and environment values
│   ├── .env.example                 # Environment-variable template; copy to .env
│   ├── hermes-config.yaml           # Hermes, Kanban, and webhook configuration source
│   ├── litellm-config.yaml          # Default LiteLLM model routes
│   └── litellm-config.copilot.yaml  # Optional GitHub Copilot model routes
├── skills/                          # Shared Skill documentation and templates
│   ├── README.md
│   └── README-zh.md
├── README.md                        # This English overview
└── README-zh.md                     # Chinese overview
```

## Quick Start

1. Copy [settings/.env.example](settings/.env.example) to `settings/.env` and set the required credentials.
2. Start the Hermes profile as described in [deploy/README.md](deploy/README.md).
3. Open the Dashboard at http://localhost:9119.

Runtime configuration and OAuth tokens are stored outside the repository under `%USERPROFILE%\.hermes-dial` by default.
