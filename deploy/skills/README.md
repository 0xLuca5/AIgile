# Hermes Skills

[中文](README-zh.md)

This directory contains project-specific Hermes Skills mounted into the Hermes container at `/opt/dial/skills`.

Create each Skill in its own directory, with `SKILL.md` as the entry point:

```text
skills/
├── README.md
├── README-zh.md
└── <skill-name>/
    └── SKILL.md
```

Use lowercase letters, numbers, and hyphens for `<skill-name>`, such as `release-runbook` or `github-triage`. After adding or changing a Skill, restart the `hermes` service and load it with `/<skill-name>` in chat.

Do not include secrets, tokens, or unreviewed destructive commands in a Skill.
