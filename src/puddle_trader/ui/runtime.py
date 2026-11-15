"""화면 뒤에서 도는 것들: 감시(연습 매매) 스레드, 백필·시험 작업, 데모 시나리오.

스레드 규칙: SQLite 연결은 그것을 쓰는 스레드 안에서 만든다. 화면 요청은 요청마다 새 연결을 연다.
"""
from __future__ import annotations

import json
import threading
import time
from collections import deque
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .. import favorites
from .. import notify as notify_mod
from ..api.client import TossApiError, TossClient
from ..api.endpoints import Account, MarketData, StockInfo
from ..backtest import engine, runner
from ..bars import from_api
from ..collect.backfill import backfill_many
from ..config import AppConfig, Credentials, credentials_present
from ..db import init_db
from ..db import repository as repo
from ..db.database import connect
from ..realtime.scanner import Scanner, SymbolSpec
from ..strategy.detector import DetectorParams
from . import service
from .access import lan_addresses

DEMO_SYMBOLS = [("900001", "예시종목 A"), ("900002", "예시종목 B"), ("900003", "예시종목 C")]


def previous_close(md: MarketData, code: str, today: date) -> float | None:
    """전일 종가: 일봉 가운데 오늘보다 앞선 날짜의 마지막 봉 종가. 등락률의 기준이다.

    /prices 응답에는 현재가만 있어서 일봉(1d)에서 구한다. 응답에 오늘 봉이 들어 있든 아니든
    같은 결과가 나오도록, 날짜(한국 시간)로 걸러 낸다.
    """
    rows = (md.candles(code, "1d", 5) or {}).get("candles") or []
    earlier = [b for b in from_api(rows) if b.ts.astimezone(repo.KST).date() < today]
    return earlier[-1].close if earlier else None


