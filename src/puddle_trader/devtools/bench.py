"""스캐너 지연 벤치마크: 가짜 서버에 지연·한도를 주입하고 분 마감 처리 시간을 잰다.

재는 것: 분이 바뀐 뒤 (settle 대기 후) 분봉 조회 → 탐지 → 호가 조회 → 진입 결정까지의 시간.
재지 않는 것: 실제 토스 서버의 응답 시간과 분봉 반영 지연. 그건 `tradebot latency` 로 잰다.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..api.client import TossClient
from ..api.endpoints import MarketData
from ..backtest.engine import ExitParams, LimitParams, SessionParams
from ..config import AppConfig, Credentials
from ..db import repository as repo
from ..realtime.scanner import Scanner, SymbolSpec
from ..realtime.stats import LatencyStats, percentile
from ..strategy.detector import DetectorParams
from .fake_server import BASE_PRICE, FakeTossServer


class VirtualClock:
    """지정한 시각에서 시작해 실제 시간만큼 흐르는 시계 (장중 시각을 흉내 낸다)."""

    def __init__(self) -> None:
        self._anchor = datetime.now(repo.KST)
        self._perf = time.perf_counter()

    def set(self, dt: datetime) -> None:
        self._anchor, self._perf = dt, time.perf_counter()

    def now(self) -> datetime:
        return self._anchor + timedelta(seconds=time.perf_counter() - self._perf)


@dataclass
class BenchCase:
    label: str
    workers: int = 1
    prefilter: bool = False
    client_limit: float | None = None     # 클라이언트 측 초당 요청 제한 (그룹별)


@dataclass
class BenchResult:
    label: str
    decision_p50: float
    decision_p95: float
    cycle_p50: float
    cycle_p95: float
    poll_p50: float
    candle_calls_per_cycle: float
    throttled: int
    expected_signals: int
    found_signals: int


def run_case(
    case: BenchCase,
    *,
    n_symbols: int = 20,
    n_signals: int = 1,
    latency_ms: float = 150.0,
    jitter_ms: float = 0.0,
    server_limit: float | None = None,
    candle_lag_ms: float = 0.0,
    settle_seconds: float = 0.0,
    cycles: int = 10,
) -> BenchResult:
    codes = [f"{k:06d}" for k in range(1, n_symbols + 1)]
    signal_codes = set(codes[:n_signals])
    specs = [SymbolSpec("KR", c, c, "STOCK") for c in codes]
    clock = VirtualClock()
    stats = LatencyStats()
    det = DetectorParams()
    limits = LimitParams(max_daily_entries=max(5, n_signals))
    limit_cfg = (
        {"MARKET_DATA": case.client_limit, "MARKET_DATA_CHART": case.client_limit}
        if case.client_limit else {}
    )
    found = 0
    cycle_ms: list[float] = []
    with FakeTossServer(latency_ms, jitter_ms, server_limit, candle_lag_ms, signal_codes,
                        clock.now) as server:
        cfg = AppConfig(api={"base_url": server.base_url, "token_cache_path": "",
                             "timeout_seconds": 15, "retry_count": 5,
                             "retry_backoff_seconds": 0.2,
                             "rate_limits_per_second": limit_cfg})
        with TossClient(Credentials("bench", "bench", 1), cfg) as client:
            md = MarketData(client)
            md.prices(codes[:1])                      # 토큰 발급·연결 수립은 측정에서 제외
            base = datetime.now(repo.KST).replace(hour=11, minute=0, second=0, microsecond=0)
            for k in range(cycles):
                boundary = base + timedelta(minutes=k)
                scanner = Scanner(md, specs, det, ExitParams(), SessionParams(), limits,
                                  workers=case.workers, prefilter=case.prefilter,
                                  now_fn=clock.now, stats=stats)
                window = scanner.tape.window
                for spec in specs:                    # 테이프를 정상 운용 상태로 채운다
                    scanner.tape.add(spec.id, boundary - window - timedelta(seconds=5), BASE_PRICE)
                    if spec.code in signal_codes:
                        scanner.tape.add(spec.id, boundary - timedelta(minutes=3), 98_500.0)
                        scanner.tape.add(spec.id, boundary - timedelta(seconds=2), 99_300.0)
                    else:
                        scanner.tape.add(spec.id, boundary - timedelta(seconds=2), BASE_PRICE)
                clock.set(boundary + timedelta(seconds=settle_seconds))
                t0 = time.perf_counter()
                found += len(scanner.on_minute_close(boundary))
                cycle_ms.append((time.perf_counter() - t0) * 1000)
                scanner.poll(clock.now())
                scanner.close()
                if server_limit:
                    time.sleep(1.1)                   # 한도 창을 비우고 다음 사이클
            candle_calls = server.calls.get("/api/v1/candles", 0)
            throttled = server.throttled
    dec = stats.samples("decision_ms")
    poll = stats.samples("poll_total_ms")
    return BenchResult(
        label=case.label,
        decision_p50=percentile(dec, 0.5), decision_p95=percentile(dec, 0.95),
        cycle_p50=percentile(cycle_ms, 0.5), cycle_p95=percentile(cycle_ms, 0.95),
        poll_p50=percentile(poll, 0.5),
        candle_calls_per_cycle=candle_calls / cycles, throttled=throttled,
        expected_signals=n_signals * cycles, found_signals=found,
    )


DEFAULT_CASES = [
    BenchCase("순차 조회, 전 종목"),
    BenchCase("병렬 8, 전 종목", workers=8),
    BenchCase("병렬 8 + 후보 압축", workers=8, prefilter=True),
]


def format_results(results: list[BenchResult]) -> str:
    lines = [f"{'구성':<24}{'결정 p50':>10}{'결정 p95':>10}{'사이클 p95':>11}"
             f"{'폴링 p50':>10}{'분봉호출/분':>11}{'429':>6}{'신호':>9}"]
    for r in results:
        lines.append(
            f"{r.label:<24}{r.decision_p50:>8.0f}ms{r.decision_p95:>8.0f}ms"
            f"{r.cycle_p95:>9.0f}ms{r.poll_p50:>8.0f}ms{r.candle_calls_per_cycle:>11.1f}"
            f"{r.throttled:>6}{r.found_signals:>5}/{r.expected_signals}"
        )
    return "\n".join(lines)
