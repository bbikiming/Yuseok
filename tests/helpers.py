"""테스트용 합성 데이터."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from puddle_trader.bars import Bar

KST = timezone(timedelta(hours=9))


def bar(day: date, minute: int, o, h, lo, c, v=100) -> Bar:
    ts = datetime(day.year, day.month, day.day, 9, 0, tzinfo=KST) + timedelta(minutes=minute)
    return Bar(ts, float(o), float(h), float(lo), float(c), float(v))


def puddle_prefix(day: date) -> list[Bar]:
    """09:00~09:35. 09:35 봉에서 웅덩이 신호가 난다 (하락 -1.5% → 지지 → 거래량 실린 양봉)."""
    bars = [bar(day, m, 100000, 100000, 100000, 100000) for m in range(30)]
    bars += [
        bar(day, 30, 100000, 100000, 99600, 99600, 300),
        bar(day, 31, 99600, 99600, 99000, 99000, 300),
        bar(day, 32, 99000, 99100, 98500, 98600, 300),   # 저점 98,500
        bar(day, 33, 98600, 98800, 98600, 98700, 100),
        bar(day, 34, 98700, 98900, 98650, 98800, 100),
        bar(day, 35, 98800, 99300, 98800, 99300, 500),   # 신호 봉
    ]
    return bars


def day_with_outcome(day: date, outcome: str) -> list[Bar]:
    """신호 뒤 결과를 붙인 하루치 봉. 진입은 09:36 시가 99,300 (+1틱)."""
    bars = puddle_prefix(day)
    bars.append(bar(day, 36, 99300, 99600, 99200, 99500))
    if outcome == "win":
        bars.append(bar(day, 37, 99500, 100400, 99500, 100300))
    elif outcome == "loss":
        bars.append(bar(day, 37, 99500, 99500, 98800, 98900))
    elif outcome == "both":      # 같은 봉에서 익절·손절 모두 터치
        bars.append(bar(day, 37, 99500, 100400, 98800, 99500))
    elif outcome == "timeout":
        bars += [bar(day, m, 99500, 99500, 99400, 99500) for m in range(37, 60)]
    bars += [bar(day, m, bars[-1].close, bars[-1].close, bars[-1].close, bars[-1].close)
             for m in range(int((bars[-1].ts.hour - 9) * 60 + bars[-1].ts.minute) + 1, 90)]
    return bars


def to_api_candles(bars: list[Bar]) -> list[dict]:
    return [
        {"timestamp": b.ts.isoformat(), "openPrice": str(b.open), "highPrice": str(b.high),
         "lowPrice": str(b.low), "closePrice": str(b.close), "volume": str(int(b.volume)),
         "currency": "KRW"}
        for b in bars
    ]
