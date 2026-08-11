# Hermes Skills

[English](README.md)

此目录用于存放项目专用的 Hermes Skills，并会被挂载到 Hermes 容器的 `/opt/dial/skills`。

每个 Skill 必须位于独立子目录中，并以 `SKILL.md` 作为入口文件：

```text
skills/
├── README.md
├── README-zh.md
└── <skill-name>/
    └── SKILL.md
```

`<skill-name>` 使用小写字母、数字和连字符，例如 `release-runbook` 或 `github-triage`。新增或修改 Skill 后，重启 `hermes` 服务，并在聊天中使用 `/<skill-name>` 加载。

不要在 Skill 中写入密钥、令牌或未经审查的破坏性命令。
