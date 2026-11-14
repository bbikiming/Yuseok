"""지연 시간 계측: 단계별 소요 시간을 모아 p50/p95/max 로 요약한다."""
from __future__ import annotations

import threading
from collections import defaultdict


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return ordered[idx]


class LatencyStats:
    def __init__(self) -> None:
        self._samples: dict[str, list[float]] = defaultdict(list)
        self._counts: dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()

    def add(self, name: str, ms: float) -> None:
        with self._lock:
            self._samples[name].append(ms)

    def count(self, name: str, n: int = 1) -> None:
        with self._lock:
            self._counts[name] += n

    def samples(self, name: str) -> list[float]:
        with self._lock:
            return list(self._samples.get(name, []))

    def counter(self, name: str) -> int:
        with self._lock:
            return self._counts.get(name, 0)

    def summary(self) -> dict[str, dict[str, float]]:
        with self._lock:
            items = {k: list(v) for k, v in self._samples.items()}
        return {
            k: {"n": len(v), "p50": percentile(v, 0.5), "p95": percentile(v, 0.95),
                "max": max(v)}
            for k, v in sorted(items.items()) if v
        }

    def format(self) -> str:
        lines = [
            f"  {name:<22} n={s['n']:<5} p50 {s['p50']:>7.0f}ms  p95 {s['p95']:>7.0f}ms  "
            f"max {s['max']:>7.0f}ms"
            for name, s in self.summary().items()
        ]
        with self._lock:
            counts = dict(self._counts)
        lines += [f"  {name:<22} {n}" for name, n in sorted(counts.items())]
        return "\n".join(lines)
