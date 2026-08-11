# Webhook Prompts

This directory stores the prompt bodies used by the GitHub webhook routes.

| File | Route |
| --- | --- |
| `github-pr.md` | `github-pr` pull request events |
| `github-issue.md` | `github-issue` issue events |

The bootstrap process embeds these files into Hermes's rendered runtime configuration. After changing a prompt, stop the services, remove `.dial-litellm-initialized` from `HERMES_DATA_DIR`, and start the `hermes` profile again.
