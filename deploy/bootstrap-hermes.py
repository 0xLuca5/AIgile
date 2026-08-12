"""Render the tracked Hermes configuration into persistent runtime state."""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def require_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        print(f"{name} must be set in .env", file=sys.stderr)
        raise SystemExit(1)
    return value


def read_prompt(path: Path, placeholder: str) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as error:
        print(f"Prompt file for {placeholder} is missing: {path}", file=sys.stderr)
        raise SystemExit(1) from error


def main() -> None:
    master_key = require_env("LITELLM_MASTER_KEY")
    require_env("GITHUB_WEBHOOK_SECRET")
    dashboard_username = require_env("HERMES_DASHBOARD_BASIC_AUTH_USERNAME")
    dashboard_password = require_env("HERMES_DASHBOARD_BASIC_AUTH_PASSWORD")
    default_model = os.environ.get("HERMES_DEFAULT_MODEL", "dial-gpt-5")

    try:
        from plugins.dashboard_auth.basic import hash_password
    except ImportError as error:
        print(
            f"Unable to load Hermes Dashboard password authentication: {error}",
            file=sys.stderr,
        )
        raise SystemExit(1) from error

    data_dir = Path("/opt/data")
    source = Path("/opt/dial/hermes-config.yaml")
    prompts_dir = Path("/opt/dial/prompts")
    target = data_dir / "config.yaml"
    marker = data_dir / ".dial-litellm-initialized"
    data_dir.mkdir(parents=True, exist_ok=True)

    if marker.exists():
        return

    if target.exists():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        shutil.copy2(target, data_dir / f"config.yaml.before-dial-bootstrap.{timestamp}")

    config = source.read_text(encoding="utf-8")
    for placeholder, filename in {
        "__GITHUB_PR_PROMPT__": "github-pr.md",
        "__GITHUB_ISSUE_PROMPT__": "github-issue.md",
    }.items():
        prompt = read_prompt(prompts_dir / filename, placeholder)
        config = config.replace(placeholder, prompt.replace("\n", "\n            "))
    config = config.replace("__LITELLM_MASTER_KEY__", master_key)
    config = config.replace("__HERMES_DEFAULT_MODEL__", default_model)
    config = config.replace("__HERMES_DASHBOARD_USERNAME__", dashboard_username)
    config = config.replace(
        "__HERMES_DASHBOARD_PASSWORD_HASH__", hash_password(dashboard_password)
    )
    target.write_text(config, encoding="utf-8")
    marker.touch()
    print("Hermes configured to use the LiteLLM DIAL proxy and Dashboard password authentication.")


if __name__ == "__main__":
    main()
