# Hermes Skills

[English](README.md)

此目录用于存放项目共享的 Hermes 自定义 Skills。每个 Skill 必须位于独立的子目录中，并以 `SKILL.md` 作为入口文件。

## 目录结构

```text
skills/
├── README.md
├── README-zh.md
└── <skill-name>/
    ├── SKILL.md
    ├── references/    # 可选：按需加载的参考资料
    ├── templates/     # 可选：输出模板
    ├── scripts/       # 可选：辅助脚本
    ├── examples/      # 可选：示例
    └── assets/        # 可选：其他资源
```

`<skill-name>` 使用小写字母、数字和连字符，例如 `release-runbook` 或 `github-triage`。

## `SKILL.md` 最小示例

```markdown
---
name: release-runbook
description: 执行项目发布前检查与发布后验证
version: 1.0.0
metadata:
  hermes:
    tags: [release, operations]
    category: devops
---

# Release Runbook

## When to Use

在准备发布或验证发布结果时使用。

## Procedure

1. 检查发布前置条件。
2. 执行发布步骤。
3. 验证服务状态与关键功能。

## Verification

记录验证结果及需要人工确认的事项。
```

## 使用方式

Hermes 会扫描已配置的外部 Skills 目录。新增或修改 Skill 后，重启 `hermes` 服务，并在聊天中使用 `/<skill-name>` 加载该 Skill。

将 Skills 作为代码评审的一部分维护；不要在 Skill 中写入密钥、令牌或未经审查的破坏性命令。