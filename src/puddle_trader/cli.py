"""tradebot CLI 진입점.

구현: init / auth test / favorites / backfill / data status / backtest /
      watch(paper) / bench / latency.
스텁: 학습 루프 명령. 실주문 명령은 아직 없다 (기본 모드는 paper).
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
    mode: str = typer.Option("paper", "--mode", help="현재 paper 만 지원"),
    duration: float = typer.Option(0, "--duration", help="N초 뒤 종료 (0 = 장 마감/Ctrl-C 까지)"),
) -> None:
    """장중 감시: 가격 폴링 → 분 마감 탐지 → 가상 진입/청산. 실주문은 하지 않는다."""
    import signal as _signal
    import threading
    from datetime import datetime

    from .api import TossApiError, TossClient
    from .api.endpoints import MarketData, MarketInfo
    from .backtest import engine
    from .db import repository as repo
    from .realtime.scanner import Scanner, SymbolSpec
    from .strategy.detector import DetectorParams

    if mode != "paper":
        typer.echo("현재는 paper 모드만 지원합니다 (실주문 미구현).")
        raise typer.Exit(code=1)
    cfg = AppConfig.load()
    rt = cfg.strategy.get("realtime", {})
    favorites = [x for x in _load_favorites()["symbols"]
                 if x.get("enabled", True) and x["market"] == "KR"]
    if not favorites:
        typer.echo("KR 관심종목이 없습니다. `tradebot favorites add KR:000660` 로 등록하세요.")
        raise typer.Exit(code=1)
    conn = _open_db()
    rows = conn.execute("SELECT id, security_type FROM symbols")
    known = {r["id"]: r["security_type"] for r in rows}
    specs = [
        SymbolSpec(x["market"], x["code"], x.get("name"),
                   known.get(repo.symbol_id(x["market"], x["code"])))
        for x in favorites
    ]
    unknown = [sp.code for sp in specs if not sp.security_type]
    stop = threading.Event()
    _signal.signal(_signal.SIGINT, lambda *_: stop.set())

    def on_event(kind, obj):
        ts = datetime.now(repo.KST).strftime("%H:%M:%S")
        if kind == "entry":
            typer.echo(f"[{ts}] PAPER BUY {obj.spec.id} {obj.entry_price:,.0f} "
                       f"TP {obj.tp:,.0f} SL {obj.sl:,.0f}")
        elif kind == "exit":
            typer.echo(f"[{ts}] PAPER SELL {obj.symbol_id} {obj.exit_price:,.0f} "
                       f"{obj.result} 순수익 {obj.net_rate:+.3%}")
        else:
            typer.echo(f"[{ts}] API 오류: {obj}")

    try:
        with TossClient(Credentials.from_env()) as client:
            if unknown:
                # 종목 유형을 모르면 비용 모델(거래세·호가단위)이 틀린다. 한 번 조회해 저장한다.
                from .api.endpoints import StockInfo

                try:
                    for info in StockInfo(client).stocks(unknown):
                        repo.ensure_symbol(conn, "KR", info["symbol"], info.get("name"),
                                           info.get("securityType"))
                        specs = [
                            SymbolSpec(sp.market, sp.code, sp.name, info.get("securityType"))
                            if sp.code == info["symbol"] else sp for sp in specs
                        ]
                    conn.commit()
                except TossApiError as exc:
                    typer.echo(f"[WARN] 종목 유형 조회 실패 — 주식으로 가정: {exc}")
            try:
                today = MarketInfo(client).calendar_kr().get("today", {})
                if today.get("integrated") is None:
                    typer.echo("[WATCH] 오늘은 휴장일입니다.")
                    raise typer.Exit()
            except TossApiError:
                pass      # 캘린더 조회 실패 시 시간 기준으로만 판단
            scanner = Scanner(
                MarketData(client), specs,
                DetectorParams.from_config(cfg.strategy),
                engine.ExitParams.from_config(cfg.strategy),
                engine.SessionParams.from_config(cfg.strategy),
                engine.LimitParams.from_config(cfg.risk),
                cfg.strategy.get("costs"), conn=conn,
                workers=int(rt.get("workers", 8)), prefilter=bool(rt.get("prefilter", True)),
                prefilter_ratio=float(rt.get("prefilter_ratio", 0.7)),
                max_spread_rate=float(rt.get("max_spread_rate", 0.004)),
                max_signal_age_seconds=float(rt.get("max_signal_age_seconds", 10.0)),
            )
            typer.echo(f"[WATCH] paper 모드, 종목 {len(specs)}개. Ctrl-C 로 종료.")
            if not scanner.in_session(datetime.now(repo.KST)):
                typer.echo("  지금은 거래 시간이 아닙니다. 장이 열리면 자동으로 시작합니다.")
            if duration > 0:
                threading.Timer(duration, stop.set).start()
            scanner.run(
                stop, float(rt.get("poll_interval_seconds", 2.0)),
                float(rt.get("settle_seconds", 1.0)), on_event,
                float(rt.get("poll_interval_holding_seconds", 1.0)),
            )
            scanner.close()
            typer.echo("[WATCH] 종료. 지연 통계:")
            typer.echo(scanner.stats.format() or "  (측정값 없음)")
            if scanner.closed:
                nets = [t.net_rate for t in scanner.closed]
                typer.echo(f"  가상 거래 {len(nets)}회, 평균 순수익 {sum(nets) / len(nets):+.3%}")
    except RuntimeError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(code=1) from None
    finally:
        conn.close()


@app.command()
def bench(
    symbols: int = typer.Option(20, "--symbols"),
    signals: int = typer.Option(1, "--signals", help="동시에 신호가 나는 종목 수"),
    latency_ms: float = typer.Option(150, "--latency-ms", help="가짜 서버 응답 지연"),
    jitter_ms: float = typer.Option(0, "--jitter-ms"),
    server_limit: float = typer.Option(0, "--server-limit", help="서버 초당 한도 (0 = 없음)"),
    cycles: int = typer.Option(10, "--cycles"),
) -> None:
    """가짜 서버로 분 마감 처리 지연을 잰다 (API 키 불필요)."""
    from .devtools import bench as b

    cases = list(b.DEFAULT_CASES)
    if server_limit:
        cases = [b.BenchCase(c.label + ", 제한기", c.workers, c.prefilter,
                             max(1.0, server_limit * 0.8)) for c in cases]
    typer.echo(f"종목 {symbols}, 신호 {signals}, 응답 지연 {latency_ms:.0f}ms"
               f"(+0~{jitter_ms:.0f}), 서버 한도 {server_limit or '없음'}, {cycles}사이클")
    results = [
        b.run_case(c, n_symbols=symbols, n_signals=signals, latency_ms=latency_ms,
                   jitter_ms=jitter_ms, server_limit=server_limit or None, cycles=cycles)
        for c in cases
    ]
    typer.echo(b.format_results(results))
    typer.echo("결정 = 분봉 조회 시작부터 진입 결정까지. 실제 신호 지연은 여기에 settle 대기와 "
               "토스 서버의 분봉 반영 지연이 더해진다.")


@app.command()
def latency(
    samples: int = typer.Option(10, "--samples"),
    candle_lag: bool = typer.Option(False, "--candle-lag", help="분봉 반영 지연 측정 (장중에만)"),
) -> None:
    """실제 토스 API 의 응답 시간·한도 헤더·시계 오차를 잰다."""
    from .api import TossClient
    from .devtools import probe

    cfg = AppConfig.load()
    favorites = [x for x in _load_favorites()["symbols"] if x.get("enabled", True)]
    codes = [x["code"] for x in favorites if x["market"] == "KR"]
    if not codes:
        typer.echo("KR 관심종목이 없습니다.")
        raise typer.Exit(code=1)
    try:
        with TossClient(Credentials.from_env()) as client:
            res = probe.measure_endpoints(client, codes, samples)
            typer.echo("[LATENCY] 엔드포인트 응답 시간")
            for name, m in res.items():
                typer.echo(f"  {name:<24} p50 {m['p50']:>6.0f}ms  p95 {m['p95']:>6.0f}ms  "
                           f"max {m['max']:>6.0f}ms  (성공 {m['n']}, 실패 {m['errors']})")
            if client.rate_limit_seen:
                typer.echo("[LATENCY] 한도 헤더")
                for group, headers in client.rate_limit_seen.items():
                    typer.echo(f"  {group}: {headers}")
            else:
                typer.echo("[LATENCY] 정상 응답에는 한도 헤더가 없습니다 (429 응답에서만 제공).")
            offset = probe.clock_offset_seconds(client)
            if offset is not None:
                typer.echo(f"[LATENCY] 시계 오차(내 PC - 서버): {offset:+.1f}s (±1s 해상도)")
                if abs(offset) > 2:
                    typer.echo("  주의: 2초 넘게 어긋나면 분 마감 시점을 잘못 잡습니다. "
                               "시간 동기화가 필요합니다.")
            if candle_lag:
                typer.echo("[LATENCY] 다음 분 경계에서 분봉 반영 지연 측정 중 (최대 70초)...")
                lag = probe.measure_candle_lag(client, codes[0])
                if not lag["target_seen"]:
                    typer.echo("  직전 1분봉이 없습니다. 장중이 아니거나 "
                               "그 1분에 체결이 없었습니다.")
                else:
                    changed = lag["last_change_after_boundary_ms"]
                    when = ("경계 시점에 이미 확정" if changed is None
                            else f"경계 +{changed:.0f}ms 까지 변경됨")
                    typer.echo(f"  직전 봉 확정: {when}")
                    if lag["new_bar_first_seen_ms"] is not None:
                        typer.echo(f"  새 봉 첫 등장: 경계 +{lag['new_bar_first_seen_ms']:.0f}ms")
            rt = cfg.strategy.get("realtime", {})
            settle = float(rt.get("settle_seconds", 1.0)) * 1000
            worst = max(res["candles 1m (30봉)"]["p95"], res["orderbook"]["p95"])
            typer.echo(f"[LATENCY] 예상 신호 지연(분 마감 → 진입 결정): settle {settle:.0f}ms + "
                       f"조회 p95 {worst:.0f}ms ≈ {settle + worst:.0f}ms")
    except RuntimeError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(code=1) from None


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
    entry_model: str = typer.Option("open", "--entry-model", help="open / mid / worst"),
    latency_sweep: bool = typer.Option(
        False, "--latency-sweep", help="진입 지연 가정(open/mid/worst)별 결과 비교"
    ),
) -> None:
    """DB 의 과거 1분봉으로 웅덩이 전략을 리플레이한다 (실주문 없음)."""
    import uuid

    from .backtest import engine, runner
    from .db import repository as repo
    from .strategy.detector import DetectorParams

    cfg = AppConfig.load()
    costs_cfg = cfg.strategy.get("costs")
    det = DetectorParams.from_config(cfg.strategy)
    if entry_model not in ("open", "mid", "worst"):
        typer.echo("entry-model 은 open / mid / worst 중 하나입니다.")
        raise typer.Exit(code=1)
    from dataclasses import replace as _replace

    ex = _replace(engine.ExitParams.from_config(cfg.strategy), entry_model=entry_model)
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

    if latency_sweep:
        labels = {"open": "즉시(다음 봉 시가)", "mid": "약 30초 지연(시가·종가 중간)",
                  "worst": "1분 내 최악(다음 봉 고가)"}
        typer.echo("진입이 늦어질수록 기대값이 얼마나 깎이는지 본다. worst 에서도 양수면 "
                   "지연은 문제가 아니다.")
        for model, label in labels.items():
            res = runner.run_single(data, costs, groups, det,
                                    _replace(ex, entry_model=model), session, limits)
            typer.echo(f"\n진입 가정: {label}")
            for group, g in res["groups"].items():
                typer.echo(f"  [{group}] {_fmt_metrics(g['metrics'])}")
        conn.close()
        return
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
