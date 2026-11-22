"""관심종목 파일(config/favorites.yaml) 읽기·쓰기. CLI 와 화면(UI)이 함께 쓴다."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FAVORITES_PATH = Path("config/favorites.yaml")
SYMBOL_RE = re.compile(r"^[A-Za-z0-9.\-]{1,12}$")
MARKETS = ("KR", "US")


def load() -> dict[str, Any]:
    if FAVORITES_PATH.exists():
        data = yaml.safe_load(FAVORITES_PATH.read_text(encoding="utf-8")) or {}
        data.setdefault("symbols", [])
        return data
    return {"symbols": []}


def save(data: dict[str, Any]) -> None:
    FAVORITES_PATH.parent.mkdir(parents=True, exist_ok=True)
    FAVORITES_PATH.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def _find(data: dict[str, Any], market: str, code: str) -> dict[str, Any] | None:
    for s in data["symbols"]:
        if s.get("market") == market and str(s.get("code")) == code:
            return s
    return None


def add(market: str, code: str, name: str = "") -> bool:
    """추가했으면 True, 이미 있으면 False. 형식이 틀리면 ValueError."""
    market, code = market.strip().upper(), code.strip()
    if market not in MARKETS:
        raise ValueError("시장은 KR 또는 US 여야 합니다.")
    if not SYMBOL_RE.match(code):
        raise ValueError("종목 코드는 영문·숫자만 쓸 수 있어요 (예: 005930).")
    if market == "KR" and not re.fullmatch(r"\d{6}", code):
        raise ValueError("국내 종목 코드는 숫자 6자리예요 (예: 005930).")
    data = load()
    if _find(data, market, code):
        return False
    data["symbols"].append(
        {"market": market, "code": code, "name": name.strip()[:40], "enabled": True}
    )
    save(data)
    return True


def remove(market: str, code: str) -> int:
    data = load()
    before = len(data["symbols"])
    data["symbols"] = [
        s for s in data["symbols"]
        if not (s.get("market") == market and str(s.get("code")) == code)
    ]
    save(data)
    return before - len(data["symbols"])


def set_enabled(market: str, code: str, enabled: bool) -> bool:
    data = load()
    item = _find(data, market, code)
    if item is None:
        return False
    item["enabled"] = bool(enabled)
    save(data)
    return True