class DemoScenario:
    """API 키 없이 화면을 써 볼 수 있는 가상 시나리오 (약 3분).

    A: 급락 후 반등 신호 → 연습 매수 → 가격이 올라 목표가에 팔림
    B: 같은 신호 → 연습 매수 → 가격이 내려 손절로 팔림
    C: 아무 일 없음
    """

    def __init__(self, start: datetime):
        self.a_buy = start.replace(second=0, microsecond=0) + timedelta(minutes=1)
        self.b_buy = self.a_buy + timedelta(minutes=2)

    def anchor(self, symbol: str) -> datetime | None:
        """신호가 나는 분 경계. 이 시각 직전 봉이 '반등 봉'이다."""
        return {"900001": self.a_buy, "900002": self.b_buy}.get(symbol)

    def price(self, symbol: str, now: datetime) -> float:
        buy = self.anchor(symbol)
        if buy is None:
            return 100_000.0
        if now < buy:
            # 신호 전: 그 분의 봉 종가를 따라간다 (봉 이력과 현재가가 어긋나지 않게)
            from ..devtools.fake_server import PUDDLE_TAIL

            back = round((buy - timedelta(minutes=1)
                          - now.replace(second=0, microsecond=0)).total_seconds() / 60)
            return float(PUDDLE_TAIL[len(PUDDLE_TAIL) - 1 - back][3]) \
                if 0 <= back < len(PUDDLE_TAIL) else 100_000.0
        steps = int((now - buy - timedelta(seconds=5)).total_seconds() // 8)
        steps = min(max(steps, 0), 10 if symbol == "900001" else 7)
        return 99_300.0 + (100.0 if symbol == "900001" else -100.0) * steps


class Task:
    """백그라운드 작업 하나의 상태 (화면이 진행 상황을 물어본다)."""

    def __init__(self) -> None:
        self.state = "idle"        # idle / running / done / error
        self.message = ""
        self._lock = threading.Lock()

    def snapshot(self) -> dict[str, str]:
        with self._lock:
            return {"state": self.state, "message": self.message}

    def set(self, state: str | None = None, message: str | None = None) -> None:
        with self._lock:
            if state is not None:
                self.state = state
            if message is not None:
                self.message = message

    def start(self, fn) -> bool:
        with self._lock:
            if self.state == "running":
                return False
            self.state, self.message = "running", "시작하는 중…"

        def run() -> None:
            try:
                fn(self)
                if self.snapshot()["state"] == "running":
                    self.set("done")
            except Exception as exc:  # noqa: BLE001 - 작업 실패는 화면에 메시지로 보여준다
                self.set("error", str(exc))

        threading.Thread(target=run, daemon=True).start()
        return True


class UiApp:
    def __init__(self, demo: bool = False, state_dir: str | Path = "data",
                 demo_lead_seconds: float = 10.0):
        self.demo = demo
        self.demo_lead_seconds = demo_lead_seconds   # 데모 시작 후 첫 신호까지 걸리는 시간
        self.state_dir = Path(state_dir)
        cfg = AppConfig.load()
        default_db = cfg.app.get("database_path", "data/tradebot.sqlite")
        self.db_path = str(self.state_dir / "demo.sqlite") if demo else default_db
        if demo:
            Path(self.db_path).unlink(missing_ok=True)   # 데모는 매번 새로 시작
        init_db(self.db_path)
        self.state_path = self.state_dir / ("ui_state.demo.json" if demo else "ui_state.json")
        self.watch_task = Task()
        self.backfill_task = Task()
        self.backtest_task = Task()
        self._stop = threading.Event()
        self._scanner: Scanner | None = None
        self._session_events: deque[dict[str, str]] = deque(maxlen=50)
        self._state_lock = threading.Lock()
        self._demo_server = None
        self._demo_clock = None
        self._md: MarketData | None = None
        self._prev_close: dict[str, float] = {}     # 종목 id → 전일 종가
        self._prev_day: date | None = None          # 위 값을 구한 날짜
        self._prev_loading = False
        self._prev_retry_at = 0.0
        self.notifier = notify_mod.Notifier()
        self.phone_port: int | None = None    # 휴대폰 접속을 켰을 때의 포트 (알림 링크에 쓴다)
        self.prev_close_pause = 0.2     # 일봉 조회 사이 쉬는 시간 (신호 조회를 막지 않게)
        self.now_fn = service.now_kst

    # ---- 저장되는 화면 상태 (연결 확인 결과, 마지막 판정) -------------------------
    def load_state(self) -> dict[str, Any]:
        with self._state_lock:
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return {}

    def update_state(self, **patch: Any) -> None:
        state = self.load_state()
        state.update(patch)
        with self._state_lock:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def db(self):
        return connect(self.db_path)

    # ---- 증권사 연결 ------------------------------------------------------------
    def check_connection(self) -> dict[str, Any]:
        if self.demo:
            return {"ok": True, "message": "데모에서는 연결이 필요 없어요"}
        try:
            with TossClient(Credentials.from_env()) as client:
                accounts = Account(client).accounts()
            ok = bool(accounts)
            message = "연결됐어요" if ok else "연결은 됐지만 계좌가 없어요"
        except RuntimeError:
            ok, message = False, "토스증권 키가 아직 없어요"
        except TossApiError as exc:
            ok = False
            if exc.status in (400, 401):
                message = "키가 맞지 않아요. 다시 확인해 주세요"
            elif exc.code in ("network-error", "timeout"):
                message = "토스증권에 닿지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요"
            else:
                message = f"연결하지 못했어요 ({exc.code})"
        self.update_state(auth={"ok": ok, "message": message,
                                "at": self.now_fn().isoformat(timespec="seconds")})
        return {"ok": ok, "message": message}

    # ---- 감시 (연습 매매) --------------------------------------------------------
    def start_watch(self) -> bool:
        self._stop.clear()
        return self.watch_task.start(self._run_watch)

    def stop_watch(self) -> None:
        self._stop.set()

    def _event(self, text: str) -> None:
        now = self.now_fn()
        self._session_events.appendleft({"at": now.isoformat(), "time": now.strftime("%H:%M"),
                                         "text": text})

    def _build_client(self) -> tuple[TossClient, list[SymbolSpec], Any]:
        cfg = AppConfig.load()
        if self.demo:
            from ..devtools.bench import VirtualClock
            from ..devtools.fake_server import FakeTossServer

            clock = VirtualClock()
            now = datetime.now(repo.KST)
            while now.weekday() >= 5:                 # 주말이면 직전 평일로
                now -= timedelta(days=1)
            start = (now.replace(hour=10, minute=21, second=0, microsecond=0)
                     - timedelta(seconds=self.demo_lead_seconds))
            clock.set(start)
            scenario = DemoScenario(start)
            server = FakeTossServer(latency_ms=30, now_fn=clock.now).start()
            server.price_fn, server.anchor_fn = scenario.price, scenario.anchor
            self._demo_server, self._demo_clock = server, clock
            self.now_fn = clock.now
            api = {"base_url": server.base_url, "token_cache_path": "",
                   "retry_backoff_seconds": 0.2}
            client = TossClient(Credentials("demo", "demo", 1), AppConfig(api=api))
            specs = [SymbolSpec("KR", code, name, "STOCK") for code, name in DEMO_SYMBOLS]
            return client, specs, clock.now
        client = TossClient(Credentials.from_env(), cfg)
        items = [x for x in favorites.load()["symbols"]
                 if x.get("enabled", True) and x.get("market") == "KR"]
        if not items:
            client.close()
            raise RuntimeError("지켜볼 국내 종목이 없어요. 관심종목을 먼저 추가해 주세요.")
        conn = self.db()
        known = {r["id"]: r["security_type"]
                 for r in conn.execute("SELECT id, security_type FROM symbols")}
        unknown = [str(x["code"]) for x in items
                   if not known.get(repo.symbol_id("KR", str(x["code"])))]
        if unknown:
            try:     # 종목 유형(주식/ETF)에 따라 세금·호가단위가 달라진다
                for info in StockInfo(client).stocks(unknown):
                    sid = repo.ensure_symbol(conn, "KR", info["symbol"], info.get("name"),
                                             info.get("securityType"))
                    known[sid] = info.get("securityType")
                conn.commit()
            except TossApiError:
                pass     # 조회 실패 시 주식으로 가정
        conn.close()
        specs = [SymbolSpec("KR", str(x["code"]), x.get("name") or None,
                            known.get(repo.symbol_id("KR", str(x["code"])))) for x in items]
        return client, specs, service.now_kst

    def _run_watch(self, task: Task) -> None:
        cfg = AppConfig.load()
        rt = cfg.strategy.get("realtime", {})
        try:
            client, specs, now_fn = self._build_client()
        except RuntimeError as exc:
            task.set("error", str(exc))
            return
        conn = self.db()
        md = MarketData(client)
        self._md = md
        self._prev_day, self._prev_retry_at = None, 0.0   # 종목이 바뀌었을 수 있으니 다시 받는다
        scanner = Scanner(
            md, specs,
            DetectorParams.from_config(cfg.strategy),
            engine.ExitParams.from_config(cfg.strategy),
            engine.SessionParams.from_config(cfg.strategy),
            engine.LimitParams.from_config(cfg.risk),
            cfg.strategy.get("costs"), conn=conn, now_fn=now_fn,
            workers=int(rt.get("workers", 8)), prefilter=bool(rt.get("prefilter", True)),
            prefilter_ratio=float(rt.get("prefilter_ratio", 0.7)),
            max_spread_rate=float(rt.get("max_spread_rate", 0.004)),
            max_signal_age_seconds=float(rt.get("max_signal_age_seconds", 10.0)),
            settle_seconds=float(rt.get("settle_seconds", 1.0)),
            probe_interval_seconds=float(rt.get("probe_interval_seconds", 0.15)),
            warm_connections=0 if self.demo else int(rt.get("warm_connections", 6)),
        )
        self._scanner = scanner
        task.set("running", f"종목 {len(specs)}개를 지켜보는 중")
        self._event(f"신호를 기다리기 시작했어요 (종목 {len(specs)}개)")

        by_id = {spec.id: spec for spec in specs}

        def on_event(kind: str, obj: Any) -> None:
            if kind == "error":
                task.set(message=f"증권사 응답이 불안정해요 ({getattr(obj, 'code', '오류')})")
                return
            task.set(message=f"종목 {len(specs)}개를 지켜보는 중")
            try:      # 알림은 뒤에서 나간다. 문구를 만들다 실패해도 감시는 계속한다
                link = self.signal_link(obj.signal_id)        # 알림을 누르면 이 신호 화면이 열린다
                if kind == "entry":
                    self.notifier.submit("entry", *service.entry_notice(cfg, obj, self.demo), link)
                elif kind == "exit" and obj.symbol_id in by_id:
                    spec = by_id[obj.symbol_id]
                    self.notifier.submit("exit", *service.exit_notice(cfg, spec, obj, self.demo),
                                         link)
            except Exception:  # noqa: BLE001 - 알림 때문에 연습 매매가 멈추면 안 된다
                pass

        try:
            scanner.run(
                self._stop, float(rt.get("poll_interval_seconds", 2.0)), on_event,
                float(rt.get("poll_interval_holding_seconds", 0.5)),
                float(rt.get("probe_start_seconds", 0.1)),
                0.0 if self.demo else float(rt.get("warm_lead_seconds", 2.0)),
            )
        finally:
            scanner.close()
            self._scanner = None
            self._md = None
            conn.close()
            client.close()
            if self._demo_server is not None:
                self._demo_server.stop()
                self._demo_server = None
            self._event("지켜보기를 멈췄어요")
        task.set("idle", "")

    def live_positions(self) -> dict[str, float]:
        """보유 중인 종목의 최신 가격 (signal_id → 현재가)."""
        scanner = self._scanner
        if scanner is None:
            return {}
        out = {}
        for sid, pos in dict(scanner.positions).items():
            last = scanner.tape.last(sid)
            if last is not None:
                out[pos.signal_id] = last
        return out

    def _ensure_prev_closes(self) -> None:
        """감시 중이면 전일 종가를 하루에 한 번, 뒤에서 받아 둔다 (실패한 종목은 1분 뒤 다시)."""
        scanner, md = self._scanner, self._md
        today = self.now_fn().date()
        if (scanner is None or md is None or self._prev_loading or self._prev_day == today
                or time.monotonic() < self._prev_retry_at):
            return
        self._prev_loading = True
        specs = list(scanner.symbols)

        def work() -> None:
            closes: dict[str, float] = {}
            failed = False
            try:
                for i, spec in enumerate(specs):
                    if self._scanner is not scanner:      # 그사이 감시가 끝났다
                        return
                    if i:
                        time.sleep(self.prev_close_pause)
                    try:
                        value = previous_close(md, spec.code, today)
                    except (TossApiError, RuntimeError, ValueError, KeyError, TypeError):
                        value, failed = None, True
                    if value:
                        closes[spec.id] = value
                self._prev_close = closes
                if failed:
                    self._prev_retry_at = time.monotonic() + 60
                else:
                    self._prev_day = today
            finally:
                self._prev_loading = False

        threading.Thread(target=work, daemon=True).start()

    def signal_link(self, signal_id: str) -> str | None:
        """휴대폰에서 그 신호 화면을 여는 주소. 휴대폰 접속이 꺼져 있으면 열 수 없으므로 없다.

        같은 와이파이에서만 열린다. 접속 코드는 넣지 않는다 (알림은 바깥 서비스를 거치므로).
        """
        if self.phone_port is None:
            return None
        ips = lan_addresses()
        if not ips:
            return None
        return f"http://{ips[0]}:{self.phone_port}/#/signal/{quote(signal_id, safe='')}"

    def watchlist(self) -> list[dict[str, Any]]:
        """옆 패널의 관심종목: 이름·코드·지켜보는지·최신 가격과 등락률(감시 중일 때만)·보유 여부."""
        self._ensure_prev_closes()
        if self.demo:
            items = [{"market": "KR", "code": code, "name": name, "enabled": True}
                     for code, name in DEMO_SYMBOLS]
        else:
            items = favorites.load()["symbols"]
        scanner = self._scanner
        held = set(dict(scanner.positions)) if scanner is not None else set()
        out = []
        for x in items:
            sid = repo.symbol_id(str(x.get("market", "KR")), str(x["code"]))
            last = scanner.tape.last(sid) if scanner is not None else None
            prev = self._prev_close.get(sid) if scanner is not None else None
            out.append({
                "symbol_id": sid, "market": x.get("market", "KR"), "code": str(x["code"]),
                "name": x.get("name") or str(x["code"]),
                "enabled": x.get("enabled", True) is not False,
                "last": last, "prev_close": prev,
                "change_rate": (last / prev - 1) if last is not None and prev else None,
                "holding": sid in held,
            })
        return out

    def in_session(self) -> bool:
        cfg = AppConfig.load()
        ses = engine.SessionParams.from_config(cfg.strategy)
        now = self.now_fn()
        open_ = datetime.combine(now.date(), ses.open, tzinfo=now.tzinfo)
        close = datetime.combine(now.date(), ses.close, tzinfo=now.tzinfo)
        return now.weekday() < 5 and open_ <= now < close

    def session_events(self) -> list[dict[str, str]]:
        return list(self._session_events)

    # ---- 과거 기록 받기 ----------------------------------------------------------
    def start_backfill(self) -> bool:
        def work(task: Task) -> None:
            targets = [(x["market"], str(x["code"]), x.get("name"))
                       for x in favorites.load()["symbols"] if x.get("enabled", True)]
            if not targets:
                raise RuntimeError("관심종목이 없어요. 먼저 종목을 추가해 주세요.")
            try:
                creds = Credentials.from_env()
            except RuntimeError:
                raise RuntimeError("토스증권 키가 없어요. 설정에서 먼저 연결해 주세요.") from None
            conn = self.db()
            done = 0

            def report(item) -> None:
                nonlocal done
                done += 1
                task.set(message=f"{done} / {len(targets)} 종목 받는 중…")

            try:
                with TossClient(creds) as client:
                    results = backfill_many(client, conn, targets, "1m", on_result=report)
            finally:
                conn.close()
            failed = [r for r in results if isinstance(r, tuple)]
            if failed and len(failed) == len(results):
                raise RuntimeError(f"기록을 받지 못했어요 ({failed[0][1]})")
            task.set("done", f"{len(results) - len(failed)}개 종목의 기록을 받았어요"
                     + (f" (실패 {len(failed)}개)" if failed else ""))

        return self.backfill_task.start(work)

    # ---- 과거로 시험 -------------------------------------------------------------
    def start_backtest(self) -> bool:
        def work(task: Task) -> None:
            task.set(message="지난 기록에 규칙을 대 보는 중…")
            conn = self.db()
            try:
                result = run_verdict(conn, AppConfig.load())
            finally:
                conn.close()
            result["at"] = self.now_fn().isoformat(timespec="seconds")
            self.update_state(backtest=result)
            task.set("done", "시험이 끝났어요")

        return self.backtest_task.start(work)

    def shutdown(self) -> None:
        self._stop.set()


def run_verdict(conn, cfg: AppConfig) -> dict[str, Any]:
    """지난 기록으로 시험해 통과 / 통과 못 함 / 판정 보류를 정한다."""
    data, costs, groups = runner.load_data(conn, cfg.strategy.get("costs"))
    days = len(runner.all_days(data)) if data else 0
    if days < service.NEED_DAYS:
        return {"verdict": "hold", "days": days, "groups": {},
                "reasons": [f"기록이 {days}일치뿐이에요. {service.NEED_DAYS}일치 이상 필요해요."]}
    res = runner.run_grid(
        data, costs, groups,
        DetectorParams.from_config(cfg.strategy),
        engine.ExitParams.from_config(cfg.strategy),
        engine.SessionParams.from_config(cfg.strategy),
        engine.LimitParams.from_config(cfg.risk),
        cfg.strategy.get("backtest"),
    )
    out_groups: dict[str, Any] = {}
    for name, g in res["groups"].items():
        best = g["best"]
        oos = best["out_of_sample"] if best else None
        out_groups[name] = {
            "passed": bool(g["passed"]), "reasons": g["reasons"],
            "trades": oos["n"] if oos else 0,
            "expectancy": oos["expectancy"] if oos else None,
            "positive_rate": oos["positive_rate"] if oos else None,
            "symbols": len(g["symbols"]), "test_days": g["test_days"],
        }
    passed = any(g["passed"] for g in out_groups.values())
    return {"verdict": "pass" if passed else "fail", "days": days, "groups": out_groups,
            "reasons": [] if passed else ["수수료·세금을 빼면 남지 않았거나, 거래 수가 모자라요."]}


def has_keys() -> bool:
    return credentials_present()
