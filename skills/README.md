# Hermes Skills

[中文说明](README-zh.md)

This directory contains project-shared custom Hermes Skills. Each Skill must live in its own subdirectory and use `SKILL.md` as its entry point.

## Directory Layout

```text
skills/
├── README.md
├── README-zh.md
└── <skill-name>/
		├── SKILL.md
		├── references/    # Optional: reference material loaded on demand
		├── templates/     # Optional: output templates
		├── scripts/       # Optional: helper scripts
		├── examples/      # Optional: examples
		└── assets/        # Optional: supporting resources
```

Use lowercase letters, numbers, and hyphens for `<skill-name>`, such as `release-runbook` or `github-triage`.

## Minimal `SKILL.md` Example

```markdown
---
name: release-runbook
description: Run pre-release checks and post-release verification
version: 1.0.0
metadata:
	hermes:
		tags: [release, operations]
		category: devops
---

# Release Runbook

## When to Use

Use when preparing a release or verifying its results.

## Procedure

1. Check release prerequisites.
2. Perform the release steps.
3. Verify service health and core functionality.

## Verification

Record the verification results and any items requiring human confirmation.
```

## Usage

Hermes scans its configured external Skill directories. After adding or changing a Skill, restart the `hermes` service and load it in chat with `/<skill-name>`.

Maintain Skills as part of code review. Do not include secrets, tokens, or unreviewed destructive commands in a Skill.
