"""tradebot CLI 진입점.

v0.1 범위: init / auth test / favorites / watch(스텁).
실주문 관련 명령은 후속 버전에서 추가한다 (기본 모드는 paper).
"""
from __future__ import annotations

from pathlib import Path

import typer
import yaml

from .config import AppConfig, Credentials
from .db import init_db

app = typer.Typer(help="Puddle Trader CLI — 토스증권 웅덩이 단타 보조 시스템")
favorites_app = typer.Typer(help="관심종목 관리")
auth_app = typer.Typer(help="인증")
app.add_typer(favorites_app, name="favorites")
app.add_typer(auth_app, name="auth")

FAVORITES_PATH = Path("config/favorites.yaml")


@app.command()
def init() -> None:
    """기본 디렉토리와 SQLite DB 를 생성한다."""
    cfg = AppConfig.load()
    for d in ("config", "data", "logs", "reports", "models", "exports"):
        Path(d).mkdir(exist_ok=True)
    db_path = cfg.app.get("database_path", "data/tradebot.sqlite")
    init_db(db_path)
    typer.echo(f"[INIT] 디렉토리 생성 완료, DB: {db_path}")


@auth_app.command("test")
def auth_test() -> None:
    """토큰 발급과 계좌 조회 가능 여부를 확인한다."""
    from .api import TossClient
    from .api.endpoints import Account

    try:
        with TossClient(Credentials.from_env()) as client:
            accounts = Account(client).accounts()
            typer.echo("[AUTH] Access token issued successfully")
            typer.echo(f"[ACCOUNT] {len(accounts)} account(s) found")
            typer.echo("[STATUS] Ready")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(code=1)


def _load_favorites() -> dict:
    if FAVORITES_PATH.exists():
        return yaml.safe_load(FAVORITES_PATH.read_text(encoding="utf-8")) or {"symbols": []}
    return {"symbols": []}


def _save_favorites(data: dict) -> None:
    FAVORITES_PATH.parent.mkdir(exist_ok=True)
    FAVORITES_PATH.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


@favorites_app.command("add")
def favorites_add(symbol: str, name: str = typer.Option("", "--name")) -> None:
    """관심종목 추가. SYMBOL 형식: KR:000660 또는 US:NVDA"""
    market, _, code = symbol.partition(":")
    if not code:
        typer.echo("형식 오류: KR:000660 처럼 입력하세요.")
        raise typer.Exit(code=1)
    data = _load_favorites()
    if any(s["code"] == code and s["market"] == market for s in data["symbols"]):
        typer.echo("이미 등록된 종목입니다.")
        raise typer.Exit()
    data["symbols"].append({"market": market, "code": code, "name": name, "enabled": True})
    _save_favorites(data)
    typer.echo(f"[ADD] {market}:{code} {name}")


@favorites_app.command("list")
def favorites_list() -> None:
    for s in _load_favorites()["symbols"]:
        flag = "on" if s.get("enabled", True) else "off"
        typer.echo(f"[{flag}] {s['market']}:{s['code']} {s.get('name', '')}")


@favorites_app.command("remove")
def favorites_remove(symbol: str) -> None:
    market, _, code = symbol.partition(":")
    data = _load_favorites()
    before = len(data["symbols"])
    data["symbols"] = [
        s for s in data["symbols"] if not (s["code"] == code and s["market"] == market)
    ]
    _save_favorites(data)
    typer.echo(f"[REMOVE] {before - len(data['symbols'])} 종목 삭제")


@app.command()
def watch(
    mode: str = typer.Option("paper", "--mode"),
    interval: str = typer.Option("10s", "--interval"),
) -> None:
    """장중 감시 (v0.1 스텁). 웅덩이 탐지/가상매매는 후속 구현."""
    typer.echo(f"[WATCH] mode={mode} interval={interval} (구현 예정)")


# --- 학습 루프 명령 (LEARNING_SYSTEM.md §9) — Phase 3~4 에서 구현 ---
model_app = typer.Typer(help="모델 레지스트리 (list/rollback)")
app.add_typer(model_app, name="model")

_TODO = "(구현 예정 — IMPLEMENTATION_PLAN Phase 4)"


@app.command()
def label(date: str = typer.Option(..., "--date", help="YYYY-MM-DD")) -> None:
    """청산 결과 라벨링 + training_examples 적재."""
    typer.echo(f"[LABEL] {date} {_TODO}")


@app.command()
def dataset(action: str = typer.Argument("build")) -> None:
    """학습 데이터셋 재구성(누수 검증 포함)."""
    typer.echo(f"[DATASET] {action} {_TODO}")


@app.command()
def train(
    target: str = typer.Option("hit_tp_before_sl", "--target"),
    algo: str = typer.Option("logreg", "--algo"),
) -> None:
    """모델 후보 학습 + 확률 보정."""
    typer.echo(f"[TRAIN] target={target} algo={algo} {_TODO}")


@app.command()
def evaluate(last: str = typer.Option("30d", "--last")) -> None:
    """워크포워드 검증 지표 출력."""
    typer.echo(f"[EVALUATE] last={last} {_TODO}")


@app.command()
def gate() -> None:
    """현재 후보 모델의 승격 게이트 통과 여부 점검."""
    typer.echo(f"[GATE] {_TODO}")


@app.command()
def promote(version: str = typer.Option(..., "--version")) -> None:
    """게이트 통과 모델을 active 로 승격."""
    typer.echo(f"[PROMOTE] {version} {_TODO}")


@app.command()
def drift() -> None:
    """성능·feature 드리프트 점검 (발동 시 auto mode 비활성화 권고)."""
    typer.echo(f"[DRIFT] {_TODO}")


@model_app.command("list")
def model_list() -> None:
    typer.echo(f"[MODEL] list {_TODO}")


@model_app.command("rollback")
def model_rollback(to: str = typer.Option(..., "--to")) -> None:
    typer.echo(f"[MODEL] rollback → {to} {_TODO}")


if __name__ == "__main__":
    app()
