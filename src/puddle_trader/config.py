"""설정 로딩: YAML 설정 + .env 자격증명."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

CONFIG_DIR = Path(os.environ.get("TRADEBOT_CONFIG_DIR", "config"))


def _load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@dataclass
class Credentials:
    client_id: str
    client_secret: str
    account_seq: int | None = None

    @classmethod
    def from_env(cls) -> "Credentials":
        load_dotenv()
        client_id = os.environ.get("TOSS_CLIENT_ID", "")
        client_secret = os.environ.get("TOSS_CLIENT_SECRET", "")
        if not client_id or not client_secret:
            raise RuntimeError(
                "TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 가 설정되지 않았습니다. "
                ".env 파일을 확인하세요 (.env.example 참고)."
            )
        seq = os.environ.get("TOSS_ACCOUNT_SEQ")
        return cls(client_id, client_secret, int(seq) if seq else None)


@dataclass
class AppConfig:
    app: dict[str, Any] = field(default_factory=dict)
    api: dict[str, Any] = field(default_factory=dict)
    logging: dict[str, Any] = field(default_factory=dict)
    strategy: dict[str, Any] = field(default_factory=dict)
    risk: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "AppConfig":
        app_yaml = _load_yaml("app.yaml")
        return cls(
            app=app_yaml.get("app", {}),
            api=app_yaml.get("api", {}),
            logging=app_yaml.get("logging", {}),
            strategy=_load_yaml("strategy.yaml"),
            risk=_load_yaml("risk.yaml"),
        )
