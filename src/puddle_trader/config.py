"""설정 로딩: YAML 설정 + .env 자격증명."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

CONFIG_DIR = Path(os.environ.get("TRADEBOT_CONFIG_DIR", "config"))


LOCAL_OVERRIDES = "local.yaml"
"""화면(UI)에서 바꾼 설정을 담는 파일. strategy.yaml / risk.yaml 은 주석을 살리기 위해
건드리지 않고, 여기 적힌 값만 그 위에 덮어쓴다. 형식: {strategy: {...}, risk: {...}}"""


def _load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """patch 의 값으로 base 를 덮어쓴 새 dict (중첩 dict 는 재귀적으로 합친다)."""
    out = dict(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def save_local_overrides(patch: dict[str, Any]) -> None:
    """local.yaml 에 patch 를 합쳐 저장한다."""
    merged = deep_merge(_load_yaml(LOCAL_OVERRIDES), patch)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / LOCAL_OVERRIDES).write_text(
        "# 화면에서 바꾼 설정 (자동 생성). 지우면 기본값으로 돌아갑니다.\n"
        + yaml.safe_dump(merged, allow_unicode=True, sort_keys=True),
        encoding="utf-8",
    )


def _load_env() -> None:
    """.env 읽기. 화면이 키를 저장하는 곳(실행 폴더)을 먼저 보고, 없으면 위쪽 폴더에서 찾는다."""
    if Path(".env").exists():
        load_dotenv(Path(".env"))
    else:
        load_dotenv()


def credentials_present() -> bool:
    _load_env()
    return bool(os.environ.get("TOSS_CLIENT_ID")) and bool(os.environ.get("TOSS_CLIENT_SECRET"))


def save_env_values(values: dict[str, str], env_path: str | Path = ".env") -> None:
    """값들을 .env 에 저장한다 (다른 줄은 보존, 권한 600). 값은 어디에도 출력하지 않는다.

    빈 문자열을 주면 그 항목을 지운다. 줄바꿈이 든 값은 받지 않는다.
    """
    for key, value in values.items():
        if any(c in value for c in "\r\n\x00") or not key.replace("_", "").isalnum():
            raise ValueError("저장할 수 없는 값이에요")
    path = Path(env_path)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    lines = [ln for ln in lines if not ln.startswith(tuple(f"{k}=" for k in values))]
    lines += [f"{k}={v}" for k, v in values.items() if v != ""]
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(path, 0o600)
    for key, value in values.items():
        if value == "":
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def save_credentials(client_id: str, client_secret: str, env_path: str | Path = ".env") -> None:
    """API 키를 .env 에 저장한다."""
    save_env_values({"TOSS_CLIENT_ID": client_id, "TOSS_CLIENT_SECRET": client_secret}, env_path)


def load_env() -> None:
    """.env 를 읽어 환경 변수로 올린다 (이미 있는 값은 그대로)."""
    _load_env()


@dataclass
class Credentials:
    client_id: str
    client_secret: str
    account_seq: int | None = None

    @classmethod
    def from_env(cls) -> Credentials:
        _load_env()
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
    def load(cls) -> AppConfig:
        app_yaml = _load_yaml("app.yaml")
        local = _load_yaml(LOCAL_OVERRIDES)
        return cls(
            app=app_yaml.get("app", {}),
            api=app_yaml.get("api", {}),
            logging=app_yaml.get("logging", {}),
            strategy=deep_merge(_load_yaml("strategy.yaml"), local.get("strategy") or {}),
            risk=deep_merge(_load_yaml("risk.yaml"), local.get("risk") or {}),
        )
