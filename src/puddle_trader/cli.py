"""tradebot CLI 진입점.

구현: init / auth test / favorites / backfill / data status / backtest.
스텁: watch 및 학습 루프 명령. 실주문 명령은 아직 없다 (기본 모드는 paper).
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
        raise typer.Exit(code=1) from None


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


# --- 백필 / 백테스트 (PROFIT_PLAN.md 1~3단계) ---
data_app = typer.Typer(help="수집 데이터 현황")
app.add_typer(data_app, name="data")


def _db_path() -> str:
    return AppConfig.load().app.get("database_path", "data/tradebot.sqlite")


def _open_db():
    from .db.database import connect

    path = _db_path()
    init_db(path)   # 스키마/마이그레이션을 최신으로 맞춘다
    return connect(path)


def _print_coverage(conn) -> None:
    from .db import repository as repo

    rows = repo.candle_coverage(conn, "1m")
    if not rows:
        typer.echo("[DATA] 1분봉 없음 — `tradebot backfill` 을 먼저 실행하세요.")
        return
    typer.echo("[DATA] 1분봉 보유 현황")
    for r in rows:
        typer.echo(
            f"  {r['symbol_id']:<12} {(r['security_type'] or '?'):<6} "
            f"{r['days']:>4}거래일 {r['bars']:>7}봉  "
            f"{r['first_ts'][:16]} ~ {r['last_ts'][:16]}  {r['name'] or ''}"
        )


@data_app.command("status")
def data_status() -> None:
    """종목별 1분봉 보유 범위(거래일 수)를 출력한다."""
    conn = _open_db()
    _print_coverage(conn)
    conn.close()


@app.command()
def backfill(
    interval: str = typer.Option("1m", "--interval", help="1m 또는 1d"),
    days: int = typer.Option(0, "--days", help="최근 N일까지만 (0 = API 가 주는 끝까지)"),
    symbol: list[str] = typer.Option(
        None, "--symbol", help="추가 종목 (예: KR:069500), 반복 가능"
    ),
    max_pages: int = typer.Option(1000, "--max-pages", help="종목당 최대 페이지(200봉/페이지)"),
) -> None:
    """관심종목의 과거 캔들을 받아 DB 에 쌓는다 (백테스트용 기존 데이터 확보)."""
    from datetime import datetime, timedelta

    from .api import TossApiError, TossClient
    from .api.endpoints import MarketData, StockInfo
    from .collect.backfill import backfill_symbol
    from .db import repository as repo

    if interval not in ("1m", "1d"):
        typer.echo("interval 은 1m 또는 1d 만 가능합니다.")
        raise typer.Exit(code=1)
    targets = [
        (s["market"], s["code"], s.get("name"))
        for s in _load_favorites()["symbols"] if s.get("enabled", True)
    ]
    for extra in symbol or []:
        market, _, code = extra.partition(":")
        if not code:
            typer.echo(f"형식 오류: {extra} (KR:069500 처럼 입력)")
            raise typer.Exit(code=1)
        if (market, code) not in [(m, c) for m, c, _ in targets]:
            targets.append((market, code, None))
    if not targets:
        typer.echo("대상 종목이 없습니다. `tradebot favorites add` 로 등록하세요.")
        raise typer.Exit(code=1)

    since = datetime.now(repo.KST) - timedelta(days=days) if days > 0 else None
    conn = _open_db()
    try:
        with TossClient(Credentials.from_env()) as client:
            md = MarketData(client)
            # 종목 유형(주식/ETF)은 비용 모델을 가르므로 함께 저장한다.
            try:
                codes = [c for _, c, _ in targets]
                infos = {i["symbol"]: i for i in StockInfo(client).stocks(codes)}
            except TossApiError as exc:
                typer.echo(f"[WARN] 종목 정보 조회 실패 — 유형 미상으로 진행: {exc}")
                infos = {}
            for market, code, name in targets:
                info = infos.get(code, {})
                repo.ensure_symbol(conn, market, code, info.get("name") or name,
                                   info.get("securityType"))
                conn.commit()
                try:
                    r = backfill_symbol(md, conn, market, code, interval,
                                        max_pages=max_pages, since=since)
                except TossApiError as exc:
                    typer.echo(f"[FAIL] {market}:{code} {exc}")
                    continue
                end = "API 끝까지 받음" if r.exhausted else "중단(기간/페이지 한도)"
                typer.echo(
                    f"[BACKFILL] {r.symbol_id} +{r.inserted}봉 ({r.pages}페이지) "
                    f"{(r.oldest or '-')[:16]} ~ {(r.newest or '-')[:16]}  {end}"
                )
    except RuntimeError as exc:   # 자격증명 미설정
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(code=1) from None
    if interval == "1m":
        _print_coverage(conn)
    conn.close()


def _fmt_metrics(m: dict) -> str:
    if m["n"] == 0:
        return "거래 0회"
    return (
        f"거래 {m['n']}회 | 기대값 {m['expectancy']:+.3%}/회 "
        f"(90% 구간 {m['ci_low']:+.3%} ~ {m['ci_high']:+.3%}) | "
        f"수익 마감 {m['positive_rate']:.0%} | "
        f"평균 익 {m['avg_win']:+.3%} / 손 {m['avg_loss']:+.3%} | "
        f"최대 연속손실 {m['max_consec_loss']} | 최대낙폭 {m['max_drawdown']:.2%}"
    )


def _fmt_combo(c: dict) -> str:
    return (
        f"TP {c['take_profit_rate']:+.1%} SL {c['stop_loss_rate']:+.1%} "
        f"하락 {c['max_drop_rate']:.1%}~{c['min_drop_rate']:.1%} "
        f"장초반 {c['skip_open_minutes']}분 제외 장세필터 {'on' if c['market_filter'] else 'off'}"
    )


@app.command()
def backtest(
    grid: bool = typer.Option(False, "--grid", help="가설 그리드 + 표본 외 검증"),
    save: bool = typer.Option(True, "--save/--no-save", help="결과를 DB 에 기록"),
    top: int = typer.Option(5, "--top", help="그리드 상위 N개 출력"),
) -> None:
    """DB 의 과거 1분봉으로 웅덩이 전략을 리플레이한다 (실주문 없음)."""
    import uuid

    from .backtest import engine, runner
    from .db import repository as repo
    from .strategy.detector import DetectorParams

    cfg = AppConfig.load()
    costs_cfg = cfg.strategy.get("costs")
    det = DetectorParams.from_config(cfg.strategy)
    ex = engine.ExitParams.from_config(cfg.strategy)
    session = engine.SessionParams.from_config(cfg.strategy)
    limits = engine.LimitParams.from_config(cfg.risk)

    conn = _open_db()
    data, costs, groups = runner.load_data(conn, costs_cfg)
    if not data:
        typer.echo("[BACKTEST] 1분봉이 없습니다. `tradebot backfill` 을 먼저 실행하세요.")
        conn.close()
        raise typer.Exit(code=1)
    days = runner.all_days(data)
    typer.echo(f"[BACKTEST] 종목 {len(data)}개, {len(days)}거래일 ({days[0]} ~ {days[-1]})")
    if len(days) < 20:
        typer.echo("  주의: 20거래일 미만이라 결과를 신뢰하기 어렵습니다.")

    def _save(label, split, combo, m, trades):
        if not save:
            return
        run_id = f"bt_{uuid.uuid4().hex[:12]}"
        repo.insert_backtest_run(
            conn, run_id, label,
            runner.params_snapshot(det, ex, session, limits, costs_cfg, combo),
            split, str(days[0]), str(days[-1]), m, [t.to_dict() for t in trades],
        )
        conn.commit()
        typer.echo(f"  저장: backtest_runs.id = {run_id}")

    if not grid:
        res = runner.run_single(data, costs, groups, det, ex, session, limits)
        typer.echo(f"설정: {_fmt_combo(res['combo'])}")
        for group, g in res["groups"].items():
            typer.echo(f"\n[{group}] 종목 {len(g['symbols'])}개 / {g['days']}거래일")
            typer.echo(f"  {_fmt_metrics(g['metrics'])}")
            _save("single", f"all:{group}", res["combo"], g["metrics"], g["trades"])
    else:
        bt_cfg = cfg.strategy.get("backtest")
        res = runner.run_grid(data, costs, groups, det, ex, session, limits, bt_cfg)
        if not res["market_filter_available"]:
            typer.echo("  참고: 지수 대용 종목의 1분봉이 없어 장세 필터 조합은 건너뜁니다.")
        typer.echo(f"가설 조합 {res['n_combos']}개")
        for group, g in res["groups"].items():
            typer.echo(
                f"\n[{group}] 종목 {len(g['symbols'])}개 / 표본 내 {g['train_days']}일, "
                f"표본 외 {g['test_days']}일"
            )
            typer.echo("  표본 내 상위:")
            for row in g["rows"][:top]:
                typer.echo(f"    {_fmt_combo(row['combo'])}")
                typer.echo(f"      {_fmt_metrics(row['in_sample'])}")
            best = g["best"]
            if best:
                typer.echo(f"  선택: {_fmt_combo(best['combo'])}")
                typer.echo(f"  표본 외: {_fmt_metrics(best['out_of_sample'])}")
                _save("grid", f"out_of_sample:{group}", best["combo"],
                      best["out_of_sample"], best["trades"])
            verdict = "통과" if g["passed"] else "미통과"
            why = "" if g["passed"] else f" — {'; '.join(g['reasons'])}"
            typer.echo(f"  판정: {verdict}{why}")
        typer.echo(
            "\n통과 = 표본 외 기대값과 신뢰구간 하한이 모두 양수. "
            "미통과면 실거래로 가지 않는다 (docs/PROFIT_PLAN.md)."
        )
    conn.close()


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
