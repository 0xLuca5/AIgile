# AIgile Deployment

[中文](README-zh.md)

This is the runnable infrastructure for [Agentic SDLC](../../../README.md). It connects Hermes to DIAL through Docker and provides GitHub webhooks, a dashboard, and Kanban. See the repository README for the product vision and human/agent responsibilities; this page covers deployment and operations only.

```text
GitHub Issue / PR → Hermes → LiteLLM → DIAL
                            ↓
                 Dashboard / Kanban (human oversight)
```

> Run the commands below from the repository root.

## Configuration

The files users normally edit are in [settings](../settings):

| File | Purpose |
| --- | --- |
| [settings/.env.example](../settings/.env.example) | Template for secrets and Dashboard credentials. Copy it to `settings/.env` and fill in the values. |
| [settings/litellm-config.yaml](../settings/litellm-config.yaml) | DIAL model configuration. |
| [settings/hermes-config.yaml](../settings/hermes-config.yaml) | Hermes, Kanban, webhook routes, and prompts. |
| [prompts](../prompts) | Prompt bodies used by GitHub webhook routes. |
| [skills](skills) | Custom Skills for Hermes. Each Skill has its own directory with a `SKILL.md` file. |

The runtime and container files in [deploy](.) normally do not need changes.

Copy `settings/.env.example` to `settings/.env` and provide the following values:

```dotenv
DIAL_API_KEY=your-DIAL-key
LITELLM_MASTER_KEY=a-long-random-string
GITHUB_WEBHOOK_SECRET=a-long-random-string
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=a-strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=a-long-random-string
```

The default model is `dial-gpt-5`; change it in [settings/litellm-config.yaml](../settings/litellm-config.yaml).

## Components and Ports

| Service | Runtime | Purpose |
| --- | --- | --- |
| `litellm-proxy` | Always running | Provides an OpenAI-compatible API and forwards Hermes requests to DIAL. |
| `hermes-init` | One-time | Generates Hermes runtime configuration and the Dashboard password hash. `Exited (0)` means success. |
| `hermes` | Long-running | Runs the Hermes Gateway, webhooks, Dashboard, and Kanban. |
| `cloudflared` | Optional | Provides a temporary public HTTPS URL for local webhook development. |

All ports bind to `127.0.0.1` by default and can only be reached from the Docker host:

| Port | Purpose |
| --- | --- |
| `4000` | LiteLLM API: `http://localhost:4000/v1` |
| `8642` | Hermes Gateway API |
| `8644` | GitHub webhook; health check: `http://localhost:8644/health` |
| `9119` | Dashboard / Kanban: `http://localhost:9119` |

[docker-compose.yml](docker-compose.yml), [Dockerfile](Dockerfile), and [bootstrap-hermes.py](bootstrap-hermes.py) are runtime files. Use an SSH or Tailscale tunnel for remote Dashboard access instead of exposing port `9119` directly.

## Deployment

### Local deployment

Use this for local chat, Dashboard, Kanban, or a server that already has a public reverse proxy. This mode does **not** make GitHub webhooks publicly reachable.

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes up -d --build
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes ps
```

`litellm-proxy` and `hermes` should be running, while `hermes-init` should show `Exited (0)`.

### Configure GitHub webhooks

To trigger PR reviews or create Kanban tasks from GitHub Issues, add webhooks under your GitHub repository's **Settings → Webhooks**. The payload URL must be an HTTPS endpoint that GitHub can reach. For local development, use the optional Cloudflared tunnel below; on a server, use an existing domain and reverse proxy.

```text
https://<random-name>.trycloudflare.com/webhooks/github-pr
```

To create Kanban tasks from Issues, add a second webhook:

```text
https://<random-name>.trycloudflare.com/webhooks/github-issue
```

The secret for both webhooks must match `GITHUB_WEBHOOK_SECRET` in `settings/.env`.

### Optional: enable Cloudflared

Enable Cloudflared only for local development when no existing public HTTPS endpoint is available. It creates a temporary HTTPS URL that forwards to Hermes on port `8644`.

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes --profile tunnel up -d --build
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes --profile tunnel logs -f cloudflared
```

The logs will include a URL like:

```text
Your quick Tunnel has been created!
https://<random-name>.trycloudflare.com
```

Replace `<random-name>.trycloudflare.com` in the webhook URLs above. The temporary URL changes whenever Cloudflared restarts, so update the GitHub webhook configuration accordingly. A `404` at the tunnel root is expected; verify the tunnel at `https://<random-name>.trycloudflare.com/health`.

Stop only Cloudflared without affecting Hermes:

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile tunnel stop cloudflared
```

## Usage

Open a Hermes terminal:

```sh
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes exec hermes hermes
```

## Dashboard and Kanban

Open http://localhost:9119 and sign in with the Dashboard credentials in `.env`.

After changing the Dashboard username or password in `.env`, regenerate the runtime configuration:

```powershell
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes down
Remove-Item "$env:USERPROFILE\.hermes-dial\.dial-litellm-initialized" -ErrorAction SilentlyContinue
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes up -d
```

If `HERMES_DATA_DIR` is set, remove `.dial-litellm-initialized` from that directory instead.

## Custom Skills

The [skills](skills) directory beside this Compose file is mounted read-only in the Hermes container at `/opt/dial/skills` and automatically discovered through `skills.external_dirs`. Create each Skill with this structure:

```text
deploy/skills/
└── <skill-name>/
    └── SKILL.md
```

After changing [settings/hermes-config.yaml](../settings/hermes-config.yaml), reinitialize the runtime configuration: stop the services, remove `.dial-litellm-initialized` from `HERMES_DATA_DIR`, then start the services again. After only adding or changing files under [skills](skills), restart the `hermes` service to reload the directory.

## Troubleshooting and Shutdown

```sh
# Logs
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes logs --tail 100 hermes
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes logs --tail 100 hermes-init
docker compose --env-file settings/.env -f deploy/docker-compose.yml logs --tail 100 litellm-proxy

# Shutdown
docker compose --env-file settings/.env -f deploy/docker-compose.yml --profile hermes down
```

Hermes runtime data is stored in `%USERPROFILE%\.hermes-dial` by default and is not committed to the repository.
